import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class TestEnergyTiers(ResourceTestCaseMixin, TestCase):
    """
    Tariff from Florida Light & Power (residential) with simple tiered energy rate:
    "energyratestructure":
    [[{"max": 1000, "rate": 0.07531, "adj": 0.0119, "unit": "kWh"}, {"rate": 0.09613, "adj": 0.0119, "unit": "kWh"}]]

    Testing with "annual_kwh": 24,000 such that the "year_one_energy_charges" should be:
        12,000 kWh * (0.07531 + 0.0119) $/kWh + 12,000 kWh * (0.09613 + 0.0119) $/kWh = $ 2,342.88
    """

    def setUp(self):
        super(TestEnergyTiers, self).setUp()

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
                            "urdb_response": {"sector": "Residential", "startdate": 1433116800, "fixedmonthlycharge": 7.57, "enddate": 1440975600, "name": "RS-1 Residential Service", "source": "https://www.fpl.com/rates/pdf/electric-tariff-section8.pdf", "supersedes": "53a455f05257a3ff4a8d8cf2", "uri": "https://openei.org/apps/USURDB/rate/view/5550d6fd5457a3187e8b4567", "label": "5550d6fd5457a3187e8b4567", "eiaid": 6452, "sourceparent": "https://www.fpl.com/rates.html", "energyratestructure": [[{"max": 1000, "rate": 0.07531, "adj": 0.0119, "unit": "kWh"}, {"rate": 0.09613, "adj": 0.0119, "unit": "kWh"}]], "energyweekendschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "energyweekdayschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "phasewiring": "Single Phase", "revisions": [1431339677, 1431340059, 1431528978, 1431529815, 1431530443, 1448395688], "energycomments": "Adjustment: Environmental, Storm Charge, Conservation, Capacity\r\nRate: Base rate and fuel", "utility": "Florida Power & Light Co."}
                          },

                          "PV": {
                            "max_kw": 0
                          },
                          "Wind": {
                            "max_kw": 0
                            },
                          "Storage": {
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

    # # the following is not needed b/c we test the app with Celery tasks in "eager" mode
    # # i.e. asynchronously. If we move to testing the API, then the while loop is needed
    # status = response['outputs']['Scenario']['status']
    # while status == "Optimizing...":
    #     time.sleep(2)
    #     response = json.loads(self.api_client.get(self.results_url + uuid).content)
    #     status = response['outputs']['Scenario']['status']

        return response

    def test_tiered_energy_rate(self):
        expected_year_one_energy_cost = 2342.88

        response = self.get_response(self.post)
        tariff_out = response['outputs']['Scenario']['Site']['ElectricTariff']
        profile_out = response['outputs']['Scenario']['Profile']
        messages = response['messages']

        try:
            self.assertEqual(tariff_out['year_one_energy_cost_us_dollars'], expected_year_one_energy_cost,
                             "Year one energy bill ({}) does not equal expected cost ({})."
                             .format(tariff_out['year_one_energy_cost_us_dollars'], expected_year_one_energy_cost))

            """
            self.assertGreater(profile_out['pre_setup_scenario'], 0, "Profiling results failed")
            self.assertGreater(profile_out['setup_scenario'], 0, "Profiling results failed")
            self.assertGreater(profile_out['reopt'], 0, "Profiling results failed")
            self.assertGreater(profile_out['reopt_bau'], 0, "Profiling results failed")
            self.assertGreater(profile_out['parse_run_outputs'], 0, "Profiling results failed")
            """

        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("test_tiered_energy_rate API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e
