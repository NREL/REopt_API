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
import uuid
import sys
import traceback
import logging
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse, HttpResponse
from tastypie.resources import ModelResource
from tastypie.validation import Validation
from job.validators import InputValidator
# from reo.src.profiler import Profiler  # TODO use Profiler?
from job.src.run_jump_model import run_jump_model
from reo.exceptions import UnexpectedError, REoptError
from job.models import Scenario
log = logging.getLogger(__name__)


def return400(data: dict, validator: InputValidator):
    data["status"] = (
        'Invalid inputs. No optimization task has been created. See messages for details.'
    )
    data["run_uuid"] = ""
    # TODO save BadInputs ?
    data["messages"]["error"] = "Invalid inputs. See 'input_errors'."
    data["messages"]["input_errors"] = validator.validation_errors
    raise ImmediateHttpResponse(HttpResponse(json.dumps(data), content_type='application/json', status=400))


class UUIDFilter(logging.Filter):

    def __init__(self, uuidstr):
        self.uuidstr = uuidstr

    def filter(self, record):
        record.uuidstr = self.uuidstr
        return True


class Job(ModelResource):

    class Meta:
        resource_name = 'job'
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
        run_uuid = str(uuid.uuid4())
        data = {
            "run_uuid": run_uuid,
            "api_version": 2,
            "reopt_version": "0.11.0",
            "messages": dict()
        }

        log.addFilter(UUIDFilter(run_uuid))

        if "Scenario" in bundle.data.keys():
            bundle.data["Scenario"].update({"run_uuid": run_uuid, "status": "validating..."})
        else:
            bundle.data.update({"Scenario": {"run_uuid": run_uuid, "status": "validating..."}})

        if bundle.request.META.get('HTTP_X_API_USER_ID', False):
            if bundle.request.META.get('HTTP_X_API_USER_ID', '') == '6f09c972-8414-469b-b3e8-a78398874103':
                bundle.data['Scenario']['job_type'] = 'REopt Lite Web Tool'
            else:
                bundle.data['Scenario']['job_type'] = 'developer.nrel.gov'
        else:
            bundle.data['Scenario']['job_type'] = 'Internal NREL'

        test_case = bundle.request.META.get('HTTP_USER_AGENT') or ''
        if test_case.startswith('check_http/'):
            bundle.data['Scenario']['job_type'] = 'Monitoring'

        # Validate inputs
        try:
            input_validator = InputValidator(bundle.data)
            input_validator.clean_fields()  # step 1 check field values
            if not input_validator.is_valid:
                return400(data, input_validator)
            input_validator.clean()  # step 2 check requirements that include more than one field (in one model)
            if not input_validator.is_valid:
                return400(data, input_validator)
            input_validator.cross_clean()  # step 3 check requirements that include more than one model
            if not input_validator.is_valid:
                return400(data, input_validator)
        except ImmediateHttpResponse as e:
            raise e  # returns the response from return400
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value.args[0], traceback.format_tb(exc_traceback),
                                  task='InputValidator', run_uuid=run_uuid)
            err.save_to_db()
            data["status"] = ('Internal Server Error during input validation. No optimization task has been created. '
                              'Please check your POST for bad values.')
            # data['inputs'] = bundle.data
            data['messages'] = {}
            data['messages']['error'] = err.message  # "Unexpected Error."
            log.error("Internal Server error: " + err.message)
            raise ImmediateHttpResponse(HttpResponse(json.dumps(data),
                                                     content_type='application/json',
                                                     status=500))  # internal server error

        try:
            input_validator.save()
        except Exception:
            log.error("Could not create and save run_uuid: {}\n Data: {}".format(run_uuid, data))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value.args[0], traceback.format_tb(exc_traceback),
                                  task='create_and_save',
                                  run_uuid=run_uuid)
            # err.save_to_db()
            data["status"] = "Internal Server Error during saving of inputs. Please see messages."
            data['messages'] = err.message  # "Unexpected Error."
            log.error("Internal Server error: " + err.message)
            raise ImmediateHttpResponse(HttpResponse(json.dumps(data),
                                                     content_type='application/json',
                                                     status=500))  # internal server error

        Scenario.objects.filter(run_uuid=run_uuid).update(status='Optimizing...')
        try:
            run_jump_model.s(data=input_validator.validated_input_dict).apply_async()
        except Exception as e:
            if isinstance(e, REoptError):
                pass  # handled in each task
            else:  # for every other kind of exception
                exc_type, exc_value, exc_traceback = sys.exc_info()
                err = UnexpectedError(exc_type, exc_value.args[0], traceback.format_tb(exc_traceback), task='api.py',
                                      run_uuid=run_uuid)
                err.save_to_db()
                data["status"] = 'Internal Server Error. See messages for more.'
                if 'messages' not in data.keys():
                    data['messages'] = {}
                data['messages']['error'] = err.message
                log.error("Internal Server error: " + err.message)
                raise ImmediateHttpResponse(HttpResponse(json.dumps(data),
                                            content_type='application/json',
                                            status=500))  # internal server error

        raise ImmediateHttpResponse(HttpResponse(json.dumps({'run_uuid': run_uuid}),
                                    content_type='application/json', status=201))


"""
NOTES
1. celery tasks raise exceptions through the .get() method. So, even though we handle exceptions with the
Task.on_failure method, they get raised again! (And again it seems. There are at least two re-raises occurring in
celery.Task).  So for tests, that call the chain synchronously, the intentional Exception that is re-raised through
the chain call causes a test failure.

Another way to solve this problem is to remove FAILURE from PROPAGATE_STATES in line 149 of:
    <where/you/keep/python/packages>/lib/python2.7/site-packages/celery/states.py
But, this may have unintended consequences.

All in all, celery exception handling is very obscure.
"""