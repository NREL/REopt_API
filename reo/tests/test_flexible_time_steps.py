import json
#from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from reo.nested_to_flat_output import nested_to_flat
from reo.models import ModelManager
from reo.utilities import check_common_outputs

fts_post_1 = {"Scenario": {
            "time_steps_per_hour": 1,
            "Site": {
                "latitude": 35.2468,
                "longitude": -91.7337,

                "LoadProfile": {
                    "doe_reference_name": "MidriseApartment",
                    "annual_kwh": 229671,
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

fts_post_2 = {"Scenario": {
            "time_steps_per_hour": 4,
            "Site": {
                "latitude": 35.2468,
                "longitude": -91.7337,

                "LoadProfile": {
                    "doe_reference_name": "MidriseApartment",
                    "annual_kwh": 229671,
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


class TestFlexibleTimeSteps(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestFlexibleTimeSteps, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'

    def get_response(self, data):
        return self.api_client.post(self.submit_url, format='json', data=data)


    def test_flexible_time_steps(self):
        """
        - Validation to ensure that upon entering time_steps_per_hour=1 or 4, the results of the analysis
        are as expected (keeping wind and storage off for the time being)
        - the output csv files dimensions (8760, 35040 etc) must also match time_steps_per_hour given as input
        :return:
        """

        self.REopt_tol = 1e-2

        # results for time_steps_per_hour = 1
        response1 = self.get_response(fts_post_1)
        self.assertHttpCreated(response1)
        r1 = json.loads(response1.content)
        run_uuid1 = r1.get('run_uuid')
        d1 = ModelManager.make_response(run_uuid=run_uuid1)
        c1 = nested_to_flat(d1['outputs'])
        print(d1['messages'])

        # results for time_steps_per_hour = 2
        response2 = self.get_response(fts_post_2)
        self.assertHttpCreated(response2)
        r2 = json.loads(response2.content)
        run_uuid2 = r2.get('run_uuid')
        d2 = ModelManager.make_response(run_uuid=run_uuid2)
        c2 = nested_to_flat(d2['outputs'])

        try:
            check_common_outputs(self, c1, c2)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid2))
            #print("Error message with ts=1: {}".format(d1['messages']))
            print("Error message with ts=2: {}".format(d2['messages']))
            raise




        """
        class ClassAttributes:
            def __init__(self, dictionary):
                for k, v in dictionary.items():
                    setattr(self, k, v)

        pv_out = ClassAttributes(response2['outputs']['Scenario']['Site']['PV'])
        load_out = ClassAttributes(response2['outputs']['Scenario']['Site']['LoadProfile'])
        financial = ClassAttributes(response2['outputs']['Scenario']['Site']['Financial'])
        messages = ClassAttributes(response2['messages'])
        """
