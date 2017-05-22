from django.db import models
from django.contrib.postgres.fields import *
from tastypie.exceptions import ImmediateHttpResponse

from api_definitions import outputs


class ResilienceCase(models.Model):

    #Inputs
    load_8760_kwh = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    pv_resource_kwh = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    api_version = models.TextField(blank=True, default='', null=False)

    #Outputs
    resiliency_hours = models.FloatField(blank=True, null=True)

    @staticmethod
    def run(input_dictionary, bundle):

        output = input_dictionary
        model_output = {'resiliency_hours':4}  ##TO DO: hook up to a submodule later to get actual results

        if "ERROR" in model_output.keys():
            raise ImmediateHttpResponse(response=ResilienceCase.error_response(bundle.request, model_output))

        else:
            for k in outputs().keys():
                output[k]= model_output[k]

            output_obj = ResilienceCase(**output)
            output_obj.save()

        return output_obj, output