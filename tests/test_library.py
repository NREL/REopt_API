import unittest

from reo.library import DatLibrary
from reo.pro_forma import ProForma
from enum import Enum

import json
import os
import shutil
import filecmp


class ValidationCases(Enum):

    BASE_CASE = 0
    NEM_CASE = 1


class RunLibraryTests(unittest.TestCase):

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

    # data
    file_scenario = "post_json.txt"

    def setUpScenario(self, scenario_num):

        self.path_valid_run = os.path.join("tests", "validation_scenario_" + str(scenario_num))
        self.path_valid_input = os.path.join(self.path_valid_run, "Inputs")
        self.path_valid_output = os.path.join(self.path_valid_run, "Outputs")
        self.path_valid_output_bau = os.path.join(self.path_valid_run, "Outputs_bau")

        with open(os.path.join(self.path_valid_run, self.file_scenario)) as json_file:
            return json.load(json_file)

    def tearDownScenario(self):

        if os.path.exists(self.path_input):
            shutil.rmtree(self.path_input)
        if os.path.exists(self.path_output):
            shutil.rmtree(self.path_output)
        if os.path.exists(self.path_output_bau):
            shutil.rmtree(self.path_output_bau)

    def get_output_paths(self, run_set):

        self.path_run = run_set.get_path_run()
        self.path_input = run_set.get_path_run_inputs()
        self.path_output = run_set.get_path_run_outputs()
        self.path_output_bau = run_set.get_path_run_outputs_bau()

    def compare_directory_contents(self):

        self.assertTrue(filecmp.dircmp(self.path_input, self.path_valid_input),
                        "Generated results for input not valid!")
        self.assertTrue(filecmp.dircmp(self.path_output, self.path_valid_output),
                        "Generated results for output not valid!")
        self.assertTrue(filecmp.dircmp(self.path_output_bau, self.path_valid_output_bau),
                        "Generated results for output not valid!")

    def run_scenario(self, scenario_num):

        json_data = self.setUpScenario(scenario_num)
        run_set = DatLibrary(scenario_num, json_data)
        run_set.run()
        self.get_output_paths(run_set)
        self.compare_directory_contents()
        self.tearDownScenario()

    def test_base_case(self):

        scenario_num = ValidationCases.BASE_CASE
        self.run_scenario(scenario_num)

    def test_nem_case(self):

        scenario_num = ValidationCases.NEM_CASE
        self.run_scenario(scenario_num)

