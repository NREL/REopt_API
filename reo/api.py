import logging
import os
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import ModelResource
from models import RunInput
from validators import REoptResourceValidation
from api_definitions import inputs
from log_levels import log
from utilities import API_Error


def get_current_api():
    return "version 0.0.1"


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
        self.is_valid(bundle)
        if bundle.errors:
            raise ImmediateHttpResponse(response=self.error_response(bundle.request, bundle.errors))

        # Format  and  Save Inputs
           
        model_inputs = dict({k: bundle.data.get(k) for k in inputs(full_list=True).keys() if k in bundle.data.keys() and bundle.data.get(k) is not None })

        model_inputs['api_version'] = get_current_api()       


        run = RunInput(**model_inputs)
        run.save()
        try:
            # Return  Results
            output_obj = run.create_output(model_inputs.keys(), bundle.data)

            bundle.obj = output_obj
            bundle.data = {k:v for k,v in output_obj.__dict__.items() if not k.startswith('_')}

            return self.full_hydrate(bundle)

        except Exception as e:
            if len(e.args)==2:
                e_type,e_message = e
            else:
                e_type,e_message = "New Error",e

            raise ImmediateHttpResponse(response=self.error_response(bundle.request, API_Error(e_type,e_message).response))
