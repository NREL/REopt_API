from django.contrib.auth.models import User
from tastypie import fields
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import Resource
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpApplicationError
from tastypie.resources import ModelResource
from models import ProForma, RunOutput
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpBadRequest


import logging
from reo.log_levels import log
from reo.models import RunOutput

import os


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
        resource_name = 'proforma/spreadsheet'
        allowed_methods = ['post']
        detail_allowed_methods = []
        object_class = ProForma
        authorization = ReadOnlyAuthorization()
        serializer = Serializer(formats=['json'])
        always_return_data = True
        include_resource_uri = False
        excludes = ['created', 'updated','resource_uri','id']
        # validation = REoptResourceValidation()

    def obj_create(self, bundle, **kwargs):
        
        uuid = bundle.data.get('run_uuid')

        try:
            run = RunOutput.objects.get(uuid=uuid)
            
            try:
                pf = ProForma.objects.get(run_output=run.id)
            except:
                pf = ProForma.create(run_output_id=run.id)
                pf.generate_spreadsheet()

            pf.save()

            bundle.obj = pf

            return self.full_hydrate(bundle)

        except:
            raise ImmediateHttpResponse(HttpBadRequest("Invalid UUID"))


