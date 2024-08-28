# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
from django.db import models
import uuid
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
    SteamTurbineOutputs, GHPInputs, GHPOutputs, ProcessHeatLoadInputs
import os
import requests
import numpy as np
import pandas as pd
import json
import logging
from reoptjl.custom_table_helpers import safe_get,flatten_dict, clean_data_dict, sum_vectors, colnum_string, check_bau_consistency
import xlsxwriter
from collections import defaultdict
import io

log = logging.getLogger(__name__)

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


def simulated_load(request):
    try:
        valid_keys = ["doe_reference_name","latitude","longitude","load_type","percent_share","annual_kwh",
                        "monthly_totals_kwh","annual_mmbtu","annual_fraction","annual_tonhour","monthly_tonhour",
                        "monthly_mmbtu","monthly_fraction","max_thermal_factor_on_peak_load","chiller_cop",
                        "addressable_load_fraction", "cooling_doe_ref_name", "cooling_pct_share", "boiler_efficiency"]
        for key in request.GET.keys():
            k = key
            if "[" in key:
                k = key.split('[')[0]
            if k not in valid_keys:
                raise ValueError("{} is not a valid input parameter".format(key))
        # Build inputs dictionary to send to http.jl /simulated_load endpoint
        inputs = {}
        # Required - will throw a Missing Error if not included
        inputs["latitude"] = float(request.GET['latitude'])  # need float to convert unicode
        inputs["longitude"] = float(request.GET['longitude'])
        # Optional load_type - will default to "electric"
        inputs["load_type"] = request.GET.get('load_type')

        # This parses the GET request way of sending a list/array for doe_reference_name, 
        # i.e. doe_reference_name[0], doe_reference_name[1], etc along with percent_share[0], percent_share[1]
        if 'doe_reference_name' in request.GET.keys():
            inputs["doe_reference_name"] = str(request.GET.get('doe_reference_name'))
        elif 'doe_reference_name[0]' in request.GET.keys():
            idx = 0
            doe_reference_name = []
            percent_share_list = []
            while 'doe_reference_name[{}]'.format(idx) in request.GET.keys():
                doe_reference_name.append(str(request.GET['doe_reference_name[{}]'.format(idx)]))
                if 'percent_share[{}]'.format(idx) in request.GET.keys():
                    percent_share_list.append(float(request.GET['percent_share[{}]'.format(idx)]))
                idx += 1
            inputs["doe_reference_name"] = doe_reference_name
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

        # Create Querysets: Select all objects associate with a user_uuid, Order by `created` column
        scenarios = APIMeta.objects.filter(user_uuid=user_uuid).only(
            'run_uuid',
            'status',
            'created'
        ).order_by("-created")

        unlinked_run_uuids = [i.run_uuid for i in UserUnlinkedRuns.objects.filter(user_uuid=user_uuid)]
        api_metas = [s for s in scenarios if s.run_uuid not in unlinked_run_uuids]

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

# Query all django models for all run_uuids found for given user_uuid
def queryset_for_summary(api_metas,summary_dict:dict):

    # Loop over all the APIMetas associated with a user_uuid, do something if needed
    for m in api_metas:
        # print(3, meta.run_uuid) #acces Meta fields like this
        summary_dict[str(m.run_uuid)] = dict()
        summary_dict[str(m.run_uuid)]['status'] = m.status
        summary_dict[str(m.run_uuid)]['run_uuid'] = str(m.run_uuid)
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
        'outage_start_time_steps'
    )
    if len(utility) > 0:
        for m in utility:
            if len(m.outage_start_time_steps) == 0:
                summary_dict[str(m.meta.run_uuid)]['focus'] = "Financial"
            else:
                summary_dict[str(m.meta.run_uuid)]['focus'] = "Resilience"

    # Use settings to find out if it is an off-grid evaluation
    settings = Settings.objects.filter(meta__run_uuid__in=run_uuids).only(
        'meta__run_uuid',
        'off_grid_flag'
    )
    if len(settings) > 0:
        for m in settings:
            if m.off_grid_flag:
                summary_dict[str(m.meta.run_uuid)]['focus'] = "Off-grid"

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
        'initial_capital_costs_after_incentives'
    )
    if len(fin) > 0:
        for m in fin:
            if m.npv is not None:
                summary_dict[str(m.meta.run_uuid)]['npv_us_dollars'] = m.npv
            else:
                summary_dict[str(m.meta.run_uuid)]['npv_us_dollars'] = None
            summary_dict[str(m.meta.run_uuid)]['net_capital_costs'] = m.initial_capital_costs_after_incentives
    
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
    
    return summary_dict

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
        
        # Create Querysets: Select all objects associate with a user_uuid, Order by `created` column
        scenarios = APIMeta.objects.filter(user_uuid=user_uuid).only(
            'run_uuid',
            'status',
            'created'
        ).order_by("-created")

        unlinked_run_uuids = [i.run_uuid for i in UserUnlinkedRuns.objects.filter(user_uuid=user_uuid)]
        api_metas = [s for s in scenarios if s.run_uuid not in unlinked_run_uuids]
        
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


# Unlink a user_uuid from a run_uuid.
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

###############################################################
################ START Custom Table ###########################
###############################################################

def access_raw_data(run_uuids, request):
    try:
        # Fetch UserProvidedMeta data for the relevant run_uuids
        usermeta = UserProvidedMeta.objects.filter(meta__run_uuid__in=run_uuids).only(
            'meta__run_uuid', 'description', 'address'
        )

        # Create a dictionary to map run_uuids to their associated meta data
        meta_data_dict = {um.meta.run_uuid: {"description": um.description, "address": um.address} for um in usermeta}

        full_summary_dict = {
            "scenarios": [
                {
                    "run_uuid": str(run_uuid),
                    "full_data": process_raw_data(request, run_uuid),
                    "meta_data": meta_data_dict.get(run_uuid, {})
                }
                for run_uuid in run_uuids
            ]
        }

        # Perform the BAU consistency check
        check_bau_consistency(full_summary_dict['scenarios'])

        return full_summary_dict

    except ValueError as e:
        log.error(f"ValueError in access_raw_data: {e}")
        raise
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        log.error(f"Error in access_raw_data: {exc_value}, traceback: {tb.format_tb(exc_traceback)}")
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='access_raw_data')
        err.save_to_db()
        raise
    
def process_raw_data(request, run_uuid):
    try:
        response = results(request, run_uuid)
        if response.status_code == 200:
            return sum_vectors(json.loads(response.content))
        return {"error": f"Failed to fetch data for run_uuid {run_uuid}"}
    except Exception:
        err = UnexpectedError(*sys.exc_info(), task='create_custom_comparison_table')
        err.save_to_db()
        raise

def generate_data_dict(config, df_gen, suffix=""):
    try:
        data_dict = defaultdict(list)
        for entry in config:
            val = entry["scenario_value"](df_gen)
            data_dict[entry["label"]].append(val)
        log.debug(f"Generated data_dict: {data_dict}")
        return data_dict
    except Exception:
        log.error(f"Error in generate_data_dict: {tb.format_exc()}")
        raise

def get_REopt_data(data_f, scenario_name, config):
    try:
        scenario_name_str = str(scenario_name)
        suffix = "_bau" if "BAU" in scenario_name_str.upper() else ""

        df_gen = flatten_dict(data_f)
        log.debug(f"Flattened data_f in get_REopt_data: {df_gen}")
        data_dict = generate_data_dict(config, df_gen, suffix)
        data_dict["Scenario"] = [scenario_name_str]

        col_order = ["Scenario"] + [entry["label"] for entry in config]
        df_res = pd.DataFrame(data_dict)[col_order]

        log.debug(f"Generated DataFrame in get_REopt_data: {df_res}")
        return df_res
    except Exception:
        log.error(f"Error in get_REopt_data: {tb.format_exc()}")
        raise

def get_bau_values(scenarios, config):
    try:
        bau_values = {entry["label"]: None for entry in config}
        log.debug(f"Initialized BAU values: {bau_values}")

        # Extract BAU values from the first scenario
        df_gen = flatten_dict(scenarios[0]['full_data'])
        log.debug(f"Flattened data for scenario {scenarios[0]['run_uuid']}: {df_gen}")

        for entry in config:
            bau_func = entry.get("bau_value")
            value = bau_func(df_gen) if bau_func else df_gen.get(f"{entry['key']}_bau")
            bau_values[entry["label"]] = value

        log.debug(f"Final consolidated BAU values: {bau_values}")
        return bau_values

    except Exception:
        log.error(f"Error in get_bau_values: {tb.format_exc()}")
        raise

def process_scenarios(scenarios, reopt_data_config):
    try:
        log.debug(f"Starting process_scenarios with config: {reopt_data_config}")
        bau_values = get_bau_values(scenarios, reopt_data_config)
        log.debug(f"BAU values: {bau_values}")
        combined_df = pd.DataFrame()

        for scenario in scenarios:
            run_uuid = scenario['run_uuid']
            df_result = get_REopt_data(scenario['full_data'], run_uuid, reopt_data_config)
            df_result = df_result.set_index('Scenario').T
            df_result.columns = [run_uuid]
            combined_df = df_result if combined_df.empty else combined_df.join(df_result, how='outer')

        # Adding BAU data as the first row in the DataFrame
        bau_data = {key: [value] for key, value in bau_values.items()}
        bau_data["Scenario"] = ["BAU"]
        df_bau = pd.DataFrame(bau_data)

        # Combine BAU data with scenario results
        combined_df = pd.concat([df_bau, combined_df.T]).reset_index(drop=True)
        log.debug(f"Final DataFrame before clean_data_dict:\n{combined_df}")

        combined_df = clean_data_dict(combined_df.to_dict(orient="list"))
        combined_df = pd.DataFrame(combined_df)
        combined_df = combined_df[["Scenario"] + [col for col in combined_df.columns if col != "Scenario"]]

        log.debug(f"Final DataFrame in process_scenarios:\n{combined_df}")
        return combined_df
    except Exception:
        log.error(f"Error in process_scenarios: {tb.format_exc()}")
        raise

def create_custom_comparison_table(request):
    """
    Create a custom comparison table based on user-provided run UUIDs.
    """
    try:
        if request.method == 'GET':
            log.debug(f"GET parameters: {request.GET}")

            table_config_name = request.GET.get('table_config_name', 'single_site_custom_table')
            log.debug(f"Using table configuration: {table_config_name}")

            run_uuids = [request.GET[key] for key in request.GET.keys() if key.startswith('run_uuid[')]
            log.debug(f"Handling GET request with run_uuids: {run_uuids}")

            if not run_uuids:
                return JsonResponse({"Error": "No run_uuids provided. Please include at least one run_uuid in the request."}, status=400)

            for r_uuid in run_uuids:
                try:
                    uuid.UUID(r_uuid)
                except ValueError as e:
                    if e.args[0] == "badly formed hexadecimal UUID string":
                        resp = {"Error": f"Invalid UUID format: {r_uuid}. Ensure that each run_uuid is a valid UUID."}
                        return JsonResponse(resp, status=400)
                    else:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        err = UnexpectedError(exc_type, exc_value.args[0], tb.format_tb(exc_traceback), task='create_custom_comparison_table', run_uuid=r_uuid)
                        err.save_to_db()
                        return JsonResponse({"Error": str(err.args[0])}, status=400)

            if table_config_name in globals():
                target_custom_table = globals()[table_config_name]
            else:
                return JsonResponse({"Error": f"Invalid table configuration: {table_config_name}. Please provide a valid configuration name."}, status=400)

            scenarios = access_raw_data(run_uuids, request)
            if 'scenarios' not in scenarios or not scenarios['scenarios']:
                response = JsonResponse({'Error': 'Failed to fetch scenarios. The provided run_uuids might be incorrect or not associated with any data.'}, content_type='application/json', status=404)
                return response

            final_df = process_scenarios(scenarios['scenarios'], target_custom_table)
            log.debug(f"Final DataFrame (before transpose):\n{final_df}")

            final_df.iloc[1:, 0] = run_uuids

            final_df_transpose = final_df.transpose()
            final_df_transpose.columns = final_df_transpose.iloc[0]
            final_df_transpose = final_df_transpose.drop(final_df_transpose.index[0])

            output = io.BytesIO()
            create_custom_table_excel(final_df_transpose, target_custom_table, calculations, output)
            output.seek(0)

            filename = "comparison_table.xlsx"
            response = HttpResponse(
                output,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename={filename}'

            return response

        else:
            return JsonResponse({"Error": "Method not allowed. This endpoint only supports GET requests."}, status=405)

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value.args[0], tb.format_tb(exc_traceback), task='create_custom_comparison_table')
        err.save_to_db()
        resp = {"Error": err.message}
        return JsonResponse(resp, status=500)

def create_custom_table_excel(df, custom_table, calculations, output):
    try:
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Custom Table')

        # Formats for general data, percentages, and currency values
        # General formatting
        data_format = workbook.add_format({
            'align'    : 'center',
            'valign'   : 'center',
            'border'   : 1,
            'font_size': 10
        })

        # Formatting for formulas
        formula_format = workbook.add_format({
            'bg_color'  : '#FFE599', # Light yellow background
            'align'     : 'center',
            'valign'    : 'center',
            'border'    : 1,
            'font_color': 'red',
            'font_size' : 10,
            'italic'    : True  # Italic to highlight it's a formula
        })

        # Formatting for errors
        error_format = workbook.add_format({
            'bg_color'  : '#FFC7CE', # Light red background
            'align'     : 'center',
            'valign'    : 'center',
            'border'    : 1,
            'font_color': 'black',
            'font_size' : 10
        })

        # Formatting for percentages, showing as whole numbers (e.g., 9%)
        percent_format = workbook.add_format({
            'num_format': '0%',     # Whole number percentage (e.g., 9%)
            'align'     : 'center',
            'valign'    : 'center',
            'border'    : 1,
            'font_size' : 10
        })

        # Formatting for currency values with two decimal places
        currency_format = workbook.add_format({
            'num_format': '$#,##0.00', # Currency with two decimal places
            'align'     : 'center',
            'valign'    : 'center',
            'border'    : 1,
            'font_size' : 10
        })

        # Formatting for formulas that are percentages
        formula_percent_format = workbook.add_format({
            'bg_color'  : '#FFE599', # Light yellow background
            'num_format': '0%',      # Whole number percentage
            'align'     : 'center',
            'valign'    : 'center',
            'border'    : 1,
            'font_color': 'red',
            'font_size' : 10,
            'italic'    : True
        })

        # Formatting for formulas that are currency values
        formula_currency_format = workbook.add_format({
            'bg_color'  : '#FFE599',   # Light yellow background
            'num_format': '$#,##0.00', # Currency with two decimal places
            'align'     : 'center',
            'valign'    : 'center',
            'border'    : 1,
            'font_color': 'red',
            'font_size' : 10,
            'italic'    : True
        })

        # Header format for the scenario column
        scenario_header_format = workbook.add_format({
            'bold'      : True,
            'bg_color'  : '#0079C2', # Dark blue background
            'border'    : 1,
            'align'     : 'center',
            'font_color': 'white',
            'font_size' : 10
        })

        # Format for the variable names in the first column
        variable_name_format = workbook.add_format({
            'bold'     : True,
            'bg_color' : '#DEE2E5', # Light gray background
            'border'   : 1,
            'align'    : 'left',
            'font_size': 10
        })
        
        worksheet.write(1, len(df.columns) + 2, "Values in red are formulas. Do not input anything.", formula_format)

        column_width = 35
        for col_num in range(len(df.columns) + 3):
            worksheet.set_column(col_num, col_num, column_width)

        worksheet.write('A1', 'Scenario', scenario_header_format)
        for col_num, header in enumerate(df.columns):
            worksheet.write(0, col_num + 1, header, scenario_header_format)

        for row_num, variable in enumerate(df.index):
            worksheet.write(row_num + 1, 0, variable, variable_name_format)

        # Use the custom table to determine format
        def get_format(label):
            entry = next((item for item in custom_table if item["label"] == label), None)
            if entry:
                if '$' in entry["label"]:
                    return currency_format, formula_currency_format
                elif '%' in entry["label"]:
                    return percent_format, formula_percent_format
            return data_format, formula_format

        # Writing data to cells with the appropriate format
        for row_num, variable in enumerate(df.index):
            cell_format, cell_formula_format = get_format(variable)
            for col_num, value in enumerate(df.loc[variable]):
                if pd.isnull(value) or value == '-':
                    worksheet.write(row_num + 1, col_num + 1, "", data_format)
                else:
                    worksheet.write(row_num + 1, col_num + 1, value, cell_format)

        headers = {header: idx for idx, header in enumerate(df.index)}

        bau_cells = {
            'grid_value': f'{colnum_string(2)}{headers["Grid Purchased Electricity (kWh)"] + 2}' if "Grid Purchased Electricity (kWh)" in headers else None,
            'net_cost_value': f'{colnum_string(2)}{headers["Net Electricity Cost ($)"] + 2}' if "Net Electricity Cost ($)" in headers else None,
            'ng_reduction_value': f'{colnum_string(2)}{headers["Total Fuel (MMBtu)"] + 2}' if "Total Fuel (MMBtu)" in headers else None,
            'util_cost_value': f'{colnum_string(2)}{headers["Total Utility Cost ($)"] + 2}' if "Total Utility Cost ($)" in headers else None,
            'co2_reduction_value': f'{colnum_string(2)}{headers["CO2 Emissions (tonnes)"] + 2}' if "CO2 Emissions (tonnes)" in headers else None,
            # New placeholders added based on Example 6 and 7 calculations
            'placeholder1_value': f'{colnum_string(2)}{headers["Placeholder1"] + 2}' if "Placeholder1" in headers else None,
    }

        relevant_columns = [entry["label"] for entry in custom_table]
        relevant_calculations = [calc for calc in calculations if calc["name"] in relevant_columns]

        logged_messages = set()
        missing_entries = []

        for col in range(2, len(df.columns) + 2):
            col_letter = colnum_string(col)
            for calc in relevant_calculations:
                try:
                    if all(key in headers or key in bau_cells for key in calc["formula"].__code__.co_names):
                        row_idx = headers.get(calc["name"])
                        if row_idx is not None:
                            formula = calc["formula"](col_letter, bau_cells, headers)
                            cell_format, cell_formula_format = get_format(calc["name"])
                            worksheet.write_formula(row_idx + 1, col-1, formula, cell_formula_format)
                        else:
                            missing_entries.append(calc["name"])
                    else:
                        missing_keys = [key for key in calc["formula"].__code__.co_names if key not in headers and key not in bau_cells]
                        if missing_keys:
                            row_idx = headers.get(calc["name"])
                            if row_idx is not None:
                                worksheet.write(row_idx + 1, col - 1, "MISSING DATA", error_format)
                            message = f"Cannot calculate '{calc['name']}' because the required fields are missing: {', '.join(missing_keys)} in the Table configuration provided. Update the Table to include {missing_keys}. Writing 'MISSING DATA' instead."
                            if message not in logged_messages:
                                print(message)
                                logged_messages.add(message)
                            missing_entries.append(calc["name"])
                except KeyError as e:
                    missing_field = str(e)
                    message = f"Cannot calculate '{calc['name']}' because the field '{missing_field}' is missing in the Table configuration provided. Update the Table to include {missing_field}. Writing 'MISSING DATA' instead."
                    if message not in logged_messages:
                        print(message)
                        logged_messages.add(message)
                    row_idx = headers.get(calc["name"])
                    if row_idx is not None:
                        worksheet.write(row_idx + 1, col - 1, "MISSING DATA", error_format)
                    missing_entries.append(calc["name"])

        if missing_entries:
            print(f"Missing entries in the input table: {', '.join(set(missing_entries))}. Please update the configuration if necessary.")

        workbook.close()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='create_custom_comparison_table')
        err.save_to_db()
        raise

# Configuration
# Set up table needed along with REopt dictionaries to grab data 

# Example Custom Table Configuration
example_table = [
    # Example 1: Basic Key Retrieval with Data Values
    {
        "label": "Site Name",
        "key": "site",
        "bau_value": lambda df: safe_get(df, "inputs.Meta.description", "None provided"),
        "scenario_value": lambda df: safe_get(df, "inputs.Meta.description", "None provided")
    },
    {
        "label": "Site Location",
        "key": "site_lat_long",
        "bau_value": lambda df: f"({safe_get(df, 'inputs.Site.latitude')}, {safe_get(df, 'inputs.Site.longitude')})",
        "scenario_value": lambda df: f"({safe_get(df, 'inputs.Site.latitude')}, {safe_get(df, 'inputs.Site.longitude')})"
    },
    # Example 2: Concatenating Strings
    {
        "label": "Site Address",
        "key": "site_address",
        "bau_value": lambda df: safe_get(df, "inputs.Meta.address", "None provided"),
        "scenario_value": lambda df: safe_get(df, "inputs.Meta.address", "None provided")
    },

    # Example 3: Calculated Value (Sum of Two Fields), this does not show up in formulas
    {
        "label": "Combined Renewable Size (kW)",
        "key": "combined_renewable_size",
        "bau_value": lambda df: 0,
        "scenario_value": lambda df: safe_get(df, "outputs.PV.size_kw") + safe_get(df, "outputs.Wind.size_kw")     #NOTE: These calculations will not show up as in the excel calculations
    },

    # Example 4: Hardcoded Values
    {
        "label": "Hardcoded Values (kWh)",
        "key": "hardcoded_value",
        "bau_value": lambda df: 500,  # BAU scenario
        "scenario_value": lambda df: 1000  # Regular scenarios
    },

    # Example 5: Conditional Formatting
    {
        "label": "PV Size Status",
        "key": "pv_size_status",
        "bau_value": lambda df: 0,
        "scenario_value": lambda df: "Above Threshold" if safe_get(df, "outputs.PV.size_kw") > 2500 else "Below Threshold"
    },
    #Example 6 and 7: First define any data that might need to be referenced, Here I've defined two placeholders
    # Define Placeholder1
    {
        "label": "Placeholder1",
        "key": "placeholder1",
        "bau_value": lambda df: 100,  # BAU value
        "scenario_value": lambda df: 200  # Scenario value
    },
    # Define Placeholder2
    {
        "label": "Placeholder2",
        "key": "placeholder2",
        "bau_value": lambda df: 50,  # BAU value
        "scenario_value": lambda df: 100  # Scenario value
    },
    # Example 6: Calculation Without Reference to BAU
    {
        "label": "Placeholder Calculation Without BAU Reference",
        "key": "placeholder_calculation_without_bau",
        "bau_value": lambda df: 0,  # Placeholder, replaced by formula in Excel
        "scenario_value": lambda df: 0  # Placeholder, replaced by formula in Excel
    },
    # Example 7: Calculation With Reference to BAU
    {
        "label": "Placeholder Calculation With BAU Reference",
        "key": "placeholder_calculation_with_bau",
        "bau_value": lambda df: 0,  # Placeholder, replaced by formula in Excel
        "scenario_value": lambda df: 0  # Placeholder, replaced by formula in Excel
    }]

# TASC/Single Site Configuration
single_site_custom_table = [
    {
        "label": "Site Name",
        "key": "site",
        "bau_value": lambda df: "",
        "scenario_value": lambda df: safe_get(df, "inputs.Meta.description", "None provided")
    },
    {
        "label": "Site Location",
        "key": "site_lat_long",
        "bau_value": lambda df: f"({safe_get(df, 'inputs.Site.latitude')}, {safe_get(df, 'inputs.Site.longitude')})",
        "scenario_value": lambda df: f"({safe_get(df, 'inputs.Site.latitude')}, {safe_get(df, 'inputs.Site.longitude')})"
    },
    {
        "label": "Site Address",
        "key": "site_address",
        "bau_value": lambda df: safe_get(df, "inputs.Meta.address", "None provided"),
        "scenario_value": lambda df: safe_get(df, "inputs.Meta.address", "None provided")
    },
    {
        "label": "PV Size (kW)",
        "key": "pv_size",
        "bau_value": lambda df: safe_get(df, "outputs.PV.size_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.PV.size_kw")
    },
    {
        "label": "Wind Size (kW)",
        "key": "wind_size",
        "bau_value": lambda df: safe_get(df, "outputs.Wind.size_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Wind.size_kw")
    },
    {
        "label": "CHP Size (kW)",
        "key": "chp_size",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.size_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.size_kw")
    },
    {
        "label": "PV Total Electricity Produced (kWh)",
        "key": "pv_total_electricity_produced",
        "bau_value": lambda df: safe_get(df, "outputs.PV.annual_energy_produced_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.PV.annual_energy_produced_kwh")
    },
    {
        "label": "PV Exported to Grid (kWh)",
        "key": "pv_exported_to_grid",
        "bau_value": lambda df: safe_get(df, "outputs.PV.electric_to_grid_series_kw"),
        "scenario_value": lambda df: safe_get(df, "outputs.PV.electric_to_grid_series_kw")
    },
    {
        "label": "PV Serving Load (kWh)",
        "key": "pv_serving_load",
        "bau_value": lambda df: safe_get(df, "outputs.PV.electric_to_load_series_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.PV.electric_to_load_series_kw")
    },
    {
        "label": "Wind Total Electricity Produced (kWh)",
        "key": "wind_total_electricity_produced",
        "bau_value": lambda df: safe_get(df, "outputs.Wind.annual_energy_produced_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Wind.annual_energy_produced_kwh")
    },
    {
        "label": "Wind Exported to Grid (kWh)",
        "key": "wind_exported_to_grid",
        "bau_value": lambda df: safe_get(df, "outputs.Wind.electric_to_grid_series_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Wind.electric_to_grid_series_kw")
    },
    {
        "label": "Wind Serving Load (kWh)",
        "key": "wind_serving_load",
        "bau_value": lambda df: safe_get(df, "outputs.Wind.electric_to_load_series_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Wind.electric_to_load_series_kw")
    },
    {
        "label": "CHP Total Electricity Produced (kWh)",
        "key": "chp_total_electricity_produced",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.annual_electric_production_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.annual_electric_production_kwh")
    },
    {
        "label": "CHP Exported to Grid (kWh)",
        "key": "chp_exported_to_grid",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.electric_to_grid_series_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.electric_to_grid_series_kw")
    },
    {
        "label": "CHP Serving Load (kWh)",
        "key": "chp_serving_load",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.electric_to_load_series_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.electric_to_load_series_kw")
    },
    {
        "label": "CHP Serving Thermal Load (MMBtu)",
        "key": "chp_serving_thermal_load",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.thermal_to_load_series_mmbtu_per_hour_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.thermal_to_load_series_mmbtu_per_hour")
    },
    {
        "label": "Grid Purchased Electricity (kWh)",
        "key": "grid_purchased_electricity",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricUtility.annual_energy_supplied_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricUtility.annual_energy_supplied_kwh")
    },
    {
        "label": "Total Site Electricity Use (kWh)",
        "key": "total_site_electricity_use",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricUtility.electric_to_load_series_kw_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricUtility.electric_to_load_series_kw")
    },
    {
        "label": "Net Purchased Electricity Reduction (%)",
        "key": "net_purchased_electricity_reduction",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricUtility.electric_to_load_series_kwsdf_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricUtility.electric_to_load_series_kwsdf")
    },
    {
        "label": "Electricity Energy Cost ($)",
        "key": "electricity_energy_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_energy_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_energy_cost_before_tax")
    },
    {
        "label": "Electricity Demand Cost ($)",
        "key": "electricity_demand_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_demand_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_demand_cost_before_tax")
    },
    {
        "label": "Utility Fixed Cost ($)",
        "key": "utility_fixed_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_fixed_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_fixed_cost_before_tax")
    },
    {
        "label": "Purchased Electricity Cost ($)",
        "key": "purchased_electricity_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_bill_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_bill_before_tax")
    },
    {
        "label": "Electricity Export Benefit ($)",
        "key": "electricity_export_benefit",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_export_benefit_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.year_one_export_benefit_before_tax")
    },
    {
        "label": "Net Electricity Cost ($)",
        "key": "net_electricity_cost",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.lifecycle_energy_cost_after_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.lifecycle_energy_cost_after_tax")
    },
    {
        "label": "Electricity Cost Savings ($/year)",
        "key": "electricity_cost_savings",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricTariff.lifecycle_energy_cost_after_tax_bau_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricTariff.lifecycle_energy_cost_after_tax_bau")
    },
    {
        "label": "Boiler Fuel (MMBtu)",
        "key": "boiler_fuel",
        "bau_value": lambda df: safe_get(df, "outputs.ExistingBoiler.fuel_used_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ExistingBoiler.fuel_used_mmbtu")
    },
    {
        "label": "CHP Fuel (MMBtu)",
        "key": "chp_fuel",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.annual_fuel_consumption_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.annual_fuel_consumption_mmbtu")
    },
    {
        "label": "Total Fuel (MMBtu)",
        "key": "total_fuel",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricUtility.total_energy_supplied_kwh_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricUtility.total_energy_supplied_kwh")
    },
    {
        "label": "Natural Gas Reduction (%)",
        "key": "natural_gas_reduction",
        "bau_value": lambda df: safe_get(df, "outputs.ElectricUtility.annual_energy_supplied_kwh_bau_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ElectricUtility.annual_energy_supplied_kwh_bau")
    },
    {
        "label": "Boiler Thermal Production (MMBtu)",
        "key": "boiler_thermal_production",
        "bau_value": lambda df: safe_get(df, "outputs.ExistingBoiler.annual_thermal_production_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.ExistingBoiler.annual_thermal_production_mmbtu")
    },
    {
        "label": "CHP Thermal Production (MMBtu)",
        "key": "chp_thermal_production",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.annual_thermal_production_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.annual_thermal_production_mmbtu")
    },
    {
        "label": "Total Thermal Production (MMBtu)",
        "key": "total_thermal_production",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.annual_thermal_production_mmbtu_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.annual_thermal_production_mmbtu")
    },
    {
        "label": "Heating System Fuel Cost ($)",
        "key": "heating_system_fuel_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Site.heating_system_fuel_cost_us_dollars_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.heating_system_fuel_cost_us_dollars")
    },
    {
        "label": "CHP Fuel Cost ($)",
        "key": "chp_fuel_cost",
        "bau_value": lambda df: safe_get(df, "outputs.CHP.year_one_fuel_cost_before_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.CHP.year_one_fuel_cost_before_tax")
    },
    {
        "label": "Total Fuel (NG) Cost ($)",
        "key": "total_fuel_ng_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Site.total_fuel_cost_us_dollars_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.total_fuel_cost_us_dollars")
    },
    {
        "label": "Total Utility Cost ($)",
        "key": "total_utility_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Site.total_utility_cost_us_dollars_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.total_utility_cost_us_dollars")
    },
    {
        "label": "O&M Cost Increase ($)",
        "key": "om_cost_increase",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.om_and_replacement_present_cost_after_tax_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.om_and_replacement_present_cost_after_tax")
    },
    {
        "label": "Payback Period (years)",
        "key": "payback_period",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.simple_payback_years_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.simple_payback_years")
    },
    {
        "label": "Gross Capital Cost ($)",
        "key": "gross_capital_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_capital_costs_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.lifecycle_capital_costs")
    },
    {
        "label": "Federal Tax Incentive (30%)",
        "key": "federal_tax_incentive",
        "bau_value": lambda df: 0.3,
        "scenario_value": lambda df: 0.3
    },
    {
        "label": "Additional Grant ($)",
        "key": "additional_grant",
        "bau_value": lambda df: 0,  
        "scenario_value": lambda df: 0
    },
    {
        "label": "Incentive Value ($)",
        "key": "incentive_value",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.total_incentives_value_us_dollars_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.total_incentives_value_us_dollars")
    },
    {
        "label": "Net Capital Cost ($)",
        "key": "net_capital_cost",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.net_capital_cost_us_dollars_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.net_capital_cost_us_dollars")
    },
    {
        "label": "Annual Cost Savings ($)",
        "key": "annual_cost_savings",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.annual_cost_savings_us_dollars_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.annual_cost_savings_us_dollars")
    },
    {
        "label": "Simple Payback (years)",
        "key": "simple_payback",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.simple_payback_years_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.simple_payback_years")
    },
    {
        "label": "CO2 Emissions (tonnes)",
        "key": "co2_emissions",
        "bau_value": lambda df: safe_get(df, "outputs.Site.annual_emissions_tonnes_CO2_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.annual_emissions_tonnes_CO2")
    },
    {
        "label": "CO2 Reduction (tonnes)",
        "key": "co2_reduction",
        "bau_value": lambda df: safe_get(df, "outputs.Site.lifecycle_emissions_tonnes_CO2_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Site.lifecycle_emissions_tonnes_CO2")
    },
    {
        "label": "CO2 (%) savings",
        "key": "co2_savings_percentage",
        "bau_value": lambda df: 0,
        "scenario_value": lambda df: 0
    },
    {
        "label": "NPV ($)",
        "key": "npv",
        "bau_value": lambda df: safe_get(df, "outputs.Financial.npv_bau"),
        "scenario_value": lambda df: safe_get(df, "outputs.Financial.npv")
    },
    {
        "label": "PV Federal Tax Incentive (%)",
        "key": "pv_federal_tax_incentive",
        "bau_value": lambda df: safe_get(df, "inputs.PV.federal_itc_fraction_bau"),
        "scenario_value": lambda df: safe_get(df, "inputs.PV.federal_itc_fraction")
    },
    {
        "label": "Storage Federal Tax Incentive (%)",
        "key": "storage_federal_tax_incentive",
        "bau_value": lambda df: safe_get(df, "inputs.ElectricStorage.total_itc_fraction_bau"),
        "scenario_value": lambda df: safe_get(df, "inputs.ElectricStorage.total_itc_fraction")
    }
]

# Configuration for calculations
calculations = [
    {
        "name": "Total Site Electricity Use (kWh)",
        "formula": lambda col, bau, headers: f'={col}{headers["PV Serving Load (kWh)"] + 2}+{col}{headers["Wind Serving Load (kWh)"] + 2}+{col}{headers["CHP Serving Load (kWh)"] + 2}+{col}{headers["Grid Purchased Electricity (kWh)"] + 2}'
    },
    {
        "name": "Net Purchased Electricity Reduction (%)",
        "formula": lambda col, bau, headers: f'=({bau["grid_value"]}-{col}{headers["Grid Purchased Electricity (kWh)"] + 2})/{bau["grid_value"]}'
    },
    {
        "name": "Purchased Electricity Cost ($)",
        "formula": lambda col, bau, headers: f'={col}{headers["Electricity Energy Cost ($)"] + 2}+{col}{headers["Electricity Demand Cost ($)"] + 2}+{col}{headers["Utility Fixed Cost ($)"] + 2}'
    },
    {
        "name": "Net Electricity Cost ($)",
        "formula": lambda col, bau, headers: f'={col}{headers["Purchased Electricity Cost ($)"] + 2}-{col}{headers["Electricity Export Benefit ($)"] + 2}'
    },
    {
        "name": "Electricity Cost Savings ($/year)",
        "formula": lambda col, bau, headers: f'={bau["net_cost_value"]}-{col}{headers["Net Electricity Cost ($)"] + 2}'
    },
    {
        "name": "Total Fuel (MMBtu)",
        "formula": lambda col, bau, headers: f'={col}{headers["Boiler Fuel (MMBtu)"] + 2}+{col}{headers["CHP Fuel (MMBtu)"] + 2}'
    },
    {
        "name": "Natural Gas Reduction (%)",
        "formula": lambda col, bau, headers: f'=({bau["ng_reduction_value"]}-{col}{headers["Total Fuel (MMBtu)"] + 2})/{bau["ng_reduction_value"]}'
    },
    {
        "name": "Total Thermal Production (MMBtu)",
        "formula": lambda col, bau, headers: f'={col}{headers["Boiler Thermal Production (MMBtu)"] + 2}+{col}{headers["CHP Thermal Production (MMBtu)"] + 2}'
    },
    {
        "name": "Total Fuel (NG) Cost ($)",
        "formula": lambda col, bau, headers: f'={col}{headers["Heating System Fuel Cost ($)"] + 2}+{col}{headers["CHP Fuel Cost ($)"] + 2}'
    },
    {
        "name": "Total Utility Cost ($)",
        "formula": lambda col, bau, headers: f'={col}{headers["Net Electricity Cost ($)"] + 2}+{col}{headers["Total Fuel (NG) Cost ($)"] + 2}'
    },
    {
        "name": "Incentive Value ($)",
        "formula": lambda col, bau, headers: f'=({col}{headers["Federal Tax Incentive (30%)"] + 2}*{col}{headers["Gross Capital Cost ($)"] + 2})+{col}{headers["Additional Grant ($)"] + 2}'
    },
    {
        "name": "Net Capital Cost ($)",
        "formula": lambda col, bau, headers: f'={col}{headers["Gross Capital Cost ($)"] + 2}-{col}{headers["Incentive Value ($)"] + 2}'
    },
    {
        "name": "Annual Cost Savings ($)",
        "formula": lambda col, bau, headers: f'={bau["util_cost_value"]}-{col}{headers["Total Utility Cost ($)"] + 2}+{col}{headers["O&M Cost Increase ($)"] + 2}'
    },
    {
        "name": "Simple Payback (years)",
        "formula": lambda col, bau, headers: f'={col}{headers["Net Capital Cost ($)"] + 2}/{col}{headers["Annual Cost Savings ($)"] + 2}'
    },
    {
        "name": "CO2 Reduction (tonnes)",
        "formula": lambda col, bau, headers: f'={bau["co2_reduction_value"]}-{col}{headers["CO2 Emissions (tonnes)"] + 2}'
    },
    {
        "name": "CO2 (%) savings",
        "formula": lambda col, bau, headers: f'=({bau["co2_reduction_value"]}-{col}{headers["CO2 Emissions (tonnes)"] + 2})/{bau["co2_reduction_value"]}'
    },
    #Example Calculations
    # Calculation Without Reference to bau_cells
    {
        "name": "Placeholder Calculation Without BAU Reference",
        "formula": lambda col, bau, headers: f'={col}{headers["Placeholder1"] + 2}+{col}{headers["Placeholder2"] + 2}'
        # This formula adds Placeholder1 and Placeholder2 values from the scenario.
    },

    # Calculation With Reference to bau_cells
    {
        "name": "Placeholder Calculation With BAU Reference",
        "formula": lambda col, bau, headers: f'=({bau["placeholder1_value"]}-{col}{headers["Placeholder2"] + 2})/{bau["placeholder1_value"]}'
        # This formula calculates the percentage change of Placeholder2 using Placeholder1's BAU value as the reference.
    }
]

###############################################################
################ END Custom Table #############################
###############################################################