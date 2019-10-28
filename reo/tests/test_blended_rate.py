import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class ClassAttributes:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)


class TestBlendedRate(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestBlendedRate, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = {"Scenario": {
            "time_steps_per_hour": 1,
            "description": "name_with_underscore",
            "Site": {
                "latitude": 35.2468,
                "longitude": -91.7337,

                "LoadProfile": {
                    "doe_reference_name": "MidriseApartment",
                    "annual_kwh": 259525,
                    "year": 2017
                },

                "ElectricTariff": {
                    "urdb_rate_name": "custom",
                    "blended_monthly_rates_us_dollars_per_kwh": [0.15, 0.2, 0.21, 0.23, 0.27, 0.19, 0.22, 0.17, 0.24, 0.26, 0.18, 0.2],
                    "blended_monthly_demand_charges_us_dollars_per_kw": [0.08, 0.11, 0, 0, 0.15, 0.14, 0.09, 0.06, 0, 0, 0.05, 0]
                },

                "PV": {
                    "max_kw": "200",
                    "existing_kw" : "0"
                },

                "Storage": {
                    "max_kw": 0,
                    "max_kwh": 0,
                },

                "Wind": {
                    "max_kw": 0,
                    "max_kwh": 0,
                }
            }
        }
        }

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        uuid = json.loads(initial_post.content)['run_uuid']
        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
        return response

    def test_blended_rate(self):
        """
        Test that self.post scenario, with monthly rates, returns the expected LCC and PV station attributes
        """
        response = self.get_response(self.post)

        pv_out = ClassAttributes(response['outputs']['Scenario']['Site']['PV'])
        financial = ClassAttributes(response['outputs']['Scenario']['Site']['Financial'])

        self.assertEqual(pv_out.station_distance_km, 0.0)
        self.assertEqual(pv_out.station_latitude, 35.25)
        self.assertAlmostEqual(pv_out.station_longitude, -91.74, 1)
        self.assertAlmostEqual(financial.lcc_us_dollars, 437842, -1)

    def test_blended_annual_rate(self):
        """
        Test that self.post scenario returns the expected LCC with annual blended rates
        """
        # remove monthly rates (because they are used before annual rates)
        self.post["Scenario"]["Site"]["ElectricTariff"]["blended_monthly_rates_us_dollars_per_kwh"] = None
        self.post["Scenario"]["Site"]["ElectricTariff"]["blended_monthly_demand_charges_us_dollars_per_kw"] = None
        # add annual rates
        self.post["Scenario"]["Site"]["ElectricTariff"]["blended_annual_rates_us_dollars_per_kwh"] = 0.2
        self.post["Scenario"]["Site"]["ElectricTariff"]["blended_annual_demand_charges_us_dollars_per_kw"] = 0.0

        response = self.get_response(self.post)
        financial = ClassAttributes(response['outputs']['Scenario']['Site']['Financial'])
        self.assertAlmostEqual(financial.lcc_us_dollars, 422437, -1)
