from django.contrib.auth.models import User
from tastypie import fields
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.authentication import ApiKeyAuthentication
from tastypie.resources import Resource
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpApplicationError
from tastypie.resources import ModelResource
from models import ProForma
from tastypie.exceptions import Unauthorized


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
        authentication = ApiKeyAuthentication()

    def obj_create(self, bundle, **kwargs):

        ro_id = bundle.data.get('run_output_id')

        if ro_id in [i.id for i in RunOutput.objects.filter(user=bundle.request.user)]:

            pfs = ProForma.objects.filter(run_output_id=ro_id,user=user) 
            
            if len(pfs) == 1:
                pf = pfs[0]    
            else:
                pf = ProForma.create(run_output_id=ro_id)
                pf.generate_spreadsheet()

            pf.save()
            
            bundle.obj = pf
                
            return self.full_hydrate(bundle)

        else:
            raise Unauthorized("Invalid Authorization")


