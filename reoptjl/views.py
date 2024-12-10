# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
from django.db import models
from django.db.models import Q
import uuid
from typing import List, Dict, Any
import sys
import traceback as tb
import re
from django.http import JsonResponse, HttpResponse
from reo.exceptions import UnexpectedError
from reoptjl.models import Settings, PVInputs, ElectricStorageInputs, WindInputs, GeneratorInputs, ElectricLoadInputs,\
    ElectricTariffInputs, ElectricUtilityInputs, SpaceHeatingLoadInputs, PVOutputs, ElectricStorageOutputs,\
    WindOutputs, ExistingBoilerInputs, GeneratorOutputs, ElectricTariffOutputs, ElectricUtilityOutputs, \
    ElectricLoadOutputs, ExistingBoilerOutputs, DomesticHotWaterLoadInputs, SiteInputs, SiteOutputs, APIMeta, \
    UserProvidedMeta, CHPInputs, CHPOutputs, CoolingLoadInputs, ExistingChillerInputs, ExistingChillerOutputs,\
    CoolingLoadOutputs, HeatingLoadOutputs, REoptjlMessageOutputs, HotThermalStorageInputs, HotThermalStorageOutputs,\
    ColdThermalStorageInputs, ColdThermalStorageOutputs, AbsorptionChillerInputs, AbsorptionChillerOutputs,\
    FinancialInputs, FinancialOutputs, UserUnlinkedRuns, BoilerInputs, BoilerOutputs, SteamTurbineInputs, \
    SteamTurbineOutputs, GHPInputs, GHPOutputs, ProcessHeatLoadInputs, ElectricHeaterInputs, ElectricHeaterOutputs, \
    ASHPSpaceHeaterInputs, ASHPSpaceHeaterOutputs, ASHPWaterHeaterInputs, ASHPWaterHeaterOutputs, PortfolioUnlinkedRuns

import os
import requests
import numpy as np
import pandas as pd
import json
import logging

from reoptjl.custom_table_helpers import flatten_dict, clean_data_dict, sum_vectors, colnum_string
from reoptjl.custom_table_config import *

import xlsxwriter
from collections import defaultdict
import io

log = logging.getLogger(__name__)
class CustomTableError(Exception):
    pass

def log_and_raise_error(task_name: str) -> None:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    log.error(f"Error in {task_name}: {exc_value}, traceback: {tb.format_tb(exc_traceback)}")
    raise CustomTableError(f"Error in {task_name}")

def make_error_resp(msg):
    resp = dict()
    resp['messages'] = {'error': msg}
    resp['status'] = 'error'
    return resp


def help(request):
    """
    used for job/inputs. keeping the help endpoint behavior from v1
    """
    try:
        d = dict()
        d["Meta"] = UserProvidedMeta.info_dict(UserProvidedMeta)
        d["Settings"] = Settings.info_dict(Settings)
        d["Financial"] = FinancialInputs.info_dict(FinancialInputs)
        d["ElectricLoad"] = ElectricLoadInputs.info_dict(ElectricLoadInputs)
        d["ElectricTariff"] = ElectricTariffInputs.info_dict(ElectricTariffInputs)
        d["ElectricUtility"] = ElectricUtilityInputs.info_dict(ElectricUtilityInputs)
        d["PV"] = PVInputs.info_dict(PVInputs)
        d["ElectricStorage"] = ElectricStorageInputs.info_dict(ElectricStorageInputs)
        d["Wind"] = WindInputs.info_dict(WindInputs)
        d["Generator"] = GeneratorInputs.info_dict(GeneratorInputs)
        d["CoolingLoad"] = CoolingLoadInputs.info_dict(CoolingLoadInputs)
        d["ExistingChiller"] = ExistingChillerInputs.info_dict(ExistingChillerInputs)
        d["ExistingBoiler"] = ExistingBoilerInputs.info_dict(ExistingBoilerInputs)
        d["Boiler"] = BoilerInputs.info_dict(BoilerInputs)
        d["HotThermalStorage"] = HotThermalStorageInputs.info_dict(HotThermalStorageInputs)
        d["ColdThermalStorage"] = ColdThermalStorageInputs.info_dict(ColdThermalStorageInputs)
        d["SpaceHeatingLoad"] = SpaceHeatingLoadInputs.info_dict(SpaceHeatingLoadInputs)
        d["DomesticHotWaterLoad"] = DomesticHotWaterLoadInputs.info_dict(DomesticHotWaterLoadInputs)
        d["ProcessHeatLoad"] = ProcessHeatLoadInputs.info_dict(ProcessHeatLoadInputs)
        d["Site"] = SiteInputs.info_dict(SiteInputs)
        d["CHP"] = CHPInputs.info_dict(CHPInputs)
        d["AbsorptionChiller"] = AbsorptionChillerInputs.info_dict(AbsorptionChillerInputs)
        d["SteamTurbine"] = SteamTurbineInputs.info_dict(SteamTurbineInputs)
        d["GHP"] = GHPInputs.info_dict(GHPInputs)
        d["ElectricHeater"] = ElectricHeaterInputs.info_dict(ElectricHeaterInputs)
        d["ASHPSpaceHeater"] = ASHPSpaceHeaterInputs.info_dict(ASHPSpaceHeaterInputs)
        d["ASHPWaterHeater"] = ASHPWaterHeaterInputs.info_dict(ASHPWaterHeaterInputs)

        return JsonResponse(d)

    except Exception as e:
        return JsonResponse({"Error": "Unexpected error in help endpoint: {}".format(e.args[0])}, status=500)


# TODO document inputs and outputs endpoints in Analysis wiki once deployed
def inputs(request):
    """
    Served at host/job/inputs
    :param request: 
    :return: JSON response with all job inputs
    """
    resp = help(request)
    return resp


def outputs(request):
    """
    Served at host/job/outputs
    :return: JSON response with all job outputs
    """

    try:
        d = dict()
        d["Financial"] = FinancialOutputs.info_dict(FinancialOutputs)
        d["ElectricLoad"] = ElectricLoadOutputs.info_dict(ElectricLoadOutputs)
        d["ElectricTariff"] = ElectricTariffOutputs.info_dict(ElectricTariffOutputs)
        d["ElectricUtility"] = ElectricUtilityOutputs.info_dict(ElectricUtilityOutputs)
        d["Site"] = SiteOutputs.info_dict(SiteOutputs)
        d["PV"] = PVOutputs.info_dict(PVOutputs)
        d["ElectricStorage"] = ElectricStorageOutputs.info_dict(ElectricStorageOutputs)
        d["Wind"] = WindOutputs.info_dict(WindOutputs)
        d["Generator"] = GeneratorOutputs.info_dict(GeneratorOutputs)
        d["ExistingChiller"] = ExistingChillerOutputs.info_dict(ExistingChillerOutputs)
        d["ExistingBoiler"] = ExistingBoilerOutputs.info_dict(ExistingBoilerOutputs)
        d["Boiler"] = BoilerOutputs.info_dict(BoilerOutputs)
        d["HotThermalStorage"] = HotThermalStorageOutputs.info_dict(HotThermalStorageOutputs)
        d["ColdThermalStorage"] = ColdThermalStorageOutputs.info_dict(ColdThermalStorageOutputs)
        d["Site"] = SiteOutputs.info_dict(SiteOutputs)
        d["HeatingLoad"] = HeatingLoadOutputs.info_dict(HeatingLoadOutputs)
        d["CoolingLoad"] = CoolingLoadOutputs.info_dict(CoolingLoadOutputs)
        d["CHP"] = CHPOutputs.info_dict(CHPOutputs)
        d["AbsorptionChiller"] = AbsorptionChillerOutputs.info_dict(AbsorptionChillerOutputs)
        d["GHP"] = GHPOutputs.info_dict(GHPOutputs)
        d["ElectricHeater"] = ElectricHeaterOutputs.info_dict(ElectricHeaterOutputs)
        d["ASHPSpaceHeater"] = ASHPSpaceHeaterOutputs.info_dict(ASHPSpaceHeaterOutputs)
        d["ASHPWaterHeater"] = ASHPWaterHeaterOutputs.info_dict(ASHPWaterHeaterOutputs)
        d["Messages"] = REoptjlMessageOutputs.info_dict(REoptjlMessageOutputs)
        d["SteamTurbine"] = SteamTurbineOutputs.info_dict(SteamTurbineOutputs)
        return JsonResponse(d)

    except Exception as e:
        return JsonResponse({"Error": "Unexpected error in help endpoint: {}".format(e.args[0])}, status=500)

def results(request, run_uuid):
    """
    results endpoint for reoptjl jobs
    """
    try:
        uuid.UUID(run_uuid)  # raises ValueError if not valid uuid
    except ValueError as e:
        if e.args[0] == "badly formed hexadecimal UUID string":
            resp = make_error_resp(e.args[0])
            return JsonResponse(resp, status=400)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value.args[0], tb.format_tb(exc_traceback), task='reoptjl.views.results', 
                run_uuid=run_uuid)
            err.save_to_db()
            return JsonResponse({"Error": str(err.args[0])}, status=400)

    try:
        # get all required inputs/outputs
        meta = APIMeta.objects.select_related(
            'Settings',
            'FinancialInputs', 'FinancialOutputs',
            'SiteInputs', 'SiteOutputs',
            'ElectricLoadInputs',
            'ElectricUtilityOutputs'
        ).get(run_uuid=run_uuid)
    except Exception as e:
        if isinstance(e, models.ObjectDoesNotExist):
            resp = {"messages": {}}
            resp['messages']['error'] = (
                "run_uuid {} not in database. "
                "You may have hit the results endpoint too quickly after POST'ing scenario, "
                "have a typo in your run_uuid, or the scenario was deleted.").format(run_uuid)
            resp['status'] = 'error'
            return JsonResponse(resp, status=404)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value.args[0], tb.format_tb(exc_traceback), task='reoptjl.views.results', 
                run_uuid=run_uuid)
            err.save_to_db()
            resp = make_error_resp(err.message)
            return JsonResponse(resp, status=500)

    r = meta.dict
    r["inputs"] = dict()
    r["inputs"]["Financial"] = meta.FinancialInputs.dict
    r["inputs"]["ElectricLoad"] = meta.ElectricLoadInputs.dict
    r["inputs"]["Site"] = meta.SiteInputs.dict
    r["inputs"]["Settings"] = meta.Settings.dict

    # We have to try for the following objects because they may or may not be defined
    try:
        pvs = meta.PVInputs.all()
        if len(pvs) == 1:
            r["inputs"]["PV"] = pvs[0].dict
        elif len(pvs) > 1:
            r["inputs"]["PV"] = []
            for pv in pvs:
                r["inputs"]["PV"].append(pv.dict)
    except: pass

    try: r["inputs"]["Meta"] = meta.UserProvidedMeta.dict
    except: pass

    try: r["inputs"]["ElectricTariff"] = meta.ElectricTariffInputs.dict
    except: pass

    try: r["inputs"]["ElectricUtility"] = meta.ElectricUtilityInputs.dict
    except: pass

    try: r["inputs"]["ElectricStorage"] = meta.ElectricStorageInputs.dict
    except: pass

    try: r["inputs"]["Generator"] = meta.GeneratorInputs.dict
    except: pass

    try: r["inputs"]["Wind"] = meta.WindInputs.dict
    except: pass

    try: r["inputs"]["CoolingLoad"] = meta.CoolingLoadInputs.dict
    except: pass

    try: r["inputs"]["ExistingChiller"] = meta.ExistingChillerInputs.dict
    except: pass
	
    try: r["inputs"]["ExistingBoiler"] = meta.ExistingBoilerInputs.dict
    except: pass

    try: r["inputs"]["Boiler"] = meta.BoilerInputs.dict
    except: pass

    try: r["inputs"]["HotThermalStorage"] = meta.HotThermalStorageInputs.dict
    except: pass

    try: r["inputs"]["ColdThermalStorage"] = meta.ColdThermalStorageInputs.dict
    except: pass

    try: r["inputs"]["SpaceHeatingLoad"] = meta.SpaceHeatingLoadInputs.dict
    except: pass

    try: r["inputs"]["DomesticHotWaterLoad"] = meta.DomesticHotWaterLoadInputs.dict
    except: pass

    try: r["inputs"]["ProcessHeatLoad"] = meta.ProcessHeatLoadInputs.dict
    except: pass

    try: r["inputs"]["CHP"] = meta.CHPInputs.dict
    except: pass

    try: r["inputs"]["AbsorptionChiller"] = meta.AbsorptionChillerInputs.dict
    except: pass

    try: r["inputs"]["SteamTurbine"] = meta.SteamTurbineInputs.dict
    except: pass

    try: r["inputs"]["GHP"] = meta.GHPInputs.dict
    except: pass    

    try: r["inputs"]["ElectricHeater"] = meta.ElectricHeaterInputs.dict
    except: pass    

    try: r["inputs"]["ASHPSpaceHeater"] = meta.ASHPSpaceHeaterInputs.dict
    except: pass    

    try: r["inputs"]["ASHPWaterHeater"] = meta.ASHPWaterHeaterInputs.dict
    except: pass  

    try:
        r["outputs"] = dict()
        r["messages"] = dict()
        try:
            msgs = meta.Message.all()
            for msg in msgs:
                r["messages"][msg.message_type] = msg.message
            
            # Add a dictionary of warnings and errors from REopt
            # key = location of warning, error, or uncaught error
            # value = vector of text from REopt
            #   In case of uncaught error, vector length > 1
            reopt_messages = meta.REoptjlMessageOutputs.dict
            for msg_type in ["errors","warnings"]:
                r["messages"][msg_type] = dict()
                for m in range(0,len(reopt_messages[msg_type])):
                    txt = reopt_messages[msg_type][m]
                    txt = re.sub('[^0-9a-zA-Z_.,() ]+', '', txt)
                    k = txt.split(',')[0]
                    v = txt.split(',')[1:]
                    r["messages"][msg_type][k] = v
            r["messages"]["has_stacktrace"] = reopt_messages["has_stacktrace"]            
        except: pass

        try:
            r["outputs"]["Financial"] = meta.FinancialOutputs.dict
            r["outputs"]["ElectricTariff"] = meta.ElectricTariffOutputs.dict
            r["outputs"]["ElectricUtility"] = meta.ElectricUtilityOutputs.dict
            r["outputs"]["ElectricLoad"] = meta.ElectricLoadOutputs.dict
            r["outputs"]["Site"] = meta.SiteOutputs.dict
        except: pass

        try:
            pvs = meta.PVOutputs.all()
            if len(pvs) == 1:
                r["outputs"]["PV"] = pvs[0].dict
            elif len(pvs) > 1:
                r["outputs"]["PV"] = []
                for pv in pvs:
                    r["outputs"]["PV"].append(pv.dict)
        except: pass
        try: r["outputs"]["ElectricStorage"] = meta.ElectricStorageOutputs.dict
        except: pass
        try: r["outputs"]["Generator"] = meta.GeneratorOutputs.dict
        except: pass
        try: r["outputs"]["Wind"] = meta.WindOutputs.dict
        except: pass
        try: r["outputs"]["ExistingChiller"] = meta.ExistingChillerOutputs.dict
        except: pass
        try: r["outputs"]["ExistingBoiler"] = meta.ExistingBoilerOutputs.dict
        except: pass
        try: r["outputs"]["Boiler"] = meta.BoilerOutputs.dict
        except: pass
        try: r["outputs"]["Outages"] = meta.OutageOutputs.dict
        except: pass

        try: r["outputs"]["HotThermalStorage"] = meta.HotThermalStorageOutputs.dict
        except: pass
        try: r["outputs"]["ColdThermalStorage"] = meta.ColdThermalStorageOutputs.dict
        except: pass
        try: r["outputs"]["CHP"] = meta.CHPOutputs.dict
        except: pass
        try: r["outputs"]["AbsorptionChiller"] = meta.AbsorptionChillerOutputs.dict
        except: pass
        try: r["outputs"]["HeatingLoad"] = meta.HeatingLoadOutputs.dict
        except: pass
        try: r["outputs"]["CoolingLoad"] = meta.CoolingLoadOutputs.dict
        except: pass
        try: r["outputs"]["SteamTurbine"] = meta.SteamTurbineOutputs.dict
        except: pass
        try: r["outputs"]["GHP"] = meta.GHPOutputs.dict
        except: pass
        try: r["outputs"]["ElectricHeater"] = meta.ElectricHeaterOutputs.dict
        except: pass    
        try: r["outputs"]["ASHPSpaceHeater"] = meta.ASHPSpaceHeaterOutputs.dict
        except: pass  
        try: r["outputs"]["ASHPWaterHeater"] = meta.ASHPWaterHeaterOutputs.dict
        except: pass

        for d in r["outputs"].values():
            if isinstance(d, dict):
                d.pop("meta_id", None)
            elif isinstance(d, list):
                for subd in d:
                    subd.pop("meta_id", None)
        # TODO fill out rest of out/inputs as they are added to REoptLite.jl
    except Exception as e:
        if 'RelatedObjectDoesNotExist' in str(type(e)):
            pass
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value.args[0], tb.format_tb(exc_traceback), task='reoptjl.views.results', 
                run_uuid=run_uuid)
            err.save_to_db()
            resp = make_error_resp(err.message)
            return JsonResponse(resp, status=500)
    
    if meta.status == "error":
        return JsonResponse(r, status=400)

    return JsonResponse(r)

def peak_load_outage_times(request):
    try:
        post_body = json.loads(request.body)
        seasonal_peaks = bool(post_body.get("seasonal_peaks"))
        outage_duration = int(post_body.get("outage_duration"))
        critical_load = np.array(list(post_body.get("critical_load")))
        start_not_center_on_peaks = bool(post_body.get("start_not_center_on_peaks"))
        
        if seasonal_peaks:
            winter_start = 334*24
            spring_start = 59*24
            summer_start = 151*24
            autumn_start = 243*24
            winter_load = np.append(critical_load[winter_start:], critical_load[0:spring_start])
            spring_load = critical_load[spring_start:summer_start]
            summer_load = critical_load[summer_start:autumn_start]
            autumn_load = critical_load[autumn_start:winter_start]
            peaks = np.array([
                (np.argmax(winter_load) + winter_start) % 8760 + 1, 
                np.argmax(spring_load) + spring_start + 1, 
                np.argmax(summer_load) + summer_start + 1, 
                np.argmax(autumn_load) + autumn_start + 1
            ])
        else:
            peaks = np.array([np.argmax(critical_load) + 1])
        if start_not_center_on_peaks: 
            outage_start_time_steps = peaks
        else:
            outage_start_time_steps = np.maximum(1,peaks - int(outage_duration / 2))

        return JsonResponse(
            {"outage_start_time_steps": outage_start_time_steps.tolist()},
            status=200
        )

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=400)

    except KeyError as e:
        return JsonResponse({"Error. Missing": str(e.args[0])}, status=400)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in outage_times_based_on_load_peaks endpoint. Check log for more."}, status=500)
    
def chp_defaults(request):
    inputs = {
        "hot_water_or_steam": request.GET.get("hot_water_or_steam"),
        "avg_boiler_fuel_load_mmbtu_per_hour": request.GET.get("avg_boiler_fuel_load_mmbtu_per_hour"),
        "prime_mover": request.GET.get("prime_mover"),
        "boiler_efficiency": request.GET.get("boiler_efficiency"),
        "avg_electric_load_kw": request.GET.get("avg_electric_load_kw"),
        "max_electric_load_kw": request.GET.get("max_electric_load_kw"),
        "is_electric_only": request.GET.get("is_electric_only")
    }

    if request.GET.get("size_class"):
        inputs["size_class"] = int(request.GET.get("size_class"))  # Not sure if this is necessary because we convert to int in http.jl

    if request.GET.get("thermal_efficiency"):
        inputs["thermal_efficiency"] = request.GET.get("thermal_efficiency")  # Conversion to correct type happens in http.jl

    try:
        julia_host = os.environ.get('JULIA_HOST', "julia")
        http_jl_response = requests.get("http://" + julia_host + ":8081/chp_defaults/", json=inputs)
        response = JsonResponse(
            http_jl_response.json(),
            status=http_jl_response.status_code
        )
        return response

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=400)

    except KeyError as e:
        return JsonResponse({"Error. Missing": str(e.args[0])}, status=400)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in chp_defaults endpoint. Check log for more."}, status=500)

def absorption_chiller_defaults(request):
    inputs = {
        "thermal_consumption_hot_water_or_steam": request.GET.get("thermal_consumption_hot_water_or_steam"), 
        "chp_prime_mover": request.GET.get("chp_prime_mover"),
        "boiler_type": request.GET.get("boiler_type"),
        "load_max_tons": request.GET.get("load_max_tons")
    }
    try:
        julia_host = os.environ.get('JULIA_HOST', "julia")
        http_jl_response = requests.get("http://" + julia_host + ":8081/absorption_chiller_defaults/", json=inputs)
        response = JsonResponse(
            http_jl_response.json()
        )
        return response

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=500)

    except KeyError as e:
        return JsonResponse({"Error. Missing": str(e.args[0])}, status=500)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in absorption_chiller_defaults endpoint. Check log for more."}, status=500)

def get_ashp_defaults(request):
    inputs = {}
    if request.GET.get("load_served") not in [None, "", []]:
        inputs["load_served"] = request.GET.get("load_served")
    else: 
        return JsonResponse({"Error: Missing input load_served in get_ashp_defaults endpoint."}, status=400)
    if request.GET.get("force_into_system") not in [None, "", []]:
        inputs["force_into_system"] = request.GET.get("force_into_system")
    else: 
        return JsonResponse({"Error: Missing input force_into_system in get_ashp_defaults endpoint."}, status=400)
    try:
        julia_host = os.environ.get('JULIA_HOST', "julia")
        http_jl_response = requests.get("http://" + julia_host + ":8081/get_ashp_defaults/", json=inputs)
        response = JsonResponse(
            http_jl_response.json(),
            status=http_jl_response.status_code
        )
        return response

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=400)

    except KeyError as e:
        return JsonResponse({"Error. Missing": str(e.args[0])}, status=400)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in get_ashp_defaults endpoint. Check log for more."}, status=500)


def simulated_load(request):
    try:      
        # Build inputs dictionary to send to http.jl /simulated_load endpoint
        inputs = {}
        
        # Required for GET - will throw a Missing Error if not included
        if request.method == "GET":
            valid_keys = ["doe_reference_name","industrial_reference_name","latitude","longitude","load_type","percent_share","annual_kwh",
                "monthly_totals_kwh","annual_mmbtu","annual_fraction","annual_tonhour","monthly_tonhour",
                "monthly_mmbtu","monthly_fraction","max_thermal_factor_on_peak_load","chiller_cop",
                "addressable_load_fraction", "cooling_doe_ref_name", "cooling_pct_share", "boiler_efficiency",
                "normalize_and_scale_load_profile_input", "year"]
            for key in request.GET.keys():
                k = key
                if "[" in key:
                    k = key.split('[')[0]
                if k not in valid_keys:
                    raise ValueError("{} is not a valid input parameter".format(key))
            
            inputs["latitude"] = float(request.GET['latitude'])  # need float to convert unicode
            inputs["longitude"] = float(request.GET['longitude'])
            # Optional load_type - will default to "electric"
            inputs["load_type"] = request.GET.get('load_type')

            if inputs["load_type"] == 'process_heat':
                expected_reference_name = 'industrial_reference_name'
            else:
                expected_reference_name = 'doe_reference_name'

            # This parses the GET request way of sending a list/array for doe_reference_name, 
            # i.e. doe_reference_name[0], doe_reference_name[1], etc along with percent_share[0], percent_share[1]
            if expected_reference_name in request.GET.keys():
                inputs[expected_reference_name] = str(request.GET.get(expected_reference_name))
            elif f'{expected_reference_name}[0]' in request.GET.keys():
                idx = 0
                doe_reference_name = []
                percent_share_list = []
                while '{}[{}]'.format(expected_reference_name, idx) in request.GET.keys():
                    doe_reference_name.append(str(request.GET['{}[{}]'.format(expected_reference_name, idx)]))
                    if 'percent_share[{}]'.format(idx) in request.GET.keys():
                        percent_share_list.append(float(request.GET['percent_share[{}]'.format(idx)]))
                    idx += 1
                inputs[expected_reference_name] = doe_reference_name
                inputs["percent_share"] = percent_share_list

            # When wanting cooling profile based on building type(s) for cooling, need separate cooling building(s)
            if 'cooling_doe_ref_name' in request.GET.keys():
                inputs["cooling_doe_ref_name"] = str(request.GET.get('cooling_doe_ref_name'))
            elif 'cooling_doe_ref_name[0]' in request.GET.keys():
                idx = 0
                cooling_doe_ref_name = []
                cooling_pct_share_list = []
                while 'cooling_doe_ref_name[{}]'.format(idx) in request.GET.keys():
                    cooling_doe_ref_name.append(str(request.GET['cooling_doe_ref_name[{}]'.format(idx)]))
                    if 'cooling_pct_share[{}]'.format(idx) in request.GET.keys():
                        cooling_pct_share_list.append(float(request.GET['cooling_pct_share[{}]'.format(idx)]))
                    idx += 1
                inputs["cooling_doe_ref_name"] = cooling_doe_ref_name
                inputs["cooling_pct_share"] = cooling_pct_share_list                

            # Build the rest of inputs for http.jl /simulated_load endpoint
            other_keys_types = ["annual", "monthly", "max_thermal_factor", "chiller_cop", "addressable"]
            for key in valid_keys:
                for key_type in other_keys_types:
                    if key_type in key:
                        if (key_type in ["monthly", "addressable"]) and request.GET.get(key + "[0]") is not None:
                            try: 
                                monthly_list  = [float(request.GET.get(key+'[{}]'.format(i))) for i in range(12)]
                                inputs[key] = monthly_list
                            except: 
                                return JsonResponse({"Error. Monthly data does not contain 12 valid entries"})
                        elif request.GET.get(key) is not None:
                            inputs[key] = float(request.GET.get(key))            

        if request.method == "POST":
            data = json.loads(request.body)
            required_post_fields = ["load_type", "normalize_and_scale_load_profile_input", "load_profile", "year"]
            for field in required_post_fields:
                # TODO make year optional?
                inputs[field] = data[field]
            if inputs["load_type"] == "electric":
                for energy in ["annual_kwh", "monthly_totals_kwh"]:
                    if data.get(energy) is not None:
                        inputs[energy] = data.get(energy)
            elif inputs["load_type"] in ["space_heating", "domestic_hot_water", "process_heat"]:
                for energy in ["annual_mmbtu", "monthly_mmbtu"]:
                    if data.get(energy) is not None:
                        inputs[energy] = data.get(energy)
            elif inputs["load_type"] == "cooling":
                for energy in ["annual_tonhour", "monthly_tonhour"]:
                    if data.get(energy) is not None:
                        inputs[energy] = data.get(energy)
            # TODO cooling, not in REopt.jl yet
        
        # TODO consider changing all requests to POST so that we don't have to do the weird array processing like percent_share[0], [1], etc?
        # json.dump(inputs, open("sim_load_post.json", "w"))
        julia_host = os.environ.get('JULIA_HOST', "julia")
        http_jl_response = requests.get("http://" + julia_host + ":8081/simulated_load/", json=inputs)
        response = JsonResponse(
            http_jl_response.json(),
            status=http_jl_response.status_code
        )
        
        return response

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=500)

    except KeyError as e:
        return JsonResponse({"Error. Missing": str(e.args[0])}, status=500)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in simulated_load endpoint. Check log for more."}, status=500)

def ghp_efficiency_thermal_factors(request):
    """
    GET default GHP heating and cooling thermal efficiency factors based on the climate zone from the lat/long input
    param: latitude: latitude of the site location
    param: longitude: longitude of the site location
    param: doe_reference_name: commercial reference building name
    return: climate_zone: climate zone of the site location
    return: nearest_city: nearest major city from the lat/long used for ASHRAE climate zone
    return: space_heating_efficiency_thermal_factor: default value for GHP.space_heating_efficiency_thermal_factor
    return: cooling_efficiency_thermal_factor: default value for GHP.cooling_efficiency_thermal_factor
    """    
    try:
        latitude = float(request.GET['latitude'])  # need float to convert unicode
        longitude = float(request.GET['longitude'])
        doe_reference_name = request.GET['doe_reference_name']

        inputs_dict = {"latitude": latitude,
                        "longitude": longitude,
                        "doe_reference_name": doe_reference_name}

        julia_host = os.environ.get('JULIA_HOST', "julia")
        http_jl_response = requests.get("http://" + julia_host + ":8081/ghp_efficiency_thermal_factors/", json=inputs_dict)
        response = JsonResponse(
            http_jl_response.json()
        )
        return response
    
    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=500)

    except KeyError as e:
        return JsonResponse({"Error. Missing": str(e.args[0])}, status=500)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in ghp_efficiency_thermal_factors endpoint. Check log for more."}, status=500)

def get_existing_chiller_default_cop(request):
    """
    GET default existing chiller COP using the max thermal cooling load.
    param: existing_chiller_max_thermal_factor_on_peak_load: max thermal factor on peak cooling load, i.e., "oversizing" of existing chiller [fraction]
    param: max_load_kw: maximum electrical load [kW]
    param: max_load_ton: maximum thermal cooling load [ton]
    return: existing_chiller_cop: default COP of existing chiller [fraction]  
    """
    try:
        existing_chiller_max_thermal_factor_on_peak_load = request.GET.get('existing_chiller_max_thermal_factor_on_peak_load')
        if existing_chiller_max_thermal_factor_on_peak_load not in [None, ""]:
            existing_chiller_max_thermal_factor_on_peak_load = float(existing_chiller_max_thermal_factor_on_peak_load)
        else: 
            existing_chiller_max_thermal_factor_on_peak_load = 1.25  # default from REopt.jl

        max_load_kw = request.GET.get('max_load_kw')
        if max_load_kw not in [None, ""]:
            max_load_kw = float(max_load_kw)
        else: 
            max_load_kw = None

        max_load_ton = request.GET.get('max_load_ton')
        if max_load_ton not in [None, ""]:
            max_load_kw_thermal = float(max_load_ton) * 3.51685  # kWh thermal per ton-hour
        else: 
            max_load_kw_thermal = None
            
        inputs_dict = {
            "existing_chiller_max_thermal_factor_on_peak_load": existing_chiller_max_thermal_factor_on_peak_load,
            "max_load_kw": max_load_kw,
            "max_load_kw_thermal": max_load_kw_thermal
        }

        julia_host = os.environ.get('JULIA_HOST', "julia")
        http_jl_response = requests.get("http://" + julia_host + ":8081/get_existing_chiller_default_cop/", json=inputs_dict)
        response = JsonResponse(
            http_jl_response.json()
        )
        return response

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=500)

    except KeyError as e:
        return JsonResponse({"Error. Missing": str(e.args[0])}, status=500)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in get_existing_chiller_default_cop endpoint. Check log for more."}, status=500)


# Inputs: 1-many run_uuid strings as single comma separated array
# Output: list of JSON summaries
# This function will query requested UUIDs and return their summary back to requestor
def summary_by_runuuids(request):

    run_uuids = json.loads(request.body)['run_uuids']

    if len(run_uuids) == 0:
        return JsonResponse({'Error': 'Must provide one or more run_uuids'}, status=400)

    # Validate that user UUID is valid.
    for r_uuid in run_uuids:

        if type(r_uuid) != str:
            return JsonResponse({'Error': 'Provided run_uuids type error, must be string. ' + str(r_uuid)}, status=400)
        
        try:
            uuid.UUID(r_uuid)  # raises ValueError if not valid uuid

        except ValueError as e:
            if e.args[0] == "badly formed hexadecimal UUID string":
                return JsonResponse({"Error": str(e.message)}, status=404)
            else:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                err = UnexpectedError(exc_type, exc_value, exc_traceback, task='summary_by_runuuids', run_uuids=run_uuids)
                err.save_to_db()
                return JsonResponse({"Error": str(err.message)}, status=404)
    
    try:
        # Dictionary to store all results. Primary key = run_uuid and secondary key = data values from each uuid
        summary_dict = dict()

        # Create Querysets: Select all objects associate with a user_uuid, Order by `created` column
        scenarios = APIMeta.objects.filter(run_uuid__in=run_uuids).only(
            'run_uuid',
            'status',
            'created'
        ).order_by("-created")

        if len(scenarios) > 0: # this should be either 0 or 1 as there are no duplicate run_uuids
            
            # Get summary information for all selected scenarios
            summary_dict = queryset_for_summary(scenarios, summary_dict)

            # Create eventual response dictionary
            return_dict = dict()
            # return_dict['user_uuid'] = user_uuid # no user uuid
            scenario_summaries = []
            for k in summary_dict.keys():
                scenario_summaries.append(summary_dict[k])
            
            return_dict['scenarios'] = scenario_summaries

            response = JsonResponse(return_dict, status=200, safe=False)
            return response
        else:
            response = JsonResponse({"Error": "No scenarios found for run_uuids '{}'".format(run_uuids)}, content_type='application/json', status=404)
            return response

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='summary_by_runuuids', run_uuids=run_uuids)
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=404)

# Inputs: 1-many run_uuid strings as single comma separated array
# Inputs: 1-many portfolio_uuid strings as single comma separated array
# Output: 200 or OK
# This function link independent run_uuids to a portfolio_uuid. The portfolio ID doesnt have to exit, run_uuids must exist in DB.
def link_run_uuids_to_portfolio_uuid(request):

    request_body = json.loads(request.body)
    run_uuids = request_body['run_uuids']
    por_uuids = request_body['portfolio_uuids']

    if len(run_uuids) != len(por_uuids):
        return JsonResponse({'Error': 'Must provide one or more run_uuids and the same number of portfolio_uuids'}, status=400)

    # Validate that all UUIDs are valid.
    for r_uuid in run_uuids+por_uuids:

        if type(r_uuid) != str:
            return JsonResponse({'Error': 'Provided uuid type error, must be string. ' + str(r_uuid)}, status=400)
        
        try:
            uuid.UUID(r_uuid)  # raises ValueError if not valid uuid

        except ValueError as e:
            if e.args[0] == "badly formed hexadecimal UUID string":
                return JsonResponse({"Error": str(e.message)}, status=404)
            else:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                err = UnexpectedError(exc_type, exc_value, exc_traceback, task='summary_by_runuuids', run_uuids=run_uuids)
                err.save_to_db()
                return JsonResponse({"Error": str(err.message)}, status=404)
    
    try:
        
        for r_uuid,p_uuid in zip(run_uuids, por_uuids):
        
            # Create Querysets: Select all objects associate with a user_uuid, Order by `created` column
            scenario = APIMeta.objects.filter(run_uuid=r_uuid).only(
                'run_uuid',
                'portfolio_uuid'
            )

            if len(scenario) > 0:

                for s in scenario:
                    s.portfolio_uuid = p_uuid
                    s.save()

                # Existing portfolio runs could have been "unlinked" from portfolio
                # so they are independent and show up in summary endpoint. If these runs
                # are re-linked with a portfolio, their portfolio_id is updated above.
                # BUT these runs could still show up under `Summary` results (niche case)
                # because they are present in PortfolioUnlinkedRuns.
                # Below, these runs are removed from PortfolioUnlinkedRuns
                # so they are "linked" to a portfolio and do not show up under `Summary`
                if PortfolioUnlinkedRuns.objects.filter(run_uuid=r_uuid).exists():
                    obj = PortfolioUnlinkedRuns.objects.get(run_uuid=r_uuid)
                    obj.delete()
                    resp_str = ' and deleted run entry from PortfolioUnlinkedRuns'
                else:
                    resp_str = ''
            else:
                # Stop processing on first bad run_uuid
                response = JsonResponse({"Error": "No scenarios found for run_uuid '{}'".format(r_uuid)}, content_type='application/json', status=500)
                return response
        
        response = JsonResponse({"Success": "All runs associated with given portfolios'{}'".format(resp_str)}, status=200, safe=False)
        return response

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='summary_by_runuuids', run_uuids=run_uuids)
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=404)

# Inputs: 1 user_uuid
# Output: Return summary information for all runs associated with the user
# Output: Portfolio_uuid for returned runs must be "" (empty) or in unlinked portfolio runs (i.e. user unlinked a run from a portforlio)
# Output: Remove any user unlinked runs and finally order by `created` column
# Returns all user runs not actively tied to a portfolio
def summary(request, user_uuid):
    """
    Retrieve a summary of scenarios for given user_uuid
    :param request:
    :param user_uuid:
    :return:
        {
            "user_uuid",
            "scenarios":
                [{
                  "run_uuid",                   # Run ID
                  "status",                     # Status
                  "created",                    # Date
                  "description",                # Description
                  "focus",                      # Focus
                  "address",                    # Address
                  "urdb_rate_name",             # Utility Tariff
                  "doe_reference_name",         # Load Profile
                  "npv_us_dollars",             # Net Present Value ($)
                  "net_capital_costs",          # DG System Cost ($)
                  "year_one_savings_us_dollars",# Year 1 Savings ($)
                  "pv_kw",                      # PV Size (kW)
                  "wind_kw",                    # Wind Size (kW)
                  "gen_kw",                     # Generator Size (kW)
                  "batt_kw",                    # Battery Power (kW)
                  "batt_kwh"                    # Battery Capacity (kWh)
                  ""
                }]
        }
    """

    # Validate that user UUID is valid.
    try:
        uuid.UUID(user_uuid)  # raises ValueError if not valid uuid

    except ValueError as e:
        if e.args[0] == "badly formed hexadecimal UUID string":
            return JsonResponse({"Error": str(e.message)}, status=404)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value, exc_traceback, task='summary', user_uuid=user_uuid)
            err.save_to_db()
            return JsonResponse({"Error": str(err.message)}, status=404)

    try:
        # Dictionary to store all results. Primary key = run_uuid and secondary key = data values from each uuid
        summary_dict = dict()

        # Create Querysets: Select all objects associate with a user_uuid. portfolio_uuid must be "" (empty) or in unlinked portfolio runs
        # Remove any unlinked runs and finally order by `created` column
        api_metas = APIMeta.objects.filter(
            Q(user_uuid=user_uuid),
            Q(portfolio_uuid = "") | Q(run_uuid__in=[i.run_uuid for i in PortfolioUnlinkedRuns.objects.filter(user_uuid=user_uuid)])
        ).exclude(
            run_uuid__in=[i.run_uuid for i in UserUnlinkedRuns.objects.filter(user_uuid=user_uuid)]
        ).only(
            'run_uuid',
            'user_uuid',
            'portfolio_uuid',
            'status',
            'created'
        ).order_by("-created")

        if len(api_metas) > 0:
            summary_dict = queryset_for_summary(api_metas, summary_dict)
            response = JsonResponse(create_summary_dict(user_uuid,summary_dict), status=200, safe=False)
            return response
        else:
            response = JsonResponse({"Error": "No scenarios found for user '{}'".format(user_uuid)}, content_type='application/json', status=404)
            return response

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='summary', user_uuid=user_uuid)
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=404)

# Same as Summary but by chunks
def summary_by_chunk(request, user_uuid, chunk):

    # Dictionary to store all results. Primary key = run_uuid and secondary key = data values from each uuid
    summary_dict = dict()

    try:
        uuid.UUID(user_uuid)  # raises ValueError if not valid uuid

    except ValueError as e:
        if e.args[0] == "badly formed hexadecimal UUID string":
            return JsonResponse({"Error": str(e.message)}, status=404)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value, exc_traceback, task='summary', user_uuid=user_uuid)
            err.save_to_db()
            return JsonResponse({"Error": str(err.message)}, status=404)
    
    try:
        try:
            # chunk size is an optional URL parameter which defines the number of chunks into which to 
            # divide all user summary results. It must be a positive integer.
            default_chunk_size = 30
            chunk_size = int(request.GET.get('chunk_size') or default_chunk_size)
            if chunk_size != float(request.GET.get('chunk_size') or default_chunk_size):
                return JsonResponse({"Error": "Chunk size must be an integer."}, status=400)    
        except:
            return JsonResponse({"Error": "Chunk size must be a positive integer."}, status=400)
        
        try:
            # chunk is the 1-indexed indice of the chunks for which to return results.
            # chunk is a mandatory input from URL, different from chunk_size.
            # It must be a positive integer.
            chunk = int(chunk)
            if chunk < 1:
                response = JsonResponse({"Error": "Chunks are 1-indexed, please provide a chunk index greater than or equal to 1"}
                    , content_type='application/json', status=400)
                return response
        except:
            return JsonResponse({"Error": "Chunk number must be a 1-indexed integer."}, status=400)
        
        # Create Querysets: Select all objects associate with a user_uuid, portfolio_uuid="", Order by `created` column
        api_metas = APIMeta.objects.filter(
            Q(user_uuid=user_uuid),
            Q(portfolio_uuid = "") | Q(run_uuid__in=[i.run_uuid for i in PortfolioUnlinkedRuns.objects.filter(user_uuid=user_uuid)])
        ).exclude(
            run_uuid__in=[i.run_uuid for i in UserUnlinkedRuns.objects.filter(user_uuid=user_uuid)]
        ).only(
            'run_uuid',
            'status',
            'created'
        ).order_by("-created")
        
        total_scenarios = len(api_metas)
        if total_scenarios == 0:
            response = JsonResponse({"Error": "No scenarios found for user '{}'".format(user_uuid)}, content_type='application/json', status=404)
            return response
        
        # Determine total number of chunks from current query of user results based on the chunk size
        total_chunks = total_scenarios/float(chunk_size)
        # If the last chunk is only patially full, i.e. there is a remainder, then add 1 so when it 
        # is converted to an integer the result will reflect the true total number of chunks
        if total_chunks%1 > 0: 
            total_chunks = total_chunks + 1
        # Make sure total chunks is an integer
        total_chunks = int(total_chunks)
        
        # Catch cases where user queries for a chunk that is more than the total chunks for the user
        if chunk > total_chunks:
            response = JsonResponse({"Error": "Chunk index {} is greater than the total number of chunks ({}) at a chunk size of {}".format(
                chunk, total_chunks, chunk_size)}, content_type='application/json', status=400)
            return response
        
        # Filter scenarios to the chunk
        start_idx = max((chunk-1) * chunk_size, 0)
        end_idx = min(chunk * chunk_size, total_scenarios)
        api_metas_by_chunk = api_metas[start_idx: end_idx]

        summary_dict = queryset_for_summary(api_metas_by_chunk, summary_dict)
        response = JsonResponse(create_summary_dict(user_uuid,summary_dict), status=200, safe=False)
        return response

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='summary', user_uuid=user_uuid)
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=404)

# Take summary_dict and convert it to the desired format for response. Also add any missing key/val pairs
def create_summary_dict(user_uuid:str,summary_dict:dict):

    # if these keys are missing from a `scenario` we add 0s for them, all Floats.
    optional_keys = ["npv_us_dollars", "net_capital_costs", "year_one_savings_us_dollars", "pv_kw", "wind_kw", "gen_kw", "batt_kw", "batt_kwh"]

    # Create eventual response dictionary
    return_dict = dict()
    return_dict['user_uuid'] = user_uuid
    scenario_summaries = []
    for k in summary_dict.keys():

        d = summary_dict[k]

        # for opt_key in optional_keys:
        #     if opt_key not in d.keys():
        #         d[opt_key] = 0.0
        
        scenario_summaries.append(d)
    
    return_dict['scenarios'] = scenario_summaries
    
    return return_dict

# Query all django models for 1 or more run_uuids provided in inputs
# Return summary_dict which contains summary information for valid run_uuids
def queryset_for_summary(api_metas,summary_dict:dict):

    # Loop over all the APIMetas associated with a user_uuid, do something if needed
    for m in api_metas:
        # print(3, meta.run_uuid) #acces Meta fields like this
        summary_dict[str(m.run_uuid)] = dict()
        summary_dict[str(m.run_uuid)]['status'] = m.status
        summary_dict[str(m.run_uuid)]['run_uuid'] = str(m.run_uuid)
        summary_dict[str(m.run_uuid)]['user_uuid'] = str(m.user_uuid)
        summary_dict[str(m.run_uuid)]['portfolio_uuid'] = str(m.portfolio_uuid)
        summary_dict[str(m.run_uuid)]['created'] = str(m.created)
        
    run_uuids = summary_dict.keys()

    # Create query of all UserProvidedMeta objects where their run_uuid is in api_metas run_uuids.
    usermeta = UserProvidedMeta.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'description',
        'address'
    )

    if len(usermeta) > 0:
        for m in usermeta:
            summary_dict[str(m.meta.run_uuid)]['description'] = m.description
            summary_dict[str(m.meta.run_uuid)]['address'] = m.address
    
    utility = ElectricUtilityInputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'outage_start_time_step',
        'outage_end_time_step',
        'outage_durations',
        'outage_start_time_steps'
    )
    if len(utility) > 0:
        for m in utility:

            if m.outage_start_time_step is None:
                if len(m.outage_start_time_steps) == 0:
                    summary_dict[str(m.meta.run_uuid)]['focus'] = "Financial"
                else:
                    summary_dict[str(m.meta.run_uuid)]['focus'] = "Resilience"
                    summary_dict[str(m.meta.run_uuid)]['outage_duration'] = m.outage_durations[0] # all durations are same.
            else:
                # outage start timestep was provided, is 1 or more
                summary_dict[str(m.meta.run_uuid)]['outage_duration'] = m.outage_end_time_step - m.outage_start_time_step + 1
                summary_dict[str(m.meta.run_uuid)]['focus'] = "Resilience"
    
    site = SiteOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'lifecycle_emissions_reduction_CO2_fraction'
    )
    if len(site) > 0:
        for m in site:
            try:
                summary_dict[str(m.meta.run_uuid)]['emission_reduction_pct'] = m.lifecycle_emissions_reduction_CO2_fraction
            except:
                summary_dict[str(m.meta.run_uuid)]['emission_reduction_pct'] = 0.0

    
    site_inputs = SiteInputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'renewable_electricity_min_fraction',
        'renewable_electricity_max_fraction'
    )
    if len(site_inputs) > 0:
        for m in site_inputs:
            try: # can be NoneType
                if m.renewable_electricity_min_fraction > 0:
                    summary_dict[str(m.meta.run_uuid)]['focus'] = "Clean-energy"
            except:
                pass # is NoneType

            try: # can be NoneType
                if m.renewable_electricity_max_fraction > 0:
                    summary_dict[str(m.meta.run_uuid)]['focus'] = "Clean-energy"
            except:
                pass # is NoneType

    # Use settings to find out if it is an off-grid evaluation
    settings = Settings.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'off_grid_flag',
        'include_climate_in_objective',
        'include_health_in_objective'
    )
    if len(settings) > 0:
        for m in settings:
            if m.off_grid_flag:
                summary_dict[str(m.meta.run_uuid)]['focus'] = "Off-grid"
            
            if m.include_climate_in_objective or m.include_health_in_objective:
                summary_dict[str(m.meta.run_uuid)]['focus'] = "Clean-energy"

    tariffInputs = ElectricTariffInputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'urdb_rate_name'
    )
    if len(tariffInputs) > 0:
        for m in tariffInputs:
            if m.urdb_rate_name is None:
                summary_dict[str(m.meta.run_uuid)]['urdb_rate_name'] = 'Custom'
            else:
                summary_dict[str(m.meta.run_uuid)]['urdb_rate_name'] = m.urdb_rate_name
    
    tariffOuts = ElectricTariffOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'year_one_energy_cost_before_tax',
        'year_one_demand_cost_before_tax',
        'year_one_fixed_cost_before_tax',
        'year_one_min_charge_adder_before_tax',
        'year_one_energy_cost_before_tax_bau',
        'year_one_demand_cost_before_tax_bau',
        'year_one_fixed_cost_before_tax_bau',
        'year_one_min_charge_adder_before_tax_bau',
    )
    if len(tariffOuts) > 0:
        for m in tariffOuts:
            if (m.year_one_bill_before_tax_bau is not None) and (m.year_one_bill_before_tax is not None):
                summary_dict[str(m.meta.run_uuid)]['year_one_savings_us_dollars'] = m.year_one_bill_before_tax_bau - m.year_one_bill_before_tax
            else:
                summary_dict[str(m.meta.run_uuid)]['year_one_savings_us_dollars'] = None

    load = ElectricLoadInputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'loads_kw',
        'doe_reference_name'
    )
    if len(load) > 0:
        for m in load:
            if m.loads_kw is None:
                summary_dict[str(m.meta.run_uuid)]['doe_reference_name'] = m.doe_reference_name
            else:
                summary_dict[str(m.meta.run_uuid)]['doe_reference_name'] = 'Custom'


    fin = FinancialOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'npv',
        'initial_capital_costs_after_incentives',
        'lcc',
        'replacements_present_cost_after_tax',
        'lifecycle_capital_costs_plus_om_after_tax',
        'lifecycle_generation_tech_capital_costs',
        'lifecycle_storage_capital_costs',
        'lifecycle_production_incentive_after_tax'
    )
    if len(fin) > 0:
        for m in fin:
            if m.npv is not None:
                summary_dict[str(m.meta.run_uuid)]['npv_us_dollars'] = m.npv
            else:
                summary_dict[str(m.meta.run_uuid)]['npv_us_dollars'] = None
            summary_dict[str(m.meta.run_uuid)]['net_capital_costs'] = m.initial_capital_costs_after_incentives
            summary_dict[str(m.meta.run_uuid)]['lcc_us_dollars'] = m.lcc
            summary_dict[str(m.meta.run_uuid)]['replacements_present_cost_after_tax'] = m.replacements_present_cost_after_tax
            summary_dict[str(m.meta.run_uuid)]['lifecycle_capital_costs_plus_om_after_tax'] = m.lifecycle_capital_costs_plus_om_after_tax
            summary_dict[str(m.meta.run_uuid)]['total_capital_costs'] = m.lifecycle_generation_tech_capital_costs + m.lifecycle_storage_capital_costs - m.lifecycle_production_incentive_after_tax

    batt = ElectricStorageOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'size_kw',
        'size_kwh'
    )
    if len(batt) > 0:
        for m in batt:
            summary_dict[str(m.meta.run_uuid)]['batt_kw'] = m.size_kw  
            summary_dict[str(m.meta.run_uuid)]['batt_kwh'] = m.size_kwh
    
    pv = PVOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'size_kw'
    )
    if len(pv) > 0:
        for m in pv:
            summary_dict[str(m.meta.run_uuid)]['pv_kw'] = m.size_kw
    
    wind = WindOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'size_kw'
    )
    if len(wind) > 0:
        for m in wind:
            summary_dict[str(m.meta.run_uuid)]['wind_kw'] = m.size_kw

    gen = GeneratorOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'size_kw'
    )
    if len(gen) > 0:
        for m in gen:
            summary_dict[str(m.meta.run_uuid)]['gen_kw'] = m.size_kw

    # assumes run_uuids exist in both CHPInputs and CHPOutputs
    chpInputs = CHPInputs.objects.filter(meta__run_uuid__in=run_uuids).only(
            'meta__run_uuid',
            'thermal_efficiency_full_load'
    )
    thermal_efficiency_full_load = dict()
    if len(chpInputs) > 0:
        for m in chpInputs:
            thermal_efficiency_full_load[str(m.meta.run_uuid)] = m.thermal_efficiency_full_load
    
    chpOutputs = CHPOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
            'meta__run_uuid',
            'size_kw'
    )
    if len(chpOutputs) > 0:
        for m in chpOutputs:
            if thermal_efficiency_full_load[str(m.meta.run_uuid)] == 0:
                summary_dict[str(m.meta.run_uuid)]['prime_gen_kw'] = m.size_kw
            else:
                summary_dict[str(m.meta.run_uuid)]['chp_kw'] = m.size_kw
    
    ghpOutputs = GHPOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
            'meta__run_uuid',
            'ghp_option_chosen',
            'ghpghx_chosen_outputs',
            'size_heat_pump_ton',
            'size_wwhp_heating_pump_ton',
            'size_wwhp_cooling_pump_ton'
    )
    if len(ghpOutputs) > 0:
        for m in ghpOutputs:
            if m.ghp_option_chosen > 0:
                if m.size_heat_pump_ton is not None:
                    summary_dict[str(m.meta.run_uuid)]['ghp_ton'] = m.size_heat_pump_ton
                else:
                    summary_dict[str(m.meta.run_uuid)]['ghp_cooling_ton'] = m.size_wwhp_cooling_pump_ton
                    summary_dict[str(m.meta.run_uuid)]['ghp_heating_ton'] = m.size_wwhp_heating_pump_ton
                summary_dict[str(m.meta.run_uuid)]['ghp_n_bores'] = m.ghpghx_chosen_outputs['number_of_boreholes']
    
    elecHeater = ElectricHeaterOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
            'meta__run_uuid',
            'size_mmbtu_per_hour'
    )
    if len(elecHeater) > 0:
        for m in elecHeater:
            summary_dict[str(m.meta.run_uuid)]['electric_heater_mmbtu_per_hour'] = m.size_mmbtu_per_hour

    ashpSpaceHeater = ASHPSpaceHeaterOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
            'meta__run_uuid',
            'size_ton'
    )
    if len(ashpSpaceHeater) > 0:
        for m in ashpSpaceHeater:
            summary_dict[str(m.meta.run_uuid)]['ASHPSpace_heater_ton'] = m.size_ton

    ashpWaterHeater = ASHPWaterHeaterOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
            'meta__run_uuid',
            'size_ton'
    )
    if len(ashpWaterHeater) > 0:
        for m in ashpWaterHeater:
            summary_dict[str(m.meta.run_uuid)]['ASHPWater_heater_ton'] = m.size_ton
    hottes = HotThermalStorageOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'size_gal'
    )
    if len(hottes) > 0:
        for m in hottes:
            summary_dict[str(m.meta.run_uuid)]['hottes_gal'] = m.size_gal
    
    coldtes = ColdThermalStorageOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'size_gal'
    )
    if len(coldtes) > 0:
        for m in coldtes:
            summary_dict[str(m.meta.run_uuid)]['coldtes_gal'] = m.size_gal
    

    abschillTon = AbsorptionChillerOutputs.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'size_ton'
    )
    if len(abschillTon) > 0:
        for m in abschillTon:
            summary_dict[str(m.meta.run_uuid)]['absorpchl_ton'] = m.size_ton

    return summary_dict

# Inputs: user_uuid and run_uuid to unlink from the user
# Outputs: 200 or OK
# add an entry to the PortfolioUnlinkedRuns for the given portfolio_uuid and run_uuid, indicating they have been unlinked
def unlink(request, user_uuid, run_uuid):

    """
    add an entry to the UserUnlinkedRuns for the given user_uuid and run_uuid
    """
    content = {'user_uuid': user_uuid, 'run_uuid': run_uuid}
    for name, check_id in content.items():
        try:
            uuid.UUID(check_id)  # raises ValueError if not valid uuid
        except ValueError as e:
            if e.args[0] == "badly formed hexadecimal UUID string":
                return JsonResponse({"Error": "{} {}".format(name, e.args[0]) }, status=400)
            else:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                if name == 'user_uuid':
                    err = UnexpectedError(exc_type, exc_value, exc_traceback, task='unlink', user_uuid=check_id)
                if name == 'run_uuid':
                    err = UnexpectedError(exc_type, exc_value, exc_traceback, task='unlink', run_uuid=check_id)
                err.save_to_db()
                return JsonResponse({"Error": str(err.message)}, status=400)

    try:
        if not APIMeta.objects.filter(user_uuid=user_uuid).exists():
            return JsonResponse({"Error": "User {} does not exist".format(user_uuid)}, status=400)


        runs = APIMeta.objects.filter(user_uuid=user_uuid)
        if len(runs) == 0:
            return JsonResponse({"Error": "Run {} does not exist".format(run_uuid)}, status=400)
        else:
            if runs[0].user_uuid != user_uuid:
                return JsonResponse({"Error": "Run {} is not associated with user {}".format(run_uuid, user_uuid)}, status=400)

        if not UserUnlinkedRuns.objects.filter(run_uuid=run_uuid).exists():
            UserUnlinkedRuns.create(**content)
            return JsonResponse({"Success": "user_uuid {} unlinked from run_uuid {}".format(user_uuid, run_uuid)},
                                status=201)
        else:
            return JsonResponse({"Nothing changed": "user_uuid {} is already unlinked from run_uuid {}".format(user_uuid, run_uuid)},
                                status=208)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='unlink', user_uuid=user_uuid)
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=404)

# Inputs: user_uuid, portfolio_uuid, and run_uuid to unlink from the portfolio
# Outputs: 200 or OK
# add an entry to the PortfolioUnlinkedRuns for the given portfolio_uuid and run_uuid, indicating they have been unlinked
def unlink_from_portfolio(request, user_uuid, portfolio_uuid, run_uuid):

    """
    add an entry to the PortfolioUnlinkedRuns for the given portfolio_uuid and run_uuid
    """
    content = {'user_uuid': user_uuid, 'portfolio_uuid': portfolio_uuid, 'run_uuid': run_uuid}
    for name, check_id in content.items():
        try:
            uuid.UUID(check_id)  # raises ValueError if not valid uuid
        except ValueError as e:
            if e.args[0] == "badly formed hexadecimal UUID string":
                return JsonResponse({"Error": "{} {}".format(name, e.args[0]) }, status=400)
            else:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                if name == 'user_uuid':
                    err = UnexpectedError(exc_type, exc_value, exc_traceback, task='unlink', user_uuid=check_id)
                if name == 'portfolio_uuid':
                    err = UnexpectedError(exc_type, exc_value, exc_traceback, task='unlink', portfolio_uuid=check_id)
                if name == 'run_uuid':
                    err = UnexpectedError(exc_type, exc_value, exc_traceback, task='unlink', run_uuid=check_id)
                err.save_to_db()
                return JsonResponse({"Error": str(err.message)}, status=400)
    
    try:
        if not APIMeta.objects.filter(portfolio_uuid=portfolio_uuid).exists():
            return JsonResponse({"Error": "Portfolio {} does not exist".format(portfolio_uuid)}, status=400)


        runs = APIMeta.objects.filter(run_uuid=run_uuid)
        if len(runs) == 0:
            return JsonResponse({"Error": "Run {} does not exist".format(run_uuid)}, status=400)
        else:
            if runs[0].portfolio_uuid != portfolio_uuid:
                return JsonResponse({"Error": "Run {} is not associated with portfolio {}".format(run_uuid, portfolio_uuid)}, status=400)
            elif runs[0].user_uuid != user_uuid:
                return JsonResponse({"Error": "Run {} is not associated with user {}".format(run_uuid, user_uuid)}, status=400)
            else:
                pass
        
        # Run exists and is tied to porfolio provided in request, hence unlink now.
        if not PortfolioUnlinkedRuns.objects.filter(run_uuid=run_uuid).exists():
            PortfolioUnlinkedRuns.create(**content)
            return JsonResponse({"Success": "run_uuid {} unlinked from portfolio_uuid {}".format(run_uuid, portfolio_uuid)},
                                status=201)
        else:
            return JsonResponse({"Nothing changed": "run_uuid {} is already unlinked from portfolio_uuid {}".format(run_uuid, portfolio_uuid)},
                                status=208)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='unlink', portfolio_uuid=portfolio_uuid)
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=404)

def avert_emissions_profile(request):
    try:
        inputs = {
            "latitude": request.GET['latitude'], # need to do float() to convert unicode?
            "longitude": request.GET['longitude'],
            "load_year": request.GET['load_year']
        }
        julia_host = os.environ.get(
            'JULIA_HOST', 
            "julia"
        )
        http_jl_response = requests.get(
            "http://" + julia_host + ":8081/avert_emissions_profile/", 
            json=inputs
        )
        response = JsonResponse(
            http_jl_response.json(),
            status=http_jl_response.status_code
        )
        return response

    except KeyError as e:
        return JsonResponse({"Error. Missing Parameter": str(e.args[0])}, status=400)

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=400)

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.error(debug_msg)
        return JsonResponse({"Error": "Unexpected Error. Please check your input parameters and contact reopt@nrel.gov if problems persist."}, status=500)

def cambium_emissions_profile(request):
    try:
        inputs = {
            "scenario": request.GET['scenario'], 
            "location_type": request.GET['location_type'],
            "latitude": request.GET['latitude'], 
            "longitude": request.GET['longitude'],
            "start_year": request.GET['start_year'],
            "lifetime": request.GET['lifetime'],
            "metric_col": request.GET['metric_col'],
            "grid_level": request.GET['grid_level'],
            # "time_steps_per_hour": request.GET['time_steps_per_hour'],
            "load_year": request.GET['load_year']
        }
        julia_host = os.environ.get(
            'JULIA_HOST', 
            "julia"
        )
        http_jl_response = requests.get(
            "http://" + julia_host + ":8081/cambium_emissions_profile/", 
            json=inputs
        )
        response = JsonResponse(
            http_jl_response.json(),
            status=http_jl_response.status_code
        )
        return response

    except KeyError as e:
        return JsonResponse({"Error. Missing Parameter": str(e.args[0])}, status=400)

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=400)

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.error(debug_msg)
        return JsonResponse({"Error": "Unexpected Error. Please check your input parameters and contact reopt@nrel.gov if problems persist."}, status=500)

def easiur_costs(request):
    try:
        inputs = {
            "latitude": request.GET['latitude'], # need to do float() to convert unicode?
            "longitude": request.GET['longitude'],
            "inflation": request.GET['inflation']
        }
        julia_host = os.environ.get(
            'JULIA_HOST', 
            "julia"
        )
        http_jl_response = requests.get(
            "http://" + julia_host + ":8081/easiur_costs/", 
            json=inputs
        )
        response = JsonResponse(
            http_jl_response.json(),
            status=http_jl_response.status_code
        )
        return response

    except KeyError as e:
        return JsonResponse({"Error. Missing Parameter": str(e.args[0])}, status=400)

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=400)

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.error(debug_msg)
        return JsonResponse({"Error": "Unexpected Error. Please check your input parameters and contact reopt@nrel.gov if problems persist."}, status=500)

# def fuel_emissions_rates(request):
#     try:

#         try:
#             response = JsonResponse({
#                 'CO2': {
#                     'generator_lb_per_gal': ValidateNestedInput.fuel_conversion_lb_CO2_per_gal,
#                     'lb_per_mmbtu': ValidateNestedInput.fuel_conversion_lb_CO2_per_mmbtu
#                     },
#                 'NOx': {
#                     'generator_lb_per_gal': ValidateNestedInput.fuel_conversion_lb_NOx_per_gal,
#                     'lb_per_mmbtu': ValidateNestedInput.fuel_conversion_lb_NOx_per_mmbtu
#                     },
#                 'SO2': {
#                     'generator_lb_per_gal': ValidateNestedInput.fuel_conversion_lb_SO2_per_gal,
#                     'lb_per_mmbtu': ValidateNestedInput.fuel_conversion_lb_SO2_per_mmbtu
#                     },
#                 'PM25': {
#                     'generator_lb_per_gal': ValidateNestedInput.fuel_conversion_lb_PM25_per_gal,
#                     'lb_per_mmbtu': ValidateNestedInput.fuel_conversion_lb_PM25_per_mmbtu
#                     }
#                 })
#             return response
#         except AttributeError as e:
#             return JsonResponse({"Error": str(e.args[0])}, status=500)

#     except KeyError as e:
#         return JsonResponse({"No parameters required."}, status=500)

#     except ValueError as e:
#         return JsonResponse({"Error": str(e.args[0])}, status=500)

#     except Exception:

#         exc_type, exc_value, exc_traceback = sys.exc_info()
#         debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
#                                                                             tb.format_tb(exc_traceback))
#         log.error(debug_msg)
#         return JsonResponse({"Error": "Unexpected Error. Please check your input parameters and contact reopt@nrel.gov if problems persist."}, status=500)

##############################################################################################################################
################################################# START Results Table #########################################################
##############################################################################################################################
def access_raw_data(run_uuids: List[str], request: Any) -> Dict[str, List[Dict[str, Any]]]:
    try:
        usermeta = UserProvidedMeta.objects.filter(meta__run_uuid__in=run_uuids).only('meta__run_uuid', 'description', 'address')
        meta_data_dict = {um.meta.run_uuid: {"description": um.description, "address": um.address} for um in usermeta}

        return {
            "scenarios": [
                {
                    "run_uuid": str(run_uuid),
                    "full_data": summarize_vector_data(request, run_uuid),
                    "meta_data": meta_data_dict.get(run_uuid, {})
                }
                for run_uuid in run_uuids
            ]
        }
    except Exception:
        log_and_raise_error('access_raw_data')
    
def summarize_vector_data(request: Any, run_uuid: str) -> Dict[str, Any]:
    try:
        response = results(request, run_uuid)
        if response.status_code == 200:
            return sum_vectors(json.loads(response.content))
        return {"error": f"Failed to fetch data for run_uuid {run_uuid}"}
    except Exception:
        log_and_raise_error('summarize_vector_data')

def generate_data_dict(config: List[Dict[str, Any]], df_gen: Dict[str, Any]) -> Dict[str, List[Any]]:
    try:
        data_dict = defaultdict(list)
        for entry in config:
            val = entry["scenario_value"](df_gen)
            data_dict[entry["label"]].append(val)
        return data_dict
    except Exception:
        log_and_raise_error('generate_data_dict')

def generate_reopt_dataframe(data_f: Dict[str, Any], scenario_name: str, config: List[Dict[str, Any]]) -> pd.DataFrame:
    try:
        scenario_name_str = str(scenario_name)
        df_gen = flatten_dict(data_f)
        data_dict = generate_data_dict(config, df_gen)
        data_dict["Scenario"] = [scenario_name_str]
        col_order = ["Scenario"] + [entry["label"] for entry in config]
        return pd.DataFrame(data_dict)[col_order]
    except Exception:
        log_and_raise_error('generate_reopt_dataframe')

def get_bau_values(scenarios: List[Dict[str, Any]], config: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    try:
        bau_values_per_scenario = {
            scenario['run_uuid']: {entry["label"]: None for entry in config} for scenario in scenarios
        }

        for scenario in scenarios:
            run_uuid = scenario['run_uuid']
            df_gen = flatten_dict(scenario['full_data'])
            for entry in config:
                bau_func = entry.get("bau_value")
                # Try to apply the BAU function, and if it fails, set value to 0
                if bau_func:
                    try:
                        bau_values_per_scenario[run_uuid][entry["label"]] = bau_func(df_gen)
                    except Exception:
                        bau_values_per_scenario[run_uuid][entry["label"]] = 0
                else:
                    bau_values_per_scenario[run_uuid][entry["label"]] = 0 

        return bau_values_per_scenario
    except Exception:
        log_and_raise_error('get_bau_values')

def process_scenarios(scenarios: List[Dict[str, Any]], reopt_data_config: List[Dict[str, Any]]) -> pd.DataFrame:
    try:
        bau_values_per_scenario = get_bau_values(scenarios, reopt_data_config)
        combined_df = pd.DataFrame()

        for idx, scenario in enumerate(scenarios):
            run_uuid = scenario['run_uuid']
            df_result = generate_reopt_dataframe(scenario['full_data'], run_uuid, reopt_data_config)
            df_result["Scenario"] = run_uuid

            bau_data = {key: [value] for key, value in bau_values_per_scenario[run_uuid].items()}
            bau_data["Scenario"] = [f"BAU {idx + 1}"]
            df_bau = pd.DataFrame(bau_data)

            combined_df = pd.concat([combined_df, df_bau, df_result], axis=0) if not combined_df.empty else pd.concat([df_bau, df_result], axis=0)

        combined_df.reset_index(drop=True, inplace=True)
        combined_df = pd.DataFrame(clean_data_dict(combined_df.to_dict(orient="list")))
        return combined_df[["Scenario"] + [col for col in combined_df.columns if col != "Scenario"]]
    except Exception:
        log_and_raise_error('process_scenarios')

def generate_results_table(request: Any) -> HttpResponse:
    if request.method != 'GET':
        return JsonResponse({"Error": "Method not allowed. This endpoint only supports GET requests."}, status=405)

    try:
        table_config_name = request.GET.get('table_config_name', 'custom_table_webtool')
        run_uuids = [request.GET[key] for key in request.GET.keys() if key.startswith('run_uuid[')]
        if not run_uuids:
            return JsonResponse({"Error": "No run_uuids provided. Please include at least one run_uuid in the request."}, status=400)

        for r_uuid in run_uuids:
            try:
                uuid.UUID(r_uuid)
            except ValueError:
                return JsonResponse({"Error": f"Invalid UUID format: {r_uuid}. Ensure that each run_uuid is a valid UUID."}, status=400)

        target_custom_table = globals().get(table_config_name)
        if not target_custom_table:
            return JsonResponse({"Error": f"Invalid table configuration: {table_config_name}. Please provide a valid configuration name."}, status=400)

        scenarios = access_raw_data(run_uuids, request)
        final_df = process_scenarios(scenarios['scenarios'], target_custom_table)
        final_df_transpose = final_df.transpose()
        final_df_transpose.columns = final_df_transpose.iloc[0]
        final_df_transpose = final_df_transpose.drop(final_df_transpose.index[0])

        output = io.BytesIO()
        generate_excel_workbook(final_df_transpose, target_custom_table, output)
        output.seek(0)

        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="comparison_table.xlsx"'
        return response
    except CustomTableError as e:
        return JsonResponse({"Error": str(e)}, status=500)
    except Exception as e:
        log.error(f"Unexpected error in generate_results_table: {e}")
        return JsonResponse({"Error": "An unexpected error occurred. Please try again later."}, status=500)
    
def generate_excel_workbook(df: pd.DataFrame, custom_table: List[Dict[str, Any]], output: io.BytesIO) -> None:
    try:
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        # Add the 'Instructions' worksheet
        instructions_worksheet = workbook.add_worksheet('Instructions')
        
        # Add the 'Results Table' worksheet
        worksheet = workbook.add_worksheet('Results Table')

        # Scenario header formatting with colors
        scenario_colors = ['#0B5E90', '#00A4E4','#f46d43','#fdae61', '#66c2a5', '#d53e4f', '#3288bd']  
        
        scenario_formats = [workbook.add_format({'bold': True, 'bg_color': color, 'border': 1, 'align': 'center', 'font_color': 'white', 'font_size': 12}) for color in scenario_colors]

        # Row alternating colors
        row_colors = ['#d1d5d8', '#fafbfb']

        # Base formats for errors, percentages, and currency values
        error_format = workbook.add_format({'bg_color': '#FFC7CE', 'align': 'center', 'valign': 'center', 'border': 1, 'font_color': 'white', 'bold': True, 'font_size': 10})
        base_percent_format = {'num_format': '0%', 'align': 'center', 'valign': 'center', 'border': 1, 'font_size': 10}
        base_currency_format = {'num_format': '$#,##0', 'align': 'center', 'valign': 'center', 'border': 1, 'font_size': 10}

        # Formula formats using dark blue background
        formula_color = '#F8F8FF'
        formula_format = workbook.add_format({'num_format': '#,##0','bg_color': '#0B5E90', 'align': 'center', 'valign': 'center', 'border': 1, 'font_color': formula_color, 'font_size': 10, 'italic': True})
        formula_percent_format = workbook.add_format({'bg_color': '#0B5E90', 'num_format': '0%', 'align': 'center', 'valign': 'center', 'border': 1, 'font_color': formula_color, 'font_size': 10, 'italic': True})
        formula_currency_format = workbook.add_format({'bg_color': '#0B5E90', 'num_format': '$#,##0', 'align': 'center', 'valign': 'center', 'border': 1, 'font_color': formula_color, 'font_size': 10, 'italic': True})

        # Message format for formula cells (blue background with white text)
        formula_message_format = workbook.add_format({
            'bg_color': '#0B5E90',
            'font_color': '#F8F8FF',
            'align': 'center',
            'valign': 'center',
            'border': 1,
            'bold': True,
            'font_size': 12,
            'italic': True
        })

        # Message format for input cells (yellow background)
        input_message_format = workbook.add_format({
            'bg_color': '#FFFC79',
            'align': 'center',
            'valign': 'center',
            'border': 1,
            'bold': True,
            'font_size': 12
        })
        
        # Separator format for rows that act as visual dividers
        separator_format = workbook.add_format({'bg_color': '#5D6A71', 'bold': True, 'border': 1,'font_size': 11,'font_color': 'white'})
        
        input_cell_format = workbook.add_format({'bg_color': '#FFFC79', 'align': 'center', 'valign': 'center', 'border': 1, 'font_size': 10})

        # Combine row color with cell format, excluding formulas
        def get_combined_format(label, row_color, is_formula=False):
            if is_formula:
                if '$' in label:
                    return formula_currency_format
                elif '%' in label:
                    return formula_percent_format
                return formula_format
            base_data_format = {'num_format': '#,##0','bg_color': row_color, 'align': 'center', 'valign': 'center', 'border': 1, 'font_size': 10}
            if label:
                if '$' in label:
                    return workbook.add_format({**base_currency_format, 'bg_color': row_color})
                elif '%' in label:
                    return workbook.add_format({**base_percent_format, 'bg_color': row_color})
            return workbook.add_format(base_data_format)

        # Set column width for the first column (labels column)
        worksheet.set_column(0, 0, 45)

        # Setting column widths and writing headers for other columns
        column_width = 25
        columns_to_hide = set()

        # Loop through BAU columns and check if all numerical values are identical across all BAU columns
        bau_columns = [i for i, header in enumerate(df.columns) if "BAU" in header]

        # Only proceed if there are BAU columns
        if bau_columns:
            identical_bau_columns = True  # Assume all BAU columns are identical unless proven otherwise

            # Loop through each row and check the values across BAU columns
            for row_num in range(len(df)):
                row_values = df.iloc[row_num, bau_columns].values  # Get all BAU values for this row

                # Filter only numerical values for comparison
                numerical_values = [value for value in row_values if isinstance(value, (int, float))]

                # Check if all numerical BAU values in this row are the same
                if numerical_values:  # Proceed only if there are numerical values to compare
                    first_bau_value = numerical_values[0]
                    if not all(value == first_bau_value for value in numerical_values):
                        identical_bau_columns = False
                        break  # If any row has different BAU values, stop checking further

            # If all BAU columns are identical across all rows, hide all but the first BAU column
            if identical_bau_columns:
                for col_num in bau_columns[1:]:
                    columns_to_hide.add(col_num)

        # Now set the column properties for hiding BAU columns and leaving others unchanged
        for col_num, header in enumerate(df.columns):
            if "BAU" in header and col_num in columns_to_hide:
                # Hide the BAU columns that have been marked
                worksheet.set_column(col_num + 1, col_num + 1, column_width, None, {'hidden': True})
            else:
                # Set the normal column width for non-hidden columns
                worksheet.set_column(col_num + 1, col_num + 1, column_width)

        # Write scenario headers
        worksheet.write('A1', 'Scenario', scenario_formats[0])
        for col_num, header in enumerate(df.columns):
            worksheet.write(0, col_num + 1, header, scenario_formats[(col_num // 2) % (len(scenario_formats) - 1) + 1])

        # Write variable names and data with full-row formatting
        row_offset = 0  # To keep track of the current row in the worksheet
        for row_num, entry in enumerate(custom_table):
            key = entry['key']  # Extract the key from custom_table

            # Check if the key contains 'separator'
            if 'separator' in key.lower():
                # Merge the first few columns for the separator
                worksheet.merge_range(row_num + 1 + row_offset, 0, row_num + 1 + row_offset, len(df.columns), entry['label'], separator_format)
            else:
                # Regular row data writing
                row_color = row_colors[(row_num + row_offset) % 2]  # Alternating row colors
                
                # Write the label in the first column
                worksheet.write(row_num + 1 + row_offset, 0, entry['label'], workbook.add_format({'bg_color': row_color, 'border': 1}))

                # Write the data for each column
                variable = entry['label']  # Assuming df index or columns match the label
                for col_num, value in enumerate(df.loc[variable]):
                    is_formula = False  # Detect if this cell contains a formula
                    if isinstance(value, str) and "formula" in value.lower():
                        is_formula = True
                    # Check if the key contains 'input' to apply the input format
                    if 'input' in key.lower():
                        cell_format = input_cell_format
                    else:
                        cell_format = get_combined_format(variable, row_color, is_formula)
                    # cell_format = get_combined_format(variable, row_color, is_formula)
                    if pd.isnull(value) or value == '-':
                        worksheet.write(row_num + 1 + row_offset, col_num + 1, "", cell_format)
                    else:
                        worksheet.write(row_num + 1 + row_offset, col_num + 1, value, cell_format)

        # Update the messages
        formula_message_text = "Values with white text on blue background are formulas; please do not edit these cells."
        input_message_text = "Yellow cells are inputs; you can modify these to explore consideration of additional Incentives or Costs, outside of REopt."

        # Determine the placement of the messages
        last_row = len(df.index) + 2  # Adjust the row index for message placement

        # Place the first message about formulas
        worksheet.merge_range(
            last_row, 0,
            last_row, len(df.columns),
            formula_message_text, formula_message_format
        )
        last_row += 1  # Move to the next row for the second message

        # Place the second message about inputs
        worksheet.merge_range(
            last_row, 0,
            last_row, len(df.columns),
            input_message_text, input_message_format
        )

        headers = {header: idx for idx, header in enumerate(df.index)}
        headers["Scenario"] = 0

        def get_bau_column(col):
            return col - 1 if col > 1 else 1

        relevant_columns = [entry["label"] for entry in custom_table]
        relevant_calculations = [calc for calc in calculations_config if calc["name"] in relevant_columns]

        logged_messages = set()
        missing_entries = []

        for col in range(2, len(df.columns) + 2):
            # Skip BAU columns (BAU columns should not have formulas)
            if col % 2 == 0:
                continue  # Skip the BAU column

            col_letter = colnum_string(col)
            bau_col = get_bau_column(col)  # Get the corresponding BAU column
            bau_col_letter = colnum_string(bau_col)  # Convert the column number to letter for Excel reference

            bau_cells = {cell_name: f'{bau_col_letter}{headers[header] + 2}' for cell_name, header in bau_cells_config.items() if header in headers}

            for calc in relevant_calculations:
                try:
                    if all(key in headers or key in bau_cells for key in calc["formula"].__code__.co_names):
                        row_idx = headers.get(calc["name"])
                        if row_idx is not None:
                            formula = calc["formula"](col_letter, bau_cells, headers)
                            cell_format = get_combined_format(calc["name"], row_colors[row_idx % 2], is_formula=True)
                            worksheet.write_formula(row_idx + 1, col - 1, formula, cell_format)
                        else:
                            missing_entries.append(calc["name"])
                    else:
                        missing_keys = [key for key in calc["formula"].__code__.co_names if key not in headers and key not in bau_cells]
                        if missing_keys:
                            row_idx = headers.get(calc["name"])
                            if row_idx is not None:
                                worksheet.write(row_idx + 1, col - 1, "MISSING REFERENCE IN FORMULA", error_format)
                            message = f"Cannot calculate '{calc['name']}' because the required fields are missing: {', '.join(missing_keys)} in the Table configuration provided. Update the Table to include {missing_keys}."
                            if message not in logged_messages:
                                logged_messages.add(message)
                            missing_entries.append(calc["name"])
                except KeyError as e:
                    missing_field = str(e)
                    message = f"Cannot calculate '{calc['name']}' because the field '{missing_field}' is missing in the Table configuration provided. Update the Table to include {missing_field}."
                    if message not in logged_messages:
                        logged_messages.add(message)
                    row_idx = headers.get(calc["name"])
                    if row_idx is not None:
                        worksheet.write(row_idx + 1, col - 1, "MISSING REFERENCE IN FORMULA", error_format)
                    missing_entries.append(calc["name"])

        if missing_entries:
            print(f"missing_entries in the input table: {', '.join(set(missing_entries))}. Please update the configuration if necessary.")

        # Formats for the instructions sheet
        title_format = workbook.add_format({
            'bold': True, 'font_size': 18, 'align': 'left', 'valign': 'top'
        })
        subtitle_format = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'left', 'valign': 'top'
        })
        text_format = workbook.add_format({
            'font_size': 12, 'align': 'left', 'valign': 'top', 'text_wrap': True
        })
        bullet_format = workbook.add_format({
            'font_size': 12, 'align': 'left', 'valign': 'top', 'text_wrap': True, 'indent': 1
        })

        # Set column width and default row height
        instructions_worksheet.set_column(0, 0, 100)
        instructions_worksheet.set_default_row(15)

        # Start writing instructions
        row = 0
        instructions_worksheet.write(row, 0, "Instructions for Using the REopt Results Table Workbook", title_format)
        row += 2

        # General Introduction
        general_instructions = (
            "Welcome to the REopt Results Table Workbook !\n\n"
            "This workbook contains all of the results of your selected REopt analysis scenarios. "
            "Please read the following instructions carefully to understand how to use this workbook effectively."
        )
        instructions_worksheet.write(row, 0, general_instructions, text_format)
        row += 4

        # Using the 'Results Table' Sheet with formula format
        instructions_worksheet.write(row, 0, "Using the 'Results Table' Sheet", subtitle_format)
        row += 1

        custom_table_instructions = (
            "The 'Results Table' sheet displays the scenario results of your REopt analysis in a structured format. "
            "Here's how to use it:"
        )
        instructions_worksheet.write(row, 0, custom_table_instructions, text_format)
        row += 2

        steps = [
            "1. Review the Results: Browse through the table to understand the system capacities, financial metrics, and energy production details.",
            "2. Identify Editable Fields: Look for yellow cells in the 'Playground' section where you can input additional incentives or costs.",
            "3. Avoid Editing Formulas: Do not edit cells with blue background and white text, as they contain important formulas.",
            "4. Interpreting BAU and Optimal Scenarios: 'BAU' stands for 'Business as Usual' and represents the baseline scenario without any new investments. 'Optimal' scenarios show the results with optimized investments.",
            "5. Hidden BAU Columns: If all scenarios are for a single site, identical BAU columns may be hidden except for the first one. For multiple sites where financials and energy consumption differ, all BAU columns will be visible."
        ]
        for step in steps:
            instructions_worksheet.write(row, 0, step, bullet_format)
            row += 1
        row += 2

        # Notes for the Playground Section
        instructions_worksheet.write(row, 0, "Notes for the Playground Section", subtitle_format)
        row += 1

        playground_notes = (
            "The 'Playground' section allows you to explore the effects of additional incentives or costs on your project's financial metrics."
        )
        instructions_worksheet.write(row, 0, playground_notes, text_format)
        row += 2

        playground_items = [
            "- Net Upfront Capital Cost After Incentives but without MACRS ($): Represents the upfront cost after incentives, excluding MACRS depreciation benefits.",
            "- Net Upfront Capital Cost After Incentives with MACRS ($): Includes MACRS depreciation, which provides tax benefits over the first 5-7 years.",
            "- Additional Upfront Incentive ($): Input any additional grants or incentives (e.g., IAC grant, state or local grants).",
            "- Additional Upfront Cost ($): Input any extra upfront costs (e.g., interconnection upgrades, microgrid components).",
            "- Additional Yearly Cost Savings ($/year): Input any ongoing yearly savings (e.g., improved productivity, product sales with ESG designation).",
            "- Additional Yearly Cost ($/year): Input any additional yearly costs (e.g., microgrid operation and maintenance).",
            "- Modified Net Upfront Capital Cost ($): This value recalculates based on your inputs.",
            "- Modified Simple Payback Period (years): Recalculates the payback period based on your inputs, providing a more conventional 'simple' payback period."
        ]
        for item in playground_items:
            instructions_worksheet.write(row, 0, item, bullet_format)
            row += 1
        row += 2

        # Unaddressable Heating Load and Emissions
        instructions_worksheet.write(row, 0, "Unaddressable Heating Load and Emissions", subtitle_format)
        row += 1

        unaddressable_notes = (
            "In scenarios where there is an unaddressable heating load (heating demand that cannot be served by the technologies analyzed), "
            "the associated fuel consumption and emissions are not accounted for in the standard REopt outputs.\n\n"
            "The 'Unaddressable CO₂ Emissions' row in the 'Playground' section includes these emissions, providing a more comprehensive view of your site's total emissions. "
            "Including unaddressable emissions results in a lower percentage reduction because the total emissions baseline is larger."
        )
        instructions_worksheet.write(row, 0, unaddressable_notes, text_format)
        row += 2

        # Final Note and Contact Info
        instructions_worksheet.write(row, 0, "Thank you for using the REopt Results Table Workbook!", text_format)
        row += 1
        contact_info = "For support or feedback, please contact the REopt team at reopt@nrel.gov."
        instructions_worksheet.write(row, 0, contact_info, text_format)

        # Freeze panes to keep the title visible
        instructions_worksheet.freeze_panes(1, 0)

        # Close the workbook after all sheets are written
        workbook.close()
        
    except Exception:
        log_and_raise_error('generate_excel_workbook')

##############################################################################################################################
################################################### END Results Table #########################################################
##############################################################################################################################