# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
import json
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
import logging
logging.disable(logging.CRITICAL)
import os


class TestJobEndpoint(ResourceTestCaseMixin, TestCase):

    def test_pv_battery_and_emissions_defaults_from_julia(self):
        """
        Same test post as"Solar and Storage w/BAU" in the Julia package. Used in development of v3.
        Also tests that inputs with defaults determined in the REopt julia package get updated in the database.
        """
        scenario = {
            "Site": {
                "longitude": -118.1164613,
                "latitude": 34.5794343,
                "roof_squarefeet": 5000.0,
                "land_acres": 1.0,
                "node": 3
            },
            "PV": {
                "macrs_bonus_fraction": 0.4,
                "installed_cost_per_kw": 2000.0,
                "tilt": 34.579,
                "degradation_fraction": 0.005,
                "macrs_option_years": 5,
                "federal_itc_fraction": 0.3,
                "module_type": 0,
                "array_type": 1,
                "om_cost_per_kw": 16.0,
                "macrs_itc_reduction": 0.5,
                "azimuth": 180.0,
                "federal_rebate_per_kw": 350.0
            },
            "ElectricLoad": {
                "doe_reference_name": "RetailStore",
                "annual_kwh": 10000000.0,
                "year": 2017
            },
            "ElectricStorage": {
                "total_rebate_per_kw": 100.0,
                "macrs_option_years": 5,
                "can_grid_charge": True,
                "macrs_bonus_fraction": 0.4,
                "replace_cost_per_kw": 460.0,
                "replace_cost_per_kwh": 230.0,
                "installed_cost_per_kw": 1000.0,
                "installed_cost_per_kwh": 500.0,
                "total_itc_fraction": 0.0
            },
            "ElectricTariff": {
                "urdb_label": "5ed6c1a15457a3367add15ae"
            },
            "ElectricUtility": {
                "emissions_factor_series_lb_NOx_per_kwh": 1
            },
            "Financial": {
                "elec_cost_escalation_rate_fraction": 0.026,
                "offtaker_discount_rate_fraction": 0.081,
                "owner_discount_rate_fraction": 0.081,
                "analysis_years": 20,
                "offtaker_tax_rate_fraction": 0.4,
                "owner_tax_rate_fraction": 0.4,
                "om_cost_escalation_rate_fraction": 0.025
            }
        }

        resp = self.api_client.post('/dev/job/', format='json', data=scenario)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')

        resp = self.api_client.get(f'/dev/job/{run_uuid}/results')
        r = json.loads(resp.content)
        results = r["outputs"]

        self.assertAlmostEqual(results["Financial"]["lcc"], 1.240037e7, places=-3)
        self.assertAlmostEqual(results["Financial"]["lcc_bau"], 12766397, places=-3)
        self.assertAlmostEqual(results["PV"]["size_kw"], 216.667, places=1)
        self.assertAlmostEqual(results["ElectricStorage"]["size_kw"], 55.9, places=1)
        self.assertAlmostEqual(results["ElectricStorage"]["size_kwh"], 78.9, places=1)
        self.assertIsNotNone(results["Site"]["total_renewable_energy_fraction"])
        self.assertIsNotNone(results["Site"]["year_one_emissions_tonnes_CO2"])
        self.assertIsNotNone(results["Site"]["lifecycle_emissions_tonnes_NOx"])

        #test that emissions inputs got updated in the database with the defaults determined in REopt julia package
        updated_inputs = r["inputs"]
        self.assertIsNotNone(updated_inputs["ElectricUtility"]["emissions_factor_series_lb_CO2_per_kwh"])
        self.assertIsNotNone(updated_inputs["Financial"]["NOx_grid_cost_per_tonne"])
        self.assertIsNotNone(updated_inputs["Financial"]["SO2_onsite_fuelburn_cost_per_tonne"])
        self.assertIsNotNone(updated_inputs["Financial"]["PM25_cost_escalation_rate_fraction"])

    def test_off_grid_defaults(self):
        """
        Purpose of this test is to validate off-grid functionality and defaults in the API.
        """
        scenario = {
            "Settings":{
                "off_grid_flag": True,
                "optimality_tolerance":0.05
            },
            "Site": {
                "longitude": -118.1164613,
                "latitude": 34.5794343
            },
            "PV": {},
            "ElectricStorage":{},
            "ElectricLoad": {
                "doe_reference_name": "FlatLoad",
                "annual_kwh": 8760.0,
                "city": "LosAngeles",
                "year": 2017
            }
        }

        resp = self.api_client.post('/dev/job/', format='json', data=scenario)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')

        resp = self.api_client.get(f'/dev/job/{run_uuid}/results')
        r = json.loads(resp.content)
        results = r["outputs"]

        # Validate that we got off-grid response fields
        self.assertAlmostEqual(results["Financial"]["offgrid_microgrid_lcoe_dollars_per_kwh"], 0.337, places=-3)
        self.assertAlmostEqual(results["ElectricTariff"]["year_one_bill_before_tax"], 0.0)
        self.assertAlmostEqual(results["ElectricLoad"]["offgrid_load_met_fraction"], 0.99999, places=-2)
        self.assertAlmostEqual(sum(results["ElectricLoad"]["offgrid_load_met_series_kw"]), 8760.0, places=-1)
        self.assertAlmostEqual(results["Financial"]["lifecycle_offgrid_other_annual_costs_after_tax"], 0.0, places=-2)

    def test_cooling_possible_sets_and_results(self):
        """
        Purpose of this test is to test the validity of Cooling Load possible_sets, in particular []/null and blend/hybrid
        """
        scenario = {
            "Settings": {"run_bau": False},
            "Site": {"longitude": -118.1164613, "latitude": 34.5794343},
            "ElectricTariff": {"urdb_label": "5ed6c1a15457a3367add15ae"},
            "PV": {"max_kw": 0.0},
            "ElectricStorage":{"max_kw": 0.0, "max_kwh": 0.0},
            "ElectricLoad": {
                "blended_doe_reference_names": ["Hospital", "LargeOffice"],
                "blended_doe_reference_percents": [0.75, 0.25],              
                "annual_kwh": 876000.0
            },
            "CoolingLoad": {
                "doe_reference_name": "Hospital",
                "annual_tonhour": 5000.0
            },
            "SpaceHeatingLoad": {
                "doe_reference_name": "Hospital",
                "annual_mmbtu": 500.0
            },
            "ExistingBoiler": {
                "efficiency": 0.72,
                "production_type": "steam",
                "fuel_cost_per_mmbtu": 10
            },
            "ExistingChiller": {
                "cop": 3.4,
                "max_thermal_factor_on_peak_load": 1.25
            },
            "CHP": {
                "prime_mover": "recip_engine",
                "fuel_cost_per_mmbtu": 10,
                "min_kw": 100,
                "max_kw": 100,
                "electric_efficiency_full_load": 0.35,
                "electric_efficiency_half_load": 0.35,
                "min_turn_down_fraction": 0.1,
                "thermal_efficiency_full_load": 0.45,
                "thermal_efficiency_half_load": 0.45
            }
        }

        resp = self.api_client.post('/dev/job/', format='json', data=scenario)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        
        resp = self.api_client.get(f'/dev/job/{run_uuid}/results')
        r = json.loads(resp.content)
        inputs = r["inputs"]
        results = r["outputs"]
        self.assertIn("CoolingLoad", list(inputs.keys()))
        self.assertIn("CoolingLoad", list(results.keys()))
        self.assertIn("CHP", list(results.keys()))
        self.assertIn("ExistingChiller",list(results.keys()))
        self.assertIn("ExistingBoiler", list(results.keys()))
        self.assertIn("HeatingLoad", list(results.keys()))


    def test_chp_defaults_from_julia(self):
        # Test that the inputs_with_defaults_set_in_julia feature worked for CHP, consistent with /chp_defaults
        post_file = os.path.join('job', 'test', 'posts', 'chp_defaults_post.json')
        post = json.load(open(post_file, 'r'))
        # Make average MMBtu/hr thermal steam greater than 7 MMBtu/hr threshold for combustion_turbine to be chosen
        # Default ExistingBoiler efficiency for production_type = steam is 0.75
        post["SpaceHeatingLoad"]["annual_mmbtu"] = 8760 * 8 / 0.75
        post["DomesticHotWaterLoad"]["annual_mmbtu"] = 8760 * 8 / 0.75
        resp = self.api_client.post('/dev/job/', format='json', data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')

        resp = self.api_client.get(f'/dev/job/{run_uuid}/results')
        r = json.loads(resp.content)
        inputs_chp = r["inputs"]["CHP"]

        avg_fuel_load = (post["SpaceHeatingLoad"]["annual_mmbtu"] + 
                            post["DomesticHotWaterLoad"]["annual_mmbtu"]) / 8760.0
        inputs_chp_defaults = {"existing_boiler_production_type": post["ExistingBoiler"]["production_type"],
                            "avg_boiler_fuel_load_mmbtu_per_hour": avg_fuel_load
            }

        # Call to the django view endpoint /chp_defaults which calls the http.jl endpoint
        resp = self.api_client.get(f'/dev/chp_defaults', data=inputs_chp_defaults)
        view_response = json.loads(resp.content)

        for key in view_response["default_inputs"].keys():
            if post["CHP"].get(key) is None: # Check that default got assigned consistent with /chp_defaults
                self.assertEquals(inputs_chp[key], view_response["default_inputs"][key])
            else:  # Make sure we didn't overwrite user-input
                self.assertEquals(inputs_chp[key], post["CHP"][key])

