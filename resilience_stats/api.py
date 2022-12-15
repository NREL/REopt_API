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
import json
import sys
import uuid
import numpy as np
import requests
import traceback
import os

from celery import shared_task
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.validation import Validation
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

from reo.exceptions import SaveToDatabase, UnexpectedError, REoptFailedToStartError

from reo.models import ScenarioModel, FinancialModel
from job.models import APIMeta, GeneratorOutputs, ElectricStorageInputs, ElectricStorageOutputs, PVOutputs, ElectricLoadInputs#, CHPOutputs
from resilience_stats.models import ResilienceModel, ERPMeta, ERPInputs, ERPOutputs, get_erp_input_dict_from_run_uuid
from resilience_stats.validators import validate_run_uuid
from resilience_stats.views import run_outage_sim


# POST data:{"run_uuid": UUID, "bau": True}


class ERPJob(ModelResource):

    class Meta:
        resource_name = 'erp'
        allowed_methods = ['post']
        detail_allowed_methods = []
        authorization = ReadOnlyAuthorization()
        serializer = Serializer(formats=['json'])
        always_return_data = True
        validation = Validation()
        object_class = None
        
    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj['id']

        return kwargs

    def get_object_list(self, request):
        return [request]

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)

    def obj_create(self, bundle, **kwargs):
        erp_run_uuid = str(uuid.uuid4())

        meta_dict = {
            "run_uuid": erp_run_uuid,
            "reopt_version": "0.18.0",
            "status": "Validating..."
        }
        try:
            if bundle.request.META.get('HTTP_X_API_USER_ID', False):
                if bundle.request.META.get('HTTP_X_API_USER_ID', '') == '6f09c972-8414-469b-b3e8-a78398874103':
                    meta_dict["job_type"] = 'REopt Web Tool'
                else:
                    meta_dict["job_type"] = 'developer.nrel.gov'
            else:
                meta_dict["job_type"] = 'Internal NREL'
            test_case = bundle.request.META.get('HTTP_USER_AGENT','')
            if test_case.startswith('check_http/'):
                meta_dict["job_type"] = 'Monitoring'

            reopt_run_uuid = bundle.data.get("reopt_run_uuid", None)
            meta_dict["reopt_run_uuid"] = reopt_run_uuid

            meta = ERPMeta.create(**meta_dict)
            meta.clean_fields()
            meta.save()

            if reopt_run_uuid is None:
                if bundle.data.get("CHP", None) or bundle.data.get("PrimeGenerator", None):
                    meta_dict["status"] = "Validation Error. See messages for details."
                    meta_dict["messages"] = {}
                    meta_dict["messages"]["error"] = "Running ERP with CHP or PrimeGenerator but no reopt_run_uuid is not yet supported."
                    raise ImmediateHttpResponse(HttpResponse(json.dumps(meta_dict),
                                            content_type='application/json',
                                            status=400))
            else:
                #TODO: put in helper function for more readable code
                try:
                    validate_run_uuid(reopt_run_uuid)
                except ValidationError as err:
                    meta_dict["status"] = "Validation Error. See messages for details."
                    meta_dict["messages"] = {}
                    meta_dict["messages"]["error"] = str(err.message)
                    raise ImmediateHttpResponse(HttpResponse(json.dumps(meta_dict), status=400))

                ### Get values from REopt run for inputs that user has not provided ###
                # Note: have to try/except for CHP, ElectricStorage, and Generator models 
                # because may not exist (not PV because just get empty list)

                ## Get Meta model, validating reopt run_uuid ##
                try:
                    reopt_run_meta = APIMeta.objects.select_related(
                        "ElectricLoadOutputs",
                    ).get(run_uuid=reopt_run_uuid)
                except:
                    # Handle non-existent REopt runs
                    meta_dict["status"] = "Validation Error. See messages for details."
                    meta_dict["messages"] = {}
                    meta_dict["messages"]["error"] = "Invalid run_uuid {}, REopt run does not exist.".format(reopt_run_uuid)
                    raise ImmediateHttpResponse(HttpResponse(
                                        json.dumps(meta_dict), 
                                        content_type='application/json', 
                                        status=404))
                
                #TODO: put all of this stuff below in a helper function, or in clean or save django methods?

                ## Outage ##
                critical_loads_kw = reopt_run_meta.ElectricLoadOutputs.dict["critical_load_series_kw"]
                if bundle.data.get("Outage", None) is None:
                     bundle.data["Outage"] = {"critical_loads_kw": critical_loads_kw}
                elif bundle.data["Outage"].get("critical_loads_kw", None) is None: 
                    bundle.data["Outage"]["critical_loads_kw"] = critical_loads_kw
                # TODO: set max_outage_duration based on reopt outage inputs when multiple outage PR merged
                # if bundle.data["Outage"].get("max_outage_duration", None) is None: 
                #     bundle.data["Outage"]["max_outage_duration"] = max(reopt_run_meta.ElectricUtilityInputs.dict["outage_durations"])
                                
                ## BackupGenerator ##
                gen_out = None
                try:
                    gen_out = reopt_run_meta.GeneratorOutputs.dict
                except AttributeError as e: 
                    pass
                if "BackupGenerator" not in bundle.data and \
                                gen_out is not None and \
                                gen_out.get("size_kw", 0) > 0:
                    bundle.data["BackupGenerator"] = {}
                # if "BackupGenerator" is still not in bundle.data then not being included
                if "BackupGenerator" in bundle.data:
                    if bundle.data["BackupGenerator"].get("generator_size_kw", None) is None \
                                                                    and gen_out is not None:
                        num_generators = bundle.data["BackupGenerator"].get("num_generators", None)
                        if num_generators is not None:
                            bundle.data["BackupGenerator"]["generator_size_kw"] = gen_out.get("size_kw", 0) / num_generators
                        else:
                            bundle.data["BackupGenerator"]["generator_size_kw"] = gen_out.get("size_kw", 0)
                    try:
                        gen_in = reopt_run_meta.GeneratorInputs.dict
                        for field_name in [
                                            "fuel_avail_gal", 
                                            "electric_efficiency_half_load", 
                                            "electric_efficiency_full_load"
                                        ]:
                            if bundle.data["BackupGenerator"].get(field_name, None) is None:
                                bundle.data["BackupGenerator"][field_name] = gen_in[field_name]
                    except AttributeError as e: 
                        pass

                ## CHP/PrimeGenerator ##
                try:
                    #TODO: how to distinguish CHP from prime generator using the CHP model?
                    if bundle.data.get("chp_size_kw", None) is None: 
                        bundle.data["chp_size_kw"] = reopt_run_meta.CHPOutputs.dict.get("size_kw", 0)
                except AttributeError as e:
                    pass

                ## PV ##
                pvs = reopt_run_meta.PVOutputs.all()
                pv_size_kw = 0
                pv_kw_series = np.zeros(len(critical_loads_kw))
                for pv in pvs:
                    pvd = pv.dict
                    pv_size_kw += pvd.get("size_kw")
                    pv_kw_series += (
                        np.array(pvd.get("year_one_to_battery_series_kw"))
                        + np.array(pvd.get("year_one_curtailed_production_series_kw"))
                        + np.array(pvd.get("year_one_to_load_series_kw"))
                        + np.array(pvd.get("year_one_to_grid_series_kw"))
                    )
                pv_kw_series = pv_kw_series.tolist()
                if bundle.data.get("pv_size_kw", None) is None: 
                    bundle.data["pv_size_kw"] = pv_size_kw
                if bundle.data.get("pv_production_factor_series", None) is None: 
                    bundle.data["pv_production_factor_series"] = (np.array(pv_kw_series) / pv_size_kw).tolist()
                
                ## ElectricStorage ##
                try:
                    stor_out = reopt_run_meta.ElectricStorageOutputs.dict
                    stor_in = reopt_run_meta.ElectricStorageInputs.dict
                    if bundle.data.get("battery_charge_efficiency", None) is None: 
                        bundle.data["battery_charge_efficiency"] = stor_in["rectifier_efficiency_fraction"] * stor_in["internal_efficiency_fraction"]**0.5
                    if bundle.data.get("battery_discharge_efficiency", None) is None: 
                        bundle.data["battery_discharge_efficiency"] = stor_in["inverter_efficiency_fraction"] * stor_in["internal_efficiency_fraction"]**0.5
                    if bundle.data.get("battery_size_kw", None) is None: bundle.data["battery_size_kw"] = stor_out.get("size_kw", 0)
                    if bundle.data.get("battery_size_kwh", None) is None: bundle.data["battery_size_kwh"] = stor_out.get("size_kwh", 0)
                    if bundle.data.get("battery_starting_soc_series_fraction", None) is None: 
                        bundle.data["battery_starting_soc_series_fraction"] = stor_out.get("year_one_soc_series_fraction", [])
                except AttributeError as e: 
                    pass
                
            
            erpinputs = ERPInputs.create(meta=meta, **bundle.data)
            erpinputs.clean()
            erpinputs.clean_fields()
            erpinputs.save()

            meta.status = 'Simulating...'
            meta.save(update_fields=['status'])
            run_erp_task.delay(erp_run_uuid)
        except ImmediateHttpResponse as e:
            raise e
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            meta_dict["status"] = "Internal Server Error. See messages for details."
            meta_dict["messages"] = {}
            meta_dict["messages"]["error"] = str(exc_value.args[0])
            raise ImmediateHttpResponse(HttpResponse(json.dumps(meta_dict),
                                        content_type='application/json',
                                        status=500))  # internal server error

        raise ImmediateHttpResponse(HttpResponse(json.dumps({'run_uuid': erp_run_uuid}),
                                    content_type='application/json', status=201))


class OutageSimJob(ModelResource):
    class Meta:
        resource_name = 'outagesimjob'
        allowed_methods = ['post']
        detail_allowed_methods = []
        authorization = ReadOnlyAuthorization()
        serializer = Serializer(formats=['json'])
        always_return_data = True
        validation = Validation()
        object_class = None

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            # Primary key is set to be the run_uuid for 1 to1 matching
            # between scenario UUID and outage sim UUID
            kwargs['pk'] = bundle_or_obj.data["run_uuid"]  # bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj.get("id")

        return kwargs

    def get_object_list(self, request):
        return [request]

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)

    def obj_create(self, bundle, **kwargs):
        run_uuid = bundle.data.get("run_uuid")
        bau = bundle.data.get("bau", False)
        # Handle invalid uuids
        try:
            validate_run_uuid(run_uuid)
        except ValidationError as err:
            raise ImmediateHttpResponse(HttpResponse(json.dumps({"Error": str(err.message)}), status=400))

        # Handle non-existent scenario runs
        try:
            scenario = ScenarioModel.objects.get(run_uuid=run_uuid)
        except ScenarioModel.DoesNotExist:
            msg = "Scenario {} does not exist!.".format(run_uuid)
            raise ImmediateHttpResponse(HttpResponse(json.dumps({"Error": msg}), content_type='application/json', status=404))

        if scenario.status == "Optimizing...":
            raise ImmediateHttpResponse(HttpResponse(json.dumps({"Error": "The scenario is still optimizing. Please try again later."}),
                                content_type='application/json', status=500))
        elif "error" in scenario.status.lower():
            raise ImmediateHttpResponse(HttpResponse(json.dumps(
                {"Error": "An error occurred in the scenario. Please check the messages from your results."}),
                content_type='application/json', status=500))

        if ResilienceModel.objects.filter(scenariomodel=scenario).count() > 0:
            err_msg = ("An outage simulation job has already been created for this run_uuid."
                "Please retrieve the results with a GET request to v1/outagesimjob/<run_uuid>/results."
                " Note: Even if not specified when the job was created, business-as-usual (BAU) can be retrieved"
                " from the results endpoint by specifying bau=true in the URL parameters.")

            raise ImmediateHttpResponse(HttpResponse(
                json.dumps({"Warning": err_msg}),
                content_type='application/json',
                status=208))
        else:  # This is the first POST for this run_uuid, kick-off outage sim run
            try:
                rm = ResilienceModel.create(scenariomodel=scenario)
            except SaveToDatabase as e:
                raise ImmediateHttpResponse(
                HttpResponse(json.dumps({"Error": e.message}), content_type='application/json', status=500))
            run_outage_sim_task.delay(rm.scenariomodel_id, run_uuid, bau)
            bundle.data = {"run_uuid": run_uuid, "bau": bau, "Success": True, "Status": 201}

        return bundle

@shared_task
def run_erp_task(run_uuid):
    name = 'run_erp_task'
    data = get_erp_input_dict_from_run_uuid(run_uuid)

    user_uuid = data.get('user_uuid')
    data.pop('user_uuid',None) # Remove user uuid from inputs dict to avoid downstream errors

    logger.info("Running ERP tool ...")
    try:
        julia_host = os.environ.get('JULIA_HOST', "julia")
        response = requests.post("http://" + julia_host + ":8081/erp/", json=data)
        response_json = response.json()
        if response.status_code == 500:
            raise REoptFailedToStartError(task=name, message=response_json["error"], run_uuid=run_uuid, user_uuid=user_uuid)

    except Exception as e:
        if isinstance(e, REoptFailedToStartError):
            raise e

        if isinstance(e, requests.exceptions.ConnectionError):  # Julia server down
            raise REoptFailedToStartError(task=name, message="Julia server is down.", run_uuid=run_uuid, user_uuid=user_uuid)

        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error("ERP raised an unexpected error: UUID: " + str(run_uuid))
        raise UnexpectedError(exc_type, exc_value, traceback.format_tb(exc_traceback), task=name, run_uuid=run_uuid,
                              user_uuid=user_uuid)
    else:
        logger.info("ERP run successful.")

    process_erp_results(response_json, run_uuid)
    return True

def process_erp_results(results: dict, run_uuid: str) -> None:
    """
    Saves ERP results returned from the Julia API in the backend database.
    Called in resilience_stats/run_erp_task (a celery task)
    """
    #TODO: get success or error status from julia
    meta = ERPMeta.objects.get(run_uuid=run_uuid)
    meta.status = 'Completed' #results.get("status")
    meta.save(update_fields=['status'])
    results.pop("marginal_outage_survival_final_time_step",None)
    ERPOutputs.create(meta=meta, **results).save()
    

@shared_task
def run_outage_sim_task(scenariomodel_id, run_uuid, bau):

    results = run_outage_sim(run_uuid, with_tech=True, bau=bau)

    try:
        ResilienceModel.objects.filter(scenariomodel_id=scenariomodel_id).update(**results)
        results = {'avoided_outage_costs_us_dollars': results['avoided_outage_costs_us_dollars']}
        FinancialModel.objects.filter(run_uuid=run_uuid).update(**results)        
    except SaveToDatabase as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = SaveToDatabase(exc_type, exc_value.args[0], exc_traceback, task='resilience_model', run_uuid=run_uuid)
        err.save_to_db()
