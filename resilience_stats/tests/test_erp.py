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
from django.test import TestCase
import numpy as np


class ERPTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(ERPTests, self).setUp()

        #for ERP simulation
        self.reopt_base_erp = '/dev/erp/'
        self.reopt_base_erp_results = '/dev/erp/{}/results/'
        self.post_sim = os.path.join('resilience_stats', 'tests', 'ERP_sim_post.json')
        
        #for REopt optimization
        self.reopt_base_opt = '/dev/job/'
        self.post_opt = os.path.join('resilience_stats', 'tests', 'ERP_opt_post.json')

    def get_response_opt(self, data):
        return self.api_client.post(self.reopt_base_opt, format='json', data=data)

    def get_response_sim(self, data_sim):
        return self.api_client.post(self.reopt_base_erp, format='json', data=data_sim)

    def get_results_sim(self, run_uuid):
        return self.api_client.get(self.reopt_base_erp_results.format(run_uuid))

    def test_erp_with_reopt_run_uuid(self):
        """
        Tests calling ERP with a REopt run_uuid provided, but all inputs from REopt results overrided.
        This ends up being the same as the second to last test in the "Backup Generator Reliability" testset in the REopt Julia package.
        Then tests calling ERP with the same REopt run_uuid provided, but only the necessary additional ERP inputs provided.
        This is the same as the last test in the "Backup Generator Reliability" testset in the REopt Julia package.
        """

        data = json.load(open(self.post_opt, 'rb'))
        resp = self.get_response_opt(data)
        self.assertHttpCreated(resp)
        r_opt = json.loads(resp.content)
        reopt_run_uuid = r_opt.get('run_uuid')

        assert(reopt_run_uuid is not None)
        post_sim = json.load(open(self.post_sim, 'rb'))
        post_sim["reopt_run_uuid"] = reopt_run_uuid
        post_sim["battery_starting_soc_series_fraction"] = 8760 * [1]

        resp = self.get_response_sim(post_sim)
        self.assertHttpCreated(resp)
        r_sim = json.loads(resp.content)
        erp_run_uuid = r_sim.get('run_uuid')

        resp = self.get_results_sim(erp_run_uuid)
        results = json.loads(resp.content)
        #same as last test in julia
        self.assertAlmostEqual(results["mean_cumulative_outage_survival_final_time_step"], 0.904242, places=-4)

        #remove inputs that override REopt results and run again
        for input_key in [
                    "generator_size_kw",
                    "battery_size_kw",
                    "battery_size_kwh",
                    "pv_size_kw",
                    "critical_loads_kw",
                    "pv_production_factor_series",
                    "battery_starting_soc_series_fraction"
                ]:
            post_sim.pop(input_key)
        
        resp = self.get_response_sim(post_sim)
        self.assertHttpCreated(resp)
        r_sim = json.loads(resp.content)
        erp_run_uuid = r_sim.get('run_uuid')

        resp = self.get_results_sim(erp_run_uuid)
        results = json.loads(resp.content)
        self.assertAlmostEqual(results["mean_cumulative_outage_survival_final_time_step"], 0.817088, places=-4)

    def test_erp_with_no_opt(self):
        """
        Tests calling ERP on it's own without providing a REopt run_uuid.
        Same as the second to last test in the "Backup Generator Reliability" testset in the REopt Julia package.
        """
        
        post_sim = json.load(open(self.post_sim, 'rb'))

        resp = self.get_response_sim(post_sim)
        self.assertHttpCreated(resp)
        r_sim = json.loads(resp.content)
        erp_run_uuid = r_sim.get('run_uuid')

        resp = self.get_results_sim(erp_run_uuid)
        results = json.loads(resp.content)
        self.assertAlmostEqual(results["mean_cumulative_outage_survival_final_time_step"], 0.990784, places=-4)
