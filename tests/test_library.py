import unittest

from reo.library import DatLibrary
from reo.pro_forma import ProForma

import json
import os
import shutil


class RunLibraryTest(unittest.TestCase):

    scenario_num = 0
    path_scenario = []

    # generated results
    path_input = None
    path_output = None
    path_output_bau = None

    # validated results
    path_valid_input = None
    path_valid_output = None
    path_valid_output_bau = None

    # filenames
    filename_economics = None
    filename_economics_bau = None
    filename_GIS = None
    filename_GIS_bau = None

    # data
    file_scenario = "post_json.txt"
    json_data = {}
    run_set = []

    def setUp(self):

        self.path_scenario = os.path.join("tests", "validation_scenario_" + str(self.scenario_num))
        self.path_valid_input = os.path.join(self.path_scenario, "Inputs")
        self.path_valid_output = os.path.join(self.path_scenario, "Outputs")
        self.path_valid_output_bau = os.path.join(self.path_scenario, "Outputs_bau")

        self.filename_economics = "economics_" + str(self.scenario_num) + ".dat"
        self.filename_economics_bau = "economics_" + str(self.scenario_num) + "_bau.dat"

        self.filename_GIS = "GIS_" + str(self.scenario_num) + ".dat"
        self.filename_GIS_bau = "GIS_" + str(self.scenario_num) + "_bau.dat"

        with open(os.path.join(self.path_scenario, self.file_scenario)) as json_file:
            self.json_data = json.load(json_file)

    def tearDown(self):

        if os.path.exists(self.path_input):
            shutil.rmtree(self.path_input)
        if os.path.exists(self.path_output):
            shutil.rmtree(self.path_output)
        if os.path.exists(self.path_output_bau):
            shutil.rmtree(self.path_output_bau)

    def test_run(self):

        self.run_set = DatLibrary(0, self.json_data)
        self.run_set.run()

        # get output paths
        self.path_input = self.run_set.get_path_run_inputs()
        self.path_output = self.run_set.get_path_run_outputs()
        self.path_output_bau = self.run_set.get_path_run_outputs_bau()

        list_files_valid = []
        list_files = []
        for dirName, subdirList, fileList in os.walk(self.path_valid_input):
            for fname in fileList:
                list_files_valid.append(os.path.join(dirName, fname))
        for dirName, subdirList, fileList in os.walk(self.path_input):
            for fname in fileList:
                list_files.append(os.path.join(dirName, fname))

        for name_valid in list_files_valid:
            for name in list_files:
                if name == name_valid:
                    with open(os.path.join(self.path_input, name), 'r') as f:
                        data = f.readlines()
                    with open(os.path.join(self.path_valid_input, name_valid), 'r') as f:
                        data_valid = f.readlines()
                    self.assertListEqual(data, data_valid, "Generated inputs for " + name + " not valid!")




