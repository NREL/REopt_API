# custom_timeseries_table_config.py
from reoptjl.timeseries_table_helpers import safe_get_list, safe_get_value, safe_get

"""
Timeseries Table Configuration
===============================
This file defines configurations for timeseries Excel tables that display hourly or sub-hourly data.
Each configuration specifies which columns to include and how to extract the data.

Naming Convention:
------------------
Structure: custom_timeseries_<feature>

- `custom_timeseries_`: Prefix indicating a timeseries table configuration
- `<feature>`: Descriptive name for the specific timeseries configuration

Examples:
- custom_timeseries_energy_demand: Configuration for energy and demand rate timeseries
- custom_timeseries_emissions: Configuration for emissions timeseries
- custom_timeseries_loads: Configuration for load profiles

Guidelines:
- Use lowercase letters and underscores
- Keep names descriptive and concise
- Each configuration is a list of column dictionaries

Column Dictionary Structure:
-----------------------------
Each column configuration should have:
{
    "label": str,               # Column header text
    "key": str,                 # Unique identifier for the column
    "timeseries_path": str,     # Dot-separated path to data in the results JSON (e.g., "outputs.ElectricLoad.load_series_kw")
    "is_base_column": bool,     # True if column comes from first scenario only, False if repeated for all scenarios
    "units": str                # Optional: Units to display in header (e.g., "($/kWh)", "(kW)")
}

Note: Formatting (Excel number formats, column widths, colors) is handled in views.py, not in this configuration file.

Special Column Types:
---------------------
1. DateTime column: Must have key="datetime" and will be auto-generated based on year and time_steps_per_hour
2. Base columns: Set is_base_column=True for columns that only use data from the first run_uuid
3. Scenario columns: Set is_base_column=False for columns that repeat for each run_uuid

Rate Name Headers:
------------------
For scenario columns (is_base_column=False), the column header will automatically include the rate name
from inputs.ElectricTariff.urdb_metadata.rate_name for each scenario.
"""

# Configuration for energy and demand rate timeseries
# This configuration specifies which data fields to extract from the results.
# Formatting (number formats, colors, widths) is handled in views.py
custom_timeseries_energy_demand = [
    {
        "label": "Date Timestep",
        "key": "datetime",
        "timeseries_path": lambda df: safe_get(df, "inputs.ElectricLoad.year"),  # Used to generate datetime column based on year and time_steps_per_hour
        "is_base_column": True
    },
    {
        "label": "Load (kW)",
        "key": "load_kw",
        "timeseries_path": lambda df: safe_get(df, "outputs.ElectricLoad.load_series_kw"),
        "is_base_column": True
    },
    {
        "label": "Peak Monthly Load (kW)",
        "key": "peak_monthly_load_kw",
        "timeseries_path": lambda df: safe_get(df, "outputs.ElectricLoad.monthly_peaks_kw"),  # 12-element array, needs special handling to repeat for each timestep
        "is_base_column": True
    },
    {
        "label": "Energy Charge",
        "key": "energy_charge",
        "timeseries_path": lambda df: safe_get(df, "outputs.ElectricTariff.energy_rate_average_series"),
        "is_base_column": False,  # Repeats for each scenario
        "units": "($/kWh)"
    },
    {
        "label": "Demand Charge",
        "key": "demand_charge",
        "timeseries_path": lambda df: safe_get(df, "outputs.ElectricTariff.demand_rate_average_series"),
        "is_base_column": False,  # Repeats for each scenario
        "units": "($/kW)"
    }
]

# Example configuration for emissions timeseries (can be expanded as needed)
custom_timeseries_emissions = [
    {
        "label": "Date Timestep",
        "key": "datetime",
        "timeseries_path": lambda df: safe_get(df, "inputs.ElectricLoad.year"),
        "is_base_column": True
    },
    {
        "label": "Grid Emissions",
        "key": "grid_emissions",
        "timeseries_path": lambda df: safe_get(df, "inputs.ElectricUtility.emissions_factor_series_lb_CO2_per_kwh"),
        "is_base_column": True,
        "units": "(lb CO2/kWh)"
    },
    {
        "label": "Grid Energy",
        "key": "grid_to_load",
        "timeseries_path": lambda df: safe_get(df, "outputs.ElectricUtility.electric_to_load_series_kw"),
        "is_base_column": False,
        "units": "(kWh)"
    }
]

# Example configuration for load profiles (can be expanded as needed)
custom_timeseries_loads = [
    {
        "label": "Date Timestep",
        "key": "datetime",
        "timeseries_path": lambda df: safe_get(df, "inputs.ElectricLoad.year"),
        "is_base_column": True
    },
    {
        "label": "Total Load",
        "key": "total_load",
        "timeseries_path": lambda df: safe_get(df, "outputs.ElectricLoad.load_series_kw"),
        "is_base_column": True,
        "units": "(kW)"
    },
    {
        "label": "Critical Load",
        "key": "critical_load",
        "timeseries_path": lambda df: safe_get(df, "outputs.ElectricLoad.critical_load_series_kw"),
        "is_base_column": True,
        "units": "(kW)"
    }
]
