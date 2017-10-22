import unittest

from reo.scenario import Scenario
from enum import Enum

import json
import os
import shutil
import filecmp
import pandas as pd
import uuid

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
        self.run_uuid = uuid.uuid4()
        self.path_valid_run = os.path.join("tests", "validation_scenario_" + str(scenario_num))
        self.path_valid_input = os.path.join(self.path_valid_run, "Inputs")
        self.path_valid_output = os.path.join(self.path_valid_run, "Outputs")
        self.path_valid_output_bau = os.path.join(self.path_valid_run, "Outputs_bau")
        self.path_static = os.path.join('static', 'files', self.run_uuid)

        with open(os.path.join(self.path_valid_run, self.file_scenario)) as json_file:
            return json.load(json_file)

    def tearDownScenario(self):

        if os.path.exists(self.path_input):
            shutil.rmtree(self.path_input)
        if os.path.exists(self.path_output):
            shutil.rmtree(self.path_output)
        if os.path.exists(self.path_output_bau):
            shutil.rmtree(self.path_output_bau)
        if os.path.exists(self.path_static):
            shutil.rmtree(self.path_static)

    def compare_directory_contents(self, path_valid_results, path_to_test):

        list_files_valid = {}
        list_files = {}

        #print "Valid files"
        for dirName, subdirList, fileList in os.walk(path_valid_results):
            for fname in fileList:
                list_files_valid[fname] = os.path.join(dirName, fname)
                #print list_files_valid[fname]

        #print "Test files"
        for dirName, subdirList, fileList in os.walk(path_to_test):
            for fname in fileList:
                list_files[fname] = os.path.join(dirName, fname)
                #print list_files[fname]

        for file_valid, path_valid in list_files_valid.iteritems():

            #print "Checking: " + file_valid
            results_contain_file = False

            if file_valid in list_files:
                results_contain_file = True
                path_generated = list_files[file_valid]

                filename, extension = os.path.splitext(path_generated)
                if extension != ".xlsx":
                    self.assertTrue(filecmp.cmp(path_generated, path_valid, shallow=False), "Files do not match!")
                else:
                    df1 = pd.read_excel(path_generated)
                    df2 = pd.read_excel(path_valid)
                    self.assertTrue(df1.equals(df2), 'Excel file does not match')

            self.assertTrue(results_contain_file, "File doesn't exist in path_to_test")

    def run_scenario(self, scenario_num):

        json_data = self.setUpScenario(scenario_num)
        run_set = Scenario(self.run_uuid, scenario_num, json_data)
        run_set.run()
        print "Test Inputs"
        self.compare_directory_contents(self.path_valid_input, run_set.paths.inputs)
        print "Test BAU Output"
        self.compare_directory_contents(self.path_valid_output_bau, run_set.paths.outputs_bau)
        print "Test Output"
        self.compare_directory_contents(self.path_valid_output, run_set.paths.outputs)
        self.tearDownScenario()

    @unittest.skip("test_library.test_base_case broken")
    def test_base_case(self):

        scenario_num = ValidationCases.BASE_CASE.value
        self.run_scenario(scenario_num)

    @unittest.skip("test_library.test_nem_case broken")
    def test_nem_case(self):

        scenario_num = ValidationCases.NEM_CASE.value
        self.run_scenario(scenario_num)

