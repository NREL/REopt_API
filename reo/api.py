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
from reo.src.run_jump_model import run_jump_model
from reo.results import parse_run_outputs
from reo.exceptions import REoptError, UnexpectedError
from celery import group, chain

api_version = "version 1.0.0"
saveToDb = True


def set_status(d, status):
    if 'outputs' not in d.keys():
        d["outputs"] = {"Scenario": {"status": status}}
    d["outputs"]["Scenario"]["status"] = status


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
        run_uuid = str(uuid.uuid4())
        data = dict()
        data["outputs"] = {"Scenario": {'run_uuid': run_uuid, 'api_version': api_version,
                                        'Profile': {'pre_setup_scenario_seconds': 0, 'setup_scenario_seconds': 0,
                                                        'reopt_seconds': 0, 'reopt_bau_seconds': 0,
                                                        'parse_run_outputs_seconds': 0},                                            
                                       }
                           }

        # Setup and start profile
        profiler = Profiler()

        uuidFilter = UUIDFilter(run_uuid)
        log.addFilter(uuidFilter)
        log.info('Beginning run setup')

        try:
            input_validator = ValidateNestedInput(bundle.data)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value.message,  exc_traceback, task='ValidateNestedInput', run_uuid=run_uuid)
            err.save_to_db()
            set_status(data, 'Internal Server Error during input validation. No optimization task has been created. Please check your POST for bad values.')
            data['inputs'] = bundle.data
            data['messages'] = {}
            data['messages']['error'] = err.message  # "Unexpected Error."
            log.error("Internal Server error: " + err.message)
            raise ImmediateHttpResponse(HttpResponse(json.dumps(data),
                                                     content_type='application/json',
                                                     status=500))  # internal server error

        data["inputs"] = input_validator.input_dict
        data["messages"] = input_validator.messages

        if not input_validator.isValid:  # 400 Bad Request
            log.debug("input_validator not valid")
            log.debug(json.dumps(data))

            set_status(data, 'Error. No optimization task has been created. See messages for more information. ' \
                               'Note that inputs have default values filled in.')
            if saveToDb:
                badpost = BadPost(run_uuid=run_uuid, post=json.dumps(bundle.data), errors=str(data['messages']))
                badpost.save()

            raise ImmediateHttpResponse(HttpResponse(json.dumps(data),
                                                     content_type='application/json',
                                                     status=400))

        log.info('Entering ModelManager')
        model_manager = ModelManager()
        profiler.profileEnd()

        if saveToDb:
            set_status(data, 'Optimizing...')
            data['outputs']['Scenario']['Profile']['pre_setup_scenario_seconds'] = profiler.getDuration()
            if bundle.request.META.get('HTTP_X_API_USER_ID',False):
                if bundle.request.META.get('HTTP_X_API_USER_ID','') == '6f09c972-8414-469b-b3e8-a78398874103':
                    data['outputs']['Scenario']['job_type'] = 'REopt Lite Web Tool'
                else:
                    data['outputs']['Scenario']['job_type'] = 'developer.nrel.gov'
            else:
                data['outputs']['Scenario']['job_type'] = 'Internal NREL'

            if bundle.request.META.get('HTTP_USER_AGENT','').startswith('check_http/'):
                data['outputs']['Scenario']['job_type'] = 'Monitoring'
            try:
                model_manager.create_and_save(data)
            except Exception as e:
                log.error("Could not create and save run_uuid: {}\n Data: {}".format(run_uuid,data))
                exc_type, exc_value, exc_traceback = sys.exc_info()
                err = UnexpectedError(exc_type, exc_value.message, exc_traceback, task='ModelManager.create_and_save',
                                      run_uuid=run_uuid)
                err.save_to_db()
                set_status(data, "Internal Server Error during saving of inputs. Please see messages.")
                data['messages']['error'] = err.message  # "Unexpected Error."
                log.error("Internal Server error: " + err.message)
                raise ImmediateHttpResponse(HttpResponse(json.dumps(data),
                                                         content_type='application/json',
                                                         status=500))  # internal server error

        setup = setup_scenario.s(run_uuid=run_uuid, data=data, raw_post=bundle.data)
        call_back = parse_run_outputs.s(data=data, meta={'run_uuid': run_uuid, 'api_version': api_version})
        # (use .si for immutable signature, if no outputs were passed from reopt_jobs)
        rjm = run_jump_model.s(data=data, run_uuid=run_uuid)
        rjm_bau = run_jump_model.s(data=data, run_uuid=run_uuid, bau=True)
        log.info("Starting celery chain")
        try:
            chain(setup | group(reopt.s(data=data, run_uuid=run_uuid, bau=False), reopt.s(data=data, run_uuid=run_uuid, bau=True)) | group(rjm, rjm_bau) | call_back)()
        except Exception as e:
            if isinstance(e, REoptError):
                pass  # handled in each task
            else:  # for every other kind of exception
                exc_type, exc_value, exc_traceback = sys.exc_info()
                err = UnexpectedError(exc_type, exc_value.message,  exc_traceback, task='api.py', run_uuid=run_uuid)
                err.save_to_db()
                set_status(data, 'Internal Server Error. See messages for more.')
                if 'messages' not in data.keys():
                    data['messages'] = {}
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
