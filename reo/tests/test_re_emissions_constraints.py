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
from reo.src.load_profile import default_annual_electric_loads
from reo.src.load_profile_boiler_fuel import LoadProfileBoilerFuel

class REandEmissionsContraintTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2
    
    def setUp(self):
        super(REandEmissionsContraintTests, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_post_elec_only = os.path.join('reo', 'tests', 'posts', 're_emissions_elec_only_POST.json')
        self.test_post_with_thermal = os.path.join('reo', 'tests', 'posts', 're_emissions_with_thermal_POST.json')

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_RE_and_ER(self):
        '''
        Test structure for renewable energy (RE) and emissions reduction (ER) targets.
        Runs a sweep of various scenarios (RE and ER targets, RE and ER accounting methodologies, technology combos (PV, wind, battery, boiler, CHP, HW-TES),
        elec-only vs thermal baselines/scenarios, net metering scenarios, and fully grid-connected vs resilience scenarios)
        and checks logic of calculations and application of constraints.
        '''

        ### define scenarios:
        ## Scenario 1: 
        #       elec-only
        #       include RE and ER from exported elec in calcs
        #       set min and max %RE constraint/target
        #       include outage with existing and new gen
        ## Scenario 2: 
        #       elec-only
        #       exclude RE and ER from exported elec in calcs
        #       set min and max %ER constraint/target
        #       no outage or backup gens
        ## Scenario 3: 
        #       elec + thermal techs, fixed capacities
        #       include RE and ER from exported elec in calcs
        #       no RE or ER targets (perhaps consider setting a min for both once we get it passing)
        #       no outage or backup gens (perhasp consider adding in)

        # for each of the following input variables, the first value corresponds to scenario 1, second value to scenario 2:
        include_exported_RE_in_total = [True,False,True]
        include_exported_ER_in_total = [True,False,True]
        RE_target = [0.8,None,None]
        ER_target = [None,0.8,None]
        resilience_scenario = ['yes_outage','no_outage','no_outage']

        for i in range(3):
            if i <= 1:
                nested_data = json.load(open(self.test_post_elec_only, 'rb'))
            elif i == 2:
                nested_data = json.load(open(self.test_post_with_thermal, 'rb')) 
                # include/exclude RE and ER from exported elec in calcs
                nested_data['Scenario']['Site']['include_exported_renewable_electricity_in_total'] = include_exported_RE_in_total[i]
                nested_data['Scenario']['Site']['include_exported_elec_emissions_in_total'] = include_exported_ER_in_total[i]
                # set min and max %RE and %RE constraint/target
                nested_data['Scenario']['Site']['renewable_electricity_min_pct'] = RE_target[i]
                nested_data['Scenario']['Site']['renewable_electricity_max_pct'] = RE_target[i]
                nested_data['Scenario']['Site']['co2_emissions_reduction_min_pct'] = ER_target[i]
                nested_data['Scenario']['Site']['co2_emissions_reduction_max_pct'] = ER_target[i]
                # include outage with existing and new gens:
                if resilience_scenario[i] == 'yes_outage':
                    outage_start_hour = 4032
                    outage_duration = 2000 #hrs
                    nested_data['Scenario']['Site']['LoadProfile']['outage_start_hour'] = outage_start_hour 
                    nested_data['Scenario']['Site']['LoadProfile']['outage_end_hour'] = outage_start_hour + outage_duration
                    nested_data['Scenario']['Site']['Generator']['max_kw'] = 20
                    nested_data['Scenario']['Site']['Generator']['existing_kw'] = 2
                    nested_data['Scenario']['Site']['Generator']['fuel_avail_gal'] = 1000    

                # post and poll
                resp = self.get_response(data=nested_data)
                self.assertHttpCreated(resp)
                r = json.loads(resp.content)
                run_uuid = r.get('run_uuid')
                d = ModelManager.make_response(run_uuid=run_uuid)

                ### automated emissions tests:                         
                # Emissions reductions:
                ER_pct_out = d['outputs']['Scenario']['Site']['lifecycle_emissions_reduction_CO2_pct']
                if ER_target[i] is not None:
                    self.assertAlmostEquals(ER_target[i], d['inputs']['Scenario']['Site']['co2_emissions_reduction_min_pct'])
                    self.assertAlmostEquals(ER_pct_out,ER_target[i],places=3)
                lifecycle_emissions_tCO2_out = d['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2']
                lifecycle_emissions_bau_tCO2_out = d['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2_bau']
                ER_pct_calced_out = (lifecycle_emissions_bau_tCO2_out-lifecycle_emissions_tCO2_out)/lifecycle_emissions_bau_tCO2_out
                ER_pct_diff = abs(ER_pct_calced_out-ER_pct_out)
                self.assertAlmostEquals(ER_pct_diff,0.0,places=2) #within 1% of each other
                # Year 1 emissions - non-BAU case:
                year_one_emissions_tCO2_out = d['outputs']['Scenario']['Site']['year_one_emissions_tCO2']
                yr1_fuel_emissions_tCO2_out = d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2'] or 0.0
                yr1_grid_emissions_tCO2_out = d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_tCO2'] or 0.0
                yr1_total_emissions_calced_tCO2 = yr1_fuel_emissions_tCO2_out + yr1_grid_emissions_tCO2_out 
                self.assertAlmostEquals(year_one_emissions_tCO2_out,yr1_total_emissions_calced_tCO2,places=-1)
                # Breakeven cost of emissions reductions 
                yr1_cost_ER_usd_per_tCO2_out = d['outputs']['Scenario']['Site']['breakeven_cost_of_emissions_reduction_us_dollars_per_tCO2'] 
                self.assertTrue(yr1_cost_ER_usd_per_tCO2_out>=0.0)

                ### test expected values for each scenario:                         
                if i ==0: # Scenario 1
                    # system sizes
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'],46.2923,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'],10.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'],2.4303,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'],6.062,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Generator']['size_kw'],22.0,places=0)
                    # NPV
                    npv = d['outputs']['Scenario']['Site']['Financial']['npv_us_dollars']
                    npv_diff_pct = (-101278.0 - npv)/-101278.0
                    self.assertAlmostEquals(npv_diff_pct,0.0,places=3)
                    # Renewable energy
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_renewable_electricity_pct'],0.8,places=3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_renewable_electricity_kwh'],75140.37,places=-3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_renewable_electricity_pct_bau'],0.146395,places=3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_total_renewable_energy_pct'],0.8,places=3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_total_renewable_energy_pct_bau'],0.146395,places=3)
                    # CO2 emissions - totals, from grid, from fuelburn, ER, $/tCO2 breakeven
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_reduction_CO2_pct'],0.660022,places=3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['breakeven_cost_of_emissions_reduction_us_dollars_per_tCO2'],301.237,places=1)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_tCO2'],12.79,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_tCO2_bau'],40.54,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2'],7.65,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2_bau'],0.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2'],8713.36,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2_bau'],25856.9,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2'],244.06,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2_bau'],717.86,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_from_fuelburn_tCO2'],152.97,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_from_fuelburn_tCO2_bau'],0.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_tCO2'],5.14,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_tCO2_bau'],40.54,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['lifecycle_emissions_tCO2'],91.09,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['lifecycle_emissions_tCO2_bau'],717.86,places=0)
                if i ==1: # Scenario 2
                    # system sizes
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'],59.1891,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'],23.0474,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'],12.532,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'],80.817,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Generator']['size_kw'],0.0,places=0)
                    # NPV
                    npv = d['outputs']['Scenario']['Site']['Financial']['npv_us_dollars']
                    npv_diff_pct = (-198934.0 - npv)/-198934.0
                    self.assertAlmostEquals(npv_diff_pct,0.0,places=3)
                    # Renewable energy
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_renewable_electricity_pct'],0.78984,places=3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_renewable_electricity_kwh'],78984.01,places=-1)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_renewable_electricity_pct_bau'],0.135426,places=3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_renewable_electricity_kwh_bau'],13542.62,places=-1)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_total_renewable_energy_pct'],0.78984,places=3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_total_renewable_energy_pct_bau'],0.135426,places=3)
                    # CO2 emissions - totals, from grid, from fuelburn, ER, $/tCO2 breakeven
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_reduction_CO2_pct'],0.8,places=3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['breakeven_cost_of_emissions_reduction_us_dollars_per_tCO2'],342.947,places=1)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_tCO2'],11.59,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_tCO2_bau'],57.97,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2'],0.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2_bau'],0.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2'],7395.84,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2_bau'],36979.2,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2'],205.33,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2_bau'],1026.65,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_from_fuelburn_tCO2'],0.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_from_fuelburn_tCO2_bau'],0.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_tCO2'],11.59,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_tCO2_bau'],57.97,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['lifecycle_emissions_tCO2'],205.33,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['lifecycle_emissions_tCO2_bau'],1026.65,places=0)
                if i ==2: # Scenario 3
                    # system sizes
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'],20.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'],0.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'],0.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'],0.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Generator']['size_kw'],0.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['CHP']['size_kw'],200.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['SteamTurbine']['size_kw'],1254.938,places=-1)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['NewBoiler']['size_mmbtu_per_hr'],28.04,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['AbsorptionChiller']['size_ton'],400.0,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['HotTES']['size_gal'],50000,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ColdTES']['size_gal'],30000,places=0)
                    # NPV
                    npv = d['outputs']['Scenario']['Site']['Financial']['npv_us_dollars']
                    npv_diff_pct = (11210580.0 - npv)/11210580.0
                    self.assertAlmostEquals(npv_diff_pct,0.0,places=3)
                    # Renewable energy
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_renewable_electricity_pct'],0.733551,places=3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_renewable_electricity_kwh'],5540064.64,places=-2)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_renewable_electricity_pct_bau'],0.001534,places=3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_renewable_electricity_kwh_bau'],13454.22,places=-1)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_total_renewable_energy_pct'],0.572143,places=3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['annual_total_renewable_energy_pct_bau'],0.000852,places=3)
                    # CO2 emissions - totals, from grid, from fuelburn, ER, $/tCO2 breakeven
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_reduction_CO2_pct'],1.276628,places=3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['breakeven_cost_of_emissions_reduction_us_dollars_per_tCO2'],0.0,places=3)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_tCO2'],-1717.17,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_tCO2_bau'],5931.29,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2'],33.89,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2_bau'],1585.32,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2'],-1212459.92,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2_bau'],4350968.52,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2'],-36835.36,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2_bau'],133157.72,places=1)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_from_fuelburn_tCO2'],847.34,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_from_fuelburn_tCO2_bau'],39633.01,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_tCO2'],-1751.07,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_tCO2_bau'],4345.97,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['lifecycle_emissions_tCO2'],-37682.7,places=0)
                    self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['lifecycle_emissions_tCO2_bau'],93524.7,places=0)
                                            
                                            
