import os
import subprocess
import utilities
import pandas as pd

# currently setup not using a database, that might improve performance
class dat_library:

    # if need to debug, change to True, outputs OUT files, GO files, debugging to cmdline
    debug = False

    run_id = []
    run_file = []
    output_file = []
    outputs = {}

    # variables that user can pass
    analysis_period = 25
    latitude = []
    longitude = []
    load_size = []
    pv_om = []
    batt_cost_kw = []
    batt_cost_kwh = []
    load_profile = []
    pv_cost = []
    owner_discount_rate = []
    offtaker_discount_rate = []
    utility_name = []
    rate_name = []


    # default load profiles
    default_load_profiles = ['FastFoodRest', 'Flat', 'FullServiceRest', 'Hospital', 'LargeHotel', 'LargeOffice',
                             'MediumOffice', 'MidriseApartment', 'Outpatient', 'PrimarySchool', 'RetailStore',
                             'SecondarySchool', 'SmallHotel', 'SmallOffice', 'StripMall', 'Supermarket', 'Warehouse',
                             'Demo']

    # directory structure
    path_xpress = []
    path_dat_library = []
    path_load_size = []
    path_pv_om = []
    path_batt_cost_kwh = []
    path_batt_cost_kw = []
    path_load_profile = []
    path_pv_cost = []
    path_owner_discount_rate = []
    path_offtaker_discount_rate = []
    path_solar_resource = []
    path_utility_rate = []
    path_output = []

    # DAT files to overwrite
    DAT = [None] * 20

    def __init__(self, run_id, path_xpress, analysis_period, latitude, longitude, load_size, pv_om, batt_cost_kw,
                 batt_cost_kwh, load_profile, pv_cost, owner_discount_rate, offtaker_discount_rate,
                 utility_name, rate_name):
        self.path_xpress = path_xpress

        self.run_id = run_id

        if analysis_period and analysis_period > 0:
            self.analysis_period = analysis_period

        self.latitude = latitude
        self.longitude = longitude
        self.load_size = load_size
        self.pv_om = pv_om
        self.batt_cost_kw = batt_cost_kw
        self.batt_cost_kwh = batt_cost_kwh
        self.load_profile = load_profile
        self.pv_cost = pv_cost
        self.owner_discount_rate = owner_discount_rate
        self.offtaker_discount_rate = offtaker_discount_rate
        self.utility_name = utility_name
        self.rate_name = rate_name

        lower_case_profile = []
        for profile in self.default_load_profiles:
            lower_case_profile.append(profile.lower())
        self.default_load_profiles = lower_case_profile

    def run(self):
        self.define_paths()
        self.create_or_load()
        self.create_run_file()

        subprocess.call(self.run_file)
        self.parse_outputs()
        #self.cleanup()

        return self.outputs

    def define_paths(self):

        self.path_dat_library = os.path.join(self.path_xpress, "DatLibrary")
        self.path_load_size = os.path.join(self.path_dat_library, "LoadSize")
        self.path_pv_om = os.path.join(self.path_dat_library, "OM")
        self.path_batt_cost_kwh = os.path.join(self.path_dat_library, "BatteryCost", "KWH")
        self.path_batt_cost_kw = os.path.join(self.path_dat_library, "BatteryCost", "KW")
        self.path_load_profile = os.path.join(self.path_dat_library, "LoadProfiles")
        self.path_pv_cost = os.path.join(self.path_dat_library, "PVcost")
        self.path_owner_discount_rate = os.path.join(self.path_dat_library, "DiscountRates", "Owner")
        self.path_offtaker_discount_rate = os.path.join(self.path_dat_library, "DiscountRates", "Offtaker")
        self.path_solar_resource = os.path.join(self.path_dat_library, "SolarResource")
        self.path_utility_rate = os.path.join(self.path_dat_library, "Utility")

        self.path_output = os.path.join(self.path_dat_library, "Output")

    def create_or_load(self):
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

    def create_run_file(self):
        go_file = "Go_" + str(self.run_id) + ".bat"
        output_file = "Out_" + str(self.run_id) + ".csv"
        header = 'mosel -c "exec ' + os.path.join(self.path_xpress, 'REoptTS1127')

        self.output_file = os.path.join(self.path_output, output_file)
        self.output_file.replace('\n', '')

        output = "OUTFILE=" + "'" + self.output_file + "'"
        outline = ''

        for dat_file in self.DAT:
            if dat_file is not None:
                outline = ', '.join([outline, dat_file])
        outline = ', '.join([outline, output])
        outline.replace('\n', '')
        outline = '  '.join([header, outline]) + '\n'

        self.run_file = os.path.join(self.path_xpress, go_file)
        f = open(self.run_file, 'w')
        f.write(outline)
        f.close()

    def parse_outputs(self):

        df = pd.read_csv(self.output_file, header=None, index_col=0)
        df = df.transpose()

        if 'LCC' in df.columns:
            self.outputs['lcc'] = df['LCC']
        if 'Batt size KW' in df.columns:
            self.outputs['batt_size_kw'] = df['Batt size KW']
        if 'Batt size KWH' in df.columns:
            self.outputs['batt_size_kwh'] = df['Batt size KWH']
        if 'PVNM size KW' in df.columns:
            self.outputs['pv_kw'] = df['PVNM size KW']

    def cleanup(self):
        if not self.debug:
            os.remove(self.output_file)
            os.remove(self.run_file)

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

    # DAT1 - LoadSize
    def create_load_size(self):
        path = self.path_load_size
        var = self.load_size
        filename = "LoadSize_" + var + ".dat"
        dat_var = "AnnualElecLoad"
        self.DAT[0] = "DAT1=" + "'" + os.path.join(path, filename) + "'"

        self.write_single_variable(path, filename, var, dat_var)


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

    # DAT5 - Load
    def create_load_profile(self):
        path = self.path_load_profile
        var = self.load_profile
        if var.lower() in self.default_load_profiles:
            filename = "Load8760_" + var + ".dat"
            self.DAT[4] = "DAT5=" + "'" + os.path.join(path, filename) + "'"

    # DAT6 - PVCost
    def create_pv_cost(self):
        path = self.path_pv_cost
        var = self.pv_cost
        filename = "PVCost" + var + ".dat"
        dat_var = "CapCostSlope"
        self.DAT[5] = "DAT6=" + "'" + os.path.join(path, filename) + "'"

        self.write_single_variable(path, filename, [var, 0], dat_var)

    # DAT12 - DAT15 - Utility Rates
    # Currently depends on files being present in directory structure
    def create_utility_rate(self):
        rate_path = os.path.join(self.path_utility_rate, self.utility_name, self.rate_name)
        self.DAT[11] = "DAT12=" + "'" + os.path.join(rate_path, "DPeriods.dat")
        self.DAT[12] = "DAT13=" + "'" + os.path.join(rate_path, "DRate.dat")
        self.DAT[13] = "DAT14=" + "'" + os.path.join(rate_path, "ERate.dat")
        self.DAT[14] = "DAT15=" + "'" + os.path.join(rate_path, "Export.dat")

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


