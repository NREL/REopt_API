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
from reo.utilities import check_common_outputs


class REandEmissionsContraintTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    # order of tests:
    # Initially, no net metering / monetary credit for exports
    # - existing + new PV, new wind, new batt
    #   -- yes export credit
    #       --- min RE
    #       --- min ER
    #   -- no export credit
    #       --- min RE
    #       --- min ER
    # - no batt. (yes new + existing PV, wind)
    #   -- yes export credit
    #       --- min RE
    #       --- min ER
    #   -- no export credit
    #       --- min RE
    #       --- min ER
    # Then, add net metering and fix min and max
    # - no batt (yes new + existing PV, wind)
    #   -- yes export credit
    #       --- min & max RE
    #       --- min & max ER
    #   -- no export credit
    #       --- min & max RE
    #       --- min & max ER


    def setUp(self):
        super(REandEmissionsContraintTests, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_post = os.path.join('reo', 'tests', 'posts', 're_emissions_POST.json')

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)
    
    # For the initial eight tests below,
    # due to the curtailment formulation, 
    # the model is choosing to curtail unless there is credit (net metering or wholesale rates) given for exports
    def test_yesexportcredit_minRE(self):
        """
        Test scenario with
        - existing PV
        - new PV, wind, and storage enabled
        - %RE accounting method = 1 (yes credit for exported RE)
        - emissions accounting method = 1 (yes credit for exported RE)
        - 90% annual RE target with RE credit for grid exports
        """

        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['renewable_generation_min_pct'] = 0.90
        nested_data['Scenario']['Site']['renewable_generation_accounting_method'] = 1
        nested_data['Scenario']['Site']['emissions_reduction_accounting_method'] = 1
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
        nested_data['Scenario']['Site']['Storage']['max_kw'] = 100.0
        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 10000.0
        nested_data['Scenario']['Site']['Wind']['max_kw'] = 100

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Recommended system sizes - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'], 81.7313, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'], 16.9244, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'], 132.23, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'], 23.708, places=1)
        # Year 1 Site RE / emissions - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_pct'], 0.9, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_kwh'], 90000.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'], 14957.57, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_reduction_pct'], 0.88, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_lb_CO2'], 0.0, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_lb_CO2'], 14957.57, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_lb_CO2'], 0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_lb_CO2'], 14957.57,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        # Year 1 Site RE / emissions - BAU case
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_pct'], 0.14,places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_kwh'], 13542.62,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_bau_lb_CO2'],127811.53, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_bau_lb_CO2'],0.0, places=0)

    def test_yesexportcredit_minER(self):
        """
        Test scenario with
        - existing PV
        - new PV, wind, and storage enabled
        - %RE accounting method = 1 (yes credit for exported RE)
        - emissions accounting method = 1 (yes credit for exported RE)
        - 90% annual RE target with RE credit for grid exports
        """

        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['emissions_reduction_min_pct'] = 0.90
        nested_data['Scenario']['Site']['renewable_generation_accounting_method'] = 1
        nested_data['Scenario']['Site']['emissions_reduction_accounting_method'] = 1
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
        nested_data['Scenario']['Site']['Storage']['max_kw'] = 100.0
        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 10000.0
        nested_data['Scenario']['Site']['Wind']['max_kw'] = 100

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Recommended system sizes - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'], 78.8617, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'], 16.88, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'], 129.697, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'], 22.2391, places=1)
        # Year 1 Site RE / emissions - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_pct'], 0.89, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_kwh'], 88645.06,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'], 12771.33, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_reduction_pct'], 0.9, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_lb_CO2'], 0.0, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_lb_CO2'], 12771.33, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_lb_CO2'], 0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_lb_CO2'], 12771.33,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        # Year 1 Site RE / emissions - BAU case
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_pct'], 0.14,places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_kwh'], 13542.62,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_bau_lb_CO2'],127811.53, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_bau_lb_CO2'],0.0, places=0)

    def test_noexportcredit_minRE(self):
        """
        Test scenario with
        - existing PV
        - new PV, wind, and storage enabled
        - %RE accounting method = 1 (yes credit for exported RE)
        - emissions accounting method = 1 (yes credit for exported RE)
        - 90% annual RE target with RE credit for grid exports
        """

        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['renewable_generation_min_pct'] = 0.90
        nested_data['Scenario']['Site']['renewable_generation_accounting_method'] = 0
        nested_data['Scenario']['Site']['emissions_reduction_accounting_method'] = 0
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
        nested_data['Scenario']['Site']['Storage']['max_kw'] = 100.0
        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 10000.0
        nested_data['Scenario']['Site']['Wind']['max_kw'] = 100

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Recommended system sizes - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'], 81.7313, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'], 16.9244, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'], 132.23, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'], 23.708, places=1)
        # Year 1 Site RE / emissions - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_pct'], 0.9, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_kwh'], 90000.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'], 14940.32, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_reduction_pct'], 0.88, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_lb_CO2'], 0.0, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_lb_CO2'], 14940.32, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_lb_CO2'], 0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_lb_CO2'], 14940.32,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        # Year 1 Site RE / emissions - BAU case
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_pct'], 0.14,places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_kwh'], 13542.62,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_bau_lb_CO2'],127811.53, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_bau_lb_CO2'],0.0, places=0)

    def test_noexportcredit_minER(self):
        """
        Test scenario with
        - existing PV
        - new PV, wind, and storage enabled
        - %RE accounting method = 1 (yes credit for exported RE)
        - emissions accounting method = 1 (yes credit for exported RE)
        - 90% annual RE target with RE credit for grid exports
        """

        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['emissions_reduction_min_pct'] = 0.90
        nested_data['Scenario']['Site']['renewable_generation_accounting_method'] = 0
        nested_data['Scenario']['Site']['emissions_reduction_accounting_method'] = 0
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
        nested_data['Scenario']['Site']['Storage']['max_kw'] = 100.0
        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 10000.0
        nested_data['Scenario']['Site']['Wind']['max_kw'] = 100

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Recommended system sizes - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'], 78.8292, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'], 16.88, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'], 129.655, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'], 22.2391, places=1)
        # Year 1 Site RE / emissions - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_pct'], 0.89, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_kwh'], 88636.25,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'], 12781.15, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_reduction_pct'], 0.9, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_lb_CO2'], 0.0, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_lb_CO2'], 12781.15, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_lb_CO2'], 0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_lb_CO2'], 12781.15,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        # Year 1 Site RE / emissions - BAU case
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_pct'], 0.14,places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_kwh'], 13542.62,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_bau_lb_CO2'],127811.53, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_bau_lb_CO2'],0.0, places=0)

    # TEST NO BATTERIES. 

    def test_yesexportcredit_minRE_NObatt(self):
        """
        Test scenario with
        - existing PV
        - new PV, wind, and storage enabled
        - %RE accounting method = 1 (yes credit for exported RE)
        - emissions accounting method = 1 (yes credit for exported RE)
        - 90% annual RE target with RE credit for grid exports
        """

        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['renewable_generation_min_pct'] = 0.90
        nested_data['Scenario']['Site']['renewable_generation_accounting_method'] = 1
        nested_data['Scenario']['Site']['emissions_reduction_accounting_method'] = 1
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
        nested_data['Scenario']['Site']['Storage']['max_kw'] = 0.0
        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 0.0
        nested_data['Scenario']['Site']['Wind']['max_kw'] = 1000

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Recommended system sizes - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'],255.878, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'], 265.0181, places=1)
        # Year 1 Site RE / emissions - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_pct'], 0.9, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_kwh'], 90000.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'], 14933.84, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_reduction_pct'], 0.88, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_lb_CO2'], 0.0, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_lb_CO2'], 14933.84, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_lb_CO2'], 0.0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_lb_CO2'], 14933.84,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_lb_CO2'],0.0, places=1) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_scope1_emissions_lb_CO2'], 0.0,places=1) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        # check curtailment vs exports
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_curtailed_production_series_kw']),336270.423, places=0)
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_curtailed_production_series_kw']),404165.496, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_to_grid_series_kw']),0.0, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_to_grid_series_kw']),0.0, places=0) 
        # Year 1 Site RE / emissions - BAU case
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_pct'], 0.14,places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_kwh'], 13542.62,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_bau_lb_CO2'],127811.53, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_bau_lb_CO2'],0.0, places=0)

    def test_yesexportcredit_minER_NObatt(self):
        """
        Test scenario with
        - existing PV
        - new PV, wind, and storage enabled
        - %RE accounting method = 1 (yes credit for exported RE)
        - emissions accounting method = 1 (yes credit for exported RE)
        - 90% annual RE target with RE credit for grid exports
        """

        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['emissions_reduction_min_pct'] = 0.90
        nested_data['Scenario']['Site']['renewable_generation_accounting_method'] = 1
        nested_data['Scenario']['Site']['emissions_reduction_accounting_method'] = 1
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
        nested_data['Scenario']['Site']['Storage']['max_kw'] = 0.0
        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 0.0
        nested_data['Scenario']['Site']['Wind']['max_kw'] = 1000

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Recommended system sizes - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'], 312.8784, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'],0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'], 407.5694, places=1)
        # Year 1 Site RE / emissions - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_pct'], 0.91, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_kwh'], 91461.11,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'], 12771.33, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_reduction_pct'], 0.9, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_lb_CO2'], 0.0, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_lb_CO2'], 12771.33, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_lb_CO2'], 0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_lb_CO2'], 12771.33,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0)
        # check curtailment vs exports
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_curtailed_production_series_kw']),415677.589999, places=0)
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_curtailed_production_series_kw']),660265.115, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_to_grid_series_kw']),0.0, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_to_grid_series_kw']),0.0, places=0) 
        # Year 1 Site RE / emissions - BAU case
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_pct'], 0.14,places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_kwh'], 13542.62,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_bau_lb_CO2'],127811.53, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_bau_lb_CO2'],0.0, places=0)
        
    def test_noexportcredit_minRE_NObatt(self):
        """
        Test scenario with
        - existing PV
        - new PV, wind, and storage enabled
        - %RE accounting method = 1 (yes credit for exported RE)
        - emissions accounting method = 1 (yes credit for exported RE)
        - 90% annual RE target with RE credit for grid exports
        """

        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['renewable_generation_min_pct'] = 0.90
        nested_data['Scenario']['Site']['renewable_generation_accounting_method'] = 0
        nested_data['Scenario']['Site']['emissions_reduction_accounting_method'] = 0
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
        nested_data['Scenario']['Site']['Storage']['max_kw'] = 0.0
        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 0.0
        nested_data['Scenario']['Site']['PV']['max_kw'] = 10000
        nested_data['Scenario']['Site']['Wind']['max_kw'] = 1000

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Recommended system sizes - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'], 255.878, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'], 265.0181, places=1)
        # Year 1 Site RE / emissions - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_pct'], 0.9, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_kwh'], 90000.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'], 14933.84, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_reduction_pct'], 0.88, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_lb_CO2'], 0.0, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_lb_CO2'], 14933.84, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_lb_CO2'], 0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_lb_CO2'], 14933.84,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        # check curtailment vs exports
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_curtailed_production_series_kw']),336270.42, places=0)
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_curtailed_production_series_kw']),404165.496, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_to_grid_series_kw']),0.0, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_to_grid_series_kw']),0.0, places=0) 
        # Year 1 Site RE / emissions - BAU case (currently same for all tests in this suite)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_pct'], 0.14,places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_kwh'], 13542.62,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_bau_lb_CO2'],127811.53, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_bau_lb_CO2'],0.0, places=0)

    def test_noexportcredit_minER_NObatt(self):
        """
        Test scenario with
        - existing PV
        - new PV, wind, and storage enabled
        - %RE accounting method = 1 (yes credit for exported RE)
        - emissions accounting method = 1 (yes credit for exported RE)
        - 90% annual RE target with RE credit for grid exports
        """

        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['emissions_reduction_min_pct'] = 0.90
        nested_data['Scenario']['Site']['renewable_generation_accounting_method'] = 0
        nested_data['Scenario']['Site']['emissions_reduction_accounting_method'] = 0
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
        nested_data['Scenario']['Site']['Storage']['max_kw'] = 0.0
        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 0.0
        nested_data['Scenario']['Site']['PV']['max_kw'] = 10000
        nested_data['Scenario']['Site']['Wind']['max_kw'] = 1000

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Recommended system sizes - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'], 311.1855, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'], 406.9693, places=1)
        # Year 1 Site RE / emissions - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_pct'], 0.91, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_kwh'], 91454.45,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'], 12781.15, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_reduction_pct'], 0.9, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_lb_CO2'], 0.0, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_lb_CO2'], 12781.15, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_lb_CO2'], 0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_lb_CO2'], 12781.15,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        # check curtailment vs exports
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_curtailed_production_series_kw']),413371.301, places=0)
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_curtailed_production_series_kw']),659182.566, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_to_grid_series_kw']),0.0, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_to_grid_series_kw']),0.0, places=0) 
        # Year 1 Site RE / emissions - BAU case
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_pct'], 0.14,places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_kwh'], 13542.62,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_bau_lb_CO2'],127811.53, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_bau_lb_CO2'],0.0, places=0)
    
    # ADD NET METERING

    def test_yesexportcredit_minandmaxRE_NObatt_addNEM(self):

        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['renewable_generation_min_pct'] = 0.40
        nested_data['Scenario']['Site']['renewable_generation_max_pct'] = 0.40
        nested_data['Scenario']['Site']['renewable_generation_accounting_method'] = 1
        nested_data['Scenario']['Site']['emissions_reduction_accounting_method'] = 1
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
        nested_data['Scenario']['Site']['Storage']['max_kw'] = 0.0
        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 0.0
        nested_data['Scenario']['Site']['Wind']['max_kw'] = 1000
        nested_data['Scenario']['Site']['ElectricTariff']['net_metering_limit_kw'] = 1000

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Recommended system sizes - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'],29.3971, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'], 0.0, places=1)
        # Year 1 Site RE / emissions - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_pct'], 0.4, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_kwh'], 40000.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'], 88740.39, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_reduction_pct'], 0.31, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_lb_CO2'], 0.0, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_lb_CO2'], 105642.69, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_lb_CO2'], -16902.29,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_lb_CO2'], 105642.687,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_lb_CO2'],-16901.99, places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) 
        # check curtailment vs exports
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_curtailed_production_series_kw']),0.0, places=0)
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_curtailed_production_series_kw']),0.0, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_to_grid_series_kw']),11252.501, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_to_grid_series_kw']),0.0, places=0) 
        # Year 1 Site RE / emissions - BAU case
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_pct'], 0.14,places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_kwh'], 13606.76,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'], 127713.31,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_bau_lb_CO2'], -98.22,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_bau_lb_CO2'],127811.53, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_bau_lb_CO2'],-98.22, places=0)
    
    def test_noexportcredit_minandmaxRE_NObatt_addNEM(self):

        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['renewable_generation_min_pct'] = 0.40
        nested_data['Scenario']['Site']['renewable_generation_max_pct'] = 0.40
        nested_data['Scenario']['Site']['renewable_generation_accounting_method'] = 0
        nested_data['Scenario']['Site']['emissions_reduction_accounting_method'] = 0
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
        nested_data['Scenario']['Site']['Storage']['max_kw'] = 0.0
        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 0.0
        nested_data['Scenario']['Site']['Wind']['max_kw'] = 1000
        nested_data['Scenario']['Site']['ElectricTariff']['net_metering_limit_kw'] = 1000

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Recommended system sizes - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'],37.3824, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'], 5.9066, places=1)
        # Year 1 Site RE / emissions - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_pct'], 0.4, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_kwh'], 40000.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'], 89077.48, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_reduction_pct'], 0.3, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_lb_CO2'], 0.0, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_lb_CO2'], 89077.48,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_lb_CO2'],-32346.66, places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_nonscope_emissions_lb_CO2'],-14.73, places=0) 
        # check curtailment vs exports
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_curtailed_production_series_kw']),0.0, places=0)
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_curtailed_production_series_kw']),0.0, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_to_grid_series_kw']),21604.985, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_to_grid_series_kw']),8.976, places=0) 
        # Year 1 Site RE / emissions - BAU case
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_pct'], 0.14,places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_kwh'],13542.62,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'],127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_bau_lb_CO2'], -98.22,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_bau_lb_CO2'],127811.53, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_bau_lb_CO2'],-98.22, places=0)

    def test_yesexportcredit_minandmaxER_NObatt_addNEM(self):

        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['emissions_reduction_min_pct'] = 0.40
        nested_data['Scenario']['Site']['emissions_reduction_max_pct'] = 0.40
        nested_data['Scenario']['Site']['renewable_generation_accounting_method'] = 1
        nested_data['Scenario']['Site']['emissions_reduction_accounting_method'] = 1
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
        nested_data['Scenario']['Site']['Storage']['max_kw'] = 0.0
        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 0.0
        nested_data['Scenario']['Site']['Wind']['max_kw'] = 1000
        nested_data['Scenario']['Site']['ElectricTariff']['net_metering_limit_kw'] = 1000

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Recommended system sizes - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'],35.4256, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'], 0.0, places=1)
        # Year 1 Site RE / emissions - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_pct'], 0.48, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_kwh'], 48202.76,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'], 76627.99, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_reduction_pct'], 0.4, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_lb_CO2'], 0.0, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_lb_CO2'], 102031.89, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_lb_CO2'], -25403.9,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_lb_CO2'], 102031.886,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_lb_CO2'],-25403.9, places=0) # model is choosing to curtail rather than count the credit for this...
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_nonscope_emissions_lb_CO2'],0.0, places=0) # model is choosing to curtail rather than count the credit for this...
        # check curtailment vs exports
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_curtailed_production_series_kw']),0.0, places=0)
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_curtailed_production_series_kw']),0.0, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_to_grid_series_kw']),16946.111, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_to_grid_series_kw']),0.0, places=0) 
        # Year 1 Site RE / emissions - BAU case
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_pct'], 0.14,places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_kwh'], 13606.76,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'], 127713.31,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_bau_lb_CO2'], -98.22,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_bau_lb_CO2'],127811.53, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_bau_lb_CO2'],-98.22, places=0)
    
    def test_noexportcredit_minandmaxER_NObatt_addNEM(self):

        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['emissions_reduction_min_pct'] = 0.40
        nested_data['Scenario']['Site']['emissions_reduction_max_pct'] = 0.40
        nested_data['Scenario']['Site']['renewable_generation_accounting_method'] = 0
        nested_data['Scenario']['Site']['emissions_reduction_accounting_method'] = 0
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
        nested_data['Scenario']['Site']['Storage']['max_kw'] = 0.0
        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 0.0
        nested_data['Scenario']['Site']['Wind']['max_kw'] = 1000
        nested_data['Scenario']['Site']['ElectricTariff']['net_metering_limit_kw'] = 1000

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Recommended system sizes - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'],39.1435, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'], 0.0, places=1)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'], 12.5555, places=1)
        # Year 1 Site RE / emissions - non-BAU
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_pct'], 0.48, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_kwh'], 48364.18,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'], 76686.92, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_reduction_pct'], 0.4, places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_lb_CO2'], 0.0, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_lb_CO2'], 76686.92,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_lb_CO2'],-36169.73, places=0) # model is choosing to curtail rather than count the credit for this...
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_scope1_emissions_lb_CO2'], 0.0,places=0) 
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['year_one_nonscope_emissions_lb_CO2'],-5328.21, places=0) # model is choosing to curtail rather than count the credit for this...
        # check curtailment vs exports
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_curtailed_production_series_kw']),0.0, places=0)
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_curtailed_production_series_kw']),0.0, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['PV']['year_one_to_grid_series_kw']),24171.19, places=0) 
        self.assertAlmostEquals(sum(d['outputs']['Scenario']['Site']['Wind']['year_one_to_grid_series_kw']),3574.279, places=0) 
        # Year 1 Site RE / emissions - BAU case
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_pct'], 0.14,places=2)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_generation_bau_kwh'],13542.62,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'],127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_scope2_emissions_bau_lb_CO2'], 127811.53,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_nonscope_emissions_bau_lb_CO2'], -98.22,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_scope2_emissions_bau_lb_CO2'],127811.53, places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_scope1_emissions_bau_lb_CO2'], 0.0,places=0)
        self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['year_one_nonscope_emissions_bau_lb_CO2'],-98.22, places=0)

