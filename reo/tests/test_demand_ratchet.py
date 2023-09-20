# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
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
        self.post = {
          "Scenario": {
            "webtool_uuid": None,
            "description": "",
            "timeout_seconds": 295,
            "Site": {
              "PV": {
                "max_kw": 0.0
              },
              "LoadProfile": {
                "year": 2017
              },
              "Storage": {
                "max_kwh": 0.0,
                "max_kw": 0.0
              },
              "land_acres": None,
              "ElectricTariff": {
                "urdb_label": "539f6a23ec4f024411ec8bf9",
              },
              "longitude": -84.387982,
              "roof_squarefeet": None,
              "latitude": 33.748995,
              "Financial": {
                "escalation_pct": 0.0,
                "offtaker_discount_pct": 0.0,
                "offtaker_tax_pct": 0.0,
                "om_cost_escalation_pct": 0.0
              }
            },
            "time_steps_per_hour": 1,
            "user_uuid": None
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
        # urdb_label used https://apps.openei.org/IURDB/rate/view/539f6a23ec4f024411ec8bf9#2__Demand
        # has a demand charge lookback of 35% for all months with 2 different demand charges based on which month        
        self.post["Scenario"]["Site"]["LoadProfile"]["loads_kw"] = [1.0]*8760
        self.post["Scenario"]["Site"]["LoadProfile"]["loads_kw"][8] = 100.0
        # Expected result is 100 kW demand for January, 35% of that for all other months and 
        # with 5x other $10.5/kW cold months and 6x $11.5/kW warm months        
        expected_year_one_demand_flat_cost = 100 * (10.5 + 0.35*10.5*5 + 0.35*11.5*6)

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
