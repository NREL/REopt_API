import logging
import os
import json
import uuid
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse, HttpResponse
from tastypie.resources import ModelResource
from validators import REoptResourceValidation, ValidateNestedInput
from log_levels import log
from utilities import API_Error
from scenario import setup_scenario
from reo.models import ModelManager, BadPost
from api_definitions import inputs as flat_inputs
from reo.src.paths import Paths
from reo.src.reopt import reopt
from reo.results import parse_run_outputs
from celery import group, chain

api_version = "version 1.0.0"
saveToDb = True


def setup_logging():
    file_logfile = os.path.join(os.getcwd(), "log", "reopt_api.log")
    logging.basicConfig(filename=file_logfile,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M%S %p',
                        level=logging.INFO)
    log("INFO", "Logging setup")


class RunInputResource(ModelResource):

    class Meta:
        setup_logging()
        # queryset = ScenarioModel.objects.all()
        resource_name = 'reopt'
        allowed_methods = ['post']
        detail_allowed_methods = []
        # object_class = ScenarioModel
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

        run_uuid = uuid.uuid4()
        
        def set_status(d, status):
            d["outputs"]["Scenario"]["status"] = status

        data = dict()
        data["inputs"] = input_validator.input_dict
        data["messages"] = input_validator.messages
        data["outputs"] = {"Scenario": {'run_uuid': str(run_uuid), 'api_version': api_version}}
        """
        for webtool need to update data with input_validator.input_for_response (flat inputs), as well as flat outputs
        """

        if not input_validator.isValid:  # 400 Bad Request

            set_status(data, "Invald inputs. See messages.")

            if saveToDb:
                bad_post = BadPost(run_uuid=run_uuid, post=bundle.data, errors=data['messages']['errors']).create()

            raise ImmediateHttpResponse(HttpResponse(json.dumps(data),
                                                     content_type='application/json',
                                                     status=400))

        model_manager = ModelManager()
        if saveToDb:
            set_status(data, 'Optimizing...')
            model_manager.create_and_save(data)

        paths = vars(Paths(run_uuid=run_uuid))

        setup = setup_scenario.s(run_uuid=run_uuid, paths=paths,
                                 json_post=input_validator.input_for_response, data=data)
        reopt_jobs = group(
            reopt.s(paths=paths, data=data, bau=False),
            reopt.s(paths=paths, data=data, bau=True),
        )
        call_back = parse_run_outputs.si(data=data, paths=paths, meta={'run_uuid': run_uuid, 'api_version': api_version})
        # .si for immutable signature, no outputs passed from reopt_jobs
        chain(setup | reopt_jobs, call_back)()

        raise ImmediateHttpResponse(HttpResponse(json.dumps({'run_uuid': str(run_uuid)}),
                                                 content_type='application/json', status=201))
