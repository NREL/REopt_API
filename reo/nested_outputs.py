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
from .nested_inputs import nested_input_definitions, list_of_float


def list_of_string(inpt):
    return [str(i) for i in inpt]

nested_output_definitions = {

    "inputs": nested_input_definitions,

    "outputs": {

          "Scenario": {
            "run_uuid": {
              "type": "str",
              "description": "Unique id",
              "units": "none"
            },
            "api_version": {
              "type": "str"
            },
            "status": {
              "type": "str",
              "description": "Problem Status",
              "units": "none"
            },
            "Profile": {
                "pre_setup_scenario_seconds": {
                  "type": "float",
                  "description": "Time spent before setting up scenario",
                  "units": "seconds"
                },
                "setup_scenario_seconds": {
                  "type": "float",
                  "description": "Time spent setting up scenario",
                  "units": "seconds"
                },
                "reopt_seconds":{
                  "type": "float",
                  "description": "Time spent solving scenario",
                  "units": "seconds"
                },
                "reopt_bau_seconds": {
                  "type": "float",
                  "description": "Time spent solving base-case scenario",
                  "units": "seconds"
                },
                "parse_run_outputs_seconds": {
                  "type": "float",
                  "description": "Time spent parsing outputs",
                  "units": "seconds"
                }
            },

            "Site": {
              "year_one_renewable_generation_pct": {
                  "type": float,
                  "description": "Percent of total energy consumption provided by renewable energy.",
                  "units": "%"
                },
              "year_one_renewable_generation_kwh": {
                  "type": int,
                  "description": "Total annual renewable energy generation.",
                  "units": "kWh"
                },
              "year_one_emissions_lb_CO2": {
                  "type": int,
                  "description": "Total equivalent pounds of carbon dioxide emissions associated with the site's energy consumption in the first year.",
                  "units": "lb CO2e"
                },
              "year_one_emissions_reduction_pct": {
                  "type": float,
                  "description": "Percent reduction in total equivalent pounds of carbon dioxide emissions in the optimal case relative to the BAU case to the ",
                  "units": "%"
                },
              "year_one_scope1_emissions_lb_CO2": {
                "type": int,
                "description": "Total equivalent pounds of carbon dioxide generated from onsite fuel consumption in the first year (Scope 1 emissions).",
                "units": "lb CO2e"
              },
              "year_one_scope2_emissions_lb_CO2": {
                "type": int,
                "description": "Total equivalent pounds of carbon dioxide associated with energy (rather than fuel) purchases (Scope 2 emissions) in the first year, currently limited to electric grid purchases.",
                "units": "lb CO2e"
              },
              "year_one_nonscope_emissions_lb_CO2": {
                "type": int,
                "description": "Total equivalent pounds of carbon dioxide offset by clean energy exports in the first year. Negative value indicates emissions offset. According to the Greenhouse Gas Protocol, these emission offsets do not technically count towards an organization's emissions reductions (i.e. they fall outside of Scope 1 or Scope 2 emissions) but can be reported as additional information.",
                "units": "lb CO2e"
              },
              "year_one_renewable_generation_bau_pct": {
                "type": float,
                "description": "Percent of total energy consumption provided by renewable energy in the BAU case.",
                "units": "%"
              },
              "year_one_renewable_generation_bau_kwh": {
                "type": int,
                "description": "Total annual renewable energy generation in the BAU case.",
                "units": "kWh"
              },
              "year_one_emissions_bau_lb_CO2": {
                "type": int,
                "description": "Total equivalent pounds of carbon dioxide emissions associated with the site's energy consumption in the first year in the BAU case.",
                "units": "lb CO2e"
              },
              "year_one_scope1_emissions_bau_lb_CO2": {
                "type": int,
                "description": "Total equivalent pounds of carbon dioxide generated from onsite fuel consumption (Scope 1 emissions) in the first year in the BAU case.",
                "units": "lb CO2e"
              },
              "year_one_scope2_emissions_bau_lb_CO2": {
                "type": int,
                "description": "Total equivalent pounds of carbon dioxide associated with energy (rather than fuel) purchases (Scope 2 emissions) in the first year in the BAU case, currently limited to electric grid purchases.",
                "units": "lb CO2e"
              },
              "year_one_nonscope_emissions_bau_lb_CO2": {
                "type": int,
                "description": "Total equivalent pounds of carbon dioxide offset by clean energy exports in the first year in the BAU case. According to the Greenhouse Gas Protocol, these emission offsets do not technically count towards an organization's emissions reductions (i.e. they fall outside of Scope 1 or Scope 2 emissions) but can be reported as additional information.",
                "units": "lb CO2e"
              },
              

              "LoadProfile": {
                "year_one_electric_load_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one hourly time series of electric load",
                  "units": "kW"
                },
                "critical_load_series_kw": {
                  "type": "list_of_float",
                  "description": "Hourly critical load for outage simulator. Values are either uploaded by user, or determined from typical load (either uploaded or simulated) and critical_load_pct.",
                  "units": "kW"
                },
                "annual_calculated_kwh": {
                  "type": "float",
                  "description": "Annual energy consumption calculated by summing up 8760 load profile",
                  "units": "kWh"
                },
                "resilience_check_flag": {
                  "type": "boolean",
                  "description": "BAU resilience check status for existing system"
                },
                "sustain_hours": {
                  "type": "int",
                  "description": "Number of hours the existing system can sustain with resilience check",
                  "units": "hours"
                },
                "bau_sustained_time_steps": {
                  "type": "int",
                  "description": "Number of time steps the existing system can sustain the critical load",
                  "units": "time steps"
                }
              },

              "Financial": {
                "lcc_us_dollars": {
                  "type": "float",
                  "description": "Optimal lifecycle cost",
                  "units": "dollars"
                },
                "lcc_bau_us_dollars": {
                  "type": "float",
                  "description": "Business as usual lifecycle cost",
                  "units": "dollars"
                },
                "npv_us_dollars": {
                  "type": "float",
                  "description": "Net present value of savings realized by the project",
                  "units": "dollars"
                },
                "net_capital_costs_plus_om_us_dollars": {
                  "type": "float",
                  "description": "Capital cost for all technologies plus present value of operations and maintenance over anlaysis period",
                  "units": "$"
                },
                "net_om_us_dollars_bau": {
                  "type": "float",
                  "description": "Business-as-usual present value of operations and maintenance over anlaysis period",
                  "units": "$"
                },
                "net_capital_costs": {
                  "type": "float",
                  "description": "Net capital costs for all technologies, in present value, including replacement costs and incentives.",
                  "units": "$"
                },
                "microgrid_upgrade_cost_us_dollars": {
                  "type": "float",
                  "description": "Cost in US dollars to make a distributed energy system islandable from the grid. Determined by multiplying the total capital costs of resultant energy systems from REopt (such as PV and Storage system) with the input value for microgrid_upgrade_cost_pct (which defaults to 0.30)."
                },
                "initial_capital_costs": {
                  "type": "float",
                  "description": "Up-front capital costs for all technologies, in present value, excluding replacement costs and incentives.",
                  "units": "$"
                },
                "initial_capital_costs_after_incentives": {
                  "type": "float",
                  "description": "Up-front capital costs for all technologies, in present value, excluding replacement costs, including incentives.",
                  "units": "$"
                },
                "replacement_costs": {
                  "type": "float",
                  "description": "Net replacement costs for all technologies, in future value, excluding incentives.",
                  "units": "$"
                },
                "simple_payback_years": {
                  "type": "float",
                  "description": ("Number of years until the cumulative annual cashflow turns positive. "
                                  "If the cashflow becomes negative again after becoming positive (i.e. due to battery repalcement costs)"
                                  " then simple payback is increased by the number of years that the cash flow "
                                  "is negative beyond the break-even year."),



                  "units": "$"
                },
                "irr_pct": {
                  "type": "float",
                  "description": ("internal Rate of Return of the cost-optimal system. In two-party cases the "
                                  "developer discount rate is used in place of the offtaker discount rate."),
                  "units": "%"
                 },
                 "net_present_cost_us_dollars": {
                  "type": "float",
                  "description": ("Present value of the total costs incurred by the third-party owning and operating the "
                                  "distributed energy resource assets."),
                  "units": "$"
                 },
                 "annualized_payment_to_third_party_us_dollars": {
                  "type": "float",
                  "description": ("The annualized amount the host will pay to the third-party owner over the life of the project."),
                  "units": "$"
                 },
                 "offtaker_annual_free_cashflow_series_us_dollars": {
                  "type": "float",
                  "description": ("Annual free cashflow for the host in the optimal case for all analysis years, including year 0. Future years have not been discounted to account for the time value of money."),
                  "units": "$"
                 },
                 "offtaker_discounted_annual_free_cashflow_series_us_dollars": {
                  "type": "float",
                  "description": ("Annual discounted free cashflow for the host in the optimal case for all analysis years, including year 0. Future years have been discounted to account for the time value of money."),
                  "units": "$"
                 },
                 "offtaker_annual_free_cashflow_series_bau_us_dollars": {
                  "type": "float",
                  "description": ("Annual free cashflow for the host in the business-as-usual case for all analysis years, including year 0. Future years have not been discounted to account for the time value of money. Only calcualted in the non-third-party case."),
                  "units": "$"
                 },
                 "offtaker_discounted_annual_free_cashflow_series_bau_us_dollars": {
                  "type": "float",
                  "description": ("Annual discounted free cashflow for the host in the business-as-usual case for all analysis years, including year 0. Future years have been discounted to account for the time value of money. Only calcualted in the non-third-party case."),
                  "units": "$"
                 },
                 "developer_annual_free_cashflow_series_bau_us_dollars": {
                  "type": "float",
                  "description": ("Annual free cashflow for the developer in the business-as-usual third party case for all analysis years, including year 0. Future years have not been discounted to account for the time value of money. Only calcualted in the third-party case."),
                  "units": "$"
                 },
              },

              "PV": {
                "pv_name": {
                  "type": "str",
                  "description": "Site name/description"
                },
                "size_kw": {
                  "type": "float",
                  "description": "Optimal PV system size",
                  "units": "kW"
                },
                "average_yearly_energy_produced_kwh": {
                  "type": "float",
                  "description": "Average annual energy produced by the PV system over one year",
                  "units": "kWh"
                },
                "average_yearly_energy_produced_bau_kwh": {
                  "type": "float",
                  "description": "Average annual energy produced by the existing PV system over one year",
                  "units": "kWh"
                },
                "average_yearly_energy_exported_kwh": {
                  "type": "float",
                  "description": "Average annual energy exported by the PV system",
                  "units": "kWh"
                },
                "year_one_energy_produced_kwh": {
                  "type": "float",
                  "description": "Year one energy produced by the PV system",
                  "units": "kWh"
                },
                "year_one_energy_produced_bau_kwh": {
                  "type": "float",
                  "description": "Year one energy produced by the PV system in the BAU case",
                  "units": "kWh"
                },
                "year_one_power_production_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one PV power production time series",
                  "units": "kW"
                },
                "year_one_to_battery_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one hourly time series of PV charging",
                  "units": "kW"
                },
                "year_one_to_load_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one hourly time series of PV serving load",
                  "units": "kW"
                },
                "year_one_to_grid_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one hourly time series of PV exporting to grid",
                  "units": "kW"
                },
                "existing_pv_om_cost_us_dollars": {
                  "type": "float",
                  "description": "Lifetime O&M cost for existing PV system.",
                  "units": "$"
                },
                "station_latitude": {
                  "type": "float",
                  "description": "The latitude of the station used for weather resource data",
                  "units": "degrees"
                },
                "station_longitude": {
                  "type": "float",
                  "description": "The longitude of the station used for weather resource data",
                  "units": "degrees"
                },
                "station_distance_km": {
                  "type": "float",
                  "description": "The distance from the weather resource station from the input site",
                  "units": "km"
                },
                "year_one_curtailed_production_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one PV power curtailed during outage time series",
                  "units": "kW"
                },
                "year_one_scope1_emissions_lb_CO2": {
                  "type": int,
                  "description": "Total equivalent pounds of carbon dioxide generated from onsite PV in the first year (Scope 1 emissions).",
                  "units": "lb CO2e"
                },
                "year_one_nonscope_emissions_lb_CO2": {
                  "type": int,
                  "description": "Total equivalent pounds of carbon dioxide by PV exports in the first year. Negative value indicates emissions offset. According to the Greenhouse Gas Protocol, these emission offsets do not technically count towards an organization's emissions reductions (i.e. they fall outside of Scope 1 or Scope 2 emissions) but can be reported as additional information.",
                  "units": "lb CO2e"
                },
                "year_one_scope1_emissions_bau_lb_CO2": {
                  "type": int,
                  "description": "Total equivalent pounds of carbon dioxide generated from onsite PV in the first year (Scope 1 emissions) in the BAU case.",
                  "units": "lb CO2e"
                },
                "year_one_nonscope_emissions_bau_lb_CO2": {
                  "type": int,
                  "description": "Total equivalent pounds of carbon dioxide by PV exports in the first year in the BAU case. Negative value indicates emissions offset. According to the Greenhouse Gas Protocol, these emission offsets do not technically count towards an organization's emissions reductions (i.e. they fall outside of Scope 1 or Scope 2 emissions) but can be reported as additional information.",
                  "units": "lb CO2e"
                },
              },


              "Wind": {
                "size_kw": {
                  "type": "float",
                  "description": "Recommended wind system size",
                  "units": "kW"
                },
                "average_yearly_energy_produced_kwh": {
                  "type": "float",
                  "description": "Average energy produced by the wind system over one year",
                  "units": "kWh"
                },
                "average_yearly_energy_exported_kwh": {
                  "type": "float",
                  "description": "Average annual energy exported by the wind system",
                  "units": "kWh"
                },
                "year_one_energy_produced_kwh": {
                  "type": "float",
                  "description": "Wind energy produced in year one",
                  "units": "kWh"
                },
                "year_one_power_production_series_kw": {
                  "type": "list_of_float",
                  "description": "Hourly wind resource",
                  "units": "kW"
                },
                "year_one_to_battery_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one wind to battery time series",
                  "units": "kW"
                },
                "year_one_to_load_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one wind to load time series",
                  "units": "kW"
                },
                "year_one_to_grid_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one wind to grid time series",
                  "units": "kW"
                },
                "year_one_curtailed_production_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one Wind power curtailed during outage time series",
                  "units": "kW"
                },
                "year_one_scope1_emissions_lb_CO2": {
                  "type": int,
                  "description": "Total equivalent pounds of carbon dioxide generated from onsite wind in the first year (Scope 1 emissions).",
                  "units": "lb CO2e"
                },
                "year_one_nonscope_emissions_lb_CO2": {
                  "type": int,
                  "description": "Total equivalent pounds of carbon dioxide by wind exports in the first year. Negative value indicates emissions offset. According to the Greenhouse Gas Protocol, these emission offsets do not technically count towards an organization's emissions reductions (i.e. they fall outside of Scope 1 or Scope 2 emissions) but can be reported as additional information.",
                  "units": "lb CO2e"
                },
              },

              "Storage": {
                "size_kw": {
                  "type": "float",
                  "description": "Optimal battery power capacity",
                  "units": "kW"
                },
                "size_kwh": {
                  "type": "float",
                  "description": "Optimal battery energy capacity",
                  "units": "kWh"
                },
                "year_one_to_load_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one hourly time series of battery serving load",
                  "units": "kW"
                },
                "year_one_to_grid_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one hourly time series of battery exporting to grid",
                  "units": "kW"
                },
                "year_one_soc_series_pct": {
                  "type": "list_of_float",
                  "description": "Year one hourly time series of battery state of charge",
                  "units": "%"
                }
              },

              "ElectricTariff": {
                "year_one_energy_cost_us_dollars": {
                  "type": "float",
                  "description": "Optimal year one utility energy cost",
                  "units": "$"
                },
                "year_one_demand_cost_us_dollars": {
                  "type": "float",
                  "description": "Optimal year one utility demand cost",
                  "units": "$"
                },
                "year_one_fixed_cost_us_dollars": {
                  "type": "float",
                  "description": "Optimal year one utility fixed cost",
                  "units": "$"
                },
                "year_one_min_charge_adder_us_dollars": {
                  "type": "float",
                  "description": "Optimal year one utility minimum charge adder",
                  "units": "$"
                },
                "year_one_energy_cost_bau_us_dollars": {
                  "type": "float",
                  "description": "Business as usual year one utility energy cost",
                  "units": "$"
                },
                "year_one_demand_cost_bau_us_dollars": {
                  "type": "float",
                  "description": "Business as usual year one utility demand cost",
                  "units": "$"
                },
                "year_one_fixed_cost_bau_us_dollars": {
                  "type": "float",
                  "description": "Business as usual year one utility fixed cost",
                  "units": "$"
                },
                "year_one_min_charge_adder_bau_us_dollars": {
                  "type": "float",
                  "description": "Business as usual year one utility minimum charge adder",
                  "units": "$"
                },
                "total_energy_cost_us_dollars": {
                  "type": "float",
                  "description": "Total utility energy cost over the lifecycle, after-tax",
                  "units": "$"
                },
                "total_demand_cost_us_dollars": {
                  "type": "float",
                  "description": "Optimal total lifecycle utility demand cost over the analysis period, after-tax",
                  "units": "$"
                },
                "total_fixed_cost_us_dollars": {
                  "type": "float",
                  "description": "Total utility fixed cost over the lifecycle, after-tax",
                  "units": "$"
                },
                "total_min_charge_adder_us_dollars": {
                  "type": "float",
                  "description": "Total utility minimum charge adder",
                  "units": "$"
                },
                "total_energy_cost_bau_us_dollars": {
                  "type": "float",
                  "description": "Business as usual total utility energy cost over the lifecycle, after-tax",
                  "units": "$"
                },
                "total_demand_cost_bau_us_dollars": {
                  "type": "float",
                  "description": "Business as usual total lifecycle utility demand cost over the analysis period, after-tax",
                  "units": "$"
                },
                "total_fixed_cost_bau_us_dollars": {
                  "type": "float",
                  "description": "Business as usual total utility fixed cost over the lifecycle, after-tax",
                  "units": "$"
                },
                "total_export_benefit_us_dollars": {
                  "type": "float",
                  "description": "Total export benefit cost over the lifecycle, after-tax",
                  "units": "$"
                },
                "total_export_benefit_bau_us_dollars": {
                  "type": "float",
                  "description": "BAU export benefit cost over the lifecycle, after-tax",
                  "units": "$"
                },
                "total_min_charge_adder_bau_us_dollars": {
                  "type": "float",
                  "description": "Business as usual total utility minimum charge adder",
                  "units": "$"
                },
                "year_one_bill_us_dollars": {
                  "type": "float",
                  "description": "Optimal year one total utility bill",
                  "units": "$"
                },
                "year_one_bill_bau_us_dollars": {
                  "type": "float",
                  "description": "Business as usual year one total utility bill",
                  "units": "$"
                },
                "year_one_export_benefit_us_dollars": {
                  "type": "float",
                  "description": "Optimal year one value of exported energy",
                  "units": "$"
                },
                "year_one_export_benefit_bau_us_dollars": {
                  "type": "float",
                  "description": "BAU year one value of exported energy",
                  "units": "$"
                },
                "year_one_energy_cost_series_us_dollars_per_kwh": {
                  "type": "list_of_float",
                  "description": "Year one hourly energy costs",
                  "units": "$/kWh"
                },
                "year_one_demand_cost_series_us_dollars_per_kw": {
                  "type": "list_of_float",
                  "description": "Year one hourly demand costs",
                  "units": "$/kW"
                },
                "year_one_to_load_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one grid to load time series",
                  "units": "kW"
                },
                "year_one_to_load_series_bau_kw": {
                  "type": "list_of_float",
                  "description": "Year one grid to load time series in the BAU case",
                  "units": "kW"
                },
                "year_one_to_battery_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one hourly time series of power from grid to battery",
                  "units": "kW"
                },
                "year_one_energy_supplied_kwh": {
                  "type": "float",
                  "description": "Year one energy supplied from grid to load",
                  "units": "kWh"
                },
                "year_one_energy_supplied_kwh_bau": {
                  "type": "float",
                  "description": "Year one energy supplied from grid to load in the business-as-usual scenario",
                  "units": "kWh"
                },
                "year_one_scope2_emissions_lb_CO2": {
                  "type": int,
                  "description": "Total equivalent pounds of carbon dioxide associated with grid electricity purchases (Scope 2 emissions) in the first year. Calculated by default from hourly emissions estimates except in AK and HI.",
                  "units": "lb CO2e"
                },
                "year_one_scope2_emissions_bau_lb_CO2": {
                  "type": int,
                  "description": "Total equivalent pounds of carbon dioxide emitted from BAU utility electricity use in the first year in the BAU case. Calculated by default from hourly emissions estimates except in AK and HI.",
                  "units": "lb CO2"
                },
              },

              "Generator": {
                "size_kw": {
                  "type": "float",
                  "description": "Optimal diesel generator system size",
                  "units": "kW"
                },
                "fuel_used_gal": {
                  "type": "float",
                  "description": "Generator fuel used to meet critical load during grid outage.",
                  "units": "US gallons"
                },
                "fuel_used_gal_bau": {
                  "type": "float",
                  "description": "Generator fuel used to meet critical load during grid outage in bau case.",
                  "units": "US gallons"
                },
                "average_yearly_energy_produced_kwh": {
                  "type": "float",
                  "description": "Average annual energy produced by the diesel generator over one year",
                  "units": "kWh"
                },
                "average_yearly_energy_exported_kwh": {
                  "type": "float",
                  "description": "Average annual energy exported by the diesel generator",
                  "units": "kWh"
                },
                "year_one_energy_produced_kwh": {
                  "type": "float",
                  "description": "Year one energy produced by the diesel generator",
                  "units": "kWh"
                },
                "year_one_power_production_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one diesel generator power production time series",
                  "units": "kW"
                },
                "year_one_to_battery_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one hourly time series of diesel generator charging",
                  "units": "kW"
                },
                "year_one_to_load_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one generator to load time series.",
                  "units": "kW"
                },
                "year_one_to_grid_series_kw": {
                  "type": "list_of_float",
                  "description": "Year one hourly time series of diesel generator exporting to grid",
                  "units": "kW"
                },
                "existing_gen_total_fixed_om_cost_us_dollars": {
                  "type": "float",
                  "description": "Lifetime fixed O&M cost for existing diesel generator system in bau case.",
                  "units": "$"
                },
                "existing_gen_total_variable_om_cost_us_dollars": {
                  "type": "float",
                  "description": "Lifetime variable (based on kwh produced) O&M cost for existing diesel generator system.",
                  "units": "$"
                },
                "existing_gen_year_one_variable_om_cost_us_dollars": {
                  "type": "float",
                  "description": "Year one variable (based on kwh produced) O&M cost for existing diesel generator system.",
                  "units": "$"
                },
                "total_fixed_om_cost_us_dollars": {
                  "type": "float",
                  "description": "Total lifecycle fixed (based on kW capacity) O&M cost for existing + recommended diesel generator system.",
                  "units": "$"
                },
                "total_variable_om_cost_us_dollars": {
                  "type": "float",
                  "description": "Total lifecycle variable (based on kWh produced) O&M cost for existing + recommended diesel generator system",
                  "units": "$"
                },
                "year_one_variable_om_cost_us_dollars": {
                  "type": "float",
                  "description": "Year one variable (based on kwh produced) O&M cost for existing + recommended diesel generator system",
                  "units": "$"
                },
                "year_one_fixed_om_cost_us_dollars": {
                  "type": "float",
                  "description": "Year one fixed (based on kW capacity) O&M cost for existing + recommended diesel generator system.",
                  "units": "$"
                },
                "total_fuel_cost_us_dollars": {
                  "type": "float",
                  "description": "Total lifecycle fuel cost for existing + newly recommended diesel generator system",
                  "units": "$"
                },
                "year_one_fuel_cost_us_dollars": {
                  "type": "float",
                  "description": "Year one fuel cost for existing + newly recommended diesel generator system",
                  "units": "$"
                },
                "existing_gen_total_fuel_cost_us_dollars": {
                  "type": "float",
                  "description": "Total lifecycle fuel cost for existing diesel generator system",
                  "units": "$"
                },
                "existing_gen_year_one_fuel_cost_us_dollars": {
                  "type": "float",
                  "description": "Year one fuel cost for existing diesel generator system",
                  "units": "$"
                },
                "year_one_scope1_emissions_lb_CO2": {
                  "type": int,
                  "description": "Total equivalent pounds of carbon dioxide generated from an onsite generator in the first year (Scope 1 emissions).",
                  "units": "lb CO2e"
                },
                "year_one_nonscope_emissions_lb_CO2": {
                  "type": int,
                  "description": "Total equivalent pounds of carbon dioxide by generator exports in the first year. Negative value indicates emissions offset. According to the Greenhouse Gas Protocol, these emission offsets do not technically count towards an organization's emissions reductions (i.e. they fall outside of Scope 1 or Scope 2 emissions) but can be reported as additional information.",
                  "units": "lb CO2e"
                },
                "year_one_scope1_emissions_bau_lb_CO2": {
                  "type": float,
                  "description": "Total equivalent pounds of carbon dioxide generated from onsite PV in the first year (Scope 1 emissions).",
                  "units": "lb CO2e"
                },
                "year_one_nonscope_emissions_bau_lb_CO2": {
                  "type": int,
                  "description": "Total equivalent pounds of carbon dioxide by PV exports in the first year. Negative value indicates emissions offset. According to the Greenhouse Gas Protocol, these emission offsets do not technically count towards an organization's emissions reductions (i.e. they fall outside of Scope 1 or Scope 2 emissions) but can be reported as additional information.",
                  "units": "lb CO2e"
                }
            }
          }
        }
      },

    "messages": {
        "warnings": {'type': "list_of_string", "description": "Warnings generated by simulation"},
        "error": {'type': "str", "description": "Error generated by simulation"}
    }
}