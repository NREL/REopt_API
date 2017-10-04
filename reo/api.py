import logging
import os
import uuid
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import ModelResource
from models import RunInput
from validators import REoptResourceValidation, ValidateNestedInput
from api_definitions import inputs
from log_levels import log
from utilities import API_Error
from library import DatLibrary
from reo.models import RunOutput


def get_current_api():
    return "version 1.0.0"


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
        queryset = RunInput.objects.all()
        resource_name = 'reopt'
        allowed_methods = ['post']
        detail_allowed_methods= []
        object_class = RunInput
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

            if bundle.errors:
                raise ImmediateHttpResponse(response=self.error_response(bundle.request, bundle.errors))

            nested_input = ValidateNestedInput(bundle.data, nested=False)
        else:  # nested input
            nested_input = ValidateNestedInput(bundle.data, nested=True)

            if not nested_input.isValid:
                raise ImmediateHttpResponse(response=self.error_response(bundle.request, nested_input.error_response))

        # Format  and  Save Inputs
        model_inputs = dict({k: bundle.data.get(k) for k in inputs(full_list=True).keys() if k in bundle.data.keys() and bundle.data.get(k) is not None })
        model_inputs['api_version'] = get_current_api()       

        run = RunInput(**model_inputs)
        run.save()
        try:
            # Return  Results
            output_model = self.create_output(model_inputs, bundle.data)

            bundle.obj = output_model
            bundle.data = {k:v for k,v in output_model.__dict__.items() if not k.startswith('_')}

            return self.full_hydrate(bundle)

        except Exception as e:
            raise ImmediateHttpResponse(response=self.error_response(bundle.request, API_Error(e).response))

    def create_output(self, inputs_dict, json_POST):

        run_uuid = uuid.uuid4()

        run_set = DatLibrary(run_uuid=run_uuid, inputs_dict=inputs_dict)

        # Log POST request
        run_set.log_post(json_POST)

        # Run Optimization
        output_dictionary = run_set.run()

        # API level outputs
        output_dictionary['uuid'] = run_uuid  # we do a lot of mapping of uuid to run_uuid, can we use just one name?
        output_dictionary['run_input_id'] = 0  # hack for now, this field can be removed from database

        result = RunOutput(**output_dictionary)
        result.save()

        return result
