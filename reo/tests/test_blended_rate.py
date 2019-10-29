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
                },

                "Generator": {
                    "max_kw": "0",
                },
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

    def test_time_of_export_rate(self):
        """
        add a time-of-export rate that is greater than retail rate for the month of January,
        check to see if PV is exported for whole month of January.
        """
        jan_rate = self.post["Scenario"]["Site"]["ElectricTariff"]["blended_monthly_rates_us_dollars_per_kwh"][0]

        self.post["Scenario"]["Site"]["ElectricTariff"]["wholesale_rate_us_dollars_per_kwh"] = \
            [jan_rate + 0.1] * 31 * 24 + [0.0] * (8760 - 31*24)

        self.post["Scenario"]["Site"]["ElectricTariff"]["blended_monthly_demand_charges_us_dollars_per_kw"] = [0]*12
        response = self.get_response(self.post)
        pv_out = ClassAttributes(response['outputs']['Scenario']['Site']['PV'])
        financial = ClassAttributes(response['outputs']['Scenario']['Site']['Financial'])
        self.assertTrue(all(x == 0 for x in pv_out.year_one_to_load_series_kw[:744]))
        self.assertEqual(pv_out.size_kw, 70.2846)
        self.assertAlmostEqual(financial.lcc_us_dollars, 431483, -1)

        """
        Test huge export benefit beyond site load, such that PV ends up at limit
        """
        self.post["Scenario"]["Site"]["ElectricTariff"]["wholesale_rate_us_dollars_per_kwh"] = 0
        self.post["Scenario"]["Site"]["ElectricTariff"]["wholesale_rate_above_site_load_us_dollars_per_kwh"] = \
            [1] * 8760
        response = self.get_response(self.post)
        pv_out = ClassAttributes(response['outputs']['Scenario']['Site']['PV'])
        financial = ClassAttributes(response['outputs']['Scenario']['Site']['Financial'])
        self.assertAlmostEqual(financial.lcc_us_dollars, -1510001, -2)
        self.assertEqual(pv_out.size_kw, 200.0)

