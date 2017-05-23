from django.db import models
from django.contrib.postgres.fields import *
from tastypie.exceptions import ImmediateHttpResponse
from outage_simulator import simulate_outage

from api_definitions import outputs


class ResilienceCase(models.Model):

    #Inputs
    pv_kw = models.FloatField(null=True, blank=True)
    batt_kw = models.FloatField(null=True, blank=True)
    batt_kwh = models.FloatField(null=True, blank=True)
    load = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    prod_factor = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    init_soc = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    crit_load_factor = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    batt_roundtrip_efficiency = models.FloatField(null=True, blank=True)
    api_version = models.TextField(blank=True, default='', null=False)

    #Outputs
    r_list = models.FloatField(blank=True, null=True)
    r_min = models.FloatField(blank=True, null=True)
    r_max = models.FloatField(blank=True, null=True)
    r_avg = models.FloatField(blank=True, null=True)

    @staticmethod
    def run(input_dictionary, bundle):

        output = input_dictionary
        model_output = simulate_outage(input_dictionary)  ##TO DO: hook up to a submodule later to get actual results

        if "ERROR" in model_output.keys():
            raise ImmediateHttpResponse(response=ResilienceCase.error_response(bundle.request, model_output))

        else:
            for k in outputs().keys():
                output[k] = model_output[k]

            output_obj = ResilienceCase(**output)
            output_obj.save()

        return output_obj, output