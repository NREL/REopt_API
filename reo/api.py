import json
import logging
import uuid
import sys
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse, HttpResponse
from tastypie.resources import ModelResource
from tastypie.validation import Validation
from validators import ValidateNestedInput
from scenario import setup_scenario
from reo.log_levels import log
from reo.models import ModelManager, BadPost
from reo.src.profiler import Profiler
from reo.src.reopt import reopt
from reo.results import parse_run_outputs
from reo.exceptions import REoptError, UnexpectedError
from celery import group, chain

api_version = "version 1.0.0"
saveToDb = True


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
        from IPython import embed
        embed()
        input_validator = ValidateNestedInput(bundle.data)
        run_uuid = str(uuid.uuid4())

        # Setup and start profile
        profiler = Profiler()

        # Setup log to include UUID of run
        uuidFilter = UUIDFilter(run_uuid)
        log.addFilter(uuidFilter)
        log.info('Beginning run setup')
        

        def set_status(d, status):
            d["outputs"]["Scenario"]["status"] = status

        data = dict()
        data["inputs"] = input_validator.input_dict
        data["messages"] = input_validator.messages
        

        if not input_validator.isValid:  # 400 Bad Request
            log.debug("input_validator not valid")
            log.debug(json.dumps(data))

            data['run_uuid'] = 'Error. See messages for more information. ' \
                               'Note that inputs have default values filled in.'

            if saveToDb:
                badpost = BadPost(run_uuid=run_uuid, post=json.dumps(bundle.data), errors=str(data['messages']))
                badpost.save()

            raise ImmediateHttpResponse(HttpResponse(json.dumps(data),
                                                     content_type='application/json',
                                                     status=400))

        data["outputs"] = {"Scenario": {'run_uuid': run_uuid, 'api_version': api_version,
                                        'Profile': {'pre_setup_scenario_seconds': 0, 'setup_scenario_seconds': 0,
                                                    'reopt_seconds': 0, 'reopt_bau_seconds': 0,
                                                    'parse_run_outputs_seconds': 0}}}

        log.info('Entering ModelManager')
        model_manager = ModelManager()
        profiler.profileEnd()

        if saveToDb:
            set_status(data, 'Optimizing...')
            data['outputs']['Scenario']['Profile']['pre_setup_scenario_seconds'] = profiler.getDuration()
            model_manager.create_and_save(data)
        setup = setup_scenario.s(run_uuid=run_uuid, data=data, raw_post=bundle.data)
        call_back = parse_run_outputs.s(data=data, meta={'run_uuid': run_uuid, 'api_version': api_version})

        # (use .si for immutable signature, if no outputs were passed from reopt_jobs)
        log.info("Starting celery chain")
        try:
            chain(setup | group(reopt.s(data=data, run_uuid=run_uuid, bau=False), reopt.s(data=data, run_uuid=run_uuid, bau=True)) | call_back)()
        except Exception as e:  # this is necessary for tests that intentionally raise Exceptions. See NOTES 1 below.
            if isinstance(e, REoptError):
                pass  # handled in each task
            else:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                err = UnexpectedError(exc_type, exc_value, exc_traceback, task='api.py', run_uuid=run_uuid)
                err.save_to_db()

                set_status(data, 'Internal Server Error. See messages for more.')
                data['messages']['error'] = err.message
                log.error("Internal Server error: " + err.message)
                raise ImmediateHttpResponse(HttpResponse(json.dumps(data),
                                                         content_type='application/json',
                                                         status=500))  # internal server error

        log.info("Returning with HTTP 201")
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