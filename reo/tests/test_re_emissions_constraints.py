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
                nested_data = json.load(open(self.test_post_with_thermal, 'rb')) #originated from test_steamturbine.py test post
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

            ### run automated tests:                         
            ## calculate BAU and non-BAU annual load:
            elec_loads_kw = d['outputs']['Scenario']['Site']['LoadProfile']['year_one_electric_load_series_kw']
            annual_elec_load_kwh = sum(elec_loads_kw)
            annual_elec_load_kwh_bau = sum(elec_loads_kw) 
            if resilience_scenario[i] == 'yes_outage':
                bau_sustained_time_steps = d['outputs']['Scenario']['Site']['LoadProfile']['bau_sustained_time_steps'] # note hourly timesteps for this test
                critical_elec_loads_kw = d['outputs']['Scenario']['Site']['LoadProfile']['critical_load_series_kw']
                annual_elec_load_kwh_bau -= sum(elec_loads_kw[outage_start_hour-1:outage_start_hour+outage_duration-1]) + \
                    sum(critical_elec_loads_kw[outage_start_hour-1:outage_start_hour-1+min(bau_sustained_time_steps,outage_duration)])
                                        
            ## RE elec tests
            # Year 1 RE elec - BAU case:
            RE_elec_bau_pct_out = d['outputs']['Scenario']['Site']['year_one_renewable_electricity_pct_bau'] or 0.0
            RE_elec_bau_kwh_out = d['outputs']['Scenario']['Site']['year_one_renewable_electricity_kwh_bau'] or 0.0
            RE_elec_bau_kwh_pct_diff = (annual_elec_load_kwh_bau*RE_elec_bau_pct_out - RE_elec_bau_kwh_out)/RE_elec_bau_kwh_out
            self.assertAlmostEquals(RE_elec_bau_kwh_pct_diff,0.0,places=2) # <0.5% error
            # Year 1 RE elec - non-BAU case:
            RE_elec_pct_out = d['outputs']['Scenario']['Site']['year_one_renewable_electricity_pct'] or 0.0
            if RE_target[i] is not None:
                self.assertAlmostEquals(RE_elec_pct_out,RE_target[i],places=3)
            RE_elec_kwh_out = d['outputs']['Scenario']['Site']['year_one_renewable_electricity_kwh'] or 0.0
            RE_elec_kwh_pct_diff = (annual_elec_load_kwh*RE_elec_pct_out - RE_elec_kwh_out)/RE_elec_kwh_out
            self.assertAlmostEquals(RE_elec_kwh_pct_diff,0.0,places=2)
            # check RE elec export credit accounting
            PV_avg_annual_kwh = d['outputs']['Scenario']['Site']['PV']['average_yearly_energy_produced_kwh'] or 0.0
            PV_avg_annual_kwh_exports = d['outputs']['Scenario']['Site']['PV']['average_yearly_energy_exported_kwh'] or 0.0
            PV_year_one_kwh = d['outputs']['Scenario']['Site']['PV']['year_one_energy_produced_kwh'] or 0.0
            if PV_year_one_kwh > 0:
                PV_year_one_to_avg_annual = PV_avg_annual_kwh/PV_year_one_kwh
            else:
                PV_year_one_to_avg_annual = 1
            PV_avg_annual_kwh_to_batt = PV_year_one_to_avg_annual*sum(d['outputs']['Scenario']['Site']['PV']['year_one_to_battery_series_kw'])
            PV_avg_annual_kwh_curtailed = PV_year_one_to_avg_annual*sum(d['outputs']['Scenario']['Site']['PV']['year_one_curtailed_production_series_kw'])

            Wind_avg_annual_kwh = d['outputs']['Scenario']['Site']['Wind']['average_yearly_energy_produced_kwh'] or 0.0
            Wind_avg_annual_kwh_exports = d['outputs']['Scenario']['Site']['Wind']['average_yearly_energy_exported_kwh'] or 0.0
            Wind_year_one_kwh = d['outputs']['Scenario']['Site']['Wind']['year_one_energy_produced_kwh'] or 0.0
            Wind_year_one_to_avg_annual = 1
            if Wind_year_one_kwh is None:
                Wind_avg_annual_kwh = 0
            elif Wind_year_one_kwh > 0:
                Wind_year_one_to_avg_annual = Wind_avg_annual_kwh/Wind_year_one_kwh
            Wind_avg_annual_kwh_to_batt = Wind_year_one_to_avg_annual*sum(d['outputs']['Scenario']['Site']['Wind']['year_one_to_battery_series_kw'])
            Wind_avg_annual_kwh_curtailed = Wind_year_one_to_avg_annual*sum(d['outputs']['Scenario']['Site']['Wind']['year_one_curtailed_production_series_kw'])
            
            chp_fuel_pct_RE_input = d['inputs']['Scenario']['Site']['FuelTariff']['chp_fuel_percent_RE'] or 0.0
            chp_annual_elec_total_kwh = d['outputs']['Scenario']['Site']['CHP']['year_one_electric_energy_produced_kwh'] or 0.0
            chp_annual_elec_to_batt_kwh = sum(d['outputs']['Scenario']['Site']['CHP']['year_one_to_battery_series_kw']) or 0.0
            chp_annual_elec_to_grid_kwh = sum(d['outputs']['Scenario']['Site']['CHP']['year_one_to_grid_series_kw']) or 0.0
            chp_annual_RE_elec_total_kwh = chp_fuel_pct_RE_input * chp_annual_elec_total_kwh or 0.0
            chp_annual_RE_elec_to_batt_kwh = chp_fuel_pct_RE_input * chp_annual_elec_to_batt_kwh or 0.0
            
            chp_therm_to_steamturbine = sum(d['outputs']['Scenario']['Site']['CHP']['year_one_thermal_to_steamturbine_series_mmbtu_per_hour']) or 0.0
            newboiler_therm_to_steamturbine = sum(d['outputs']['Scenario']['Site']['NewBoiler']['year_one_thermal_to_steamturbine_series_mmbtu_per_hour']) or 0.0
            newboiler_fuel_pct_RE_input = d['inputs']['Scenario']['Site']['FuelTariff']['newboiler_fuel_percent_RE'] or 0.0
            if chp_therm_to_steamturbine + newboiler_therm_to_steamturbine != 0:
                steamturbine_pct_RE_actual = (chp_fuel_pct_RE_input * chp_therm_to_steamturbine \
                    + newboiler_fuel_pct_RE_input*newboiler_therm_to_steamturbine) \
                    / (chp_therm_to_steamturbine + newboiler_therm_to_steamturbine)
            else:
                steamturbine_pct_RE_actual = 0.0
            steamturbine_pct_RE_estimated = (newboiler_fuel_pct_RE_input + chp_fuel_pct_RE_input)/2 #steamturbine pct RE estimated as average of all techs that feed steam to steamturbine
            steamturbine_annual_elec_total_kwh = d['outputs']['Scenario']['Site']['SteamTurbine']['year_one_electric_energy_produced_kwh'] or 0.0
            steamturbine_annual_elec_to_batt_kwh = sum(d['outputs']['Scenario']['Site']['SteamTurbine']['year_one_to_battery_series_kw']) or 0.0
            steamturbine_annual_elec_to_grid_kwh = sum(d['outputs']['Scenario']['Site']['SteamTurbine']['year_one_to_grid_series_kw']) or 0.0
            steamturbine_annual_RE_elec_total_kwh = steamturbine_pct_RE_actual * steamturbine_annual_elec_total_kwh or 0.0
            steamturbine_annual_RE_elec_to_batt_kwh = steamturbine_pct_RE_estimated * steamturbine_annual_elec_to_batt_kwh or 0.0

            Batt_eff = d['inputs']['Scenario']['Site']['Storage']['rectifier_efficiency_pct'] \
                * d['inputs']['Scenario']['Site']['Storage']['inverter_efficiency_pct'] \
                * d['inputs']['Scenario']['Site']['Storage']['internal_efficiency_pct'] 
                                        
            RE_elec_tot_kwh_calced = PV_avg_annual_kwh + Wind_avg_annual_kwh + chp_annual_RE_elec_total_kwh + steamturbine_annual_RE_elec_total_kwh \
                - (1-Batt_eff)*(PV_avg_annual_kwh_to_batt + Wind_avg_annual_kwh_to_batt + chp_annual_RE_elec_to_batt_kwh + steamturbine_annual_RE_elec_to_batt_kwh) \
                - (PV_avg_annual_kwh_curtailed + Wind_avg_annual_kwh_curtailed) \
                
            if include_exported_RE_in_total[i] is False:
                RE_elec_tot_kwh_calced -= PV_avg_annual_kwh_exports + Wind_avg_annual_kwh_exports + chp_annual_elec_to_grid_kwh + steamturbine_annual_elec_to_grid_kwh

            RE_elec_tot_kwh_pct_diff = (RE_elec_tot_kwh_calced - RE_elec_kwh_out)/RE_elec_kwh_out
            self.assertAlmostEquals(RE_elec_tot_kwh_pct_diff,0.0,places=1) #(<5% error) 

            ## RE Heat tests
            if i ==2: # only test RE heat for 
                # Year 1 RE heat calcs - BAU case
                RE_heat_bau_pct_out = d['outputs']['Scenario']['Site']['year_one_renewable_heat_pct_bau'] 
                RE_heat_bau_mmbtu_out = d['outputs']['Scenario']['Site']['year_one_renewable_heat_mmbtu_bau']
                total_heat_bau_mmbtu_out = d['outputs']['Scenario']['Site']['year_one_heat_load_mmbtu_bau']
                if RE_heat_bau_mmbtu_out != 0:
                    RE_heat_bau_diff = (RE_heat_bau_mmbtu_out - total_heat_bau_mmbtu_out*RE_heat_bau_pct_out)/RE_heat_bau_mmbtu_out
                    self.assertAlmostEquals(RE_heat_bau_diff,0.0,places=1)
                # Year 1 RE heat - non-BAU case
                RE_heat_pct_out = d['outputs']['Scenario']['Site']['year_one_renewable_heat_pct']
                RE_heat_mmbtu_out = d['outputs']['Scenario']['Site']['year_one_renewable_heat_mmbtu']
                total_heat_mmbtu_out = d['outputs']['Scenario']['Site']['year_one_heat_load_mmbtu']
                if RE_heat_mmbtu_out != 0:
                    RE_heat_diff = (RE_heat_mmbtu_out - total_heat_mmbtu_out*RE_heat_pct_out)/RE_heat_mmbtu_out
                    self.assertAlmostEquals(RE_heat_diff,0.0,places=1)
                                    
            ## Emissions tests
            # BAU emissions:
            # check pre-processed year 1 bau CO2 emissions calcs vs year 1 bau CO2 emissions output
            year_one_emissions_bau_tCO2_out = d['outputs']['Scenario']['Site']['year_one_emissions_tCO2_bau']
            year_one_emissions_bau_tCO2_in = d['outputs']['Scenario']['Site']['preprocessed_BAU_year_one_emissions_tCO2']
            year_one_emissions_bau_preprocess_pct_diff = (year_one_emissions_bau_tCO2_out-year_one_emissions_bau_tCO2_in)/year_one_emissions_bau_tCO2_out
            self.assertAlmostEquals(year_one_emissions_bau_preprocess_pct_diff,0.0,places=2) #(<0.5% error) 
            # check pre-processed lifecycle bau CO2 emissions calcs vs lifecycle bau CO2 emissions output
            lifecycle_emissions_bau_tCO2_out = d['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2_bau']
            lifecycle_emissions_bau_tCO2_in = d['outputs']['Scenario']['Site']['preprocessed_BAU_lifecycle_emissions_tCO2']
            lifecycle_emissions_bau_preprocess_pct_diff = (lifecycle_emissions_bau_tCO2_out-lifecycle_emissions_bau_tCO2_in)/lifecycle_emissions_bau_tCO2_out
            self.assertAlmostEquals(lifecycle_emissions_bau_preprocess_pct_diff,0.0,places=2) #(<0.5% error) 
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
            # TODO: update test on breakeven cost of emissions reduction, pending finalizing that calculation with PWFs
            yr1_cost_ER_usd_per_tCO2_out = d['outputs']['Scenario']['Site']['breakeven_cost_of_emissions_reduction_us_dollars_per_tCO2'] 
            self.assertAlmostEquals(yr1_cost_ER_usd_per_tCO2_out,0.0,places=1)
            
            ### test specific values:                         
            if i ==0: # Scenario 1
                # system sizes
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['PV']['size_kw'],46.2788,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Wind']['size_kw'],10.0,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kw'],2.4303,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Storage']['size_kwh'],6.062,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Generator']['size_kw'],22.0,places=0)
                # NPV
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Financial']['npv_us_dollars'],-101278.0,places=0)
                # Renewable energy
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_electricity_pct'],0.8,places=3)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_electricity_kwh'],75140.37,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_electricity_pct_bau'],0.146395,places=3)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_electricity_kwh_bau'],10193.12,places=0)
                # CO2 emissions - totals, from grid, from fuelburn, ER, $/tCO2 breakeven
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['preprocessed_BAU_year_one_emissions_tCO2'],40.54,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['preprocessed_BAU_lifecycle_emissions_tCO2'],717.86,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_reduction_CO2_pct'],0.660013,places=3)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['breakeven_cost_of_emissions_reduction_us_dollars_per_tCO2'],0.0,places=3)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_tCO2'],12.79,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_tCO2_bau'],40.54,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2'],7.65,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2_bau'],0.0,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2'],7070.97,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2_bau'],21098.48,places=0)
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
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Financial']['npv_us_dollars'],-198934.0,places=0)
                # Renewable energy
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_electricity_pct'],0.78984,places=3)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_electricity_kwh'],78984.01,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_electricity_pct_bau'],0.135426,places=3)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_electricity_kwh_bau'],13542.62,places=0)
                # CO2 emissions - totals, from grid, from fuelburn, ER, $/tCO2 breakeven
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['preprocessed_BAU_year_one_emissions_tCO2'],57.97,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['preprocessed_BAU_lifecycle_emissions_tCO2'],1026.65,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_reduction_CO2_pct'],0.8,places=3)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['breakeven_cost_of_emissions_reduction_us_dollars_per_tCO2'],0.0,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_tCO2'],11.59,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_tCO2_bau'],57.97,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2'],0.0,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2_bau'],0.0,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2'],6034.79,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2_bau'],30173.96,places=0)
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
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['SteamTurbine']['size_kw'],1411.081,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['NewBoiler']['size_mmbtu_per_hr'],25.088,places=0)
                # NPV
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['Financial']['npv_us_dollars'],10814436.0,places=0)
                # Renewable energy
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_electricity_pct'],0.707555,places=3)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_electricity_kwh'],6207700.8,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_electricity_pct_bau'],0.001534,places=3)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_electricity_kwh_bau'],13454.22,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_heat_pct'],0.499801,places=3)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_heat_mmbtu'],29751251.13,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_heat_pct_bau'],0.0,places=3)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_renewable_heat_mmbtu_bau'],0.0,places=0)
                # CO2 emissions - totals, from grid, from fuelburn, ER, $/tCO2 breakeven
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['preprocessed_BAU_year_one_emissions_tCO2'],5931.31,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['preprocessed_BAU_lifecycle_emissions_tCO2'],133158.25,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_reduction_CO2_pct'],1.282582,places=3)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['breakeven_cost_of_emissions_reduction_us_dollars_per_tCO2'],0.0,places=3)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_tCO2'],-1758.06,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_tCO2_bau'],5931.29,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2'],58.94,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2_bau'],1585.32,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2'],-979477.42,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2_bau'],3424585.89,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2'],-37628.15,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2_bau'],133157.72,places=1)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_from_fuelburn_tCO2'],1473.5,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['lifecycle_emissions_from_fuelburn_tCO2_bau'],39633.01,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_tCO2'],-1817.0,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_tCO2_bau'],4345.97,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['lifecycle_emissions_tCO2'],-39101.64,places=0)
                self.assertAlmostEquals(d['outputs']['Scenario']['Site']['ElectricTariff']['lifecycle_emissions_tCO2_bau'],93524.7,places=0)
                                        
                                        
