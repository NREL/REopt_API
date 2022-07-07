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
import os
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat
from django.test import TestCase
from reo.models import ModelManager
from reo.utilities import check_common_outputs, annuity


class CriticalLoadBAUTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(CriticalLoadBAUTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_critical_load_bau_can_sustain_part_outage(self):
        """
        Test scenario with
        - outage_start_time_step: 5196
        - outage_end_time_step: 5244
        - existing diesel generator 2001 kW
        - available fuel 1000000000 gallons
        """
        test_post = os.path.join('reo', 'tests', 'posts', 'critical_load_bau_can_sustain_part_outage.json')
        nested_data = json.load(open(test_post, 'rb'))

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])
        c['resilience_check_flag'] = d['outputs']['Scenario']['Site']['LoadProfile']['resilience_check_flag']
        c['bau_sustained_time_steps'] = d['outputs']['Scenario']['Site']['LoadProfile']['bau_sustained_time_steps']
        c["fuel_used_gal_bau"] = round(d['outputs']['Scenario']['Site']['Generator']['fuel_used_gal_bau'])

        d_expected = dict()
        d_expected['status'] = 'optimal'
        energy_rate = nested_data['Scenario']['Site']['ElectricTariff']["blended_annual_rates_us_dollars_per_kwh"]
        flat_load = nested_data['Scenario']['Site']['LoadProfile']["annual_kwh"] / 8760
        outage_duration = (1 + nested_data['Scenario']['Site']['LoadProfile']["outage_end_time_step"] - nested_data['Scenario']['Site']['LoadProfile']["outage_start_time_step"])
        d_expected['year_one_energy_cost_bau'] = energy_rate * flat_load * (8760 - outage_duration)
        d_expected['resilience_check_flag'] = False
        d_expected['bau_sustained_time_steps'] = int(nested_data['Scenario']['Site']['Generator']["fuel_avail_gal"] / (nested_data['Scenario']['Site']['Generator']["fuel_slope_gal_per_kwh"] * flat_load * nested_data['Scenario']['Site']['LoadProfile']["critical_load_pct"]))
        d_expected["fuel_used_gal_bau"] = d_expected['bau_sustained_time_steps'] * (nested_data['Scenario']['Site']['Generator']["fuel_slope_gal_per_kwh"] * flat_load * nested_data['Scenario']['Site']['LoadProfile']["critical_load_pct"])
        analysis_years = nested_data['Scenario']['Site']['Financial']["analysis_years"]
        escalation_pct = nested_data['Scenario']['Site']['Financial']["escalation_pct"]
        offtaker_discount_pct = nested_data['Scenario']['Site']['Financial']["offtaker_discount_pct"]
        tax_fraction = 1 - nested_data['Scenario']['Site']['Financial']["offtaker_tax_pct"]

        pwf_e = annuity(analysis_years, escalation_pct, offtaker_discount_pct)
        bau_energy_cost = d['outputs']['Scenario']['Site']['ElectricTariff']["total_energy_cost_bau_us_dollars"]
        d_expected["total_energy_cost_bau"] = round(pwf_e * flat_load * energy_rate * (8760 - outage_duration) * tax_fraction)

        bau_fixed_om_cost = d['outputs']['Scenario']['Site']['Generator']["existing_gen_total_fixed_om_cost_us_dollars"]
        bau_var_om_cost = d['outputs']['Scenario']['Site']['Generator']["existing_gen_total_variable_om_cost_us_dollars"]
        
        bau_fuel_used = d['outputs']['Scenario']['Site']['Generator']["fuel_used_gal_bau"]
        pwf_gen_fuel = annuity(analysis_years, nested_data['Scenario']['Site']['Generator']["generator_fuel_escalation_pct"], offtaker_discount_pct)
        bau_fuel_cost = tax_fraction*bau_fuel_used*nested_data['Scenario']['Site']['Generator']["diesel_fuel_cost_us_dollars_per_gallon"]*pwf_gen_fuel
        d_expected['lcc_bau'] = round(bau_energy_cost + bau_fixed_om_cost + bau_var_om_cost + bau_fuel_cost)
        
        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed.".format(run_uuid))
            print("Error message: {}".format(d['messages']['errors']))
            raise

    def test_critical_load_bau_can_sustain_outage(self):
        """
        Test scenario with
        - outage_start_time_step: 17
        - outage_end_time_step: 21
        - existing diesel generator 20 kW
        - existing PV 3 kW
        - available fuel 50 gallons
        """
        test_post = os.path.join('reo', 'tests', 'posts', 'critical_load_bau_can_sustain_outage.json')
        nested_data = json.load(open(test_post, 'rb'))

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])
        load_bau = d['outputs']['Scenario']['Site']['LoadProfile']['year_one_electric_load_series_kw']

        # check first 100 hours
        c['load_bau'] = load_bau[:100]
        c['status'] = d['outputs']['Scenario']['status']
        c['resilience_check_flag'] = d['outputs']['Scenario']['Site']['LoadProfile']['resilience_check_flag']
        c['bau_sustained_time_steps'] = d['outputs']['Scenario']['Site']['LoadProfile']['bau_sustained_time_steps']

        load_bau_expected = [19.5635, 18.9651, 20.3557, 19.0925, 20.2735, 19.0383, 20.3317, 13.6065, 9.20435, 7.3294,
                             7.14286, 5.62887, 5.20491, 4.40816, 4.21774, 4.21774, 2.13005, 6.20206, 8.43682, 8.63245,
                             17.7916, 17.9585, 18.6981, 18.7381, 19.5483, 19.2944, 20.0656, 19.5757, 20.2466, 19.8914,
                             24.4053, 32.5911, 39.7653, 47.1892, 47.1892, 47.1892, 42.9714, 47.1892, 47.1892, 47.1892,
                             47.1892, 21.2452, 16.5046, 17.0414, 17.6651, 17.7595, 18.298, 18.2451, 18.8185, 18.7475,
                             19.4191, 19.1492, 19.881, 19.5412, 24.4053, 32.5911, 39.7653, 47.1892, 47.1892, 47.1892,
                             42.9714, 47.1892, 47.1892, 47.1892, 47.1892, 21.4645, 16.1414, 16.5509, 16.7304, 17.308,
                             17.3808, 17.858, 17.8368, 18.1468, 17.8958, 18.1091, 17.7883, 18.1495, 24.4053, 32.5911,
                             39.7653, 47.1892, 47.1892, 47.1892, 42.9714, 47.1892, 47.1892, 47.1892, 47.1892, 20.9702,
                             15.1757, 15.3862, 15.8559, 15.9813, 16.7046, 16.5464, 17.2186, 16.8851, 17.7358, 17.2112]

        d_expected = dict()
        d_expected['load_bau'] = load_bau_expected
        d_expected['status'] = 'optimal'
        d_expected['total_energy_cost_bau'] = 53967.58
        d_expected['year_one_energy_cost_bau'] = 7434.65
        d_expected['resilience_check_flag'] = True
        d_expected['bau_sustained_time_steps'] = 5

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed.".format(run_uuid))
            print("Error message: {}".format(d['messages']['errors']))
            raise
