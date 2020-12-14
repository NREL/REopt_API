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


class TestEnergyTiers(ResourceTestCaseMixin, TestCase):
    """
    Tariff from Florida Light & Power (residential) with simple tiered energy rate:
    "energyratestructure":
    [[{"max": 1000, "rate": 0.07531, "adj": 0.0119, "unit": "kWh"}, {"rate": 0.09613, "adj": 0.0119, "unit": "kWh"}]]

    Testing with "annual_kwh": 24,000 such that the "year_one_energy_charges" should be:
        12,000 kWh * (0.07531 + 0.0119) $/kWh + 12,000 kWh * (0.09613 + 0.0119) $/kWh = $ 2,342.88
    """
    def setUp(self):
        super(TestEnergyTiers, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = {"Scenario": {"webtool_uuid": None, "description": "", "timeout_seconds": 295,
                                  "Site": {
                                      "land_acres": None,
                                      "longitude": -91.7337,
                                      "roof_squarefeet": None,
                                      "latitude": 35.2468,
                                      "address": "",
                                      "PV": {"max_kw": 0.0},
                                      "Generator": {"max_kw": 0.0},
                                      "LoadProfile": {"critical_loads_kw_is_net": False, "year": 2017, "loads_kw_is_net": True, "outage_start_hour": None, "outage_end_hour": None, "monthly_totals_kwh": [], "critical_load_pct": 0.5, "loads_kw": [], "outage_is_major_event": True, "critical_loads_kw": [], "doe_reference_name": "MidriseApartment", "annual_kwh": 24000.0},
                                      "Storage": {"max_kwh": 0.0, "max_kw": 0.0, },
                                      "ElectricTariff": {"add_blended_rates_to_urdb_rate": False, "wholesale_rate_us_dollars_per_kwh": 0.0, "net_metering_limit_kw": 0.0, "interconnection_limit_kw": 100000000.0, "urdb_utility_name": "Florida Power & Light Co.", "urdb_label": "", "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0, "urdb_rate_name": "RS-1 Residential Service", "urdb_response": {"sector": "Residential", "startdate": 1433116800, "phasewiring": "Single Phase", "name": "RS-1 Residential Service", "enddate": 1440975600, "source": "https://www.fpl.com/rates/pdf/electric-tariff-section8.pdf", "uri": "https://openei.org/apps/USURDB/rate/view/5550d6fd5457a3187e8b4567", "label": "5550d6fd5457a3187e8b4567", "utility": "Florida Power & Light Co.", "eiaid": 6452, "sourceparent": "https://www.fpl.com/rates.html", "energyratestructure": [[{"max": 1000, "rate": 0.07531, "adj": 0.0119, "unit": "kWh"}, {"rate": 0.09613, "adj": 0.0119, "unit": "kWh"}]], "energyweekdayschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "energyweekendschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "fixedmonthlycharge": 7.57, "energycomments": "Adjustment: Environmental, Storm Charge, Conservation, Capacity\\r\\nRate: Base rate and fuel", "supersedes": "53a455f05257a3ff4a8d8cf2", "revisions": [1431339677, 1431340059, 1431528978, 1431529815, 1431530443, 1448395688]}, "blended_annual_demand_charges_us_dollars_per_kw": 0.0, "blended_annual_rates_us_dollars_per_kwh": 0.0, },
                                      "Financial": {"escalation_pct": 0.026, "offtaker_discount_pct": 0.081, "value_of_lost_load_us_dollars_per_kwh": 100.0, "analysis_years": 20, "microgrid_upgrade_cost_pct": 0.3, "offtaker_tax_pct": 0.26, "om_cost_escalation_pct": 0.025},
                                      "Wind": {"max_kw": 0.0}
                                  }
                            }
                     }

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        uuid = json.loads(initial_post.content)['run_uuid']
        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
        return response

    def test_tiered_energy_rate_and_profiler(self):
        expected_year_one_energy_cost = 2342.88

        response = self.get_response(self.post)
        tariff_out = response['outputs']['Scenario']['Site']['ElectricTariff']
        profile_out = response['outputs']['Scenario']['Profile']
        messages = response['messages']

        try:
            self.assertEqual(tariff_out['year_one_energy_cost_us_dollars'], expected_year_one_energy_cost,
                             "Year one energy bill ({}) does not equal expected cost ({})."
                             .format(tariff_out['year_one_energy_cost_us_dollars'], expected_year_one_energy_cost))

            self.assertGreater(profile_out['pre_setup_scenario_seconds'], 0, "Profiling results failed")
            self.assertGreater(profile_out['setup_scenario_seconds'], 0, "Profiling results failed")
            self.assertGreater(profile_out['reopt_seconds'], 0, "Profiling results failed")
            self.assertGreater(profile_out['reopt_bau_seconds'], 0, "Profiling results failed")
            self.assertGreater(profile_out['parse_run_outputs_seconds'], 0, "Profiling results failed")

        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("test_tiered_energy_rate API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e
