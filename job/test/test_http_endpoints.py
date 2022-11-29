
import json
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
import logging
import os
import requests
logging.disable(logging.CRITICAL)

class TestHTTPEndpoints(ResourceTestCaseMixin, TestCase):

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

        # Check that size_class logic is the same, but we shifted it to 1-indexed instead of 0-indexed
        # Modify input names for v2
        inputs_v2 = {
            "existing_boiler_production_type_steam_or_hw": inputs["existing_boiler_production_type"],
            "avg_boiler_fuel_load_mmbtu_per_hr": inputs["avg_boiler_fuel_load_mmbtu_per_hour"]
        }
        resp = self.api_client.get(f'/v2/chp_defaults', data=inputs_v2)
        v2_response = json.loads(resp.content)
        self.assertEqual(http_response["size_class"], v2_response["size_class"]+1)

    def test_simulated_load(self):

        # Test heating load because REopt.jl separates SpaceHeating and DHW, so had to aggregate for this endpoint
        inputs = {"load_type": "heating",
                "doe_reference_name": "Hospital",
                "latitude": 37.78,
                "longitude": -122.45
        }

        # Direct call of the http.jl endpoint /chp_defaults
        julia_host = os.environ.get('JULIA_HOST', "julia")
        response = requests.get("http://" + julia_host + ":8081/simulated_load/", json=inputs)
        http_response = response.json()

        # Call to the v2 /simulated_load to check for consistency
        resp = self.api_client.get(f'/v2/simulated_load', data=inputs)
        v2_response = json.loads(resp.content)     
        self.assertAlmostEqual(http_response["annual_mmbtu"], v2_response["annual_mmbtu"], delta=1.0)

        # Test blended/hybrid buildings
        inputs["load_type"] = "electric"
        inputs["annual_kwh"] = 1.5E7
        inputs["doe_reference_name[0]"] = "Hospital"
        inputs["doe_reference_name[1]"] = "LargeOffice"
        inputs["percent_share[0]"] = 25.0
        inputs["percent_share[1]"] = 100.0 - inputs["percent_share[0]"]
        
        # Direct call of the http.jl endpoint /chp_defaults
        julia_host = os.environ.get('JULIA_HOST', "julia")
        response = requests.get("http://" + julia_host + ":8081/simulated_load/", json=inputs)
        http_response = response.json()

        # Call to the v2 /simulated_load to check for consistency
        resp = self.api_client.get(f'/v2/simulated_load', data=inputs)
        v2_response = json.loads(resp.content)     
        self.assertAlmostEqual(http_response["annual_kwh"], v2_response["annual_kwh"], delta=1.0)        

        # Test bad and missing inputs
        inputs["invalid_key"] = "invalid_val"
        resp = self.api_client.get(f'/v2/simulated_load', data=inputs)
        v2_response = json.loads(resp.content)   
        assert("Error" in v2_response.keys())

        inputs.pop("invalid_key")
        inputs.pop("load_type")
        inputs.pop("doe_reference_name")
        resp = self.api_client.get(f'/v2/simulated_load', data=inputs)
        v2_response = json.loads(resp.content)   
        assert("Error. Missing" in v2_response.keys())

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