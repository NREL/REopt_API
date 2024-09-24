# custom_table_config.py
from reoptjl.custom_table_helpers import safe_get

"""
1. Naming Convention for Tables:
-------------------------------
To prevent namespace pollution and keep table configurations well-organized, use the following naming convention when adding new tables:

Structure:
    custom_table_<feature>

- `custom_table_`: A prefix to indicate that this variable represents a custom table configuration.
- `<feature>`: A descriptive word representing the feature, tool, or module the table is associated with the table configuration.

Examples:
- custom_table_webtool: A table configuration for the webtool feature.
- custom_table_simple: A table configuration for the simple results.
- custom_table_iedo: A table configuration for the IEDO.

Guidelines:
- Use lowercase letters and underscores to separate words.
- Avoid numbering unless necessary to differentiate versions.
- Ensure each table configuration is descriptive enough to understand its context or feature.
----------------------------------
"""
# Example table configuration
custom_table_example = [
    {
        "label": "Site Name",
        "key": "site",
        "bau_value": lambda df: "",
        "scenario_value": lambda df: safe_get(df, "inputs.Meta.description", "None provided")
    },
    {
        "label": "Site Address",
        "key": "site_address",
        "bau_value": lambda df: safe_get(df, "inputs.Meta.address", "None provided"),
        "scenario_value": lambda df: safe_get(df, "inputs.Meta.address", "None provided")
    },
    # Example 2: Concatenating Strings
    {
        "label": "Site Location",
        "key": "site_lat_long",
        "bau_value": lambda df: f"({safe_get(df, 'inputs.Site.latitude')}, {safe_get(df, 'inputs.Site.longitude')})",
        "scenario_value": lambda df: f"({safe_get(df, 'inputs.Site.latitude')}, {safe_get(df, 'inputs.Site.longitude')})"
    },
    {
        "label": "Technology Sizing",  # This is your separator label
        "key": "tech_separator", #MUST HAVE "separator" somewhere in the name
        "bau_value": lambda df: "",
        "scenario_value": lambda df: ""
    },
    # Example 3: Calculated Value (Sum of Two Fields), this does not show up in formulas
    {
        "label": "Combined Renewable Size (kW)",
        "key": "combined_renewable_size",
        "bau_value": lambda df: 0,
        "scenario_value": lambda df: safe_get(df, "outputs.PV.size_kw") + safe_get(df, "outputs.Wind.size_kw")     #NOTE: These calculations will not show up as in the excel calculations
    },

    # Example 4: Hardcoded Values
    {
        "label": "Hardcoded Values (kWh)",
        "key": "hardcoded_value",
        "bau_value": lambda df: 500,  # BAU scenario
        "scenario_value": lambda df: 1000  # other scenarios
    },

    # Example 5: Conditional Formatting
    {
        "label": "PV Size Status",
        "key": "pv_size_status",
        "bau_value": lambda df: 0,
        "scenario_value": lambda df: "Above Threshold" if safe_get(df, "outputs.PV.size_kw") > 2500 else "Below Threshold"
    },
    #Example 6 and 7: First define any data that might need to be referenced, Here I've defined two placeholders
    # Define Placeholder1
    {
        "label": "Placeholder1",
        "key": "placeholder1",
        "bau_value": lambda df: 100,  # BAU value
        "scenario_value": lambda df: 200  # Scenario value
    },
    # Define Placeholder2
    {
        "label": "Placeholder2",
        "key": "placeholder2",
        "bau_value": lambda df: 50,  # BAU value
        "scenario_value": lambda df: 100  # Scenario value
    },
    # Example 6: Calculation Without Reference to BAU
    {
        "label": "Placeholder Calculation Without BAU Reference",
        "key": "placeholder_calculation_without_bau",
        "bau_value": lambda df: 0,  # Placeholder, replaced by formula in Excel
        "scenario_value": lambda df: 0  # Placeholder, replaced by formula in Excel
    },
    # Example 7: Calculation With Reference to BAU
    {
        "label": "Placeholder Calculation With BAU Reference",
        "key": "placeholder_calculation_with_bau",
        "bau_value": lambda df: 0,  # Placeholder, replaced by formula in Excel
        "scenario_value": lambda df: 0  # Placeholder, replaced by formula in Excel
    },
    {
        "label": "Results URL",
        "key": "url",
        "bau_value": lambda df: f"https://custom-table-download-reopt-stage.its.nrel.gov/tool/results/"+safe_get(df, "webtool_uuid"),
        "scenario_value": lambda df: f"https://custom-table-download-reopt-stage.its.nrel.gov/tool/results/"+safe_get(df, "webtool_uuid")
    }
    ]

# Webtool table configuration
custom_table_webtool = [
    {
        "label": "Evaluation Name",
        "key": "evaluation_name",
        "bau_value": lambda df: safe_get(df, "inputs.Meta.description", "None provided"),
        "scenario_value": lambda df: safe_get(df, "inputs.Meta.description", "None provided")
    },
    {
        "label": "BAU or Optimal Case?",
        "key": "bau_or_optimal_case",
        "bau_value": lambda df: "BAU",
        "scenario_value": lambda df: "Optimal"
    },
    {
        "label": "Site Location",
        "key": "site_location",
        "bau_value": lambda df: f"({safe_get(df, 'inputs.Site.latitude')}, {safe_get(df, 'inputs.Site.longitude')})",
        "scenario_value": lambda df: f"({safe_get(df, 'inputs.Site.latitude')}, {safe_get(df, 'inputs.Site.longitude')})"
    },
    {
        "label": "Results URL",
        "key": "url",
        "bau_value": lambda df: '',
        "scenario_value": lambda df: f'=HYPERLINK("https://custom-table-download-reopt-stage.its.nrel.gov/tool/results/{safe_get(df, "webtool_uuid")}", "Results Link")'
    },
    {
        "label": "System Capacities",
        "key": "system_capacities_separator",
        "bau_value": lambda df: "",
        "scenario_value": lambda df: ""
    },
    {
        "label": "PV capacity, new (kW)",
        "key": "pv_capacity_new",
        "bau_value": lambda df: safe_get(df, "outputs.PV.size_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.PV.size_kw")
    },
    {
        "label": "PV capacity, existing (kW)",
        "key": "pv_size_purchased",
        "bau_value": lambda df: safe_get(df, "outputs.PV.existing_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.PV.existing_kw")
    },
    {
        "label": "Wind Capacity (kW)",
        "key": "wind_capacity",
        "bau_value": lambda df: safe_get(df, "outputs.Wind.size_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Wind.size_kw")
    },
    {
        "label": "Backup Generator Capacity, New (kW)",
        "key": "backup_generator_new",
        "bau_value": lambda df: safe_get(df, "outputs.Generator.size_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Generator.size_kw")
    },
    {
        "label": "Backup Generator Capacity, Existing (kW)",
        "key": "backup_generator_existing",
        "bau_value": lambda df: safe_get(df, "outputs.Generator.existing_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Generator.existing_kw")
    },
    {
        "label": "Generator Annual Fuel Consumption (gallons)",
        "key": "backup_generator_fuel_consumption",
        "bau_value": lambda df: safe_get(df, "outputs.Generator.annual_fuel_consumption_gal_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Generator.annual_fuel_consumption_gal")
    },
    {
        "label": "Generator Fuel Cost ($)",
        "key": "backup_generator_fuel_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Generator.year_one_fuel_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Generator.year_one_fuel_cost_before_tax")
    },
    {
        "label": "Generator Lifecycle Fuel Cost ($)",
        "key": "lifecycle_fuel_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Generator.lifecycle_fuel_cost_after_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Generator.lifecycle_fuel_cost_after_tax")
    },
    {
        "label": "Battery Power Capacity (kW)",
        "key": "battery_power_capacity",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricStorage.size_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricStorage.size_kw")
    },
    {
        "label": "Battery Energy Capacity (kWh)",
        "key": "battery_energy_capacity",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricStorage.size_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricStorage.size_kwh")
    },
    {
        "label": "CHP Capacity (kW)",
        "key": "chp_capacity",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.size_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.size_kw")
    },
    {
        "label": "Absorption Chiller Capacity (tons)",
        "key": "absorption_chiller_capacity",
        "bau_value": lambda df: safe_get(df, "outputs.AbsorptionChiller.size_ton_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.AbsorptionChiller.size_ton")
    },
    {
        "label": "Chilled Water TES Capacity (gallons)",
        "key": "chilled_water_tes_capacity",
        "bau_value": lambda df: safe_get(df, "outputs.ColdThermalStorage.size_gal_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ColdThermalStorage.size_gal")
    },
    {
        "label": "Hot Water TES Capacity (gallons)",
        "key": "hot_water_tes_capacity",
        "bau_value": lambda df: safe_get(df, "outputs.HotThermalStorage.size_gal_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.HotThermalStorage.size_gal")
    },
    {
        "label": "Steam Turbine Capacity (kW)",
        "key": "steam_turbine_capacity",
        "bau_value": lambda df: safe_get(df, "outputs.SteamTurbine.size_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.SteamTurbine.size_kw")
    },
    {
        "label": "GHP Heat Pump Capacity (ton)",
        "key": "ghp_heat_pump_capacity",
        "bau_value": lambda df: safe_get(df, "outputs.GHP.size_ton_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.GHP.size_ton")
    },
    {
        "label": "GHP Ground Heat Exchanger Size (ft)",
        "key": "ghp_ground_heat_exchanger_size",
        "bau_value": lambda df: safe_get(df, "outputs.GHP.length_boreholes_ft_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.GHP.length_boreholes_ft")
    },
    {
        "label": "Summary Financial Metrics",
        "key": "summary_financial_metrics_separator",
        "bau_value": lambda df: "",
        "scenario_value": lambda df: ""
    },
    {
        "label": "Gross Capital Costs, Before Incentives ($)",
        "key": "gross_capital_costs_before_incentives",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.initial_capital_costs_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.initial_capital_costs")
    },
    {
        "label": "Present Value of Incentives ($)",
        "key": "present_value_of_incentives",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.production_incentive_max_benefit_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.production_incentive_max_benefit")
    },
    {
        "label": "Net Capital Cost ($)",
        "key": "net_capital_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_capital_costs_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_capital_costs")
    },
    {
        "label": "Year 1 O&M Cost, Before Tax ($)",
        "key": "year_1_om_cost_before_tax",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.year_one_om_costs_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.year_one_om_costs_before_tax")
    },
    {
        "label": "Total Life Cycle Costs ($)",
        "key": "total_life_cycle_costs",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.lcc_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.lcc")
    },
    {
        "label": "Net Present Value ($)",
        "key": "npv",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.npv_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.npv")
    },
    {
        "label": "Payback Period (years)",
        "key": "payback_period",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.simple_payback_years_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.simple_payback_years")
    },
    {
        "label": "Simple Payback (years)",
        "key": "simple_payback_period",
        "bau_value": lambda df: safe_get(df, ""),
        "scenario_value": lambda df: safe_get(df, "")
    },
    {
        "label": "Internal Rate of Return (%)",
        "key": "internal_rate_of_return",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.internal_rate_of_return_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.internal_rate_of_return")
    },
    {
        "label": "Life Cycle Cost Breakdown",
        "key": "lifecycle_cost_breakdown_separator",
        "bau_value": lambda df: "",
        "scenario_value": lambda df: ""
    },
    {
        "label": "Technology Capital Costs + Replacements, After Incentives ($)",
        "key": "technology_capital_costs_after_incentives",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_generation_tech_capital_costs_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_generation_tech_capital_costs")
    },
    {
        "label": "O&M Costs ($)",
        "key": "om_costs",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.om_and_replacement_present_cost_after_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.om_and_replacement_present_cost_after_tax")
    },
    {
        "label": "Total Electric Costs ($)",
        "key": "total_electric_utility_costs",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_elecbill_after_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_elecbill_after_tax")
    },
    {
        "label": "Total Fuel Costs ($)",
        "key": "total_fuel_costs",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_fuel_costs_after_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_fuel_costs_after_tax")
    },
    {
        "label": "Total Utility Costs ($)",
        "key": "total_fuel_costs",
        "bau_value": lambda df: "",
        "scenario_value": lambda df: ""
    },
    {
        "label": "Total Emissions Costs ($)",
        "key": "total_emissions_costs",
        "bau_value": lambda df: safe_get(df, "outputs.Site.lifecycle_emissions_cost_health_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.lifecycle_emissions_cost_health")
    },
    {
        "label": "LCC ($)",
        "key": "lcc",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.lcc_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.lcc")
    },
    {
        "label": "NPV as a % of BAU LCC (%)",
        "key": "npv_bau_percent",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.npv_as_bau_lcc_percent_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.npv_as_bau_lcc_percent")
    },
    {
        "label": "Year 1 Electric Bill",
        "key": "year_1_electric_bill_separator",
        "bau_value": lambda df: "",
        "scenario_value": lambda df: ""
    },
    {
        "label": "Electric Grid Purchases (kWh)",
        "key": "electric_grid_purchases",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricUtility.annual_energy_supplied_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricUtility.annual_energy_supplied_kwh")
    },
    {
        "label": "Energy Charges ($)",
        "key": "electricity_energy_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_energy_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_energy_cost_before_tax")
    },
    {
        "label": "Demand Charges ($)",
        "key": "electricity_demand_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_demand_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_demand_cost_before_tax")
    },
    {
        "label": "Fixed Charges ($)",
        "key": "utility_fixed_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_fixed_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_fixed_cost_before_tax")
    },
    {
        "label": "Purchased Electricity Cost ($)",
        "key": "purchased_electricity_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_bill_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_bill_before_tax")
    },
    {
        "label": "Annual Cost Savings ($)",
        "key": "annual_cost_savings",
        "bau_value": lambda df: "",
        "scenario_value": lambda df: ""
    },
    {
        "label": "Year 1 Fuel Costs & Consumption",
        "key": "year_1_fuel_costs_separator",
        "bau_value": lambda df: "",
        "scenario_value": lambda df: ""
    },
    {
        "label": "Boiler Fuel Consumption (mmbtu)",
        "key": "boiler_fuel_consumption",
        "bau_value": lambda df: safe_get(df, "outputs.ExistingBoiler.annual_fuel_consumption_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ExistingBoiler.annual_fuel_consumption_mmbtu")
    },
    {
        "label": "Boiler Fuel Costs ($)",
        "key": "boiler_fuel_costs",
        "bau_value": lambda df: safe_get(df, "outputs.ExistingBoiler.year_one_fuel_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ExistingBoiler.year_one_fuel_cost_before_tax")
    },
    {
        "label": "CHP Fuel Consumption (mmbtu)",
        "key": "chp_fuel_consumption",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.annual_fuel_consumption_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.annual_fuel_consumption_mmbtu")
    },
    {
        "label": "CHP Fuel Cost ($)",
        "key": "chp_fuel_cost",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.year_one_fuel_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.year_one_fuel_cost_before_tax")
    },
    {
        "label": "Backup Generator Fuel Consumption (gallons)",
        "key": "backup_generator_fuel_consumption",
        "bau_value": lambda df: safe_get(df, "outputs.Generator.annual_fuel_consumption_gal_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Generator.annual_fuel_consumption_gal")
    },
    {
        "label": "Backup Generator Fuel Cost ($)",
        "key": "backup_generator_fuel_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Generator.year_one_fuel_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Generator.year_one_fuel_cost_before_tax")
    },
    {
        "label": "Renewable Energy & Emissions",
        "key": "renewable_energy_emissions_separator",
        "bau_value": lambda df: "",
        "scenario_value": lambda df: ""
    },
    {
        "label": "Annual % Renewable Electricity (%)",
        "key": "annual_renewable_electricity",
        "bau_value": lambda df: safe_get(df, "outputs.Site.renewable_electricity_fraction_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.renewable_electricity_fraction")
    },
    {
        "label": "Year 1 CO2 Emissions (tonnes)",
        "key": "year_1_co2_emissions",
        "bau_value": lambda df: safe_get(df, "outputs.Site.annual_emissions_tonnes_CO2_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.annual_emissions_tonnes_CO2")
    },
    {
        "label": "CO2 Emissions (tonnes)",
        "key": "co2_emissions",
        "bau_value": lambda df: safe_get(df, "outputs.Site.lifecycle_emissions_tonnes_CO2_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.lifecycle_emissions_tonnes_CO2")
    },
    {
        "label": "CO2 (%) savings",
        "key": "co2_savings_percentage",
        "bau_value": lambda df: 0,
        "scenario_value": lambda df: 0
    },
    {
        "label": "Annual Energy Production & Throughput",
        "key": "energy_production_throughput_separator",
        "bau_value": lambda df: "",
        "scenario_value": lambda df: ""
    },
    {
        "label": "PV (kWh)",
        "key": "pv_kwh",
        "bau_value": lambda df: safe_get(df, "outputs.PV.annual_energy_produced_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.PV.annual_energy_produced_kwh")
    },
    {
        "label": "Wind (kWh)",
        "key": "wind_kwh",
        "bau_value": lambda df: safe_get(df, "outputs.Wind.annual_energy_produced_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Wind.annual_energy_produced_kwh")
    },
    {
        "label": "CHP (kWh)",
        "key": "chp_kwh",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.annual_electric_production_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.annual_electric_production_kwh")
    },
    {
        "label": "CHP (MMBtu)",
        "key": "chp_mmbtu",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.annual_thermal_production_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.annual_thermal_production_mmbtu")
    },
    {
        "label": "Boiler (MMBtu)",
        "key": "boiler_mmbtu",
        "bau_value": lambda df: safe_get(df, "outputs.ExistingBoiler.annual_thermal_production_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ExistingBoiler.annual_thermal_production_mmbtu")
    },
    {
        "label": "Battery (kWh)",
        "key": "battery_kwh",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricStorage.storage_to_load_series_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricStorage.storage_to_load_series_kw")
    },
    {
        "label": "HW-TES (MMBtu)",
        "key": "hw_tes_mmbtu",
        "bau_value": lambda df: safe_get(df, "outputs.HotThermalStorage.annual_energy_produced_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.HotThermalStorage.annual_energy_produced_mmbtu")
    },
    {
        "label": "CW-TES (MMBtu)",
        "key": "cw_tes_mmbtu",
        "bau_value": lambda df: safe_get(df, "outputs.ColdThermalStorage.annual_energy_produced_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ColdThermalStorage.annual_energy_produced_mmbtu")
    },
    {
        "label": "Breakdown of Incentives",
        "key": "breakdown_of_incentives_separator",
        "bau_value": lambda df: "",
        "scenario_value": lambda df: ""
    },
    {
        "label": "Federal Tax Incentive (30%)",
        "key": "federal_tax_incentive_30",
        "bau_value": lambda df: 0.3,
        "scenario_value": lambda df: 0.3
    },
    {
        "label": "PV Federal Tax Incentive (%)",
        "key": "pv_federal_tax_incentive",
        "bau_value": lambda df: safe_get(df, "inputs.PV.federal_itc_fraction_bau"),
        "scenario_value": lambda df: safe_get(df, "inputs.PV.federal_itc_fraction")
    },
    {
        "label": "Storage Federal Tax Incentive (%)",
        "key": "storage_federal_tax_incentive",
        "bau_value": lambda df: safe_get(df, "inputs.ElectricStorage.total_itc_fraction_bau"),
        "scenario_value": lambda df: safe_get(df, "inputs.ElectricStorage.total_itc_fraction")
    },
    # {
    #     "label": "Incentive Value ($)",
    #     "key": "incentive_value",
    #     "bau_value": lambda df: safe_get(df, "outputs.Financial.breakeven_cost_of_emissions_reduction_per_tonne_CO2_bau"),
    #     "scenario_value": lambda df: safe_get(df, "outputs.Financial.breakeven_cost_of_emissions_reduction_per_tonne_CO2")
    # },
    {
        "label": "Additional Grant ($)",
        "key": "iac_grant",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_production_incentive_after_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_production_incentive_after_tax")
    }
]

# IEDO TASC Configuration
custom_table_tasc = [
    {
        "label": "Site Name",
        "key": "site",
        "bau_value": lambda df: "",
        "scenario_value": lambda df: safe_get(df, "inputs.Meta.description", "None provided")
    },
    {
        "label": "Site Location",
        "key": "site_lat_long",
        "bau_value": lambda df: f"({safe_get(df, 'inputs.Site.latitude')}, {safe_get(df, 'inputs.Site.longitude')})",
        "scenario_value": lambda df: f"({safe_get(df, 'inputs.Site.latitude')}, {safe_get(df, 'inputs.Site.longitude')})"
    },
    {
        "label": "Site Address",
        "key": "site_address",
        "bau_value": lambda df: safe_get(df, "inputs.Meta.address", "None provided"),
        "scenario_value": lambda df: safe_get(df, "inputs.Meta.address", "None provided")
    },
    {
        "label": "PV Size (kW)",
        "key": "pv_size",
        "bau_value": lambda df: safe_get(df, "outputs.PV.size_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.PV.size_kw")
    },
    {
        "label": "Wind Size (kW)",
        "key": "wind_size",
        "bau_value": lambda df: safe_get(df, "outputs.Wind.size_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Wind.size_kw")
    },
    {
        "label": "CHP Size (kW)",
        "key": "chp_size",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.size_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.size_kw")
    },
    {
        "label": "PV Total Electricity Produced (kWh)",
        "key": "pv_total_electricity_produced",
        "bau_value": lambda df: safe_get(df, "outputs.PV.annual_energy_produced_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.PV.annual_energy_produced_kwh")
    },
    {
        "label": "PV Exported to Grid (kWh)",
        "key": "pv_exported_to_grid",
        "bau_value": lambda df: safe_get(df, "outputs.PV.electric_to_grid_series_kw"),
        "scenario_value": lambda df: safe_get(df, "outputs.PV.electric_to_grid_series_kw")
    },
    {
        "label": "PV Serving Load (kWh)",
        "key": "pv_serving_load",
        "bau_value": lambda df: safe_get(df, "outputs.PV.electric_to_load_series_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.PV.electric_to_load_series_kw")
    },
    {
        "label": "Wind Total Electricity Produced (kWh)",
        "key": "wind_total_electricity_produced",
        "bau_value": lambda df: safe_get(df, "outputs.Wind.annual_energy_produced_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Wind.annual_energy_produced_kwh")
    },
    {
        "label": "Wind Exported to Grid (kWh)",
        "key": "wind_exported_to_grid",
        "bau_value": lambda df: safe_get(df, "outputs.Wind.electric_to_grid_series_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Wind.electric_to_grid_series_kw")
    },
    {
        "label": "Wind Serving Load (kWh)",
        "key": "wind_serving_load",
        "bau_value": lambda df: safe_get(df, "outputs.Wind.electric_to_load_series_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Wind.electric_to_load_series_kw")
    },
    {
        "label": "CHP Total Electricity Produced (kWh)",
        "key": "chp_total_electricity_produced",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.annual_electric_production_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.annual_electric_production_kwh")
    },
    {
        "label": "CHP Exported to Grid (kWh)",
        "key": "chp_exported_to_grid",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.electric_to_grid_series_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.electric_to_grid_series_kw")
    },
    {
        "label": "CHP Serving Load (kWh)",
        "key": "chp_serving_load",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.electric_to_load_series_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.electric_to_load_series_kw")
    },
    {
        "label": "CHP Serving Thermal Load (MMBtu)",
        "key": "chp_serving_thermal_load",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.thermal_to_load_series_mmbtu_per_hour_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.thermal_to_load_series_mmbtu_per_hour")
    },
    {
        "label": "Grid Purchased Electricity (kWh)",
        "key": "grid_purchased_electricity",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricUtility.annual_energy_supplied_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricUtility.annual_energy_supplied_kwh")
    },
    {
        "label": "Total Site Electricity Use (kWh)",
        "key": "total_site_electricity_use",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricUtility.electric_to_load_series_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricUtility.electric_to_load_series_kw")
    },
    {
        "label": "Net Purchased Electricity Reduction (%)",
        "key": "net_purchased_electricity_reduction",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricUtility.electric_to_load_series_kwsdf_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricUtility.electric_to_load_series_kwsdf")
    },
    {
        "label": "Electricity Energy Cost ($)",
        "key": "electricity_energy_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_energy_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_energy_cost_before_tax")
    },
    {
        "label": "Electricity Demand Cost ($)",
        "key": "electricity_demand_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_demand_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_demand_cost_before_tax")
    },
    {
        "label": "Utility Fixed Cost ($)",
        "key": "utility_fixed_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_fixed_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_fixed_cost_before_tax")
    },
    {
        "label": "Purchased Electricity Cost ($)",
        "key": "purchased_electricity_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_bill_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_bill_before_tax")
    },
    {
        "label": "Electricity Export Benefit ($)",
        "key": "electricity_export_benefit",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_export_benefit_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_export_benefit_before_tax")
    },
    {
        "label": "Net Electricity Cost ($)",
        "key": "net_electricity_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.lifecycle_energy_cost_after_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.lifecycle_energy_cost_after_tax")
    },
    {
        "label": "Electricity Cost Savings ($/year)",
        "key": "electricity_cost_savings",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.lifecycle_energy_cost_after_tax_bau_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.lifecycle_energy_cost_after_tax_bau")
    },
    {
        "label": "Boiler Fuel (MMBtu)",
        "key": "boiler_fuel",
        "bau_value": lambda df: safe_get(df, "outputs.ExistingBoiler.fuel_used_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ExistingBoiler.fuel_used_mmbtu")
    },
    {
        "label": "CHP Fuel (MMBtu)",
        "key": "chp_fuel",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.annual_fuel_consumption_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.annual_fuel_consumption_mmbtu")
    },
    {
        "label": "Total Fuel (MMBtu)",
        "key": "total_fuel",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricUtility.total_energy_supplied_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricUtility.total_energy_supplied_kwh")
    },
    {
        "label": "Natural Gas Reduction (%)",
        "key": "natural_gas_reduction",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricUtility.annual_energy_supplied_kwh_bau_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricUtility.annual_energy_supplied_kwh_bau")
    },
    {
        "label": "Boiler Thermal Production (MMBtu)",
        "key": "boiler_thermal_production",
        "bau_value": lambda df: safe_get(df, "outputs.ExistingBoiler.annual_thermal_production_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ExistingBoiler.annual_thermal_production_mmbtu")
    },
    {
        "label": "CHP Thermal Production (MMBtu)",
        "key": "chp_thermal_production",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.annual_thermal_production_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.annual_thermal_production_mmbtu")
    },
    {
        "label": "Total Thermal Production (MMBtu)",
        "key": "total_thermal_production",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.annual_thermal_production_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.annual_thermal_production_mmbtu")
    },
    {
        "label": "Heating System Fuel Cost ($)",
        "key": "heating_system_fuel_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Site.heating_system_fuel_cost_us_dollars_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.heating_system_fuel_cost_us_dollars")
    },
    {
        "label": "CHP Fuel Cost ($)",
        "key": "chp_fuel_cost",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.year_one_fuel_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.year_one_fuel_cost_before_tax")
    },
    {
        "label": "Total Fuel (NG) Cost ($)",
        "key": "total_fuel_ng_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Site.total_fuel_cost_us_dollars_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.total_fuel_cost_us_dollars")
    },
    {
        "label": "Total Utility Cost ($)",
        "key": "total_utility_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Site.total_utility_cost_us_dollars_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.total_utility_cost_us_dollars")
    },
    {
        "label": "O&M Cost Increase ($)",
        "key": "om_cost_increase",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.om_and_replacement_present_cost_after_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.om_and_replacement_present_cost_after_tax")
    },
    {
        "label": "Payback Period (years)",
        "key": "payback_period",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.simple_payback_years_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.simple_payback_years")
    },
    {
        "label": "Gross Capital Cost ($)",
        "key": "gross_capital_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_capital_costs_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_capital_costs")
    },
    {
        "label": "Federal Tax Incentive (30%)",
        "key": "federal_tax_incentive",
        "bau_value": lambda df: 0.3,
        "scenario_value": lambda df: 0.3
    },
    {
        "label": "Additional Grant ($)",
        "key": "additional_grant",
        "bau_value": lambda df: 0,  
        "scenario_value": lambda df: 0
    },
    {
        "label": "Incentive Value ($)",
        "key": "incentive_value",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.total_incentives_value_us_dollars_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.total_incentives_value_us_dollars")
    },
    {
        "label": "Net Capital Cost ($)",
        "key": "net_capital_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.net_capital_cost_us_dollars_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.net_capital_cost_us_dollars")
    },
    {
        "label": "Annual Cost Savings ($)",
        "key": "annual_cost_savings",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.annual_cost_savings_us_dollars_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.annual_cost_savings_us_dollars")
    },
    {
        "label": "Simple Payback (years)",
        "key": "simple_payback",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.simple_payback_years_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.simple_payback_years")
    },
    {
        "label": "CO2 Emissions (tonnes)",
        "key": "co2_emissions",
        "bau_value": lambda df: safe_get(df, "outputs.Site.annual_emissions_tonnes_CO2_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.annual_emissions_tonnes_CO2")
    },
    {
        "label": "CO2 Reduction (tonnes)",
        "key": "co2_reduction",
        "bau_value": lambda df: safe_get(df, "outputs.Site.lifecycle_emissions_tonnes_CO2_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.lifecycle_emissions_tonnes_CO2")
    },
    {
        "label": "CO2 (%) savings",
        "key": "co2_savings_percentage",
        "bau_value": lambda df: 0,
        "scenario_value": lambda df: 0
    },
    {
        "label": "NPV ($)",
        "key": "npv",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.npv_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.npv")
    },
    {
        "label": "PV Federal Tax Incentive (%)",
        "key": "pv_federal_tax_incentive",
        "bau_value": lambda df: safe_get(df, "inputs.PV.federal_itc_fraction_bau"),
        "scenario_value": lambda df: safe_get(df, "inputs.PV.federal_itc_fraction")
    },
    {
        "label": "Storage Federal Tax Incentive (%)",
        "key": "storage_federal_tax_incentive",
        "bau_value": lambda df: safe_get(df, "inputs.ElectricStorage.total_itc_fraction_bau"),
        "scenario_value": lambda df: safe_get(df, "inputs.ElectricStorage.total_itc_fraction")
    }
]

'''
 2. Defining BAU Columns:
------------------------
- If your calculation involves BAU (Business As Usual) columns, ensure that the relevant BAU columns are included in the `bau_cells_config` dictionary. Each key in this dictionary represents a BAU variable used in calculations, and the value is the corresponding table label.

- Example `bau_cells_config` for BAU references:
  bau_cells_config = {
      "grid_value": "Grid Purchased Electricity (kWh)",
      "elec_cost_value": "Purchased Electricity Cost ($)",
  }
  
- When defining calculations that use BAU columns, reference the BAU values using the `bau` dictionary. For example, to calculate the optimal reduction in grid electricity purchases compared to BAU:
  "formula": lambda col, bau, headers: f'=({bau["grid_value"]} - {col}{headers["Grid Purchased Electricity (kWh)"] + 2}) / {bau["grid_value"]}'

- Note: the bau cell has to be associated with a variable name in the custom table
- Note: It is safe to define bau cells that are not being used. If they are not associated with an entry in the custom table, they will be safely ignored
'''

# Define bau_cells configuration for calculations that reference bau cells
bau_cells_config = {
    "grid_value"         : "Grid Purchased Electricity (kWh)",
    "elec_cost_value"    : "Purchased Electricity Cost ($)",
    "ng_reduction_value" : "Total Fuel (MMBtu)",
    "total_elec_costs"   : "Total Electric Costs ($)",
    "total_fuel_costs"   : "Total Fuel Costs ($)",
    "co2_reduction_value": "CO2 Emissions (tonnes)",
    "placeholder1_value" : "Placeholder1"
}

'''
3. Defining Calculations:
-------------------------
- Each calculation should be defined using a dictionary with the following structure:
  {
      "name": <calculation_name>,    # The name of the calculation (matches the label in the table)
      "formula": <lambda_function>   # A lambda function that calculates the desired value
  }

- The lambda function receives the following parameters:
  - `col`: The column letter for the scenario data in Excel.
  - `bau`: A dictionary of BAU cell references (if applicable).
  - `headers`: A dictionary containing the row indices for relevant table headers.

  Example Calculation:
  {
      "name": "Net Purchased Electricity Reduction (%)",
      "formula": lambda col, bau, headers: f'=({bau["grid_value"]} - {col}{headers["Grid Purchased Electricity (kWh)"] + 2}) / {bau["grid_value"]}'
  }
  - Note: The calculation name has to be the same as a variable in the custom table
  - Note: It is safe to define calculations that are not being used, if they are not associated with an entry in the custom table, it will be ignored
  '''
  
# Calculation logic
calculations_config = [
    {
        "name": "Total Site Electricity Use (kWh)",
        "formula": lambda col, bau, headers: (
            f'={col}{headers["PV Serving Load (kWh)"] + 2}+'
            f'{col}{headers["Wind Serving Load (kWh)"] + 2}+'
            f'{col}{headers["CHP Serving Load (kWh)"] + 2}+'
            f'{col}{headers["Battery Serving Load (kWh)"] + 2}+'
            f'{col}{headers["Backup Generator Serving Load (kWh)"] + 2}+'
            f'{col}{headers["Steam Turbine Serving Load (kWh)"] + 2}+'
            f'{col}{headers["Grid Purchased Electricity (kWh)"] + 2}'
        )
    },
    
    {
        "name": "Net Purchased Electricity Reduction (%)",
        "formula": lambda col, bau, headers: f'=({bau["grid_value"]}-{col}{headers["Grid Purchased Electricity (kWh)"] + 2})/{bau["grid_value"]}'
    },
    {
        "name": "Purchased Electricity Cost ($)",
        "formula": lambda col, bau, headers: f'={col}{headers["Energy Charges ($)"] + 2}+{col}{headers["Demand Charges ($)"] + 2}+{col}{headers["Fixed Charges ($)"] + 2}'
    },
    {
        "name": "Net Electricity Cost ($)",
        "formula": lambda col, bau, headers: f'={col}{headers["Purchased Electricity Cost ($)"] + 2}-{col}{headers["Electricity Export Benefit ($)"] + 2}'
    },
    {
        "name": "Electricity Cost Savings ($/year)",
        "formula": lambda col, bau, headers: f'={bau["elec_cost_value"]}-{col}{headers["Purchased Electricity Cost ($)"] + 2}'
    },
    {
        "name": "Total Fuel (MMBtu)",
        "formula": lambda col, bau, headers: f'={col}{headers["Boiler Fuel (MMBtu)"] + 2}+{col}{headers["CHP Fuel (MMBtu)"] + 2}'
    },
    {
        "name": "Natural Gas Reduction (%)",
        "formula": lambda col, bau, headers: f'=({bau["ng_reduction_value"]}-{col}{headers["Total Fuel (MMBtu)"] + 2})/{bau["ng_reduction_value"]}'
    },
    {
        "name": "Total Thermal Production (MMBtu)",
        "formula": lambda col, bau, headers: f'={col}{headers["Boiler Thermal Production (MMBtu)"] + 2}+{col}{headers["CHP Thermal Production (MMBtu)"] + 2}'
    },
    # {
    #     "name": "Total Fuel Costs ($)",
    #     "formula": lambda col, bau, headers: f'={col}{headers["Heating System Fuel Cost ($)"] + 2}+{col}{headers["CHP Fuel Cost ($)"] + 2}'
    # },
    {
        "name": "Total Utility Costs ($)",
        "formula": lambda col, bau, headers: f'={col}{headers["Total Electric Costs ($)"] + 2}+{col}{headers["Total Fuel Costs ($)"] + 2}'
    },
    # {
    #     "name": "Incentive Value ($)",
    #     "formula": lambda col, bau, headers: f'=({col}{headers["Federal Tax Incentive (30%)"] + 2}*{col}{headers["Gross Capital Cost ($)"] + 2})+{col}{headers["Additional Grant ($)"] + 2}'
    # },
    # {
    #     "name": "Net Capital Cost ($)",
    #     "formula": lambda col, bau, headers: f'={col}{headers["Gross Capital Cost ($)"] + 2}-{col}{headers["Incentive Value ($)"] + 2}'
    # },
    {
        "name": "Annual Cost Savings ($)",
        "formula": lambda col, bau, headers: f'={bau["elec_cost_value"]}+-{col}{headers["Purchased Electricity Cost ($)"] + 2}'
    },
    {
        "name": "Simple Payback (years)",
        "formula": lambda col, bau, headers: f'={col}{headers["Net Capital Cost ($)"] + 2}/{col}{headers["Annual Cost Savings ($)"] + 2}'
    },
    # {
    #     "name": "CO2 Reduction (tonnes)",
    #     "formula": lambda col, bau, headers: f'={bau["co2_reduction_value"]}-{col}{headers["CO2 Emissions (tonnes)"] + 2}'
    # },
    {
        "name": "CO2 (%) savings",
        "formula": lambda col, bau, headers: f'=({bau["co2_reduction_value"]}-{col}{headers["CO2 Emissions (tonnes)"] + 2})/{bau["co2_reduction_value"]}'
    },
    #Example Calculations
    # Calculation Without Reference to bau_cells
    {
        "name": "Placeholder Calculation Without BAU Reference",
        "formula": lambda col, bau, headers: f'={col}{headers["Placeholder1"] + 2}+{col}{headers["Placeholder2"] + 2}'
        # This formula adds Placeholder1 and Placeholder2 values from the scenario.
    },

    # Calculation With Reference to bau_cells
    {
        "name": "Placeholder Calculation With BAU Reference",
        "formula": lambda col, bau, headers: f'=({bau["placeholder1_value"]}-{col}{headers["Placeholder2"] + 2})/{bau["placeholder1_value"]}'
        # This formula calculates the percentage change of Placeholder2 using Placeholder1's BAU value as the reference.
    }
]