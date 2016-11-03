from tastypie import fields
import os

def inputs(filter='',full_list=False,just_required=False):

    output = {'analysis_period': {'req':True, 'type': int, 'null': True, 'pct': False,"needed_for":['economics'],'default':25},
            'latitude': {'req':True,'type': float, 'null': True,'pct': False,"needed_for":['economics','gis','loads','pvwatts']},
            'longitude': {'req':True,'type': float, 'null': True,'pct': False,"needed_for":['economics','gis','loads','pvwatts']},

            'load_profile': {'req':True,'type': str, 'null': True, 'pct': False, "needed_for": ['economics']},
            'load_size': {'req':True,'type': float, 'null': True,'pct': False,"needed_for":['economics']},
            'load_8760_kw': {'req':True,'type': list, 'null': True,'pct': False,"needed_for":['economics']},
            'load_monthly_kwh': {'req':True,'type': list, 'null': True,'pct': False,"needed_for":['economics']},

            'pv_cost': {'req':True,'type': float, 'null': True, 'pct': False, "needed_for": ['economics'], 'default':2160},# nominal price in $/kW
            'pv_om': {'req':True,'type': float, 'null': True,'pct': False,"needed_for":['economics'],'default':20},# $/kW/year
            'batt_cost_kw': {'req':True,'type': float, 'null': True,'pct': False,"needed_for":['economics'],'default':1600},# nominal price in $/kW (inverter)
            'batt_cost_kwh': {'req':True,'type': float, 'null': True,'pct': False,"needed_for":['economics'],'default':500},# nominal price in $/kWh


            'owner_discount_rate': {'req':True,'type': float, 'null': True,'pct': True,"needed_for":['economics'],'default': 0.08},
            'offtaker_discount_rate': {'req':True,'type': float, 'null': True,'pct': True,"needed_for":['economics'],'default': 0.08},

            'utility_name': {'req':False,'type': str, 'null': True,'pct': False,"needed_for":['economics','utility']},
            'rate_name': {'req':False,'type': str, 'null': True,'pct': False,"needed_for":['economics','utility']},
            'rate_degradation': {'req':False,'type': float, 'null': False, 'pct': True, "needed_for": ['economics'], 'default': 0.005}, # 0.5% annual degradation for solar panels, accounted for in LevelizationFactor

            #Not Required
            'rate_inflation': {'req':False,'type': float, 'null': False, 'pct': True,"needed_for":['economics'],'default':0.02},  # percent/year inflation
            'rate_escalation':  {'req':False,'type': float, 'null': False, 'pct': True,"needed_for":['economics'],'default':0.0039}, # percent/year electricity escalation rate
            'rate_tax':  {'req':False,'type': float, 'null': True, 'pct': False,"needed_for":['economics'],'default':0.35},
            'rate_itc':  {'req':False,'type': float, 'null': True, 'pct': False,"needed_for":['economics'],'default':0.30},


            'batt_replacement_cost_kw': {'req':False,'type': float, 'null': False, 'pct': False,"needed_for":['economics'],'default':200},# $/kW to replace battery inverter
            'batt_replacement_cost_kwh': {'req':False,'type': float, 'null': False, 'pct': False,"needed_for":['economics'],'default':200},# $/kWh to replace battery
            'batt_replacement_year': {'req':False,'type': int, 'null': False, 'pct': False, "needed_for": ['economics'],'default':10},

            'flag_macrs': {'req':False,'type': bool, 'null': False, 'pct': False,"needed_for":['economics'],'default':1},
            'flag_itc': {'req':False,'type': bool, 'null': False, 'pct': False,"needed_for":['economics'],'default':1},
            'flag_bonus': {'req':False,'type': bool, 'null': False, 'pct': False,"needed_for":['economics'],'default':1},
            'flag_replace_batt': {'req':False,'type': bool, 'null': False, 'pct': False,"needed_for":['economics'],'default':1},

            'macrs_years': {'req':False,'type': int, 'null': False, 'pct': False,"needed_for":['economics'],'default':5},# 5 or 7 year shedules, taken for both PV and storage
            'macrs_itc_reduction': {'req':False,'type': float, 'null': False, 'pct': False,"needed_for":['economics'],'default':0.5}, # if ITC is taken with macrs, the depreciable value is reduced by this fraction of the ITC
            'bonus_fraction': {'req':False,'type': float, 'null': False, 'pct': False,"needed_for":['economics'],'default': 0.5}, # this fraction of the depreciable value is taken in year 1 in addition to MACRS

            'dataset': {'req':False,'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default':"tmy3"},# Default: tmy2 Options: tmy2 , tmy3, intl
            'inv_eff': {'req':False,'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 92},# or 96?
            'dc_ac_ratio': {'req':False,'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 1.1},
            'azimuth': {'req':False,'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 180},
            'system_capacity': {'req':False,'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 1},# kw to get prod factor
            'array_type': {'req':False,'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 0}, # fixed open rack
            'module_type': {'req':False,'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 0},# standard
            'timeframe': {'req':False,'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 'hourly'},
            'losses': {'req':False,'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 14},
            'radius': {'req':False,'type': str, 'null': False, 'pct': False, "needed_for": ['pvwatts'],'default': 0},

            'building_type': {'req': False, 'type': str, 'null': False, 'pct': False, "needed_for": ['loads'],'default': "Hospital"}
              }

    if full_list:
        return output

    if filter != '':
        output = {k:v for k, v in output.items() if filter in v['needed_for'] }

    if just_required:
        output = dict((k, v) for k, v in output.items() if v['req'])
    return output

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

def get_egg():
    # when deployed, runs from egg file, need to update if version changes!
    # path_egg = os.path.join("..", "reopt_api-1.0-py2.7.egg")

    # when not deployed (running from 127.0.0.1:8000)
    return os.getcwd()

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
