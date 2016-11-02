from tastypie import fields

def inputs(filter='',full_list=False,just_required=False):

    output = {'analysis_period': {'type': int, 'null': True, 'pct': False,"needed_for":['economics'],'default':25},
            'latitude': {'type': float, 'null': True,'pct': False,"needed_for":['economics','gis','loads','pvwatts']},
            'longitude': {'type': float, 'null': True,'pct': False,"needed_for":['economics','gis','loads','pvwatts']},

            'load_profile': {'type': str, 'null': True, 'pct': False, "needed_for": ['economics']},
            'load_size': {'type': float, 'null': True,'pct': False,"needed_for":['economics']},
            'load_8760_kw': {'type': list, 'null': True,'pct': False,"needed_for":['economics']},
            'load_monthly_kwh': {'type': list, 'null': True,'pct': False,"needed_for":['economics']},

            'pv_cost': {'type': float, 'null': True, 'pct': False, "needed_for": ['economics'], 'default':2160},# nominal price in $/kW
            'pv_om': {'type': float, 'null': True,'pct': False,"needed_for":['economics'],'default':20},# $/kW/year
            'batt_cost_kw': {'type': float, 'null': True,'pct': False,"needed_for":['economics'],'default':1600},# nominal price in $/kW (inverter)
            'batt_cost_kwh': {'type': float, 'null': True,'pct': False,"needed_for":['economics'],'default':500},# nominal price in $/kWh


            'owner_discount_rate': {'type': float, 'null': True,'pct': True,"needed_for":['economics'],'default': 0.08},
            'offtaker_discount_rate': {'type': float, 'null': True,'pct': True,"needed_for":['economics'],'default': 0.08},

            'utility_name': {'type': str, 'null': True,'pct': False,"needed_for":['economics','utility']},
            'rate_name': {'type': str, 'null': True,'pct': False,"needed_for":['economics','utility']},
            'rate_degradation': {'type': float, 'null': False, 'pct': True, "needed_for": ['economics'], 'default': 0.005}, # 0.5% annual degradation for solar panels, accounted for in LevelizationFactor

            #Not Required
            'rate_inflation': {'type': float, 'null': False, 'pct': True,"needed_for":['economics'],'default':0.02},  # percent/year inflation
            'rate_escalation':  {'type': float, 'null': False, 'pct': True,"needed_for":['economics'],'default':0.0039}, # percent/year electricity escalation rate
            'rate_tax':  {'type': float, 'null': True, 'pct': False,"needed_for":['economics'],'default':0.35},
            'rate_itc':  {'type': float, 'null': True, 'pct': False,"needed_for":['economics'],'default':0.30},


            'batt_replacement_cost_kw': {'type': float, 'null': False, 'pct': False,"needed_for":['economics'],'default':200},# $/kW to replace battery inverter
            'batt_replacement_cost_kwh': {'type': float, 'null': False, 'pct': False,"needed_for":['economics'],'default':200},# $/kWh to replace battery
            'batt_replacement_year': {'type': int, 'null': False, 'pct': False, "needed_for": ['economics'],'default':10},

            'flag_macrs': {'type': bool, 'null': False, 'pct': False,"needed_for":['economics'],'default':1},
            'flag_itc': {'type': bool, 'null': False, 'pct': False,"needed_for":['economics'],'default':1},
            'flag_bonus': {'type': bool, 'null': False, 'pct': False,"needed_for":['economics'],'default':1},
            'flag_replace_batt': {'type': bool, 'null': False, 'pct': False,"needed_for":['economics'],'default':1},

            'macrs_years': {'type': int, 'null': False, 'pct': False,"needed_for":['economics'],'default':5},# 5 or 7 year shedules, taken for both PV and storage
            'macrs_itc_reduction': {'type': float, 'null': False, 'pct': False,"needed_for":['economics'],'default':0.5}, # if ITC is taken with macrs, the depreciable value is reduced by this fraction of the ITC
            'bonus_fraction': {'type': float, 'null': False, 'pct': False,"needed_for":['economics'],'default': 0.5}, # this fraction of the depreciable value is taken in year 1 in addition to MACRS

            'dataset': {'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default':"tmy3"},# Default: tmy2 Options: tmy2 , tmy3, intl
            'inv_eff': {'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 92},# or 96?
            'dc_ac_ratio': {'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 1.1},
            'azimuth': {'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 180},
            'system_capacity': {'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 1},# kw to get prod factor
            'array_type': {'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 0}, # fixed open rack
            'module_type': {'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 0},# standard
            'timeframe': {'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 'hourly'},
            'losses': {'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 14},
            'radius': {'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 0}
              }

    if full_list:
        return output
    elif just_required:
        return dict((k, v) for k, v in output.items() if v['null'])
    elif filter != '':
        return dict((k,v) for k,v in output.items() if filter in v['needed_for'])

def internals():
    return {'id': {'type': int, 'null': False},
            'path_egg': {'type': int, 'null': False}}

def updates():
    return {'load_size':{},
            'pv_cost':{},
            'pv_om':{},
            'batt_cost_kw':{},
            'batt_cost_kwh':{},
            'owner_discount_rate':{},
            'offtaker_discount_rate':{},
            'analysis_period':{}}

def outputs():
    return {'lcc': {'type': float, 'null': True},
           'npv': {'type': str, 'null': True},
           'utility_kwh': {'type': str, 'null': True},
           'pv_kw': {'type': str, 'null': True},
           'batt_kw': {'type': str, 'null': True},
           'batt_kwh': {'type': str, 'null': True}}

def create_fields(inputs):
    output = {}
    for f, meta in inputs.items():
        if meta['type'] == float:
            output[f] = fields.FloatField(attribute=f, null=meta['null'])
        if meta['type'] == list:
            output[f] = fields.ListField(attribute=f, null=meta['null'])
        if meta['type'] == str:
            output[f] = fields.CharField(attribute=f, null=meta['null'])
def get_id():
    return random.randint(0, 1000000)

def set_internal(path_egg):
    return {"id":get_id(),"path_egg":path_egg}

# default load profiles
def default_load_profiles():
    return  ['FastFoodRest', 'Flat', 'FullServiceRest', 'Hospital', 'LargeHotel', 'LargeOffice',
                         'MediumOffice', 'MidriseApartment', 'Outpatient', 'PrimarySchool', 'RetailStore',
                         'SecondarySchool', 'SmallHotel', 'SmallOffice', 'StripMall', 'Supermarket', 'Warehouse']

# default locations
def default_cities():
    return ['Miami', 'Houston', 'Phoenix', 'Atlanta', 'LosAngeles', 'SanFrancisco', 'LasVegas', 'Baltimore',
                'Albuquerque', 'Seattle', 'Chicago', 'Boulder', 'Minneapolis', 'Helena', 'Duluth', 'Fairbanks']

# default latitudes
def default_latitudes():
    return [25.761680, 29.760427, 33.448377, 33.748995, 34.052234, 37.774929, 36.114707, 39.290385,
                     35.085334, 47.606209, 41.878114, 40.014986, 44.977753, 46.588371, 46.786672, 64.837778]

# default longitudes
def default_longitudes():
    return [-80.191790, -95.369803, -112.074037, -84.387982, -118.243685, -122.419416, -115.172850,
                      -76.612189, -106.605553, -122.332071, -87.629798, -105.270546, -93.265011, -112.024505,
                      -92.100485, -147.716389]
