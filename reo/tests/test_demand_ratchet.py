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


class TestDemandRatchets(ResourceTestCaseMixin, TestCase):
    """
    Tariff from Florida Light & Power (residential) with simple tiered energy rate:
    "energyratestructure":
    [[{"max": 1000, "rate": 0.07531, "adj": 0.0119, "unit": "kWh"}, {"rate": 0.09613, "adj": 0.0119, "unit": "kWh"}]]

    Testing with "annual_kwh": 24,000 such that the "year_one_energy_charges" should be:
        12,000 kWh * (0.07531 + 0.0119) $/kWh + 12,000 kWh * (0.09613 + 0.0119) $/kWh = $ 2,342.88
    """

    def setUp(self):
        super(TestDemandRatchets, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = {
          "Scenario": {
            "webtool_uuid": None,
            "description": "",
            "timeout_seconds": 295,
            "Site": {
              "PV": {
                "pbi_years": 1.0,
                "macrs_bonus_pct": 0.0,
                "max_kw": 0.0,
                "pbi_max_us_dollars": 1000000000.0,
                "radius": 0.0,
                "state_ibi_pct": 0.0,
                "state_rebate_us_dollars_per_kw": 0.0,
                "installed_cost_us_dollars_per_kw": 2000.0,
                "utility_ibi_max_us_dollars": 10000000000.0,
                "tilt": 0.537,
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
                "max_kw": 1000000000.0,
                "pbi_max_us_dollars": 0.0,
                "state_ibi_pct": 0.0,
                "fuel_intercept_gal_per_hr": 0.0125,
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
                "fuel_slope_gal_per_kwh": 0.068,
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
                "outage_start_hour": None,
                "outage_end_hour": None,
                "monthly_totals_kwh": [],
                "critical_load_pct": 0.5,
                "loads_kw": [],
                "outage_is_major_event": True,
                "critical_loads_kw": [],
                "doe_reference_name": "MidriseApartment",
                "annual_kwh": 24000.0
              },
              "address": "",
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
              "land_acres": None,
              "ElectricTariff": {
                "add_blended_rates_to_urdb_rate": False,
                "wholesale_rate_us_dollars_per_kwh": 0.0,
                "net_metering_limit_kw": 0.0,
                "interconnection_limit_kw": 100000000.0,
                "urdb_utility_name": "Town of Wallingford, Connecticut (Utility Company)",
                "urdb_label": "",
                "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0,
                "urdb_rate_name": "Primary Service - Northford",
                "urdb_response": {"sector": "Industrial", "utility": "Town of Wallingford, Connecticut (Utility Company)", "energyratestructure": [[{"rate": 0.0687, "adj": 0.008376, "unit": "kWh"}], [{"rate": 0.0619, "adj": 0.008376, "unit": "kWh"}]], "energyweekendschedule": [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], "revisions": [1376316457, 1376316486, 1399411674, 1399585108, 1401288502, 1402428494, 1402433957, 1427405196], "flatdemandstructure": [[{"rate": 11.5}], [{"rate": 10.5}]], "startdate": 1372658400, "phasewiring": "3-Phase", "source": "http://www.town.wallingford.ct.us/images/customer-files//EDRate5110813.pdf", "label": "539f6a23ec4f024411ec8bf9", "flatdemandunit": "kW", "eiaid": 20038, "demandrateunit": "kW", "energycomments": "energy adjustments can be found here: http://www.town.wallingford.ct.us/images/customer-files//EDRate12PCAHist60514.pdf", "sourceparent": "http://www.town.wallingford.ct.us/Content/Retail_Rates_and_Fees.asp", "energyweekdayschedule": [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], "flatdemandmonths": [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1], "approved": "True", "demandratchetpercentage": [0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35], "enddate": 1383199200, "name": "Primary Service - Northford", "fixedmonthlycharge": 275, "uri": "https://openei.org/apps/USURDB/rate/view/539f6a23ec4f024411ec8bf9", "peakkwcapacitymin": 400, "demandreactivepowercharge": 2.7},
                "blended_annual_demand_charges_us_dollars_per_kw": 0.0,
                "blended_annual_rates_us_dollars_per_kwh": 0.0,
              },
              "longitude": -84.387982,
              "roof_squarefeet": None,
              "latitude": 33.748995,
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
                "size_class": "",
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
            },
            "time_steps_per_hour": 1,
            "user_uuid": None
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

    def test_demand_ratchet_rate(self):
        expected_year_one_demand_flat_cost = 721.99

        response = self.get_response(self.post)
        tariff_out = response['outputs']['Scenario']['Site']['ElectricTariff']
        messages = response['messages']

        try:
            self.assertEqual(tariff_out['year_one_demand_cost_bau_us_dollars'], expected_year_one_demand_flat_cost,
                             "Year one  demand cost ({}) does not equal expected  demand cost ({})."
                             .format(tariff_out['year_one_demand_cost_bau_us_dollars'], expected_year_one_demand_flat_cost))

        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("test_tiered_energy_rate API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e
