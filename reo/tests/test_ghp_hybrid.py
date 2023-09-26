# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
import json
import os
import pandas as pd
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
from reo.models import ModelManager

class GHPTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(GHPTest, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_reopt_post = os.path.join('reo', 'tests', 'posts', 'test_ghp_hybrid_POST.json')
        self.test_ghpghx_post = os.path.join('ghpghx', 'tests', 'posts', 'test_hybrid_ghpghx_POST.json')

    def get_ghpghx_response(self, data):
        return self.api_client.post(self.ghpghx_base, format='json', data=data)

    def get_reopt_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_ghp(self):
        """

        This tests the automatic sizing functionality of hybrid GHP

        """
        nested_data = json.load(open(self.test_reopt_post, 'rb'))
        ghpghx_post = json.load(open(self.test_ghpghx_post, 'rb'))

        nested_data["Scenario"]["Site"]["GHP"]["ghpghx_inputs"] = [ghpghx_post]
        
        # Call REopt
        resp = self.get_reopt_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        ghp_uuid = d["outputs"]["Scenario"]["Site"]["GHP"]["ghp_chosen_uuid"]
        print("GHP uuid chosen = ", ghp_uuid)

        # Output number of boreholes and heatpump sizing 
        n_boreholes = d["outputs"]["Scenario"]["Site"]["GHP"]["ghpghx_chosen_outputs"]["number_of_boreholes"]
        heatpump_tons = d["outputs"]["Scenario"]["Site"]["GHP"]["ghpghx_chosen_outputs"]["peak_combined_heatpump_thermal_ton"]
        aux_cooler_annual_thermal_production_kwht = sum(d["outputs"]["Scenario"]["Site"]["GHP"]["ghpghx_chosen_outputs"]["yearly_aux_cooler_thermal_production_series_kwt"])
        aux_heater_annual_thermal_production_mmbtu = sum(d["outputs"]["Scenario"]["Site"]["GHP"]["ghpghx_chosen_outputs"]["yearly_aux_heater_thermal_production_series_mmbtu_per_hour"])
        
        # Comparison to TESS exe range
        # TODO: Number of boreholes vary between runs with the same input
        # self.assertAlmostEqual(n_boreholes, 45)
        self.assertAlmostEqual(heatpump_tons, 824.927)
        self.assertAlmostEqual(aux_cooler_annual_thermal_production_kwht, 0.0)
        self.assertGreater(aux_heater_annual_thermal_production_mmbtu, 480.0)
