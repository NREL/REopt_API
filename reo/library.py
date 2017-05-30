# python libraries
import os
import traceback
import shutil
import math
import pandas as pd
from datetime import datetime, timedelta
import re
import json

# logging
from log_levels import log

# user defined
import economics
import pvwatts
import results
from api_definitions import *

from urdb_parse import *
from utilities import Command, check_directory_created, write_single_variable


def alphanum(s):
    return re.sub(r'\W+', '', s)


class DatLibrary:

    # statically constant
    max_big_number = 100000000

    # timeout is slightly less than server timeout of 5 minutes
    timeout = 295
    timed_out = False

    # if need to debug, change to True, outputs OUT files, GO files, debugging to cmdline
    debug = True
    logfile = "reopt_api.log"
    xpress_model = "REopt_API.mos"
    time_steps_per_hour = 1

    def get_egg(self):
        wd = os.getcwd()
        return wd

    def inputs(self, **args):
        return inputs(**args)

    def outputs(self, **args):
        return outputs(**args)

    def __init__(self, run_input_id, lib_inputs):

        self.timed_out = False
        self.net_metering = False

        # DAT files to overwrite
        self.DAT = [None] * 20
        self.DAT_bau = [None] * 20

        # Command line constants
        self.command_line_constants = list()
        self.command_line_constants.append("ScenarioNum=" + str(run_input_id))

        # Economic inputs and calculated vals
        self.economics = list()

        self.run_input_id = run_input_id
        self.path_egg = self.get_egg()

        self.path_xpress = os.path.join(self.path_egg, "Xpress")
        self.file_logfile = os.path.join(self.path_egg, 'log', self.logfile)

        self.path_dat_library = os.path.join(self.path_xpress, "DatLibrary")
        self.path_run = os.path.join(self.path_xpress, "Run" + str(self.run_input_id))
        self.path_files_to_download = os.path.join(self.path_xpress, "Downloads")

        self.path_run_inputs = os.path.join(self.path_run, "Inputs")
        self.path_run_outputs = os.path.join(self.path_run, "Outputs")
        self.path_run_outputs_bau = os.path.join(self.path_run, "Outputs_bau")

        if os.path.exists(self.path_run):
            shutil.rmtree(self.path_run)

        for f in [self.path_run, self.path_run_inputs, self.path_run_outputs, self.path_run_outputs_bau]:
            os.mkdir(f)

        check_directory_created(self.path_run)
        check_directory_created(self.path_run_inputs)
        check_directory_created(self.path_run_outputs)
        check_directory_created(self.path_run_outputs_bau)

        self.file_output = os.path.join(self.path_run_outputs, "summary.csv")
        self.file_output_bau = os.path.join(self.path_run_outputs_bau, "summary.csv")

        self.file_post_input = os.path.join(self.path_run_inputs, "POST.json")
        self.file_cmd_input = os.path.join(self.path_run_inputs, "cmd.log")
        self.file_cmd_input_bau = os.path.join(self.path_run_inputs, "cmd_bau.log")
        self.file_constant = os.path.join(self.path_run_inputs, 'constant_' + str(self.run_input_id) + '.dat')
        self.file_constant_bau = os.path.join(self.path_run_inputs, 'constant_' + str(self.run_input_id) + '_bau.dat')
        self.file_storage = os.path.join(self.path_run_inputs, 'storage_' + str(self.run_input_id) + '.dat')
        self.file_storage_bau = os.path.join(self.path_run_inputs, 'storage_' + str(self.run_input_id) + '_bau.dat')
        self.file_max_size = os.path.join(self.path_run_inputs, 'maxsizes_' + str(self.run_input_id) + '.dat')
        self.file_max_size_bau = os.path.join(self.path_run_inputs, 'maxsizes_' + str(self.run_input_id) + '_bau.dat')
        self.file_economics = os.path.join(self.path_run_inputs, 'economics_' + str(self.run_input_id) + '.dat')
        self.file_economics_bau = os.path.join(self.path_run_inputs, 'economics_' + str(self.run_input_id) + '_bau.dat')
        self.file_gis = os.path.join(self.path_run_inputs, 'GIS_' + str(self.run_input_id) + '.dat')
        self.file_gis_bau = os.path.join(self.path_run_inputs, 'GIS_' + str(self.run_input_id) + '_bau.dat')
        self.file_load_size = os.path.join(self.path_run_inputs, 'LoadSize_' + str(self.run_input_id) + '.dat')
        self.file_load_profile = os.path.join(self.path_run_inputs, 'Load8760_' + str(self.run_input_id) + '.dat')
        self.file_NEM = os.path.join(self.path_run_inputs, 'NMIL_' + str(self.run_input_id) + '.dat')

        self.path_utility = os.path.join(self.path_run_inputs, "Utility")
        self.path_various = os.path.join(self.path_run_inputs)

        self.folder_utility = os.path.join(self.path_dat_library, "Utility")
        self.folder_load_profile = os.path.join(self.path_dat_library, "LoadProfiles")
        self.folder_load_size = os.path.join(self.path_dat_library, "LoadSize")
        self.folder_various = os.path.join(self.path_dat_library, "Various")

        for k, v in self.inputs(full_list=True).items():
            # see api_definitions.py for attributes set here
            if k == 'load_profile_name' and lib_inputs.get(k) is not None:
                setattr(self, k, lib_inputs.get(k).replace(" ", ""))

            elif lib_inputs.get(k) is None:
                setattr(self, k, self.inputs()[k].get('default'))

            else:
                setattr(self, k, lib_inputs.get(k))

        if self.tilt is None:
            self.tilt = self.latitude

        self.default_load_profiles = [p.lower() for p in default_load_profiles()]
        self.default_building = default_building()
        self.default_city = default_cities()[0]
        if self.latitude is not None and self.longitude is not None:
            self.default_city = default_cities()[self.localize_load()]

        for k in self.outputs():
            setattr(self, k, None)
        self.update_types()

    def log_post(self, json_POST):
        with open(self.file_post_input, 'w') as file_post:
            json.dump(json_POST, file_post)

    def get_path_run(self):
        return self.path_run

    def get_path_run_inputs(self):
        return self.path_run_inputs

    def get_path_run_outputs(self):
        return self.path_run_outputs

    def get_path_run_outputs_bau(self):
        return self.path_run_outputs_bau

    def update_types(self):
        for group in [self.inputs(full_list=True), self.outputs()]:
            for k, v in group.items():
                value = getattr(self, k)

                if value is not None:
                    if v['type'] == float:
                        if v['pct']:
                            if value > 1.0:
                                setattr(self, k, float(value) * 0.01)

                    elif v['type'] == list:
                        if 'listtype' in v:
                            if v['listtype'] != str:
                                value = [float(i) for i in getattr(self, k)]
                                setattr(self, k, value)
                    else:
                        setattr(self, k, v['type'](value))

    def get_subtask_inputs(self, name):
        output = {}
        defaults = self.inputs(filter=name)

        for k in defaults.keys():
            output[k] = getattr(self, k)
            if output[k] is None:
                default = defaults[k].get('default')
                if default is not None:
                    output[k] = default

        return output

    def run(self):

        self.create_simple_bau()
        self.create_constants()
        self.create_storage()
        self.create_size_limits()
        self.create_economics()
        self.create_loads()
        self.create_GIS()
        self.create_nem()
        self.create_utility()

        run_command = self.create_run_command(self.path_run_outputs, self.xpress_model, self.DAT, False)
        run_command_bau = self.create_run_command(self.path_run_outputs_bau, self.xpress_model, self.DAT_bau, True)

        log("INFO", "Initializing Command")
        command = Command(run_command)
        log("INFO", "Initializing Command BAU")
        command_bau = Command(run_command_bau)

        log("INFO", "Running Command")
        run1 = command.run(self.timeout)
        if not run1 == True:
            return {"ERROR":run1}
        log("INFO", "Running BAU")

        run2 = command_bau.run(self.timeout)
        if not run2 == True:
            return {"ERROR":run2}

        self.parse_run_outputs()
        self.cleanup()
        return self.lib_output()

    def lib_output(self):
        output = {'run_input_id': self.run_input_id}
        for k in self.inputs(full_list=True).keys() + self.outputs().keys():
            if hasattr(self, k):
                output[k] = getattr(self, k)
            else:
                output[k] = None
        return output

    def create_run_command(self, path_output, xpress_model, DATs, base_case):

        log("DEBUG", "Current Directory: " + os.getcwd())
        log("INFO", "Creating output directory: " + path_output)

        # base case
        base_string = ""
        if base_case:
            base_string = "Base"

        # RE case
        header = 'exec '
        header += os.path.join(self.path_xpress, xpress_model)

        # Command line constants and Dat file overrides
        outline = ''
        for constant in self.command_line_constants:
            outline = ' '.join([outline, constant.strip('\n')])

        for dat_file in DATs:
            if dat_file is not None:
                outline = ' '.join([outline, dat_file.strip('\n')])

        outline.replace('\n', '')

        cmd = r"mosel %s %s OutputDir='%s' DatLibraryPath='%s' ScenarioPath='%s' BaseString='%s'" \
                 % (header, outline, path_output, self.path_dat_library, self.path_run_inputs, base_string)

        log("DEBUG", "Returning Process Command " + cmd)

        # write a cmd file for easy debugging
        filename = self.file_cmd_input
        if base_case:
            filename = self.file_cmd_input_bau

        f = open(filename, 'w')
        f.write(cmd)
        f.close()

        return cmd

    def parse_run_outputs(self):

        if os.path.exists(self.file_output):
            process_results = results.Results(self.path_run_outputs, self.path_run_outputs_bau, self.economics, self.load_year)
            process_results.run()

            for k in self.outputs():
                val = getattr(process_results, k)
                setattr(self, k, val)
        else:
            log("DEBUG", "Current directory: " + os.getcwd())
            log("WARNING", "Output file: " + self.file_output + " + doesn't exist!")

    def cleanup(self):
        return
        log("INFO", "Cleaning up folders from: " + os.getcwd())
        log("DEBUG", "Output folder: " + self.path_run_outputs)

        if not self.debug:
            for f in [self.path_run_output]:
                if os.path.exists(f):
                    shutil.rmtree(f, ignore_errors=True)

            for p in [self.file_economics, self.file_economics_bau, self.file_gis, self.file_gis_bau,
                      self.file_load_profile, self.file_load_size]:
                if os.path.exists(p):
                    os.remove(p)


    # BAU files
    def create_simple_bau(self):
        self.DAT_bau[0] = "DAT1=" + "'" + self.file_constant_bau + "'"
        self.DAT_bau[5] = "DAT6=" + "'" + self.file_storage_bau + "'"
        self.DAT_bau[6] = "DAT7=" + "'" + self.file_max_size_bau + "'"

        shutil.copyfile(os.path.join(self.folder_various, 'constant_bau.dat'), self.file_constant_bau)
        shutil.copyfile(os.path.join(self.folder_various, 'storage_bau.dat'), self.file_storage_bau)
        shutil.copyfile(os.path.join(self.folder_various, 'maxsizes_bau.dat'), self.file_max_size_bau)

    # Constant file
    def create_constants(self):

        can_grid_charge = getattr(self, "batt_can_gridcharge", 1)

        Tech = ['PV', 'PVNM', 'UTIL1']
        TechIsGrid = [0, 0, 1]
        Load = ['1R', '1W', '1X', '1S']
        TechToLoadMatrix = [1, 1, 1, 1, \
                            1, 1, 1, 1, \
                            1, 0, 0, int(can_grid_charge)]
        TechClass = ['PV', 'UTIL']
        NMILRegime = ['BelowNM', 'NMtoIL', 'AboveIL']
        TechToNMILMapping = [1, 0, 0, \
                             0, 1, 0, \
                             0, 0, 0]
        TurbineDerate = [1, 1, 0]
        TechToTechClassMatrix = [1, 0, \
                                 1, 0, \
                                 0, 0]

        self.DAT[0] = "DAT1=" + "'" + self.file_constant + "'"
        write_single_variable(self.file_constant, Tech, 'Tech')
        write_single_variable(self.file_constant, TechIsGrid, 'TechIsGrid', 'a')
        write_single_variable(self.file_constant, Load, 'Load', 'a')
        write_single_variable(self.file_constant, TechToLoadMatrix, 'TechToLoadMatrix', 'a')
        write_single_variable(self.file_constant, TechClass, 'TechClass', 'a')
        write_single_variable(self.file_constant, NMILRegime, 'NMILRegime', 'a')
        write_single_variable(self.file_constant, TechToNMILMapping, 'TechToNMILMapping', 'a')
        write_single_variable(self.file_constant, TurbineDerate, 'TurbineDerate', 'a')
        write_single_variable(self.file_constant, TechToTechClassMatrix, 'TechToTechClassMatrix', 'a')

    # storage
    def create_storage(self):
        self.DAT[5] = "DAT6=" + "'" + self.file_storage + "'"
        shutil.copyfile(os.path.join(self.folder_various, 'storage.dat'), self.file_storage)

    # DAT2 - Economics
    def create_economics(self):

        econ_inputs = self.get_subtask_inputs('economics')

        fp = self.file_economics
        self.economics = economics.Economics(econ_inputs, file_path=fp, business_as_usual=False)

        for k in ['analysis_period', 'pv_cost', 'pv_om', 'batt_cost_kw', 'batt_replacement_cost_kw',
                  'batt_replacement_cost_kwh', 'owner_discount_rate', 'offtaker_discount_rate', 'owner_tax_rate',
                  'pv_levelization_factor', 'cap_cost_segments']:
            setattr(self, k, getattr(self.economics, k))

        self.DAT[1] = "DAT2=" + "'" + self.file_economics + "'"

        fp = self.file_economics_bau
        econ = economics.Economics(econ_inputs, file_path=fp, business_as_usual=True)

        self.DAT_bau[1] = "DAT2=" + "'" + self.file_economics_bau + "'"
        self.command_line_constants.append("CapCostSegCount=" + str(self.cap_cost_segments))

    # DAT3 & DAT4 LoadSize, LoadProfile
    def create_loads(self):

        default_load_profile = "Load8760_raw_" + self.default_city + "_" + self.default_building + ".dat"
        default_load_profile_norm = "Load8760_norm_" + self.default_city + "_" + self.default_building + ".dat"
        default_load_size = "LoadSize_" + self.default_city + "_" + self.default_building + ".dat"

        load_profile = None

        log("INFO", "Creating loads.  "
                     "LoadSize: " + ("None" if self.load_size is None else str(self.load_size)) +
            ", LoadProfile: " + ("None" if self.load_profile_name is None else self.load_profile_name) +
            ", Load 8760 Specified: " + ("No" if self.load_8760_kw is None else "Yes") +
            ", Load Monthly Specified: " + ("No" if self.load_monthly_kwh is None else "Yes"))

        if self.load_8760_kw is not None:  # user load profile

            if len(self.load_8760_kw) == 8760:

                self.load_size = sum(self.load_8760_kw)
                write_single_variable(self.file_load_size, self.load_size, "AnnualElecLoad")
                load_profile = self.load_8760_kw

            else:
                log("ERROR", "Load profile uploaded contains: " + len(self.load_8760_kw) + " values, 8760 required")

        if self.load_monthly_kwh is not None:

            if len(self.load_monthly_kwh) == 12:
                self.load_size = float(sum(self.load_monthly_kwh))
                write_single_variable(self.file_load_size, self.load_size, "AnnualElecLoad")

                if (self.load_profile_name is not None) and (
                    self.load_profile_name.lower() in self.default_load_profiles):
                    name = "Load8760_norm_" + self.default_city + "_" + self.load_profile_name + ".dat"
                    path = os.path.join(self.folder_load_profile, name)
                    load_profile = self.scale_load_by_month(path)
                else:
                    path = os.path.join(self.folder_load_profile, default_load_profile_norm)
                    load_profile = self.scale_load_by_month(path)

            else:
                log("ERROR",
                    "Load monthly kWh uploaded contains: " + str(len(self.load_monthly_kwh)) + " values, 12 required")

        if self.load_8760_kw is None and self.load_monthly_kwh is None:

            if self.load_size is None:  # use defaults

                self.file_load_size = os.path.join(self.folder_load_size, default_load_size)
                self.file_load_profile = os.path.join(self.folder_load_profile, default_load_profile)
                # nlaws: why is no load_profile defined here?

                # Load profile with no load size
                if self.load_profile_name is not None:
                    if self.load_profile_name.lower() in self.default_load_profiles:
                        filename_profile = "Load8760_raw_" + self.default_city + "_" + self.load_profile_name + ".dat"
                        filename_size = "LoadSize_" + self.default_city + "_" + self.load_profile_name + ".dat"
                        self.file_load_size = os.path.join(self.folder_load_size, filename_size)
                        self.file_load_profile = os.path.join(self.folder_load_profile, filename_profile)
                        # nlaws: why is no load_profile defined here?

            else:  # load_size provided
                write_single_variable(self.file_load_size, self.load_size, "AnnualElecLoad")

                # Load profile specified, with load size specified
                if self.load_profile_name is not None:
                    if self.load_profile_name.lower() in self.default_load_profiles:
                        tmp_profile = os.path.join(self.folder_load_profile,
                                                   "Load8760_norm_" + self.default_city + "_" + self.load_profile_name + ".dat")
                        load_profile = self.scale_load(tmp_profile, self.load_size)

                # Load size specified, no profile
                else:
                    p = os.path.join(self.folder_load_profile, default_load_profile)
                    load_profile = self.scale_load(p, self.load_size)

        if load_profile:

            # resilience: modify load during outage with crit_load_factor
            if self.crit_load_factor and self.outage_start and self.outage_end:  # default values are None
                load_profile = load_profile[0:self.outage_start] \
                                + [ld * self.crit_load_factor for ld in load_profile[self.outage_start:self.outage_end]] \
                                + load_profile[self.outage_end:]

            # fill in W, X, S bins
            for _ in range(8760 * 3):
                load_profile.append(self.max_big_number)

            write_single_variable(self.file_load_profile, load_profile, "LoadProfile")

        self.DAT[2] = "DAT3=" + "'" + self.file_load_size + "'"
        self.DAT_bau[2] = self.DAT[2]
        self.DAT[3] = "DAT4=" + "'" + self.file_load_profile + "'"
        self.DAT_bau[3] = self.DAT[3]

    def scale_load(self, file_load_profile, scale_factor):

        load_profile = []
        f = open(file_load_profile, 'r')
        for line in f:
            load_profile.append(float(line.strip('\n')) * scale_factor)

        return load_profile

    def scale_load_by_month(self, profile_file):

        load_profile = []
        f = open(profile_file, 'r')

        datetime_current = datetime(self.load_year, 1, 1, 0)
        month_total = 0
        month_scale_factor = []
        normalized_load = []

        for line in f:
            month = datetime_current.month
            normalized_load.append(float(line.strip('\n')))
            month_total += self.load_size * float(line.strip('\n'))

            # add an hour
            datetime_current = datetime_current + timedelta(0, 0, 0, 0, 0, 1, 0)

            if month != datetime_current.month:
                if month_total == 0:
                    month_scale_factor.append(0)
                else:
                    month_scale_factor.append(float(self.load_monthly_kwh[month - 1] / month_total))
                month_total = 0

                log("DEBUG", "Monthly kwh: " + str(self.load_monthly_kwh[month - 1]) +
                    ", Month scale factor: " + str(month_scale_factor[month - 1]) +
                    ", Annual load: " + str(self.load_size))

        datetime_current = datetime(self.load_year, 1, 1, 0)
        for load in normalized_load:
            month = datetime_current.month

            load_profile.append(self.load_size * load * month_scale_factor[month - 1])

            # add an hour
            datetime_current = datetime_current + timedelta(0, 0, 0, 0, 0, 1, 0)

        return load_profile

    def localize_load(self):

        min_distance = self.max_big_number
        min_index = 0

        idx = 0
        for _ in default_cities():
            lat = default_latitudes()[idx]
            lon = default_longitudes()[idx]
            lat_dist = self.latitude - lat
            lon_dist = self.longitude - lon

            distance = math.sqrt(math.pow(lat_dist, 2) + math.pow(lon_dist, 2))
            if distance < min_distance:
                min_distance = distance
                min_index = idx

            idx += 1

        return min_index

    def create_GIS(self):

        if self.latitude is not None and self.longitude is not None:
            pv_inputs = self.get_subtask_inputs('pvwatts')
            GIS = pvwatts.PVWatts(self.path_run_inputs, self.run_input_id, pv_inputs, self.pv_levelization_factor,
                                  outage_start=self.outage_start, outage_end=self.outage_end)

            self.DAT[4] = "DAT5=" + "'" + self.file_gis + "'"
            self.DAT_bau[4] = "DAT5=" + "'" + self.file_gis_bau + "'"

    def create_size_limits(self):

        acres_per_MW = 6
        squarefeet_to_acre = 0.0002471
        total_acres = 0

        # Internal working defaults, probably need to revamp and move to api_definitions.py
        pv_kw_min = 0
        pv_kw_max = 200000
        util_kw_max = 12000000

        batt_kw_min = 0
        batt_kwh_min = 0
        batt_kw_max = 10000
        batt_kwh_max = 10000


        # pv max size based on user input
        if self.pv_kw_max is not None:
            pv_kw_max = self.pv_kw_max
        else:
            # don't restrict unless they specify both land_area and roof_area, otherwise one of them is "unlimited" in UI
            if self.roof_area is not None and self.land_area is not None:
                total_acres += (self.roof_area * squarefeet_to_acre) + self.land_area
                pv_kw_max = (total_acres / acres_per_MW) * 1000

        if self.pv_kw_min is not None:
            pv_kw_min = self.pv_kw_min

        if pv_kw_min > pv_kw_max:
            pv_kw_min = pv_kw_max

        # battery constraints
        if self.batt_kw_max is not None:
            batt_kw_max = self.batt_kw_max
        if self.batt_kwh_max is not None:
            batt_kwh_max = self.batt_kwh_max
        if self.batt_kw_min is not None:
            batt_kw_min = self.batt_kw_min
        if self.batt_kwh_min is not None:
            batt_kwh_min = self.batt_kwh_min

        # update outputs
        self.pv_kw_min = pv_kw_min
        self.pv_kw_max = pv_kw_max
        self.batt_kwh_min = batt_kwh_min
        self.batt_kwh_max = batt_kwh_max
        self.batt_kw_min = batt_kw_min
        self.batt_kw_max = batt_kw_max

        MaxSize = [pv_kw_max, pv_kw_max, util_kw_max]
        MinStorageSizeKW = batt_kw_min
        MinStorageSizeKWH = batt_kwh_min
        MaxStorageSizeKW = batt_kw_max
        MaxStorageSizeKWH = batt_kwh_max
        TechClassMinSize = [pv_kw_min, 0]

        write_single_variable(self.file_max_size, MaxSize, "MaxSize", 'a')
        write_single_variable(self.file_max_size, MinStorageSizeKW, "MinStorageSizeKW", 'a')
        write_single_variable(self.file_max_size, MaxStorageSizeKW, "MaxStorageSizeKW", 'a')
        write_single_variable(self.file_max_size, MinStorageSizeKWH, "MinStorageSizeKWH", 'a')
        write_single_variable(self.file_max_size, MaxStorageSizeKWH, "MaxStorageSizeKWH", 'a')
        write_single_variable(self.file_max_size, TechClassMinSize, "TechClassMinSize", 'a')

        self.DAT[6] = "DAT7=" + "'" + self.file_max_size + "'"

    def create_utility(self):

        if self.urdb_rate is not None:
            log("INFO", "Parsing URDB rate")
            self.parse_urdb(self.urdb_rate)
        else:
            if None not in [self.blended_utility_rate, self.demand_charge]:
                log("INFO", "Making URDB rate from blended data")
                urdb_rate = self.make_urdb_rate(self.blended_utility_rate, self.demand_charge)
                self.parse_urdb(urdb_rate)

        if self.utility_name is not None and self.rate_name is not None:
            self.path_util_rate = os.path.join(self.path_utility, self.utility_name, self.rate_name)

            with open(os.path.join(self.path_util_rate, "NumRatchets.dat"), 'r') as f:
                num_ratchets = str(f.readline())

            with open(os.path.join(self.path_util_rate, "bins.dat"), 'r') as f:
                fuel_bin_count = str(f.readline())
                demand_bin_count = str(f.readline())

            self.command_line_constants.append(num_ratchets)
            self.command_line_constants.append("UtilName=" + "'" + str(self.utility_name) + "'")
            self.command_line_constants.append("UtilRate=" + "'" + str(self.rate_name) + "'")
            self.command_line_constants.append(fuel_bin_count)
            self.command_line_constants.append(demand_bin_count)

    def parse_urdb(self, urdb_rate):

        utility_name = alphanum(urdb_rate['utility'])
        rate_name = alphanum(urdb_rate['name'])

        base_folder = os.path.join(self.path_utility, utility_name)
        rate_output_folder = os.path.join(base_folder, rate_name)

        if os.path.exists(base_folder):
            shutil.rmtree(base_folder)

        for f in [self.path_utility, base_folder, rate_output_folder]:
            os.mkdir(f)

        check_directory_created(self.path_utility)
        check_directory_created(base_folder)
        check_directory_created(rate_output_folder)

        with open(os.path.join(rate_output_folder, 'json.txt'), 'w') as outfile:
            json.dump(urdb_rate, outfile)
            outfile.close()

        with open(os.path.join(rate_output_folder, 'rate_name.txt'), 'w') as outfile:
            outfile.write(str(rate_name).replace(' ', '_'))
            outfile.close()

        urdb_parse = UrdbParse(self.path_utility, self.load_year, self.time_steps_per_hour,
                               self.net_metering, self.wholesale_rate)
        urdb_parse.parse_specific_rates([utility_name], [rate_name])

        # Copy hourly rate summary to outputs
        if os.path.exists(urdb_parse.utility_dat_files.path_hourly_summary):
            shutil.copyfile(urdb_parse.utility_dat_files.path_hourly_summary,
                            os.path.join(self.path_run_outputs, urdb_parse.utility_dat_files.name_hourly_summary))
            shutil.copyfile(urdb_parse.utility_dat_files.path_hourly_summary,
                            os.path.join(self.path_run_outputs_bau, urdb_parse.utility_dat_files.name_hourly_summary))

        self.utility_name = utility_name
        self.rate_name = rate_name

    def make_urdb_rate(self, blended_utility_rate, demand_charge):

        urdb_rate = {}

        # energy rate
        energyratestructure = []
        energyweekdayschedule = []
        energyweekendschedule = []

        flatdemandstructure = []
        flatdemandmonths = []

        unique_energy_rate = set(blended_utility_rate)
        unique_demand_rate = set(demand_charge)

        for energy_rate in unique_energy_rate:
            rate = [{'rate': energy_rate, 'unit': 'kWh'}]
            energyratestructure.append(rate)

        for demand_rate in unique_demand_rate:
            rate = [{'rate': demand_rate}]
            flatdemandstructure.append(rate)

        for month in range(0, 12):
            energy_period = 0
            demand_period = 0
            for energy_rate in unique_energy_rate:
                if energy_rate == blended_utility_rate[month]:
                    tmp = [energy_period] * 24
                    energyweekdayschedule.append(tmp)
                    energyweekendschedule.append(tmp)
                energy_period += 1
            for demand_rate in unique_demand_rate:
                if demand_rate == demand_charge[month]:
                    flatdemandmonths.append(demand_period)
                demand_period += 1

        # ouput
        urdb_rate['energyweekdayschedule'] = energyweekdayschedule
        urdb_rate['energyweekendschedule'] = energyweekendschedule
        urdb_rate['energyratestructure'] = energyratestructure

        if sum(unique_demand_rate) > 0:
            urdb_rate['flatdemandstructure'] = flatdemandstructure
            urdb_rate['flatdemandmonths'] = flatdemandmonths
            urdb_rate['flatdemandunit'] = 'kW'

        urdb_rate['label'] = self.run_input_id
        urdb_rate['name'] = "Custom_rate_" + str(self.run_input_id)
        urdb_rate['utility'] = "Custom_utility_" + str(self.run_input_id)
        return urdb_rate

    def create_nem(self):

        net_metering_limit = 0
        interconnection_limit = 1000000

        nem_input = getattr(self, "net_metering_limit")
        ic_input = getattr(self, "interconnection_limit")

        if nem_input is not None:
            net_metering_limit = nem_input
        if ic_input is not None:
            interconnection_limit = ic_input
        if net_metering_limit > 0:
            self.net_metering = True

        # check on if NM, IC are in right spot
        write_single_variable(self.file_NEM,
                                   [net_metering_limit, interconnection_limit, self.max_big_number],
                                   "NMILLimits")

        self.DAT[16] = "DAT17=" + "'" + self.file_NEM + "'"
