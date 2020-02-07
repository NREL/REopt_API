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
# from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import *
from django.forms.models import model_to_dict
from picklefield.fields import PickledObjectField
from reo.nested_inputs import nested_input_definitions
import logging
log = logging.getLogger(__name__)
import sys
import traceback as tb
import warnings


class URDBError(models.Model):
    label = models.TextField(blank=True, default='')
    type = models.TextField(blank=True, default='')
    message = models.TextField(blank=True, default='')

    def save_to_db(self):
        try:
            self.save()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            message = 'Could not save URDBError {} for label {} error to the database - {} \n\n{}'.format(self.type,
                                                                                                          self.label,
                                                                                                          self.message,
                                                                                                          tb.format_tb(
                                                                                                              exc_traceback))
            warnings.warn(message)
            log.debug(message)


class ProfileModel(models.Model):
    run_uuid = models.UUIDField(unique=True)
    pre_setup_scenario_seconds = models.FloatField(null=True, blank=True)
    setup_scenario_seconds = models.FloatField(null=True, blank=True)
    reopt_seconds = models.FloatField(null=True, blank=True)
    reopt_bau_seconds = models.FloatField(null=True, blank=True)
    parse_run_outputs_seconds = models.FloatField(null=True, blank=True)

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()
        return obj


class ScenarioModel(models.Model):
    # Inputs
    # user = models.ForeignKey(User, null=True, blank=True)
    run_uuid = models.UUIDField(unique=True)
    api_version = models.TextField(null=True, blank=True, default='')
    user_uuid = models.TextField(null=True, blank=True)
    webtool_uuid = models.TextField(null=True, blank=True)
    job_type = models.TextField(null=True, blank=True)

    description = models.TextField(null=True, blank=True, default='')
    status = models.TextField(null=True, blank=True)
    timeout_seconds = models.IntegerField(default=295)
    time_steps_per_hour = models.IntegerField(default=8760)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()
        return obj


class SiteModel(models.Model):
    # Inputs
    run_uuid = models.UUIDField(unique=True)
    address = models.TextField(null=True, blank=True, default='')
    latitude = models.FloatField()
    longitude = models.FloatField()
    land_acres = models.FloatField(null=True, blank=True)
    roof_squarefeet = models.FloatField(null=True, blank=True)

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


class FinancialModel(models.Model):
    # Input
    run_uuid = models.UUIDField(unique=True)
    analysis_years = models.IntegerField()
    escalation_pct = models.FloatField()
    om_cost_escalation_pct = models.FloatField()
    offtaker_discount_pct = models.FloatField()
    offtaker_tax_pct = models.FloatField()
    value_of_lost_load_us_dollars_per_kwh = models.FloatField(null=True, blank=True)
    microgrid_upgrade_cost_pct = models.FloatField(null=True, blank=True)
    # owner_discount_pct = models.FloatField(null=True)
    # owner_tax_pct = models.FloatField(null=True)

    # Outputs
    lcc_us_dollars = models.FloatField(null=True, blank=True)
    lcc_bau_us_dollars = models.FloatField(null=True, blank=True)
    npv_us_dollars = models.FloatField(null=True, blank=True)
    net_capital_costs_plus_om_us_dollars = models.FloatField(null=True, blank=True)
    avoided_outage_costs_us_dollars = models.FloatField(null=True, blank=True)
    microgrid_upgrade_cost_us_dollars = models.FloatField(null=True, blank=True)
    net_capital_costs = models.FloatField(null=True, blank=True)
    net_om_us_dollars_bau = models.FloatField(null=True, blank=True)

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


class LoadProfileModel(models.Model):
    # Inputs
    run_uuid = models.UUIDField(unique=True)
    doe_reference_name = models.TextField(null=True, blank=True, default='')
    annual_kwh = models.FloatField(null=True, blank=True)
    year = models.IntegerField(default=2018)
    monthly_totals_kwh = ArrayField(models.FloatField(blank=True), default=list)
    loads_kw = ArrayField(models.FloatField(blank=True), default=list)
    critical_loads_kw = ArrayField(models.FloatField(blank=True), default=list)
    loads_kw_is_net = models.BooleanField(default=True)
    critical_loads_kw_is_net = models.BooleanField(default=False)
    outage_start_hour = models.IntegerField(null=True, blank=True)
    outage_end_hour = models.IntegerField(null=True, blank=True)
    critical_load_pct = models.FloatField()
    outage_is_major_event = models.BooleanField(default=True)

    #Outputs
    year_one_electric_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), default=list)
    critical_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), default=list)
    annual_calculated_kwh = models.FloatField(null=True, blank=True)
    sustain_hours = models.IntegerField(null=True, blank=True)
    resilience_check_flag = models.BooleanField(default=False)

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


class ElectricTariffModel(models.Model):
    # Inputs
    run_uuid = models.UUIDField(unique=True)
    urdb_utility_name = models.TextField(blank=True, default='')
    urdb_rate_name = models.TextField(blank=True, default='')
    urdb_label = models.TextField(blank=True, default='')
    blended_monthly_rates_us_dollars_per_kwh = ArrayField(models.FloatField(blank=True), default=list)
    blended_monthly_demand_charges_us_dollars_per_kw = ArrayField(models.FloatField(blank=True), default=list)
    blended_annual_rates_us_dollars_per_kwh = models.FloatField(blank=True, default=0, null=True)
    blended_annual_demand_charges_us_dollars_per_kw = models.FloatField(blank=True, default=0, null=True)
    net_metering_limit_kw = models.FloatField()
    interconnection_limit_kw = models.FloatField()
    wholesale_rate_us_dollars_per_kwh = ArrayField(models.FloatField(default=[0]))
    wholesale_rate_above_site_load_us_dollars_per_kwh = ArrayField(models.FloatField(default=[0]))
    urdb_response = PickledObjectField(null=True, editable=True)
    add_blended_rates_to_urdb_rate = models.BooleanField(null=False)

    # Ouptuts
    year_one_energy_cost_us_dollars = models.FloatField(null=True, blank=True)
    year_one_demand_cost_us_dollars = models.FloatField(null=True, blank=True)
    year_one_fixed_cost_us_dollars = models.FloatField(null=True, blank=True)
    year_one_min_charge_adder_us_dollars = models.FloatField(null=True, blank=True)
    year_one_energy_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    year_one_demand_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    year_one_fixed_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    year_one_min_charge_adder_bau_us_dollars = models.FloatField(null=True, blank=True)
    total_energy_cost_us_dollars = models.FloatField(null=True, blank=True)
    total_demand_cost_us_dollars = models.FloatField(null=True, blank=True)
    total_fixed_cost_us_dollars = models.FloatField(null=True, blank=True)
    total_min_charge_adder_us_dollars = models.FloatField(null=True, blank=True)
    total_energy_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    total_demand_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    total_fixed_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    total_export_benefit_us_dollars = models.FloatField(null=True, blank=True)
    total_min_charge_adder_bau_us_dollars = models.FloatField(null=True, blank=True)
    year_one_bill_us_dollars = models.FloatField(null=True, blank=True)
    year_one_bill_bau_us_dollars = models.FloatField(null=True, blank=True)
    year_one_export_benefit_us_dollars = models.FloatField(null=True, blank=True)
    year_one_energy_cost_series_us_dollars_per_kwh = ArrayField(models.FloatField(null=True, blank=True), null=True,
                                                                blank=True)
    year_one_demand_cost_series_us_dollars_per_kw = ArrayField(models.FloatField(null=True, blank=True), null=True,
                                                               blank=True)
    year_one_to_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_battery_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_energy_supplied_kwh = models.FloatField(null=True, blank=True)
    year_one_energy_supplied_kwh_bau = models.FloatField(null=True, blank=True)

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


class PVModel(models.Model):
    # Inputs
    run_uuid = models.UUIDField(unique=True)
    existing_kw = models.FloatField()
    min_kw = models.FloatField()
    max_kw = models.FloatField()
    installed_cost_us_dollars_per_kw = models.FloatField()
    om_cost_us_dollars_per_kw = models.FloatField()
    macrs_option_years = models.IntegerField()
    macrs_bonus_pct = models.FloatField()
    macrs_itc_reduction = models.FloatField()
    federal_itc_pct = models.FloatField()
    state_ibi_pct = models.FloatField()
    state_ibi_max_us_dollars = models.FloatField()
    utility_ibi_pct = models.FloatField()
    utility_ibi_max_us_dollars = models.FloatField()
    federal_rebate_us_dollars_per_kw = models.FloatField()
    state_rebate_us_dollars_per_kw = models.FloatField()
    state_rebate_max_us_dollars = models.FloatField()
    utility_rebate_us_dollars_per_kw = models.FloatField()
    utility_rebate_max_us_dollars = models.FloatField()
    pbi_us_dollars_per_kwh = models.FloatField()
    pbi_max_us_dollars = models.FloatField()
    pbi_years = models.FloatField()
    pbi_system_max_kw = models.FloatField()
    degradation_pct = models.FloatField(null=True, blank=True)
    azimuth = models.FloatField()
    losses = models.FloatField()
    array_type = models.IntegerField()
    module_type = models.IntegerField()
    gcr = models.FloatField()
    dc_ac_ratio = models.FloatField()
    inv_eff = models.FloatField()
    radius = models.FloatField()
    tilt = models.FloatField()

    # Outputs
    size_kw = models.FloatField(null=True, blank=True)
    station_latitude = models.FloatField(null=True, blank=True)
    station_longitude = models.FloatField(null=True, blank=True)
    station_distance_km = models.FloatField(null=True, blank=True)
    average_yearly_energy_produced_kwh = models.FloatField(null=True, blank=True)
    average_yearly_energy_produced_bau_kwh = models.FloatField(null=True, blank=True)
    average_yearly_energy_exported_kwh = models.FloatField(null=True, blank=True)
    year_one_energy_produced_kwh = models.FloatField(null=True, blank=True)
    year_one_power_production_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_battery_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_grid_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    existing_pv_om_cost_us_dollars = models.FloatField(null=True, blank=True)

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


class WindModel(models.Model):
    # Inputs
    run_uuid = models.UUIDField(unique=True)
    size_class = models.TextField(null=True, blank=True, default='')
    wind_meters_per_sec = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    wind_direction_degrees = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    temperature_celsius = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    pressure_atmospheres = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    min_kw = models.FloatField()
    max_kw = models.FloatField()
    installed_cost_us_dollars_per_kw = models.FloatField()
    om_cost_us_dollars_per_kw = models.FloatField()
    macrs_option_years = models.IntegerField()
    macrs_bonus_pct = models.FloatField()
    macrs_itc_reduction = models.FloatField()
    federal_itc_pct = models.FloatField()
    state_ibi_pct = models.FloatField()
    state_ibi_max_us_dollars = models.FloatField()
    utility_ibi_pct = models.FloatField()
    utility_ibi_max_us_dollars = models.FloatField()
    federal_rebate_us_dollars_per_kw = models.FloatField()
    state_rebate_us_dollars_per_kw = models.FloatField()
    state_rebate_max_us_dollars = models.FloatField()
    utility_rebate_us_dollars_per_kw = models.FloatField()
    utility_rebate_max_us_dollars = models.FloatField()
    pbi_us_dollars_per_kwh = models.FloatField()
    pbi_max_us_dollars = models.FloatField()
    pbi_years = models.FloatField()
    pbi_system_max_kw = models.FloatField()

    # Outputs
    size_kw = models.FloatField(null=True, blank=True)
    average_yearly_energy_produced_kwh = models.FloatField(null=True, blank=True)
    average_yearly_energy_exported_kwh = models.FloatField(null=True, blank=True)
    year_one_energy_produced_kwh = models.FloatField(null=True, blank=True)
    year_one_power_production_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_battery_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_grid_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


class StorageModel(models.Model):
    # Inputs
    run_uuid = models.UUIDField(unique=True)
    min_kw = models.FloatField()
    max_kw = models.FloatField()
    min_kwh = models.FloatField()
    max_kwh = models.FloatField()
    internal_efficiency_pct = models.FloatField()
    inverter_efficiency_pct = models.FloatField()
    rectifier_efficiency_pct = models.FloatField()
    soc_min_pct = models.FloatField()
    soc_init_pct = models.FloatField()
    canGridCharge = models.BooleanField()
    installed_cost_us_dollars_per_kw = models.FloatField()
    installed_cost_us_dollars_per_kwh = models.FloatField()
    replace_cost_us_dollars_per_kw = models.FloatField()
    replace_cost_us_dollars_per_kwh = models.FloatField()
    inverter_replacement_year = models.IntegerField()
    battery_replacement_year = models.IntegerField()
    macrs_option_years = models.IntegerField()
    macrs_bonus_pct = models.FloatField()
    macrs_itc_reduction = models.FloatField()
    total_itc_pct = models.FloatField()
    total_rebate_us_dollars_per_kw = models.IntegerField()

    # Outputs
    size_kw = models.FloatField(null=True, blank=True)
    size_kwh = models.FloatField(null=True, blank=True)
    year_one_to_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_grid_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_soc_series_pct = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


class GeneratorModel(models.Model):
        # Inputs
        run_uuid = models.UUIDField(unique=True)
        existing_kw = models.FloatField(null=True, blank=True, default=0)
        min_kw = models.FloatField(default=0)
        max_kw = models.FloatField(null=True, blank=True)
        installed_cost_us_dollars_per_kw = models.FloatField(null=True, blank=True,)
        om_cost_us_dollars_per_kw = models.FloatField(null=True, blank=True,)
        om_cost_us_dollars_per_kwh = models.FloatField(null=True, blank=True,)
        diesel_fuel_cost_us_dollars_per_gallon = models.FloatField(null=True, blank=True)
        fuel_slope_gal_per_kwh = models.FloatField(null=True, blank=True,)
        fuel_intercept_gal_per_hr = models.FloatField(null=True, blank=True,)
        fuel_avail_gal = models.FloatField(null=True, blank=True,)
        min_turn_down_pct = models.FloatField(null=True, blank=True)
        generator_only_runs_during_grid_outage = models.BooleanField(default=True)
        generator_sells_energy_back_to_grid = models.BooleanField(default=False)
        macrs_option_years = models.IntegerField(null=True, blank=True)
        macrs_bonus_pct = models.FloatField(null=True, blank=True)
        macrs_itc_reduction = models.FloatField(null=True, blank=True)
        federal_itc_pct = models.FloatField(null=True, blank=True)
        state_ibi_pct = models.FloatField(null=True, blank=True)
        state_ibi_max_us_dollars = models.FloatField(null=True, blank=True)
        utility_ibi_pct = models.FloatField(null=True, blank=True)
        utility_ibi_max_us_dollars = models.FloatField(null=True, blank=True)
        federal_rebate_us_dollars_per_kw = models.FloatField(null=True, blank=True)
        state_rebate_us_dollars_per_kw = models.FloatField(null=True, blank=True)
        state_rebate_max_us_dollars = models.FloatField(null=True, blank=True)
        utility_rebate_us_dollars_per_kw = models.FloatField(null=True, blank=True)
        utility_rebate_max_us_dollars = models.FloatField(null=True, blank=True)
        pbi_us_dollars_per_kwh = models.FloatField(null=True, blank=True)
        pbi_max_us_dollars = models.FloatField(null=True, blank=True)
        pbi_years = models.FloatField(null=True, blank=True)
        pbi_system_max_kw = models.FloatField(null=True, blank=True)

        # Outputs
        fuel_used_gal = models.FloatField(null=True, blank=True)
        fuel_used_gal_bau = models.FloatField(null=True, blank=True)
        size_kw = models.FloatField(null=True, blank=True)
        average_yearly_energy_produced_kwh = models.FloatField(null=True, blank=True)
        average_yearly_energy_exported_kwh = models.FloatField(null=True, blank=True)
        year_one_energy_produced_kwh = models.FloatField(null=True, blank=True)
        year_one_power_production_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True,
                                                         blank=True)
        year_one_to_battery_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
        year_one_to_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
        year_one_to_grid_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
        year_one_variable_om_cost_us_dollars = models.FloatField(null=True, blank=True)
        year_one_fuel_cost_us_dollars = models.FloatField(null=True, blank=True)
        total_variable_om_cost_us_dollars = models.FloatField(null=True, blank=True)
        total_fuel_cost_us_dollars = models.FloatField(null=True, blank=True)
        existing_gen_year_one_variable_om_cost_us_dollars = models.FloatField(null=True, blank=True)
        existing_gen_year_one_fuel_cost_us_dollars = models.FloatField(null=True, blank=True)
        existing_gen_total_variable_om_cost_us_dollars = models.FloatField(null=True, blank=True)
        existing_gen_total_fuel_cost_us_dollars = models.FloatField(null=True, blank=True)
        existing_gen_total_fixed_om_cost_us_dollars = models.FloatField(null=True, blank=True)

        @classmethod
        def create(cls, **kwargs):
            obj = cls(**kwargs)
            obj.save()

            return obj


class MessageModel(models.Model):
    """
    For Example:
    {"messages":{
                "warnings": "This is a warning message.",
                "error": "REopt had an error."
                }
    }
    """
    message_type = models.TextField(blank=True, default='')
    message = models.TextField(blank=True, default='')
    run_uuid = models.UUIDField(unique=False)
    description = models.TextField(blank=True, default='')

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


class BadPost(models.Model):
    run_uuid = models.UUIDField(unique=True)
    post = models.TextField()
    errors = models.TextField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            super(BadPost, self).save()
        except Exception as e:
            log.info("Database saving error: {}".format(e.args[0]))


def attribute_inputs(inputs):
    return {k: v for k, v in inputs.items() if k[0] == k[0].lower() and v is not None}


class ErrorModel(models.Model):
    task = models.TextField(blank=True, default='')
    name = models.TextField(blank=True, default='')
    run_uuid = models.TextField(blank=True, default='')
    user_uuid = models.TextField(blank=True, default='')
    message = models.TextField(blank=True, default='')
    traceback = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)


class ModelManager(object):

    def __init__(self):
        self.scenarioM = None
        self.siteM = None
        self.financialM = None
        self.load_profileM = None
        self.electric_tariffM = None
        self.pvM = None
        self.windM = None
        self.storageM = None
        self.generatorM = None
        self.profileM = None
        self.messagesM = None

    def create_and_save(self, data):
        """
        create and save models
        saves input json to db tables
        :param data: dict, constructed in api.py, mirrors reopt api response structure
        """
        d = data["inputs"]['Scenario']
        scenario_dict = data["outputs"]['Scenario'].copy()
        scenario_dict.update(d)

        self.scenarioM = ScenarioModel.create(**attribute_inputs(scenario_dict))
        self.profileM = ProfileModel.create(run_uuid=self.scenarioM.run_uuid,
                                            **attribute_inputs(scenario_dict['Profile']))
        self.siteM = SiteModel.create(run_uuid=self.scenarioM.run_uuid, **attribute_inputs(d['Site']))
        self.financialM = FinancialModel.create(run_uuid=self.scenarioM.run_uuid,
                                                **attribute_inputs(d['Site']['Financial']))
        self.load_profileM = LoadProfileModel.create(run_uuid=self.scenarioM.run_uuid,
                                                     **attribute_inputs(d['Site']['LoadProfile']))
        self.electric_tariffM = ElectricTariffModel.create(run_uuid=self.scenarioM.run_uuid,
                                                           **attribute_inputs(d['Site']['ElectricTariff']))
        self.pvM = PVModel.create(run_uuid=self.scenarioM.run_uuid, **attribute_inputs(d['Site']['PV']))
        self.windM = WindModel.create(run_uuid=self.scenarioM.run_uuid, **attribute_inputs(d['Site']['Wind']))
        self.storageM = StorageModel.create(run_uuid=self.scenarioM.run_uuid, **attribute_inputs(d['Site']['Storage']))
        self.generatorM = GeneratorModel.create(run_uuid=self.scenarioM.run_uuid, **attribute_inputs(d['Site']['Generator']))
        for message_type, message in data['messages'].items():
            MessageModel.create(run_uuid=self.scenarioM.run_uuid, message_type=message_type, message=message)

    @staticmethod
    def updateModel(modelName, modelData, run_uuid):
        eval(modelName).objects.filter(run_uuid=run_uuid).update(**attribute_inputs(modelData))

    @staticmethod
    def remove(run_uuid):
        """
        remove Scenario from database
        :param run_uuid: id of Scenario
        :return: None
        """
        ScenarioModel.objects.filter(run_uuid=run_uuid).delete()
        ProfileModel.objects.filter(run_uuid=run_uuid).delete()
        SiteModel.objects.filter(run_uuid=run_uuid).delete()
        FinancialModel.objects.filter(run_uuid=run_uuid).delete()
        LoadProfileModel.objects.filter(run_uuid=run_uuid).delete()
        ElectricTariffModel.objects.filter(run_uuid=run_uuid).delete()
        PVModel.objects.filter(run_uuid=run_uuid).delete()
        WindModel.objects.filter(run_uuid=run_uuid).delete()
        StorageModel.objects.filter(run_uuid=run_uuid).delete()
        GeneratorModel.objects.filter(run_uuid=run_uuid).delete()
        MessageModel.objects.filter(run_uuid=run_uuid).delete()
        ErrorModel.objects.filter(run_uuid=run_uuid).delete()

    @staticmethod
    def update(data, run_uuid):
        """
        save Scenario results in database
        :param data: dict, constructed in api.py, mirrors reopt api response structure
        :param model_ids: dict, optional, for use when updating existing models that have not been created in memory
        :return: None
        """
        d = data["outputs"]["Scenario"]
        ScenarioModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d))  # force_update=True
        ProfileModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Profile']))
        SiteModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']))
        FinancialModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['Financial']))
        LoadProfileModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['LoadProfile']))
        ElectricTariffModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['ElectricTariff']))
        PVModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['PV']))
        WindModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['Wind']))
        StorageModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['Storage']))
        GeneratorModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['Generator']))

        for message_type, message in data['messages'].items():
            if len(MessageModel.objects.filter(run_uuid=run_uuid, message=message)) > 0:
                # message already saved
                pass
            else:
                MessageModel.create(run_uuid=run_uuid, message_type=message_type, message=message)

    @staticmethod
    def update_scenario_and_messages(data, run_uuid):
        """
        save Scenario results in database
        :param data: dict, constructed in api.py, mirrors reopt api response structure
        :return: None
        """
        d = data["outputs"]["Scenario"]
        ScenarioModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d))
        for message_type, message in data['messages'].items():
            if len(MessageModel.objects.filter(run_uuid=run_uuid, message=message)) > 0:
                # message already saved
                pass
            else:
                MessageModel.create(run_uuid=run_uuid, message_type=message_type, message=message)

    @staticmethod
    def add_user_uuid(user_uuid, run_uuid):
        """
        update the user_uuid associated with a Scenario
        :param user_uuid: string
        :param run_uuid: string
        :return: None
        """
        d = {"user_uuid": user_uuid}
        ScenarioModel.objects.filter(run_uuid=run_uuid).update(**d)
        ErrorModel.objects.filter(run_uuid=run_uuid).update(**d)

    @staticmethod
    def make_response(run_uuid):
        """
        Reconstruct response dictionary from postgres tables (django models).
        NOTE: postgres column type UUID is not JSON serializable. Work-around is removing those columns and then
              adding back into outputs->Scenario as string.
        :param run_uuid:
        :return: nested dictionary matching nested_output_definitions
        """

        def remove_ids(d):
            del d['run_uuid']
            del d['id']
            return d

        def move_outs_to_ins(site_key, resp):

            resp['inputs']['Scenario']['Site'][site_key] = dict()

            for k in nested_input_definitions['Scenario']['Site'][site_key].keys():

                try:
                    resp['inputs']['Scenario']['Site'][site_key][k] = resp['outputs']['Scenario']['Site'][site_key][k]
                    # special handling for inputs that can be scalar or array,
                    # (which we have to make an array in database)
                    if isinstance(resp['inputs']['Scenario']['Site'][site_key][k], list):
                        if len(resp['inputs']['Scenario']['Site'][site_key][k]) == 1:
                            resp['inputs']['Scenario']['Site'][site_key][k] = \
                                resp['inputs']['Scenario']['Site'][site_key][k][0]
                    del resp['outputs']['Scenario']['Site'][site_key][k]
                except KeyError:  # known exception for k = urdb_response (user provided blended rates)
                    resp['inputs']['Scenario']['Site'][site_key][k] = None

        # add try/except for get fail / bad run_uuid
        site_keys = ['PV', 'Storage', 'Financial', 'LoadProfile', 'ElectricTariff', 'Generator', 'Wind']

        resp = dict()
        resp['outputs'] = dict()
        resp['outputs']['Scenario'] = dict()
        resp['outputs']['Scenario']['Profile'] = dict()
        resp['inputs'] = dict()
        resp['inputs']['Scenario'] = dict()
        resp['inputs']['Scenario']['Site'] = dict()
        resp['messages'] = dict()

        try:
            scenario_model = ScenarioModel.objects.get(run_uuid=run_uuid)
        except Exception as e:
            if isinstance(e, models.ObjectDoesNotExist):
                resp['messages']['error'] = "run_uuid {} not in database. "\
                                            "You may have hit the results endpoint too quickly after POST'ing scenario, "\
                                            "you may have a typo in your run_uuid, or the scenario was deleted.".format(run_uuid)
                resp['outputs']['Scenario']['status'] = 'error'
                return resp
            else:
                raise Exception
        scenario_data = remove_ids(model_to_dict(scenario_model))
        del scenario_data['job_type']
        resp['outputs']['Scenario'] = scenario_data
        resp['outputs']['Scenario']['run_uuid'] = str(run_uuid)
        resp['outputs']['Scenario']['Site'] = remove_ids(model_to_dict(SiteModel.objects.get(run_uuid=run_uuid)))
        resp['outputs']['Scenario']['Site']['Financial'] = remove_ids(
            model_to_dict(FinancialModel.objects.get(run_uuid=run_uuid)))
        resp['outputs']['Scenario']['Site']['LoadProfile'] = remove_ids(
            model_to_dict(LoadProfileModel.objects.get(run_uuid=run_uuid)))
        resp['outputs']['Scenario']['Site']['ElectricTariff'] = remove_ids(
            model_to_dict(ElectricTariffModel.objects.get(run_uuid=run_uuid)))
        resp['outputs']['Scenario']['Site']['PV'] = remove_ids(model_to_dict(PVModel.objects.get(run_uuid=run_uuid)))
        resp['outputs']['Scenario']['Site']['Storage'] = remove_ids(
            model_to_dict(StorageModel.objects.get(run_uuid=run_uuid)))
        resp['outputs']['Scenario']['Site']['Generator'] = remove_ids(
            model_to_dict(GeneratorModel.objects.get(run_uuid=run_uuid)))
        resp['outputs']['Scenario']['Site']['Wind'] = remove_ids(
            model_to_dict(WindModel.objects.get(run_uuid=run_uuid)))
        profile_data = ProfileModel.objects.filter(run_uuid=run_uuid)

        if len(profile_data) > 0:
            resp['outputs']['Scenario']['Profile'] = remove_ids(model_to_dict(profile_data[0]))

        for m in MessageModel.objects.filter(run_uuid=run_uuid).values('message_type', 'message'):
            resp['messages'][m['message_type']] = m['message']

        for scenario_key in nested_input_definitions['Scenario'].keys():
            if scenario_key.islower():
                resp['inputs']['Scenario'][scenario_key] = resp['outputs']['Scenario'][scenario_key]
                del resp['outputs']['Scenario'][scenario_key]

        for site_key in nested_input_definitions['Scenario']['Site'].keys():
            if site_key.islower():
                resp['inputs']['Scenario']['Site'][site_key] = resp['outputs']['Scenario']['Site'][site_key]
                del resp['outputs']['Scenario']['Site'][site_key]

            elif site_key in site_keys:

                move_outs_to_ins(site_key, resp=resp)

        if resp['inputs']['Scenario']['Site']['LoadProfile'].get('doe_reference_name') == '':
            del resp['inputs']['Scenario']['Site']['LoadProfile']['doe_reference_name']

        return resp
