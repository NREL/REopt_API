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
import numpy as np
from reo.utilities import annuity
import os


class TestSIADScenarios(ResourceTestCaseMixin, TestCase):
    
    def setUp(self):
        super(TestSIADScenarios, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post_BAU = json.load(open(os.path.join('reo', 'tests', 'posts', 'SIAD_post_BAU.json'),'rb'))
        self.post_no_PV_no_ITC = json.load(open(os.path.join('reo', 'tests', 'posts', 'SIAD_post_no_PV_no_ITC.json'),'rb'))
        self.post_no_PV_with_ITC = json.load(open(os.path.join('reo', 'tests', 'posts', 'SIAD_post_no_PV_with_ITC.json'),'rb'))
        self.post_with_PV_no_ITC = json.load(open(os.path.join('reo', 'tests', 'posts', 'SIAD_post_with_PV_no_ITC.json'),'rb'))
        self.post_with_PV_with_ITC = json.load(open(os.path.join('reo', 'tests', 'posts', 'SIAD_post_with_PV_with_ITC.json'),'rb'))

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        postjsoncontent = json.loads(initial_post.content)
        uuid = json.loads(initial_post.content)['run_uuid']
        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
        return response

    def test_run_scenarios(self):
        results_dir = 'results'
        run_BAU = False
        if run_BAU:
            post = self.post_BAU
            post["Scenario"]["Site"]["LoadProfile"]["outage_start_hour"] = 0
            post["Scenario"]["Site"]["LoadProfile"]["outage_end_hour"] = 1
            response = self.get_response(data=post)
            with open(os.path.join(results_dir,'SIAD_results_BAU_no_outage.json'), 'w') as json_file:
                json.dump(response, json_file)
        # response = self.get_response(data=self.post_with_PV)
        # with open(os.path.join(results_dir,'SIAD_results_with_PV_no_resilience_newfin.json'), 'w') as json_file:
        #     json.dump(response, json_file)
        # response = self.get_response(data=self.post_no_PV)
        # with open(os.path.join(results_dir,'SIAD_results_no_PV_no_resilience.json'), 'w') as json_file:
        #     json.dump(response, json_file)

        def analyze_resilient_coa(FULL_RESILIENCE, post, results_filename):
            if FULL_RESILIENCE == True:
                critical_pct = 1
            else:
                critical_pct = 0.81
                
            post["Scenario"]["Site"]["LoadProfile"]["critical_load_pct"] = critical_pct
            day = 329
            post["Scenario"]["Site"]["LoadProfile"]["outage_start_hour"] = day*24
            post["Scenario"]["Site"]["LoadProfile"]["outage_end_hour"] = (day+14)*24
            response = self.get_response(data=post)
            pv_kw = response["outputs"]["Scenario"]["Site"]["PV"]["size_kw"] - post["Scenario"]["Site"]["PV"]["existing_kw"]
            day = 281
            post["Scenario"]["Site"]["LoadProfile"]["outage_start_hour"] = day*24
            post["Scenario"]["Site"]["LoadProfile"]["outage_end_hour"] = (day+14)*24
            response = self.get_response(data=post)
            batt_kw = response["outputs"]["Scenario"]["Site"]["Storage"]["size_kw"]
            day = 7
            post["Scenario"]["Site"]["LoadProfile"]["outage_start_hour"] = day*24
            post["Scenario"]["Site"]["LoadProfile"]["outage_end_hour"] = (day+14)*24
            response = self.get_response(data=post)
            batt_kwh = response["outputs"]["Scenario"]["Site"]["Storage"]["size_kwh"]
            day = 334
            post["Scenario"]["Site"]["LoadProfile"]["outage_start_hour"] = day*24
            post["Scenario"]["Site"]["LoadProfile"]["outage_end_hour"] = (day+14)*24
            response = self.get_response(data=post)
            gen_kw = response["outputs"]["Scenario"]["Site"]["Generator"]["size_kw"]
            
            post["Scenario"]["Site"]["PV"]["max_kw"] = pv_kw
            post["Scenario"]["Site"]["PV"]["min_kw"] = pv_kw
            post["Scenario"]["Site"]["Storage"]["max_kw"] = batt_kw
            post["Scenario"]["Site"]["Storage"]["min_kw"] = batt_kw
            post["Scenario"]["Site"]["Storage"]["max_kwh"] = batt_kwh
            post["Scenario"]["Site"]["Storage"]["min_kwh"] = batt_kwh
            post["Scenario"]["Site"]["Generator"]["max_kw"] = gen_kw
            post["Scenario"]["Site"]["Generator"]["min_kw"] = gen_kw
            post["Scenario"]["Site"]["LoadProfile"]["outage_start_hour"] = 0
            post["Scenario"]["Site"]["LoadProfile"]["outage_end_hour"] = 1
            response = self.get_response(data=post)
            with open(os.path.join(results_dir,results_filename), 'w') as json_file:
                json.dump(response, json_file)
            print(response["outputs"]["Scenario"]["Site"]["Financial"]["npv_us_dollars"])
        
        FULL_RESILIENCE = False
        analyze_resilient_coa(FULL_RESILIENCE, self.post_with_PV_no_ITC, 'SIAD_results_with_PV_no_ITC_{}.json'.format("full_resilience" if FULL_RESILIENCE else "neutral_NPV"))
        # analyze_resilient_coa(FULL_RESILIENCE, self.post_with_PV_with_ITC, 'SIAD_results_with_PV_with_ITC_{}.json'.format("full_resilience" if FULL_RESILIENCE else "neutral_NPV"))

        # for day in range(365-14):
        #     self.post_no_PV["Scenario"]["Site"]["LoadProfile"]["outage_start_hour"] = day*24
        #     self.post_no_PV["Scenario"]["Site"]["LoadProfile"]["outage_end_hour"] = (day+14)*24
        #     self.post_with_PV["Scenario"]["Site"]["LoadProfile"]["outage_start_hour"] = day*24
        #     self.post_with_PV["Scenario"]["Site"]["LoadProfile"]["outage_end_hour"] = (day+14)*24
        #     response = self.get_response(data=self.post_no_PV)
        #     with open(os.path.join(results_dir,'SIAD_results_no_PV_outage_{}.json'.format(day)), 'w') as json_file:
        #         json.dump(response, json_file)
        #     response = self.get_response(data=self.post_with_PV)
        #     with open(os.path.join(results_dir,'SIAD_results_with_PV_outage_{}.json'.format(day)), 'w') as json_file:
        #         json.dump(response, json_file)
        
        # resilience_sizes = {
        #     "no_PV":
        #         {
        #             "PV_kw": {100: 3100, 75: 3100, 50: 3100},
        #             "Storage_kw": {100: 1193.5067039999997, 75: 854.7337587499999, 50: 630.4682222068786},
        #             "Storage_kwh": {100: 3167.9785765893807, 75: 2442.9684545042373, 50: 1914.4676437190394},
        #             "Generator_kw": {100: 2261.104548506551, 75: 2261.104548506551, 50: 1560.7940500714649}
        #         },
        #     "with_PV":
        #         {
        #             "PV_kw": {100: 5449.2675, 75: 5183.6452, 50: 5092.6271},
        #             "Storage_kw": {100: 1357.6898421055575, 75: 1137.6451204218793, 50: 997.7849278437443},
        #             "Storage_kwh": {100: 4431.39393077016, 75: 3561.9007866028724, 50: 3101.541476740098},
        #             "Generator_kw": {100: 1773.9846833661054, 75: 1323.1884774629507, 50: 1167.351564405073}
        #         }
        # }
        # for pctl in [100,75,50]:
        #     scen = "with_PV"
        #     self.post_with_PV["Scenario"]["Site"]["PV"]["max_kw"] = resilience_sizes[scen]["PV_kw"][pctl] - self.post_with_PV["Scenario"]["Site"]["PV"]["existing_kw"]
        #     self.post_with_PV["Scenario"]["Site"]["PV"]["min_kw"] = resilience_sizes[scen]["PV_kw"][pctl] - self.post_with_PV["Scenario"]["Site"]["PV"]["existing_kw"]
        #     self.post_with_PV["Scenario"]["Site"]["Storage"]["max_kw"] = resilience_sizes[scen]["Storage_kw"][pctl]
        #     self.post_with_PV["Scenario"]["Site"]["Storage"]["min_kw"] = resilience_sizes[scen]["Storage_kw"][pctl]
        #     self.post_with_PV["Scenario"]["Site"]["Storage"]["max_kwh"] = resilience_sizes[scen]["Storage_kwh"][pctl]
        #     self.post_with_PV["Scenario"]["Site"]["Storage"]["min_kwh"] = resilience_sizes[scen]["Storage_kwh"][pctl]
        #     self.post_with_PV["Scenario"]["Site"]["LoadProfile"]["outage_start_hour"] = 0
        #     self.post_with_PV["Scenario"]["Site"]["LoadProfile"]["outage_end_hour"] = 1
        #     self.post_with_PV["Scenario"]["Site"]["Generator"]["max_kw"] = resilience_sizes[scen]["Generator_kw"][pctl]
        #     self.post_with_PV["Scenario"]["Site"]["Generator"]["min_kw"] = resilience_sizes[scen]["Generator_kw"][pctl]
        #     response = self.get_response(data=self.post_with_PV)
        #     with open(os.path.join(results_dir,'SIAD_results_{}_{}pctl_resilience.json'.format(scen,pctl)), 'w') as json_file:
        #             json.dump(response, json_file)
        #     scen = "no_PV"
        #     self.post_no_PV["Scenario"]["Site"]["Storage"]["max_kw"] = resilience_sizes[scen]["Storage_kw"][pctl]
        #     self.post_no_PV["Scenario"]["Site"]["Storage"]["min_kw"] = resilience_sizes[scen]["Storage_kw"][pctl]
        #     self.post_no_PV["Scenario"]["Site"]["Storage"]["max_kwh"] = resilience_sizes[scen]["Storage_kwh"][pctl]
        #     self.post_no_PV["Scenario"]["Site"]["Storage"]["min_kwh"] = resilience_sizes[scen]["Storage_kwh"][pctl]
        #     self.post_no_PV["Scenario"]["Site"]["LoadProfile"]["outage_start_hour"] = 0
        #     self.post_no_PV["Scenario"]["Site"]["LoadProfile"]["outage_end_hour"] = 1
        #     self.post_no_PV["Scenario"]["Site"]["Generator"]["max_kw"] = resilience_sizes[scen]["Generator_kw"][pctl]
        #     self.post_no_PV["Scenario"]["Site"]["Generator"]["min_kw"] = resilience_sizes[scen]["Generator_kw"][pctl]
        #     response = self.get_response(data=self.post_no_PV)
        #     with open(os.path.join(results_dir,'SIAD_results_{}_{}pctl_resilience.json'.format(scen,pctl)), 'w') as json_file:
        #             json.dump(response, json_file)
            
        # for scen in ["no_PV","with_PV"]:
        #     for pctl in [100,75,50]:
        #         exec('self.post_{}["Scenario"]["Site"]["PV"]["max_kw"] = resilience_sizes[scen]["PV_kw"][pctl] - self.post_{}["Scenario"]["Site"]["PV"]["existing_kw"]'.format(scen,scen))
        #         exec('self.post_{}["Scenario"]["Site"]["PV"]["min_kw"] = resilience_sizes[scen]["PV_kw"][pctl] - self.post_{}["Scenario"]["Site"]["PV"]["existing_kw"]'.format(scen,scen))
        #         exec('self.post_{}["Scenario"]["Site"]["Storage"]["max_kw"] = resilience_sizes[scen]["Storage_kw"][pctl]'.format(scen))
        #         exec('self.post_{}["Scenario"]["Site"]["Storage"]["min_kw"] = resilience_sizes[scen]["Storage_kw"][pctl]'.format(scen))
        #         exec('self.post_{}["Scenario"]["Site"]["Storage"]["max_kwh"] = resilience_sizes[scen]["Storage_kwh"][pctl]'.format(scen))
        #         exec('self.post_{}["Scenario"]["Site"]["Storage"]["min_kwh"] = resilience_sizes[scen]["Storage_kwh"][pctl]'.format(scen))
        #         exec('self.post_{}["Scenario"]["Site"]["LoadProfile"]["outage_start_hour"] = 0'.format(scen))
        #         exec('self.post_{}["Scenario"]["Site"]["LoadProfile"]["outage_end_hour"] = 1'.format(scen))
        #         exec('self.post_{}["Scenario"]["Site"]["Generator"]["max_kw"] = resilience_sizes[scen]["Generator_kw"][pctl]'.format(scen))
        #         exec('self.post_{}["Scenario"]["Site"]["Generator"]["min_kw"] = resilience_sizes[scen]["Generator_kw"][pctl]'.format(scen))
        #         exec('response = self.get_response(data=self.post_{})'.format(scen))
        #         with open(os.path.join(results_dir,'SIAD_results_{}_{}pctl_resilience.json'.format(scen,pctl)), 'w') as json_file:
        #             json.dump(response, json_file)

