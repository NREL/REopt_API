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
        self.test_post = os.path.join('reo', 'tests', 'posts', 're_emissions_POST.json')

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)
    
    def test_RE_and_ER(self):
        '''
        Test structure for RE and emissions targets.
        Runs a sweep of various scenarios () and checks logic of calculations and application of constraints.
        '''
        # inputs
        RE_target_totest = [None, 0.8] ##used for min and max #for test, if RE_target = None, then ER target = 0.4
        include_exported_RE_in_total_totest = [True,False] # [True,False] #[True,False] #,1] #0 or 1
        include_exported_elec_emissions_totest = [True,False] #[True,False]# [True,False] #[0,1] #0 or 1
        no_battery_totest = [0,1] #[0,1] #,1] #0 or 1 (0 = PV+batt, 1 = PV only)
        net_metering_totest = [0,1] #,1] #[0,1] #0 or 1
        elec_only_totest = [1] #0 or 1 (1= true,elec only; 0=not elec only (i.e. elec + thermal))

        # runs
        for RE_target in RE_target_totest:
            if RE_target is None:
                ER_target = 0.8
            else:
                ER_target = None
            for include_exported_RE_in_total in include_exported_RE_in_total_totest:
                for include_exported_elec_emissions_in_total in include_exported_elec_emissions_totest:
                    for no_battery in no_battery_totest:
                        for net_metering in net_metering_totest:
                            for elec_only in elec_only_totest:
                                print(RE_target,", ",\
                                    ER_target,", ",\
                                    include_exported_RE_in_total,", ",\
                                    include_exported_elec_emissions_in_total,", ",\
                                    no_battery,", ",\
                                    net_metering,",",\
                                    elec_only,'\n')
                                # inputs - automated:
                                nested_data = json.load(open(self.test_post, 'rb'))
                                annual_elec_load_kwh = 100000
                                annual_heat_load_mmbtu = 100000      
                                nat_gas_dollars_per_mmbtu = 3     
                                nested_data['Scenario']['Site']['LoadProfile']['annual_kwh'] = annual_elec_load_kwh
                                nested_data['Scenario']['Site']['include_exported_renewable_electricity_in_total'] = include_exported_RE_in_total
                                nested_data['Scenario']['Site']['include_exported_elec_emissions_in_total'] = include_exported_elec_emissions_in_total
                                if RE_target is not None:
                                    nested_data['Scenario']['Site']['renewable_electricity_min_pct'] = RE_target
                                    nested_data['Scenario']['Site']['renewable_electricity_max_pct'] = RE_target
                                if ER_target is not None:
                                    nested_data['Scenario']['Site']['co2_emissions_reduction_min_pct'] = ER_target
                                    nested_data['Scenario']['Site']['co2_emissions_reduction_max_pct'] = ER_target                            
                                if net_metering == 0:
                                    nested_data['Scenario']['Site']['ElectricTariff']['net_metering_limit_kw'] = 0
                                else:
                                    nested_data['Scenario']['Site']['ElectricTariff']['net_metering_limit_kw'] = 100000
                                nested_data['Scenario']['Site']['PV']['existing_kw'] = 10.0
                                nested_data['Scenario']['Site']['Wind']['max_kw'] = 100
                                if no_battery == 0:
                                    nested_data['Scenario']['Site']['Storage']['max_kw'] = 10000.0
                                    nested_data['Scenario']['Site']['Storage']['max_kwh'] = 100000.0
                                elif no_battery == 1:
                                    nested_data['Scenario']['Site']['Storage']['max_kw'] = 0
                                    nested_data['Scenario']['Site']['Storage']['max_kwh'] = 0
                                if elec_only == 0:
                                    nested_data['Scenario']['Site']['LoadProfileBoilerFuel']['annual_mmbtu'] = annual_heat_load_mmbtu
                                    nested_data['Scenario']['Site']['FuelTariff']['boiler_fuel_blended_annual_rates_us_dollars_per_mmbtu'] = nat_gas_dollars_per_mmbtu
                                    nested_data['Scenario']['Site']['FuelTariff']['chp_fuel_blended_annual_rates_us_dollars_per_mmbtu'] = nat_gas_dollars_per_mmbtu
                                    nested_data['Scenario']['Site']['FuelTariff']['boiler_fuel_percent_RE'] = 0.0
                                    nested_data['Scenario']['Site']['FuelTariff']['chp_fuel_percent_RE'] = 0.50
                                    nested_data['Scenario']['Site']['CHP']['max_kw'] = 10000
                                    nested_data['Scenario']['Site']['HotTES']['max_gal'] = 10000
                                #else:
                                #    nested_data['Scenario']['Site']['LoadProfileBoilerFuel']['annual_mmbtu'] = 0
                                #    nested_data['Scenario']['Site']['CHP']['max_kw'] = 0
                                #    nested_data['Scenario']['Site']['HotTES']['max_gal'] = 0

                                # post & poll:
                                resp = self.get_response(data=nested_data)
                                self.assertHttpCreated(resp)
                                r = json.loads(resp.content)
                                run_uuid = r.get('run_uuid')
                                d = ModelManager.make_response(run_uuid=run_uuid)

                                # check results - automated:
                                # print system sizes
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
                                # Year 1 RE elec - BAU case:
                                RE_elec_bau_pct_out = d['outputs']['Scenario']['Site']['year_one_renewable_electricity_bau_pct'] or 0.0
                                RE_elec_bau_kwh_out = d['outputs']['Scenario']['Site']['year_one_renewable_electricity_bau_kwh'] or 0.0
                                self.assertAlmostEquals(annual_elec_load_kwh*RE_elec_bau_pct_out,RE_elec_bau_kwh_out,places=-1)
                                # Year 1 RE elec - non-BAU case:
                                RE_elec_pct_out = d['outputs']['Scenario']['Site']['year_one_renewable_electricity_pct'] or 0.0
                                if RE_target is not None:
                                    self.assertAlmostEquals(RE_elec_pct_out,RE_target,places=3)
                                RE_elec_kwh_out = d['outputs']['Scenario']['Site']['year_one_renewable_electricity_kwh'] or 0.0
                                self.assertAlmostEquals(annual_elec_load_kwh*RE_elec_pct_out,RE_elec_kwh_out,places=-1)
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

                                Wind_avg_annual_kwh = d['outputs']['Scenario']['Site']['Wind']['average_yearly_energy_produced_kwh']
                                Wind_avg_annual_kwh_exports = d['outputs']['Scenario']['Site']['Wind']['average_yearly_energy_exported_kwh']
                                Wind_year_one_kwh = d['outputs']['Scenario']['Site']['Wind']['year_one_energy_produced_kwh']
                                if Wind_year_one_kwh > 0:
                                    Wind_year_one_to_avg_annual = Wind_avg_annual_kwh/Wind_year_one_kwh
                                else:
                                    Wind_year_one_to_avg_annual = 1
                                Wind_avg_annual_kwh_to_batt = Wind_year_one_to_avg_annual*sum(d['outputs']['Scenario']['Site']['Wind']['year_one_to_battery_series_kw'])
                                Wind_avg_annual_kwh_curtailed = Wind_year_one_to_avg_annual*sum(d['outputs']['Scenario']['Site']['Wind']['year_one_curtailed_production_series_kw'])

                                Batt_eff = d['inputs']['Scenario']['Site']['Storage']['rectifier_efficiency_pct'] \
                                    * d['inputs']['Scenario']['Site']['Storage']['inverter_efficiency_pct'] \
                                    * d['inputs']['Scenario']['Site']['Storage']['internal_efficiency_pct'] 
                                
                                RE_tot_kwh_calced = PV_avg_annual_kwh + Wind_avg_annual_kwh \
                                    - (1-Batt_eff)*(PV_avg_annual_kwh_to_batt+Wind_avg_annual_kwh_to_batt) \
                                    - (PV_avg_annual_kwh_curtailed + Wind_avg_annual_kwh_curtailed)
                                if include_exported_RE_in_total is False:
                                    RE_tot_kwh_calced -= PV_avg_annual_kwh_exports + Wind_avg_annual_kwh_exports

                                RE_tot_kwh_pct_diff = (RE_tot_kwh_calced - RE_elec_kwh_out)/RE_tot_kwh_calced
                                self.assertAlmostEquals(RE_tot_kwh_pct_diff,0.0,places=-1) #(<5% error) 

                                # BAU emissions:
                                emissions_bau_lbCO2_out = d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2']
                                emissions_bau_lbCO2_in = d['outputs']['Scenario']['Site']['preprocessed_year_one_emissions_bau_lb_CO2']
                                emissions_bau_preprocess_pct_diff = (emissions_bau_lbCO2_out-emissions_bau_lbCO2_in)/emissions_bau_lbCO2_out
                                self.assertAlmostEquals(emissions_bau_preprocess_pct_diff,0.0,places=2) #(<1.5% error) 
                                # Year 1 emissions reductions:
                                ER_pct_out = d['outputs']['Scenario']['Site']['year_one_CO2_emissions_reduction_pct']
                                if ER_target is not None:
                                    self.assertAlmostEquals(ER_pct_out,ER_target,places=3)
                                emissions_lbCO2_out = d['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2']
                                emissions_bau_lbCO2_out = d['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2']
                                ER_pct_calced_out = (emissions_bau_lbCO2_out-emissions_lbCO2_out)/emissions_bau_lbCO2_out
                                ER_pct_diff = abs(ER_pct_calced_out-ER_pct_out)
                                self.assertAlmostEquals(ER_pct_diff,0.0,places=2) #within 1%
                                # Year 1 emissions - non-BAU case:
                                yr1_fuel_emissions = d['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_CO2'] or 0.0
                                if elec_only == 0:
                                    yr1_fuel_emissions += d['outputs']['Scenario']['Site']['CHP']['year_one_emissions_lb_CO2'] or 0.0
                                    yr1_fuel_emissions += d['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_lb_CO2'] or 0.0
                                yr1_grid_emissions = d['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_CO2'] or 0.0
                                yr1_total_emissions_calced = yr1_fuel_emissions + yr1_grid_emissions 
                                yr1_RE_exported_emissions_offset_lb_CO2 = d['outputs']['Scenario']['Site']['year_one_CO2_emissions_offset_from_elec_exports'] or 0.0
                                if include_exported_elec_emissions_in_total:
                                    yr1_total_emissions_calced += -1*yr1_RE_exported_emissions_offset_lb_CO2
                                self.assertAlmostEquals(emissions_lbCO2_out,yr1_total_emissions_calced,places=-1)
                                # Breakeven cost of emissions reductions 
                                # TODO: update test on breakeven cost of emissions reduction
                                yr1_cost_ER_usd_per_tCO2_out = d['outputs']['Scenario']['Site']['breakeven_cost_of_emissions_reduction_us_dollars_per_ton_CO2'] 
                                #pwf_om_proxy = d['outputs']['Scenario']['Site']['Financial']['total_om_costs_us_dollars'] / \
                                #    d['outputs']['Scenario']['Site']['Financial']['year_one_om_costs_us_dollars']
                                #yr1_cost_ER_usd_per_tCO2_calced = -1 * d['outputs']['Scenario']['Site']['Financial']['npv_us_dollars']/ \
                                #    pwf_om_proxy / ((emissions_bau_lbCO2_out-emissions_lbCO2_out)/2204.62) if emissions_bau_lbCO2_out-emissions_lbCO2_out else 0.0
                                #self.assertAlmostEquals(yr1_cost_ER_usd_per_tCO2_out,yr1_cost_ER_usd_per_tCO2_calced,places=-1)
                                self.assertAlmostEquals(yr1_cost_ER_usd_per_tCO2_out,0.0,places=1)
                                # RE heat calcs
                                if elec_only == 0:
                                    # Year 1 RE heat calcs - BAU case
                                    RE_heat_bau_pct_out = d['outputs']['Scenario']['Site']['year_one_renewable_heat_pct']
                                    RE_heat_bau_mmbtu_out = d['outputs']['Scenario']['Site']['year_one_renewable_heat_mmbtu']
                                    self.assertAlmostEquals(annual_heat_load_mmbtu*RE_heat_bau_pct_out,RE_heat_bau_mmbtu_out,places=-1)
                                    # Year 1 RE heat - non-BAU case
                                    RE_heat_pct_out = d['outputs']['Scenario']['Site']['year_one_renewable_heat_pct']
                                    RE_heat_mmbtu_out = d['outputs']['Scenario']['Site']['year_one_renewable_heat_mmbtu']
                                    self.assertAlmostEquals(annual_heat_load_mmbtu*RE_heat_pct_out,RE_heat_mmbtu_out,places=-1)
                                    

