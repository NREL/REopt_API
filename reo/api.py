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
from scenario import Scenario
from reo.models import RunOutput, REoptResponse


api_version = "version 1.0.0"


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
        detail_allowed_methods = []
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

            input_validator = ValidateNestedInput(bundle.data, nested=False)

        else:  # nested input
            input_validator = ValidateNestedInput(bundle.data, nested=True)

        # Format  and  Save Inputs
        # model_inputs = dict({k: bundle.data.get(k) for k in inputs(full_list=True).keys() if k in bundle.data.keys() and bundle.data.get(k) is not None })
        # model_inputs['api_version'] = api_version

        # run = RunInput(**model_inputs)
        # run.save()

        # Return  Results
        output_model = self.create_output(bundle.data, input_validator)
        bundle.obj = output_model
        bundle.data = {k: v for k, v in output_model.__dict__.items() if not k.startswith('_')}
        bundle.data['id'] = 1  # get error without this line?

        return self.full_hydrate(bundle)

    def create_output(self, json_POST, input_validator):

        run_uuid = uuid.uuid4()

        if not input_validator.isValid:
            output_dictionary = {
                "messages": {
                    "errors": input_validator.errors,
                    "warnings": input_validator.warnings
                },
                "inputs": json_POST,
                "outputs": {},
            }

        else:
            try: # should return output structure to match new nested_outputs, even with exception
                run_set = Scenario(run_uuid=run_uuid, inputs_dict=input_validator.input_dict['Scenario'])

                # Log POST request
                run_set.log_post(json_POST)

                # Run Optimization
                output_dictionary = dict()
                output_dictionary['outputs'] = run_set.run()

            except Exception as e:
                output_dictionary = {
                    # "Input": inputs_dict,
                    "messages": {
                        "error": API_Error(e).response,
                        "warnings": input_validator.warnings,
                    },
                    "inputs": json_POST,
                    "outputs": {},
                }
        # API level outputs
        output_dictionary['outputs']['uuid'] = run_uuid  # we do a lot of mapping of uuid to run_uuid, can we use just one name?
        output_dictionary['outputs']['api_version'] = api_version
        result = REoptResponse(messages={"warnings": input_validator.warnings},
                               inputs=json_POST,
                               **output_dictionary)
        # result.save()
        # import pdb; pdb.set_trace()

        return result
