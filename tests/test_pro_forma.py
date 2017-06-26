import unittest
import os
import json

from reo.pro_forma_writer import ProForma


class MockEconomics:

    # class to mimic an economic object with data that matches the ProForma template
    def __init__(self, path_template, case_number):

        case_file = "econ_" + str(case_number) + ".json"

        econ_file = open(os.path.join(path_template, case_file))
        econ_data = econ_file.read()
        self.econ_dict = json.loads(econ_data)

        for key in self.econ_dict:
            setattr(self, key, self.econ_dict[key])


class MockResults:

    # class to mimic a results object with data that matches the ProForma template
    def __init__(self, path_template, case_number):

        case_file = "results_" + str(case_number) + ".json"

        results_file = open(os.path.join(path_template, case_file))
        results_data = results_file.read()
        self.results_dict = json.loads(results_data)

        for key in self.results_dict:
            setattr(self, key, self.results_dict[key])


class MockCashFlow:
    # class to mimic a results object with data that matches the ProForma template
    def __init__(self, path_template, case_number):
        case_file = "expected_" + str(case_number) + ".json"

        expected_file = open(os.path.join(path_template, case_file))
        expected_data = expected_file.read()
        self.expected_dict = json.loads(expected_data)

        for key in self.expected_dict:
            setattr(self, key, self.expected_dict[key])


def round_list(list1):
    return [int(round(i, 0)) for i in list1]


class TestProForma(unittest.TestCase):

    def setUp(self):
        self.num_scenarios = 1
        self.delta = 2 # allowed variation in values

    def setUpScenario(self, case_number):
        print "Setting up scenario: " + str(case_number)
        self.path_template = os.path.join(os.getcwd(), "tests", "pro_forma_test")
        self.econ = MockEconomics(self.path_template, case_number)
        self.results = MockResults(self.path_template, case_number)
        self.cf = MockCashFlow(self.path_template, case_number)

    def test_cash_flow(self):

        for case in range(0, self.num_scenarios):
            self.setUpScenario(case)

            cash_flow = ProForma(self.path_template, self.path_template, self.econ, self.results.results_dict)
            cash_flow.update_template()
            cash_flow.compute_cashflow()

            # begin test asserts
            self.assertListEqual(round_list(cash_flow.bill_bau), round_list(self.cf.expected_bill_no_system))
            self.assertListEqual(round_list(cash_flow.bill_with_sys), round_list(self.cf.expected_bill_with_system))
            self.assertListAlmostEqual(round_list(cash_flow.total_operating_expenses), round_list(self.cf.expected_total_operating_expenses), self.delta)
            self.assertEqual(round(cash_flow.capital_costs, 0), round(self.cf.expected_cap_costs), msg='CapCosts of {0} does not match expected result of {1}'.format(int(cash_flow.capital_costs), self.cf.expected_cap_costs))
            self.assertEqual(round(cash_flow.fed_itc_basis_calc, 0), round(self.cf.expected_fed_itc_basis))
            self.assertEqual(round(cash_flow.fed_depr_basis_calc, 0), round(self.cf.expected_fed_depreciation_basis))
            self.assertListEqual(round_list(cash_flow.federal_tax_liability), round_list(self.cf.expected_federal_tax_liability))
            self.assertListEqual(round_list(cash_flow.after_tax_annual_costs), round_list(self.cf.expected_after_tax_annual_costs))
            self.assertListEqual(round_list(cash_flow.after_tax_value), round_list(self.cf.expected_after_tax_value))
            self.assertListEqual(round_list(cash_flow.after_tax_cash_flow), round_list(self.cf.expected_after_tax_cash_flow))
            self.assertListEqual(round_list(cash_flow.net_annual_cost_without_sys), round_list(self.cf.expected_net_annual_cost_without_sys))
            self.assertListEqual(round_list(cash_flow.net_annual_cost_with_sys), round_list(self.cf.expected_net_annual_cost_with_sys))

            self.assertEqual(round(cash_flow.lcc_bau, 0), round(self.cf.expected_lcc_bau), msg='LCC bau of {0} does not match expected result of {1}'.format(int(cash_flow.lcc_bau), self.cf.expected_lcc_bau))
            self.assertEqual(round(cash_flow.lcc, 0), round(self.cf.expected_lcc), msg='LCC of {0} does not match expected result of {1}'.format(int(cash_flow.lcc), self.cf.expected_lcc))
            self.assertAlmostEqual(round(cash_flow.npv, 0), round(self.cf.expected_npv), delta=2, msg='NPV of {0} does not match expected result of {1}'.format(int(cash_flow.npv), self.cf.expected_npv))
            self.assertEqual(round(cash_flow.irr, 2), round(self.cf.expected_irr, 2), msg='IRR of {0} does not match expected result of {1}'.format(cash_flow.irr, self.cf.expected_irr))

    def assertListAlmostEqual(self, list1, list2, delta):

        self.assertEqual(len(list1), len(list2))

        for i in range(0, len(list1)):
            self.assertAlmostEqual(list1[i], list2[i], delta=delta)




