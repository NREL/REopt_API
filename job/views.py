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
from job.models import Settings, PVInputs, ElectricStorageInputs, WindInputs, GeneratorInputs, ElectricLoadInputs,\
    ElectricTariffInputs, ElectricUtilityInputs, SpaceHeatingLoadInputs, PVOutputs, ElectricStorageOutputs,\
    WindOutputs, ExistingBoilerInputs, GeneratorOutputs, ElectricTariffOutputs, ElectricUtilityOutputs, \
    ElectricLoadOutputs, ExistingBoilerOutputs, DomesticHotWaterLoadInputs, SiteInputs, SiteOutputs, APIMeta, \
    UserProvidedMeta, CHPInputs, CHPOutputs, CoolingLoadInputs, ExistingChillerInputs, ExistingChillerOutputs,\
    CoolingLoadOutputs, HeatingLoadOutputs, REoptjlMessageOutputs
import os
import requests
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
        # d["Boiler"] = BoilerInputs.info_dict(BoilerInputs)
        d["SpaceHeatingLoad"] = SpaceHeatingLoadInputs.info_dict(SpaceHeatingLoadInputs)
        d["DomesticHotWaterLoad"] = DomesticHotWaterLoadInputs.info_dict(DomesticHotWaterLoadInputs)
        d["Site"] = SiteInputs.info_dict(SiteInputs)
        d["CHP"] = CHPInputs.info_dict(CHPInputs)
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
        # d["Boiler"] = BoilerOutputs.info_dict(BoilerOutputs)
        d["Messages"] = REoptjlMessageOutputs.info_dict(REoptjlMessageOutputs)
        d["HeatingLoad"] = HeatingLoadOutputs.info_dict(HeatingLoadOutputs)
        d["CoolingLoad"] = CoolingLoadOutputs.info_dict(CoolingLoadOutputs)
        d["CHP"] = CHPOutputs.info_dict(CHPOutputs)
        return JsonResponse(d)

    except Exception as e:
        return JsonResponse({"Error": "Unexpected error in help endpoint: {}".format(e.args[0])}, status=500)


def results(request, run_uuid):
    """
    results endpoint for jobs
    """
    try:
        uuid.UUID(run_uuid)  # raises ValueError if not valid uuid
    except ValueError as e:
        if e.args[0] == "badly formed hexadecimal UUID string":
            resp = make_error_resp(e.args[0])
            return JsonResponse(resp, status=400)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value.args[0], tb.format_tb(exc_traceback), task='job.views.results', 
                run_uuid=run_uuid)
            err.save_to_db()
            return JsonResponse({"Error": str(err.args[0])}, status=400)

    try:
        # get all required inputs/outputs
        meta = APIMeta.objects.select_related(
            "Settings",
            'FinancialInputs', 'FinancialOutputs',
            'SiteInputs', 'SiteOutputs',
            'ElectricLoadInputs',
            'ElectricUtilityOutputs'
        ).get(run_uuid=run_uuid)
    except Exception as e:
        if isinstance(e, models.ObjectDoesNotExist):
            resp = {"messages": {"error": ""}}
            resp['messages']['error'] = (
                "run_uuid {} not in database. "
                "You may have hit the results endpoint too quickly after POST'ing scenario, "
                "have a typo in your run_uuid, or the scenario was deleted.").format(run_uuid)
            resp['status'] = 'error'
            return JsonResponse(resp, status=404)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value.args[0], tb.format_tb(exc_traceback), task='job.views.results', 
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

    # try: r["inputs"]["Boiler"] = meta.BoilerInputs.dict
    # except: pass

    try: r["inputs"]["SpaceHeatingLoad"] = meta.SpaceHeatingLoadInputs.dict
    except: pass

    try: r["inputs"]["DomesticHotWaterLoad"] = meta.DomesticHotWaterLoadInputs.dict
    except: pass

    try: r["inputs"]["CHP"] = meta.CHPInputs.dict
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
        # try: r["outputs"]["Boiler"] = meta.BoilerOutputs.dict
        # except: pass
        try: r["outputs"]["CHP"] = meta.CHPOutputs.dict
        except: pass
        try: r["outputs"]["HeatingLoad"] = meta.HeatingLoadOutputs.dict
        except: pass
        try: r["outputs"]["CoolingLoad"] = meta.CoolingLoadOutputs.dict
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
            err = UnexpectedError(exc_type, exc_value.args[0], tb.format_tb(exc_traceback), task='job.views.results', 
                run_uuid=run_uuid)
            err.save_to_db()
            resp = make_error_resp(err.message)
            return JsonResponse(resp, status=500)
    
    if meta.status == "error":
        return JsonResponse(r, status=400)

    return JsonResponse(r)


def chp_defaults(request):
    inputs = {
        "existing_boiler_production_type": request.GET.get("existing_boiler_production_type"),
        "avg_boiler_fuel_load_mmbtu_per_hour": request.GET.get("avg_boiler_fuel_load_mmbtu_per_hour"),
        "prime_mover": request.GET.get("prime_mover"),
        "size_class": request.GET.get("size_class"),
        "boiler_efficiency": request.GET.get("boiler_efficiency")
    }
    try:
        julia_host = os.environ.get('JULIA_HOST', "julia")
        http_jl_response = requests.get("http://" + julia_host + ":8081/chp_defaults/", json=inputs)
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
        return JsonResponse({"Error": "Unexpected error in chp_defaults endpoint. Check log for more."}, status=500)

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
        inputs["latitude"] = float(request.GET['latitude'])  # need float to convert unicode
        inputs["longitude"] = float(request.GET['longitude'])
        inputs["load_type"] = request.GET.get('load_type')

        # This parses the GET request way of sending a list/array for doe_reference_name, 
        # i.e. doe_reference_name[0], doe_reference_name[1], etc
        if 'doe_reference_name' in request.GET.keys():
            inputs["doe_reference_name"] = request.GET.get('doe_reference_name')
        elif 'doe_reference_name[0]' in request.GET.keys():
            idx = 0
            doe_reference_name = []
            percent_share_list = []
            while 'doe_reference_name[{}]'.format(idx) in request.GET.keys():
                doe_reference_name.append(request.GET['doe_reference_name[{}]'.format(idx)])
                if 'percent_share[{}]'.format(idx) in request.GET.keys():
                    percent_share_list.append(float(request.GET['percent_share[{}]'.format(idx)]))
                idx += 1
            inputs["doe_reference_name"] = doe_reference_name
            inputs["percent_share_list"] = percent_share_list

        # When wanting cooling profile based on building type(s) for cooling, need separate cooling building(s)
        if 'cooling_doe_ref_name' in request.GET.keys():
            inputs["cooling_doe_ref_name"] = request.GET.get('cooling_doe_ref_name')
        elif 'cooling_doe_ref_name[0]' in request.GET.keys():
            idx = 0
            cooling_doe_ref_name = []
            cooling_pct_share_list = []
            while 'cooling_doe_ref_name[{}]'.format(idx) in request.GET.keys():
                cooling_doe_ref_name.append(request.GET['cooling_doe_ref_name[{}]'.format(idx)])
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
                        inputs[key] = value

        julia_host = os.environ.get('JULIA_HOST', "julia")
        http_jl_response = requests.get("http://" + julia_host + ":8081/simulated_load/", json=inputs)
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
        return JsonResponse({"Error": "Unexpected error in simulated_load endpoint. Check log for more."}, status=500)
