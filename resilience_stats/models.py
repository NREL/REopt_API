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
        d.pop("meta_id", None)
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
    reopt_run_uuid = models.UUIDField(
        blank=True,
        null=True,
        help_text="The unique ID of a REopt optimization run from which to load inputs."
    )
    job_type = models.TextField(
        default='developer.nrel.gov'
    )
    status = models.TextField(
        blank=True,
        default="",
        help_text="Status of the ERP job."

    )
    created = models.DateTimeField(auto_now_add=True)
    reopt_version = models.TextField(
        blank=True,
        default="",
        help_text="Version number of the REopt Julia package that is used to calculate reliability."
    )

# class ERPGeneratorBaseModel(BaseModel, models.Model):
#     @property
#     def dict(self):
#         """
#         Serialize Django Model.__dict__
#         NOTE: to get correct field types you must run self.clean_fields() first (eg. convert int to float)
#         :return: dict
#         """
#         d1 = self.__dict__
#         d2 = dict()
#         for (from_key, to_key) in [
#                                     ("operational_availability","generator_operational_availability"),
#                                     ("failure_to_start","generator_failure_to_start"),
#                                     ("failure_to_run","generator_failure_to_run"),
#                                     ("num_generators","num_generators"),
#                                     ("size_kw","generator_size_kw"),
#                                     ("fuel_avail_gal","fuel_avail_gal"),
#                                     ("fuel_intercept","generator_fuel_intercept"),
#                                     ("fuel_avail_gal_is_per_generator","fuel_avail_gal_is_per_generator"),
#                                     ("burn_rate_fuel_per_kwh","generator_burn_rate_fuel_per_kwh"),
#                                 ]:
#             d2[to_key] = d1[from_key]
#         return d2

class ERPGeneratorInputs(BaseModel, models.Model):
    key = "Generator"
    meta = models.OneToOneField(
        ERPMeta,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="ERPGeneratorInputs"
    )
    operational_availability = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        default=0.9998, 
        blank=True,
        help_text=("Fraction of year generators not down for maintenance")
    )
    failure_to_start = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        default=0.0066,
        blank=True,
        help_text=("Chance of generator starting when an outage occurs")
    )
    failure_to_run = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        default=0.00157,
        blank=True,
        help_text=("Chance of generator failing in each hour of outage")
    )
    num_generators = models.IntegerField(
        validators=[
            MinValueValidator(1)
        ],
        blank=True,
        default=1,
        help_text=("Number of generator units")
    )
    size_kw = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        default=0.0,
        help_text=("Generator unit capacity")
    )
    fuel_avail_gal = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        default=1.0e9,
        help_text=("Amount of diesel fuel available, either for all generators or per generator depending on value of fuel_avail_gal_is_per_generator.")
    )
    fuel_avail_gal_is_per_generator = models.BooleanField(
        default=False,
        blank=True,
        help_text=("Whether fuel_avail_gal is per generator or per generator type")
    )
    electric_efficiency_half_load = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0)
        ],
        blank=True,
        null=True,
        help_text=("Electric efficiency of generator running at half load.electric_efficiency_full_load")
    )
    electric_efficiency_full_load = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0)
        ],
        blank=True,
        default=0.34,
        help_text=("Electric efficiency of generator running at full load.")
    )

    def clean(self):
        if not self.electric_efficiency_half_load:
            self.electric_efficiency_half_load = self.electric_efficiency_full_load

class ERPPrimeGeneratorInputs(BaseModel, models.Model):
    key = "PrimeGenerator"
    meta = models.OneToOneField(
        ERPMeta,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="ERPPrimeGeneratorInputs"
    )
    is_chp = models.BooleanField(
        default=False,
        blank=True,
        help_text=("Whether prime generator system is CHP")
    )
    PRIME_MOVER = models.TextChoices('PRIME_MOVER', (
        "recip_engine",
        "micro_turbine",
        "combustion_turbine",
        "fuel_cell"
    ))
    prime_mover = models.TextField(
        default="recip_engine",
        choices=PRIME_MOVER.choices,
        help_text="Prime generator/CHP prime mover, one of recip_engine, micro_turbine, combustion_turbine, fuel_cell"
    )
    operational_availability = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text=("Fraction of year CHP units are not down for maintenance")
    )
    failure_to_start = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text=("Chance of CHP unit starting when an outage occurs")
    )
    failure_to_run = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text=("Chance of CHP unit failing in each hour of outage")
    )
    num_generators = models.IntegerField(
        validators=[
            MinValueValidator(1)
        ],
        blank=True,
        default=1,
        help_text=("Number of CHP units")
    )
    size_kw = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        default=0.0,
        help_text=("CHP unit electric capacity")
    )
    electric_efficiency_half_load = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0)
        ],
        blank=True,
        null=True,
        help_text=("Electric efficiency of CHP unit running at half load.electric_efficiency_full_load")
    )
    electric_efficiency_full_load = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0)
        ],
        default=0.34,
        help_text=("Electric efficiency of CHP unit running at full load.")
    )

    def clean(self):
        if not self.electric_efficiency_half_load:
            self.electric_efficiency_half_load = self.electric_efficiency_full_load


class ERPElectricStorageInputs(BaseModel, models.Model):
    key = "ElectricStorage"
    meta = models.OneToOneField(
        ERPMeta,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="ERPElectricStorageInputs"
    )
    operational_availability = models.FloatField(
        blank=True,
        default=1.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0)
        ],
        help_text=("Fraction of year battery system not down for maintenance")
    )
    size_kw = models.FloatField(
        blank=True,
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        help_text=("Battery kW power capacity")
    )
    size_kwh = models.FloatField(
        blank=True,
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        help_text=("Battery kWh energy capacity")
    )
    starting_soc_series_fraction = ArrayField(
        models.FloatField(
            validators=[
                MinValueValidator(0)
            ]
        ),
        blank=True,
        default=list,
        help_text=("Battery state of charge fraction when an outage begins, at each timestep. Must be hourly (8,760 samples).")
    )
    charge_efficiency = models.FloatField(
        blank=True,
        default=0.948,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Efficiency of charging battery")
    )
    discharge_efficiency = models.FloatField(
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

    # @property
    # def dict(self):
    #     """
    #     Serialize Django Model.__dict__
    #     NOTE: to get correct field types you must run self.clean_fields() first (eg. convert int to float)
    #     :return: dict
    #     """
    #     d1 = self.__dict__
    #     d2 = dict()
    #     for (from_key, to_key) in [
    #                                 ("operational_availability","battery_operational_availability"),
    #                                 ("size_kw","battery_size_kw"),
    #                                 ("size_kwh","battery_size_kwh"),
    #                                 ("starting_soc_series_fraction","battery_starting_soc_series_fraction"),
    #                                 ("charge_efficiency","battery_charge_efficiency"),
    #                                 ("charge_disefficiency","battery_discharge_efficiency"),
    #                                 ("num_battery_bins","num_battery_bins"),
    #                             ]:
    #         d2[to_key] = d1[from_key]
    #     return d2

class ERPPVInputs(BaseModel, models.Model):
    key = "PV"
    meta = models.OneToOneField(
        ERPMeta,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="ERPPVInputs"
    )    
    operational_availability = models.FloatField(
        blank=True,
        default=1.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0)
        ],
        help_text=("Fraction of year PV system not down for maintenance")
    )
    size_kw = models.FloatField(
        blank=True,
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        help_text=("PV system capacity")
    )
    #TODO: add _kw_per_kw_rated?
    production_factor_series = ArrayField(
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

    # @property
    # def dict(self):
    #     """
    #     Serialize Django Model.__dict__
    #     NOTE: to get correct field types you must run self.clean_fields() first (eg. convert int to float)
    #     :return: dict
    #     """
    #     d1 = self.__dict__
    #     d2 = dict()
    #     for (from_key, to_key) in [
    #                                 ("operational_availability","pv_operational_availability"),
    #                                 ("size_kw","pv_size_kw"),
    #                                 ("production_factor_series","pv_production_factor_series")
    #                             ]:
    #         d2[to_key] = d1[from_key]
    #     return d2

class ERPOutageInputs(BaseModel, models.Model):
    key = "Outage"
    meta = models.OneToOneField(
        ERPMeta,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="ERPOutageInputs"
    )
    max_outage_duration = models.IntegerField(
        blank=True,
        default=336,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(672),
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
    unlimited_fuel_mean_cumulative_survival_by_duration = ArrayField(
        models.FloatField(blank=True),
        blank=True,
        default=list,
        help_text=("The mean, calculated over outages starting at each hour of the year, of the probability of surviving up to and including each hour of max_outage_duration, if generator fuel is unlimited.")
    )
    unlimited_fuel_min_cumulative_survival_by_duration = ArrayField(
        models.FloatField(blank=True),
        blank=True,
        default=list,
        help_text=("The minimum, calculated over outages starting at each hour of the year, of the probability of surviving up to and including each hour of max_outage_duration, if generator fuel is unlimited.")
    )
    unlimited_fuel_cumulative_outage_survival_final_time_step = ArrayField(
        models.FloatField(blank=True),
        blank=True,
        default=list,
        help_text=("The probability of surviving the full max_outage_duration, for outages starting at each hour of the year, if generator fuel is unlimited.")
    )
    mean_fuel_survival_by_duration = ArrayField(
        models.FloatField(blank=True),
        blank=True,
        default=list,
        help_text=("The probability, averaged over outages starting at each hour of the year, of having sufficient fuel to survive up to and including each hour of max_outage_duration.")
    )
    fuel_outage_survival_final_time_step = ArrayField(
        models.IntegerField(blank=True),
        blank=True,
        default=list,
        help_text=("Whether there is sufficient fuel to survive the full max_outage_duration, for outages starting at each hour of the year. A 1 means true, a 0 means false.")
    )
    mean_cumulative_survival_by_duration = ArrayField(
        models.FloatField(blank=True),
        blank=True,
        default=list,
        help_text=("The mean, calculated over outages starting at each hour of the year, of the probability of surviving up to and including each hour of max_outage_duration.")
    )
    min_cumulative_survival_by_duration = ArrayField(
        models.FloatField(blank=True),
        blank=True,
        default=list,
        help_text=("The minimum, calculated over outages starting at each hour of the year, of the probability of surviving up to and including each hour of max_outage_duration.")
    )
    cumulative_outage_survival_final_time_step = ArrayField(
        models.FloatField(blank=True),
        blank=True,
        default=list,
        help_text=("The probability of surviving the full max_outage_duration, for outages starting at each hour of the year.")
    )
    mean_cumulative_outage_survival_final_time_step = models.FloatField(
        null=True,
        blank=True,
        help_text=("The mean, calculated over outages starting at each hour of the year, of the probability of surviving the full max_outage_duration.")
    )
    monthly_cumulative_outage_survival_final_time_step = ArrayField(
        models.FloatField(blank=True),
        blank=True,
        default=list,
        help_text=("The monthly means, calculated over outages starting at each hour of the month, of the probability of surviving the full max_outage_duration.")
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
    meta = ERPMeta.objects.select_related("ERPOutageInputs").get(run_uuid=run_uuid)

    def filter_none_and_empty_array(d:dict):
        return {k: v for (k, v) in d.items() if v not in [None, [], {}]}

    def add_tech_prefixes(d:dict, prefix):
        keys_to_add_tech_prefix = {
                                    "operational_availability",
                                    "failure_to_start",
                                    "failure_to_run",
                                    "size_kw",
                                    "fuel_intercept_per_hr",
                                    "fuel_burn_rate_per_kwh",
                                    "operational_availability",
                                    "size_kw",
                                    "size_kwh",
                                    "starting_soc_series_fraction",
                                    "charge_efficiency",
                                    "charge_disefficiency",
                                    "operational_availability",
                                    "size_kw",
                                    "production_factor_series",
                                }
        return {(prefix + "_" + k if k in keys_to_add_tech_prefix else k): v for (k, v) in d.items()}
    
    def merge_generator_inputs(gen_dicts:list):
        #assumes gen_dicts not empty and all dicts in it have all same keys
        return {k: [gen_type[k] for gen_type in gen_dicts] for k in gen_dicts[0].keys()}

    d = dict()
    d["user_uuid"] = meta.user_uuid # Add user_uuid for error handling in run_erp_task
    d.update(filter_none_and_empty_array(meta.ERPOutageInputs.dict))
    try:
        d.update(add_tech_prefixes(filter_none_and_empty_array(meta.ERPElectricStorageInputs.dict),"battery"))
    except: pass
    try:
        d.update(add_tech_prefixes(filter_none_and_empty_array(meta.ERPPVInputs.dict),"pv"))
    except: pass
    gen_dicts = []
    try: 
        gen = meta.ERPGeneratorInputs.dict

        # Temp conversions until extend input structure changes to julia
        # convert efficiency to slope/intercept in gen dict
        KWH_PER_GAL_DIESEL = 40.7
        fuel_burn_full_load_kwht = 1.0 / gen.pop("electric_efficiency_full_load")  # [kWe_rated/(kWhe/kWht)]
        fuel_burn_half_load_kwht = 0.5 / gen.pop("electric_efficiency_half_load")  # [kWe_rated/(kWhe/kWht)]
        fuel_slope_kwht_per_kwhe = (fuel_burn_full_load_kwht - fuel_burn_half_load_kwht) / (1.0 - 0.5)  # [kWht/kWhe]
        fuel_intercept_kwht_per_hr = fuel_burn_full_load_kwht - fuel_slope_kwht_per_kwhe * 1.0  # [kWht/hr]
        gen["fuel_burn_rate_per_kwh"] = fuel_slope_kwht_per_kwhe / KWH_PER_GAL_DIESEL # [gal/kWhe]
        gen["fuel_intercept_per_hr"] = fuel_intercept_kwht_per_hr / KWH_PER_GAL_DIESEL # [gal/hr]
        # change fuel_avail_gal to fuel_limit
        gen["fuel_limit"] = gen.pop("fuel_avail_gal")
    
        gen_dicts += gen
    except AttributeError: pass
    try: 
        gen = meta.ERPPrimeGeneratorInputs.dict
        gen.pop("prime_mover")

        # Temp conversions until extend input structure changes to julia
        # convert efficiency to slope/intercept in chp dict
        fuel_burn_full_load = 1.0 / gen.pop("electric_efficiency_full_load")
        fuel_burn_half_load = 0.5 / gen.pop("electric_efficiency_half_load")
        gen["fuel_burn_rate_per_kwh"] = (fuel_burn_full_load - fuel_burn_half_load) / (1.0 - 0.5)  # [kWht/kWhe]
        gen["fuel_intercept_per_hr"] = fuel_burn_full_load - gen["fuel_burn_rate_per_kwh"] * 1.0  # [kWht/hr]
        # add fuel_limit
        gen["fuel_limit"] = 1e9
    
        gen_dicts += gen
    except AttributeError: pass
    if gen_dicts != []:
        d.update(filter_none_and_empty_array(merge_generator_inputs(gen_dicts)))

    # TODO: do this instead once extend input structure changes to julia (and do conversion of effic to slope/intercept in julia using existing util function)
    # d["Generator"] = filter_none_and_empty_array(meta.ERPGeneratorInputs.dict)
    # d["PrimeGenerator"] = filter_none_and_empty_array(meta.ERPPrimeGeneratorInputs.dict)
    # d["ElectricStorage"] = filter_none_and_empty_array(meta.ERPElectricStorageInputs.dict)
    # d["PV"] = filter_none_and_empty_array(meta.ERPPVInputs.dict)
    # d["Outage"] = filter_none_and_empty_array(meta.ERPOutageInputs.dict)

    return d