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

    # directory structure
    path_dat_library = []
    path_xpress = []
    path_load_size = []
    path_solar_resource = []


    # DAT files to overwrite
    DAT = [None] * 20

    def __init__(self, run_id, path_xpress, latitude, longitude, load_size):
        self.path_xpress = path_xpress

        self.run_id = run_id
        self.latitude = latitude
        self.longitude = longitude
        if isinstance(load_size, float):
            self.load_size = round(load_size, 0)
        else:
            self.load_size = load_size

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
        self.path_solar_resource = os.path.join(self.path_dat_library, "SolarResource")
        self.path_output = os.path.join(self.path_dat_library, "Output")

    def create_or_load(self):
        if self.load_size and self.load_size > 0:
            self.create_load_size()

    def create_run_file(self):
        go_file = "Go_" + str(self.run_id) + ".bat"
        output_file = "Out_" + str(self.run_id) + ".bat"
        header = 'mosel -c "exec ' + os.path.join(self.path_xpress, 'REoptTS1127')

        self.output_file = os.path.join(self.path_output, output_file + '.txt')
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

    # DAT1
    def create_load_size(self):
        filename = "LoadSize_" + self.load_size + ".dat"
        if filename not in os.listdir(self.path_load_size):
            f = open(os.path.join(self.path_load_size, filename), 'w')
            f.write("AnnualElecLoad: [\n")
            f.write(str(self.load_size) + "\t,\n")
            f.write("]")
            f.close()
        self.DAT[0] = "DAT1=" + "'" + os.path.join(self.path_load_size, filename) + "'"






