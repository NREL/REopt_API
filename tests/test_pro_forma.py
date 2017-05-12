import unittest
import os
import json

from reo.pro_forma_writer import ProForma


class MockEconomics:

    # class to mimic an economic object with data that matches the ProForma template
    def __init__(self, path_template):

        econ_file = open(os.path.join(path_template, "econ.json"))
        econ_data = econ_file.read()
        econ_dict = json.loads(econ_data)

        for key in econ_dict:
            setattr(self, key, econ_dict[key])


class MockResults:

    # class to mimic a results object with data that matches the ProForma template
    def __init__(self, path_template):

        results_file = open(os.path.join(path_template, "results.json"))
        results_data = results_file.read()
        results_dict = json.loads(results_data)

        for key in results_dict:
            setattr(self, key, results_dict[key])


class TestProForma(unittest.TestCase):

    def setUp(self):

        self.path_template = os.path.join(os.getcwd(), "tests", "pro_forma_test")
        self.econ = MockEconomics(self.path_template)
        self.results = MockResults(self.path_template)

    def test_cash_flow(self):

        cash_flow = ProForma(self.path_template, self.path_template, self.econ, self.results)
        cash_flow.update_template()
        cash_flow.compute_cashflow()

        # begin test asserts
        self.assertEqual(round(cash_flow.LCC_BAU, 0), 6739405, msg='LCC of {0} does not match expected result of {1}'.format(int(cash_flow.LCC), 6739405))
        self.assertEqual(round(cash_flow.LCC, 0), 6678063, "LCC bau does not match expected result")
        self.assertEqual(round(cash_flow.NPV, 0), 61342, "NPV does not match expected result")
        self.assertEqual(round(cash_flow.IRR * 100, 1), 10.4, "IRR does not match expected result")






