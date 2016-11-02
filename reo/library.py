# python libraries
import os
import traceback
import shutil
import math
import pandas as pd
from datetime import datetime, timedelta

# logging
from log_levels import log
import logging

# user defined
import economics
import pvwatts
from api_definitions import *

from urdb_parse import *
from exceptions import SubprocessTimeoutError
from utilities import Command

class DatLibrary:

    max_big_number = 100000000
    timeout = 60
    timed_out = False

    # if need to debug, change to True, outputs OUT files, GO files, debugging to cmdline
    debug = True
    logfile = "reopt_api.log"
    xpress_model = "REoptTS1127_PVBATT72916.mos"
    xpress_model_bau = "REoptTS1127_Util_Only.mos"
    year = 2017
    time_steps_per_hour = 1

    # directory structure
    path_egg = []
    path_xpress = []
    path_logfile = []
    path_dat_library = []
    path_util_rate = []
    path_various = []
    path_load_size = []
    path_load_profile = []
    path_gis_data = []
    path_economics = []
    path_utility = []
    path_output = []
    path_output_bau = []
    path_dat_library_relative = []

    file_run = []
    file_run_bau = []
    file_output = []
    file_output_bau = []
    file_economics = []
    file_economics_bau = []
    file_gis = []
    file_gis_bau = []
    file_load_size = []
    file_load_profile = []

    # DAT files to overwrite
    DAT = [None] * 20
    DAT_bau = [None] * 20

    @staticmethod
    def write_var(f, var, dat_var):
        f.write(dat_var + ": [\n")
        if isinstance(var, list):
            for i in var:
                f.write(str(i) + "\t,\n")
        else:
            f.write(str(var) + "\t,\n")
        f.write("]\n")

    def write_single_variable(self, path, filename, var, dat_var):
        filename_path = os.path.join(path, filename)
        log("DEBUG", "Writing " + dat_var + " to " + filename_path)
        if filename not in os.listdir(path):
            f = open(filename_path, 'w')
            self.write_var(f, var, dat_var)
            f.close()

    def __init__(self, inputs, internals):

        for k in internals().keys():
            setattr(self, k, internals.get(k))

        for k,v in inputs(full_list=True):
            setattr(self, k, internals.get(k))

            if k=='analysis_period' and internals.get(k) < 0:
                setattr(self, k, None)

            elif k == 'load_profile' and internals.get(k) is not None:
                setattr(self, k, internals.get(k).replace(" ", ""))

            setattr(self, k, internals.get(k))

        self.default_load_profiles = [p.lower() for p in default_load_profiles()]

        self.update_types()
        self.define_paths()
        self.setup_logging()

    def update_types(self):

        for k,v in inputs(full_list=True):

            if v['type']==float:
                value = float(getattr(self,k))
                if v['pct']:
                    if value > 1.0:
                        setattr(self, k, value*0.01)
                else:
                    setattr(self,k,value)

            if v['type']==int:
                setattr(self,k,int(getattr(self,k)))

            if v['type'] == str:
                setattr(self, k, str(getattr(self, k)))

            if v['type'] == list:
                value = [float(i) for i in getattr(self, k)]
                setattr(self, k, value)

    def get_subtask_inputs(self,name):
        output = {}
        defaults = inputs(filter=name)

        for k in defaults.keys():
            output[k] = getattr(self,k)
            if output[k] is None:
                output[k] = defaults[k]['default']

        return output

    def run(self):

        self.create_or_load()
        self.create_run_file()

        command = Command(self.file_run)
        command_bau = Command(self.file_run_bau)

        try:
            command.run(self.timeout)
        except SubprocessTimeoutError:
            self.timed_out = True

        if not self.timed_out:
            try:
                command_bau.run(self.timeout)
            except SubprocessTimeoutError:
                self.timed_out = True

        self.parse_outputs()
        self.cleanup()

        return self.outputs

    def setup_logging(self):
        logging.basicConfig(filename=self.path_logfile,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M%S %p',
                            level=logging.DEBUG)

    def define_paths(self):

        # absolute (anything that needs written out)
        self.path_xpress = os.path.join(self.path_egg, "Xpress")
        self.path_logfile = os.path.join(self.path_egg, 'reopt_api', self.logfile)
        self.path_dat_library = os.path.join(self.path_xpress, "DatLibrary")

        # relative
        self.path_dat_library_relative = os.path.join("Xpress", "DatLibrary")
        self.path_various = os.path.join("Various")
        self.path_economics = os.path.join("Economics")
        self.path_gis_data = os.path.join("GISdata")
        self.path_utility = os.path.join("Utility")
        self.path_load_size = os.path.join("LoadSize")
        self.path_load_profile = os.path.join("LoadProfiles")
        self.path_output = os.path.join("Xpress", "Output", "Run_" + str(self.run_id))
        self.path_output_bau = os.path.join(self.path_output, "bau")

        self.file_run = os.path.join(self.path_xpress, "Go_" + str(self.run_id) + ".bat")
        self.file_run_bau = os.path.join(self.path_xpress, "Go_" + str(self.run_id) + "_bau.bat")
        self.file_output = os.path.join(self.path_output, "summary.csv")
        self.file_output_bau = os.path.join(self.path_output_bau, "summary.csv")
        self.file_economics = os.path.join(self.path_economics, 'economics_' + str(self.run_id) + '.dat')
        self.file_economics_bau = os.path.join(self.path_economics, 'economics_' + str(self.run_id) + '_bau.dat')
        self.file_gis = os.path.join(self.path_gis_data, 'GIS_' + str(self.run_id) + '.dat')
        self.file_gis_bau = os.path.join(self.path_gis_data, 'GIS_' + str(self.run_id) + '_bau.dat')
        self.file_load_size = os.path.join(self.path_load_size, 'LoadSize_' + str(self.run_id) + '.dat')
        self.file_load_profile = os.path.join(self.path_load_profile, 'Load8760_' + str(self.run_id) + '.dat')

    def create_or_load(self):

        self.create_constant_bau()
        self.create_economics()
        self.create_loads()
        self.create_GIS()
        self.create_utility()

    def create_run_file(self):

        log("DEBUG", "Current Directory: " + os.getcwd())
        log("DEBUG", "Creating output directory: " + self.path_output)
        log("DEBUG", "Created run file: " + self.file_run)

        path_output = os.path.join(self.path_egg, self.path_output)
        path_output_bau = os.path.join(self.path_egg, self.path_output_bau)

        if os.path.exists(path_output):
            shutil.rmtree(path_output)

        os.mkdir(path_output)
        os.mkdir(path_output_bau)

        # RE case
        header = 'mosel -c "exec ' + os.path.join(self.path_xpress, self.xpress_model)
        output = "OUTDIR=" + "'" + self.path_output + "'"
        outline = ''

        for dat_file in self.DAT:
            if dat_file is not None:
                outline = ', '.join([outline, dat_file.strip('\n')])
        outline = ', '.join([outline, output])
        outline.replace('\n', '')
        outline = '  '.join([header, outline]) + '\n'

        f = open(self.file_run, 'w')
        f.write(outline)
        f.close()

        #BAU
        header = 'mosel -c "exec ' + os.path.join(self.path_xpress, self.xpress_model_bau)
        output = "OUTDIR=" + "'" + self.path_output_bau + "'"
        outline = ''

        for dat_file in self.DAT_bau:
            if dat_file is not None:
                outline = ', '.join([outline, dat_file.strip('\n')])
        outline = ', '.join([outline, output])
        outline.replace('\n', '')
        outline = '  '.join([header, outline]) + '\n'

        f = open(self.file_run_bau, 'w')
        f.write(outline)
        f.close()

    def parse_outputs(self):

        if os.path.exists(os.path.join(self.path_egg, self.file_output)):
            df = pd.read_csv(os.path.join(self.path_egg, self.file_output), header=None, index_col=0)
            df = df.transpose()
            self.outputs = {}
            pv_size = 0
            if 'LCC' in df.columns:
                self.outputs['lcc'] = df['LCC']
            if 'BattInverter_kW' in df.columns:
                self.outputs['batt_kw'] = df['BattInverter_kW']
            if 'BattSize_kWh' in df.columns:
                self.outputs['batt_kwh'] = df['BattSize_kWh']
            if 'PVNMsize_kW' in df.columns:
                pv_size += float(df['PVNMsize_kW'])
            if 'PVsize_kW' in df.columns:
                pv_size += float(df['PVsize_kW'])
            if 'Utility_kWh' in df.columns:
                self.outputs['utility_kwh'] = df['Utility_kWh']

            if pv_size > 0:
                self.outputs['pv_kw'] = str(round(pv_size, 0))

        else:
            log("DEBUG", "Current directory: " + os.getcwd())
            log("WARNING", "Output file: " + self.file_output + " + doesn't exist!")

        if os.path.exists(os.path.join(self.path_egg, self.file_output_bau)):
            df = pd.read_csv(os.path.join(self.path_egg, self.file_output_bau), header=None, index_col=0)
            df = df.transpose()

            if 'LCC' in df.columns:
                self.outputs['npv'] = float(df['LCC']) - float(self.outputs['lcc'])

    def cleanup(self):

        log("DEBUG", "Cleaning up folders from: " + os.getcwd())
        log("DEBUG", "Output folder: " + self.path_output)

        if not self.debug:
            for f in [os.path.join(self.path_egg, self.path_output)]:
                if os.path.exists(f):
                    shutil.rmtree(f, ignore_errors=True)

            for p in [self.file_run, self.file_run_bau,
                        os.path.join(self.path_dat_library, self.file_economics),
                        os.path.join(self.path_dat_library, self.file_economics_bau),
                        os.path.join(self.path_dat_library, self.file_gis),
                        os.path.join(self.path_dat_library, self.file_gis_bau),
                        os.path.join(self.path_dat_library, self.file_load_profile),
                        os.path.join(self.path_dat_library, self.file_load_size)]:
                if os.path.exists(p):
                    os.remove(p)

    # BAU files
    def create_constant_bau(self):
        self.DAT_bau[0] = "DAT1=" + "'" + os.path.join(self.path_various, 'constant_bau.dat') + "'"
        self.DAT_bau[5] = "DAT6=" + "'" + os.path.join(self.path_various, 'storage_bau.dat') + "'"
        self.DAT_bau[6] = "DAT7=" + "'" + os.path.join(self.path_various, 'maxsizes_bau.dat') + "'"

    # DAT2 - Economics
    def create_economics(self):

        econ_inputs = self.get_subtask_inputs('economics')

        file_path = os.path.join(self.path_dat_library, self.file_economics)
        econ = economics.Economics(econ_inputs, file_path=file_path,business_as_usual=False)

        for k in ['analysis_period','pv_cost','pv_om','batt_cost_kw','batt_replacement_cost_kw',
                  'batt_replacement_cost_kwh','owner_discount_rate','offtaker_discount_rate']:
           setattr(self, k, getattr(econ,k))

        self.DAT[1] = "DAT2=" + "'" + self.file_economics + "'"


        file_path = os.path.join(self.path_dat_library, self.file_economics_bau)
        econ = economics.Economics(econ_inputs, file_path=file_path, business_as_usual=True)
        self.DAT_bau[1] = "DAT2=" + "'" + self.file_economics_bau + "'"

    # DAT3 & DAT4 LoadSize, LoadProfile
    def create_loads(self):

        filename_profile = []
        filename_size = []

        default_city = default_cities()[0]
        if self.latitude is not None and self.longitude is not None:
            default_city = default_cities()[self.localize_load()]

        default_building = inputs(full_list=True)['building_type']
        default_load_profile = "Load8760_raw_" + default_city + "_" + default_building + ".dat"
        default_load_profile_norm = "Load8760_norm_" + default_city + "_" + default_building + ".dat"
        default_load_size = "LoadSize_" + default_city + "_" + default_building + ".dat"

        log("DEBUG", "Creating loads.  "
                     "LoadSize: " + ("None" if self.load_size is None else str(self.load_size)) +
                     ", LoadProfile: " + ("None" if self.load_profile is None else self.load_profile) +
                     ", Load 8760 Specified: " + ("No" if self.load_8760_kw is None else "Yes") +
                     ", Load Monthly Specified: " + ("No" if self.load_monthly_kwh is None else "Yes"))

        custom_profile = False
        if self.load_8760_kw is not None:
            if len(self.load_8760_kw) == 8760:
                custom_profile = True
                load_size = sum(self.load_8760_kw)
                self.load_size = load_size
                filename_size = "LoadSize_" + str(self.run_id) + ".dat"
                self.write_single_variable(os.path.join(self.path_dat_library, self.path_load_size),
                                           filename_size, load_size, "AnnualElecLoad")
                filename_profile = "LoadProfile_" + str(self.run_id) + ".dat"
                self.write_single_variable(os.path.join(self.path_dat_library, self.path_load_profile),
                                           filename_profile, self.load_8760_kw, "LoadProfile")
            else:
                log("ERROR", "Load profile uploaded contains: " + len(self.load_8760_kw) + " values, 8760 required")

        if self.load_monthly_kwh is not None:
            if len(self.load_monthly_kwh) == 12:
                custom_profile = True
                load_size = float(sum(self.load_monthly_kwh))
                filename_size = "LoadSize_" + str(self.run_id) + ".dat"
                filename_profile = "LoadProfile_" + str(self.run_id) + ".dat"
                self.write_single_variable(os.path.join(self.path_dat_library, self.path_load_size),
                                           filename_size, load_size, "AnnualElecLoad")
                self.load_size = load_size
                if self.load_profile is not None:
                    if self.load_profile.lower() in self.default_load_profiles:
                        tmp_profile = "Load8760_norm_" + default_city + "_" + self.load_profile + ".dat"
                        self.scale_load_by_month(tmp_profile, filename_profile)
                else:
                    self.scale_load_by_month(default_load_profile_norm, filename_profile)
            else:
                log("ERROR", "Load profile uploaded contains: " + len(self.load_monthly_kwh) + " values, 12 required")

        if not custom_profile:
            if self.load_size is None:

                # Load profile with no load size
                if self.load_profile is not None:
                    if self.load_profile.lower() in self.default_load_profiles:
                        filename_profile = "Load8760_raw_" + default_city + "_" + self.load_profile + ".dat"
                        filename_size = "LoadSize_" + default_city + "_" + self.load_profile + ".dat"
                # No load profile or size specified
                else:
                    filename_profile = default_load_profile
                    filename_size = default_load_size
            else:

                filename_profile = "Load8760_" + str(self.run_id) + ".dat"
                filename_size = "LoadSize_" + str(self.run_id) + ".dat"
                self.write_single_variable(os.path.join(self.path_dat_library, self.path_load_size),
                                           filename_size, self.load_size, "AnnualElecLoad")

                # Load profile specified, with load size specified
                if self.load_profile is not None:
                    if self.load_profile.lower() in self.default_load_profiles:
                        tmp_profile = "Load8760_norm_" + default_city + "_" + self.load_profile + ".dat"
                        self.scale_load(tmp_profile, filename_profile, self.load_size)
                # Load size specified, no profile
                else:
                    self.scale_load(default_load_profile_norm, filename_profile, self.load_size)

        self.DAT[2] = "DAT3=" + "'" + os.path.join(self.path_load_size, filename_size) + "'"
        self.DAT_bau[2] = self.DAT[2]
        self.DAT[3] = "DAT4=" + "'" + os.path.join(self.path_load_profile, filename_profile) + "'"
        self.DAT_bau[3] = self.DAT[3]

    def scale_load(self, file_norm, filename_profile, scale_factor):
        path_load_profile = os.path.join(self.path_dat_library, self.path_load_profile)
        load_profile = []
        f = open(os.path.join(path_load_profile, file_norm), 'r')
        for line in f:
            load_profile.append(float(line.strip('\n')) * scale_factor)

        # fill in W, X, S bins
        for _ in range(8760*3):
            load_profile.append(self.max_big_number)

        self.write_single_variable(path_load_profile, filename_profile, load_profile, "LoadProfile")

    def scale_load_by_month(self, file_norm, filename_profile):
        path_load_profile = os.path.join(self.path_dat_library, self.path_load_profile)
        load_profile = []
        f = open(os.path.join(path_load_profile, file_norm), 'r')

        datetime_current = datetime(self.year, 1, 1, 0)
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
                month_scale_factor.append(float(self.load_monthly_kwh[month - 1] / month_total))
                month_total = 0

                log("DEBUG", "Monthly kwh: " + str(self.load_monthly_kwh[month - 1]) +
                    ", Month scale factor: " + str(month_scale_factor[month - 1]) +
                    ", Annual load: " + str(self.load_size))

        datetime_current = datetime(self.year, 1, 1, 0)
        for load in normalized_load:
            month = datetime_current.month

            load_profile.append(self.load_size * load * month_scale_factor[month - 1])

            # add an hour
            datetime_current = datetime_current + timedelta(0, 0, 0, 0, 0, 1, 0)

        # fill in W, X, S bins
        for _ in range(8760*3):
            load_profile.append(self.max_big_number)

        self.write_single_variable(path_load_profile, filename_profile, load_profile, "LoadProfile")

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

            pv_inputs = self.get_subtask_inputs('pv_watts')

            GIS = pvwatts.PVWatts(self.path_dat_library, self.run_id, pv_inputs)

            self.DAT[4] = "DAT5=" + "'" + os.path.join(self.path_gis_data, GIS.filename_GIS) + "'"
            self.DAT_bau[4] = "DAT5=" + "'" + os.path.join(self.path_gis_data, GIS.filename_GIS_bau) + "'"

    def create_utility(self):

        if self.utility_name is not None and self.rate_name is not None:
            self.path_util_rate = os.path.join(self.path_dat_library, self.path_utility,
                                               self.utility_name, self.rate_name)

            with open(os.path.join(self.path_util_rate, "NumRatchets.dat"), 'r') as f:
                num_ratchets = str(f.readline())
            with open(os.path.join(self.path_util_rate, "bins.dat"), 'r') as f:
                fuel_bin_count = str(f.readline())
                demand_bin_count = str(f.readline())

            self.DAT[7] = num_ratchets
            self.DAT_bau[7] = self.DAT[7]
            self.DAT[8] = "UtilName=" + "'" + str(self.utility_name) + "'"
            self.DAT_bau[8] = self.DAT[8]
            self.DAT[9] = "UtilRate=" + "'" + str(self.rate_name) + "'"
            self.DAT_bau[9] = self.DAT[9]
            self.DAT[10] = fuel_bin_count
            self.DAT_bau[10] = self.DAT[10]
            self.DAT[11] = demand_bin_count
            self.DAT_bau[11] = self.DAT[11]

    def parse_urdb(self, urdb_rate):

        utility_name = urdb_rate['utility'].replace(',', '')
        rate_name = urdb_rate['name'].replace(' ', '_').replace(':', '').replace(',', '')
        folder_name = os.path.join(utility_name, rate_name)

        rate_output_folder = os.path.join(self.path_dat_library, self.path_utility, folder_name)

        if not os.path.isdir(rate_output_folder):
            os.makedirs(rate_output_folder)
        with open(os.path.join(rate_output_folder, 'json.txt'), 'w') as outfile:
            json.dump(urdb_rate, outfile)
            outfile.close()
        with open(os.path.join(rate_output_folder, 'rate_name.txt'), 'w') as outfile:
            outfile.write(str(rate_name).replace(' ', '_'))
            outfile.close()

        log_root = os.path.join(self.path_egg, 'reopt_api')
        urdb_parse = UrdbParse(self.path_dat_library, log_root, self.year, self.time_steps_per_hour)
        urdb_parse.parse_specific_rates([utility_name], [rate_name])

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

        urdb_rate['label'] = self.run_id
        urdb_rate['name'] = "Custom_rate_" + str(self.run_id)
        urdb_rate['utility'] = "Custom_utility_" + str(self.run_id)

        return urdb_rate