# EnSite UI → API Integration Guide

The frontend (UI) only sends a **simple declarative JSON** describing what the user edits: charger settings, vehicle arrival counts, arrival distribution, and optional max charge duration. **It does NOT build the full EnLitePy engine payload.** The Django view (`ensite_view`) transforms this UI JSON into the full simulation payload (`simConfig`, `hubConfig`, `evInfo`, `resultsConfig`) and runs EnLitePy.

## Endpoint

Stable path:
```
POST /stable/ensite/
```
If running locally with Django development server:
```
http://localhost:8000/stable/ensite/
```
(Ensure the trailing slash is included; the server will usually redirect if omitted.)

## Authentication

If the API is secured with a bearer token, include:
```
Authorization: Bearer <YOUR_TOKEN>
```
If no auth is required in your environment, omit the header.

## Request Headers
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>   # optional
```

## UI Input Contract (Simple JSON the Frontend Sends)

The UI sends ONLY a lightweight object with optional sections. Any omitted section uses server defaults.

Top-level keys (all optional):

| Key | Type | Description |
|-----|------|-------------|
| `chargers` | object | Per charger category overrides (counts, power, efficiency, pci) |
| `vehicles` | object | Per vehicle class overrides (weekday/weekend arrivals, SOC, power, battery size) |
| `arrival` | object | Two arrays (`weekday`, `weekend`) each length 12 (2‑hr bins, percentages) |
| `maxChargeDurationMin` | number/null | Max charge duration in minutes (null or omit = no limit) |

Charger category keys (if present): `L1`, `L2`, `DCFC_LD`, `DCFC_MDHD`.

Vehicle class keys (if present): `LD`, `MD`, `HD`.

Example UI request (only what the user edits):
```json
{
  "chargers": {
    "L2": { "count": 4, "power_kW": 11.5, "eff": 0.86, "pci": "LD" },
    "DCFC_LD": { "count": 1, "power_kW": 150, "eff": 0.92, "pci": "LD" }
  },
  "vehicles": {
    "LD": { "weekday": 40, "weekend": 15, "battery_kWh": 82, "initSOC": 0.15, "targetSOC": 0.90, "pChgMax_kW": 170 }
  },
  "arrival": {
    "weekday": [0,0,0,0,5,10,10,15,20,20,5,5],
    "weekend": [0,0,0,0,0,10,15,25,20,15,5,0]
  },
  "maxChargeDurationMin": 180
}
```

That’s it—the UI does not build nodes, counts arrays, PMFs, or unit conversions.

## Server Transformation (What Django Builds Internally)

Given the UI JSON above, the server produces a full EnLitePy payload:
1. Expands charger `count` into individual EVSE nodes (naming: `EVSE_<TYPE>_<i>`).
2. Converts `power_kW` → watts (`pMax`).
3. Builds each vehicle class `count` array: `[weekend, weekday, weekday, weekday, weekday, weekday, weekend]`.
4. Computes `energyDemandPMF` from `targetSOC - initSOC` (clamped 0–1).
5. Normalizes non-zero arrival bucket percentages into probability arrays (2‑hr bins → 7200 sec `dur`).
6. Converts battery and charger powers to integer watt values (`eCap`, `pChgMax`).
7. Converts `maxChargeDurationMin` → seconds (`chgDurMax`).
8. Adds standard `simConfig`, `resultsConfig`, and `ems` defaults.

Conceptual (abbreviated) resulting payload:
```json
{
  "simConfig": {"tStart":0,"tEnd":604800,"dowStart":0},
  "hubConfig": {
    "nodes": {
      "grid": {"type":"Grid","pMax":500000,"pMin":0,"eff":0.99},
      "EVSE_L2_1": {"type":"EVSE","pMax":11500,"pMin":0,"eff":0.86,"nEVPort":1,"pci":"LD"},
      "EVSE_L2_2": {"type":"EVSE","pMax":11500,"pMin":0,"eff":0.86,"nEVPort":1,"pci":"LD"},
      "EVSE_L2_3": {"type":"EVSE","pMax":11500,"pMin":0,"eff":0.86,"nEVPort":1,"pci":"LD"},
      "EVSE_L2_4": {"type":"EVSE","pMax":11500,"pMin":0,"eff":0.86,"nEVPort":1,"pci":"LD"},
      "EVSE_DCFC_LD_1": {"type":"EVSE","pMax":150000,"pMin":0,"eff":0.92,"nEVPort":1,"pci":"LD"}
    },
    "ems": {"type":"basic","pChgCap":500000,"pap":"FCFS+SMX"}
  },
  "evInfo": {
    "stochasticModel":1,
    "chgDurMax":10800,
    "evTypes": {
      "LD": {
        "type":"LD",
        "eCap":82000,
        "pChgMax":170000,
        "count":[15,40,40,40,40,40,15],
        "targetFinalSOCPMF":{"val":[0.9],"prob":[1.0]},
        "energyDemandPMF":{"val":[0.75],"prob":[1.0]},
        "arrivalTimePMF": {"1-5": {"val":[28800,36000,43200,50400,57600,64800,72000],"prob":[...] ,"dur":7200}, "0,6": {"val":[43200,50400,57600,64800],"prob":[...],"dur":7200}},
        "departureTimePMF": null
      }
    }
  },
  "resultsConfig": {"timeseriesDt":3600,"powerMetricsDt":3600,"resultFieldOptions":{"nodes":"Grid","portUsage":true,"queueLength":true,"nodeStats":true,"evStats":true}}
}
```

## Why This Design
| Benefit | Explanation |
|---------|-------------|
| Thin UI | Frontend only manages user-facing fields (no internal engine schema knowledge). |
| Backward compatibility | Engine schema changes isolated to server transformation layer. |
| Validation centralization | Single place to clamp SOC, normalize arrival probabilities, enforce array lengths. |
| Faster iteration | Add new derived metrics in server without redeploying UI. |

## Minimal Frontend Payload Builder (Pseudocode)
```javascript
// uiState collects user edits. Only send what changed; server fills defaults.
const payload = {
  chargers: uiState.chargers,          // optional
  vehicles: uiState.vehicles,          // optional
  arrival: uiState.arrival,            // { weekday: [...12], weekend: [...12] }
  maxChargeDurationMin: uiState.maxDurationMin // optional
};
fetch('/stable/ensite/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
  body: JSON.stringify(payload)
}).then(r => r.json()).then(console.log);
```

## Validation Expectations (Server-Side)
| Check | Rule | Failure Response |
|-------|------|------------------|
| Arrival arrays length | Exactly 12 buckets | 400 with error message |
| Arrival values | ≥ 0 | 400 error |
| SOC bounds | 0 ≤ init < target ≤ 1 | Clamped or 400 depending on severity |
| Count arrays | Derived only (UI never sends them) | n/a |
| Charger counts | ≥ 0 integer | 400 if invalid |

## Automatic Enrichment (Default Behavior)

Every response now automatically includes cleaned & enriched metrics:

| Field | Description |
|-------|-------------|
| `equipment_statistics` | Original weekly equipment statistics list |
| `equipment_statistics_annual` | Annual-scaled version (select kWh metrics × 365/7) |
| `ev_statistics` | Original weekly EV stats |
| `ev_statistics_annual` | Annual-scaled EV counts & energy; durations converted to hours |
| `timeseries.power_in_grid` | Weekly (or simulation horizon) power series |
| `timeseries.power_in_grid_annual` | Replicated to 8760 steps if source shorter |
| `logs` | Always present (empty list if none) |
| `enrichment_version` | Integer version of enrichment logic (currently 1) |

No request flags are needed—UI simply posts the minimal input JSON and receives enriched results.

## Response (Simplified)
```json
{
  "results": {
    "equipment_statistics": [...],
    "equipment_statistics_annual": [...],
    "ev_statistics": [...],
    "ev_statistics_annual": [...],
    "timeseries": {"power_in_grid": [...], "power_in_grid_annual": [...]},
    "logs": [],
    "enrichment_version": 1
  }
}
```

## Optional Advanced Mode (Direct Payload)
If a power user posts the full engine schema (with `simConfig` etc.), the server detects it and runs directly—skipping transformation.

## Quick UI Smoke Test
```bash
curl -s -X POST http://localhost:8000/stable/ensite/ \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"vehicles":{"LD":{"weekday":5,"weekend":2}}}' | jq '.results | keys'
```

---
For automated parity checks or deeper validation use `run_enlitepy_compare.py`.

## curl Example
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $ENLITEPY_API_TOKEN" \ # optional
  -d @payload.json \
  http://localhost:8000/stable/ensite/
```

## JavaScript fetch Example
```javascript
async function runSimulation(payload) {
  const resp = await fetch('http://localhost:8000/stable/ensite/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      // 'Authorization': 'Bearer ' + token, // uncomment if needed
    },
    body: JSON.stringify(payload)
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`HTTP ${resp.status}: ${text}`);
  }
  const data = await resp.json();
  console.log('Simulation results:', data);
  return data;
}
```

## Response Structure (Simplified)
Successful responses contain:
```json
{
  "status": "OK",                // or similar
  "results": {
    "equipment_statistics": [...],
    "ev_statistics": [...],
    "timeseries": {"power_in_grid": [ ... ]},
    "logs": []
  }
}
```
Some fields may be JSON strings if not normalized; downstream clients can parse if needed.

## Common Errors
| Issue | Cause | Fix |
|-------|-------|-----|
| 400 Bad Request | Missing required keys | Ensure `simConfig`, `hubConfig`, `evInfo`, `resultsConfig` present |
| 415 Unsupported Media Type | Missing Content-Type header | Add `Content-Type: application/json` |
| 401 Unauthorized | Missing or invalid token | Provide valid Bearer token if auth enabled |
| 500 Internal Server Error | Server-side exception | Re-check payload values; look at server logs |

## Tips
- Keep integer power values in watts if the engine expects integer (e.g. 13 kW => 13000).
- Use consistent time units (seconds for `tStart`, `tEnd`, arrival values).
- For a no-op auth environment, simply omit the Authorization header.
- Start simple (one EV type, minimal EVSE nodes) before scaling up complexity.

## Minimal Quick Test
```bash
python - <<'PY'
import json, urllib.request
payload = {"simConfig":{"tStart":0,"tEnd":604800,"dowStart":0},"hubConfig":{"nodes":{"grid":{"type":"Grid","pMax":500000,"pMin":0,"eff":0.99}},"ems":{"type":"basic","pChgCap":500000,"pap":"FCFS+SMX"}},"evInfo":{"stochasticModel":1,"chgDurMax":None,"evTypes":{}},"resultsConfig":{"timeseriesDt":3600,"powerMetricsDt":3600,"resultFieldOptions":{"nodes":"Grid","portUsage":True,"queueLength":True,"nodeStats":True,"evStats":True}}}
req = urllib.request.Request('http://localhost:8000/stable/ensite/', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json','Accept':'application/json'})
print(json.loads(urllib.request.urlopen(req).read().decode())['results'].keys())
PY
```

---
If you need a deeper validation or remote/local parity comparison, use `run_enlitepy_compare.py` which was added for automated checks.
