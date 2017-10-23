from nested_inputs import nested_input_definitions, list_of_float
from datetime import datetime

def list_of_string(input):
    return [str(i) for i in input]

nested_outputs = {

    "Input": {nested_input_definitions},

    "Output": {

        "Scenario": {
            "uuid": {'type': str, "description": "Unique id", "units": 'none'},
            "api_version": {'type': str},
            "status": {'type': str, "description": "Problem Status", "units": 'none'},
            'year_one_datetime_start': {'type': datetime, "description": "Year 1 time start", "units": 'Year/month/day/hour/minute/second'},

        },

        "Financial": {
            "lcc": {'type': float,  "description": "Lifecycle Cost", "units": 'dollars'},
            "lcc_bau": {'type': float, "description": "Lifecycle Cost", "units": 'dollars'},
            "npv": {'type': float, "description": "Net Present  Value of System", "units": 'dollars'},
            "irr": {'type': float, "description": "Internal Rate of Return for System", "units": 'percentage'},
            "net_capital_costs_plus_om": {'type': float, "description": "Capital Cost plus Operations and Maintenance over Project Lifetime", "units": '$'},
        },

        "PV": {
            "size_kw": {'type': float, "description": "Recommended PV System Size", "units": 'kW'},
            "average_yearly_energy_produced": {'type': float, "description": "Average energy produced by the PV system over one year", "units": 'kWh'},
            "average_annual_energy_exported": {'type': float, "description": "Average annual energy exported by the PV system", "units": 'kWh'},
            'year_one_energy_produced': {'type': float, "description": "PV energy produced in year 1", "units": 'kWh'},
            'kw_ac_hourly': {'type': list_of_float, "description": "Hourly Solar Resource", "units": 'kW'},
            'degradation_pct': {'type': float, "description": "PV annual degradation rate", "units": '%/year'},
            'macrs_itc_reduction': {'type': float, "description": "Amount that the MACRS depreciable base is reduced if the ITC is also taken."},

        },

        "Wind": {
            "size_kw": {'type': float, "description": "Recommended Wind System Size", "units": 'kW'},
            "average_yearly_energy_produced": {'type': float, "description": "Average energy produced by the wind system over one year", "units": 'kWh'},
            "average_annual_energy_exported": {'type': float, "description": "Average annual energy exported by the Wind system", "units": 'kWh'},
            'year_one_energy_produced': {'type': float, "description": "Wind energy produced in year 1","units": 'kWh'},
            'kw_ac_hourly': {'type': list_of_float, "description": "Hourly Wind Resource", "units": 'kW'},
        },

        "Storage": {
            "size_kw": {'type': float, "description": "Recommended Battery Inverter Size", "units": 'kW'},
            "size_kwh": {'type': float, "description": "Recommended Battery Size", "units": 'kWh'},
            'macrs_itc_reduction': {'type': float, "description": "Amount that the MACRS depreciable base is reduced if the ITC is also taken."},
        },

        "Grid": {
            "year_one_energy_produced": {'type': float, "description": "Energy Supplied from the Grid", "units": 'kWh'},
        },

        "ElectricTariff": {
            "year_one_energy_cost": {'type': float, "description": "Year 1 Utility Energy Cost", "units": '$'},
            "year_one_demand_cost": {'type': float, "description": "Year 1 Utility Demand Cost", "units": '$'},
            "year_one_fixed_cost": {'type': float, "description": "Year 1 Utility Fixed Cost", "units": '$'},
            "year_one_min_charge_adder": {'type': float, "description": "Year 1 Utility Minimum Charge Adder", "units": '$'},
            "year_one_energy_cost_bau": {'type': float, "description": "Business as Usual Year 1 Utility Energy Cost", "units": '$'},
            "year_one_demand_cost_bau": {'type': float, "description": "Business as Usual Year 1 Utility Demand Cost", "units": '$'},
            "year_one_fixed_cost_bau": {'type': float, "description": "Business as Usual Year 1 Utility Fixed Cost", "units": '$'},
            "year_one_min_charge_adder_bau": {'type': float, "description": "Business as Usual Year 1 Utility Minimum Charge Adder", "units": '$'},
            "total_energy_cost": {'type': float, "description": "Total Utility Energy Cost over the Project Lifetime, after-tax", "units": '$'},
            "total_demand_cost": {'type': float, "description": "Total Utility Demand Cost over the Project Lifetime, after-tax", "units": '$'},
            "total_fixed_cost" : {'type': float, "description": "Total Utility Fixed Cost over the Project Lifetime, after-tax", "units": '$'},
            "total_min_charge_adder": {'type': float, "description": "Total Utility Minimum Charge Adder", "units": '$'},
            "total_energy_cost_bau": {'type': float, "description": "Business as Usual Total Utility Energy Cost over the Project Lifetime, after-tax", "units": '$'},
            "total_demand_cost_bau": {'type': float, "description": "Business as Usual Total Utility Demand Cost over the Project Lifetime, after-tax", "units": '$'},
            "total_fixed_cost_bau" : {'type': float, "description": "Business as Usual Total Utility Fixed Cost over the Project Lifetime, after-tax", "units": '$'},
            "total_min_charge_adder_bau": {'type': float, "description": "Business as Usual Total Utility Minimum Charge Adder", "units": '$'},
            'year_one_bill': {'type': float, "description": "Result - year one bill", "units": 'hours'},
            'year_one_bill_bau': {'type': float, "description": "Result - year one bill bau", "units": 'hours'},
            'year_one_export_benefit': {'type': float, "description": "Result - total export benefit", "units": 'hours'},

            # "year_one_payments_to_third_party_owner": {'type': float, "description": "Revenue to Battery Owner", "units": '$'}, # currently unused
            # "total_payments_to_third_party_owner": {'type': float, "description": "Revenue to Battery Owner", "units": '$'},    # currently unused
        },

        "Dispatch": {
            "year_one_electric_load_series": {'type': list_of_float,  "description": "Year 1 electric load time series", "units": 'kW'},
            "year_one_pv_to_battery_series": {'type': list_of_float, "description": "Year 1 PV to battery time series", "units": 'kW'},
            "year_one_pv_to_load_series": {'type': list_of_float, "description": "Year 1 PV to load time series", "units": 'kW'},
            "year_one_pv_to_grid_series": {'type': list_of_float, "description": "Year 1 PV to grid time series", "units": 'kW'},
            "year_one_wind_to_battery_series": {'type': list_of_float, "description": "Year 1 wind to battery time series", "units": 'kW'},
            "year_one_wind_to_load_series": {'type': list_of_float, "description": "Year 1 wind to load time series", "units": 'kW'},
            "year_one_wind_to_grid_series": {'type': list_of_float, "description": "Year 1 wind to grid time series", "units": 'kW'},
            "year_one_grid_to_load_series": {'type': list_of_float, "description": "Year 1 grid to load time series", "units": 'kW'},
            "year_one_grid_to_battery_series": {'type': list_of_float, "description": "Year 1 grid to battery time series", "units": 'kW'},
            "year_one_battery_to_load_series": {'type': list_of_float, "description": "Year 1 battery to load time series", "units": 'kW'},
            "year_one_battery_to_grid_series": {'type': list_of_float, "description": "Year 1 battery to grid time series", "units": 'kW'},
            "year_one_battery_soc_series": {'type': list_of_float, "description": "Year 1 battery state of charge", "units": '%'},
            "year_one_energy_cost_series": {'type': list_of_float, "description": "Year 1 energy cost time series", "units": '$/kWh'},
            "year_one_demand_cost_series": {'type': list_of_float, "description": "Year 1 demand cost time series", "units": '$/kW'},
        }
    },

    "Messages": {
        "warnings": {'type': list_of_string, "description": "Warnings generated by simulation"},
        "error": {'type': str, "description": "Error generated by simulation"}

    }
}