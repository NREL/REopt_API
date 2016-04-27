import os
import subprocess

# currently setup not using a database, that might improve performance
class dat_library:

    run_id = []
    run_file = []
    output_file = []
    outputs = {}

    # variables that user can pass
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

    # default load profiles
    default_load_profiles = ['FastFoodRest', 'Flat', 'FullServiceRest', 'Hospital', 'LargeHotel', 'LargeOffice', 'MediumOffice', 'MidriseApartment', 'Outpatient',
                             'PrimarySchool', 'RetailStore', 'SecondarySchool', 'SmallHotel', 'SmallOffice', 'StripMall','Supermarket','Warehouse']

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
    path_output = []

    # DAT files to overwrite
    DAT = [None] * 20

    def __init__(self, run_id, path_xpress, latitude, longitude, load_size, pv_om, batt_cost_kw, batt_cost_kwh, load_profile, pv_cost, owner_discount_rate, offtaker_discount_rate):
        self.path_xpress = path_xpress

        self.run_id = run_id
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

    def run(self):
        self.define_paths()
        self.create_or_load()
        self.create_run_file()

        subprocess.call(self.run_file)
        self.parse_outputs()
        self.cleanup()

        return self.outputs

    def define_paths(self):
        self.path_dat_library = os.path.join(self.path_xpress,"DatLibrary")
        self.path_load_size = os.path.join(self.path_dat_library, "LoadSize")
        self.path_pv_om = os.path.join(self.path_dat_library, "OM")
        self.path_batt_cost_kwh = os.path.join(self.path_dat_library, "BatteryCost", "KWH")
        self.path_batt_cost_kw = os.path.join(self.path_dat_library, "BatteryCost", "KW")
        self.path_load_profile = os.path.join(self.path_dat_library, "LoadProfiles")
        self.path_pv_cost = os.path.join(self.path_dat_library, "PVcost")
        self.path_owner_discount_rate = os.path.join(self.path_dat_library, "DiscountRates", "Owner")
        self.path_offtaker_discount_rate = os.path.join(self.path_dat_library, "DiscountRates", "Offtaker")

        self.path_solar_resource = os.path.join(self.path_dat_library, "SolarResource")


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
        output_file = "Out_" + str(self.run_id) + ".txt"
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
        output = open(self.output_file, 'r')

        for line in output:
            if "LCC" in line:
                eq_ind = line.index("=")
                self.outputs['lcc'] = line[eq_ind + 2:len(line)]

    def cleanup(self):
        os.remove(self.output_file)
        os.remove(self.run_file)

    def write_var(self, f, dat_var, var):
        f.write(dat_var + ": [\n")
        for i in var:
            f.write(str(i) + "\t,\n")
        f.write("]\n")

    def write_single_variable(self, path, filename, dat_var, var):
        filename_path = os.path.join(path, filename)
        if filename not in os.listdir(path):
            f = open(filename_path, 'w')
            self.write_var(f, dat_var, var)
            f.close()

    def write_two_variables(self, path, filename, dat_var, var, dat_var2, var2):
        filename_path = os.path.join(path, filename)
        if filename not in os.listdir(path):
            f = open(filename_path, 'w')
            self.write_var(f, dat_var, var)
            self.write_var(f, dat_var2, var2)
            f.close()

    # DAT1 - LoadSize
    def create_load_size(self):
        path = self.path_load_size
        var = self.load_size
        filename = "LoadSize_" + var + ".dat"
        dat_var = "AnnualElecLoad"
        self.DAT[0] = "DAT1=" + "'" + os.path.join(path, filename) + "'"

        self.write_single_variable(path, filename, dat_var, var)


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
        if var in self.default_load_profiles:
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

    # DAT19 - Owner Discount Rate
    def create_owner_discount_rate(self):
        path = self.path_owner_discount_rate
        var1 = self.owner_discount_rate
        var2 = 25 #NEED TO DEFINE PWF OWNER
        filename = "Owner" + var1 + ".dat"
        dat_var1 = "r_owner"
        dat_var2 = "pwf_owner"
        self.DAT[18] = "DAT19=" + "'" + os.path.join(path, filename) + "'"

        self.write_two_variables(path, filename, var1, dat_var1, var2, dat_var2)

    # DAT20 - Offtaker Discount Rate
    def create_offtaker_discount_rate(self):
        path = self.path_offtaker_discount_rate
        var1 = self.offtaker_discount_rate
        var2 = 25  # NEED TO DEFINE PWF OFFTAKER
        filename = "Offtaker" + var1 + ".dat"
        dat_var1 = "r_offtaker"
        dat_var2 = "pwf_offtaker"
        self.DAT[19] = "DAT20=" + "'" + os.path.join(path, filename) + "'"

        self.write_two_variables(path, filename, var1, dat_var1, var2, dat_var2)


    # SResource, hookup PVWatts

    # Constants don't envision messing with
    # DAT8 - ActiveTechs
    # DAT9 - FuelIsActive
    # DAT10 - MaxSystemSize
    # DAT11 - TechIS
    # DAT16 - Storage
    # Utility rates, hookup urdb processor

    # Calculate PWFs from discount rate, or use defaults


