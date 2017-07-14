from tastypie import fields
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import Resource
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpApplicationError
from tastypie.resources import ModelResource
from models import ProForma

import logging
from reo.log_levels import log
from reo.models import RunOutput

import os
from api_definitions import *
from validators import *
from utilities import is_error

from IPython import embed

def get_current_api():
    return "version 0.0.1"

def setup_logging():
    file_logfile = os.path.join(os.getcwd(), "log", "reopt_api.log")
    logging.basicConfig(filename=file_logfile,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M%S %p',
                        level=logging.INFO)
    log("INFO", "Logging setup")


class ProFormaResource(ModelResource):

    class Meta:
        setup_logging()
        queryset = ProForma.objects.all()
        resource_name = 'proforma'
        allowed_methods = ['post']
        detail_allowed_methods = []
        object_class = ProForma
        authorization = ReadOnlyAuthorization()
        serializer = Serializer(formats=['json'])
        always_return_data = True
        # validation = REoptResourceValidation()

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

        id = bundle.data.get('run_id')
        run_outputs = RunOutput.objects.get(pk=id)
        pf = ProForma(run_input_id=id)
        pf.save()
        pf.make(run_outputs)

        bundle.object = pf

        return self.full_hydrate(bundle)
