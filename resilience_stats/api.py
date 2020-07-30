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

from celery import shared_task
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from tastypie.resources import ModelResource
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.bundle import Bundle
from tastypie.validation import Validation
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.serializers import Serializer

from reo.models import ScenarioModel
from reo.exceptions import SaveToDatabase
from resilience_stats.models import ResilienceModel
from resilience_stats.validators import validate_run_uuid
from resilience_stats.views import run_outage_sim

# POST data:{"run_uuid": UUID, "bau": True}


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
            return JsonResponse({"Error": str(err.message)}, status=400)

        # Handle non-existent scenario runs
        try:
            scenario = ScenarioModel.objects.get(run_uuid=run_uuid)
        except ScenarioModel.DoesNotExist:
            msg = "Scenario {} does not exist.".format(run_uuid)
            return JsonResponse({"Error": msg}, content_type='application/json', status=404)

        if scenario.status == "Optimizing...":
            return JsonResponse({"Error": "The scenario is still optimizing. Please try again later."},
                                content_type='application/json', status=500)
        elif "error" in scenario.status.lower():
            return JsonResponse(
                {"Error": "An error occurred in the scenario. Please check the messages from your results."},
                content_type='application/json', status=500)
        # Kick-off outage sim run
        run_outage_sim_task.delay(run_uuid, bau)
        bundle.data = {"run_uuid": run_uuid, "bau": bau, "Success": True, "Status": 204}

        return bundle


@shared_task
def run_outage_sim_task(run_uuid, bau):
        scenario = ScenarioModel.objects.get(run_uuid=run_uuid)
        results = run_outage_sim(run_uuid, with_tech=True, bau=bau)
        rm = ResilienceModel.create(scenariomodel=scenario)

        try:
            ResilienceModel.objects.filter(id=rm.id).update(**results)
        except SaveToDatabase as e:
            raise ImmediateHttpResponse(HttpResponse(json.dumps({"Error": e.message}), content_type='application/json', status=201))
