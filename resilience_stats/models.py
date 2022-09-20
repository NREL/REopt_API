# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
import sys
import logging
import copy
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from reo.models import ScenarioModel
from reo.exceptions import SaveToDatabase
log = logging.getLogger(__name__)

class BaseModel(object):

    @property
    def dict(self):
        """
        Serialize Django Model.__dict__
        NOTE: to get correct field types you must run self.clean_fields() first (eg. convert int to float)
        :return: dict
        """
        d = copy.deepcopy(self.__dict__)
        d.pop("_state", None)
        d.pop("id", None)
        d.pop("basemodel_ptr_id", None)
        d.pop("run_uuid", None)  # redundant with base_scenario
        return d

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        return obj
        
class ERPMeta(BaseModel, models.Model):

    run_uuid = models.UUIDField(unique=True)
    user_uuid = models.TextField(
        blank=True,
        default="",
        help_text="The assigned unique ID of a signed in REopt user."
    )
    job_type = models.TextField(
        default='developer.nrel.gov'
    )
    # status = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    reopt_version = models.TextField(
        blank=True,
        default="",
        help_text="Version number of the REopt Julia package that is used to calculate reliability."
    )

class ERPInputs(BaseModel, models.Model):

    meta = models.OneToOneField(
        ERPMeta,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="ERPInputs"
    )
    reopt_run_uuid = models.UUIDField(
        blank=True,
        null=True,
        help_text="The unique ID of a REopt optimization run from which to load inputs."
    )
    generator_operational_availability = models.FloatField(
        blank=True,
        default=0.9998,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Fraction of year generators not down for maintenance")
    )
    generator_failure_to_start = models.FloatField(
        blank=True,
        default=0.0066,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Chance of generator starting given outage")
    )
    generator_failure_to_run = models.FloatField(
        blank=True,
        default=0.00157,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Chance of generator failing in each hour of outage")
    )
    def num_generators_default():
        return list([1])
    num_generators = ArrayField(
        models.IntegerField(
            validators=[
                MinValueValidator(1)
            ]
        ),
        blank=True,
        default=num_generators_default,
        help_text=("Number of generators")
    )
    generator_size_kw = models.FloatField(
        blank=True,
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        help_text=("Backup generator capacity")
    )
    battery_size_kw = models.FloatField(
        blank=True,
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        help_text=("Battery kW power capacity")
    )
    battery_size_kwh = models.FloatField(
        blank=True,
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        help_text=("Battery kWh energy capacity")
    )
    starting_battery_soc_kwh = ArrayField(
        models.FloatField(
            validators=[
                MinValueValidator(0),
                MaxValueValidator(battery_size_kwh)
            ]
        ),
        blank=True,
        default=list,
        help_text=("Battery kWh state of charge when an outage begins, at each timestep. Must be hourly (8,760 samples).")
    )
    battery_charge_efficiency = models.FloatField(
        blank=True,
        default=0.948,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Efficiency of charging battery")
    )
    battery_discharge_efficiency = models.FloatField(
        blank=True,
        default=0.948,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Efficiency of discharging battery")
    )
    num_battery_bins = models.IntegerField(
        blank=True,
        default=100,
        validators=[
            MinValueValidator(1),
        ],
        help_text=("Number of bins for modeling battery state of charge")
    )
    pv_size_kw = models.FloatField(
        blank=True,
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        help_text=("PV system capacity")
    )
    #TODO: add _kw_per_kw_rated?
    pv_production_factor_series = ArrayField(
        models.FloatField(
            validators=[
                MinValueValidator(0),
                MaxValueValidator(1)
            ]
        ),
        blank=True,
        default=list,
        help_text=("PV system output at each timestep, normalized to PV system size. Must be hourly (8,760 samples).")
    )
    chp_size_kw = models.FloatField(
        blank=True,
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        help_text=("CHP system electric capacity")
    )
    max_outage_duration = models.IntegerField(
        blank=True,
        default=96,
        validators=[
            MinValueValidator(1),
        ],
        help_text=("Maximum outage duration modeled")
    )
    critical_loads_kw = ArrayField(
        models.FloatField(blank=True),
        help_text=("Critical load during an outage. Must be hourly (8,760 samples). All non-net load values must be greater than or equal to zero.")
    )

    
class ERPOutputs(BaseModel, models.Model):

    meta = models.OneToOneField(
        ERPMeta,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="ERPOutputs"
    )
    mean_marginal_duration_survival_probability = ArrayField(
        models.FloatField(blank=True),
        help_text=("The mean, calculated over outages starting at each hour of the year, of the marginal probability of surviving each hour of max_outage_duration.")
    )
    min_marginal_duration_survival_probability = ArrayField(
        models.FloatField(blank=True),
        help_text=("The minimum, calculated over outages starting at each hour of the year, of the marginal probability of surviving each hour of max_outage_duration.")
    )
    mean_cumulative_duration_survival_probability = ArrayField(
        models.FloatField(blank=True),
        help_text=("The mean, calculated over outages starting at each hour of the year, of the cumulative probability of surviving up to and including each hour of max_outage_duration.")
    )
    min_cumulative_duration_survival_probability = ArrayField(
        models.FloatField(blank=True),
        help_text=("The minimum, calculated over outages starting at each hour of the year, of the cumulative probability of surviving up to and including each hour of max_outage_duration.")
    )
    cumulative_outage_survival_probability = ArrayField(
        models.FloatField(blank=True),
        help_text=("The probability of surviving the full max_outage_duration, for outages starting at each hour of the year.")
    )
    mean_cumulative_outage_survival_probability = models.FloatField(
        blank=True,
        help_text=("The mean, calculated over outages starting at each hour of the year, of the probability of surviving the full max_outage_duration.")
    )

class ResilienceModel(models.Model):

    scenariomodel = models.OneToOneField(
        ScenarioModel,
        to_field='id',
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True
    )
    # WITH TECH
    resilience_by_timestep = ArrayField(models.FloatField(null=True), null=True)
    resilience_hours_min = models.FloatField(null=True)
    resilience_hours_max = models.FloatField(null=True)
    resilience_hours_avg = models.FloatField(null=True)
    outage_durations = ArrayField(models.FloatField(null=True), null=True)
    probs_of_surviving = ArrayField(models.FloatField(null=True), null=True)
    probs_of_surviving_by_month = ArrayField(ArrayField(models.FloatField(null=True), null=True), null=True)
    probs_of_surviving_by_hour_of_the_day = ArrayField(ArrayField(models.FloatField(null=True), null=True), null=True)
    # BAU
    resilience_by_timestep_bau = ArrayField(models.FloatField(null=True), null=True)
    resilience_hours_min_bau = models.FloatField(null=True)
    resilience_hours_max_bau = models.FloatField(null=True)
    resilience_hours_avg_bau = models.FloatField(null=True)
    outage_durations_bau = ArrayField(models.FloatField(null=True), null=True)
    probs_of_surviving_bau = ArrayField(models.FloatField(null=True), null=True)
    probs_of_surviving_by_month_bau = ArrayField(ArrayField(models.FloatField(null=True), null=True), null=True)
    probs_of_surviving_by_hour_of_the_day_bau = ArrayField(ArrayField(models.FloatField(null=True), null=True),
                                                           null=True)
    avoided_outage_costs_us_dollars = models.FloatField(null=True, blank=True)
    present_worth_factor = models.FloatField(null=True)
    avg_critical_load = models.FloatField(null=True)

    @classmethod
    def create(cls, scenariomodel, **kwargs):
        rm = cls(scenariomodel=scenariomodel, **kwargs)
        try:
            rm.save()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = SaveToDatabase(exc_type, exc_value.args[0], exc_traceback, task='resilience_model', run_uuid=scenariomodel.run_uuid)
            err.save_to_db()
            raise err
        return rm

def get_erp_input_dict_from_run_uuid(run_uuid:str):
    """
    Construct the input dict for REopt backup reliability
    """
    meta = ERPMeta.objects.select_related("ERPInputs").get(run_uuid=run_uuid)

    def filter_none_and_empty_array(d:dict):
        return {k: v for (k, v) in d.items() if v not in [None, [], {}]}

    d = dict()
    d = filter_none_and_empty_array(meta.ERPInputs.dict)
    d.pop('reopt_run_uuid',None) # Remove REopt run_uuid from inputs dict because it is not used by the REopt julia package
    d["user_uuid"] = meta.user_uuid # Add user_uuid for error handling in run_erp_task

    return d