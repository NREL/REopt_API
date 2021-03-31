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
import logging
import traceback

from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.validation import Validation

from reo.exceptions import SaveToDatabase, UnexpectedError
from reo.models import ScenarioModel
from resilience_stats.validators import validate_run_uuid
from futurecosts.models import FutureCostsJob
from futurecosts.validators import InputValidator
from futurecosts.tasks import setup_jobs
log = logging.getLogger(__name__)


def return400(data: dict, validator: InputValidator):
    data["status"] = (
        'Invalid inputs. No job has been created. See messages for details.'
    )
    data["messages"] = validator.validation_errors
    raise ImmediateHttpResponse(HttpResponse(json.dumps(data), content_type='application/json', status=400))


class FutureCostsAPI(ModelResource):

    class Meta:
        resource_name = 'futurecosts'
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
        # Handle invalid uuids
        try:
            validate_run_uuid(run_uuid)
        except ValidationError as err:
            raise ImmediateHttpResponse(HttpResponse(json.dumps({"Error": str(err.message)}), status=400))

        # Handle non-existent scenario
        try:
            scenario = ScenarioModel.objects.get(run_uuid=run_uuid)
        except ScenarioModel.DoesNotExist:
            msg = "Scenario {} does not exist!.".format(run_uuid)
            raise ImmediateHttpResponse(HttpResponse(json.dumps({"Error": msg}), content_type='application/json', status=404))

        if scenario.status == "Optimizing...":
            raise ImmediateHttpResponse(HttpResponse(json.dumps(
                {"Error": "The scenario is still optimizing. Please try again later."}),
                content_type='application/json', status=500)
            )
        elif "error" in scenario.status.lower():
            raise ImmediateHttpResponse(HttpResponse(json.dumps(
                {"Error": "An error occurred in the scenario. Please check the messages from your results."}),
                content_type='application/json', status=500))

        if FutureCostsJob.objects.filter(base_scenario=scenario).count() > 0:
            err_msg = (
                "A futurecosts job has already been created for this run_uuid."
                "You can retrieve the results with a GET request to /futurecosts/<run_uuid>/results."
            )
            raise ImmediateHttpResponse(HttpResponse(
                json.dumps({"Warning": err_msg}),
                content_type='application/json',
                status=208))
        else:  # This is the first POST for this run_uuid

            job = FutureCostsJob.create(**{"base_scenario": scenario, "run_uuid": run_uuid})
            job.clean()
            job.save()

            setup_jobs(run_uuid)
            resp = {'status': 'Future Costs Job created for scenario {}'.format(run_uuid)}
            raise ImmediateHttpResponse(HttpResponse(
                json.dumps(resp),
                content_type='application/json',
                status=201
            ))




            # # Validate inputs
            # # TODO don't need all this since only input is a run_uuid?
            # try:
            #     input_validator = InputValidator(bundle.data, run_uuid=run_uuid)
            #     input_validator.clean_fields()  # step 1 check field values
            #     if not input_validator.is_valid:
            #         return400(data, input_validator)
            #     input_validator.clean()  # step 2 check requirements that include more than one field (in one model)
            #     if not input_validator.is_valid:
            #         return400(data, input_validator)
            #     input_validator.cross_clean()  # step 3 check requirements that include more than one model
            #     if not input_validator.is_valid:
            #         return400(data, input_validator)
            # except ImmediateHttpResponse as e:
            #     raise e
            # except Exception:
            #     exc_type, exc_value, exc_traceback = sys.exc_info()
            #     err = UnexpectedError(exc_type, exc_value.args[0], traceback.format_tb(exc_traceback),
            #                           task='InputValidator', run_uuid=run_uuid)
            #     err.save_to_db()
            #     data["status"] = (
            #         'Internal Server Error during input validation. No optimization task has been created. '
            #         'Please check your POST for bad values.')
            #     # data['inputs'] = bundle.data
            #     data['messages'] = {}
            #     data['messages']['error'] = err.message  # "Unexpected Error."
            #     log.error("Internal Server error: " + err.message)
            #     raise ImmediateHttpResponse(HttpResponse(json.dumps(data),
            #                                              content_type='application/json',
            #                                              status=500))  # internal server error

            """
            Have to serialize the Django Models to pass to celery task!
            """

            # data["status"] = 'Optimizing...'
            # try:
            #     input_validator.save()
            # except Exception:
            #     log.error("Could not create and save run_uuid: {}\n Data: {}".format(run_uuid, data))
            #     exc_type, exc_value, exc_traceback = sys.exc_info()
            #     err = UnexpectedError(exc_type, exc_value.args[0], traceback.format_tb(exc_traceback),
            #                           task='create_and_save',
            #                           run_uuid=run_uuid)
            #     # err.save_to_db()
            #     data["status"] = "Internal Server Error during saving of inputs. Please see messages."
            #     data['messages'] = err.message  # "Unexpected Error."
            #     log.error("Internal Server error: " + err.message)
            #     raise ImmediateHttpResponse(HttpResponse(json.dumps(data),
            #                                              content_type='application/json',
            #                                              status=500))  # internal server error
