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
        ## inputs
        RE_target_totest = [None, 0.4] 
        include_exported_RE_in_total_totest = [True,False] 
        include_exported_elec_emissions_totest = [True,False]
        include_battery_totest = [True,False] 
        net_metering_limit_totest = [0,1000]
        elec_only_totest = [False] #True = elec only, False = add thermal loads and test CHP w/ TES-HW
        resilience_scenarios_totest = ['no_outage','no_gen','new_gen','existing_gen'] 
        # Note resilience scenarios eliminate the upper limit on RE or ER target, so it's "at least" _% RE or ER, rather than "exactly" (which yields infeasibilities)

        ## runs
        for RE_target in RE_target_totest:
            if RE_target is None:
                ER_target = None #0.8 # note tests with thermal techs use lower ER target (5%) due to limited options to reduce
            else:
                ER_target = None
            for resilience_scenario in resilience_scenarios_totest:
                for include_exported_RE_in_total in include_exported_RE_in_total_totest:
                    for include_exported_elec_emissions_in_total in include_exported_elec_emissions_totest:
                        for include_battery in include_battery_totest:
                            for net_metering_limit in net_metering_limit_totest:
                                for elec_only in elec_only_totest:
                                    print("RE_target: ",RE_target,", ",\
                                        "ER_target: ",ER_target,", ",\
                                        "resilience_scenario: ",resilience_scenario,", "\
                                        "include_exported_RE_in_total: ",include_exported_RE_in_total,", ",\
                                        "include_exported_elec_emissions_in_total: ",include_exported_elec_emissions_in_total,", ",\
                                        "include_battery: ",include_battery,", ",\
                                        "net_metering_limit: ",net_metering_limit,",",\
                                        "elec_only: ",elec_only,'\n')
                                    
                                    # inputs - automated:
                                    annual_typical_elec_load_kwh = 100000
                                    annual_heat_load_mmbtu = 1000      
                                    nat_gas_dollars_per_mmbtu = 3 # model uses this for chp fuel price, 2x this for boiler (to incentivize CHP in this test) 
                                    chp_fuel_pct_RE_input = 0.5
                                    boiler_fuel_pct_RE_input = 0.1

                                    # test posts  
                                    # techs and load profiles  
                                    if elec_only == True: 
                                        nested_data = json.load(open(self.test_post_elec_only, 'rb'))
                                        nested_data['Scenario']['Site']['Wind']['max_kw'] = 100
                                    else:
                                        nested_data = json.load(open(self.test_post_with_thermal, 'rb'))
                                        nested_data['Scenario']['Site']['LoadProfileBoilerFuel']['annual_mmbtu'] = annual_heat_load_mmbtu
                                        nested_data['Scenario']['Site']['FuelTariff']['boiler_fuel_blended_annual_rates_us_dollars_per_mmbtu'] = 2*nat_gas_dollars_per_mmbtu
                                        nested_data['Scenario']['Site']['FuelTariff']['chp_fuel_blended_annual_rates_us_dollars_per_mmbtu'] = nat_gas_dollars_per_mmbtu
                                        nested_data['Scenario']['Site']['FuelTariff']['boiler_fuel_percent_RE'] = boiler_fuel_pct_RE_input
                                        nested_data['Scenario']['Site']['FuelTariff']['chp_fuel_percent_RE'] = chp_fuel_pct_RE_input
                                        nested_data['Scenario']['Site']['CHP']['min_kw'] = 50
                                        nested_data['Scenario']['Site']['CHP']['max_kw'] = 50
                                        nested_data['Scenario']['Site']['HotTES']['max_gal'] = 0
                                        nested_data['Scenario']['Site']['Wind']['max_kw'] = 0
                                    
                                    nested_data['Scenario']['Site']['LoadProfile']['annual_kwh'] = annual_typical_elec_load_kwh
                                    nested_data['Scenario']['Site']['include_exported_renewable_electricity_in_total'] = include_exported_RE_in_total
                                    nested_data['Scenario']['Site']['include_exported_elec_emissions_in_total'] = include_exported_elec_emissions_in_total
                                    nested_data['Scenario']['Site']['ElectricTariff']['net_metering_limit_kw'] = net_metering_limit
                                    nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
                                    
                                    if include_battery == True:
                                        nested_data['Scenario']['Site']['Storage']['max_kw'] = 10000.0
                                        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 100000.0
                                    elif include_battery == False:
                                        nested_data['Scenario']['Site']['Storage']['max_kw'] = 0
                                        nested_data['Scenario']['Site']['Storage']['max_kwh'] = 0                                    
                                    
                                    # add RE/ER targets
                                    if RE_target is not None:
                                        nested_data['Scenario']['Site']['renewable_electricity_min_pct'] = RE_target
                                        if elec_only == True:
                                            nested_data['Scenario']['Site']['renewable_electricity_max_pct'] = RE_target
                                    if ER_target is not None:
                                        if elec_only == True:
                                            nested_data['Scenario']['Site']['co2_emissions_reduction_min_pct'] = ER_target
                                            if resilience_scenario == 'no_outage': 
                                                nested_data['Scenario']['Site']['co2_emissions_reduction_max_pct'] = ER_target
                                        elif elec_only == False:
                                            nested_data['Scenario']['Site']['co2_emissions_reduction_min_pct'] = 0.05 
                                            #using lower ER target for scenarios with thermal techs due to lack of options (until GHP is added) for reducing thermal emissions 
                                    
                                    # add outage for resilience scenarios
                                    if resilience_scenario != 'no_outage': 
                                        outage_start_hour = 4032
                                        outage_duration = 2000 #hrs
                                        nested_data['Scenario']['Site']['LoadProfile']['outage_start_hour'] = outage_start_hour 
                                        nested_data['Scenario']['Site']['LoadProfile']['outage_end_hour'] = outage_start_hour + outage_duration
                                        nested_data['Scenario']['Site']['renewable_electricity_max_pct'] = None
                                        nested_data['Scenario']['Site']['co2_emissions_reduction_max_pct'] = None
                                        if resilience_scenario == 'new_gen':
                                            nested_data['Scenario']['Site']['Generator']['max_kw'] = 20
                                            nested_data['Scenario']['Site']['Generator']['fuel_avail_gal'] = 1000
                                        elif resilience_scenario == 'existing_gen':
                                            nested_data['Scenario']['Site']['Generator']['existing_kw'] = 5
                                            nested_data['Scenario']['Site']['Generator']['fuel_avail_gal'] = 1000

                                    # post & poll:
                                    resp = self.get_response(data=nested_data)
                                    self.assertHttpCreated(resp)
                                    r = json.loads(resp.content)
                                    run_uuid = r.get('run_uuid')
                                    d = ModelManager.make_response(run_uuid=run_uuid)

                                    ## check results - automated:

                                    ## print system sizes
                                    print('optimization status: ',d['outputs']['Scenario']['status'])
                                    print('PV kW: ',round(d['outputs']['Scenario']['Site']['PV']['size_kw'],2))
                                    print('Wind kW: ',round(d['outputs']['Scenario']['Site']['Wind']['size_kw'],2))
                                    print('Batt kW: ',round(d['outputs']['Scenario']['Site']['Storage']['size_kw'],2))
                                    print('Batt kWh: ',round(d['outputs']['Scenario']['Site']['Storage']['size_kwh'],2))
                                    print('Generator kW: ',round(d['outputs']['Scenario']['Site']['Generator']['size_kw'],2))
                                    print('CHP kW: ',round(d['outputs']['Scenario']['Site']['CHP']['size_kw'],2))
                                    print('AbsChl ton: ',round(d['outputs']['Scenario']['Site']['AbsorptionChiller']['size_ton'],2))
                                    print('ColdTES gal: ',round(d['outputs']['Scenario']['Site']['ColdTES']['size_gal'],2))
                                    print('HotTES gal: ',round(d['outputs']['Scenario']['Site']['HotTES']['size_gal'],2))
                                    
                                    ## calculate BAU and non-BAU annual load:
                                    if resilience_scenario == 'no_outage': 
                                        annual_elec_load_kwh = annual_typical_elec_load_kwh
                                        annual_elec_load_kwh_bau = annual_typical_elec_load_kwh
                                    else:
                                        bau_sustained_time_steps = d['outputs']['Scenario']['Site']['LoadProfile']['bau_sustained_time_steps'] # note hourly timesteps for this test
                                        loads_kw = d['outputs']['Scenario']['Site']['LoadProfile']['year_one_electric_load_series_kw']
                                        critical_loads_kw = d['outputs']['Scenario']['Site']['LoadProfile']['critical_load_series_kw']
                                        annual_elec_load_kwh = sum(loads_kw)
                                        annual_elec_load_kwh_bau = sum(loads_kw) - sum(loads_kw[outage_start_hour-1:outage_start_hour+outage_duration-1]) + \
                                            sum(critical_loads_kw[outage_start_hour-1:outage_start_hour-1+min(bau_sustained_time_steps,outage_duration)])
                                    
                                    ## RE tests
                                    # Year 1 RE elec - BAU case:
                                    RE_elec_bau_pct_out = d['outputs']['Scenario']['Site']['year_one_renewable_electricity_pct_bau'] or 0.0
                                    RE_elec_bau_kwh_out = d['outputs']['Scenario']['Site']['year_one_renewable_electricity_kwh_bau'] or 0.0
                                    RE_elec_bau_kwh_pct_diff = (annual_elec_load_kwh_bau*RE_elec_bau_pct_out - RE_elec_bau_kwh_out)/RE_elec_bau_kwh_out
                                    self.assertAlmostEquals(RE_elec_bau_kwh_pct_diff,0.0,places=2) # <0.5% error
                                    # Year 1 RE elec - non-BAU case:
                                    RE_elec_pct_out = d['outputs']['Scenario']['Site']['year_one_renewable_electricity_pct'] or 0.0
                                    if RE_target is not None:
                                        if resilience_scenario == 'no_outage':
                                            self.assertAlmostEquals(RE_elec_pct_out,RE_target,places=3)
                                        else:
                                            self.assertFalse(RE_elec_pct_out < RE_target) # RE_pct_out should be >= RE_target
                                    RE_elec_kwh_out = d['outputs']['Scenario']['Site']['year_one_renewable_electricity_kwh'] or 0.0
                                    RE_elec_kwh_pct_diff = (annual_elec_load_kwh*RE_elec_pct_out - RE_elec_kwh_out)/RE_elec_kwh_out
                                    self.assertAlmostEquals(RE_elec_kwh_pct_diff,0.0,places=2)
                                    # check RE elec export credit accounting
                                    PV_avg_annual_kwh = d['outputs']['Scenario']['Site']['PV']['average_yearly_energy_produced_kwh']
                                    PV_avg_annual_kwh_exports = d['outputs']['Scenario']['Site']['PV']['average_yearly_energy_exported_kwh']
                                    PV_year_one_kwh = d['outputs']['Scenario']['Site']['PV']['year_one_energy_produced_kwh']
                                    if PV_year_one_kwh > 0:
                                        PV_year_one_to_avg_annual = PV_avg_annual_kwh/PV_year_one_kwh
                                    else:
                                        PV_year_one_to_avg_annual = 1
                                    PV_avg_annual_kwh_to_batt = PV_year_one_to_avg_annual*sum(d['outputs']['Scenario']['Site']['PV']['year_one_to_battery_series_kw'])
                                    PV_avg_annual_kwh_curtailed = PV_year_one_to_avg_annual*sum(d['outputs']['Scenario']['Site']['PV']['year_one_curtailed_production_series_kw'])

                                    Wind_avg_annual_kwh = d['outputs']['Scenario']['Site']['Wind']['average_yearly_energy_produced_kwh'] or 0.0
                                    Wind_avg_annual_kwh_exports = d['outputs']['Scenario']['Site']['Wind']['average_yearly_energy_exported_kwh']
                                    Wind_year_one_kwh = d['outputs']['Scenario']['Site']['Wind']['year_one_energy_produced_kwh']
                                    Wind_year_one_to_avg_annual = 1
                                    if Wind_year_one_kwh is None:
                                        Wind_avg_annual_kwh = 0
                                    elif Wind_year_one_kwh > 0:
                                        Wind_year_one_to_avg_annual = Wind_avg_annual_kwh/Wind_year_one_kwh
                                    Wind_avg_annual_kwh_to_batt = Wind_year_one_to_avg_annual*sum(d['outputs']['Scenario']['Site']['Wind']['year_one_to_battery_series_kw'])
                                    Wind_avg_annual_kwh_curtailed = Wind_year_one_to_avg_annual*sum(d['outputs']['Scenario']['Site']['Wind']['year_one_curtailed_production_series_kw'])
                                    
                                    CHP_fuel_percent_RE_check = d['inputs']['Scenario']['Site']['FuelTariff']['chp_fuel_percent_RE']
                                    boiler_fuel_percent_RE_check = d['inputs']['Scenario']['Site']['FuelTariff']['boiler_fuel_percent_RE']
                                    self.assertAlmostEquals(CHP_fuel_percent_RE_check,chp_fuel_pct_RE_input,places=3) 
                                    self.assertAlmostEquals(boiler_fuel_percent_RE_check,boiler_fuel_pct_RE_input,places=3)  
                                    CHP_annual_elec_kwh = d['outputs']['Scenario']['Site']['CHP']['year_one_electric_energy_produced_kwh']
                                    CHP_annual_elec_kwh_to_batt = sum(d['outputs']['Scenario']['Site']['CHP']['year_one_to_battery_series_kw'])
                                    CHP_annual_RE_elec_kwh = CHP_fuel_percent_RE_check*CHP_annual_elec_kwh
                                    CHP_annual_RE_elec_kwh_to_batt = CHP_fuel_percent_RE_check*CHP_annual_elec_kwh_to_batt 

                                    Batt_eff = d['inputs']['Scenario']['Site']['Storage']['rectifier_efficiency_pct'] \
                                        * d['inputs']['Scenario']['Site']['Storage']['inverter_efficiency_pct'] \
                                        * d['inputs']['Scenario']['Site']['Storage']['internal_efficiency_pct'] 
                                    
                                    RE_tot_kwh_calced = PV_avg_annual_kwh + Wind_avg_annual_kwh + CHP_annual_RE_elec_kwh \
                                        - (1-Batt_eff)*(PV_avg_annual_kwh_to_batt+Wind_avg_annual_kwh_to_batt + CHP_annual_RE_elec_kwh_to_batt) \
                                        - (PV_avg_annual_kwh_curtailed + Wind_avg_annual_kwh_curtailed)
                                    if include_exported_RE_in_total is False:
                                        RE_tot_kwh_calced -= PV_avg_annual_kwh_exports + Wind_avg_annual_kwh_exports

                                    RE_tot_kwh_pct_diff = (RE_tot_kwh_calced - RE_elec_kwh_out)/RE_tot_kwh_calced
                                    self.assertAlmostEquals(RE_tot_kwh_pct_diff,0.0,places=1) #(<5% error) 

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
                                    if ER_target is not None:
                                        self.assertAlmostEquals(ER_target, d['inputs']['Scenario']['Site']['co2_emissions_reduction_min_pct'])
                                        if resilience_scenario == 'no_outage':
                                            self.assertAlmostEquals(ER_pct_out,ER_target,places=3)
                                        else:
                                            self.assertFalse(ER_pct_out < ER_target) # ER_pct_out should be >= ER_target
                                    lifecycle_emissions_tCO2_out = d['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2']
                                    lifecycle_emissions_bau_tCO2_out = d['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2_bau']
                                    ER_pct_calced_out = (lifecycle_emissions_bau_tCO2_out-lifecycle_emissions_tCO2_out)/lifecycle_emissions_bau_tCO2_out
                                    ER_pct_diff = abs(ER_pct_calced_out-ER_pct_out)
                                    self.assertAlmostEquals(ER_pct_diff,0.0,places=2) #within 1% of each other
                                    # Year 1 emissions - non-BAU case:
                                    year_one_emissions_tCO2_out = d['outputs']['Scenario']['Site']['year_one_emissions_tCO2']
                                    yr1_fuel_emissions_tCO2 = d['outputs']['Scenario']['Site']['Generator']['year_one_emissions_tCO2'] or 0.0
                                    if elec_only == 0:
                                        yr1_fuel_emissions_tCO2 += d['outputs']['Scenario']['Site']['CHP']['year_one_emissions_tCO2'] or 0.0
                                        yr1_fuel_emissions_tCO2 += d['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_tCO2'] or 0.0
                                    yr1_fuel_emissions_output_total_tCO2 = d['outputs']['Scenario']['Site']['year_one_emissions_from_fuelburn_tCO2'] or 0.0
                                    self.assertAlmostEquals(yr1_fuel_emissions_tCO2,yr1_fuel_emissions_output_total_tCO2,places=-1)
                                    yr1_grid_emissions_tCO2 = d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_gross_tCO2'] or 0.0
                                    yr1_total_emissions_calced_tCO2 = yr1_fuel_emissions_tCO2 + yr1_grid_emissions_tCO2 
                                    yr1_RE_exported_emissions_offset_tCO2 = d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_offset_from_elec_exports_tCO2'] or 0.0
                                    if include_exported_elec_emissions_in_total:
                                        yr1_total_emissions_calced_tCO2 += -1*yr1_RE_exported_emissions_offset_tCO2
                                    self.assertAlmostEquals(year_one_emissions_tCO2_out,yr1_total_emissions_calced_tCO2,places=-1)
                                    # Breakeven cost of emissions reductions 
                                    # TODO: update test on breakeven cost of emissions reduction, pending finalizing that calculation with PWFs
                                    yr1_cost_ER_usd_per_tCO2_out = d['outputs']['Scenario']['Site']['breakeven_cost_of_emissions_reduction_us_dollars_per_tCO2'] 
                                    self.assertAlmostEquals(yr1_cost_ER_usd_per_tCO2_out,0.0,places=1)
                                    # RE heat calcs- annual_calculated_boiler_fuel_load_mmbtu_bau
                                    if elec_only == False:
                                        # Year 1 RE heat calcs - BAU case
                                        RE_heat_bau_pct_out = d['outputs']['Scenario']['Site']['year_one_renewable_heat_pct_bau']
                                        RE_heat_bau_mmbtu_out = d['outputs']['Scenario']['Site']['year_one_renewable_heat_mmbtu_bau']
                                        total_heat_bau_mmbtu_out = d['outputs']['Scenario']['Site']['year_one_heat_load_mmbtu_bau']
                                        self.assertAlmostEquals(total_heat_bau_mmbtu_out*RE_heat_bau_pct_out,RE_heat_bau_mmbtu_out,places=-1)
                                        # Year 1 RE heat - non-BAU case
                                        RE_heat_pct_out = d['outputs']['Scenario']['Site']['year_one_renewable_heat_pct']
                                        RE_heat_mmbtu_out = d['outputs']['Scenario']['Site']['year_one_renewable_heat_mmbtu']
                                        total_heat_mmbtu_out = d['outputs']['Scenario']['Site']['year_one_heat_load_mmbtu']
                                        self.assertAlmostEquals(total_heat_mmbtu_out*RE_heat_pct_out,RE_heat_mmbtu_out,places=-1)
                                        

