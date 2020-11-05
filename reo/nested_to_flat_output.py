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
def nested_to_flat(nested_output):
    
    base = {

        'run_uuid': nested_output['Scenario']['run_uuid'],
        'api_version': nested_output['Scenario']['api_version'],
        'status': nested_output['Scenario']['status'],

        'year_one_electric_load_series': nested_output['Scenario']['Site']['LoadProfile']['year_one_electric_load_series_kw'],
        
        'lcc': nested_output['Scenario']['Site']['Financial']['lcc_us_dollars'],
        'lcc_bau': nested_output['Scenario']['Site']['Financial']['lcc_bau_us_dollars'],
        'npv': nested_output['Scenario']['Site']['Financial']['npv_us_dollars'],
        'net_capital_costs_plus_om': nested_output['Scenario']['Site']['Financial']['net_capital_costs_plus_om_us_dollars'],
        'avoided_outage_costs_us_dollars': nested_output['Scenario']['Site']['Financial']['avoided_outage_costs_us_dollars'],
        'microgrid_upgrade_cost_us_dollars': nested_output['Scenario']['Site']['Financial']['microgrid_upgrade_cost_us_dollars'],

        'pv_kw': nested_output['Scenario']['Site']['PV']['size_kw'],
        'year_one_energy_produced': nested_output['Scenario']['Site']['PV']['year_one_energy_produced_kwh'],
        'pv_kw_ac_hourly': nested_output['Scenario']['Site']['PV']['year_one_power_production_series_kw'],
        'average_yearly_pv_energy_produced': nested_output['Scenario']['Site']['PV']['average_yearly_energy_produced_kwh'],
        'average_annual_energy_exported': nested_output['Scenario']['Site']['PV']['average_yearly_energy_exported_kwh'],
        'year_one_pv_to_battery_series': nested_output['Scenario']['Site']['PV']['year_one_to_battery_series_kw'],
        'year_one_pv_to_load_series': nested_output['Scenario']['Site']['PV']['year_one_to_load_series_kw'],
        'year_one_pv_to_grid_series': nested_output['Scenario']['Site']['PV']['year_one_to_grid_series_kw'],
        'existing_pv_om_cost_us_dollars': nested_output['Scenario']['Site']['PV']['existing_pv_om_cost_us_dollars'],
        
        'batt_kw': nested_output['Scenario']['Site']['Storage']['size_kw'],
        'batt_kwh': nested_output['Scenario']['Site']['Storage']['size_kwh'],
        'year_one_battery_to_load_series': nested_output['Scenario']['Site']['Storage']['year_one_to_load_series_kw'],
        'year_one_battery_to_grid_series': nested_output['Scenario']['Site']['Storage']['year_one_to_grid_series_kw'],
        'year_one_battery_soc_series': nested_output['Scenario']['Site']['Storage']['year_one_soc_series_pct'],

        'year_one_energy_cost': nested_output['Scenario']['Site']['ElectricTariff']['year_one_energy_cost_us_dollars'],
        'year_one_demand_cost': nested_output['Scenario']['Site']['ElectricTariff']['year_one_demand_cost_us_dollars'],
        'year_one_fixed_cost': nested_output['Scenario']['Site']['ElectricTariff']['year_one_fixed_cost_us_dollars'],
        'year_one_min_charge_adder': nested_output['Scenario']['Site']['ElectricTariff']['year_one_min_charge_adder_us_dollars'],
        'year_one_energy_cost_bau': nested_output['Scenario']['Site']['ElectricTariff']['year_one_energy_cost_bau_us_dollars'],
        'year_one_demand_cost_bau': nested_output['Scenario']['Site']['ElectricTariff']['year_one_demand_cost_bau_us_dollars'],
        'year_one_fixed_cost_bau': nested_output['Scenario']['Site']['ElectricTariff']['year_one_fixed_cost_bau_us_dollars'],
        'year_one_min_charge_adder_bau': nested_output['Scenario']['Site']['ElectricTariff']['year_one_min_charge_adder_bau_us_dollars'],
        'total_energy_cost': nested_output['Scenario']['Site']['ElectricTariff']['total_energy_cost_us_dollars'],
        'total_demand_cost': nested_output['Scenario']['Site']['ElectricTariff']['total_demand_cost_us_dollars'],
        'total_fixed_cost': nested_output['Scenario']['Site']['ElectricTariff']['total_fixed_cost_us_dollars'],
        'total_min_charge_adder': nested_output['Scenario']['Site']['ElectricTariff']['total_min_charge_adder_us_dollars'],
        'total_energy_cost_bau': nested_output['Scenario']['Site']['ElectricTariff']['total_energy_cost_bau_us_dollars'],
        'total_demand_cost_bau': nested_output['Scenario']['Site']['ElectricTariff']['total_demand_cost_bau_us_dollars'],
        'total_fixed_cost_bau': nested_output['Scenario']['Site']['ElectricTariff']['total_fixed_cost_bau_us_dollars'],
        'total_min_charge_adder_bau': nested_output['Scenario']['Site']['ElectricTariff']['total_min_charge_adder_bau_us_dollars'],
        'year_one_bill': nested_output['Scenario']['Site']['ElectricTariff']['year_one_bill_us_dollars'],
        'year_one_bill_bau': nested_output['Scenario']['Site']['ElectricTariff']['year_one_bill_bau_us_dollars'],
        'year_one_export_benefit': nested_output['Scenario']['Site']['ElectricTariff']['year_one_export_benefit_us_dollars'],
        'year_one_grid_to_load_series': nested_output['Scenario']['Site']['ElectricTariff']['year_one_to_load_series_kw'],
        'year_one_grid_to_battery_series': nested_output['Scenario']['Site']['ElectricTariff']['year_one_to_battery_series_kw'],
        'year_one_energy_cost_series': nested_output['Scenario']['Site']['ElectricTariff']['year_one_energy_cost_series_us_dollars_per_kwh'],
        'year_one_demand_cost_series': nested_output['Scenario']['Site']['ElectricTariff']['year_one_demand_cost_series_us_dollars_per_kw'],
        'year_one_utility_kwh': nested_output['Scenario']['Site']['ElectricTariff']['year_one_energy_supplied_kwh'],
        'year_one_payments_to_third_party_owner': None,
        'total_payments_to_third_party_owner': None
    }
    if nested_output['Scenario']['Site'].get('Wind') is not None:
        base.update({
            'wind_kw':nested_output['Scenario']['Site']['Wind']['size_kw'],
            'average_yearly_wind_energy_produced':nested_output['Scenario']['Site']['Wind']['average_yearly_energy_produced_kwh'],
            'average_annual_energy_exported_wind': nested_output['Scenario']['Site']['Wind']['average_yearly_energy_exported_kwh'],
            'year_one_wind_to_battery_series': nested_output['Scenario']['Site']['Wind']['year_one_to_battery_series_kw'],
            'year_one_wind_to_load_series': nested_output['Scenario']['Site']['Wind']['year_one_to_load_series_kw'],
            'year_one_wind_to_grid_series': nested_output['Scenario']['Site']['Wind']['year_one_to_grid_series_kw']
       })
    if nested_output['Scenario']['Site'].get('Generator') is not None:
        base.update({
            'gen_kw':nested_output['Scenario']['Site']['Generator']['size_kw'],
            'average_yearly_gen_energy_produced':nested_output['Scenario']['Site']['Generator']['average_yearly_energy_produced_kwh'],
            'average_annual_energy_exported_gen': nested_output['Scenario']['Site']['Generator']['average_yearly_energy_exported_kwh'],
            'year_one_gen_to_battery_series': nested_output['Scenario']['Site']['Generator']['year_one_to_battery_series_kw'],
            'year_one_gen_to_load_series': nested_output['Scenario']['Site']['Generator']['year_one_to_load_series_kw'],
            'year_one_gen_to_grid_series': nested_output['Scenario']['Site']['Generator']['year_one_to_grid_series_kw'],
            'fuel_used_gal': nested_output['Scenario']['Site']['Generator']['fuel_used_gal'],
            'existing_gen_total_fixed_om_cost_us_dollars': nested_output['Scenario']['Site']['Generator']['existing_gen_total_fixed_om_cost_us_dollars'],
            'existing_gen_total_variable_om_cost_us_dollars': nested_output['Scenario']['Site']['Generator'][
                'existing_gen_total_variable_om_cost_us_dollars'],
            'total_fuel_cost_us_dollars': nested_output['Scenario']['Site']['Generator'][
                'total_fuel_cost_us_dollars'],
            'gen_total_variable_om_cost_us_dollars': nested_output['Scenario']['Site']['Generator'][
                'total_variable_om_cost_us_dollars'],
            'existing_gen_total_fuel_cost_us_dollars': nested_output['Scenario']['Site']['Generator'][
                'existing_gen_total_fuel_cost_us_dollars'],
       })
    if nested_output['Scenario']['Site'].get('Nuclear') is not None:
        base.update({
            'nuc_kw':nested_output['Scenario']['Site']['Nuclear']['size_kw'],
            'average_yearly_nuc_energy_produced':nested_output['Scenario']['Site']['Nuclear']['average_yearly_energy_produced_kwh'],
            'average_annual_energy_exported_nuc': nested_output['Scenario']['Site']['Nuclear']['average_yearly_energy_exported_kwh'],
            'year_one_nuc_to_battery_series': nested_output['Scenario']['Site']['Nuclear']['year_one_to_battery_series_kw'],
            'year_one_nuc_to_load_series': nested_output['Scenario']['Site']['Nuclear']['year_one_to_load_series_kw'],
            'year_one_nuc_to_grid_series': nested_output['Scenario']['Site']['Nuclear']['year_one_to_grid_series_kw'],
            #'fuel_used_gal': nested_output['Scenario']['Site']['Generator']['fuel_used_gal'],
            'existing_nuc_total_fixed_om_cost_us_dollars': nested_output['Scenario']['Site']['Nuclear']['existing_nuc_total_fixed_om_cost_us_dollars'],
            'existing_nuc_total_variable_om_cost_us_dollars': nested_output['Scenario']['Site']['Nuclear'][
                'existing_nuc_total_variable_om_cost_us_dollars'],
            'total_fuel_cost_us_dollars': nested_output['Scenario']['Site']['Nuclear'][
                'total_fuel_cost_us_dollars'],
            'gen_total_variable_om_cost_us_dollars': nested_output['Scenario']['Site']['Nuclear'][
                'total_variable_om_cost_us_dollars'],
            'existing_gen_total_fuel_cost_us_dollars': nested_output['Scenario']['Site']['Nuclear'][
                'existing_nuc_total_fuel_cost_us_dollars'],
       })
    return base

