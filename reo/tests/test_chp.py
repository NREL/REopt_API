import json
import copy
import os
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat_chp
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from unittest import skip
from reo.models import ModelManager
from reo.utilities import check_common_outputs
from reo.validators import ValidateNestedInput
import numpy as np

class CHPTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(CHPTest, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_post = os.path.join('reo', 'tests', 'posts', 'test_chp_sizing_POST.json')

    def get_response(self, data):

        return self.api_client.post(self.reopt_base, format='json', data=data)

    #@skip("CHP test")
    def test_chp_sizing(self):
        """
        Validation to ensure that:
         1) CHP Sizing is consistent

         This test was verified to be withing 1.5% gap after 10 mins of the Mosel/Xpress monolith using windows Xpress IVE

        :return:
        """

        # Call API, get results in "d" dictionary
        nested_data = json.load(open(self.test_post, 'rb'))
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat_chp(d['outputs'])

        # The values compared to the expected values may change if optimization parameters were changed
        d_expected = dict()
        d_expected['lcc'] = 13480652.87
        d_expected['npv'] = 1227168.13
        d_expected['chp_kw'] = 554.28
        d_expected['chp_year_one_fuel_used_mmbtu'] = 34756.08
        d_expected['chp_year_one_electric_energy_produced_kwh'] = 3489855.76
        d_expected['chp_year_one_thermal_energy_produced_mmbtu'] = 9759.82
        d_expected['boiler_total_fuel_cost_us_dollars'] = 4555.27
        d_expected['chp_total_fuel_cost_us_dollars'] = 3721693.94
        d_expected['total_opex_costs'] = 811596.0

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages'].get('error')))
            raise

    def test_cost_curve(self):
        """
        Validation to ensure that:
         1) CHP capital cost curve handling is correct
         2)

        :return:
        """

        # Call API, get results in "d" dictionary
        nested_data = json.load(open(self.test_post, 'rb'))
        # CHP
        nested_data["Scenario"]["Site"]["CHP"] = {}
        nested_data["Scenario"]["Site"]["CHP"]["prime_mover"] = "recip_engine"
        nested_data["Scenario"]["Site"]["CHP"]["size_class"] = 2
        nested_data["Scenario"]["Site"]["CHP"]["min_kw"] = 800
        nested_data["Scenario"]["Site"]["CHP"]["max_kw"] = 800
        nested_data["Scenario"]["Site"]["CHP"]["installed_cost_us_dollars_per_kw"] = [2900, 2700, 2370]
        nested_data["Scenario"]["Site"]["CHP"]["tech_size_for_cost_curve"] = [100, 600, 1140]
        #nested_data["Scenario"]["Site"]["CHP"]["utility_rebate_us_dollars_per_kw"] = 50
        #nested_data["Scenario"]["Site"]["CHP"]["utility_rebate_max_us_dollars"] = 1.0E10 #50 * 200
        #nested_data["Scenario"]["Site"]["CHP"]["federal_rebate_us_dollars_per_kw"] = 50
        nested_data["Scenario"]["Site"]["CHP"]["federal_itc_pct"] = 0.1
        nested_data["Scenario"]["Site"]["CHP"]["macrs_option_years"] = 0
        nested_data["Scenario"]["Site"]["CHP"]["macrs_bonus_pct"] = 0
        nested_data["Scenario"]["Site"]["CHP"]["macrs_itc_reduction"] = 0.0

        init_capex_chp_expected = 2020666.67
        net_capex_chp_expected = init_capex_chp_expected - np.npv(0.083, [0, init_capex_chp_expected * 0.1])

        #PV
        nested_data["Scenario"]["Site"]["PV"]["min_kw"] = 1500
        nested_data["Scenario"]["Site"]["PV"]["max_kw"] = 1500
        nested_data["Scenario"]["Site"]["PV"]["installed_cost_us_dollars_per_kw"] = 1600
        nested_data["Scenario"]["Site"]["PV"]["federal_itc_pct"] = 0.26
        nested_data["Scenario"]["Site"]["PV"]["macrs_option_years"] = 0
        nested_data["Scenario"]["Site"]["PV"]["macrs_bonus_pct"] = 0
        nested_data["Scenario"]["Site"]["PV"]["macrs_itc_reduction"] = 0.0

        init_capex_pv_expected = 1500 * 1600
        net_capex_pv_expected = init_capex_pv_expected - np.npv(0.083, [0, init_capex_pv_expected * 0.26])

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        init_capex_total_expected = init_capex_chp_expected + init_capex_pv_expected
        net_capex_total_expected = net_capex_chp_expected + net_capex_pv_expected

        init_capex_total = d["outputs"]["Scenario"]["Site"]["Financial"]["initial_capital_costs"]
        net_capex_total = d["outputs"]["Scenario"]["Site"]["Financial"]["net_capital_costs"]


        # # The values compared to the expected values may change if optimization parameters were changed
        self.assertAlmostEqual(init_capex_total_expected, init_capex_total, delta=1.0)
        self.assertAlmostEqual(net_capex_total_expected, net_capex_total, delta=1.0)


