from nested_inputs import nested_input_definitions, list_of_float


def list_of_string(input):
    return [str(i) for i in input]

nested_output_definitions = {

    "inputs": nested_input_definitions,

    "outputs": {

        "Scenario": {
            "uuid": {'type': str, "description": "Unique id", "units": 'none'},
            "api_version": {'type': str},
            "status": {'type': str, "description": "Problem Status", "units": 'none'},

            "Site":
            {

                "LoadProfile": {
                    "year_one_electric_load_series_kw": {'type': list_of_float, "description": "Year 1 electric load time series", "units": 'kW'},
                },

                "Financial": {
                    "lcc_us_dollars": {'type': float,  "description": "Lifecycle cost", "units": 'dollars'},
                    "lcc_bau_us_dollars": {'type': float, "description": "Business as usual lifecycle cost", "units": 'dollars'},
                    "npv_us_dollars": {'type': float, "description": "Net present value of system", "units": 'dollars'},
                    "net_capital_costs_plus_om_us_dollars": {'type': float, "description": "Capital cost plus operations and maintenance over project lifetime", "units": '$'},
                },

                "PV": {
                    "size_kw": {'type': float, "description": "Recommended PV system size", "units": 'kW'},
                    "average_yearly_energy_produced_kwh": {'type': float, "description": "Average energy produced by the PV system over one year", "units": 'kWh'},
                    "average_yearly_energy_exported_kwh": {'type': float, "description": "Average annual energy exported by the PV system", "units": 'kWh'},
                    'year_one_energy_produced_kwh': {'type': float, "description": "Year 1 PV energy produced", "units": 'kWh'},
                    'year_one_power_production_series_kw': {'type': list_of_float, "description": "Hourly wolar resource", "units": 'kW'},
                    "year_one_to_battery_series_kw": {'type': list_of_float, "description": "Year 1 PV to battery time series", "units": 'kW'},
                    "year_one_to_load_series_kw": {'type': list_of_float, "description": "Year 1 PV to load time series", "units": 'kW'},
                    "year_one_to_grid_series_kw": {'type': list_of_float, "description": "Year 1 PV to grid time series", "units": 'kW'},
                },

                "Wind": {
                    "size_kw": {'type': float, "description": "Recommended wind system size", "units": 'kW'},
                    "average_yearly_energy_produced_kwh": {'type': float, "description": "Average energy produced by the wind system over one year", "units": 'kWh'},
                    "average_yearly_energy_exported_kwh": {'type': float, "description": "Average annual energy exported by the wind system", "units": 'kWh'},
                    'year_one_energy_produced_kwh': {'type': float, "description": "Year 1 wind energy produced","units": 'kWh'},
                    'year_one_power_production_series_kw': {'type': list_of_float, "description": "Hourly wind resource", "units": 'kW'},
                    "year_one_to_battery_series_kw": {'type': list_of_float, "description": "Year 1 wind to battery time series", "units": 'kW'},
                    "year_one_to_load_series_kw": {'type': list_of_float, "description": "Year 1 wind to load time series", "units": 'kW'},
                    "year_one_to_grid_series_kw": {'type': list_of_float, "description": "Year 1 wind to grid time series", "units": 'kW'},
                },

                "Storage": {
                    "size_kw": {'type': float, "description": "Recommended battery inverter Size", "units": 'kW'},
                    "size_kwh": {'type': float, "description": "Recommended battery capacity", "units": 'kWh'},
                    "year_one_to_load_series_kw": {'type': list_of_float, "description": "Year 1 battery to load time series", "units": 'kW'},
                    "year_one_to_grid_series_kw": {'type': list_of_float, "description": "Year 1 battery to grid time series", "units": 'kW'},
                    "year_one_soc_series_pct": {'type': list_of_float, "description": "Year 1 battery state of charge", "units": '%'},
                },

                "ElectricTariff": {
                    "year_one_energy_cost_us_dollars": {'type': float, "description": "Year 1 utility energy cost", "units": '$'},
                    "year_one_demand_cost_us_dollars": {'type': float, "description": "Year 1 utility demand cost", "units": '$'},
                    "year_one_fixed_cost_us_dollars": {'type': float, "description": "Year 1 utility fixed cost", "units": '$'},
                    "year_one_min_charge_adder_us_dollars": {'type': float, "description": "Year 1 utility minimum charge adder", "units": '$'},
                    "year_one_energy_cost_bau_us_dollars": {'type': float, "description": "Business as usual year 1 utility energy cost", "units": '$'},
                    "year_one_demand_cost_bau_us_dollars": {'type': float, "description": "Business as usual year 1 utility demand cost", "units": '$'},
                    "year_one_fixed_cost_bau_us_dollars": {'type': float, "description": "Business as usual year 1 utility fixed cost", "units": '$'},
                    "year_one_min_charge_adder_bau_us_dollars": {'type': float, "description": "Business as usual year 1 utility minimum charge adder", "units": '$'},
                    "total_energy_cost_us_dollars": {'type': float, "description": "Total utility energy cost over the project lifetime, after-tax", "units": '$'},
                    "total_demand_cost_us_dollars": {'type': float, "description": "Total utility demand cost over the project lifetime, after-tax", "units": '$'},
                    "total_fixed_cost_us_dollars": {'type': float, "description": "Total utility fixed cost over the project lifetime, after-tax", "units": '$'},
                    "total_min_charge_adder_us_dollars": {'type': float, "description": "Total utility minimum charge adder", "units": '$'},
                    "total_energy_cost_bau_us_dollars": {'type': float, "description": "Business as usual total utility energy cost over the project lifetime, after-tax", "units": '$'},
                    "total_demand_cost_bau_us_dollars": {'type': float, "description": "Business as usual total utility demand cost over the project lifetime, after-tax", "units": '$'},
                    "total_fixed_cost_bau_us_dollars" : {'type': float, "description": "Business as usual total utility fixed cost over the project lifetime, after-tax", "units": '$'},
                    "total_min_charge_adder_bau_us_dollars": {'type': float, "description": "Business as usual total utility minimum charge adder", "units": '$'},
                    'year_one_bill_us_dollars': {'type': float, "description": "Year 1 utility Bill", "units": '$'},
                    'year_one_bill_bau_us_dollars': {'type': float, "description": "Business as usual year 1 utility Bill", "units": '$'},
                    'year_one_export_benefit_us_dollars': {'type': float, "description": "Year 1 export benefit", "units": '$'},
                    "year_one_energy_cost_series_us_dollars_per_kwh": {'type': list_of_float, "description": "Year 1 energy cost time series", "units": '$/kWh'},
                    "year_one_demand_cost_series_us_dollars_per_kw": {'type': list_of_float, "description": "Year 1 demand cost time series", "units": '$/kW'},
                    "year_one_to_load_series_kw": {'type': list_of_float, "description": "Year 1 grid to load time series", "units": 'kW'},
                    "year_one_to_battery_series_kw": {'type': list_of_float, "description": "Year 1 grid to battery time series", "units": 'kW'},
                    "year_one_energy_supplied_kwh": {'type': float, "description": "Year 1 energy supplied from the grid", "units": 'kWh'},
                },
            }
        }

    },

    "messages": {
        "warnings": {'type': list_of_string, "description": "Warnings generated by simulation"},
        "error": {'type': str, "description": "Error generated by simulation"}

    }
}