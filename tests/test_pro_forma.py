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


        expected_cap_costs = 542718
        expected_lcc_bau = 6739405
        expected_lcc = 6714537
        expected_npv = 24868
        expected_irr = 8.96

        # begin test asserts
        self.assertListEqual([int(round(i, 0)) for i in cash_flow.bill_bau], expected_bill_no_system)
        self.assertListEqual([int(round(i, 0)) for i in cash_flow.bill_with_sys], expected_bill_with_system)
        self.assertListEqual([int(round(i, 0)) for i in cash_flow.total_operating_expenses], expected_total_operating_expenses)
        self.assertEqual(round(cash_flow.capital_costs, 0), expected_cap_costs, msg='CapCosts of {0} does not match expected result of {1}'.format(int(cash_flow.capital_costs), expected_cap_costs))
        self.assertEqual(round(cash_flow.LCC_BAU, 0), expected_lcc_bau, msg='LCC bau of {0} does not match expected result of {1}'.format(int(cash_flow.LCC_BAU), expected_lcc_bau))
        self.assertEqual(round(cash_flow.LCC, 0), expected_lcc, msg='LCC of {0} does not match expected result of {1}'.format(int(cash_flow.LCC_), expected_lcc))
        self.assertEqual(round(cash_flow.NPV, 0), expected_npv, msg='NPV of {0} does not match expected result of {1}'.format(int(cash_flow.NPV), expected_npv))
        self.assertEqual(round(cash_flow.IRR * 100, 1), expected_irr, msg='IRR of {0} does not match expected result of {1}'.format(int(cash_flow.IRR), expected_irr))






