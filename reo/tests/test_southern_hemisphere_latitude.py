# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
import json
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
from reo.models import ModelManager
import numpy as np

class NegativeLatitudeTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(NegativeLatitudeTest, self).setUp()
        self.reopt_base = '/v2/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_southern_hemisphere_latitude(self):
        """
        Tests locations in the Southern Hemisphere (Indonesia) 
        where the tilt must be set to the latitude (array type 0 - Ground Mount Fixed (Open Rack)).
        In these cases we need to make the negative latitude positive and set the azimuth to 0.
        Also tests that NSRDB HIMIWARI data for SE Asia is utilized to determine the PV prod factor.

        :return:
        """

        nested_data = {"Scenario": {
                "Site": {
                    "longitude": 130.1452734,
                    "latitude": -3.2384616, 
                "PV": {
                    "min_kw": 1000,
                    "max_kw": 1000,
                    'array_type': 0,
                    'degradation_pct': 0.0
                },
                "LoadProfile": {
                    "doe_reference_name": "FlatLoad",
                    "annual_kwh": 10000000.0,
                    "city": "LosAngeles"
                },
                "ElectricTariff": {
                    "urdb_label": "5ed6c1a15457a3367add15ae"
                },
                "Financial": {
                    "escalation_pct": 0.026,
                    "analysis_years": 25
                }
            }}}

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        messages = d['messages']

        a = d["outputs"]["Scenario"]["Site"]["PV"]
        pv_list = a['year_one_to_battery_series_kw'], a['year_one_to_load_series_kw'], a['year_one_to_grid_series_kw'], a['year_one_curtailed_production_series_kw']
        tot_pv = np.sum(pv_list, axis=0)
        total_pv = sum(tot_pv)

        try:
            self.assertEqual(d['inputs']['Scenario']['Site']['PV']['azimuth'], 0,
                             "Not adjusting azimuth for negative latitudes.")

            self.assertEqual(d['inputs']['Scenario']['Site']['PV']['tilt'], 3.2384616,
                             "Not adjusting tilt for negative latitudes"
                             )
            self.assertAlmostEqual(total_pv, 1246915, delta=0.5) # checked against PVWatts online calculator

        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("NegativeLatitudeTest API error message: {}".format(error_msg))
            print("Run uuid: {}".format(d['outputs']['Scenario']['run_uuid']))
            raise e

