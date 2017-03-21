from api_definitions import *
import requests
import json
import logging
import datetime

logging.basicConfig(filename='log_%s.log' % (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')), filemode='w', level=logging.DEBUG)

localhost = False

def case(
        analysis_period=20,user_id="123",latitude=34.5794343,longitude=-118,pv_om=20,batt_cost_kw=1600,batt_cost_kwh=500,
        load_profile_name="RetailStore",load_size=500000,pv_cost=2160,offtaker_discount_rate=0.07,offtaker_tax_rate=0.35,
        owner_discount_rate=0.1,owner_tax_rate=0.35,rate_inflation=0.02,rate_escalation=0.0,load_year=2018,batt_itc_federal=0.3,
        batt_itc_state=0.0,batt_itc_utility=0.0,batt_itc_federal_max=10000000,batt_itc_state_max=0,batt_itc_utility_max=0,
        batt_rebate_federal=0,batt_rebate_state=0,batt_rebate_utility=0,batt_rebate_federal_max=0,batt_rebate_state_max=0,
        batt_rebate_utility_max=0,pv_pbi=0.3,pv_pbi_max=1000,pv_pbi_years=20,pv_pbi_system_max=1000,pv_itc_federal=0.3,
        pv_itc_state=0.0,pv_itc_utility=0.0, pv_itc_federal_max=10000000,pv_itc_state_max=0,pv_itc_utility_max=0,pv_rebate_federal=0,
        pv_rebate_state=0,pv_rebate_utility=0,pv_rebate_federal_max=0,pv_rebate_state_max=0,pv_rebate_utility_max=0, urdb_rate=None,
        blended_utility_rate=None, demand_charge=None
  ):

  response = {
    "analysis_period": analysis_period,
    'user_id': user_id,
    "latitude": latitude,
    "longitude": longitude,
    "pv_om": pv_om,
    "batt_cost_kw": batt_cost_kw,
    "batt_cost_kwh": batt_cost_kwh,
    "load_profile_name": load_profile_name,
    "load_size": load_size,
    "pv_cost": pv_cost,
    "offtaker_discount_rate": offtaker_discount_rate,
    "offtaker_tax_rate": offtaker_tax_rate,
    "owner_discount_rate": owner_discount_rate,
    "owner_tax_rate": owner_tax_rate,
    "rate_inflation": rate_inflation,
    "rate_escalation": rate_escalation,
    "load_year": load_year,
    "batt_itc_federal": batt_itc_federal,
    "batt_itc_state": batt_itc_state,
    "batt_itc_utility": batt_itc_utility,
    "batt_itc_federal_max": batt_itc_federal_max,
    "batt_itc_state_max": batt_itc_state_max,
    "batt_itc_utility_max": batt_itc_utility_max,
    "batt_rebate_federal": batt_rebate_federal,
    "batt_rebate_state": batt_rebate_state,
    "batt_rebate_utility": batt_rebate_utility,
    "batt_rebate_federal_max": batt_rebate_federal_max,
    "batt_rebate_state_max": batt_rebate_state_max,
    "batt_rebate_utility_max": batt_rebate_utility_max,
    "pv_pbi": pv_pbi,
    "pv_pbi_max": pv_pbi_max,
    "pv_pbi_years": pv_pbi_years,
    "pv_pbi_system_max": pv_pbi_system_max,
    "pv_itc_federal": pv_itc_federal,
    "pv_itc_state": pv_itc_state,
    "pv_itc_utility": pv_itc_utility,
    "pv_itc_federal_max": pv_itc_federal_max,
    "pv_itc_state_max": pv_itc_state_max,
    "pv_itc_utility_max": pv_itc_utility_max,
    "pv_rebate_federal": pv_rebate_federal,
    "pv_rebate_state": pv_rebate_state,
    "pv_rebate_utility": pv_rebate_utility,
    "pv_rebate_federal_max": pv_rebate_federal_max,
    "pv_rebate_state_max": pv_rebate_state_max,
    "pv_rebate_utility_max": pv_rebate_utility_max,
  }

  if urdb_rate == None and blended_utility_rate is None and demand_charge is None:

    urdb_rate = {"sector": "Commercial", "peakkwcapacitymax": 200,
     "demandattrs": [{"Facilties Voltage Discount (2KV-<50KV)": "$-0.18/KW"},
                     {"Facilties Voltage Discount >50 kV-<220kV": "$-5.78/KW"},
                     {"Facilties Voltage Discount >220 kV": "$-9.96/KW"},
                     {"Time Voltage Discount (2KV-<50KV)": "$-0.70/KW"},
                     {"Time Voltage Discount >50 kV-<220kV": "$-1.93/KW"},
                     {"Time Voltage Discount >220 kV": "$-1.95/KW"}],
     "energyratestructure": [[{"rate": 0.0712, "unit": "kWh"}], [{"rate": 0.09368, "unit": "kWh"}],
                             [{"rate": 0.066, "unit": "kWh"}], [{"rate": 0.08888, "unit": "kWh"}],
                             [{"rate": 0.1355, "unit": "kWh"}]],
     "energyweekendschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                               [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                               [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                               [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
     "demandweekendschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
     "utility": "Southern California Edison Co", "flatdemandstructure": [[{"rate": 13.2}]], "startdate": 1433116800,
     "phasewiring": "Single Phase", "eiaid": 17609, "label": "55fc81d7682bea28da64f9ae", "flatdemandunit": "kW",
     "source": "http://www.sce.com/NR/sc3/tm2/pdf/ce30-12.pdf", "voltagecategory": "Primary",
     "fixedmonthlycharge": 259.2,
     "revisions": [1433408708, 1433409358, 1433516188, 1441198316, 1441199318, 1441199417, 1441199824, 1441199996,
                   1454521683],
     "demandweekdayschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
     "voltageminimum": 2000,
     "description": "- Energy tiered charge = generation charge + delivery charge\r\n\r\n- Time of day demand charges (generation-based) are to be added to the monthly demand charge(Delivery based).",
     "energyattrs": [{"Voltage Discount (2KV-<50KV)": "$-0.00106/Kwh"},
                     {"Voltage Discount (>50 KV<220 KV)": "$-0.00238/Kwh"},
                     {"Voltage Discount at 220 KV": "$-0.0024/Kwh"}, {"California Climate credit": "$-0.00669/kwh"}],
     "energyweekdayschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
                               [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2],
                               [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2],
                               [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2],
                               [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2],
                               [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]],
     "flatdemandmonths": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "approved": True, "enddate": 1451520000,
     "name": "Time of Use, General Service, Demand Metered, Option B: GS-2 TOU B, Single Phase", "country": "USA",
     "uri": "http://en.openei.org/apps/IURDB/rate/view/55fc81d7682bea28da64f9ae", "voltagemaximum": 50000,
     "demandratestructure": [[{"rate": 0}], [{"rate": 5.3}], [{"rate": 18.11}]], "peakkwcapacitymin": 20,
     "peakkwcapacityhistory": 12, "demandrateunit": "kW"
     }
    response['urdb_rate'] = urdb_rate

  else:
    response['demand_charge'] = demand_charge
    response['blended_utility_rate'] = blended_utility_rate

  return response


def make_call(data):

  headers = { "Content-Type":"application/json", "Cache-Control": "no-cache" }
  data =  json.dumps(data, ensure_ascii=False)

  if localhost:
    h = "http://127.0.0.1:8000"

  else:
    h = "https://reopt-dev-api1.nrel.gov"

  r = requests.post(h + "/api/v1/reopt/?format=json",data=data, headers=headers)
  return r


def check_response(key, case, r):
    msg = read_response(key, r)
    if msg is not None:
        logging.warning('%s\n%s\n%s' % (key, case, r.content))
        print key, case, r.content

    else:
        logging.info('%s\n%s\n%s' % (key, case, r.content))

def read_response(key, r):
  try:
      if 'error' in r.content:
        return "Error"

      result = json.loads(r.content)

      for k,v in result.items():

          if k in outputs():
              if v is None and bool(outputs()[k].get('req')):
                  return "No Value for required non-null output " + k

              dtype = outputs()[k]['type']

              if dtype in [int,float] and v not in [None, 'null']:
                  if v < 0:
                      return "Negative Value for " + k

              if dtype in [list] and bool(outputs()[k].get('req')):
                  for ii in v:
                    if ii < 0:
                        return "Negative Value for " + k

  except Exception as e:
      print key + " " + e
      logging.warning(e)

  return None

for k,v in inputs().items():

    logging.info('Started ' + k + ' ' + datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'))
    start_time = datetime.datetime.now()

    if k.get('restrict_to') is not None:
      for restriction in k.get('restrict_to'):
        c = case()
        c[k] = test
        r = make_call(c)
        check_response(k,c,r)


    if v['type'] in [float, int]:

        min_ = inputs()[k].get('min')
        max_ = inputs()[k].get('max')

        if min_ is None:
            min_ = 0

        if max_ is None:
            if v['type'] == float:
                if v['pct']:
                    max_ = 1
                else:
                    max_ = 1000000

            elif v['type'] == int:
                max_ = 100000000

        for test in [min_,max_]:
            c = case()
            c[k] = test
            r = make_call(c)
            check_response(k,c,r)
    else:
        if k in ['blended_utility_rate','demand_charge','load_monthly_kwh','load_8760_kw']:
            min_ = [0]*12
            max_ = [100000] * 12

            if k in ['load_8760_kw']:
                min_ = [0] * 8760
                max_ = [100000] * 8760

            if k in ['blended_utility_rate','demand_charge']:
                for test in [min_, max_]:
                    c = case(blended_utility_rate=test,demand_charge=test)
                    r = make_call(c)
                    check_response(k,c,r)

            else:
                for test in [min_, max_]:
                    c = case()
                    c[k] = test
                    r = make_call(c)
                    check_response(k,c,r)

    end_time = datetime.datetime.now()
    duration =  end_time - start_time

    logging.info('End ' + k + ' ' + end_time.strftime('%Y%m%d %H:%M:%S') + (' (% seconds)' % (duration)) )
    print k, "complete"

    if duration.seconds > 120:
        logging.warning( 'Long API call ' + k )




