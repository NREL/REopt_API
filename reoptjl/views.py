# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
from django.db import models
import uuid
import sys
import traceback as tb
import re
from django.http import JsonResponse
from reo.exceptions import UnexpectedError
from reoptjl.models import Settings, PVInputs, ElectricStorageInputs, WindInputs, GeneratorInputs, ElectricLoadInputs,\
    ElectricTariffInputs, ElectricUtilityInputs, SpaceHeatingLoadInputs, PVOutputs, ElectricStorageOutputs,\
    WindOutputs, ExistingBoilerInputs, GeneratorOutputs, ElectricTariffOutputs, ElectricUtilityOutputs, \
    ElectricLoadOutputs, ExistingBoilerOutputs, DomesticHotWaterLoadInputs, SiteInputs, SiteOutputs, APIMeta, \
    UserProvidedMeta, CHPInputs, CHPOutputs, CoolingLoadInputs, ExistingChillerInputs, ExistingChillerOutputs,\
    CoolingLoadOutputs, HeatingLoadOutputs, REoptjlMessageOutputs, HotThermalStorageInputs, HotThermalStorageOutputs,\
    ColdThermalStorageInputs, ColdThermalStorageOutputs, AbsorptionChillerInputs, AbsorptionChillerOutputs,\
    FinancialInputs, FinancialOutputs, UserUnlinkedRuns, BoilerInputs, BoilerOutputs, SteamTurbineInputs, SteamTurbineOutputs
import os
import requests
import numpy as np
import json
import logging
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
        d["Site"] = SiteInputs.info_dict(SiteInputs)
        d["CHP"] = CHPInputs.info_dict(CHPInputs)
        d["AbsorptionChiller"] = AbsorptionChillerInputs.info_dict(AbsorptionChillerInputs)
        d["SteamTurbine"] = SteamTurbineInputs.info_dict(SteamTurbineInputs)
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

    try: r["inputs"]["CHP"] = meta.CHPInputs.dict
    except: pass

    try: r["inputs"]["AbsorptionChiller"] = meta.AbsorptionChillerInputs.dict
    except: pass

    try: r["inputs"]["SteamTurbine"] = meta.SteamTurbineInputs.dict
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
    }
    if (request.GET.get("size_class")):
        inputs["size_class"] = int(request.GET.get("size_class"))
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
                        "addressable_load_fraction", "cooling_doe_ref_name", "cooling_pct_share"]
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
                    value = request.GET.get(key)
                    if value is not None:
                        if type(value) == list:
                            monthly_list  = [request.GET.get(key+'[{}]'.format(i)) for i in range(12)]
                            k = key.split('[')[0]
                            inputs[k] = [float(i) for i in monthly_list]
                        else:
                            inputs[key] = float(value)

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
            summary_dict[str(m.meta.run_uuid)]['year_one_savings_us_dollars'] = (m.year_one_energy_cost_before_tax_bau + m.year_one_demand_cost_before_tax_bau + m.year_one_fixed_cost_before_tax_bau + m.year_one_min_charge_adder_before_tax_bau) - (m.year_one_energy_cost_before_tax + m.year_one_demand_cost_before_tax + m.year_one_fixed_cost_before_tax + m.year_one_min_charge_adder_before_tax)

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
            summary_dict[str(m.meta.run_uuid)]['npv_us_dollars'] = m.npv
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
    
    return summary_dict

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

def emissions_profile(request):
    try:
        inputs = {
            "latitude": request.GET['latitude'], # need to do float() to convert unicode?
            "longitude": request.GET['longitude']
        }
        julia_host = os.environ.get(
            'JULIA_HOST', 
            "julia"
        )
        http_jl_response = requests.get(
            "http://" + julia_host + ":8081/emissions_profile/", 
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
