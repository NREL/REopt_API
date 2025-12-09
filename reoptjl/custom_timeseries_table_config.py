# custom_timeseries_table_config.py
from reoptjl.custom_timeseries_table_helpers import safe_get_list, safe_get_value, safe_get

"""
Timeseries Table Configuration
===============================
This file defines configurations for timeseries Excel tables that display hourly or sub-hourly data.
Each configuration specifies which columns to include, how to extract the data, and how to format the Excel output.

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
    "units": str,               # Optional: Units to display in header (e.g., "($/kWh)", "(kW)")
    "column_width": float,      # Optional: Column width in Excel (default: 15)
    "num_format": str,          # Optional: Excel number format (e.g., '#,##0', 'm/d/yyyy h:mm')
}

Formatting Configuration:
-------------------------
Each configuration should also include a "formatting" dictionary with Excel formatting options:
{
    "worksheet_name": str,                  # Name of the Excel worksheet
    "base_header_color": str,              # Hex color for base column headers (e.g., '#0B5E90')
    "scenario_header_colors": list[str],   # List of hex colors for scenario column headers
    "header_format": dict,                 # xlsxwriter format options for headers (bold, font_color, border, etc.)
    "data_format": dict,                   # xlsxwriter format options for data cells (border, align, valign)
    "freeze_panes": tuple,                 # Row and column to freeze (e.g., (1, 0) freezes top row)
}

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

# Formatting configuration for energy and demand rate timeseries
timeseries_energy_demand_formatting = {
    "worksheet_name": "Timeseries Data",
    "base_header_color": "#0B5E90",
    "scenario_header_colors": [
        "#50AEE9",  # Blue (first rate)
        '#2E7D32',  # Green (second rate)
        '#D32F2F',  # Red (third rate)
        '#F57C00',  # Orange (fourth rate)
        '#7B1FA2',  # Purple (fifth rate)
        '#0097A7',  # Cyan (sixth rate)
        '#C2185B',  # Pink (seventh rate)
        '#5D4037',  # Brown (eighth rate)
    ],
    "header_format": {
        'bold': True,
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True
    },
    "data_format": {
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    },
    "freeze_panes": (1, 0)  # Freeze top row
}

# Configuration for energy and demand rate timeseries
custom_timeseries_energy_demand = {
    "columns": [
        {
            "label": "Date Timestep",
            "key": "datetime",
            "timeseries_path": lambda df: safe_get(df, "inputs.ElectricLoad.year"),  # Used to generate datetime column based on year and time_steps_per_hour
            "is_base_column": True,
            "column_width": 15,
            "num_format": "m/d/yyyy h:mm"
        },
        {
            "label": "Load (kW)",
            "key": "load_kw",
            "timeseries_path": lambda df: safe_get(df, "outputs.ElectricLoad.load_series_kw"),
            "is_base_column": True,
            "column_width": 11,
            "num_format": "#,##0"
        },
        {
            "label": "Peak Monthly Load (kW)",
            "key": "peak_monthly_load_kw",
            "timeseries_path": lambda df: safe_get(df, "outputs.ElectricLoad.monthly_peaks_kw"),  # 12-element array, needs special handling to repeat for each timestep
            "is_base_column": True,
            "column_width": 15,
            "num_format": "#,##0"
        },
        {
            "label": "Energy Charge",
            "key": "energy_charge",
            "timeseries_path": lambda df: safe_get(df, "outputs.ElectricTariff.energy_rate_average_series"),
            "is_base_column": False,  # Repeats for each scenario
            "units": "($/kWh)",
            "column_width": 25,
            "num_format": "#,##0.00000"
        },
        {
            "label": "Demand Charge",
            "key": "demand_charge",
            "timeseries_path": lambda df: safe_get(df, "outputs.ElectricTariff.demand_rate_average_series"),
            "is_base_column": False,  # Repeats for each scenario
            "units": "($/kW)",
            "column_width": 25,
            "num_format": "#,##0.00"
        }
    ],
    "formatting": timeseries_energy_demand_formatting
}

# Example configuration for emissions timeseries (can be expanded as needed)
custom_timeseries_emissions = {
    "columns": [
        {
            "label": "Date Timestep",
            "key": "datetime",
            "timeseries_path": lambda df: safe_get(df, "inputs.ElectricLoad.year"),
            "is_base_column": True,
            "column_width": 18,
            "num_format": "m/d/yyyy h:mm"
        },
        {
            "label": "Grid Emissions",
            "key": "grid_emissions",
            "timeseries_path": lambda df: safe_get(df, "inputs.ElectricUtility.emissions_factor_series_lb_CO2_per_kwh"),
            "is_base_column": False,
            "units": "(lb CO2/kWh)",
            "column_width": 15,
            "num_format": "#,##0.00000"
        },
        {
            "label": "Grid Energy",
            "key": "grid_to_load",
            "timeseries_path": lambda df: safe_get(df, "outputs.ElectricUtility.electric_to_load_series_kw"),
            "is_base_column": False,
            "units": "(kWh)",
            "column_width": 15,
            "num_format": "#,##0.00"
        }
    ],
    "formatting": {
        "worksheet_name": "Emissions Data",
        "base_header_color": "#0B5E90",
        "scenario_header_colors": ["#50AEE9", '#2E7D32', '#D32F2F', '#F57C00', '#7B1FA2', '#0097A7', '#C2185B', '#5D4037'],
        "header_format": {
            'bold': True,
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        },
        "data_format": {
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        },
        "freeze_panes": (1, 0)
    }
}

# Example configuration for load profiles (can be expanded as needed)
custom_timeseries_loads = {
    "columns": [
        {
            "label": "Date Timestep",
            "key": "datetime",
            "timeseries_path": lambda df: safe_get(df, "inputs.ElectricLoad.year"),
            "is_base_column": True,
            "column_width": 18,
            "num_format": "m/d/yyyy h:mm"
        },
        {
            "label": "Total Load",
            "key": "total_load",
            "timeseries_path": lambda df: safe_get(df, "outputs.ElectricLoad.load_series_kw"),
            "is_base_column": True,
            "units": "(kW)",
            "column_width": 15,
            "num_format": "#,##0.00"
        },
        {
            "label": "Critical Load",
            "key": "critical_load",
            "timeseries_path": lambda df: safe_get(df, "outputs.ElectricLoad.critical_load_series_kw"),
            "is_base_column": True,
            "units": "(kW)",
            "column_width": 15,
            "num_format": "#,##0.00"
        }
    ],
    "formatting": {
        "worksheet_name": "Load Profiles",
        "base_header_color": "#0B5E90",
        "scenario_header_colors": ["#50AEE9", '#2E7D32', '#D32F2F', '#F57C00', '#7B1FA2', '#0097A7', '#C2185B', '#5D4037'],
        "header_format": {
            'bold': True,
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        },
        "data_format": {
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        },
        "freeze_panes": (1, 0)
    }
}
