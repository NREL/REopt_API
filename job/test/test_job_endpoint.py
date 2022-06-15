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


class TestJobEndpoint(ResourceTestCaseMixin, TestCase):

    def test_pv_and_battery_scenario(self):
        """
        Same test as"Solar and Storage w/BAU" in the Julia package. Used in development of v2.
        No need to keep this test.
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
                "macrs_bonus_pct": 0.4,
                "installed_cost_per_kw": 2000.0,
                "tilt": 34.579,
                "degradation_pct": 0.005,
                "macrs_option_years": 5,
                "federal_itc_pct": 0.3,
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
                "macrs_bonus_pct": 0.4,
                "replace_cost_per_kw": 460.0,
                "replace_cost_per_kwh": 230.0,
                "installed_cost_per_kw": 1000.0,
                "installed_cost_per_kwh": 500.0,
                "total_itc_pct": 0.0
            },
            "ElectricTariff": {
                "urdb_label": "5ed6c1a15457a3367add15ae"
            },
            "Financial": {
                "elec_cost_escalation_pct": 0.026,
                "offtaker_discount_pct": 0.081,
                "owner_discount_pct": 0.081,
                "analysis_years": 20,
                "offtaker_tax_pct": 0.4,
                "owner_tax_pct": 0.4,
                "om_cost_escalation_pct": 0.025
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
    
class TestBoilerScenario(ResourceTestCaseMixin, TestCase):

    def test_boilers_scenario(self):

        """
        This test runs a simple test to determine if Boiler and ExistingBoiler keys are returned from the JOB API if a SpaceHeatingLoad is provided.
        It tests the API's ability to read inputs such as scalar fuel costs and process them as vectors.

        SteamTurbine key is manually removed for now. When the functionality is added to REopt it can be tested using below test case as well.

        Execution steps:
            run CLI for active Docker container
            Execeute python manage.py test job.test.test_job_endpoint.TestBoilerScenario
        """
        scenario = {
            "Site": {
            "latitude": 37.78,
            "longitude": -122.45
            },
            "ExistingBoiler": {
                "production_type": "steam",
                "efficiency": 0.8,
                "can_supply_steam_turbine": False,
                "fuel_type": "natural_gas",
                "fuel_cost_per_mmbtu": 0.5
            },
            "Boiler": {
                "min_mmbtu_per_hour": 0.0,
                "max_mmbtu_per_hour": 1.0E9,
                "efficiency": 0.8,
                "can_supply_steam_turbine": True,
                "installed_cost_per_mmbtu_per_hour": 1.0,
                "om_cost_per_mmbtu_per_hour": 0.1,
                "om_cost_per_mmbtu": 0.1,                  
                "fuel_type": "uranium",
                "fuel_cost_per_mmbtu": 10.0
            },
            "SteamTurbine": {
                "min_kw": 0.0,
                "max_kw": 20000.0,
                "is_condensing": True,
                "inlet_steam_pressure_psig": 1000.0,
                "inlet_steam_temperature_degF": '',
                "inlet_steam_superheat_degF": 10.0,
                "outlet_steam_pressure_psig": -12.7,
                "outlet_steam_min_vapor_fraction": 0.7,                         
                "isentropic_efficiency": 0.7,
                "gearbox_generator_efficiency": 0.96,
                "net_to_gross_electric_ratio": 0.98,
                "installed_cost_per_kw": 4000.0,
                "om_cost_per_kw": 80.0,
                "om_cost_per_kwh": 0.0,
                "can_net_meter": False,
                "can_wholesale": True,
                "can_export_beyond_site_load": True,
                "can_curtail": False        
            },
            "Financial": {
                "om_cost_escalation_pct": 0.025,
                "elec_cost_escalation_pct": 0.023,
                "existing_boiler_fuel_cost_escalation_pct": 0.034,
                "boiler_fuel_cost_escalation_pct": 0.034,
                "offtaker_tax_pct": 0.26,
                "offtaker_discount_pct": 0.083,
                "third_party_ownership": False,
                "owner_tax_pct": 0.26,
                "owner_discount_pct": 0.083,
                "analysis_years": 25
            },
            "ElectricLoad": {
                "doe_reference_name": "Hospital",
                "annual_kwh": 8760000.0
            },
            "SpaceHeatingLoad": {
                "doe_reference_name": "Hospital",
                "annual_mmbtu": 29897.6
            },
            "ElectricTariff": {
                "urdb_utility_name": "Pacific Gas & Electric Co",
                "urdb_rate_name": "E-20 Maximum demand of (1000 KW or more) (Secondary)",
                "urdb_label": "5e1676e95457a3f87673e3b0",
                "wholesale_rate": 0.04
            }
        }

        del scenario["SteamTurbine"]

        resp = self.api_client.post('/dev/job/', format='json', data=scenario)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')

        resp = self.api_client.get(f'/dev/job/{run_uuid}/results')
        r = json.loads(resp.content)
        results = r["outputs"]

        assert("ExistingBoiler" in results)
        assert("Boiler" in results)
        self.assertAlmostEqual(results["ExistingBoiler"]["year_one_fuel_consumption_mmbtu"], 29897, places=-3)
        self.assertAlmostEqual(results["ExistingBoiler"]["lifecycle_fuel_cost"], 160072, places=-3)
        self.assertAlmostEqual(results["ExistingBoiler"]["year_one_fuel_cost"], 14948, places=-3)
        self.assertAlmostEqual(results["Boiler"]["year_one_fuel_consumption_mmbtu"], 0.0)