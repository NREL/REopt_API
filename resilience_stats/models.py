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
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from reo.models import ScenarioModel
from reo.exceptions import SaveToDatabase
log = logging.getLogger(__name__)

class ERPInputs(models.Model):

    run_uuid = models.UUIDField(unique=True)
 
    generator_operational_availability = models.FloatField(
        default=0.9998,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Fraction of year generators not down for maintenance")
    )
    generator_failure_to_start = models.FloatField(
        default=0.0066,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Chance of generator starting given outage")
    )
    generator_failure_to_run = models.FloatField(
        default=0.00157,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Chance of generator failing in each hour of outage")
    )
    num_generators = models.IntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
        ],
        help_text=("Number of generators")
    )
    generator_size_kw = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        help_text=("Backup generator capacity")
    )
    battery_size_kw = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        help_text=("Battery kW power capacity")
    )
    battery_size_kwh = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        help_text=("Battery kWh energy capacity")
    )
    starting_battery_soc_kwh = ArrayField(
        models.FloatField(
            blank=True,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(batt_kwh)
            ]
        ),
        help_text=("Battery kWh state of charge when an outage begins, at each timestep. Must be hourly (8,760 samples).")
    )
    battery_charge_efficiency = models.FloatField(
        default=0.948,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Efficiency of charging battery")
    )
    battery_discharge_efficiency = models.FloatField(
        default=0.948,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Efficiency of discharging battery")
    )
    num_battery_bins = models.IntegerField(
        default=100,
        validators=[
            MinValueValidator(1),
        ],
        help_text=("Number of bins for modeling battery state of charge")
    )
    pv_size_kw = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        help_text=("PV system capacity")
    )
    pv_production_factor_series = ArrayField(
        models.FloatField(
            blank=True,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(1)
            ]
        ),
        help_text=("PV system output at each timestep, normalized to PV system size. Must be hourly (8,760 samples).")
    )
    chp_size_kw = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        help_text=("CHP system electric capacity")
    )
    chp_production_factor_series = ArrayField(
        models.FloatField(
            blank=True,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(1)
            ]
        ),
        help_text=("CHP system electric output at each timestep, normalized to CHP system size. Must be hourly (8,760 samples).")
    )
    max_outage_duration = models.IntegerField(
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

    
class ERPOutputs(models.Model):

    erp_inputs = models.OneToOneField(
        ERPInputs,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="ERPInputs"
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
