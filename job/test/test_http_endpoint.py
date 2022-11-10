
import json
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
import logging
import os
import requests
logging.disable(logging.CRITICAL)

class TestHTTPEndpoints(ResourceTestCaseMixin, TestCase):

    @skip("TestHTTPEndpoings until we merge simulated-load into master")
    def test_chp_defaults(self):

        inputs = {"existing_boiler_production_type": "hot_water",
                "avg_boiler_fuel_load_mmbtu_per_hour": 28.0
        }

        # Direct call of the http.jl endpoint /chp_defaults
        julia_host = os.environ.get('JULIA_HOST', "julia")
        response = requests.get("http://" + julia_host + ":8081/chp_defaults/", json=inputs)
        http_response = response.json()

        # Call to the django view endpoint /chp_defaults which calls the http.jl endpoint
        resp = self.api_client.get(f'/dev/chp_defaults', data=inputs)
        view_response = json.loads(resp.content)

        mismatch = []
        for k, v in http_response["default_inputs"].items():
            if v != view_response["default_inputs"][k]:
                mismatch.append(k)
        
        self.assertEqual(mismatch, [])

        # Check the endpoint logic with the expected selection
        self.assertEqual(http_response["prime_mover"], "combustion_turbine")
        self.assertEqual(http_response["size_class"], 4)
        self.assertGreater(http_response["chp_size_based_on_avg_heating_load_kw"], 3500.0)


    def test_simulated_load(self):

        inputs = {"existing_boiler_production_type": "hot_water",
                "avg_boiler_fuel_load_mmbtu_per_hour": 28.0
        }

        # Direct call of the http.jl endpoint /chp_defaults
        julia_host = os.environ.get('JULIA_HOST', "julia")
        response = requests.get("http://" + julia_host + ":8081/chp_defaults/", json=inputs)
        http_response = response.json()

        # Call to the django view endpoint /chp_defaults which calls the http.jl endpoint
        resp = self.api_client.get(f'/dev/chp_defaults', data=inputs)
        view_response = json.loads(resp.content)

        mismatch = []
        for k, v in http_response["default_inputs"].items():
            if v != view_response["default_inputs"][k]:
                mismatch.append(k)
        
        self.assertEqual(mismatch, [])        

        # Check the endpoint logic with the expected selection
        self.assertEqual(http_response["prime_mover"], "combustion_turbine")
        self.assertEqual(http_response["size_class"], 4)
        self.assertGreater(http_response["chp_size_based_on_avg_heating_load_kw"], 3500.0)

        


# For POSTing to an endpoint which returns a `run_uuid` to later GET the results from the database
# resp = self.api_client.post('/dev/job/', format='json', data=scenario))
# self.assertHttpCreated(resp)
# r = json.loads(resp.content)
# run_uuid = r.get('run_uuid')

# This method is used for calling a REopt_API endpoint (/ghpghx) from within the scenario.py celery task
# client = TestApiClient()
# ghpghx_results_url = "/v1/ghpghx/"+ghpghx_uuid_list[i]+"/results/"
# ghpghx_results_resp = client.get(ghpghx_results_url)  # same as doing ghpModelManager.make_response(ghp_uuid)
# ghpghx_results_resp_dict = json.loads(ghpghx_results_resp.content)