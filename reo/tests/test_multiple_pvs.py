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
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class TestMultiplePV(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        """
        Testing space-constrained ground and roof mount PV systems.
        A site with 0.25 acre translates to room for 41.67 kW
        and 1,000 SF of roof translates to room for 10 kW,
            plus 5 kW of existing roof mount we should get a total of 15 kW on the roof
        (using acres_per_kw = 6e-3, kw_per_square_foot = 0.01).
        """
        super(TestMultiplePV, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = {
              "Scenario": {
                "Site": {
                  "latitude": 34.5794343,
                  "longitude": -118.11646129999997,
                  "address": "Palmdale CA",
                  "land_acres": 0.25,
                  "roof_squarefeet": 1000.0,
                  "Financial": {
                    "om_cost_escalation_pct": 0.025,
                    "escalation_pct": 0.023,
                    "offtaker_tax_pct": 0.26,
                    "offtaker_discount_pct": 0.083,
                    "analysis_years": 25,
                    "value_of_lost_load_us_dollars_per_kwh": 100.0,
                    "microgrid_upgrade_cost_pct": 0.3
                  },
                  "LoadProfile": {
                    "doe_reference_name": "RetailStore",
                    "annual_kwh": 1000000.0,
                    "year": 2017,
                    "monthly_totals_kwh": [],
                    "loads_kw": [],
                    "critical_loads_kw": [],
                    "loads_kw_is_net": True,
                    "critical_loads_kw_is_net": False,
                    "outage_start_time_step": None,
                    "outage_end_time_step": None,
                    "critical_load_pct": 0.5,
                    "outage_is_major_event": True
                  },
                  "ElectricTariff": {
                    "urdb_utility_name": "",
                    "urdb_rate_name": "",
                    "add_blended_rates_to_urdb_rate": False,
                    "blended_annual_rates_us_dollars_per_kwh": 0.3,
                    "blended_annual_demand_charges_us_dollars_per_kw": 20.0,
                    "net_metering_limit_kw": 0.0,
                    "interconnection_limit_kw": 100000000.0,
                    "urdb_response": None,
                    "urdb_label": ""
                  },
                  "Wind": {
                    "size_class": "",
                    "wind_meters_per_sec": None,
                    "wind_direction_degrees": None,
                    "temperature_celsius": None,
                    "pressure_atmospheres": None,
                    "min_kw": 0.0,
                    "max_kw": 0.0,
                    "installed_cost_us_dollars_per_kw": 3013.0,
                    "om_cost_us_dollars_per_kw": 40.0,
                    "macrs_option_years": 5,
                    "macrs_bonus_pct": 1.0,
                    "macrs_itc_reduction": 0.5,
                    "federal_itc_pct": 0.26,
                    "state_ibi_pct": 0.0,
                    "state_ibi_max_us_dollars": 10000000000.0,
                    "utility_ibi_pct": 0.0,
                    "utility_ibi_max_us_dollars": 10000000000.0,
                    "federal_rebate_us_dollars_per_kw": 0.0,
                    "state_rebate_us_dollars_per_kw": 0.0,
                    "state_rebate_max_us_dollars": 10000000000.0,
                    "utility_rebate_us_dollars_per_kw": 0.0,
                    "utility_rebate_max_us_dollars": 10000000000.0,
                    "pbi_us_dollars_per_kwh": 0.0,
                    "pbi_max_us_dollars": 1000000000.0,
                    "pbi_years": 1.0,
                    "pbi_system_max_kw": 1000000000.0
                  },
                  "PV": [
                    {
                      "pv_name": "ground",
                      "existing_kw": 5.0,
                      "min_kw": 10.0,
                      "max_kw": 10.0,
                      "installed_cost_us_dollars_per_kw": 1600.0,
                      "om_cost_us_dollars_per_kw": 16.0,
                      "macrs_option_years": 5,
                      "macrs_bonus_pct": 1.0,
                      "macrs_itc_reduction": 0.5,
                      "federal_itc_pct": 0.26,
                      "state_ibi_pct": 0.0,
                      "state_ibi_max_us_dollars": 10000000000.0,
                      "utility_ibi_pct": 0.0,
                      "utility_ibi_max_us_dollars": 10000000000.0,
                      "federal_rebate_us_dollars_per_kw": 0.0,
                      "state_rebate_us_dollars_per_kw": 0.0,
                      "state_rebate_max_us_dollars": 10000000000.0,
                      "utility_rebate_us_dollars_per_kw": 0.0,
                      "utility_rebate_max_us_dollars": 10000000000.0,
                      "pbi_us_dollars_per_kwh": 0.0,
                      "pbi_max_us_dollars": 1000000000.0,
                      "pbi_years": 1.0,
                      "pbi_system_max_kw": 1000000000.0,
                      "degradation_pct": 0.005,
                      "azimuth": 180.0,
                      "losses": 0.14,
                      "array_type": 0,
                      "module_type": 0,
                      "gcr": 0.4,
                      "dc_ac_ratio": 1.2,
                      "inv_eff": 0.96,
                      "radius": 0.0,
                      "tilt": 34.5794343,
                      "location": "ground"
                    },
                    {
                      "pv_name": "roof_west",
                      "existing_kw": 5.0,
                      "min_kw": 2.0,
                      "max_kw": 2.0,
                      "installed_cost_us_dollars_per_kw": 1600.0,
                      "om_cost_us_dollars_per_kw": 16.0,
                      "macrs_option_years": 5,
                      "macrs_bonus_pct": 1.0,
                      "macrs_itc_reduction": 0.5,
                      "federal_itc_pct": 0.26,
                      "state_ibi_pct": 0.0,
                      "state_ibi_max_us_dollars": 10000000000.0,
                      "utility_ibi_pct": 0.0,
                      "utility_ibi_max_us_dollars": 10000000000.0,
                      "federal_rebate_us_dollars_per_kw": 0.0,
                      "state_rebate_us_dollars_per_kw": 0.0,
                      "state_rebate_max_us_dollars": 10000000000.0,
                      "utility_rebate_us_dollars_per_kw": 0.0,
                      "utility_rebate_max_us_dollars": 10000000000.0,
                      "pbi_us_dollars_per_kwh": 0.0,
                      "pbi_max_us_dollars": 1000000000.0,
                      "pbi_years": 1.0,
                      "pbi_system_max_kw": 1000000000.0,
                      "degradation_pct": 0.005,
                      "azimuth": 270.0,
                      "losses": 0.14,
                      "array_type": 1,
                      "module_type": 0,
                      "gcr": 0.4,
                      "dc_ac_ratio": 1.2,
                      "inv_eff": 0.96,
                      "radius": 0.0,
                      "tilt": 10.0,
                      "location": "roof"
                    },
                    {
                      "pv_name": "roof_east",
                      "existing_kw": 0.0,
                      "min_kw": 4.0,
                      "max_kw": 4.0,
                      "installed_cost_us_dollars_per_kw": 1600.0,
                      "om_cost_us_dollars_per_kw": 16.0,
                      "macrs_option_years": 5,
                      "macrs_bonus_pct": 1.0,
                      "macrs_itc_reduction": 0.5,
                      "federal_itc_pct": 0.26,
                      "state_ibi_pct": 0.0,
                      "state_ibi_max_us_dollars": 10000000000.0,
                      "utility_ibi_pct": 0.0,
                      "utility_ibi_max_us_dollars": 10000000000.0,
                      "federal_rebate_us_dollars_per_kw": 0.0,
                      "state_rebate_us_dollars_per_kw": 0.0,
                      "state_rebate_max_us_dollars": 10000000000.0,
                      "utility_rebate_us_dollars_per_kw": 0.0,
                      "utility_rebate_max_us_dollars": 10000000000.0,
                      "pbi_us_dollars_per_kwh": 0.0,
                      "pbi_max_us_dollars": 1000000000.0,
                      "pbi_years": 1.0,
                      "pbi_system_max_kw": 1000000000.0,
                      "degradation_pct": 0.005,
                      "azimuth": 180.0,
                      "losses": 0.14,
                      "array_type": 1,
                      "module_type": 0,
                      "gcr": 0.4,
                      "dc_ac_ratio": 1.2,
                      "inv_eff": 0.96,
                      "radius": 0.0,
                      "tilt": 10.0,
                      "location": "roof"
                    }
                  ],
                  "Storage": {
                    "min_kw": 0.0,
                    "max_kw": 0.0,
                    "min_kwh": 0.0,
                    "max_kwh": 1000000.0,
                    "internal_efficiency_pct": 0.975,
                    "inverter_efficiency_pct": 0.96,
                    "rectifier_efficiency_pct": 0.96,
                    "soc_min_pct": 0.2,
                    "soc_init_pct": 0.5,
                    "canGridCharge": True,
                    "installed_cost_us_dollars_per_kw": 840.0,
                    "installed_cost_us_dollars_per_kwh": 420.0,
                    "replace_cost_us_dollars_per_kw": 410.0,
                    "replace_cost_us_dollars_per_kwh": 200.0,
                    "inverter_replacement_year": 10,
                    "battery_replacement_year": 10,
                    "macrs_option_years": 7,
                    "macrs_bonus_pct": 1.0,
                    "macrs_itc_reduction": 0.5,
                    "total_itc_pct": 0.0,
                    "total_rebate_us_dollars_per_kw": 0
                  },
                  "Generator": {
                    "existing_kw": 0.0,
                    "min_kw": 0.0,
                    "max_kw": 0.0,
                    "installed_cost_us_dollars_per_kw": 500.0,
                    "om_cost_us_dollars_per_kw": 10.0,
                    "om_cost_us_dollars_per_kwh": 0.0,
                    "diesel_fuel_cost_us_dollars_per_gallon": 3.0,
                    "fuel_slope_gal_per_kwh": 0.076,
                    "fuel_intercept_gal_per_hr": 0.0,
                    "fuel_avail_gal": 660.0,
                    "min_turn_down_pct": 0.0,
                    "generator_only_runs_during_grid_outage": True,
                    "generator_sells_energy_back_to_grid": False,
                    "macrs_option_years": 0,
                    "macrs_bonus_pct": 1.0,
                    "macrs_itc_reduction": 0.0,
                    "federal_itc_pct": 0.0,
                    "state_ibi_pct": 0.0,
                    "state_ibi_max_us_dollars": 0.0,
                    "utility_ibi_pct": 0.0,
                    "utility_ibi_max_us_dollars": 0.0,
                    "federal_rebate_us_dollars_per_kw": 0.0,
                    "state_rebate_us_dollars_per_kw": 0.0,
                    "state_rebate_max_us_dollars": 0.0,
                    "utility_rebate_us_dollars_per_kw": 0.0,
                    "utility_rebate_max_us_dollars": 0.0,
                    "pbi_us_dollars_per_kwh": 0.0,
                    "pbi_max_us_dollars": 0.0,
                    "pbi_years": 0.0,
                    "pbi_system_max_kw": 0.0
                  }
                },
                "timeout_seconds": 295,
                "user_uuid": None,
                "description": "",
                "time_steps_per_hour": 1,
                "webtool_uuid": None
              }
            }

    def test_multiple_pv(self):
        resp = self.api_client.post(self.submit_url, format='json', data=self.post)
        uuid = json.loads(resp.content)['run_uuid']
        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
        pvs = response['outputs']['Scenario']['Site']['PV']
        ground_pv = next(d for d in pvs if d["pv_name"] == "ground")
        roof_west = next(d for d in pvs if d["pv_name"] == "roof_west")
        roof_east = next(d for d in pvs if d["pv_name"] == "roof_east")

        self.assertAlmostEquals(ground_pv['size_kw'], 15, places=2)
        self.assertAlmostEquals(roof_west['size_kw'], 7, places=2)
        self.assertAlmostEquals(roof_east['size_kw'], 4, places=2)
        self.assertAlmostEquals(ground_pv['existing_pv_om_cost_us_dollars'], 782.0, places=2)
        self.assertAlmostEquals(roof_west['existing_pv_om_cost_us_dollars'], 782.0, places=2)
        self.assertAlmostEquals(roof_east['existing_pv_om_cost_us_dollars'], 0, places=2)
        self.assertAlmostEquals(ground_pv['average_yearly_energy_produced_bau_kwh'], 8719.0, places=2)
        self.assertAlmostEquals(roof_west['average_yearly_energy_produced_bau_kwh'], 7334.0, places=2)
        self.assertAlmostEquals(roof_east['average_yearly_energy_produced_bau_kwh'], 0, places=2)
        self.assertAlmostEquals(ground_pv['average_yearly_energy_produced_kwh'], 26157.0, places=2)
        self.assertAlmostEquals(roof_west['average_yearly_energy_produced_kwh'], 10268.0, places=2)
        self.assertAlmostEquals(roof_east['average_yearly_energy_produced_kwh'], 6390.0, places=2)