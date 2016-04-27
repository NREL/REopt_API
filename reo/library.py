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

    # directory structure
    path_dat_library = []
    path_xpress = []
    path_load_size = []
    path_solar_resource = []


    # DAT files to overwrite
    DAT = [None] * 20

    def __init__(self, run_id, path_xpress, latitude, longitude, load_size, pv_om, batt_cost_kw, batt_cost_kwh):
        self.path_xpress = path_xpress

        self.run_id = run_id
        self.latitude = latitude
        self.longitude = longitude
        self.load_size = load_size
        self.pv_om = pv_om
        self.batt_cost_kw = batt_cost_kw
        self.batt_cost_kwh = batt_cost_kwh

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
        self.path_solar_resource = os.path.join(self.path_dat_library, "SolarResource")
        self.path_output = os.path.join(self.path_dat_library, "Output")

    def create_or_load(self):
        if self.load_size and self.load_size > 0:
            self.create_load_size()
        if self.pv_om and self.pv_om > 0:
            self.create_pv_om()
        if self.batt_cost_kw and self.batt_cost_kw > 0:
            self.create_batt_kw()
        if self.batt_cost_kwh and self.batt_cost_kwh > 0:
            self.create_batt_kwh()

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

    def write_single_variable(self, path, filename, dat_var, var):
        filename_path = os.path.join(path, filename)
        if filename not in os.listdir(path):
            f = open(filename_path, 'w')
            f.write(dat_var + ": [\n")
            for i in var:
                f.write(str(i) + "\t,\n")
            f.write("]")
            f.close()

    # DAT1
    def create_load_size(self):
        path = self.path_load_size
        var = self.load_size
        filename = "LoadSize_" + var + ".dat"
        dat_var = "AnnualElecLoad"
        self.DAT[0] = "DAT1=" + "'" + os.path.join(path, filename) + "'"

        self.write_single_variable(path, filename, dat_var, var)


    # DAT2
    def create_pv_om(self):
        path = self.path_pv_om
        var = self.pv_om
        filename = "PVOM" + var + ".dat"
        dat_var = "OMperUnitSize"
        self.DAT[1] = "DAT2=" + "'" + os.path.join(path, filename) + "'"

        self.write_single_variable(path, filename, [var, 0], dat_var)

    # DAT3
    def create_batt_kw(self):
        path = self.path_batt_cost_kw
        var = self.batt_cost_kw
        filename = "BCostKW" + var + ".dat"
        dat_var = "StorageCostPerKW"
        self.DAT[2] = "DAT3=" + "'" + os.path.join(path, filename) + "'"

        self.write_single_variable(path, filename, var, dat_var)

    # DAT4
    def create_batt_kwh(self):
        path = self.path_batt_cost_kwh
        var = self.batt_cost_kwh
        filename = "BCostKWH" + var + ".dat"
        dat_var = "StorageCostPerKWH"
        self.DAT[3] = "DAT4=" + "'" + os.path.join(path, filename) + "'"

        self.write_single_variable(path, filename, var, dat_var)



