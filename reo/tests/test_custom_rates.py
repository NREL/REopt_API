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
import copy
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class ClassAttributes:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)


class TestBlendedRate(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestBlendedRate, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = {
          "Scenario": {
            "time_steps_per_hour": 1,
            "Site": {
              "longitude": -91.7337,
              "latitude": 35.2468,
              "roof_squarefeet": None,
              "land_acres": None,
              "PV": {
                "pbi_years": 1.0,
                "macrs_bonus_pct": 0.0,
                "max_kw": 200.0,
                "pbi_max_us_dollars": 1000000000.0,
                "radius": 0.0,
                "state_ibi_pct": 0.0,
                "state_rebate_us_dollars_per_kw": 0.0,
                "installed_cost_us_dollars_per_kw": 2000.0,
                "utility_ibi_max_us_dollars": 10000000000.0,
                "tilt": 10.0,
                "degradation_pct": 0.005,
                "gcr": 0.4,
                "pbi_system_max_kw": 1000000000.0,
                "utility_ibi_pct": 0.0,
                "state_ibi_max_us_dollars": 10000000000.0,
                "utility_rebate_max_us_dollars": 10000000000.0,
                "macrs_option_years": 5,
                "state_rebate_max_us_dollars": 10000000000.0,
                "dc_ac_ratio": 1.1,
                "federal_itc_pct": 0.3,
                "existing_kw": 0.0,
                "module_type": 0,
                "array_type": 1,
                "pbi_us_dollars_per_kwh": 0.0,
                "om_cost_us_dollars_per_kw": 16.0,
                "utility_rebate_us_dollars_per_kw": 0.0,
                "min_kw": 0.0,
                "losses": 0.14,
                "macrs_itc_reduction": 0.5,
                "federal_rebate_us_dollars_per_kw": 0.0,
                "inv_eff": 0.96,
                "azimuth": 180.0
              },
              "Generator": {
                "pbi_years": 0.0,
                "macrs_bonus_pct": 0.0,
                "om_cost_us_dollars_per_kwh": 0.01,
                "max_kw": 0.0,
                "pbi_max_us_dollars": 0.0,
                "state_ibi_pct": 0.0,
                "fuel_intercept_gal_per_hr": 0.0,
                "generator_only_runs_during_grid_outage": True,
                "utility_rebate_max_us_dollars": 0.0,
                "installed_cost_us_dollars_per_kw": 600.0,
                "utility_ibi_max_us_dollars": 0.0,
                "fuel_avail_gal": 1000000000.0,
                "min_turn_down_pct": 0.0,
                "pbi_system_max_kw": 0.0,
                "utility_ibi_pct": 0.0,
                "state_ibi_max_us_dollars": 0.0,
                "diesel_fuel_cost_us_dollars_per_gallon": 3.0,
                "fuel_slope_gal_per_kwh": 0.0,
                "state_rebate_us_dollars_per_kw": 0.0,
                "macrs_option_years": 0,
                "state_rebate_max_us_dollars": 0.0,
                "federal_itc_pct": 0.0,
                "pbi_us_dollars_per_kwh": 0.0,
                "existing_kw": 0.0,
                "om_cost_us_dollars_per_kw": 10.0,
                "utility_rebate_us_dollars_per_kw": 0.0,
                "min_kw": 0.0,
                "macrs_itc_reduction": 0.0,
                "federal_rebate_us_dollars_per_kw": 0.0,
                "generator_sells_energy_back_to_grid": False
              },
              "LoadProfile": {
                "critical_loads_kw_is_net": False,
                "year": 2017,
                "loads_kw_is_net": True,
                "outage_start_time_step": None,
                "outage_end_time_step": None,
                "monthly_totals_kwh": [],
                "critical_load_pct": 0.5,
                "loads_kw": [],
                "outage_is_major_event": True,
                "critical_loads_kw": [],
                "doe_reference_name": "MidriseApartment",
                "annual_kwh": 259525.0
              },
              "Storage": {
                "max_kwh": 0.0,
                "rectifier_efficiency_pct": 0.96,
                "total_itc_pct": 0.0,
                "min_kw": 0.0,
                "max_kw": 0.0,
                "replace_cost_us_dollars_per_kw": 460.0,
                "replace_cost_us_dollars_per_kwh": 230.0,
                "min_kwh": 0.0,
                "installed_cost_us_dollars_per_kw": 1000.0,
                "total_rebate_us_dollars_per_kw": 0,
                "installed_cost_us_dollars_per_kwh": 500.0,
                "inverter_efficiency_pct": 0.96,
                "battery_replacement_year": 10,
                "canGridCharge": True,
                "macrs_bonus_pct": 0.0,
                "macrs_itc_reduction": 0.5,
                "macrs_option_years": 7,
                "internal_efficiency_pct": 0.975,
                "soc_min_pct": 0.2,
                "soc_init_pct": 0.5,
                "inverter_replacement_year": 10
              },
              "ElectricTariff": {
                "add_blended_rates_to_urdb_rate": False,
                "wholesale_rate_us_dollars_per_kwh": 0.0,
                "net_metering_limit_kw": 0.0,
                "interconnection_limit_kw": 100000000.0,
                "urdb_utility_name": "",
                "urdb_label": "",
                "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0,
                "urdb_rate_name": "custom",
                "urdb_response": None,
                "blended_monthly_rates_us_dollars_per_kwh": [0.15, 0.2, 0.21, 0.23, 0.27, 0.19, 0.22, 0.17, 0.24, 0.26, 0.18, 0.2],
                "blended_monthly_demand_charges_us_dollars_per_kw": [0.08, 0.11, 0, 0, 0.15, 0.14, 0.09, 0.06, 0, 0, 0.05, 0]
              },
              "Financial": {
                "escalation_pct": 0.026,
                "offtaker_discount_pct": 0.081,
                "value_of_lost_load_us_dollars_per_kwh": 100.0,
                "analysis_years": 20,
                "microgrid_upgrade_cost_pct": 0.3,
                "offtaker_tax_pct": 0.26,
                "om_cost_escalation_pct": 0.025
              },
              "Wind": {
                "pbi_years": 1.0,
                "macrs_bonus_pct": 0.0,
                "max_kw": 0.0,
                "pbi_max_us_dollars": 1000000000.0,
                "wind_meters_per_sec": None,
                "state_ibi_pct": 0.0,
                "utility_rebate_max_us_dollars": 10000000000.0,
                "installed_cost_us_dollars_per_kw": 3013.0,
                "utility_ibi_max_us_dollars": 10000000000.0,
                "pressure_atmospheres": None,
                "pbi_system_max_kw": 1000000000.0,
                "utility_ibi_pct": 0.0,
                "state_ibi_max_us_dollars": 10000000000.0,
                "wind_direction_degrees": None,
                "state_rebate_us_dollars_per_kw": 0.0,
                "macrs_option_years": 5,
                "state_rebate_max_us_dollars": 10000000000.0,
                "federal_itc_pct": 0.3,
                "temperature_celsius": None,
                "pbi_us_dollars_per_kwh": 0.0,
                "om_cost_us_dollars_per_kw": 35.0,
                "utility_rebate_us_dollars_per_kw": 0.0,
                "min_kw": 0.0,
                "macrs_itc_reduction": 0.5,
                "federal_rebate_us_dollars_per_kw": 0.0
              }
            }
          }
        }

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        uuid = json.loads(initial_post.content)['run_uuid']
        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
        return response

    def test_blended_rate_and_pv_station(self):
        """
        Test that self.post scenario with monthly rates returns the expected LCC and PV station attributes
        """
        post = copy.deepcopy(self.post)
        response = self.get_response(post)
        pv_out = ClassAttributes(response['outputs']['Scenario']['Site']['PV'])
        financial = ClassAttributes(response['outputs']['Scenario']['Site']['Financial'])
        self.assertEqual(pv_out.station_distance_km, 0.7)  # increased accuracy with Python 3??? (was 0.0)
        self.assertEqual(pv_out.station_latitude, 35.25)
        self.assertAlmostEqual(pv_out.station_longitude, -91.74, 1)
        self.assertAlmostEqual(financial.lcc_us_dollars, 437842, -1)

    def test_time_of_export_rate(self):
        """
        add a time-of-export rate that is greater than retail rate for the month of January,
        check to make sure that PV does NOT export unless the site load is met first for the month of January.
        """
        post = copy.deepcopy(self.post)
        jan_rate = post["Scenario"]["Site"]["ElectricTariff"]["blended_monthly_rates_us_dollars_per_kwh"][0]
        post["Scenario"]["Site"]["ElectricTariff"]["wholesale_rate_us_dollars_per_kwh"] = \
            [jan_rate + 0.1] * 31 * 24 + [0.0] * (8760 - 31*24)

        post["Scenario"]["Site"]["ElectricTariff"]["blended_monthly_demand_charges_us_dollars_per_kw"] = [0]*12
        response = self.get_response(post)
        pv_out = ClassAttributes(response['outputs']['Scenario']['Site']['PV'])
        pv_to_grid = pv_out.year_one_to_grid_series_kw[:31*24]
        elec_tariff_out = ClassAttributes(response['outputs']['Scenario']['Site']['ElectricTariff'])
        grid_to_load = elec_tariff_out.year_one_to_load_series_kw[:31*24]
        self.assertTrue(all(x == 0 for i, x in enumerate(grid_to_load) if pv_to_grid[i] > 0))

    def test_time_of_use_energy_rate(self):
        """
        test custom time-of-use energy rate
        two use cases:
        1. modeling just TOU energy rate
        2. modeling TOU energy rate + URDB rate
        Setting all max Tech sizes to zero to evaluate just the ElectricTariff
        """
        post = copy.deepcopy(self.post)
        post["Scenario"]["Site"]["PV"]["max_kw"] = 0  # rest of Techs already set to zero
        post["Scenario"]["Site"]["ElectricTariff"]["urdb_label"] = "5a592c995457a3371c423a7d"
        post["Scenario"]["Site"]["LoadProfile"]["doe_reference_name"] = "FlatLoad"
        post["Scenario"]["Site"]["LoadProfile"]["annual_kwh"] = 1.0e6
        response = self.get_response(post)  # to get baseline util costs
        tariff = ClassAttributes(response['outputs']['Scenario']['Site']['ElectricTariff'])
        baseline_bill = tariff.year_one_bill_us_dollars
        # make sure we really turned off all techs:
        self.assertEqual(tariff.year_one_bill_us_dollars, tariff.year_one_bill_bau_us_dollars)

        post["Scenario"]["Site"]["ElectricTariff"]["tou_energy_rates_us_dollars_per_kwh"] = [.1] * 8760
        post["Scenario"]["Site"]["ElectricTariff"]["add_tou_energy_rates_to_urdb_rate"] = False
        response = self.get_response(post)
        tariff = ClassAttributes(response['outputs']['Scenario']['Site']['ElectricTariff'])
        self.assertAlmostEqual(tariff.year_one_bill_us_dollars, 1.0e5, places=1)
        self.assertAlmostEqual(tariff.year_one_bill_bau_us_dollars, 1.0e5, places=1)

        post["Scenario"]["Site"]["ElectricTariff"]["add_tou_energy_rates_to_urdb_rate"] = True
        response = self.get_response(post)
        tariff = ClassAttributes(response['outputs']['Scenario']['Site']['ElectricTariff'])
        self.assertAlmostEqual(tariff.year_one_bill_us_dollars, 1.0e5 + baseline_bill, places=1)
        self.assertAlmostEqual(tariff.year_one_bill_bau_us_dollars, 1.0e5 + baseline_bill, places=1)
