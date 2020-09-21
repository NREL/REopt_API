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


class CHPTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(CHPTest, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_post = os.path.join('reo', 'tests', 'posts', 'test_chp_sizing_POST.json')

    def get_response(self, data):

        return self.api_client.post(self.reopt_base, format='json', data=data)

    #@skip("CHP test")
    def test_chp_sizing_decomposition_7pct(self):
        """
        Validation to ensure that:
         1) CHP Sizing is consistent

         This test was verified to be withing 1.5% gap after 10 mins of the Mosel/Xpress monolith using windows Xpress IVE

        :return:
        """

        # Call API, get results in "d" dictionary
        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data["Scenario"]["timeout_seconds"] = 420
        nested_data["Scenario"]["optimality_tolerance_bau"] = 0.001
        nested_data["Scenario"]["optimality_tolerance_techs"] = 0.07
        nested_data["Scenario"]["use_decomposition_model"] = True
        nested_data["Scenario"]["optimality_tolerance_decomp_subproblem"] = 0.03
        nested_data["Scenario"]["timeout_decomp_subproblem_seconds"] = 120
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

            # @skip("CHP test")

    def test_chp_sizing_monolith_1pct(self):
        """
        Validation to ensure that:
         1) CHP Sizing is consistent

         This test was verified to be withing 1.5% gap after 10 mins of the Mosel/Xpress monolith using windows Xpress IVE

        :return:
        """

        # Call API, get results in "d" dictionary
        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data["Scenario"]["timeout_seconds"] = 420
        nested_data["Scenario"]["optimality_tolerance_bau"] = 0.001
        nested_data["Scenario"]["optimality_tolerance_techs"] = 0.01
        nested_data["Scenario"]["use_decomposition_model"] = False
        nested_data["Scenario"]["optimality_tolerance_decomp_subproblem"] = 0.03
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat_chp(d['outputs'])

        # The values compared to the expected values may change if optimization parameters were changed
        d_expected = dict()
        d_expected['lcc'] = 13476072.0
        d_expected['npv'] = 1231748.579
        d_expected['chp_kw'] = 468.718
        d_expected['chp_year_one_fuel_used_mmbtu'] = 30555.6
        d_expected['chp_year_one_electric_energy_produced_kwh'] = 3086580.645
        d_expected['chp_year_one_thermal_energy_produced_mmbtu'] = 9739.972
        d_expected['boiler_total_fuel_cost_us_dollars'] = 7211.964
        d_expected['chp_total_fuel_cost_us_dollars'] = 3271904.872
        d_expected['total_opex_costs'] = 686311.0

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages'].get('error')))
            raise

