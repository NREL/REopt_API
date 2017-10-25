from nested_inputs import nested_input_definitions, list_of_float


def list_of_string(input):
    return [str(i) for i in input]

nested_output_definitions = {

    "Input": nested_input_definitions,

    "Output": {

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
                    "lcc_us_dollars": {'type': float,  "description": "Lifecycle Cost", "units": 'dollars'},
                    "lcc_bau_us_dollars": {'type': float, "description": "Lifecycle Cost", "units": 'dollars'},
                    "npv_us_dollars": {'type': float, "description": "Net Present  Value of System", "units": 'dollars'},
                    "net_capital_costs_plus_om_us_dollars": {'type': float, "description": "Capital Cost plus Operations and Maintenance over Project Lifetime", "units": '$'},
                },

                "PV": {
                    "size_kw": {'type': float, "description": "Recommended PV System Size", "units": 'kW'},
                    "average_yearly_energy_produced_kwh": {'type': float, "description": "Average energy produced by the PV system over one year", "units": 'kWh'},
                    "average_yearly_energy_exported_kwh": {'type': float, "description": "Average annual energy exported by the PV system", "units": 'kWh'},
                    'year_one_energy_produced_kwh': {'type': float, "description": "PV energy produced in year 1", "units": 'kWh'},
                    'year_one_power_production_series_kw': {'type': list_of_float, "description": "Hourly Solar Resource", "units": 'kW'},
                    "year_one_to_battery_series_kw": {'type': list_of_float, "description": "Year 1 PV to battery time series", "units": 'kW'},
                    "year_one_to_load_series_kw": {'type': list_of_float, "description": "Year 1 PV to load time series", "units": 'kW'},
                    "year_one_to_grid_series_kw": {'type': list_of_float, "description": "Year 1 PV to grid time series", "units": 'kW'},
                },

                "Wind": {
                    "size_kw": {'type': float, "description": "Recommended Wind System Size", "units": 'kW'},
                    "average_yearly_energy_produced_kwh": {'type': float, "description": "Average energy produced by the wind system over one year", "units": 'kWh'},
                    "average_yearly_energy_exported_kwh": {'type': float, "description": "Average annual energy exported by the Wind system", "units": 'kWh'},
                    'year_one_energy_produced_kwh': {'type': float, "description": "Wind energy produced in year 1","units": 'kWh'},
                    'year_one_power_production_series_kwh': {'type': list_of_float, "description": "Hourly Wind Resource", "units": 'kW'},
                    "year_one_to_battery_series_kw": {'type': list_of_float, "description": "Year 1 wind to battery time series", "units": 'kW'},
                    "year_one_to_load_series_kw": {'type': list_of_float, "description": "Year 1 wind to load time series", "units": 'kW'},
                    "year_one_to_grid_series_kw": {'type': list_of_float, "description": "Year 1 wind to grid time series", "units": 'kW'},
                },

                "Storage": {
                    "size_kw": {'type': float, "description": "Recommended Battery Inverter Size", "units": 'kW'},
                    "size_kwh": {'type': float, "description": "Recommended Battery Size", "units": 'kWh'},
                    "year_one_to_load_series_kw": {'type': list_of_float, "description": "Year 1 battery to load time series", "units": 'kW'},
                    "year_one_to_grid_series_kw": {'type': list_of_float, "description": "Year 1 battery to grid time series", "units": 'kW'},
                    "year_one_soc_series_pct": {'type': list_of_float, "description": "Year 1 battery state of charge", "units": '%'},
                },

                "ElectricTariff": {
                    "year_one_energy_cost_us_dollars": {'type': float, "description": "Year 1 Utility Energy Cost", "units": '$'},
                    "year_one_demand_cost_us_dollars": {'type': float, "description": "Year 1 Utility Demand Cost", "units": '$'},
                    "year_one_fixed_cost_us_dollars": {'type': float, "description": "Year 1 Utility Fixed Cost", "units": '$'},
                    "year_one_min_charge_adder_us_dollars": {'type': float, "description": "Year 1 Utility Minimum Charge Adder", "units": '$'},
                    "year_one_energy_cost_bau_us_dollars": {'type': float, "description": "Business as Usual Year 1 Utility Energy Cost", "units": '$'},
                    "year_one_demand_cost_bau_us_dollars": {'type': float, "description": "Business as Usual Year 1 Utility Demand Cost", "units": '$'},
                    "year_one_fixed_cost_bau_us_dollars": {'type': float, "description": "Business as Usual Year 1 Utility Fixed Cost", "units": '$'},
                    "year_one_min_charge_adder_bau_us_dollars": {'type': float, "description": "Business as Usual Year 1 Utility Minimum Charge Adder", "units": '$'},
                    "total_energy_cost_us_dollars": {'type': float, "description": "Total Utility Energy Cost over the Project Lifetime, after-tax", "units": '$'},
                    "total_demand_cost_us_dollars": {'type': float, "description": "Total Utility Demand Cost over the Project Lifetime, after-tax", "units": '$'},
                    "total_fixed_cost_us_dollars" : {'type': float, "description": "Total Utility Fixed Cost over the Project Lifetime, after-tax", "units": '$'},
                    "total_min_charge_adder_us_dollars": {'type': float, "description": "Total Utility Minimum Charge Adder", "units": '$'},
                    "total_energy_cost_bau_us_dollars": {'type': float, "description": "Business as Usual Total Utility Energy Cost over the Project Lifetime, after-tax", "units": '$'},
                    "total_demand_cost_bau_us_dollars": {'type': float, "description": "Business as Usual Total Utility Demand Cost over the Project Lifetime, after-tax", "units": '$'},
                    "total_fixed_cost_bau_us_dollars" : {'type': float, "description": "Business as Usual Total Utility Fixed Cost over the Project Lifetime, after-tax", "units": '$'},
                    "total_min_charge_adder_bau_us_dollars": {'type': float, "description": "Business as Usual Total Utility Minimum Charge Adder", "units": '$'},
                    'year_one_bill_us_dollars': {'type': float, "description": "Result - year one bill", "units": '$'},
                    'year_one_bill_bau_us_dollars': {'type': float, "description": "Result - year one bill bau", "units": '$'},
                    'year_one_export_benefit_us_dollars': {'type': float, "description": "Result - total export benefit", "units": '$'},
                    "year_one_energy_cost_series_us_dollars_per_kwh": {'type': list_of_float, "description": "Year 1 energy cost time series", "units": '$/kWh'},
                    "year_one_demand_cost_series_us_dollars_per_kw": {'type': list_of_float, "description": "Year 1 demand cost time series", "units": '$/kW'},
                    "year_one_to_load_series_kw": {'type': list_of_float, "description": "Year 1 grid to load time series", "units": 'kW'},
                    "year_one_to_battery_series_kw": {'type': list_of_float, "description": "Year 1 grid to battery time series", "units": 'kW'},
                    "year_one_energy_supplied_kwh": {'type': float, "description": "Energy Supplied from the Grid", "units": 'kWh'},
                },
            }
        }

    },

    "Messages": {
        "warnings": {'type': list_of_string, "description": "Warnings generated by simulation"},
        "error": {'type': str, "description": "Error generated by simulation"}

    }
}