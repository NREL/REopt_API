import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class TestEnergyTiers(ResourceTestCaseMixin, TestCase):
    """
    Tariff from  Entergy Louisiana Inc with simple modifued tiered demand rate such that some demand buckets are used (i.e. bottom two) and others are not for this load:
    "flatdemandstructure":
    [[{"max": 300, "rate": 0}, {"max": 400, "rate": 13.48}, {"max": 500, "rate": 14.48}]]

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
                            "doe_reference_name": "Hospital",
                            "year": 2017,
                            "annual_kwh": 2400000
                          },

                          "ElectricTariff": {
                            "urdb_response": {"sector": "Industrial", "peakkwcapacitymax": 125000, "demandcomments": "$0.41 per rkVA of Reactive Demand in excess of 25% of the Firm Demand.", "utility": "Entergy Louisiana Inc", "energyratestructure": [[{"rate": 0.00258, "adj": 0.027304, "unit": "kWh"}]], "energyweekendschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "demandrateunit": "kW", "flatdemandstructure": [[{"max": 300, "rate": 0}, {"max": 400, "rate": 13.48}, {"max": 500, "rate": 14.48}]], "startdate": 1506553200, "phasewiring": "3-Phase", "eiaid": 11241, "label": "5a552cd45457a32374423a7c", "flatdemandunit": "kW", "source": "http://www.entergy-louisiana.com/content/price/tariffs/LA/ell_elec_lips-l.pdf", "voltagecategory": "Transmission", "revisions": [1515506276, 1515506301, 1515506634], "energycomments": "Adjustments = Average of Fuel Adjustments (2017) + Environmental Adjustment \r\n+ Financed Storm Cost riders I, II, and II + Storm Cost Offset Rider \r\n+ Securitized Little Gypsy rider.", "supersedes": "58f11dbf5457a3770f08f4b6", "voltageminimum": 115000, "description": "This rate does not apply to service supplied in the 15th Ward of the City of New Orleans (Algiers).\r\nTo Electric Service up to 125,000 kilowatts for industrial purposes, including lighting and\r\nother uses accessory thereto, and for other Service for which no specific Rate Schedule\r\nis provided. All Service is supplied through one metering installation at one Point of\r\nDelivery. Lighting and incidental Service supplied through other Meters will be billed at\r\nthe schedule applicable to such Service. Service hereunder is subject to any of the\r\nCompany's Rider Schedules that may be applicable. Service under this schedule shall\r\nnot be resold, sub-metered, used for standby, or shared with others.", "sourceparent": "http://www.entergy-louisiana.com/your_business/ELI_Tariffs.aspx", "energyweekdayschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "flatdemandmonths": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "approved": True, "fixedmonthlycharge": 249720.88, "name": "Large Industrial Power Service (LIPS-L)", "uri": "https://openei.org/apps/USURDB/rate/view/5a552cd45457a32374423a7c", "demandreactivepowercharge": 0.41, "usenetmetering": True},
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

    def test_tiered_demand_rate(self):
        expected_year_one_energy_cost = 71712.0

        response = self.get_response(self.post)
        tariff_out = response['outputs']['Scenario']['Site']['ElectricTariff']
        profile_out = response['outputs']['Scenario']['Profile']
        messages = response['messages']

        try:
            self.assertEqual(tariff_out['year_one_energy_cost_us_dollars'], expected_year_one_energy_cost,
                             "Year one energy bill ({}) does not equal expected cost ({})."
                             .format(tariff_out['year_one_energy_cost_us_dollars'], expected_year_one_energy_cost))

            self.assertGreater(profile_out['pre_setup_scenario_seconds'], 0, "Profiling results failed")
            self.assertGreater(profile_out['setup_scenario_seconds'], 0, "Profiling results failed")
            self.assertGreater(profile_out['reopt_seconds'], 0, "Profiling results failed")
            self.assertGreater(profile_out['reopt_bau_seconds'], 0, "Profiling results failed")
            self.assertGreater(profile_out['parse_run_outputs_seconds'], 0, "Profiling results failed")


        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("test_tiered_energy_rate API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e
