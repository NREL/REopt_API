import os
import csv
import subprocess
import traceback
import shutil
from log_levels import log
import logging
import math

import pandas as pd

import economics
import pvwatts
from urdb_parse import *

class DatLibrary:

    max_big_number = 100000000

    # if need to debug, change to True, outputs OUT files, GO files, debugging to cmdline
    debug = True
    logfile = "reopt_api.log"
    xpress_model = "REoptTS1127_PVBATT72916.mos"
    xpress_model_bau = "REoptTS1127_Util_Only.mos"
    year = 2017
    time_steps_per_hour = 1

    run_id = []
    outputs = {}

    # variables that user can pass
    latitude = None
    longitude = None
    load_size = None
    load_profile = None
    utility_name = None
    utility_rate_name = None

    # Economics.dat
    analysis_period = None

    rate_owner_discount = None
    rate_offtaker_discount = None
    rate_inflation = None
    rate_escalation = None
    rate_tax = None
    rate_itc = None
    rate_degradation = None

    batt_cost_kw = None
    batt_cost_kwh = None
    pv_cost = None
    pv_om = None
    batt_replacement_cost_kw = None
    batt_replacement_cost_kwh = None

    flag_macrs = None
    flag_itc = None
    flag_bonus = None
    flag_replace_batt = None

    macrs_years = None
    macrs_itc_reduction = None
    bonus_fraction = None
    batt_replacement_year = None

    # default load profiles
    default_load_profiles = ['FastFoodRest', 'Flat', 'FullServiceRest', 'Hospital', 'LargeHotel', 'LargeOffice',
                             'MediumOffice', 'MidriseApartment', 'Outpatient', 'PrimarySchool', 'RetailStore',
                             'SecondarySchool', 'SmallHotel', 'SmallOffice', 'StripMall', 'Supermarket', 'Warehouse']

    # default locations
    default_city = ['Miami', 'Houston', 'Phoenix', 'Atlanta', 'LosAngeles', 'SanFrancisco', 'LasVegas', 'Baltimore',
                    'Albuquerque', 'Seattle', 'Chicago', 'Boulder', 'Minneapolis', 'Helena', 'Duluth', 'Fairbanks']

    # default latitudes
    default_latitudes = [25.761680, 29.760427, 33.448377, 33.748995, 34.052234, 37.774929, 36.114707, 39.290385,
                         35.085334, 47.606209, 41.878114, 40.014986, 44.977753, 46.588371, 46.786672, 64.837778]

    #default longitudes
    default_longitudes = [-80.191790, -95.369803, -112.074037, -84.387982, -118.243685, -122.419416, -115.172850,
                          -76.612189, -106.605553, -122.332071, -87.629798, -105.270546, -93.265011, -112.024505,
                          -92.100485, -147.716389]

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

    def __init__(self, run_id, path_egg, analysis_period, latitude, longitude, load_size, cost_pv_om, cost_batt_kw,
                 cost_batt_kwh, load_profile, cost_pv, rate_owner_discount, rate_offtaker_discount,
                 utility_name, rate_name):

        self.run_id = run_id
        self.path_egg = path_egg
        if analysis_period and analysis_period > 0:
            self.analysis_period = analysis_period

        self.latitude = latitude
        self.longitude = longitude
        self.load_size = load_size
        self.load_profile = load_profile.replace(" ", "")
        self.pv_om = cost_pv_om
        self.batt_cost_kw = cost_batt_kw
        self.batt_cost_kwh = cost_batt_kwh
        self.pv_cost = cost_pv
        self.rate_owner_discount = rate_owner_discount
        self.rate_offtaker_discount = rate_offtaker_discount
        self.utility_name = utility_name
        self.utility_rate_name = rate_name

        lower_case_profile = []
        for profile in self.default_load_profiles:
            lower_case_profile.append(profile.lower())
        self.default_load_profiles = lower_case_profile

        self.update_types()
        self.define_paths()
        self.setup_logging()

    def update_types(self):

        if self.latitude is not None:
            self.latitude = float(self.latitude)
        if self.longitude is not None:
            self.longitude = float(self.longitude)
        if self.load_size is not None:
            self.load_size = float(self.load_size)
        if self.pv_om is not None:
            self.pv_om = float(self.pv_om)
        if self.batt_cost_kw is not None:
            self.batt_cost_kw = float(self.batt_cost_kw)
        if self.batt_cost_kwh is not None:
            self.batt_cost_kwh = float(self.batt_cost_kwh)
        if self.pv_cost is not None:
            self.pv_cost = float(self.pv_cost)
        if self.rate_owner_discount is not None:
            self.rate_owner_discount = float(self.rate_owner_discount)
        if self.rate_offtaker_discount is not None:
            self.rate_offtaker_discount = float(self.rate_offtaker_discount)
        if self.utility_name is not None:
            self.utility_name = str(self.utility_name)
        if self.utility_rate_name is not None:
            self.utility_rate_name = str(self.utility_rate_name)

    def run(self):

        self.create_or_load()
        self.create_run_file()

        #print ('New subprocess')
        #tracefile = open('traceback.txt', 'a')
        #traceback.print_stack(limit=5, file=tracefile)
        subprocess.call(self.file_run)
        subprocess.call(self.file_run_bau)
        # print ('Subprocess done')

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
                print dat_file.strip('\n')
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

            if 'LCC' in df.columns:
                self.outputs['lcc'] = df['LCC']
            if 'BattInverter_kW' in df.columns:
                self.outputs['batt_kw'] = df['BattInverter_kW']
            if 'BattSize_kWh' in df.columns:
                self.outputs['batt_kwh'] = df['BattSize_kWh']
            if 'PVNMsize_kW' in df.columns:
                self.outputs['pv_kw'] = df['PVNMsize_kW']
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
            if os.path.exists(os.path.join(self.path_egg, self.path_output)):
                shutil.rmtree(os.path.join(self.path_egg, self.path_output), ignore_errors=True)
            if os.path.exists(self.file_run):
                os.remove(self.file_run)
                os.remove(self.file_run_bau)
            if os.path.exists(os.path.join(self.path_dat_library, self.file_economics)):
                os.remove(os.path.join(self.path_dat_library, self.file_economics))
                os.remove(os.path.join(self.path_dat_library, self.file_economics_bau))
            if os.path.exists(os.path.join(self.path_dat_library, self.file_gis)):
                os.remove(os.path.join(self.path_dat_library, self.file_gis))
                os.remove(os.path.join(self.path_dat_library, self.file_gis_bau))
            if os.path.exists(os.path.join(self.path_dat_library, self.file_load_profile)):
                os.remove(os.path.join(self.path_dat_library, self.file_load_profile))
            if os.path.exists(os.path.join(self.path_dat_library, self.file_load_size)):
                os.remove(os.path.join(self.path_dat_library, self.file_load_size))

    # BAU files
    def create_constant_bau(self):
        self.DAT_bau[0] = "DAT1=" + "'" + os.path.join(self.path_various, 'constant_bau.dat') + "'"
        self.DAT_bau[5] = "DAT6=" + "'" + os.path.join(self.path_various, 'storage_bau.dat') + "'"
        self.DAT_bau[6] = "DAT7=" + "'" + os.path.join(self.path_various, 'maxsizes_bau.dat') + "'"

    # DAT2 - Economics
    def create_economics(self):

        file_path = os.path.join(self.path_dat_library, self.file_economics)
        business_as_usual = False
        economics.Economics(file_path, self.flag_macrs, self.flag_itc, self.flag_bonus, self.flag_replace_batt,
                            self.analysis_period, self.rate_inflation, self.rate_offtaker_discount,
                            self.rate_owner_discount, self.rate_escalation, self.rate_tax, self.rate_itc,
                            self.macrs_years, self.macrs_itc_reduction, self.bonus_fraction, self.pv_cost,
                            self.pv_om, self.rate_degradation, self.batt_cost_kw, self.batt_cost_kwh,
                            self.batt_replacement_year, self.batt_replacement_cost_kw, self.batt_replacement_cost_kwh,
                            business_as_usual)

        self.DAT[1] = "DAT2=" + "'" + self.file_economics + "'"

        file_path = os.path.join(self.path_dat_library, self.file_economics_bau)
        business_as_usual = True
        economics.Economics(file_path, self.flag_macrs, self.flag_itc, self.flag_bonus, self.flag_replace_batt,
                            self.analysis_period, self.rate_inflation, self.rate_offtaker_discount,
                            self.rate_owner_discount, self.rate_escalation, self.rate_tax, self.rate_itc,
                            self.macrs_years, self.macrs_itc_reduction, self.bonus_fraction, self.pv_cost,
                            self.pv_om, self.rate_degradation, self.batt_cost_kw, self.batt_cost_kwh,
                            self.batt_replacement_year, self.batt_replacement_cost_kw, self.batt_replacement_cost_kwh,
                            business_as_usual)

        self.DAT_bau[1] = "DAT2=" + "'" + self.file_economics_bau + "'"

    # DAT3 & DAT4 LoadSize, LoadProfile
    def create_loads(self):

        filename_profile = []
        filename_size = []

        default_city = self.default_city[0]
        if self.latitude is not None and self.longitude is not None:
            default_city = self.default_city[self.localize_load()]

        default_building = "Hospital"
        default_load_profile = "Load8760_raw_" + default_city + "_" + default_building + ".dat"
        default_load_profile_norm = "Load8760_norm_" + default_city + "_" + default_building + ".dat"
        default_load_size = "LoadSize_" + default_city + "_" + default_building + ".dat"

        log("DEBUG", "Creating loads.  "
                     "LoadSize: " + ("None" if self.load_size is None else str(self.load_size)) +
                     " LoadProfile: " + ("None" if self.load_profile is None else self.load_profile))

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
                    self.scale_load(tmp_profile, filename_profile)
            # Load size specified, no profile
            else:
                self.scale_load(default_load_profile_norm, filename_profile)

        self.DAT[2] = "DAT3=" + "'" + os.path.join(self.path_load_size, filename_size) + "'"
        self.DAT_bau[2] = self.DAT[2]
        self.DAT[3] = "DAT4=" + "'" + os.path.join(self.path_load_profile, filename_profile) + "'"
        self.DAT_bau[3] = self.DAT[3]

    def scale_load(self, file_norm, filename_profile):
        path_load_profile = os.path.join(self.path_dat_library, self.path_load_profile)
        load_profile = []
        f = open(os.path.join(path_load_profile, file_norm), 'r')
        for line in f:
            load_profile.append(float(line.strip('\n')) * self.load_size)

        # fill in W, X, S bins
        for _ in range(8760*3):
            load_profile.append(self.max_big_number)

        self.write_single_variable(path_load_profile, filename_profile, load_profile, "LoadProfile")

    def localize_load(self):

        min_distance = self.max_big_number
        min_index = 0

        idx = 0
        for _ in self.default_city:
            lat = self.default_latitudes[idx]
            lon = self.default_longitudes[idx]
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
            GIS = pvwatts.PVWatts(self.path_dat_library, self.run_id, self.latitude, self.longitude)
            self.DAT[4] = "DAT5=" + "'" + os.path.join(self.path_gis_data, GIS.filename_GIS) + "'"
            self.DAT_bau[4] = "DAT5=" + "'" + os.path.join(self.path_gis_data, GIS.filename_GIS_bau) + "'"

    def create_utility(self):

        if self.utility_name is not None and self.utility_rate_name is not None:
            self.path_util_rate = os.path.join(self.path_dat_library, self.path_utility,
                                               self.utility_name, self.utility_rate_name)

            with open(os.path.join(self.path_util_rate, "NumRatchets.dat"), 'r') as f:
                num_ratchets = str(f.readline())
            with open(os.path.join(self.path_util_rate, "bins.dat"), 'r') as f:
                fuel_bin_count = str(f.readline())
                demand_bin_count = str(f.readline())

            self.DAT[7] = num_ratchets
            self.DAT_bau[7] = self.DAT[7]
            self.DAT[8] = "UtilName=" + "'" + str(self.utility_name) + "'"
            self.DAT_bau[8] = self.DAT[8]
            self.DAT[9] = "UtilRate=" + "'" + str(self.utility_rate_name) + "'"
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
        self.utility_rate_name = rate_name

    def make_urdb_rate(self, blended_utility_rate, demand_charge):

        urdb_rate = {}

        # energy rate
        energyratestructure = []
        schedule = []
        for month in range(0, 12):
            rate = {'rate': blended_utility_rate[month], 'unit': 'kWh'}
            tier = [rate]
            energyratestructure.append(tier)

            tmp = [month] * 24
            schedule.append(tmp)

        # demand rate
        flatdemandmonths = []
        flatdemandstructure = []

        for month in range(0, 12):
            flatdemandmonths.append(month)
            rate = {'rate': demand_charge[month]}
            tier = [rate]
            flatdemandstructure.append(tier)

        # ouput
        urdb_rate['energyweekdayschedule'] = schedule
        urdb_rate['energyweekendschedule'] = schedule
        urdb_rate['energyratestructure'] = energyratestructure
        urdb_rate['flatdemandstructure'] = flatdemandstructure
        urdb_rate['flatdemandmonths'] = flatdemandmonths
        urdb_rate['flatdemandunit'] = 'kW'
        urdb_rate['label'] = self.run_id
        urdb_rate['name'] = "Custom_rate_" + str(self.run_id)
        urdb_rate['utility'] = "Custom_utility_" + str(self.run_id)

        return urdb_rate