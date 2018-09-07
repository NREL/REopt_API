import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class TestBlendedRate(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestBlendedRate, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = {"Scenario": {
            "Site": {
                "latitude": 35.2468,
                "longitude": -91.7337,

                "LoadProfile": {
                    "doe_reference_name": "MidriseApartment",
                    "year": 2017,
                },

                "ElectricTariff": {
                    "urdb_rate_name": "custom",
                    "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2,0.2],
                    "blended_monthly_demand_charges_us_dollars_per_kw": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                },

                "PV": {
                    "max_kw": "200"

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

    """
    def testing(self):
        response = self.get_response(self.post)
        #print(response)
    """


    def test_blended_rate(self):

        class ClassAttributes:
            def __init__(self, dictionary):
                for k, v in dictionary.items():
                    setattr(self, k, v)

        pv_size = 0
        existing_kw = pv_size
        #max_kw = pv_size
        flat_load = [pv_size] * 8760

        #self.post['Scenario']['Site']['PV']['existing_kw'] = existing_kw
        #self.post['Scenario']['Site']['PV']['max_kw'] = max_kw
        #self.post['Scenario']['Site']['LoadProfile']['loads_kw_is_net'] = True
        #self.post['Scenario']['Site']['LoadProfile']['loads_kw'] = flat_load

        response = self.get_response(self.post)

        pv_out = ClassAttributes(response['outputs']['Scenario']['Site']['PV'])
        load_out = ClassAttributes(response['outputs']['Scenario']['Site']['LoadProfile'])
        financial = ClassAttributes(response['outputs']['Scenario']['Site']['Financial'])
        messages = ClassAttributes(response['messages'])

        net_load = [a - round(b,3) for a, b in zip(load_out.year_one_electric_load_series_kw, pv_out.year_one_power_production_series_kw)]
