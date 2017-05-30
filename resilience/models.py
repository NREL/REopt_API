from django.db import models
from django.contrib.postgres.fields import *
from tastypie.exceptions import ImmediateHttpResponse
from outage_simulator import simulate_outage
from urls import get_current_api
from api_definitions import inputs


class ResilienceCase(models.Model):

    #Inputs
    pv_kw = models.FloatField(null=True, blank=True)
    batt_kw = models.FloatField(null=True, blank=True)
    batt_kwh = models.FloatField(null=True, blank=True)
    load = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    prod_factor = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    init_soc = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    crit_load_factor = models.FloatField(null=True, blank=True)
    batt_roundtrip_efficiency = models.FloatField(null=True, blank=True)
    api_version = models.TextField(blank=True, default='', null=False)

    #Outputs
    r_list = ArrayField(models.FloatField(blank=True, null=True), null=True, blank=True, default=[])
    r_min = models.FloatField(blank=True, null=True)
    r_max = models.FloatField(blank=True, null=True)
    r_avg = models.FloatField(blank=True, null=True)

    @staticmethod
    def run(bundle):
        
        data = dict({k: bundle.data.get(k) for k in inputs(full_list=True).keys() if k in bundle.data.keys() and bundle.data.get(k) is not None })

        model_results = simulate_outage(**data)
        
        if "ERROR" in model_results.keys():
            raise ImmediateHttpResponse(response=ResilienceCase.error_response(bundle.request, model_results))

        else:

            for k in model_results.keys():
                data[k] = model_results[k]
            
            data['api_version'] = get_current_api()
            
            output_obj = ResilienceCase(**data)
            output_obj.save()

        return output_obj