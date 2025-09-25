#!/usr/bin/env python3
"""Run EnLitePy minimal logic against two endpoints (remote & local) with identical payload.

Features:
  * Reuses the canonical weekly payload (same as run_enlitepy_minimal.py structure)
  * Posts to --remote and --local (or one if desired)
  * Supports --clean / --annual / --validate identical semantics
  * Normalizes JSON-string statistics, produces annual derivatives (timeseries + *_annual stats)
  * Writes individual response JSONs plus a combined diff summary
  * Diff focuses on structure + key presence + simple numeric sanity (lengths, counts)

Usage examples:
    # Single line
    python run_enlitepy_compare.py --remote https://ensite-py312-reopt-dev-api.its.nrel.gov/stable/ensite --local http://localhost:8000/stable/ensite/ --clean --annual --validate

    # Multi-line (must escape line breaks with backslashes!)
    python run_enlitepy_compare.py \\
            --remote https://ensite-py312-reopt-dev-api.its.nrel.gov/stable/ensite \\
            --local http://localhost:8000/stable/ensite/ \\
            --clean --annual --validate

    # Using env vars (no flags needed if set)
    export ENLITEPY_REMOTE_URL="https://ensite-py312-reopt-dev-api.its.nrel.gov/stable/ensite"
    export ENLITEPY_LOCAL_URL="http://localhost:8000/stable/ensite/"
    python run_enlitepy_compare.py --clean --annual --validate

Outputs:
  remote_response.json / local_response.json
  compare_summary.json (diff + summary)
"""
from __future__ import annotations

import argparse
import json
import os
from statistics import mean
from typing import Any, Dict, List, Tuple

try:
    import requests  # type: ignore
except ImportError:
    requests = None  # type: ignore
    import urllib.request
    import urllib.error

# ---------------- Base constants (copy from minimal) -------------------------
DEFAULT_CHARGER_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "L1": {"count": 0, "power_kW": 2.4, "eff": 0.80, "pci": "LD"},
    "L2": {"count": 2, "power_kW": 13.0, "eff": 0.80, "pci": "LD"},
    "DCFC_LD": {"count": 0, "power_kW": 50.0, "eff": 0.90, "pci": "LD"},
    "DCFC_MDHD": {"count": 0, "power_kW": 250.0, "eff": 0.90, "pci": "MD/HD"},
}
DEFAULT_VEHICLE_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "LD": {"weekday": 5, "weekend": 2, "battery_kWh": 80, "initSOC": 0.10, "targetSOC": 0.80, "pChgMax_kW": 120}
}
ARRIVAL_WEEKDAY_PCT = [0,0,0,0,0,0,0,0,40,40,20,0]
ARRIVAL_WEEKEND_PCT = [0]*12
SIM_DAYS = 7
EMS_CONFIG = {"type": "basic", "pChgCap": 500_000, "pap": "FCFS+SMX"}
BASE_SIM_CONFIG = {"tStart": 0, "tEnd": 7 * 24 * 3600, "dowStart": 0}
RESULTS_CONFIG_BASE = {"timeseriesDt": 3600, "powerMetricsDt": 3600}
WEEK_TO_YEAR_SCALE = 365 / 7
EQUIPMENT_ANNUAL_SCALARS = {"Energy output [kWh]", "Energy loss [kWh]"}
EV_COUNT_SCALARS = {"Total EVs arrived [#]", "Total unique EVs arrived [#]", "EVs no queue wait [#]", "EVs arrived but not charged [#]", "EVs that did not start/complete charge [#]"}
EV_ENERGY_SCALARS = {"Total energy charged [kWh]"}

# ---------------- Payload build ---------------------------------------------

def build_arrival_pmf(weekday_pct: List[float], weekend_pct: List[float], bucket_hours: int = 2) -> Dict[str, Any]:
    bucket_seconds = bucket_hours * 3600
    def normalize(side: List[float]):
        active = [(i,x) for i,x in enumerate(side) if x>0]
        if not active:
            return {"val": [0], "prob": [1.0], "dur": bucket_seconds}
        total = sum(v for _,v in active)
        vals = [i*bucket_seconds for i,_ in active]
        probs = [v/total for _,v in active]
        diff = 1 - sum(probs)
        if abs(diff) > 1e-9:
            probs[-1] += diff
        return {"val": vals, "prob": [round(p,6) for p in probs], "dur": bucket_seconds}
    return {"1-5": normalize(weekday_pct), "0,6": normalize(weekend_pct)}

def build_payload(days: int = SIM_DAYS) -> Dict[str, Any]:
    nodes: Dict[str, Any] = {"grid": {"type": "Grid", "pMax": 500_000, "pMin": 0, "eff": 0.99}}
    for cat, cfg in DEFAULT_CHARGER_DEFAULTS.items():
        for i in range(1, cfg["count"] + 1):
            nodes[f"EVSE_{cat}_{i}"] = {
                "type": "EVSE", "pMax": int(cfg["power_kW"]*1000), "pMin": 0, "eff": cfg["eff"], "nEVPort": 1, "pci": cfg["pci"]
            }
    def expand(we:int, wd:int): return [we, wd, wd, wd, wd, wd, we]
    weekday_weekend = {k: expand(v["weekend"], v["weekday"]) for k,v in DEFAULT_VEHICLE_DEFAULTS.items()}
    ev_types: Dict[str, Any] = {}
    arrival = build_arrival_pmf(ARRIVAL_WEEKDAY_PCT, ARRIVAL_WEEKEND_PCT)
    for k,v in DEFAULT_VEHICLE_DEFAULTS.items():
        delta = max(0.0, min(1.0, v['targetSOC'] - v['initSOC']))
        ev_types[k] = {
            "type": k,
            "eCap": int(v['battery_kWh']*1000),
            "pChgMax": int(v['pChgMax_kW']*1000),
            "count": weekday_weekend[k],
            "targetFinalSOCPMF": {"val": [round(v['targetSOC'],4)], "prob": [1.0]},
            "energyDemandPMF": {"val": [round(delta,4)], "prob": [1.0]},
            "arrivalTimePMF": arrival,
            "departureTimePMF": None,
        }
    sim_cfg = dict(BASE_SIM_CONFIG)
    sim_cfg['tEnd'] = days * 24 * 3600
    rc = {**RESULTS_CONFIG_BASE, "resultFieldOptions": {"nodes": "Grid", "portUsage": True, "queueLength": True, "nodeStats": True, "evStats": True}}
    return {"simConfig": sim_cfg, "hubConfig": {"nodes": nodes, "ems": EMS_CONFIG}, "evInfo": {"stochasticModel": 1, "chgDurMax": None, "evTypes": ev_types}, "resultsConfig": rc}

# ---------------- HTTP ------------------------------------------------------

def post(url: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any] | None, str]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    token = os.getenv("ENLITEPY_API_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(payload)
    try:
        if requests:
            r = requests.post(url.rstrip('/'), data=body, headers=headers, timeout=(10,120))
            if r.status_code == 404:
                r = requests.post(url.rstrip('/')+'/', data=body, headers=headers, timeout=(10,120))
            status, text = r.status_code, r.text
        else:
            data_b = body.encode()
            def _one(u):
                req = urllib.request.Request(u, data=data_b, headers=headers)
                return urllib.request.urlopen(req, timeout=120)
            try:
                resp = _one(url.rstrip('/'))
            except Exception:
                resp = _one(url.rstrip('/')+'/')
            status = resp.status
            text = resp.read().decode()
    except Exception as e:  # noqa
        return 0, None, f"EXC:{e}"
    try:
        js = json.loads(text)
    except json.JSONDecodeError:
        return status, None, text[:400]
    return status, js, ''

# ---------------- Cleaning / Annual -----------------------------------------

def replicate_to_8760(series: Any) -> Any:
    if not isinstance(series, list) or len(series) in (0, 8760):
        return series
    reps = (8760 // len(series)) + 1
    return (series * reps)[:8760]

def make_annual_equipment(weekly: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for row in weekly:
        copy = row.copy()
        for k in EQUIPMENT_ANNUAL_SCALARS:
            v = copy.get(k)
            if isinstance(v, (int,float)):
                copy[k] = round(v * WEEK_TO_YEAR_SCALE, 2)
        out.append(copy)
    return out

def make_annual_ev(weekly: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for row in weekly:
        copy = row.copy()
        for k,v in list(copy.items()):
            if k in EV_COUNT_SCALARS or k in EV_ENERGY_SCALARS:
                if isinstance(v,(int,float)):
                    copy[k] = round(v * WEEK_TO_YEAR_SCALE, 2)
        for k in list(copy.keys()):
            if k.endswith('[min]') and isinstance(copy[k], (int,float)):
                copy[k.replace('[min]','[h]')] = round(copy[k]/60.0,2)
                del copy[k]
        out.append(copy)
    return out

def add_grid_util(ts: Dict[str, Any], equip_annual: List[Dict[str, Any]]):
    power = ts.get('power_in_grid') if isinstance(ts, dict) else None
    if not isinstance(power, list) or not power:
        return
    grid_row = next((r for r in equip_annual if r.get('Name') in ('grid','Grid')), None)
    if not grid_row or 'Power capacity [kW]' not in grid_row:
        return
    cap = grid_row['Power capacity [kW]']
    if not isinstance(cap,(int,float)) or cap <= 0:
        return
    sample = [v for v in power[:50] if isinstance(v,(int,float))]
    if not sample:
        return
    max_sample = max(sample)
    to_kw = 1000.0 if max_sample > cap*1.1 else 1.0
    series_kw = [v/to_kw for v in power if isinstance(v,(int,float))]
    if not series_kw:
        return
    grid_row.setdefault('Min capacity utilization [kW]', round(min(series_kw),2))
    grid_row.setdefault('Average capacity utilization [kW]', round(mean(series_kw),2))

def normalize_and_enrich(resp: Dict[str, Any], do_annual: bool):
    results = resp.get('results')
    if not isinstance(results, dict):
        return
    for key in ('equipment_statistics','ev_statistics'):
        val = results.get(key)
        if isinstance(val,str):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    results[key] = parsed
            except json.JSONDecodeError:
                pass
    if do_annual:
        ts = results.get('timeseries')
        if isinstance(ts, dict) and 'power_in_grid' in ts:
            ann = replicate_to_8760(ts['power_in_grid'])
            if isinstance(ann, list) and len(ann) == 8760:
                ts['power_in_grid_annual'] = ann
        equip = results.get('equipment_statistics') or []
        ev = results.get('ev_statistics') or []
        if isinstance(equip, list):
            equip_ann = make_annual_equipment(equip)
            results['equipment_statistics_annual'] = equip_ann
            add_grid_util(results.get('timeseries',{}), equip_ann)
        if isinstance(ev, list):
            results['ev_statistics_annual'] = make_annual_ev(ev)

# ---------------- Validation -------------------------------------------------

def validate_scaling(resp: Dict[str, Any], tol: float = 0.05) -> List[str]:
    out: List[str] = []
    res = resp.get('results', {})
    ew = res.get('equipment_statistics', [])
    ea = res.get('equipment_statistics_annual', [])
    eq_map = {r.get('Name'): r for r in ew if isinstance(r, dict)}
    for a in ea:
        name = a.get('Name')
        w = eq_map.get(name)
        if not w:
            continue
        for k in EQUIPMENT_ANNUAL_SCALARS:
            wv = w.get(k)
            av = a.get(k)
            if isinstance(wv,(int,float)) and isinstance(av,(int,float)) and wv>0:
                expect = wv*WEEK_TO_YEAR_SCALE
                err = abs(av - expect)/expect if expect else 0
                if err > tol:
                    out.append(f"Equip {name}.{k} rel error {err:.2%} > {tol:.0%}")
    evw = res.get('ev_statistics', [])
    eva = res.get('ev_statistics_annual', [])
    if isinstance(evw,list) and isinstance(eva,list) and evw and eva:
        w0 = evw[0]
        e0 = eva[0]
        for k in EV_COUNT_SCALARS | EV_ENERGY_SCALARS:
            wv = w0.get(k)
            av = e0.get(k)
            if isinstance(wv,(int,float)) and isinstance(av,(int,float)) and wv>0:
                expect = wv*WEEK_TO_YEAR_SCALE
                err = abs(av - expect)/expect
                if err > tol:
                    out.append(f"EV {k} rel error {err:.2%} > {tol:.0%}")
    if not out:
        out.append('All scaling checks within tolerance.')
    return out

# ---------------- Diff helpers ----------------------------------------------

def keyset(results: Dict[str, Any]) -> List[str]:
    if not isinstance(results, dict):
        return []
    return sorted(list(results.keys()))

def diff_keysets(remote: Dict[str, Any], local: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    rk = set(keyset(remote.get('results', {})))
    lk = set(keyset(local.get('results', {})))
    for miss in sorted(rk - lk):
        issues.append(f'local missing key: {miss}')
    for miss in sorted(lk - rk):
        issues.append(f'remote missing key: {miss}')
    return issues

# ---------------- Main ------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--remote', help='Remote EnLitePy endpoint URL')
    ap.add_argument('--local', help='Local /stable/ensite/ endpoint URL')
    ap.add_argument('--annual', dest='annual', action='store_true', help='(Deprecated) Force annual enrichment (now default)')
    ap.add_argument('--no-annual', dest='no_annual', action='store_true', help='Disable annual enrichment (default: enabled)')
    ap.add_argument('--clean', dest='clean', action='store_true', help='(Deprecated) Force cleaning (now default)')
    ap.add_argument('--no-clean', dest='no_clean', action='store_true', help='Disable cleaning/normalization (default: enabled)')
    ap.add_argument('--validate', action='store_true', help='Run scaling validation (always implies cleaning & annual)')
    ap.add_argument('--outfile-prefix', default='compare_run', help='Prefix for output files')
    args = ap.parse_args()

    # Allow environment variable fallback if flags omitted
    if not args.remote:
        args.remote = os.getenv('ENLITEPY_REMOTE_URL') or os.getenv('ENLITEPY_API_URL')
    if not args.local:
        args.local = os.getenv('ENLITEPY_LOCAL_URL') or os.getenv('REOPT_LOCAL_ENLITEPY_URL')

    # Default behavior: clean & annual ON unless explicitly disabled
    clean_enabled = True
    annual_enabled = True
    if args.no_clean:
        clean_enabled = False
    if args.no_annual:
        annual_enabled = False
    if args.validate:
        clean_enabled = True
        annual_enabled = True

    payload = build_payload()
    print('Built payload EV types:', list(payload['evInfo']['evTypes'].keys()), 'EVSE count:', sum(1 for k in payload['hubConfig']['nodes'] if k.startswith('EVSE_')))

    remote_resp = local_resp = None
    remote_status = local_status = None
    if not (args.remote or args.local):
        print('Must supply at least one of --remote or --local')
        return 1

    if args.remote:
        print('POST remote:', args.remote)
        remote_status, remote_resp, r_err = post(args.remote, payload)
        if remote_status != 200 or not remote_resp:
            print(' Remote failed:', remote_status, r_err)
        else:
            print(' Remote OK')
    if args.local:
        print('POST local:', args.local)
        local_status, local_resp, l_err = post(args.local, payload)
        if local_status != 200 or not local_resp:
            print(' Local failed:', local_status, l_err)
        else:
            print(' Local OK')

    if clean_enabled:
        if remote_resp:
            normalize_and_enrich(remote_resp, annual_enabled)
        if local_resp:
            normalize_and_enrich(local_resp, annual_enabled)

    if args.validate:
        if remote_resp:
            for v in validate_scaling(remote_resp):
                print('REMOTE VALIDATE:', v)
        if local_resp:
            for v in validate_scaling(local_resp):
                print('LOCAL VALIDATE:', v)

    # Write individual responses
    if remote_resp:
        with open(f'{args.outfile_prefix}_remote.json','w') as f:
            json.dump(remote_resp, f)
        print('Wrote', f'{args.outfile_prefix}_remote.json')
    if local_resp:
        with open(f'{args.outfile_prefix}_local.json','w') as f:
            json.dump(local_resp, f)
        print('Wrote', f'{args.outfile_prefix}_local.json')

    diff_issues: List[str] = []
    if remote_resp and local_resp:
        diff_issues = diff_keysets(remote_resp, local_resp)
        # ignore enrichment_version differences in key diff
        diff_issues = [d for d in diff_issues if 'enrichment_version' not in d]
        if diff_issues:
            print('STRUCTURAL DIFFS:')
            for d in diff_issues:
                print(' -', d)
        else:
            print('Structures align.')

    summary = {
        'remote_status': remote_status,
        'local_status': local_status,
        'annual_requested': annual_enabled,
        'clean_requested': clean_enabled,
        'validated': args.validate,
        'remote_results_keys': keyset(remote_resp.get('results', {})) if remote_resp else None,
        'local_results_keys': keyset(local_resp.get('results', {})) if local_resp else None,
        'structural_differences': diff_issues,
    }
    with open(f'{args.outfile_prefix}_summary.json','w') as f:
        json.dump(summary, f, indent=2)
    print('Wrote', f'{args.outfile_prefix}_summary.json')

    # exit code
    if remote_status and remote_status != 200:
        return 2
    if local_status and local_status != 200:
        return 3
    if diff_issues:
        return 4
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
