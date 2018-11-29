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
                    "blended_monthly_rates_us_dollars_per_kwh": [0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29],
                    "blended_monthly_demand_charges_us_dollars_per_kw": [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
                },

                "PV": {
                    "max_kw": 0

                },

                "Storage": {
                    "max_kw": 0,
                    "max_kwh": 0,
                },

                "Wind": {
                    "max_kw": 35,
                    "min_kw":35
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
                    "blended_monthly_rates_us_dollars_per_kwh": [0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29],
                    "blended_monthly_demand_charges_us_dollars_per_kw": [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
                },

                "PV": {
                    "max_kw": 0

                },

                "Storage": {
                    "max_kw": 0,
                    "max_kwh": 0,
                },

                "Wind": {
                    "max_kw": 35,
                    "min_kw": 35
                }
            }
        }
        }



class TestFlexibleTimeSteps(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(TestFlexibleTimeSteps, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)


    def test_flexible_time_steps(self):
        """
        - Validation to ensure that upon entering time_steps_per_hour=1 or 4, the results of the analysis
        are as expected (keeping pv and storage off to test wind module's performance)
        - the output csv files dimensions (8760, 35040 etc) must also match time_steps_per_hour given as input
        :return:
        """

        self.REopt_tol = 1e-2

        
        # results for time_steps_per_hour = 1
        resp1 = self.get_response(data=fts_post_1)
        self.assertHttpCreated(resp1)
        r1 = json.loads(resp1.content)
        run_uuid1 = r1.get('run_uuid')
        d1 = ModelManager.make_response(run_uuid=run_uuid1)
        c1 = nested_to_flat(d1['outputs'])


        # results for time_steps_per_hour = 4
        response2 = self.get_response(data=fts_post_2)
        self.assertHttpCreated(response2)
        r2 = json.loads(response2.content)
        run_uuid2 = r2.get('run_uuid')
        d2 = ModelManager.make_response(run_uuid=run_uuid2)
        c2 = nested_to_flat(d2['outputs'])

        # Seems reasonable that the exact resiliency average will be different due to a great granularity of survival
        # information in a quarter-hourly simulation vs hourly.
        del c1['avoided_outage_costs_us_dollars']
        del c2['avoided_outage_costs_us_dollars']


        try:
            check_common_outputs(self, c1, c2)
            print("Test Successful!")
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid2))
            #print("Error message with ts=1: {}".format(d1['messages']))
            print("Error message with ts=4: {}") #.format(d2['messages']
            raise

