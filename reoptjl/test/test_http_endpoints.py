
import json
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
import logging
import os
import requests
logging.disable(logging.CRITICAL)

class TestHTTPEndpoints(ResourceTestCaseMixin, TestCase):

    def test_chp_defaults(self):

        inputs = {"hot_water_or_steam": "hot_water",
                "avg_boiler_fuel_load_mmbtu_per_hour": 28.0
        }

        # Direct call of the http.jl endpoint /chp_defaults
        julia_host = os.environ.get('JULIA_HOST', "julia")
        response = requests.get("http://" + julia_host + ":8081/chp_defaults/", json=inputs)
        http_response = response.json()

        # Call to the django view endpoint /chp_defaults which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/chp_defaults', data=inputs)
        view_response = json.loads(resp.content)

        mismatch = []
        for k, v in http_response["default_inputs"].items():
            if v != view_response["default_inputs"][k]:
                mismatch.append(k)
        
        self.assertEqual(mismatch, [])

        # Check the endpoint logic with the expected selection
        self.assertEqual(http_response["prime_mover"], "combustion_turbine")
        self.assertEqual(http_response["size_class"], 2)
        self.assertGreater(http_response["chp_elec_size_heuristic_kw"], 3500.0)
        self.assertEqual(http_response["default_inputs"]["federal_itc_fraction"], 0.0)

        inputs = {
            "prime_mover": "micro_turbine",
            "avg_electric_load_kw": 885.0247784246575,
            "max_electric_load_kw": 1427.334,
            "is_electric_only": "true"
        }

        # Direct call of the http.jl endpoint /chp_defaults
        julia_host = os.environ.get('JULIA_HOST', "julia")
        response = requests.get("http://" + julia_host + ":8081/chp_defaults/", json=inputs)
        http_response = response.json()

        # Check the endpoint logic with the expected selection
        self.assertEqual(http_response["default_inputs"]["federal_itc_fraction"], 0.0)

        inputs = {
            "prime_mover": "combustion_turbine",
            "size_class": 4,
            "is_electric_only": "true",
            "avg_electric_load_kw": 885.0247784246575,
            "max_electric_load_kw": 1427.334
            }

        # Direct call of the http.jl endpoint /chp_defaults
        julia_host = os.environ.get('JULIA_HOST', "julia")
        response = requests.get("http://" + julia_host + ":8081/chp_defaults/", json=inputs)
        http_response = response.json()

        # Check the endpoint logic with the expected selection
        self.assertEqual(http_response["default_inputs"]["federal_itc_fraction"], 0.0)

        inputs = {
            "prime_mover": "recip_engine",
            "size_class": 4,
            "is_electric_only": "true",
            "avg_electric_load_kw": 885.0247784246575,
            "max_electric_load_kw": 1427.334
            }

        # Call to the django view endpoint /chp_defaults which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/chp_defaults', data=inputs)
        view_response = json.loads(resp.content)

        # Check the endpoint logic with the expected selection
        self.assertEqual(http_response["default_inputs"]["federal_itc_fraction"], 0.0)
    
    def test_steamturbine_defaults(self):

        inputs = {
            "prime_mover": "steam_turbine",
            "avg_boiler_fuel_load_mmbtu_per_hour": 28.0
        }

        # Direct call of the http.jl endpoint /chp_defaults
        julia_host = os.environ.get('JULIA_HOST', "julia")
        response = requests.get("http://" + julia_host + ":8081/chp_defaults/", json=inputs)
        http_response = response.json()

        # Call to the django view endpoint /chp_defaults which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/chp_defaults', data=inputs)
        view_response = json.loads(resp.content)

        mismatch = []
        for k, v in http_response["default_inputs"].items():
            if v != view_response["default_inputs"][k]:
                mismatch.append(k)
        
        self.assertEqual(mismatch, [])

        # Check the endpoint logic with the expected selection
        self.assertEqual(http_response["prime_mover"], "steam_turbine")
        self.assertEqual(http_response["size_class"], 1)
        self.assertGreater(http_response["chp_elec_size_heuristic_kw"], 574.419)

    def test_absorption_chiller_defaults(self):

        inputs = {"thermal_consumption_hot_water_or_steam": "hot_water",
                "load_max_tons": 50
        }

        # Direct call of the http.jl endpoint /absorption_chiller_defaults
        julia_host = os.environ.get('JULIA_HOST', "julia")
        response = requests.get("http://" + julia_host + ":8081/absorption_chiller_defaults/", json=inputs)
        http_response = response.json()

        # Call to the django view endpoint /absorption_chiller_defaults which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/absorption_chiller_defaults', data=inputs)
        view_response = json.loads(resp.content)

        mismatch = []
        for k, v in http_response["default_inputs"].items():
            if v != view_response["default_inputs"][k]:
                mismatch.append(k)
        
        self.assertEqual(mismatch, [])

        # Check the endpoint logic with the expected selection
        self.assertEqual(http_response["thermal_consumption_hot_water_or_steam"], "hot_water")
        self.assertEqual(http_response["default_inputs"]["om_cost_per_ton"], 80.0)
        self.assertEqual(http_response["default_inputs"]["installed_cost_per_ton"], 3066.0)
        self.assertEqual(http_response["default_inputs"]["cop_thermal"], 0.74)
        self.assertNotIn("thermal_consumption_hot_water_or_steam", http_response["default_inputs"].keys())
    
    def test_simulated_load(self):

        # Test heating load because REopt.jl separates SpaceHeating and DHW, so had to aggregate for this endpoint
        inputs = {"load_type": "heating",
                "doe_reference_name": "Hospital",
                "latitude": 36.12,
                "longitude": -115.5
        }

        # The /v3/simulated_load endpoint calls the http.jl /simulated_load endpoint
        response = self.api_client.get(f'/v3/simulated_load', data=inputs)
        http_response = json.loads(response.content)

        # Call to the v2 /simulated_load to check for consistency
        resp = self.api_client.get(f'/v2/simulated_load', data=inputs)
        v2_response = json.loads(resp.content)     
        self.assertAlmostEqual(http_response["annual_mmbtu"], v2_response["annual_mmbtu"], delta=1.0)

        # Test blended/hybrid buildings
        inputs["load_type"] = "electric"
        inputs["annual_kwh"] = 1.5E7
        inputs["doe_reference_name[0]"] = "Hospital"
        inputs["doe_reference_name[1]"] = "LargeOffice"
        inputs["percent_share[0]"] = 0.25
        inputs["percent_share[1]"] = 1.0 - inputs["percent_share[0]"]
        
        # The /v3/simulated_load endpoint calls the http.jl /simulated_load endpoint
        response = self.api_client.get(f'/v3/simulated_load', data=inputs)
        http_response = json.loads(response.content)

        # Call to the v2 /simulated_load to check for consistency
        resp = self.api_client.get(f'/v2/simulated_load', data=inputs)
        v2_response = json.loads(resp.content)     
        self.assertAlmostEqual(http_response["annual_kwh"], v2_response["annual_kwh"], delta=1.0)        

        # Test bad inputs
        inputs["invalid_key"] = "invalid_val"
        resp = self.api_client.get(f'/v2/simulated_load', data=inputs)
        v2_response = json.loads(resp.content)   
        assert("Error" in v2_response.keys())

    def test_avert_emissions_profile_endpoint(self):
        # Call to the django view endpoint dev/avert_emissions_profile which calls the http.jl endpoint
        #case 1: location in CONUS (Seattle, WA)
        inputs = {
            "latitude": 47.606211,
            "longitude": -122.336052,
            "load_year": 2021
        }
        resp = self.api_client.get(f'/v3/avert_emissions_profile', data=inputs)
        self.assertHttpOK(resp)
        view_response = json.loads(resp.content)
        self.assertEquals(view_response["avert_meters_to_region"], 0.0)
        self.assertEquals(view_response["avert_region"], "Northwest")
        self.assertEquals(len(view_response["emissions_factor_series_lb_NOx_per_kwh"]), 8760)
        #case 2: location off shore of NJ (works for AVERT, not Cambium)
        inputs = {
            "latitude": 39.034417, 
            "longitude": -74.759292,
            "load_year": 2021
        }
        resp = self.api_client.get(f'/v3/avert_emissions_profile', data=inputs)
        self.assertHttpOK(resp)
        view_response = json.loads(resp.content)
        self.assertAlmostEqual(view_response["avert_meters_to_region"], 760.62, delta=1.0)
        self.assertEquals(view_response["avert_region"], "Mid-Atlantic")
        self.assertEquals(len(view_response["emissions_factor_series_lb_NOx_per_kwh"]), 8760)
        #case 3: Honolulu, HI (works for AVERT but not Cambium)
        inputs = {
            "latitude": 21.3099, 
            "longitude": -157.8581,
            "load_year": 2021
        }
        resp = self.api_client.get(f'/v3/avert_emissions_profile', data=inputs)
        self.assertHttpOK(resp)
        view_response = json.loads(resp.content)
        self.assertEquals(view_response["avert_meters_to_region"], 0.0)
        self.assertEquals(view_response["avert_region"], "Hawaii (Oahu)")
        self.assertEquals(len(view_response["emissions_factor_series_lb_NOx_per_kwh"]), 8760)
        #case 4: location well outside of US (does not work)
        inputs = {
            "latitude": 0.0,
            "longitude": 0.0,
            "load_year": 2022
        }
        resp = self.api_client.get(f'/v3/avert_emissions_profile', data=inputs)
        self.assertHttpBadRequest(resp)
        view_response = json.loads(resp.content)
        self.assertTrue("error" in view_response)
        

    def test_cambium_profile_endpoint(self):
        # Call to the django view endpoint v3/cambium_profile which calls the http.jl endpoint
        #case 1: location in CONUS (Seattle, WA)
        inputs = {
            "load_year": 2021,
            "scenario": "Mid-case",
            "location_type": "GEA Regions 2023", 
            "latitude": 47.606211, # Seattle 
            "longitude": -122.336052, # Seattle 
            "start_year": 2024,
            "lifetime": 25,
            "metric_col": "lrmer_co2e",
            "grid_level": "enduse"
        }
        resp = self.api_client.get(f'/v3/cambium_profile', data=inputs) 
        self.assertHttpOK(resp)
        view_response = json.loads(resp.content)
        self.assertEquals(view_response["metric_col"], "lrmer_co2e")
        self.assertEquals(view_response["location"], "Northern Grid West") 
        self.assertEquals(len(view_response["data_series"]), 8760)
        #case 2: location off shore of NJ (works for AVERT, not Cambium)
        inputs["latitude"] = 39.034417
        inputs["longitude"] = -74.759292
        resp = self.api_client.get(f'/v3/cambium_profile', data=inputs) 
        self.assertHttpBadRequest(resp)
        view_response = json.loads(resp.content)
        self.assertTrue("error" in view_response)
        #case 3: Honolulu, HI (works for AVERT but not Cambium)
        inputs["latitude"] = 21.3099
        inputs["longitude"] = -157.8581
        resp = self.api_client.get(f'/v3/cambium_profile', data=inputs)
        self.assertHttpBadRequest(resp) 
        view_response = json.loads(resp.content)
        self.assertTrue("error" in view_response)
        #case 4: location well outside of US (does not work)
        inputs["latitude"] = 0.0
        inputs["longitude"] = 0.0
        resp = self.api_client.get(f'/v3/cambium_profile', data=inputs)
        self.assertHttpBadRequest(resp) 
        view_response = json.loads(resp.content)
        self.assertTrue("error" in view_response)

    def test_easiur_endpoint(self):
        # Call to the django view endpoint dev/easiur_costs which calls the http.jl endpoint
        inputs = {
            "latitude": 47.606211,
            "longitude": -122.336052,
            "inflation": 0.025
        }
        resp = self.api_client.get(f'/v3/easiur_costs', data=inputs)
        self.assertHttpOK(resp)
        view_response = json.loads(resp.content)
        for ekey in ["NOx", "SO2", "PM25"]:
            for key_format in ["{}_grid_cost_per_tonne", "{}_onsite_fuelburn_cost_per_tonne", "{}_cost_escalation_rate_fraction"]:
                self.assertTrue(type(view_response[key_format.format(ekey)]) == float)
        inputs = {
            "latitude": 47.606211,
            "longitude": 122.336052,
            "inflation": 0.025
        }
        resp = self.api_client.get(f'/v3/easiur_costs', data=inputs)
        self.assertHttpBadRequest(resp)
        view_response = json.loads(resp.content)
        self.assertTrue("error" in view_response)

    def test_ghp_endpoints(self):
        # Test /ghp_efficiency_thermal_factors
        inputs_dict = {"latitude": 37.78,
                        "longitude": -122.45,
                        "doe_reference_name": "MediumOffice"}

        # Call to the django view endpoint /ghp_efficiency_thermal_factors which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/ghp_efficiency_thermal_factors', data=inputs_dict)
        view_response = json.loads(resp.content)

        self.assertEqual(view_response["cooling_efficiency_thermal_factor"], 0.43)
        self.assertEqual(view_response["space_heating_efficiency_thermal_factor"], 0.46)

        # Test /ghpghx/ground_conductivity
        inputs_dict = {"latitude": 37.78,
                        "longitude": -122.45}

        # Call to the django view endpoint /ghpghx/ground_conductivity which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/ghpghx/ground_conductivity', data=inputs_dict)
        view_response = json.loads(resp.content)

        self.assertEqual(view_response["thermal_conductivity"], 1.117)

    def test_default_existing_chiller_cop(self):
        # Test 1: full dictionary
        inputs_dict = {
            "existing_chiller_max_thermal_factor_on_peak_load":1.25,
            "max_load_kw": 50,
            "max_load_ton":10
        }

        # Call to the django view endpoint /get_existing_chiller_default_cop which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/get_existing_chiller_default_cop', data=inputs_dict)
        view_response = json.loads(resp.content)

        self.assertEqual(view_response["existing_chiller_cop"], 4.4)

        # Test 2: empty dictionary, which should return unknown value
        inputs_dict = {}

        # Call to the django view endpoint /get_existing_chiller_default_cop which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/get_existing_chiller_default_cop', data=inputs_dict)
        view_response = json.loads(resp.content)

        self.assertEqual(view_response["existing_chiller_cop"], 4.545)

        # Test 3: Check that "existing_chiller_max_thermal_factor_on_peak_load" can influence the COP; accept max_load_ton empty string
        inputs_dict = {
            "existing_chiller_max_thermal_factor_on_peak_load":1000,
            "max_load_kw": 5,
            "max_load_ton":""
        }

        # Call to the django view endpoint /get_existing_chiller_default_cop which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/get_existing_chiller_default_cop', data=inputs_dict)
        view_response = json.loads(resp.content)

        self.assertEqual(view_response["existing_chiller_cop"], 4.69)

        # Test 4: max_load_ton empty string 
        inputs_dict = {
            "max_load_ton":90,
            "max_load_kw":""
        }

        # Call to the django view endpoint /get_existing_chiller_default_cop which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/get_existing_chiller_default_cop', data=inputs_dict)
        view_response = json.loads(resp.content)

        self.assertEqual(view_response["existing_chiller_cop"], 4.69)

        #Test 5: max_load_kw only, small value yields low COP
        inputs_dict = {
            "max_load_kw":1
        }

        # Call to the django view endpoint /get_existing_chiller_default_cop which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/get_existing_chiller_default_cop', data=inputs_dict)
        view_response = json.loads(resp.content)

        self.assertEqual(view_response["existing_chiller_cop"], 4.4)

    def test_get_ashp_defaults(self):
        inputs_dict = {
            "load_served": "SpaceHeating",
            "force_into_system": "true"
        }

        # Call to the django view endpoint /get_existing_chiller_default_cop which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/get_ashp_defaults', data=inputs_dict)
        view_response = json.loads(resp.content)

        self.assertEqual(view_response["installed_cost_per_ton"], 2250)
        self.assertEqual(view_response["om_cost_per_ton"], 0.0)
        self.assertEqual(view_response["sizing_factor"], 1.1)

        inputs_dict = {
            "load_served": "DomesticHotWater",
            "force_into_system": "false"
        }

        # Call to the django view endpoint /get_existing_chiller_default_cop which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/get_ashp_defaults', data=inputs_dict)
        view_response = json.loads(resp.content)

        self.assertNotIn("cooling_cf_reference", view_response.keys())
        self.assertEqual(view_response["sizing_factor"], 1.0)

    def test_pv_cost_defaults(self):
        inputs_dict = {
            "electric_load_annual_kwh": 2000000.0,
            "array_type": 1,
            "site_roof_squarefeet": 50000
        }

        # Call to the django view endpoint /get_existing_chiller_default_cop which calls the http.jl endpoint
        resp = self.api_client.get(f'/v3/pv_cost_defaults', data=inputs_dict)
        view_response = json.loads(resp.content)

        self.assertEqual(view_response["size_class"], 3)   


