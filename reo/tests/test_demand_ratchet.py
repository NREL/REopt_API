import time
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
                          "latitude": 33.748995,
                          "longitude": -84.387982,

                          "LoadProfile": {
                            "doe_reference_name": "MidriseApartment",
                            "year": 2017,
                            "annual_kwh": 24000
                          },

                          "ElectricTariff": {
                            "urdb_response": {"sector": "Industrial", "utility": "Town of Wallingford, Connecticut (Utility Company)", "energyratestructure": [[{"rate": 0.0687, "adj": 0.008376, "unit": "kWh"}], [{"rate": 0.0619, "adj": 0.008376, "unit": "kWh"}]], "energyweekendschedule": [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], "revisions": [1376316457, 1376316486, 1399411674, 1399585108, 1401288502, 1402428494, 1402433957, 1427405196], "flatdemandstructure": [[{"rate": 11.5}], [{"rate": 10.5}]], "startdate": 1372658400, "phasewiring": "3-Phase", "source": "http://www.town.wallingford.ct.us/images/customer-files//EDRate5110813.pdf", "label": "539f6a23ec4f024411ec8bf9", "flatdemandunit": "kW", "eiaid": 20038, "demandrateunit": "kW", "energycomments": "energy adjustments can be found here: http://www.town.wallingford.ct.us/images/customer-files//EDRate12PCAHist60514.pdf", "sourceparent": "http://www.town.wallingford.ct.us/Content/Retail_Rates_and_Fees.asp", "energyweekdayschedule": [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], "flatdemandmonths": [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1], "approved": "true", "demandratchetpercentage": [0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35], "enddate": 1383199200, "name": "Primary Service - Northford", "fixedmonthlycharge": 275, "uri": "https://openei.org/apps/USURDB/rate/view/539f6a23ec4f024411ec8bf9", "peakkwcapacitymin": 400, "demandreactivepowercharge": 2.7}
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
