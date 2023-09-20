# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
import json
import os
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
from reo.models import ModelManager

class SOCIncentiveTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1.0e-2

    def setUp(self):
        super(SOCIncentiveTests, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_post = os.path.join('reo', 'tests', 'posts', 'socIncentivePost.json')

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_soc_incentive(self):
        """
        Test scenario with
        - fixed PV of 100 kW
        - fixed battery of 20kW, 20kWh
        - no other techs
        Toggle on and off the SOC incentive in the objective function and compare average SOC and LCC's.
        """
        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['add_soc_incentive'] = True
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        high_avg_soc = (sum(d['outputs']['Scenario']['Site']['Storage']['year_one_soc_series_pct']) /
                        len(d['outputs']['Scenario']['Site']['Storage']['year_one_soc_series_pct']))

        nested_data['Scenario']['add_soc_incentive'] = False
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        low_avg_soc = (sum(d['outputs']['Scenario']['Site']['Storage']['year_one_soc_series_pct']) /
                       len(d['outputs']['Scenario']['Site']['Storage']['year_one_soc_series_pct']))

        self.assertGreater(high_avg_soc, low_avg_soc, "Average SOC should be higher when including SOC incentive.")
