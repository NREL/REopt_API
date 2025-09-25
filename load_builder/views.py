# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/load_builder/views.py
import csv
import io
import json
import sys
import numpy as np
from django.http import JsonResponse
from reo.exceptions import UnexpectedError

try:
    from ensitepy.simextension import enlitepyapi
except ImportError:
    enlitepyapi = None

# EnLitePy Configuration Constants
DEFAULT_CHARGER_DEFAULTS = {
    "L1": {"count": 0, "power_kW": 2.4, "eff": 0.80, "pci": "LD"},
    "L2": {"count": 0, "power_kW": 13.0, "eff": 0.80, "pci": "LD"},
    "DCFC_LD": {"count": 0, "power_kW": 50.0, "eff": 0.90, "pci": "LD"},
    "DCFC_MDHD": {"count": 0, "power_kW": 250.0, "eff": 0.90, "pci": "MD/HD"},
}

DEFAULT_VEHICLE_DEFAULTS = {
    "LD": {"weekday": 0, "weekend": 0, "battery_kWh": 80, "initSOC": 0.10, "targetSOC": 0.80, "pChgMax_kW": 120},
    "MD": {"weekday": 0, "weekend": 0, "battery_kWh": 200, "initSOC": 0.20, "targetSOC": 0.80, "pChgMax_kW": 300},
    "HD": {"weekday": 0, "weekend": 0, "battery_kWh": 500, "initSOC": 0.30, "targetSOC": 0.85, "pChgMax_kW": 600},
}

SIM_DAYS = 7
EMS_CONFIG = {"type": "basic", "pChgCap": 500_000, "pap": "FCFS+SMX"}
BASE_SIM_CONFIG = {"tStart": 0, "tEnd": 7 * 24 * 3600, "dowStart": 0}
RESULTS_CONFIG_BASE = {"timeseriesDt": 3600, "powerMetricsDt": 3600}
WEEK_TO_YEAR_SCALE = 365 / 7

# Keys for annual scaling
EQUIPMENT_ANNUAL_SCALARS = {"Energy output [kWh]", "Energy loss [kWh]"}
EV_COUNT_SCALARS = {"Total EVs arrived [#]", "Total unique EVs arrived [#]", "EVs no queue wait [#]", "EVs arrived but not charged [#]", "EVs that did not start/complete charge [#]"}
EV_ENERGY_SCALARS = {"Total energy charged [kWh]"}

# ---------------------------------------------------------------------------
# EnLitePy Helper Functions
# ---------------------------------------------------------------------------

def build_arrival_pmf(weekday_pct, weekend_pct, bucket_hours=2):
    """Convert UI bucket percentages to API arrivalTimePMF structure."""
    bucket_seconds = bucket_hours * 3600

    def normalize(side, label):
        if len(side) != 12:
            raise ValueError(f"{label} arrival array must have 12 entries (got {len(side)})")
        if any(x < 0 for x in side):
            raise ValueError(f"{label} arrival percentages must be non-negative")
        active = [(i, x) for i, x in enumerate(side) if x > 0]
        if not active:  # fallback deterministic midnight arrival
            return {"val": [0], "prob": [1.0], "dur": bucket_seconds}
        total = sum(x for _, x in active)
        vals = [i * bucket_seconds for i, _ in active]
        probs = [x / total for _, x in active]
        # Adjust final probability for floating sum errors
        diff = 1.0 - sum(probs)
        if abs(diff) > 1e-9:
            probs[-1] += diff
        return {"val": vals, "prob": [round(p, 6) for p in probs], "dur": bucket_seconds}

    return {"1-5": normalize(weekday_pct, "Weekday"), "0,6": normalize(weekend_pct, "Weekend")}


def build_enlitepy_payload(ui_inputs=None):
    """Build EnLitePy payload from UI inputs or use defaults."""
    # Apply UI overrides or use defaults
    charger_config = ui_inputs.get("chargers", {}) if ui_inputs else {}
    vehicle_config = ui_inputs.get("vehicles", {}) if ui_inputs else {}
    arrival_config = ui_inputs.get("arrival", {}) if ui_inputs else {}
    max_duration = ui_inputs.get("maxChargeDurationMin") if ui_inputs else None
    
    # Deep merge with defaults
    chargers = {}
    for cat, defaults in DEFAULT_CHARGER_DEFAULTS.items():
        chargers[cat] = {**defaults}
        if cat in charger_config:
            chargers[cat].update(charger_config[cat])
    
    vehicles = {}
    for vtype, defaults in DEFAULT_VEHICLE_DEFAULTS.items():
        vehicles[vtype] = {**defaults}
        if vtype in vehicle_config:
            vehicles[vtype].update(vehicle_config[vtype])
    
    # Arrival patterns
    weekday_pct = arrival_config.get("weekday", [0] * 12)
    weekend_pct = arrival_config.get("weekend", [0] * 12)
    
    # Build nodes
    nodes = {"grid": {"type": "Grid", "pMax": 500_000, "pMin": 0, "eff": 0.99}}
    
    # Add EVSE nodes
    for cat, cfg in chargers.items():
        for i in range(1, cfg["count"] + 1):
            nodes[f"EVSE_{cat}_{i}"] = {
                "type": "EVSE",
                "pMax": int(cfg["power_kW"] * 1000),
                "pMin": 0,
                "eff": cfg["eff"],
                "nEVPort": 1,
                "pci": cfg["pci"],
            }
    
    # Build EV types
    def expand_counts(weekend, weekday):
        return [weekend, weekday, weekday, weekday, weekday, weekday, weekend]
    
    weekday_weekend = {k: expand_counts(v["weekend"], v["weekday"]) for k, v in vehicles.items()}
    arrival_pmf = build_arrival_pmf(weekday_pct, weekend_pct)
    
    ev_types = {}
    for k, v in vehicles.items():
        delta = max(0.0, min(1.0, v["targetSOC"] - v["initSOC"]))
        ev_types[k] = {
            "type": k,
            "eCap": int(v["battery_kWh"] * 1000),
            "pChgMax": int(v["pChgMax_kW"] * 1000),
            "count": weekday_weekend[k],
            "targetFinalSOCPMF": {"val": [round(v["targetSOC"], 4)], "prob": [1.0]},
            "energyDemandPMF": {"val": [round(delta, 4)], "prob": [1.0]},
            "arrivalTimePMF": arrival_pmf,
            "departureTimePMF": None,
        }
    
    sim_cfg = dict(BASE_SIM_CONFIG)
    sim_cfg["tEnd"] = SIM_DAYS * 24 * 3600
    
    duration_max = None
    if max_duration is not None:
        duration_max = int(max_duration * 60)  # Convert minutes to seconds
    
    return {
        "simConfig": sim_cfg,
        "hubConfig": {"nodes": nodes, "ems": EMS_CONFIG},
        "evInfo": {"stochasticModel": 1, "chgDurMax": duration_max, "evTypes": ev_types},
        "resultsConfig": {
            **RESULTS_CONFIG_BASE,
            "resultFieldOptions": {
                "nodes": "Grid",
                "portUsage": True,
                "queueLength": True,
                "nodeStats": True,
                "evStats": True,
            },
        },
    }


def is_ui_input(data):
    """Detect if input is UI format vs direct EnLitePy payload."""
    if not isinstance(data, dict):
        return False
    
    # Check for UI-specific keys
    ui_keys = {"chargers", "vehicles", "arrival", "maxChargeDurationMin"}
    if any(key in data for key in ui_keys):
        return True
    
    # Check for direct EnLitePy payload keys
    enlitepy_keys = {"simConfig", "hubConfig", "evInfo", "resultsConfig"}
    if any(key in data for key in enlitepy_keys):
        return False
    
    # Default to UI format for safety
    return True

def ensite_view(request):
    """Enhanced EnLitePy endpoint that handles both UI inputs and direct payloads."""
    if enlitepyapi is not None:
        try:
            if request.method == 'POST':
                try:
                    input_data = json.loads(request.body)
                except json.JSONDecodeError as e:
                    return JsonResponse({"Error": f"Invalid JSON in request body: {e}"}, status=400)
                if is_ui_input(input_data):
                    try:
                        enlitepy_payload = build_enlitepy_payload(input_data)
                    except Exception as e:
                        return JsonResponse({"Error": f"Failed to build EnLitePy payload: {e}"}, status=400)
                else:
                    enlitepy_payload = input_data
                try:
                    results = enlitepyapi.run(enlitepy_payload)
                    if isinstance(results, dict) and 'logs' not in results:
                        results['logs'] = []
                    # Always normalize and annualize for client convenience
                    _normalize_and_enrich(results)
                    results.setdefault('enrichment_version', 1)
                    return JsonResponse({"results": results})
                except Exception as e:
                    return JsonResponse({"Error": f"EnLitePy execution failed: {e}"}, status=500)
            else:
                return JsonResponse({"Error": "Must POST a JSON body for ensitepy."}, status=400)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value, exc_traceback, task='ensite')
            return JsonResponse({"Error": err.message}, status=500)
    else:
        return JsonResponse({"Error": "ensitepy is not installed."}, status=500)
    

def check_load_builder_inputs(loads_table):
    required_inputs = ["Power (W)", "Quantity", "% Run Time", "Start Mo.", "Stop Mo.", "Start Hr.", "Stop Hr."]
    for load in loads_table:
        inputs = load.keys()
        for required_input in required_inputs:
            if required_input in inputs:
                pass
            else:
                return False
    return True


def validate_load_builder_inputs(loads_table):
    numeric_inputs = ["Power (W)", "Quantity", "% Run Time"]
    hour_inputs = ["Start Hr.", "Stop Hr."]
    month_inputs = ["Start Mo.", "Stop Mo."]
    required_hours = list(np.linspace(0,24,25).astype(int))
    required_months= ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for load in loads_table:

        for numeric_input in numeric_inputs:
            try:
                float(load[numeric_input])
            except Exception:
                return False

        for month_input in month_inputs:
            if load[month_input] not in required_months:
                return False

        for hour_input in hour_inputs:
            if int(load[hour_input]) not in required_hours:
                return False

    return True


def load_builder(request):
    """
    Convert the SolarResilient Component Load Builder CSV into an 8760 Load
    :param request:
    :return: 8760 list for critical_load_kw input into REOpt
    """
    try:
        if request.method == 'POST':
            post = request.body
            try:
                # Try to import JSON, then fall back to CSV
                try:
                    loads_table = json.loads(post)
                except Exception:
                    loads_table = post.decode("utf-8")
                finally:
                    if not isinstance(loads_table, list):
                        csv_reader = csv.DictReader(io.StringIO(loads_table))
                        loads_table = list(csv_reader)
            except Exception:
                return JsonResponse({"Error": "Invalid JSON or CSV"})

            # Validation
            if not check_load_builder_inputs(loads_table):
                return JsonResponse({"Error": "There are missing required inputs. Must include the following: 'Power (W)', 'Quantity', '% Run Time', 'Start Mo.', 'Stop Mo.', 'Start Hr.', 'Stop Hr.'"})
            if not validate_load_builder_inputs(loads_table):
                return JsonResponse({"Error": "Some input values are invalid"})

            # Run conversion and respond
            loads_kw = convert_loads(loads_table)
            return JsonResponse({"critical_loads_kw": loads_kw})

        else:
            return JsonResponse({"Error": "Must POST a JSON based on the SolarResilient component based load builder downloadable CSV"})

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='load_builder')
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=500)


def convert_loads(loads_table):
    """
    Generates critical load profile from critical load builder
    :param loads_table: (json string) contain data from load table
    :return: (1 list) hourly load values (8,760 values) in kw
    """

    class Load:
        def __init__(self, power_total, start_hour, stop_hour, start_month, stop_month):
            self.power_total = power_total
            self.start_hour = start_hour
            self.stop_hour = stop_hour
            self.start_month = start_month
            self.stop_month = stop_month

    def translate_months(string):
        """
        Translate month names to number
        :param string: (str) name of month
        :return: (int) number of month
        """
        switcher = {
            "January": 0,
            "February": 1,
            "March": 2,
            "April": 3,
            "May": 4,
            "June": 5,
            "July": 6,
            "August": 7,
            "September": 8,
            "October": 9,
            "November": 10,
            "December": 11,
        }
        return switcher.get(string, 0)

    loads = []
    for row in loads_table:
        power = int(row["Power (W)"]) * int(row["Quantity"]) * (float(row["% Run Time"]) / 100) / 1000  # total hourly power in kW
        # checks if stop_month has a smaller value than start_month
        start_mo = int(translate_months(row["Start Mo."]))
        stop_mo = int(translate_months(row["Stop Mo."]))
        months = []
        if start_mo < stop_mo:
            months.append((start_mo, stop_mo))
        else:
            months.append((start_mo, 11))
            months.append((0, stop_mo))
        # check if fixture/appliance is running over midnight
        start_hr = int(row["Start Hr."])
        stop_hr = int(row["Stop Hr."])
        hours = []
        if start_hr <= stop_hr:
            hours.append((start_hr, stop_hr))
        else:
            hours.append((start_hr, 24))
            hours.append((0, stop_hr))
        for (start_mo, stop_mo) in months:
            for (start_hr, stop_hr) in hours:
                loads.append(Load(power, start_hr, stop_hr, start_mo, stop_mo))
    loads_kw = []
    days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    for month in range(12):
        number_days = days_per_month[month]
        for days in range(number_days):
            for hr in range(24):
                hour_load = 0
                for load in loads:
                    if load.start_month <= month and load.stop_month >= month:
                        if load.start_hour <= hr and load.stop_hour > hr:
                            hour_load += load.power_total
                loads_kw.append(hour_load)
    return loads_kw

# Annual scaling helper constants (reuse existing ones if defined)
EQUIPMENT_ANNUAL_SCALARS = {"Energy output [kWh]", "Energy loss [kWh]"}
EV_COUNT_SCALARS = {"Total EVs arrived [#]", "Total unique EVs arrived [#]", "EVs no queue wait [#]", "EVs arrived but not charged [#]", "EVs that did not start/complete charge [#]"}
EV_ENERGY_SCALARS = {"Total energy charged [kWh]"}

def _replicate_to_8760(series):
    if not isinstance(series, list) or len(series) == 0:
        return series
    if len(series) == 8760:
        return series
    reps = (8760 // len(series)) + 1
    return (series * reps)[:8760]

def _annualize_equipment(stats_list):
    if not isinstance(stats_list, list):
        return []
    out = []
    for row in stats_list:
        if not isinstance(row, dict):
            continue
        copy = row.copy()
        for k in EQUIPMENT_ANNUAL_SCALARS:
            v = copy.get(k)
            if isinstance(v, (int, float)):
                copy[k] = round(v * WEEK_TO_YEAR_SCALE, 2)
        out.append(copy)
    return out

def _annualize_ev(stats_list):
    if not isinstance(stats_list, list):
        return []
    out = []
    for row in stats_list:
        if not isinstance(row, dict):
            continue
        copy = row.copy()
        for k, v in list(copy.items()):
            if k in EV_COUNT_SCALARS or k in EV_ENERGY_SCALARS:
                if isinstance(v, (int, float)):
                    copy[k] = round(v * WEEK_TO_YEAR_SCALE, 2)
            if k.endswith('[min]') and isinstance(v, (int, float)):
                copy[k.replace('[min]', '[h]')] = round(v / 60.0, 2)
                del copy[k]
        out.append(copy)
    return out

def _add_grid_util(timeseries_dict, equip_annual):
    if not isinstance(timeseries_dict, dict):
        return
    power = timeseries_dict.get('power_in_grid')
    if not isinstance(power, list) or not power:
        return
    # Locate grid equipment row
    grid_row = None
    for r in equip_annual:
        if isinstance(r, dict) and r.get('Name') in ('grid', 'Grid'):
            grid_row = r
            break
    if not grid_row:
        return
    cap = grid_row.get('Power capacity [kW]')
    if not isinstance(cap, (int, float)) or cap <= 0:
        return
    sample = [v for v in power[:50] if isinstance(v, (int, float))]
    if not sample:
        return
    max_sample = max(sample)
    to_kw = 1000.0 if max_sample > cap * 1.1 else 1.0
    series_kw = [v / to_kw for v in power if isinstance(v, (int, float))]
    if not series_kw:
        return
    grid_row.setdefault('Min capacity utilization [kW]', round(min(series_kw), 2))
    grid_row.setdefault('Average capacity utilization [kW]', round(sum(series_kw) / len(series_kw), 2))


def _normalize_and_enrich(results_dict):
    if not isinstance(results_dict, dict):
        return
    # Normalize stringified JSON lists
    for key in ('equipment_statistics', 'ev_statistics'):
        val = results_dict.get(key)
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    results_dict[key] = parsed
            except json.JSONDecodeError:
                pass
    equipment = results_dict.get('equipment_statistics') or []
    evstats = results_dict.get('ev_statistics') or []
    timeseries = results_dict.get('timeseries')
    # Annual replication for timeseries
    if isinstance(timeseries, dict) and 'power_in_grid' in timeseries:
        annual_series = _replicate_to_8760(timeseries['power_in_grid'])
        if isinstance(annual_series, list) and len(annual_series) == 8760:
            timeseries['power_in_grid_annual'] = annual_series
    equip_annual = _annualize_equipment(equipment) if equipment else []
    ev_annual = _annualize_ev(evstats) if evstats else []
    if equip_annual:
        results_dict['equipment_statistics_annual'] = equip_annual
        _add_grid_util(timeseries, equip_annual)
    if ev_annual:
        results_dict['ev_statistics_annual'] = ev_annual
