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
from reo.nested_to_flat_output import nested_to_flat_chp
from django.test import TestCase
from reo.models import ModelManager
from reo.utilities import check_common_outputs
import numpy as np

class CHPTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(CHPTest, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_post = os.path.join('reo', 'tests', 'posts', 'test_chp_sizing_POST.json')
        self.resilience_post = os.path.join('reo', 'tests', 'posts', 'test_chp_resilience_POST.json')

    def get_response(self, data):

        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_chp_sizing_monolith_1pct(self):
        """
        Validation to ensure that:
         1) CHP Sizing is consistent

         This test was verified to be withing 1.5% gap after 10 mins of the Mosel/Xpress monolith using windows Xpress IVE

        :return:
        """

        # Call API, get results in "d" dictionary
        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data["Scenario"]["timeout_seconds"] = 420
        nested_data["Scenario"]["optimality_tolerance_bau"] = 0.001
        nested_data["Scenario"]["optimality_tolerance_techs"] = 0.01

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat_chp(d['outputs'])

        # The values compared to the expected values may change if optimization parameters were changed
        d_expected = dict()
        d_expected['lcc'] = 13476072.0
        d_expected['npv'] = 1231748.579
        d_expected['chp_kw'] = 468.718
        d_expected['chp_year_one_fuel_used_mmbtu'] = 30555.6
        d_expected['chp_year_one_electric_energy_produced_kwh'] = 3086580.645
        d_expected['chp_year_one_thermal_energy_produced_mmbtu'] = 9739.972
        d_expected['boiler_total_fuel_cost_us_dollars'] = 7211.964
        d_expected['chp_total_fuel_cost_us_dollars'] = 3271904.872
        d_expected['total_om_costs'] = 686311.0

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages'].get('error')))
            raise

    def test_cost_curve(self):
        """
        Validation to ensure that:
         1) CHP capital cost curve handling is correct

        :return:
        """

        # Call API, get results in "d" dictionary
        nested_data = json.load(open(self.test_post, 'rb'))
        # CHP
        nested_data["Scenario"]["Site"]["CHP"] = {}
        nested_data["Scenario"]["timeout_seconds"] = 420
        nested_data["Scenario"]["optimality_tolerance_bau"] = 0.001
        nested_data["Scenario"]["optimality_tolerance_techs"] = 0.01
        nested_data["Scenario"]["Site"]["CHP"]["prime_mover"] = "recip_engine"
        nested_data["Scenario"]["Site"]["CHP"]["size_class"] = 2
        nested_data["Scenario"]["Site"]["CHP"]["min_kw"] = 800
        nested_data["Scenario"]["Site"]["CHP"]["max_kw"] = 800
        nested_data["Scenario"]["Site"]["CHP"]["installed_cost_us_dollars_per_kw"] = [2900, 2700, 2370]
        nested_data["Scenario"]["Site"]["CHP"]["tech_size_for_cost_curve"] = [100, 600, 1140]
        #nested_data["Scenario"]["Site"]["CHP"]["utility_rebate_us_dollars_per_kw"] = 50
        #nested_data["Scenario"]["Site"]["CHP"]["utility_rebate_max_us_dollars"] = 1.0E10 #50 * 200
        #nested_data["Scenario"]["Site"]["CHP"]["federal_rebate_us_dollars_per_kw"] = 50
        nested_data["Scenario"]["Site"]["CHP"]["federal_itc_pct"] = 0.1
        nested_data["Scenario"]["Site"]["CHP"]["macrs_option_years"] = 0
        nested_data["Scenario"]["Site"]["CHP"]["macrs_bonus_pct"] = 0
        nested_data["Scenario"]["Site"]["CHP"]["macrs_itc_reduction"] = 0.0

        # init_capex = 600 * 2700 + (800 - 600) * slope, where
        # slope = (1140 * 2370 - 600 * 2700) / (1140 - 600)
        init_capex_chp_expected = 2020666.67
        net_capex_chp_expected = init_capex_chp_expected - np.npv(0.083, [0, init_capex_chp_expected * 0.1])

        #PV
        nested_data["Scenario"]["Site"]["PV"]["min_kw"] = 1500
        nested_data["Scenario"]["Site"]["PV"]["max_kw"] = 1500
        nested_data["Scenario"]["Site"]["PV"]["installed_cost_us_dollars_per_kw"] = 1600
        nested_data["Scenario"]["Site"]["PV"]["federal_itc_pct"] = 0.26
        nested_data["Scenario"]["Site"]["PV"]["macrs_option_years"] = 0
        nested_data["Scenario"]["Site"]["PV"]["macrs_bonus_pct"] = 0
        nested_data["Scenario"]["Site"]["PV"]["macrs_itc_reduction"] = 0.0

        init_capex_pv_expected = 1500 * 1600
        net_capex_pv_expected = init_capex_pv_expected - np.npv(0.083, [0, init_capex_pv_expected * 0.26])

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        init_capex_total_expected = init_capex_chp_expected + init_capex_pv_expected
        net_capex_total_expected = net_capex_chp_expected + net_capex_pv_expected

        init_capex_total = d["outputs"]["Scenario"]["Site"]["Financial"]["initial_capital_costs"]
        net_capex_total = d["outputs"]["Scenario"]["Site"]["Financial"]["net_capital_costs"]


        # # The values compared to the expected values may change if optimization parameters were changed
        self.assertAlmostEqual(init_capex_total_expected, init_capex_total, delta=1.0)
        self.assertAlmostEqual(net_capex_total_expected, net_capex_total, delta=1.0)

    def test_chp_resilience_unavailability(self):
        """
        Validation to ensure that:
            1) CHP meets load during outage without exporting
            2) CHP never exports if chp_allowed_to_export input is False
            3) CHP does not "curtail", i.e. send power to a load bank
            4) Cooling load gets zeroed out during the outage period
            5) Unavailability intervals that intersect with grid-outages get ignored
            6) Unavailability intervals that do not intersect with grid-outages result in no CHP production

        :return:
        """

        # Call API, get results in "d" dictionary
        nested_data = json.load(open(self.resilience_post, 'rb'))
        nested_data["Scenario"]["timeout_seconds"] = 420
        nested_data["Scenario"]["optimality_tolerance_bau"] = 0.001
        nested_data["Scenario"]["optimality_tolerance_techs"] = 0.01
        
        # Add unavailability periods that 1) intersect (ignored) and 2) don't intersect with outage period
        nested_data["Scenario"]["Site"]["CHP"]["chp_unavailability_periods"] = [{"month": 1, "start_week_of_month": 2,
                                                                                "start_day_of_week": 1, "start_hour": 1,
                                                                                "duration_hours": 8},
                                                                                {"month": 1, "start_week_of_month": 2,
                                                                                "start_day_of_week": 3,"start_hour": 9,
                                                                                "duration_hours": 8}
                                                                                ]
        unavail_1_start = 24 + 1  # Manually doing the math from the unavailability defined above
        unavail_1_end = unavail_1_start + 8
        unavail_2_start = 24*3 + 9
        unavail_2_end = unavail_2_start + 8
        
        # Specify the CHP.min_turn_down_pct which is NOT used during an outage
        nested_data["Scenario"]["Site"]["CHP"]["min_turn_down_pct"] = 0.5
        # Specify outage period; outage timesteps are 1-indexed
        outage_start = unavail_1_start
        nested_data["Scenario"]["Site"]["LoadProfile"]["outage_start_time_step"] = outage_start
        outage_end = unavail_1_end
        nested_data["Scenario"]["Site"]["LoadProfile"]["outage_end_time_step"] = outage_end
        nested_data["Scenario"]["Site"]["LoadProfile"]["critical_load_pct"] = 0.25

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        tot_elec_load = d['outputs']['Scenario']['Site']['LoadProfile']['year_one_electric_load_series_kw']
        chp_total_elec_prod = d['outputs']['Scenario']['Site']['CHP']['year_one_electric_production_series_kw']
        chp_to_load = d['outputs']['Scenario']['Site']['CHP']['year_one_to_load_series_kw']
        chp_export = d['outputs']['Scenario']['Site']['CHP']['year_one_to_grid_series_kw']
        cooling_elec_load = d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['year_one_chiller_electric_load_series_kw']

        # The values compared to the expected values
        #self.assertTrue(all(chp_to_load[i] == tot_elec_load[i] for i in range(outage_start, outage_end)))
        self.assertAlmostEqual(sum(chp_to_load[outage_start-1:outage_end-1]),sum(tot_elec_load[outage_start-1:outage_end-1]), places=1)
        self.assertEqual(sum(chp_export), 0.0)  # Resulting in "None" instead of zero - likely because ExportTiers is empty
        self.assertAlmostEqual(sum(chp_total_elec_prod), sum(chp_to_load), delta=1.0E-5*sum(chp_total_elec_prod))
        self.assertEqual(sum(cooling_elec_load[outage_start-1:outage_end-1]), 0.0) 
        self.assertEqual(sum(chp_total_elec_prod[unavail_2_start-1:unavail_2_end-1]), 0.0)

    def test_supplementary_firing(self):
        """
        validation to ensure that: 
        (1) CHP Supplementary firing option loads as intended
        (2) CHP Supplementary firing is used to meet heating load when pricing is low relative to boiler fuel use
        (3) CHP Supplementary firing is not used to meet heating load when capital cost it too high to justify purchase
        (4) Capital Cost of CHP Supplementary firing is included in objective function
        """
        # Call API, get results in "d" dictionary
        nested_data = json.load(open(self.test_post, 'rb'))
        # CHP
        nested_data["Scenario"]["timeout_seconds"] = 420
        nested_data["Scenario"]["optimality_tolerance_bau"] = 0.001
        nested_data["Scenario"]["optimality_tolerance_techs"] = 0.01
        nested_data["Scenario"]["Site"]["CHP"]["prime_mover"] = "combustion_turbine"
        nested_data["Scenario"]["Site"]["CHP"]["size_class"] = 2
        nested_data["Scenario"]["Site"]["CHP"]["min_kw"] = 800
        nested_data["Scenario"]["Site"]["CHP"]["max_kw"] = 800
        #Supplementary Firing
        nested_data["Scenario"]["Site"]["CHP"]["supplementary_firing_capital_cost_per_kw"] = 10000
        nested_data["Scenario"]["Site"]["CHP"]["supplementary_firing_max_steam_ratio"] = 5.0
        nested_data["Scenario"]["Site"]["CHP"]["supplementary_firing_efficiency"] = 0.9
        #Flat Thermal and Electrical Loads
        kw_to_mmbtu = 0.00340951064
        nested_data["Scenario"]["Site"]["LoadProfileBoilerFuel"]["loads_mmbtu_per_hour"] = [3000*kw_to_mmbtu]*8760
        nested_data["Scenario"]["Site"]["LoadProfile"]["loads_kw"] = [800]*8760
        nested_data["Scenario"]["Site"]["LoadProfile"]["critical_loads_kw"] = [800]*8760
        #Make Boiler relatively inefficient to justify use of chp supplementary firing when available  
        nested_data["Scenario"]["Site"]["Boiler"]["boiler_efficiency"] = 0.95
        # PV set to zero
        nested_data["Scenario"]["Site"]["PV"]["min_kw"] = 0
        nested_data["Scenario"]["Site"]["PV"]["max_kw"] = 0
        # Run, and record capital cost and thermal production
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        # Edit capital cost to a more reasonable value
        c = nested_to_flat_chp(d['outputs'])
        d_expected = {}
        d_expected['chp_kw'] = 800
        d_expected['chp_supplementary_firing_kw'] = 0
        d_expected['chp_year_one_electric_energy_produced_kwh'] = 800*8760
        d_expected['chp_year_one_thermal_energy_produced_mmbtu'] = 800*(0.4418/0.3573)*(kw_to_mmbtu)*8760
        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages'].get('error')))
            raise

        # Calculate capex without supplementary firing
        capex_no_supp_firing = 1.0*d["outputs"]["Scenario"]["Site"]["Financial"]["initial_capital_costs"]

        # Rerun and record capital cost and thermal production of CHP
        nested_data["Scenario"]["Site"]["Boiler"]["boiler_efficiency"] = 0.85
        nested_data["Scenario"]["Site"]["CHP"]["supplementary_firing_capital_cost_per_kw"] = 10
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat_chp(d['outputs'])
        d_expected['chp_supplementary_firing_kw'] = 800
        d_expected['chp_year_one_thermal_energy_produced_mmbtu'] = 122756
        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages'].get('error')))
            raise

        capex_with_supp_firing = d["outputs"]["Scenario"]["Site"]["Financial"]["initial_capital_costs"]
        self.assertAlmostEqual(capex_no_supp_firing+8000, capex_with_supp_firing, delta=1.0)