import os
import subprocess
import traceback
import economics
import shutil
from log_levels import log
import logging

import pandas as pd

class DatLibrary:

    # if need to debug, change to True, outputs OUT files, GO files, debugging to cmdline
    debug = True
    logfile = "reopt_api.log"
    xpress_model = "REoptTS1127_PVBATT72916.mos"

    run_id = []
    run_file = []
    output_file = []
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
                             'SecondarySchool', 'SmallHotel', 'SmallOffice', 'StripMall', 'Supermarket', 'Warehouse',
                             'Demo']

    # directory structure
    path_egg = []
    path_xpress = []
    path_logfile = []
    path_dat_library = []
    path_various = []
    path_load_size = []
    path_load_profile = []
    path_gis_data = []
    path_utility = []
    path_output = []

    path_dat_library_relative = []
    file_economics = []

    # DAT files to overwrite
    DAT = [None] * 20

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
        self.load_profile = load_profile
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

    def run(self):
        self.update_types()
        self.define_paths()
        self.setup_logging()
        self.create_or_load()
        self.create_run_file()

        #print ('New subprocess')
        #tracefile = open('traceback.txt', 'a')
        #traceback.print_stack(limit=5, file=tracefile)
        subprocess.call(self.run_file)
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

        # absolute
        self.path_xpress = os.path.join(self.path_egg, "Xpress")
        self.path_logfile = os.path.join(self.path_egg, 'reopt_api', self.logfile)
        self.path_dat_library = os.path.join(self.path_xpress, "DatLibrary")

        # relative
        self.path_dat_library_relative = os.path.join("Xpress", "DatLibrary")

        self.path_various = os.path.join("Various")
        self.path_load_size = os.path.join("LoadSize")
        self.path_load_profile = os.path.join("LoadProfiles")
        self.path_gis_data = os.path.join("GISdata")
        self.path_utility = os.path.join("Utility")
        self.path_output = os.path.join("Xpress", "Output", "Run_" + str(self.run_id))

        self.file_economics = os.path.join("Economics", 'economics_' + str(self.run_id) + '.dat')

    def create_or_load(self):

        self.create_economics()

        '''
        if self.load_size and self.load_size > 0:
            self.create_load_size()
        if self.pv_om and self.pv_om >= 0:
            self.create_pv_om()
        if self.batt_cost_kw and self.batt_cost_kw >= 0:
            self.create_batt_kw()
        if self.batt_cost_kwh and self.batt_cost_kwh >= 0:
            self.create_batt_kwh()
        if self.load_profile:
            self.create_load_profile()
        if self.pv_cost and self.pv_cost >= 0:
            self.create_pv_cost()
        if self.owner_discount_rate and self.owner_discount_rate >=0:
            self.create_owner_discount_rate()
        if self.offtaker_discount_rate and self.offtaker_discount_rate >=0:
            self.create_offtaker_discount_rate()
        '''

    def create_run_file(self):

        go_file = "Go_" + str(self.run_id) + ".bat"
        output_dir = self.path_output

        log("DEBUG", "Current Directory: " + os.getcwd())
        log("DEBUG", "Creating output directory: " + output_dir)
        log("DEBUG", "Created run file: " + go_file)

        os.mkdir(output_dir)

        header = 'mosel -c "exec ' + os.path.join(self.path_xpress, self.xpress_model)

        output = "OUTDIR=" + "'" + output_dir + "'"
        outline = ''

        for dat_file in self.DAT:
            if dat_file is not None:
                outline = ', '.join([outline, dat_file])
        outline = ', '.join([outline, output])
        outline.replace('\n', '')
        outline = '  '.join([header, outline]) + '\n'

        self.run_file = os.path.join(self.path_xpress, go_file)
        self.output_file = os.path.join(output_dir, "summary.csv")

        f = open(self.run_file, 'w')
        f.write(outline)
        f.close()

    def parse_outputs(self):

        if os.path.exists(self.output_file):
            df = pd.read_csv(self.output_file, header=None, index_col=0)
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
            log("WARNING", "Output file: " + self.output_file + " + doesn't exist!")

    def cleanup(self):

        if not self.debug:
            if os.path.exists(self.path_output):
                shutil.rmtree(self.path_output, ignore_errors=True)
            if os.path.exists(self.run_file):
                os.remove(self.run_file)
            if os.path.exists(os.path.join(self.path_dat_library_relative, self.file_economics)):
                os.remove(os.path.join(self.path_dat_library_relative, self.file_economics))

    def write_var(self, f, var, dat_var):
        f.write(dat_var + ": [\n")
        if isinstance(var, list):
            for i in var:
                f.write(str(i) + "\t,\n")
        else:
            f.write(str(var) + "\t,\n")
        f.write("]\n")

    def write_single_variable(self, path, filename, var, dat_var):
        filename_path = os.path.join(path, filename)
        if filename not in os.listdir(path):
            f = open(filename_path, 'w')
            self.write_var(f, var, dat_var)
            f.close()

    def write_two_variables(self, path, filename, var, dat_var, var2, dat_var2, overwrite=False):
        filename_path = os.path.join(path, filename)
        if filename not in os.listdir(path) or overwrite:
            f = open(filename_path, 'w')
            self.write_var(f, var, dat_var)
            self.write_var(f, var2, dat_var2)
            f.close()

    # DAT1 - Constant
    # DAT2 - Economics
    def create_economics(self):

        file_path = os.path.join(self.path_dat_library, self.file_economics)
        print self.batt_cost_kw
        economics.Economics(file_path, self.flag_macrs, self.flag_itc, self.flag_bonus, self.flag_replace_batt,
                            self.analysis_period, self.rate_inflation, self.rate_offtaker_discount,
                            self.rate_owner_discount, self.rate_escalation, self.rate_tax, self.rate_itc,
                            self.macrs_years, self.macrs_itc_reduction, self.bonus_fraction, self.pv_cost,
                            self.pv_om, self.rate_degradation, self.batt_cost_kw, self.batt_cost_kwh,
                            self.batt_replacement_year, self.batt_replacement_cost_kw, self.batt_replacement_cost_kwh)

        self.DAT[1] = "DAT2=" + "'" + self.file_economics + "'"

    # DAT3 - LoadSize
    def create_load_size(self):
        path = self.path_load_size
        var = self.load_size
        filename = "LoadSize_" + var + ".dat"
        dat_var = "AnnualElecLoad"
        self.DAT[2] = "DAT3=" + "'" + os.path.join(path, filename) + "'"

        self.write_single_variable(path, filename, var, dat_var)

    # DAT4 - Load
    def create_load_profile(self):
        path = self.path_load_profile
        var = self.load_profile
        if var.lower() in self.default_load_profiles:
            filename = "Load8760_" + var + ".dat"
            self.DAT[3] = "DAT4=" + "'" + os.path.join(path, filename) + "'"

    # DAT5 - Solar Resource
    # DAT6 - Storage
    # DAT7 - Max Sizes

    # DAT8 - DAT11 - Utility Rates
    # Currently depends on files being present in directory structure
    def create_utility_rate(self):
        rate_path = os.path.join(self.path_utility_rate, self.utility_name, self.rate_name)
        self.DAT[7] = "DAT8=" + "'" + os.path.join(rate_path, "TimeStepsDemand.dat")
        self.DAT[8] = "DAT9=" + "'" + os.path.join(rate_path, "DemandRate.dat")
        self.DAT[9] = "DAT10=" + "'" + os.path.join(rate_path, "FuelCost.dat")
        self.DAT[10] = "DAT11=" + "'" + os.path.join(rate_path, "Export.dat")


    '''
    # DAT2 - PVOM
    def create_pv_om(self):
        path = self.path_pv_om
        var = self.pv_om
        filename = "PVOM" + var + ".dat"
        dat_var = "OMperUnitSize"
        self.DAT[1] = "DAT2=" + "'" + os.path.join(path, filename) + "'"

        self.write_single_variable(path, filename, [var, 0], dat_var)

    # DAT3 - BCostKW
    def create_batt_kw(self):
        path = self.path_batt_cost_kw
        var = self.batt_cost_kw
        filename = "BCostKW" + var + ".dat"
        dat_var = "StorageCostPerKW"
        self.DAT[2] = "DAT3=" + "'" + os.path.join(path, filename) + "'"

        self.write_single_variable(path, filename, var, dat_var)

    # DAT4 - BCostKWH
    def create_batt_kwh(self):
        path = self.path_batt_cost_kwh
        var = self.batt_cost_kwh
        filename = "BCostKWH" + var + ".dat"
        dat_var = "StorageCostPerKWH"
        self.DAT[3] = "DAT4=" + "'" + os.path.join(path, filename) + "'"

        self.write_single_variable(path, filename, var, dat_var)


    # DAT6 - PVCost
    def create_pv_cost(self):
        path = self.path_pv_cost
        var = self.pv_cost
        filename = "PVCost" + var + ".dat"
        dat_var = "CapCostSlope"
        self.DAT[5] = "DAT6=" + "'" + os.path.join(path, filename) + "'"

        self.write_single_variable(path, filename, [var, 0], dat_var)


    # DAT19 - Owner Discount Rate
    def create_owner_discount_rate(self):
        path = self.path_owner_discount_rate
        var1 = self.owner_discount_rate
        var2 = utilities.present_worth_factor(int(self.analysis_period), 0., float(var1))
        #var2.replace('\n', '')
        filename = "Owner" + var1 + ".dat"
        dat_var1 = "r_owner"
        dat_var2 = "pwf_owner"
        self.DAT[18] = "DAT19=" + "'" + os.path.join(path, filename) + "'"
        # overwrite anytime we compute present worth factor
        overwrite = True

        self.write_two_variables(path, filename, var1, dat_var1, var2, dat_var2, overwrite)

    # DAT20 - Offtaker Discount Rate
    def create_offtaker_discount_rate(self):
        path = self.path_offtaker_discount_rate
        var1 = self.offtaker_discount_rate
        var2 = utilities.present_worth_factor(int(self.analysis_period), 0., float(var1))
        #var2.replace('\n', '')
        filename = "Offtaker" + var1 + ".dat"
        dat_var1 = "r_offtaker"
        dat_var2 = "pwf_offtaker"
        self.DAT[19] = "DAT20=" + "'" + os.path.join(path, filename) + "'"

        overwrite = True

        self.write_two_variables(path, filename, var1, dat_var1, var2, dat_var2, overwrite)


    # SResource, hookup PVWatts

    # Constants don't envision messing with
    # DAT8 - ActiveTechs
    # DAT9 - FuelIsActive
    # DAT10 - MaxSystemSize
    # DAT11 - TechIS
    # DAT16 - Storage


    # Utility rates, hookup urdb processor

    # Calculate PWFs from discount rate, or use defaults
    '''


