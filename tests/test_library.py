import unittest

from reo.library import DatLibrary
from reo.pro_forma import ProForma

import json
import os
import shutil
import filecmp

class RunLibraryTest(unittest.TestCase):

    scenario_num = 0
    remove_files = False

    # generated results
    path_run = None
    path_input = None
    path_output = None
    path_output_bau = None

    # validated results
    path_valid_run = []
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

        self.path_valid_run = os.path.join("tests", "validation_scenario_" + str(self.scenario_num))
        self.path_valid_input = os.path.join(self.path_valid_run, "Inputs")
        self.path_valid_output = os.path.join(self.path_valid_run, "Outputs")
        self.path_valid_output_bau = os.path.join(self.path_valid_run, "Outputs_bau")

        self.filename_economics = "economics_" + str(self.scenario_num) + ".dat"
        self.filename_economics_bau = "economics_" + str(self.scenario_num) + "_bau.dat"

        self.filename_GIS = "GIS_" + str(self.scenario_num) + ".dat"
        self.filename_GIS_bau = "GIS_" + str(self.scenario_num) + "_bau.dat"

        with open(os.path.join(self.path_valid_run, self.file_scenario)) as json_file:
            self.json_data = json.load(json_file)

    def tearDown(self):

        if self.remove_files:
            if os.path.exists(self.path_input):
                shutil.rmtree(self.path_input)
            if os.path.exists(self.path_output):
                shutil.rmtree(self.path_output)
            if os.path.exists(self.path_output_bau):
                shutil.rmtree(self.path_output_bau)

    def test_run(self):

        self.run_set = DatLibrary(0, self.json_data)
        self.run_set.run()

        self.path_run = self.run_set.get_path_run()
        self.path_input = self.run_set.get_path_run_inputs()
        self.path_output = self.run_set.get_path_run_outputs()
        self.path_output_bau = self.run_set.get_path_run_outputs_bau()

        self.assertTrue(filecmp.dircmp(self.path_input, self.path_valid_input), "Generated results for input not valid!")
        self.assertTrue(filecmp.dircmp(self.path_output, self.path_valid_output), "Generated results for output not valid!")
        self.assertTrue(filecmp.dircmp(self.path_output_bau, self.path_valid_output_bau), "Generated results for output not valid!")

        self.remove_files = True



