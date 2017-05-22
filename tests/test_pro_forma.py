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

        # expected values
        expected_bill_no_system = [0, 826030, 842551, 859402, 876590, 894121, 912004, 930244, 948849, 967826, 987182,
                                   1006926, 1027064, 1047606, 1068558, 1089929, 1111728, 1133962, 1156641, 1179774,
                                   1203370, 1227437, 1251986, 1277026, 1302566, 1328617]

        expected_bill_with_system = [0, 783215, 798879, 814857, 831154, 847777, 864733, 882027, 899668, 917661, 936014,
                                     954735, 973829, 993306, 1013172, 1033436, 1054104, 1075186, 1096690, 1118624,
                                     1140996, 1163816, 1187093, 1210834, 1235051, 1259752]

        expected_total_operating_expenses = [0, 4392, 4480, 4569, 4661, 4754, 4849, 4946, 5045, 5146, 94880, 5353, 5461,
                                             5570, 5681, 5795, 5911, 6029, 6149, 6272, 6398, 6526, 6656, 6790, 6925, 7064]

        expected_state_tax_liability = [0, 6766, 10647, 6520, 4046, 4053, 2199, 346, 353, 360, 6642, 375, 382, 390, 398,
                                        406, 414, 422, 430, 439, 448, 457, 466, 475, 485, 494]

        expected_federal_tax_liability = [0, 189782, 42436, 25986, 16127, 16153, 8766, 1380, 1407, 1436, 26472, 1494,
                                          1523, 1554, 1585, 1617, 1649, 1682, 1716, 1750, 1785, 1821, 1857, 1894, 1932,
                                          1971]

        expected_after_tax_annual_costs = [-542718, 192156, 48603, 27937, 15513, 15452, 6117, -3220, -3284, -3350,
                                           -61767, -3485, -3555, -3626, -3698, -3772, -3848, -3925, -4003, -4083, -4165,
                                           -4248, -4333, -4420, -4508, -4599]

        expected_after_tax_value = [0, 27873, 28430, 28999, 29579, 30170, 30774, 31389, 32017, 32657, 33310, 33977,
                                    34656, 35349, 36056, 36777, 37513, 38263, 39028, 39809, 40605, 41417, 42246, 43090,
                                    43952, 44831]

        expected_after_tax_cash_flow = [-542718, 220028, 77033, 56936, 45091, 45622, 36890, 28169, 28733, 29307, -28457,
                                        30491, 31101, 31723, 32358, 33005, 33665, 34338, 35025, 35726, 36440, 37169,
                                        37912, 38670, 39444, 40233]

        expected_net_annual_cost_without_sys = [0, -537746, -548500, -559470, -570660, -582073, -593715, -605589,
                                                -617701, -630055, -642656, -655509, -668619, -681991, -695631, -709544,
                                                -723735, -738209, -752974, -768033, -783394, -799062, -815043, -831344,
                                                -847971, -864930]

        expected_net_annual_cost_with_sys = [-542718, -317717, -471467, -502535, -525568, -536451, -556824, -577419,
                                             -588968, -600747, -671113, -625017, -637518, -650268, -663273, -676539,
                                             -690070, -703871, -717949, -732308, -746954, -761893, -777131, -792673,
                                             -808527, -824697]

        expected_cap_costs = 542718
        expected_state_depreciation_basis = 461310
        expected_state_itc_basis = 542718
        expected_fed_depreciation_basis = 461310
        expected_fed_itc_basis = 542718
        expected_lcc_bau = 6739405
        expected_lcc = 6714537
        expected_npv = 24868
        expected_irr = 8.96

        # begin test asserts
        self.assertListEqual([int(round(i, 0)) for i in cash_flow.bill_bau], expected_bill_no_system)
        self.assertListEqual([int(round(i, 0)) for i in cash_flow.bill_with_sys], expected_bill_with_system)
        self.assertListEqual([int(round(i, 0)) for i in cash_flow.total_operating_expenses], expected_total_operating_expenses)
        self.assertEqual(round(cash_flow.capital_costs, 0), expected_cap_costs, msg='CapCosts of {0} does not match expected result of {1}'.format(int(cash_flow.capital_costs), expected_cap_costs))
        self.assertEqual(round(cash_flow.state_depr_basis_calc, 0), expected_state_depreciation_basis)
        self.assertEqual(round(cash_flow.state_itc_basis_calc, 0), expected_state_itc_basis)
        self.assertEqual(round(cash_flow.fed_depr_basis_calc, 0), expected_fed_depreciation_basis)
        self.assertEqual(round(cash_flow.fed_itc_basis_calc, 0), expected_fed_itc_basis)
        self.assertListEqual([int(round(i, 0)) for i in cash_flow.state_tax_liability], expected_state_tax_liability)
        self.assertListEqual([int(round(i, 0)) for i in cash_flow.federal_tax_liability], expected_federal_tax_liability)
        self.assertListEqual([int(round(i, 0)) for i in cash_flow.after_tax_annual_costs], expected_after_tax_annual_costs)
        self.assertListEqual([int(round(i, 0)) for i in cash_flow.after_tax_value], expected_after_tax_value)
        self.assertListEqual([int(round(i, 0)) for i in cash_flow.after_tax_cash_flow], expected_after_tax_cash_flow)
        self.assertListEqual([int(round(i, 0)) for i in cash_flow.net_annual_cost_without_sys], expected_net_annual_cost_without_sys)
        self.assertListEqual([int(round(i, 0)) for i in cash_flow.net_annual_cost_with_sys], expected_net_annual_cost_with_sys)

        self.assertEqual(round(cash_flow.LCC_BAU, 0), expected_lcc_bau, msg='LCC bau of {0} does not match expected result of {1}'.format(int(cash_flow.LCC_BAU), expected_lcc_bau))
        self.assertEqual(round(cash_flow.LCC, 0), expected_lcc, msg='LCC of {0} does not match expected result of {1}'.format(int(cash_flow.LCC), expected_lcc))
        self.assertAlmostEqual(round(cash_flow.NPV, 0), expected_npv, delta=2, msg='NPV of {0} does not match expected result of {1}'.format(int(cash_flow.NPV), expected_npv))
        self.assertEqual(round(cash_flow.IRR * 100, 2), expected_irr, msg='IRR of {0} does not match expected result of {1}'.format(int(cash_flow.IRR), expected_irr))






