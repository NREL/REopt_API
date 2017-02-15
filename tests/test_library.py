import unittest

from reo.library import DatLibrary
from reo.pro_forma import ProForma
from enum import Enum

import json
import os
import shutil
import filecmp
import pandas as pd


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
        run_set = DatLibrary(scenario_num, json_data)
        run_set.run()
        self.get_output_paths(run_set)
        print "Test Inputs"
        self.compare_directory_contents(self.path_valid_input, self.path_input)
        print "Test BAU Output"
        self.compare_directory_contents(self.path_valid_output_bau, self.path_output_bau)
        print "Test Output"
        self.compare_directory_contents(self.path_valid_output, self.path_output)
        #self.tearDownScenario()

    def test_base_case(self):

        scenario_num = ValidationCases.BASE_CASE
        self.run_scenario(scenario_num)

    def test_nem_case(self):

        scenario_num = ValidationCases.NEM_CASE
        self.run_scenario(scenario_num)

