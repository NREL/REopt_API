from django.db import models
from  django.contrib.postgres.fields import *
from api_definitions import *
import json
from picklefield.fields import PickledObjectField
from library import *

# Create your models here.
class RunInput(models.Model):
    user_id = models.TextField(blank=True,default='')
    api_version = models.TextField(blank=True, default='',null=False)

    # Required
    analysis_period = models.IntegerField(null=True,blank=True)
    latitude = models.FloatField(null=True,blank=True)
    longitude = models.FloatField(null=True, blank=True)
    pv_cost = models.FloatField(null=True,blank=True)
    pv_om = models.FloatField(null=True,blank=True)
    batt_cost_kw = models.FloatField(null=True,blank=True)
    batt_cost_kwh = models.FloatField(null=True,blank=True)

    owner_discount_rate = models.FloatField(null=True,blank=True)
    offtaker_discount_rate = models.FloatField(null=True,blank=True)

    blended_utility_rate = ArrayField(models.TextField(blank=True),null=True,blank=True,default=[])
    demand_charge =  ArrayField(models.TextField(blank=True),null=True,blank=True,default=[])
    urdb_rate =  PickledObjectField(null=True)

    # Not Required
    load_profile_name  = models.TextField(null=True,blank=True,default='')
    load_size = models.FloatField(null=True,blank=True)
    load_8760_kw =  ArrayField(models.TextField(blank=True),null=True,blank=True,default=[])
    load_monthly_kwh =  ArrayField(models.TextField(blank=True),null=True,blank=True,default=[])
    utility_name = models.TextField(blank=True,default='')
    rate_name = models.TextField(blank=True,default='')
    rate_degradation = models.FloatField(null=True,blank=True)

    rate_inflation = models.FloatField(null=True,blank=True)
    rate_escalation = models.FloatField(null=True,blank=True)

    offtaker_tax_rate = models.FloatField(null=True,blank=True)
    owner_tax_rate = models.FloatField(null=True,blank=True)

    rate_itc = models.FloatField(null=True,blank=True)

    batt_replacement_cost_kw = models.FloatField(null=True,blank=True)
    batt_replacement_cost_kwh = models.FloatField(null=True,blank=True)
    batt_replacement_year = models.IntegerField(null=True,blank=True)

    flag_macrs =  models.NullBooleanField(blank=True)
    flag_itc =  models.NullBooleanField(blank=True)
    flag_bonus =  models.NullBooleanField(blank=True)
    flag_replace_batt =  models.NullBooleanField(blank=True)

    macrs_years = models.IntegerField(null=True,blank=True)
    macrs_itc_reduction = models.FloatField(null=True,blank=True)
    bonus_fraction = models.FloatField(null=True,blank=True)

    dataset = models.TextField(blank=True,default='')
    inv_eff = models.FloatField(null=True,blank=True)
    dc_ac_ratio = models.FloatField(null=True,blank=True)
    azimuth = models.FloatField(null=True,blank=True)
    system_capacity = models.FloatField(null=True,blank=True)
    array_type = models.IntegerField(null=True,blank=True)
    module_type = models.IntegerField(null=True,blank=True)
    timeframe = models.TextField(blank=True,default='')
    losses = models.FloatField(null=True,blank=True)
    radius = models.FloatField(null=True,blank=True)
    tilt = models.FloatField(null=True, blank=True)
    gcr = models.FloatField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    def create_output(self, fields):
        response_inputs = {f:getattr(self,f) for f in fields}

        run_set = DatLibrary(self.id, response_inputs)

        # Run Optimization
        run_set.run()
        output_dictionary = run_set.run()
        output_dictionary['api_version'] = self.api_version 

        result = RunOutput(**output_dictionary)
        result.save()

        return result

class RunOutput(models.Model):
    run_input_id = models.IntegerField(null=False)
    user_id = models.TextField(blank=True, default='')
    api_version = models.TextField(blank=True, default='')

    # Required
    analysis_period = models.IntegerField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    pv_cost = models.FloatField(null=True, blank=True)
    pv_om = models.FloatField(null=True, blank=True)
    batt_cost_kw = models.FloatField(null=True, blank=True)
    batt_cost_kwh = models.FloatField(null=True, blank=True)

    owner_discount_rate = models.FloatField(null=True, blank=True)
    offtaker_discount_rate = models.FloatField(null=True, blank=True)

    blended_utility_rate =   ArrayField(models.TextField(blank=True),null=True,blank=True,default=[])
    demand_charge =  ArrayField(models.TextField(blank=True),null=True,blank=True,default=[])
    urdb_rate = PickledObjectField(null=True)

    # Not Required
    load_profile_name = models.TextField(null=True,blank=True,default='')
    load_size = models.FloatField(null=True, blank=True)
    load_8760_kw =  ArrayField(models.TextField(blank=True),null=True,blank=True,default=[])
    load_monthly_kwh =  ArrayField(models.TextField(blank=True),null=True,blank=True,default=[])
    utility_name = models.TextField(blank=True,default='')
    rate_name = models.TextField(blank=True,default='')
    rate_degradation = models.FloatField(null=True, blank=True)

    rate_inflation = models.FloatField(null=True, blank=True)
    rate_escalation = models.FloatField(null=True, blank=True)
    offtaker_tax_rate = models.FloatField(null=True, blank=True)
    owner_tax_rate = models.FloatField(null=True, blank=True)
    rate_itc = models.FloatField(null=True, blank=True)

    batt_replacement_cost_kw = models.FloatField(null=True, blank=True)
    batt_replacement_cost_kwh = models.FloatField(null=True, blank=True)
    batt_replacement_year = models.IntegerField(null=True, blank=True)

    flag_macrs = models.NullBooleanField(blank=True)
    flag_itc =  models.NullBooleanField(blank=True)
    flag_bonus =  models.NullBooleanField(blank=True)
    flag_replace_batt = models.NullBooleanField(blank=True)

    macrs_years = models.IntegerField(null=True, blank=True)
    macrs_itc_reduction = models.FloatField(null=True, blank=True)
    bonus_fraction = models.FloatField(null=True, blank=True)

    dataset = models.TextField(blank=True,default='')
    inv_eff = models.FloatField(null=True, blank=True)
    dc_ac_ratio = models.FloatField(null=True, blank=True)
    azimuth = models.FloatField(null=True, blank=True)
    system_capacity = models.FloatField(null=True, blank=True)
    array_type = models.IntegerField(null=True, blank=True)
    module_type = models.IntegerField(null=True, blank=True)
    timeframe = models.TextField(blank=True,default='')
    losses = models.FloatField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)
    tilt = models.FloatField(null=True, blank=True)
    gcr = models.FloatField(null=True, blank=True)

    lcc = models.FloatField(null=True, blank=True)
    npv = models.FloatField(null=True, blank=True)
    utility_kwh = models.FloatField(null=True, blank=True)
    pv_kw = models.FloatField(null=True, blank=True)
    batt_kw = models.FloatField(null=True, blank=True)
    batt_kwh = models.FloatField(null=True, blank=True)

    created =  models.DateTimeField(auto_now_add=True)

    def to_dictionary(self):
        output = {'run_input_id': self.run_input_id,
                  'api_version': self.api_version}

        for k in inputs(full_list=True).keys() + outputs().keys():
            if hasattr(self, k):
                output[k] = getattr(self, k)
            else:
                output[k] = 0
        return output
