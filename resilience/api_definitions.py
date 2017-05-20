from datetime import datetime


def inputs(filter='', full_list=False, just_required=False):
    output = {

        'load_8760_kwh': {'req': True, 'type': list, 'null': False, 'pct': False, "needed_for": [], 'default': [0]*8760
            , "description": "Hourly Load Profile", "units": 'kWh', "tool_tip": "Hourly load profile in kwh."},

        'pv_resource_kwh': {'req': True, 'type': list, 'null': False, 'pct': False, "needed_for": [], 'default': [0]*8760
            , "description": "Hourly Solar Resource Profile", "units": 'kWh', "tool_tip": "Hourly incoming solar profile in kwh."}

        }
    if full_list:
      return output

    return output
