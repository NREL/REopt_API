from nested_inputs import nested_input_definitions, list_of_float


def list_of_string(input):
    return [str(i) for i in input]

nested_output_definitions = {

    "inputs": nested_input_definitions,

    "outputs": {

          "Scenario": {
            "uuid": {
              "type": str,
              "description": "Unique id",
              "units": "none"
            },
            "api_version": {
              "type": str
            },
            "status": {
              "type": str,
              "description": "Problem Status",
              "units": "none"
            },

            "Site": {

              "LoadProfile": {
                "year_one_electric_load_series_kw": {
                  "type": list_of_float,
                  "description": "Year one hourly time series of electric load",
                  "units": "kW"
                }
              },

              "Financial": {
                "lcc_us_dollars": {
                  "type": float,
                  "description": "Optimal lifecycle cost",
                  "units": "dollars"
                },
                "lcc_bau_us_dollars": {
                  "type": float,
                  "description": "Business as usual lifecycle cost",
                  "units": "dollars"
                },
                "npv_us_dollars": {
                  "type": float,
                  "description": "Net present value of savings realized by the project",
                  "units": "dollars"
                },
                "net_capital_costs_plus_om_us_dollars": {
                  "type": float,
                  "description": "Optimal capital cost plus present value of operations and maintenance over anlaysis period",
                  "units": "$"
                },
                "avoided_outage_costs_us_dollars": {
                  "type": float,
                  "description": "Avoided outage costs are determined using the Value of Lost Load [$/kWh], multiplied by the average critical load (determined using critical_load_pct) and the average hours that the critical load is sustained (determined by simulating outages starting at every hour of the year).",
                  "units": "$"
                }
              },

              "PV": {
                "size_kw": {
                  "type": float,
                  "description": "Optimal PV system size",
                  "units": "kW"
                },
                "average_yearly_energy_produced_kwh": {
                  "type": float,
                  "description": "Average annual energy produced by the PV system over one year",
                  "units": "kWh"
                },
                "average_yearly_energy_exported_kwh": {
                  "type": float,
                  "description": "Average annual energy exported by the PV system",
                  "units": "kWh"
                },
                "year_one_energy_produced_kwh": {
                  "type": float,
                  "description": "Year one energy produced by the PV system",
                  "units": "kWh"
                },
                "year_one_power_production_series_kw": {
                  "type": list_of_float,
                  "description": "Year one PV power production time series",
                  "units": "kW"
                },
                "year_one_to_battery_series_kw": {
                  "type": list_of_float,
                  "description": "Year one hourly time series of PV charging",
                  "units": "kW"
                },
                "year_one_to_load_series_kw": {
                  "type": list_of_float,
                  "description": "Year one hourly time series of PV serving load",
                  "units": "kW"
                },
                "year_one_to_grid_series_kw": {
                  "type": list_of_float,
                  "description": "Year one hourly time series of PV exporting to grid",
                  "units": "kW"
                }
              },

              "Wind": {
                "size_kw": {
                  "type": float,
                  "description": "Recommended wind system size",
                  "units": "kW"
                },
                "average_yearly_energy_produced_kwh": {
                  "type": float,
                  "description": "Average energy produced by the wind system over one year",
                  "units": "kWh"
                },
                "average_yearly_energy_exported_kwh": {
                  "type": float,
                  "description": "Average annual energy exported by the wind system",
                  "units": "kWh"
                },
                "year_one_energy_produced_kwh": {
                  "type": float,
                  "description": "Wind energy produced in year one",
                  "units": "kWh"
                },
                "year_one_power_production_series_kw": {
                  "type": list_of_float,
                  "description": "Hourly wind resource",
                  "units": "kW"
                },
                "year_one_to_battery_series_kw": {
                  "type": list_of_float,
                  "description": "Year one wind to battery time series",
                  "units": "kW"
                },
                "year_one_to_load_series_kw": {
                  "type": list_of_float,
                  "description": "Year one wind to load time series",
                  "units": "kW"
                },
                "year_one_to_grid_series_kw": {
                  "type": list_of_float,
                  "description": "Year one wind to grid time series",
                  "units": "kW"
                }
              },

              "Storage": {
                "size_kw": {
                  "type": float,
                  "description": "Optimal battery power capacity",
                  "units": "kW"
                },
                "size_kwh": {
                  "type": float,
                  "description": "Optimal battery energy capacity",
                  "units": "kWh"
                },
                "year_one_to_load_series_kw": {
                  "type": list_of_float,
                  "description": "Year one hourly time series of battery serving load",
                  "units": "kW"
                },
                "year_one_to_grid_series_kw": {
                  "type": list_of_float,
                  "description": "Year one hourly time series of battery exporting to grid",
                  "units": "kW"
                },
                "year_one_soc_series_pct": {
                  "type": list_of_float,
                  "description": "Year one hourly time series of battery state of charge",
                  "units": "%"
                }
              },

              "ElectricTariff": {
                "year_one_energy_cost_us_dollars": {
                  "type": float,
                  "description": "Optimal year one utility energy cost",
                  "units": "$"
                },
                "year_one_demand_cost_us_dollars": {
                  "type": float,
                  "description": "Optimal year one utility demand cost",
                  "units": "$"
                },
                "year_one_fixed_cost_us_dollars": {
                  "type": float,
                  "description": "Optimal year one utility fixed cost",
                  "units": "$"
                },
                "year_one_min_charge_adder_us_dollars": {
                  "type": float,
                  "description": "Optimal year one utility minimum charge adder",
                  "units": "$"
                },
                "year_one_energy_cost_bau_us_dollars": {
                  "type": float,
                  "description": "Business as usual year one utility energy cost",
                  "units": "$"
                },
                "year_one_demand_cost_bau_us_dollars": {
                  "type": float,
                  "description": "Business as usual year one utility demand cost",
                  "units": "$"
                },
                "year_one_fixed_cost_bau_us_dollars": {
                  "type": float,
                  "description": "Business as usual year one utility fixed cost",
                  "units": "$"
                },
                "year_one_min_charge_adder_bau_us_dollars": {
                  "type": float,
                  "description": "Business as usual year one utility minimum charge adder",
                  "units": "$"
                },
                "total_energy_cost_us_dollars": {
                  "type": float,
                  "description": "Total utility energy cost over the lifecycle, after-tax",
                  "units": "$"
                },
                "total_demand_cost_us_dollars": {
                  "type": float,
                  "description": "Optimal total lifecycle utility demand cost over the analysis period, after-tax",
                  "units": "$"
                },
                "total_fixed_cost_us_dollars": {
                  "type": float,
                  "description": "Total utility fixed cost over the lifecycle, after-tax",
                  "units": "$"
                },
                "total_min_charge_adder_us_dollars": {
                  "type": float,
                  "description": "Total utility minimum charge adder",
                  "units": "$"
                },
                "total_energy_cost_bau_us_dollars": {
                  "type": float,
                  "description": "Business as usual total utility energy cost over the lifecycle, after-tax",
                  "units": "$"
                },
                "total_demand_cost_bau_us_dollars": {
                  "type": float,
                  "description": "Business as usual total lifecycle utility demand cost over the analysis period, after-tax",
                  "units": "$"
                },
                "total_fixed_cost_bau_us_dollars": {
                  "type": float,
                  "description": "Business as usual total utility fixed cost over the lifecycle, after-tax",
                  "units": "$"
                },
                "total_min_charge_adder_bau_us_dollars": {
                  "type": float,
                  "description": "Business as usual total utility minimum charge adder",
                  "units": "$"
                },
                "year_one_bill_us_dollars": {
                  "type": float,
                  "description": "Optimal year one total utility bill",
                  "units": "$"
                },
                "year_one_bill_bau_us_dollars": {
                  "type": float,
                  "description": "Business as usual year one total utility bill",
                  "units": "$"
                },
                "year_one_export_benefit_us_dollars": {
                  "type": float,
                  "description": "Optimal year one value of exported energy",
                  "units": "$"
                },
                "year_one_energy_cost_series_us_dollars_per_kwh": {
                  "type": list_of_float,
                  "description": "Year one hourly energy costs",
                  "units": "$/kWh"
                },
                "year_one_demand_cost_series_us_dollars_per_kw": {
                  "type": list_of_float,
                  "description": "Year one hourly demand costs",
                  "units": "$/kW"
                },
                "year_one_to_load_series_kw": {
                  "type": list_of_float,
                  "description": "Year one grid to load time series",
                  "units": "kW"
                },
                "year_one_to_battery_series_kw": {
                  "type": list_of_float,
                  "description": "Year one hourly time series of power from grid to battery",
                  "units": "kW"
                },
                "year_one_energy_supplied_kwh": {
                  "type": float,
                  "description": "Year one hourly time series of power from grid to load",
                  "units": "kWh"
                }
              },

              "Generator": {
                "fuel_used_gal": {
                  "type": float,
                  "description": "Generator fuel used to meet critical load during grid outage.",
                  "units": "US gallons"
                }
              }
            }
          }
        },

    "messages": {
        "warnings": {'type': list_of_string, "description": "Warnings generated by simulation"},
        "error": {'type': str, "description": "Error generated by simulation"}

    }
}