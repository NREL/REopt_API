import os
import json
import uuid
import sys
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse, HttpResponse
from tastypie.resources import ModelResource
from validators import REoptResourceValidation, ValidateNestedInput
from log_levels import log, setup_logging
from scenario import setup_scenario
from reo.models import ModelManager, BadPost
from reo.src.paths import Paths
from reo.src.reopt import reopt
from reo.results import parse_run_outputs
from reo.exceptions import REoptError, UnexpectedError
from celery import group, chain

api_version = "version 1.0.0"
saveToDb = True


class RunInputResource(ModelResource):

    class Meta:
        setup_logging()
        resource_name = 'reopt'
        allowed_methods = ['post']
        detail_allowed_methods = []
        authorization = ReadOnlyAuthorization()
        serializer = Serializer(formats=['json'])
        always_return_data = True
        validation = REoptResourceValidation()
        
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
        
        if 'Scenario' not in bundle.data.keys():
            self.is_valid(bundle)  # runs REoptResourceValidation
            output_format = 'flat'

            if bundle.errors:
                raise ImmediateHttpResponse(response=self.error_response(bundle.request, bundle.errors))

            input_validator = ValidateNestedInput(bundle.data, nested=False)

        else:  # nested input
            output_format = 'nested'
            input_validator = ValidateNestedInput(bundle.data, nested=True)

        run_uuid = str(uuid.uuid4())
        
        def set_status(d, status):
            d["outputs"]["Scenario"]["status"] = status

        data = dict()
        data["inputs"] = input_validator.input_dict
        data["messages"] = input_validator.messages
        data["outputs"] = {"Scenario": {'run_uuid': run_uuid, 'api_version': api_version}}
        """
        for webtool need to update data with input_validator.input_for_response (flat inputs), as well as flat outputs,
        this should be done in ModelManager.get_response if we are going to maintain backwards compatibility
        with the worker_queue.
        """

        if not input_validator.isValid:  # 400 Bad Request

            set_status(data, "Invalid inputs. See messages.")

            if saveToDb:
                badpost = BadPost(run_uuid=run_uuid, post=json.dumps(bundle.data), errors=str(data['messages']['errors']))
                badpost.save()

            raise ImmediateHttpResponse(HttpResponse(json.dumps(data),
                                                     content_type='application/json',
                                                     status=400))

        model_manager = ModelManager()
        if saveToDb:
            set_status(data, 'Optimizing...')
            model_manager.create_and_save(data)

        paths = vars(Paths(run_uuid=run_uuid))

        # Log POST request
        file_post_input = os.path.join(paths['inputs'], "POST.json")
        with open(file_post_input, 'w') as file_post:
            json.dump(input_validator.input_for_response, file_post)

        setup = setup_scenario.s(run_uuid=run_uuid, paths=paths, data=data)

        reopt_jobs = group(
            reopt.s(paths=paths, data=data, bau=False),
            reopt.s(paths=paths, data=data, bau=True),
        )
        call_back = parse_run_outputs.si(data=data, paths=paths, meta={'run_uuid': run_uuid, 'api_version': api_version})
        # .si for immutable signature, no outputs passed from reopt_jobs
        try:
            chain(setup | reopt_jobs, call_back)()
        except Exception as e:  # this is necessary for tests that intentionally raise Exceptions. See NOTES 1 below.

            if isinstance(e, REoptError):
                pass  # handled in each task
            else:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                log("UnexpectedError", "{} occurred in reo.api.".format(exc_type))
                err = UnexpectedError(exc_type, exc_value, exc_traceback, task='api.py', run_uuid=run_uuid)
                err.save_to_db()

                set_status(data, 'Internal Server Error. See messages for more.')
                data['messages']['errors'] = err.message

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