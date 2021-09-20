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
from django.http import JsonResponse
from reo.exceptions import UnexpectedError
from job.models import Scenario, Settings, PVInputs, StorageInputs, WindInputs, GeneratorInputs, ElectricLoadInputs,\
    ElectricTariffInputs, ElectricUtilityInputs, PVOutputs, StorageOutputs, WindOutputs, GeneratorOutputs, \
    ElectricTariffOutputs, ElectricUtilityOutputs, ElectricLoadOutputs


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
        d["Scenario"] = Scenario.info_dict(Scenario)
        d["Settings"] = Settings.info_dict(Settings)
        d["ElectricLoad"] = ElectricLoadInputs.info_dict(ElectricLoadInputs)
        d["ElectricTariff"] = ElectricTariffInputs.info_dict(ElectricTariffInputs)
        d["ElectricUtility"] = ElectricUtilityInputs.info_dict(ElectricUtilityInputs)
        d["PV"] = PVInputs.info_dict(PVInputs)
        d["Storage"] = StorageInputs.info_dict(StorageInputs)
        d["Wind"] = WindInputs.info_dict(WindInputs)
        d["Generator"] = GeneratorInputs.info_dict(GeneratorInputs)
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
        d["PV"] = PVOutputs.info_dict(PVOutputs)
        d["Storage"] = StorageOutputs.info_dict(StorageOutputs)
        d["Wind"] = WindOutputs.info_dict(WindOutputs)
        d["Generator"] = GeneratorOutputs.info_dict(GeneratorOutputs)
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
        s = Scenario.objects.select_related(
            "Settings",
            'FinancialInputs', 'FinancialOutputs',
            'SiteInputs',
            'ElectricLoadInputs',
            'ElectricTariffInputs', 'ElectricTariffOutputs',
            'ElectricUtilityOutputs'
        ).get(run_uuid=run_uuid)
        # TODO: how do we get the Message's models?
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

    r = s.dict
    r["inputs"] = dict()
    r["inputs"]["Scenario"] = s.dict
    r["inputs"]["Financial"] = s.FinancialInputs.dict
    r["inputs"]["ElectricLoad"] = s.ElectricLoadInputs.dict
    r["inputs"]["ElectricTariff"] = s.ElectricTariffInputs.dict
    r["inputs"]["Site"] = s.SiteInputs.dict
    r["inputs"]["Settings"] = s.Settings.dict

    # We have to try for the following objects because they may or may not be defined
    try:
        pvs = s.PVInputs.all()
        if len(pvs) == 1:
            r["inputs"]["PV"] = pvs[0].dict
        elif len(pvs) > 1:
            r["inputs"]["PV"] = []
            for pv in pvs:
                r["inputs"]["PV"].append(pv.dict)

    except: pass

    try: r["inputs"]["ElectricUtility"] = s.ElectricUtilityInputs.dict
    except: pass

    try: r["inputs"]["Storage"] = s.StorageInputs.dict
    except: pass

    try: r["inputs"]["Generator"] = s.GeneratorInputs.dict
    except: pass

    try: r["inputs"]["Wind"] = s.WindInputs.dict
    except: pass

    for d in r["inputs"].values():
        if isinstance(d, dict):
            d.pop("scenario_id", None)
        elif isinstance(d, list):
            for subd in d:
                subd.pop("scenario_id", None)

    try:
        r["outputs"] = dict()
        r["outputs"]["Financial"] = s.FinancialOutputs.dict
        r["outputs"]["ElectricTariff"] = s.ElectricTariffOutputs.dict
        r["outputs"]["ElectricUtility"] = s.ElectricUtilityOutputs.dict
        r["outputs"]["ElectricLoad"] = s.ElectricLoadOutputs.dict

        try:
            pvs = s.PVOutputs.all()
            if len(pvs) == 1:
                r["outputs"]["PV"] = pvs[0].dict
            elif len(pvs) > 1:
                r["outputs"]["PV"] = []
                for pv in pvs:
                    r["outputs"]["PV"].append(pv.dict)
        except: pass
        try: r["outputs"]["Storage"] = s.StorageOutputs.dict
        except: pass
        try: r["outputs"]["Generator"] = s.GeneratorOutputs.dict
        except: pass
        try: r["outputs"]["Wind"] = s.WindOutputs.dict
        except: pass

        for d in r["outputs"].values():
            if isinstance(d, dict):
                d.pop("scenario_id", None)
            elif isinstance(d, list):
                for subd in d:
                    subd.pop("scenario_id", None)
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

    return JsonResponse(r)
