def nested_to_flat(nested_output):
    
    base = {

        'run_uuid': nested_output['Scenario']['run_uuid'],
        'api_version': nested_output['Scenario']['api_version'],
        'status': nested_output['Scenario']['status'],

        'year_one_electric_load_series': nested_output['Scenario']['Site']['LoadProfile']['year_one_electric_load_series_kw'],
        
        'lcc': nested_output['Scenario']['Site']['Financial']['lcc_us_dollars'],
        'lcc_bau': nested_output['Scenario']['Site']['Financial']['lcc_bau_us_dollars'],
        'npv': nested_output['Scenario']['Site']['Financial']['npv_us_dollars'],
        'irr': nested_output['Scenario']['Site']['Financial'].get('irr_pct'),
        'net_capital_costs_plus_om': nested_output['Scenario']['Site']['Financial']['net_capital_costs_plus_om_us_dollars'],
        
        'pv_kw': nested_output['Scenario']['Site']['PV']['size_kw'],
        'pv_degradation_rate': nested_output['Scenario']['Site']['PV']['degradation_pct'],
        'year_one_energy_produced': nested_output['Scenario']['Site']['PV']['year_one_energy_produced_kwh'],
        'pv_kw_ac_hourly': nested_output['Scenario']['Site']['PV']['year_one_power_production_series_kw'],
        'average_yearly_pv_energy_produced': nested_output['Scenario']['Site']['PV']['average_yearly_energy_produced_kwh'],
        'average_annual_energy_exported': nested_output['Scenario']['Site']['PV']['average_yearly_energy_exported_kwh'],
        'year_one_pv_to_battery_series': nested_output['Scenario']['Site']['PV']['year_one_to_battery_series_kw'],
        'year_one_pv_to_load_series': nested_output['Scenario']['Site']['PV']['year_one_to_load_series_kw'],
        'year_one_pv_to_grid_series': nested_output['Scenario']['Site']['PV']['year_one_to_grid_series_kw'],
        
        'batt_kw':nested_output['Scenario']['Site']['Storage']['size_kw'],
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
        'year_one_utility_kwh':nested_output['Scenario']['Site']['ElectricTariff']['year_one_energy_supplied_kwh'],
        'year_one_payments_to_third_party_owner': None,
        'total_payments_to_third_party_owner': None,
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
    return base

