import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class TestDemandRatchets(ResourceTestCaseMixin, TestCase):
    """
    Tariff from Florida Light & Power (residential) with simple tiered energy rate:
    "energyratestructure":
    [[{"max": 1000, "rate": 0.07531, "adj": 0.0119, "unit": "kWh"}, {"rate": 0.09613, "adj": 0.0119, "unit": "kWh"}]]

    Testing with "annual_kwh": 24,000 such that the "year_one_energy_charges" should be:
        12,000 kWh * (0.07531 + 0.0119) $/kWh + 12,000 kWh * (0.09613 + 0.0119) $/kWh = $ 2,342.88
    """

    def setUp(self):
        super(TestDemandRatchets, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = {"Scenario": {
                        "Site": {
                          "latitude": 35.2468,
                          "longitude": -91.7337,

                          "LoadProfile": {
                            "doe_reference_name": "MidriseApartment",
                            "year": 2017,
                            "annual_kwh": 24000
                          },

                          "ElectricTariff": {
                            "urdb_label": "539f6a23ec4f024411ec8bf9"
                          },

                          "PV": {
                            "max_kw": 0
                          },

                          "Storage": {
                              "max_kw": 0,
                              "max_kwh": 0,
                          },

                          "Wind": {
                            "max_kw": 0
                          },

                        }
                      }
                    }

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        uuid = json.loads(initial_post.content)['run_uuid']

        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)

        # # the following is not needed b/c we test the app with Celery tasks in "eager" mode
        # # i.e. asynchronously. If we move to testing the API, then the while loop is needed
        # status = response['outputs']['Scenario']['status']
        # while status == "Optimizing...":
        #     time.sleep(2)
        #     response = json.loads(self.api_client.get(self.results_url + uuid).content)
        #     status = response['outputs']['Scenario']['status']

        return response

    def test_demand_ratchet_rate(self):
        expected_year_one_demand_flat_cost = 721.99

        response = self.get_response(self.post)
        tariff_out = response['outputs']['Scenario']['Site']['ElectricTariff']
        messages = response['messages']

        try:
            self.assertEqual(tariff_out['year_one_demand_cost_bau_us_dollars'], expected_year_one_demand_flat_cost,
                             "Year one  demand cost ({}) does not equal expected  demand cost ({})."
                             .format(tariff_out['year_one_demand_cost_bau_us_dollars'], expected_year_one_demand_flat_cost))

        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("test_tiered_energy_rate API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e
