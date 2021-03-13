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
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
import copy
import sys
import traceback as tb
import warnings
import logging
log = logging.getLogger(__name__)
"""
Can we use:
django.db.models.Model
for all that nested_inputs provides, and some validation? YES!

https://docs.djangoproject.com/en/3.1/ref/models/fields/#validators

max/min   https://docs.djangoproject.com/en/3.1/ref/validators/#maxvaluevalidator
weight = models.FloatField(
    validators=[MinValueValidator(0.9), MaxValueValidator(58)],
)

type Field type

default https://docs.djangoproject.com/en/3.1/ref/models/fields/#default 

required https://docs.djangoproject.com/en/3.1/ref/models/fields/#blank

restrict_to https://docs.djangoproject.com/en/3.1/ref/models/fields/#choices

description https://docs.djangoproject.com/en/3.1/ref/models/fields/#help-text


Define our own clean method for each model:
https://docs.djangoproject.com/en/3.1/ref/models/instances/#django.db.models.Model.clean

https://docs.djangoproject.com/en/3.1/ref/models/fields/#error-messages


https://github.com/django/django/blob/876dc0c1a7dbf569782eb64f62f339c1daeb75e0/django/db/models/base.py#L1256
# Skip validation for empty fields with blank=True. The developer
# is responsible for making sure they have a valid value.
-> implies that we should NOT have blank=True for required inputs


Avoid using null on string-based fields such as CharField and TextField.
https://stackoverflow.com/questions/8609192/what-is-the-difference-between-null-true-and-blank-true-in-django

Guidance:
- start all Model fields with required fields (default value of blank is False)
- TextField and CharField should not have null=True


Input and Results models
test type validation for multiple fields, need to override clean_fields to go through all fields before rasing ValidationError?

    def clean_fields(self, exclude=None):
        Clean all fields and raise a ValidationError containing a dict
        of all validation errors if any occur.
        if exclude is None:
            exclude = []

        errors = {}
        for f in self._meta.fields:
            if f.name in exclude:
                continue
            # Skip validation for empty fields with blank=True. The developer
            # is responsible for making sure they have a valid value.
            raw_value = getattr(self, f.attname)
            if f.blank and raw_value in f.empty_values:
                continue
            try:
                setattr(self, f.attname, f.clean(raw_value, self))
            except ValidationError as e:
                errors[f.name] = e.error_list

        if errors:
            raise ValidationError(errors)
            
"""


def at_least_one_set(model, possible_sets):
    case = False
    for list_of_keys in possible_sets:
        if all(model.get(key) not in [None, ""] for key in list_of_keys):
            case = True
            break
    return case


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
        d.pop("run_uuid", None)
        return d

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        return obj


class Scenario(BaseModel, models.Model):
    """
    All the values specific to API (and not used in Julia package)
    """
    name = "Scenario"

    run_uuid = models.UUIDField(unique=True)
    api_version = models.IntegerField(default=2)
    user_uuid = models.TextField(
        null=True,
        blank=True,
        help_text="The assigned unique ID of a signed in REopt user."
    )
    webtool_uuid = models.TextField(
        null=True,
        blank=True,
        help_text=("The unique ID of a scenario created by the REopt Lite Webtool. Note that this ID can be shared by "
                   "several REopt Lite API Scenarios (for example when users select a 'Resilience' analysis more than "
                   "one REopt API Scenario is created).")
    )
    job_type = models.TextField(
        default='developer.nrel.gov'
    )
    description = models.TextField(blank=True)
    status = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)


class OptimizationInputs(BaseModel, models.Model):
    name = "Optimization"

    run_uuid = models.UUIDField(unique=True)
    timeout_seconds = models.IntegerField(
        default=420,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(420)
        ],
        help_text="The number of seconds allowed before the optimization times out."
    )
    time_steps_per_hour = models.IntegerField(
        default=1,
        choices=models.IntegerChoices("TIME_STEP_CHOICES", ("1 2 4")).choices,
        help_text="The number of time steps per hour in the REopt model."
    )
    optimality_tolerance = models.FloatField(
        default=0.001,
        validators=[
            MinValueValidator(1.0e-5),
            MaxValueValidator(10)
        ],
        help_text=("The threshold for the difference between the solution's objective value and the best possible "
                   "value at which the solver terminates")
    )
    # use_decomposition_model = models.BooleanField(null=True, blank=True)
    # optimality_tolerance_decomp_subproblem = models.FloatField(null=True, blank=True)
    # timeout_decomp_subproblem_seconds = models.IntegerField(null=True, blank=True)
    # add_soc_incentive = models.BooleanField(null=True, blank=True)


class SiteInputs(BaseModel, models.Model):
    name = "Site"

    run_uuid = models.UUIDField(unique=True)
    latitude = models.FloatField(
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )
    longitude = models.FloatField(
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )
    address = models.TextField(
        blank=True,
        help_text="A user defined address as optional metadata (street address, city, state or zip code)"
    )
    land_acres = models.FloatField(null=True, blank=True)
    roof_squarefeet = models.FloatField(null=True, blank=True)
    # year_one_emissions_lb_C02 = models.FloatField(null=True, blank=True)
    # year_one_emissions_bau_lb_C02 = models.FloatField(null=True, blank=True)
    # outdoor_air_temp_degF = ArrayField(models.FloatField(blank=True, null=True), default=list, null=True)
    # elevation_ft = models.FloatField(null=True, blank=True)
    # renewable_electricity_energy_pct = models.FloatField(null=True, blank=True)


class FinancialInputs(BaseModel, models.Model):
    name = "Financial"

    run_uuid = models.UUIDField(unique=True)
    analysis_years = models.IntegerField(
        default=25,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(75)
        ],
        help_text="Analysis period in years. Must be integer."
    )
    escalation_pct = models.FloatField(
        default=0.023,
        validators=[
            MinValueValidator(-1),
            MaxValueValidator(1)
        ],
        help_text="Annual nominal utility electricity cost escalation rate."
    )
    om_cost_escalation_pct = models.FloatField(
        default=0.025,
        validators=[
            MinValueValidator(-1),
            MaxValueValidator(1)
        ],
        help_text="Annual nominal O&M cost escalation rate"
    )
    offtaker_discount_pct = models.FloatField(
        default=0.083,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Nominal energy offtaker discount rate. In single ownership model the offtaker is also the "
                   "generation owner.")
    )
    offtaker_tax_pct = models.FloatField(
        default=0.26,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(0.999)
        ],
        help_text="Host tax rate"
    )
    value_of_lost_load_us_dollars_per_kwh = models.FloatField(
        default=100,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1e6)
        ],
        help_text=("Value placed on unmet site load during grid outages. Units are US dollars per unmet kilowatt-hour. "
                   "The value of lost load (VoLL) is used to determine the avoided outage costs by multiplying VoLL "
                   "[$/kWh] with the average number of hours that the critical load can be met by the energy system "
                   "(determined by simulating outages occuring at every hour of the year), and multiplying by the mean "
                   "critical load.")
    )
    microgrid_upgrade_cost_pct = models.FloatField(
        default=0.3,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Additional cost, in percent of non-islandable capital costs, to make a distributed energy system "
                   "islandable from the grid and able to serve critical loads. Includes all upgrade costs such as "
                   "additional laber and critical load panels.")
    )
    third_party_ownership = models.BooleanField(
        default=False,
        help_text=("Specify if ownership model is direct ownership or two party. In two party model the offtaker does "
                   "not purcharse the generation technologies, but pays the generation owner for energy from the "
                   "generator(s).")
    )
    owner_discount_pct = models.FloatField(
        default=0.083,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Nominal generation owner discount rate. Used for two party financing model. In two party ownership "
                   "model the offtaker does not own the generator(s).")
    )
    owner_tax_pct = models.FloatField(
        default=0.26,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(0.999)
        ],
        help_text=("Generation owner tax rate. Used for two party financing model. In two party ownership model the "
                   "offtaker does not own the generator(s).")
    )
    # boiler_fuel_escalation_pct = models.FloatField(null=True, blank=True)
    # chp_fuel_escalation_pct = models.FloatField(null=True, blank=True)


# class FinancialOutputs(BaseModel, models.Model):
#     name = "FinancialOutputs"
#
#     run_uuid = models.UUIDField(unique=True)
#     lcc_us_dollars = models.FloatField(null=True, blank=True)
#     lcc_bau_us_dollars = models.FloatField(null=True, blank=True)
#     npv_us_dollars = models.FloatField(null=True, blank=True)
#     net_capital_costs_plus_om_us_dollars = models.FloatField(null=True, blank=True)
#     avoided_outage_costs_us_dollars = models.FloatField(null=True, blank=True)
#     microgrid_upgrade_cost_us_dollars = models.FloatField(null=True, blank=True)
#     net_capital_costs = models.FloatField(null=True, blank=True)
#     net_om_us_dollars_bau = models.FloatField(null=True, blank=True)
#     initial_capital_costs = models.FloatField(null=True, blank=True)
#     replacement_costs = models.FloatField(null=True, blank=True)
#     om_and_replacement_present_cost_after_tax_us_dollars = models.FloatField(null=True, blank=True)
#     initial_capital_costs_after_incentives = models.FloatField(null=True, blank=True)
#     total_om_costs_us_dollars = models.FloatField(null=True, blank=True)
#     year_one_om_costs_us_dollars = models.FloatField(null=True, blank=True)
#     year_one_om_costs_before_tax_us_dollars = models.FloatField(null=True, blank=True)
#     simple_payback_years = models.FloatField(null=True, blank=True)
#     irr_pct = models.FloatField(null=True, blank=True)
#     net_present_cost_us_dollars = models.FloatField(null=True, blank=True)
#     annualized_payment_to_third_party_us_dollars = models.FloatField(null=True, blank=True)
#     offtaker_annual_free_cashflow_series_us_dollars = ArrayField(
#             models.FloatField(null=True, blank=True), default=list, null=True)
#     offtaker_discounted_annual_free_cashflow_series_us_dollars = ArrayField(
#             models.FloatField(null=True, blank=True), default=list, null=True)
#     offtaker_annual_free_cashflow_series_bau_us_dollars = ArrayField(
#             models.FloatField(null=True, blank=True), default=list, null=True)
#     offtaker_discounted_annual_free_cashflow_series_bau_us_dollars = ArrayField(
#             models.FloatField(null=True, blank=True), default=list, null=True)
#     developer_annual_free_cashflow_series_us_dollars = ArrayField(
#             models.FloatField(null=True, blank=True), default=list, null=True)
#     developer_om_and_replacement_present_cost_after_tax_us_dollars = models.FloatField(null=True, blank=True)


class LoadProfileInputs(BaseModel, models.Model):
    name = "LoadProfile"

    possible_sets = [
        ["loads_kw"],
        ["doe_reference_name", "monthly_totals_kwh"],
        ["annual_kwh", "doe_reference_name"],
        ["doe_reference_name"]
    ]

    run_uuid = models.UUIDField(unique=True)
    DOE_REFERENCE_NAME = models.TextChoices('DOE_REFERENCE_NAME', (
         'FastFoodRest '
         'FullServiceRest '
         'Hospital '
         'LargeHotel '
         'LargeOffice '
         'MediumOffice '
         'MidriseApartment '
         'Outpatient '
         'PrimarySchool '
         'RetailStore '
         'SecondarySchool '
         'SmallHotel '
         'SmallOffice '
         'StripMall '
         'Supermarket '
         'Warehouse '
         'FlatLoad '
         'FlatLoad_24_5 '
         'FlatLoad_16_7 '
         'FlatLoad_16_5 '
         'FlatLoad_8_7 '
         'FlatLoad_8_5'
    ))
    # Inputs
    doe_reference_name = ArrayField(
        models.TextField(
            # blank=True,  # TODO do we have to include "" in choices for blank=True to work?
            choices=DOE_REFERENCE_NAME.choices
        ),
        default=list,
        help_text=("Simulated load profile from DOE <a href='https: "
                   "//energy.gov/eere/buildings/commercial-reference-buildings' target='blank'>Commercial Reference "
                   "Buildings</a>")
    )
    annual_kwh = models.FloatField(null=True, blank=True)
    percent_share = ArrayField(
        models.FloatField(
            default=100,
            validators=[
                MinValueValidator(1),
                MaxValueValidator(100)
            ],
        ),
        default=list,
        help_text=("Percentage share of the types of building for creating hybrid simulated building and campus "
                   "profiles.")
    )
    year = models.IntegerField(
        default=2020,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9999)
        ],
        help_text=("Year of Custom Load Profile. If a custom load profile is uploaded via the loads_kw parameter, it "
                   "is important that this year correlates with the load profile so that weekdays/weekends are "
                   "determined correctly for the utility rate tariff. If a DOE Reference Building profile (aka "
                   "'simulated' profile) is used, the year is set to 2017 since the DOE profiles start on a Sunday.")
    )
    monthly_totals_kwh = ArrayField(models.FloatField(blank=True), null=True, blank=True)
    loads_kw = ArrayField(models.FloatField(blank=True), default=list, null=True, blank=True)
    critical_loads_kw = ArrayField(models.FloatField(blank=True), default=list, null=True, blank=True)
    loads_kw_is_net = models.BooleanField(null=True, blank=True)
    critical_loads_kw_is_net = models.BooleanField(null=True, blank=True)
    outage_start_time_step = models.IntegerField(null=True, blank=True)
    outage_end_time_step = models.IntegerField(null=True, blank=True)
    critical_load_pct = models.FloatField(null=True, blank=True)
    outage_is_major_event = models.BooleanField(null=True, blank=True)

    # #Outputs
    # year_one_electric_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), default=list, null=True)
    # critical_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), default=list, null=True)
    # annual_calculated_kwh = models.FloatField(null=True, blank=True)
    # sustain_hours = models.IntegerField(null=True, blank=True)
    # bau_sustained_time_steps = models.IntegerField(null=True, blank=True)
    # resilience_check_flag = models.BooleanField(null=True, blank=True)

    def clean(self):
        error_messages = []

        # outage start/end time step dependencies
        if self.outage_start_time_step and self.outage_end_time_step is None:
            error_messages.append("Got outage_start_time_step but no outage_end_time_step.")

        if self.outage_end_time_step and self.outage_start_time_step is None:
            error_messages.append("Got outage_end_time_step but no outage_start_time_step.")

        if self.outage_start_time_step is not None and self.outage_end_time_step is not None:
            if self.outage_start_time_step >= self.outage_end_time_step:
                error_messages.append((
                    'LoadProfile outage_end_time_step must be larger than outage_start_time_step and these inputs '
                    'cannot be equal.'
                ))

        # possible sets for defining load profile
        if not at_least_one_set(self.dict, self.possible_sets):
            error_messages.append((
                "Must provide at valid at least one set of valid inputs from {}.".format(self.possible_sets)
            ))

        # TODO validate length of load profile

        if error_messages:
            raise ValidationError(' & '.join(error_messages))


class ElectricTariffInputs(BaseModel, models.Model):
    name = "ElectricTariff"
    possible_sets = [
        ["urdb_response"],
        ["blended_monthly_demand_charges_us_dollars_per_kw", "blended_monthly_rates_us_dollars_per_kwh"],
        ["blended_annual_demand_charges_us_dollars_per_kw", "blended_annual_rates_us_dollars_per_kwh"],
        ["urdb_label"],
        ["urdb_utility_name", "urdb_rate_name"],
        ["tou_energy_rates_us_dollars_per_kwh"]
    ]
    #Inputs
    run_uuid = models.UUIDField(unique=True)
    urdb_utility_name = models.TextField(blank=True)
    urdb_rate_name = models.TextField(blank=True)
    urdb_label = models.TextField(blank=True)
    blended_monthly_rates_us_dollars_per_kwh = ArrayField(models.FloatField(blank=True), null=True, blank=True)
    blended_monthly_demand_charges_us_dollars_per_kw = ArrayField(
        models.FloatField(null=True, blank=True),
        null=True, blank=True
    )
    blended_annual_rates_us_dollars_per_kwh = models.FloatField(blank=True, default=0, null=True)
    blended_annual_demand_charges_us_dollars_per_kw = models.FloatField(blank=True, default=0, null=True)
    net_metering_limit_kw = models.FloatField(null=True, blank=True)
    interconnection_limit_kw = models.FloatField(null=True, blank=True)
    wholesale_rate_us_dollars_per_kwh = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    wholesale_rate_above_site_load_us_dollars_per_kwh = ArrayField(
        models.FloatField(null=True, blank=True),
        null=True, blank=True
    )
    urdb_response = PickledObjectField(null=True, editable=True, blank=True)
    # add_blended_rates_to_urdb_rate = models.BooleanField(null=True, blank=True)
    # add_tou_energy_rates_to_urdb_rate = models.BooleanField(null=True, blank=True)
    tou_energy_rates_us_dollars_per_kwh = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    # emissions_factor_series_lb_CO2_per_kwh = ArrayField(models.FloatField(null=True, blank=True), null=True, default=list)
    # chp_standby_rate_us_dollars_per_kw_per_month = models.FloatField(blank=True, null=True)
    # chp_does_not_reduce_demand_charges = models.BooleanField(null=True, blank=True)
    # emissions_region = models.TextField(blank=True)
    # coincident_peak_load_active_timesteps = ArrayField(ArrayField(models.FloatField(null=True, blank=True), null=True, default=list), null=True, default=list)
    # coincident_peak_load_charge_us_dollars_per_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, default=list)

    # # Ouptuts
    # year_one_energy_cost_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_demand_cost_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_fixed_cost_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_min_charge_adder_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_energy_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_demand_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_fixed_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_min_charge_adder_bau_us_dollars = models.FloatField(null=True, blank=True)
    # total_energy_cost_us_dollars = models.FloatField(null=True, blank=True)
    # total_demand_cost_us_dollars = models.FloatField(null=True, blank=True)
    # total_fixed_cost_us_dollars = models.FloatField(null=True, blank=True)
    # total_min_charge_adder_us_dollars = models.FloatField(null=True, blank=True)
    # total_energy_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    # total_demand_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    # total_fixed_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    # total_export_benefit_us_dollars = models.FloatField(null=True, blank=True)
    # total_export_benefit_bau_us_dollars = models.FloatField(null=True, blank=True)
    # total_min_charge_adder_bau_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_bill_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_bill_bau_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_export_benefit_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_export_benefit_bau_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_energy_cost_series_us_dollars_per_kwh = ArrayField(models.FloatField(null=True, blank=True), default=list, null=True, blank=True)
    # year_one_demand_cost_series_us_dollars_per_kw = ArrayField(models.FloatField(null=True, blank=True), default=list, null=True, blank=True)
    # year_one_to_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), default=list, null=True, blank=True)
    # year_one_to_load_series_bau_kw = ArrayField(models.FloatField(null=True, blank=True), default=list, null=True, blank=True)
    # year_one_to_battery_series_kw = ArrayField(models.FloatField(null=True, blank=True), default=list, null=True, blank=True)
    # year_one_energy_supplied_kwh = models.FloatField(null=True, blank=True)
    # year_one_energy_supplied_kwh_bau = models.FloatField(null=True, blank=True)
    # year_one_emissions_lb_C02 = models.FloatField(null=True, blank=True)
    # year_one_emissions_bau_lb_C02 = models.FloatField(null=True, blank=True)
    # year_one_coincident_peak_cost_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_coincident_peak_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    # total_coincident_peak_cost_us_dollars = models.FloatField(null=True, blank=True)
    # total_coincident_peak_cost_bau_us_dollars = models.FloatField(null=True, blank=True)
    # year_one_chp_standby_cost_us_dollars = models.FloatField(null=True, blank=True)
    # total_chp_standby_cost_us_dollars = models.FloatField(null=True, blank=True)

    def clean(self):
        error_messages = []

        # possible sets for defining tariff
        if not at_least_one_set(self.dict, self.possible_sets):
            error_messages.append((
                "Must provide at valid at least one set of valid inputs from {}.".format(self.possible_sets)
            ))

        if error_messages:
            raise ValidationError(' & '.join(error_messages))


# class PV(BaseModel, models.Model):
#
#     #Inputs
#     run_uuid = models.UUIDField(unique=False)
#     existing_kw = models.FloatField(null=True, blank=True)
#     min_kw = models.FloatField(null=True, blank=True)
#     max_kw = models.FloatField(null=True, blank=True)
#     installed_cost_us_dollars_per_kw = models.FloatField(null=True, blank=True)
#     om_cost_us_dollars_per_kw = models.FloatField(null=True, blank=True)
#     macrs_option_years = models.IntegerField(null=True, blank=True)
#     macrs_bonus_pct = models.FloatField(null=True, blank=True)
#     macrs_itc_reduction = models.FloatField(null=True, blank=True)
#     federal_itc_pct = models.FloatField(null=True, blank=True)
#     state_ibi_pct = models.FloatField(null=True, blank=True)
#     state_ibi_max_us_dollars = models.FloatField(null=True, blank=True)
#     utility_ibi_pct = models.FloatField(null=True, blank=True)
#     utility_ibi_max_us_dollars = models.FloatField(null=True, blank=True)
#     federal_rebate_us_dollars_per_kw = models.FloatField(null=True, blank=True)
#     state_rebate_us_dollars_per_kw = models.FloatField(null=True, blank=True)
#     state_rebate_max_us_dollars = models.FloatField(null=True, blank=True)
#     utility_rebate_us_dollars_per_kw = models.FloatField(null=True, blank=True)
#     utility_rebate_max_us_dollars = models.FloatField(null=True, blank=True)
#     pbi_us_dollars_per_kwh = models.FloatField(null=True, blank=True)
#     pbi_max_us_dollars = models.FloatField(null=True, blank=True)
#     pbi_years = models.FloatField(null=True, blank=True)
#     pbi_system_max_kw = models.FloatField(null=True, blank=True)
#     degradation_pct = models.FloatField(null=True, blank=True)
#     azimuth = models.FloatField(null=True, blank=True)
#     losses = models.FloatField(null=True, blank=True)
#     array_type = models.IntegerField(null=True, blank=True)
#     module_type = models.IntegerField(null=True, blank=True)
#     gcr = models.FloatField(null=True, blank=True)
#     dc_ac_ratio = models.FloatField(null=True, blank=True)
#     inv_eff = models.FloatField(null=True, blank=True)
#     radius = models.FloatField(null=True, blank=True)
#     tilt = models.FloatField(null=True, blank=True)
#     prod_factor_series_kw = ArrayField(
#             models.FloatField(null=True, blank=True), default=list, null=True)
#     pv_number = models.IntegerField(null=True, blank=True)
#     pv_name = models.TextField(blank=True)
#     location = models.TextField(blank=True)
#     can_net_meter = models.BooleanField(null=True, blank=True)
#     can_wholesale = models.BooleanField(null=True, blank=True)
#     can_export_beyond_site_load = models.BooleanField(null=True, blank=True)
#     can_curtail = models.BooleanField(null=True, blank=True)
#
#     # Outputs
#     size_kw = models.FloatField(null=True, blank=True)
#     station_latitude = models.FloatField(null=True, blank=True)
#     station_longitude = models.FloatField(null=True, blank=True)
#     station_distance_km = models.FloatField(null=True, blank=True)
#     average_yearly_energy_produced_kwh = models.FloatField(null=True, blank=True)
#     average_yearly_energy_produced_bau_kwh = models.FloatField(null=True, blank=True)
#     average_yearly_energy_exported_kwh = models.FloatField(null=True, blank=True)
#     year_one_energy_produced_kwh = models.FloatField(null=True, blank=True)
#     year_one_energy_produced_bau_kwh = models.FloatField(null=True, blank=True)
#     year_one_power_production_series_kw = ArrayField(
#             models.FloatField(null=True, blank=True), null=True, blank=True, default=list)
#     year_one_to_battery_series_kw = ArrayField(
#             models.FloatField(null=True, blank=True), null=True, blank=True, default=list)
#     year_one_to_load_series_kw = ArrayField(
#             models.FloatField(null=True, blank=True), null=True, blank=True, default=list)
#     year_one_to_grid_series_kw = ArrayField(
#             models.FloatField(null=True, blank=True), null=True, blank=True, default=list)
#     existing_pv_om_cost_us_dollars = models.FloatField(null=True, blank=True)
#     year_one_curtailed_production_series_kw = ArrayField(
#             models.FloatField(null=True, blank=True), null=True, blank=True, default=list)
#     existing_pv_om_cost_us_dollars = models.FloatField(null=True, blank=True)
#     lcoe_us_dollars_per_kwh = models.FloatField(null=True, blank=True)
#
#
# class Storage(BaseModel, models.Model):
#     # Inputs
#     run_uuid = models.UUIDField(unique=True)
#     min_kw = models.FloatField(null=True, blank=True)
#     max_kw = models.FloatField(null=True, blank=True)
#     min_kwh = models.FloatField(null=True, blank=True)
#     max_kwh = models.FloatField(null=True, blank=True)
#     internal_efficiency_pct = models.FloatField(null=True, blank=True)
#     inverter_efficiency_pct = models.FloatField(null=True, blank=True)
#     rectifier_efficiency_pct = models.FloatField(null=True, blank=True)
#     soc_min_pct = models.FloatField(null=True, blank=True)
#     soc_init_pct = models.FloatField(null=True, blank=True)
#     canGridCharge = models.BooleanField(null=True, blank=True)
#     installed_cost_us_dollars_per_kw = models.FloatField(null=True, blank=True)
#     installed_cost_us_dollars_per_kwh = models.FloatField(null=True, blank=True)
#     replace_cost_us_dollars_per_kw = models.FloatField(null=True, blank=True)
#     replace_cost_us_dollars_per_kwh = models.FloatField(null=True, blank=True)
#     inverter_replacement_year = models.IntegerField(null=True, blank=True)
#     battery_replacement_year = models.IntegerField(null=True, blank=True)
#     macrs_option_years = models.IntegerField(null=True, blank=True)
#     macrs_bonus_pct = models.FloatField(null=True, blank=True)
#     macrs_itc_reduction = models.FloatField(null=True, blank=True)
#     total_itc_pct = models.FloatField(null=True, blank=True)
#     total_rebate_us_dollars_per_kw = models.IntegerField(null=True, blank=True)
#     total_rebate_us_dollars_per_kwh = models.IntegerField(null=True, blank=True)
#
#     # Outputs
#     size_kw = models.FloatField(null=True, blank=True)
#     size_kwh = models.FloatField(null=True, blank=True)
#     year_one_to_load_series_kw = ArrayField(
#             models.FloatField(null=True, blank=True), null=True, blank=True, default=list)
#     year_one_to_grid_series_kw = ArrayField(
#             models.FloatField(null=True, blank=True), null=True, blank=True, default=list)
#     year_one_soc_series_pct = ArrayField(
#             models.FloatField(null=True, blank=True), null=True, blank=True, default=list)
#
#
# class Generator(BaseModel, models.Model):
#     # Inputs
#     run_uuid = models.UUIDField(unique=True)
#     existing_kw = models.FloatField(null=True, blank=True)
#     min_kw = models.FloatField(null=True, blank=True)
#     max_kw = models.FloatField(null=True, blank=True)
#     installed_cost_us_dollars_per_kw = models.FloatField(null=True, blank=True,)
#     om_cost_us_dollars_per_kw = models.FloatField(null=True, blank=True)
#     om_cost_us_dollars_per_kwh = models.FloatField(null=True, blank=True)
#     diesel_fuel_cost_us_dollars_per_gallon = models.FloatField(null=True, blank=True)
#     fuel_slope_gal_per_kwh = models.FloatField(null=True, blank=True)
#     fuel_intercept_gal_per_hr = models.FloatField(null=True, blank=True)
#     fuel_avail_gal = models.FloatField(null=True, blank=True)
#     min_turn_down_pct = models.FloatField(null=True, blank=True)
#     generator_only_runs_during_grid_outage = models.BooleanField(null=True, blank=True)
#     generator_sells_energy_back_to_grid = models.BooleanField(null=True, blank=True)
#     macrs_option_years = models.IntegerField(null=True, blank=True)
#     macrs_bonus_pct = models.FloatField(null=True, blank=True)
#     macrs_itc_reduction = models.FloatField(null=True, blank=True)
#     federal_itc_pct = models.FloatField(null=True, blank=True)
#     state_ibi_pct = models.FloatField(null=True, blank=True)
#     state_ibi_max_us_dollars = models.FloatField(null=True, blank=True)
#     utility_ibi_pct = models.FloatField(null=True, blank=True)
#     utility_ibi_max_us_dollars = models.FloatField(null=True, blank=True)
#     federal_rebate_us_dollars_per_kw = models.FloatField(null=True, blank=True)
#     state_rebate_us_dollars_per_kw = models.FloatField(null=True, blank=True)
#     state_rebate_max_us_dollars = models.FloatField(null=True, blank=True)
#     utility_rebate_us_dollars_per_kw = models.FloatField(null=True, blank=True)
#     utility_rebate_max_us_dollars = models.FloatField(null=True, blank=True)
#     pbi_us_dollars_per_kwh = models.FloatField(null=True, blank=True)
#     pbi_max_us_dollars = models.FloatField(null=True, blank=True)
#     pbi_years = models.FloatField(null=True, blank=True)
#     pbi_system_max_kw = models.FloatField(null=True, blank=True)
#     emissions_factor_lb_CO2_per_gal = models.FloatField(null=True, blank=True)
#     can_net_meter = models.BooleanField(null=True, blank=True)
#     can_wholesale = models.BooleanField(null=True, blank=True)
#     can_export_beyond_site_load = models.BooleanField(null=True, blank=True)
#     can_curtail = models.BooleanField(null=True, blank=True)
#
#     # Outputs
#     fuel_used_gal = models.FloatField(null=True, blank=True)
#     fuel_used_gal_bau = models.FloatField(null=True, blank=True)
#     size_kw = models.FloatField(null=True, blank=True)
#     average_yearly_energy_produced_kwh = models.FloatField(null=True, blank=True)
#     average_yearly_energy_exported_kwh = models.FloatField(null=True, blank=True)
#     year_one_energy_produced_kwh = models.FloatField(null=True, blank=True)
#     year_one_power_production_series_kw = ArrayField(
#             models.FloatField(null=True, blank=True), null=True, blank=True, default=list)
#     year_one_to_battery_series_kw = ArrayField(
#             models.FloatField(null=True, blank=True), null=True, blank=True)
#     year_one_to_load_series_kw = ArrayField(
#             models.FloatField(null=True, blank=True), null=True, blank=True, default=list)
#     year_one_to_grid_series_kw = ArrayField(
#             models.FloatField(null=True, blank=True), null=True, blank=True, default=list)
#     year_one_variable_om_cost_us_dollars = models.FloatField(null=True, blank=True)
#     year_one_fuel_cost_us_dollars = models.FloatField(null=True, blank=True)
#     year_one_fixed_om_cost_us_dollars = models.FloatField(null=True, blank=True)
#     total_variable_om_cost_us_dollars = models.FloatField(null=True, blank=True)
#     total_fuel_cost_us_dollars = models.FloatField(null=True, blank=True)
#     total_fixed_om_cost_us_dollars = models.FloatField(null=True, blank=True)
#     existing_gen_year_one_variable_om_cost_us_dollars = models.FloatField(null=True, blank=True)
#     existing_gen_year_one_fuel_cost_us_dollars = models.FloatField(null=True, blank=True)
#     existing_gen_total_variable_om_cost_us_dollars = models.FloatField(null=True, blank=True)
#     existing_gen_total_fuel_cost_us_dollars = models.FloatField(null=True, blank=True)
#     existing_gen_total_fixed_om_cost_us_dollars = models.FloatField(null=True, blank=True)
#     year_one_emissions_lb_C02 = models.FloatField(null=True, blank=True)
#     year_one_emissions_bau_lb_C02 = models.FloatField(null=True, blank=True)
#
#
# class Message(models.Model):
#     """
#     For Example:
#     {"messages":{
#                 "warnings": "This is a warning message.",
#                 "error": "REopt had an error."
#                 }
#     }
#     """
#     message_type = models.TextField(null=True, blank=True, default='')
#     message = models.TextField(null=True, blank=True, default='')
#     run_uuid = models.UUIDField(unique=False)
#     description = models.TextField(null=True, blank=True, default='')
#
#
# class BadPost(models.Model):
#     run_uuid = models.UUIDField(unique=True)
#     post = models.TextField(blank=True)
#     errors = models.TextField(blank=True)
#
#     def save(self, force_insert=False, force_update=False, using=None,
#              update_fields=None):
#         try:
#             super(BadPost, self).save()
#         except Exception as e:
#             log.info("Database saving error: {}".format(e.args[0]))
#
#
# def attribute_inputs(inputs):
#     return {k: v for k, v in inputs.items() if k[0] == k[0].lower() and v is not None}
#
#
# class Error(models.Model):
#     task = models.TextField(null=True, blank=True, default='')
#     name = models.TextField(null=True, blank=True, default='')
#     run_uuid = models.TextField(null=True, blank=True, default='')
#     user_uuid = models.TextField(null=True, blank=True, default='')
#     message = models.TextField(null=True, blank=True, default='')
#     traceback = models.TextField(null=True, blank=True, default='')
#     created = models.DateTimeField(auto_now_add=True)
#
#
# def update_model(model_name, model_data, run_uuid, number=None):
#     if number is None:
#         eval(model_name).objects.filter(run_uuid=run_uuid).update(**attribute_inputs(model_data))
#     else:
#         if 'PV' in model_name:
#             eval(model_name).objects.filter(run_uuid=run_uuid, pv_number=number).update(**attribute_inputs(model_data))
#
#
# def remove(run_uuid):
#     """
#     remove Scenario from database
#     :param run_uuid: id of Scenario
#     :return: None
#     """
#     Scenario.objects.filter(run_uuid=run_uuid).delete()
#     # Profile.objects.filter(run_uuid=run_uuid).delete()
#     SiteInputs.objects.filter(run_uuid=run_uuid).delete()
#     FinancialInputs.objects.filter(run_uuid=run_uuid).delete()
#     LoadProfileInputs.objects.filter(run_uuid=run_uuid).delete()
#     # LoadProfileBoilerFuel.objects.filter(run_uuid=run_uuid).delete()
#     # LoadProfileChillerThermal.objects.filter(run_uuid=run_uuid).delete()
#     ElectricTariffInputs.objects.filter(run_uuid=run_uuid).delete()
#     PV.objects.filter(run_uuid=run_uuid).delete()
#     # Wind.objects.filter(run_uuid=run_uuid).delete()
#     Storage.objects.filter(run_uuid=run_uuid).delete()
#     Generator.objects.filter(run_uuid=run_uuid).delete()
#     # CHP.objects.filter(run_uuid=run_uuid).delete()
#     # Boiler.objects.filter(run_uuid=run_uuid).delete()
#     # ElectricChiller.objects.filter(run_uuid=run_uuid).delete()
#     # AbsorptionChiller.objects.filter(run_uuid=run_uuid).delete()
#     # HotTES.objects.filter(run_uuid=run_uuid).delete()
#     # ColdTES.objects.filter(run_uuid=run_uuid).delete()
#     Message.objects.filter(run_uuid=run_uuid).delete()
#     Error.objects.filter(run_uuid=run_uuid).delete()
#
#
# def update(data, run_uuid):
#     """
#     save Scenario results in database
#     :param data: dict, constructed in api.py, mirrors reopt api response structure
#     :param model_ids: dict, optional, for use when updating existing models that have not been created in memory
#     :return: None
#     """
#     d = data["outputs"]["Scenario"]
#     # Profile.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Profile']))
#     SiteInputs.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']))
#     FinancialInputs.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['Financial']))
#     LoadProfileInputs.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['LoadProfile']))
#     # LoadProfileBoilerFuel.objects.filter(run_uuid=run_uuid).update(
#     #     **attribute_inputs(d['Site']['LoadProfileBoilerFuel']))
#     # LoadProfileChillerThermal.objects.filter(run_uuid=run_uuid).update(
#     #     **attribute_inputs(d['Site']['LoadProfileChillerThermal']))
#     ElectricTariffInputs.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['ElectricTariff']))
#     # FuelTariff.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['FuelTariff']))
#     if type(d['Site']['PV'])==dict:
#         PV.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['PV']))
#     if type(d['Site']['PV']) == list:
#         for pv in d['Site']['PV']:
#             PV.objects.filter(run_uuid=run_uuid, pv_number=pv['pv_number']).update(**attribute_inputs(pv))
#     # Wind.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['Wind']))
#     Storage.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['Storage']))
#     Generator.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['Generator']))
#     # CHP.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['CHP']))
#     # Boiler.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['Boiler']))
#     # ElectricChiller.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['ElectricChiller']))
#     # AbsorptionChiller.objects.filter(run_uuid=run_uuid).update(
#     #     **attribute_inputs(d['Site']['AbsorptionChiller']))
#     # HotTES.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['HotTES']))
#     # ColdTES.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['ColdTES']))
#
#     for message_type, message in data['messages'].items():
#         if len(Message.objects.filter(run_uuid=run_uuid, message=message)) > 0:
#             # message already saved
#             pass
#         else:
#             Message.create(run_uuid=run_uuid, message_type=message_type, message=message)
#     # Do this last so that the status does not change to optimal before the rest of the results are filled in
#     Scenario.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d))  # force_update=True
#
#
# def update_scenario_and_messages(data, run_uuid):
#     """
#     save Scenario results in database
#     :param data: dict, constructed in api.py, mirrors reopt api response structure
#     :return: None
#     """
#     d = data["outputs"]["Scenario"]
#     Scenario.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d))
#     for message_type, message in data['messages'].items():
#         if len(Message.objects.filter(run_uuid=run_uuid, message=message)) > 0:
#             # message already saved
#             pass
#         else:
#             Message.create(run_uuid=run_uuid, message_type=message_type, message=message)
#
#
# def add_user_uuid(user_uuid, run_uuid):
#     """
#     update the user_uuid associated with a Scenario
#     :param user_uuid: string
#     :param run_uuid: string
#     :return: None
#     """
#     d = {"user_uuid": user_uuid}
#     Scenario.objects.filter(run_uuid=run_uuid).update(**d)
#     Error.objects.filter(run_uuid=run_uuid).update(**d)
#

# def make_response(run_uuid):
#     """
#     Reconstruct response dictionary from postgres tables (django models).
#     NOTE: postgres column type UUID is not JSON serializable. Work-around is removing those columns and then
#           adding back into outputs->Scenario as string.
#     :param run_uuid:
#     :return: nested dictionary matching nested_output_definitions
#     """
#     def remove_number(k, d):
#         if k in d.keys():
#             del d[k]
#         return d
#
#     def remove_ids(d):
#         del d['run_uuid']
#         del d['id']
#         return d
#
#     def move_outs_to_ins(site_key, resp):
#         if not (resp['outputs']['Scenario']['Site'].get(site_key) or None) in [None, [], {}]:
#             resp['inputs']['Scenario']['Site'][site_key] = dict()
#
#             for k in nested_input_definitions['Scenario']['Site'][site_key].keys():
#                 try:
#                     if site_key == "PV":
#                         if type(resp['outputs']['Scenario']['Site'][site_key])==dict:
#                             resp['inputs']['Scenario']['Site'][site_key][k] = resp['outputs']['Scenario']['Site'][site_key][k]
#                             del resp['outputs']['Scenario']['Site'][site_key][k]
#
#                         elif type(resp['outputs']['Scenario']['Site'][site_key])==list:
#                             max_order = max([p.get('pv_number') for p in resp['outputs']['Scenario']['Site'][site_key]])
#                             if resp['inputs']['Scenario']['Site'].get(site_key) == {}:
#                                 resp['inputs']['Scenario']['Site'][site_key] = []
#                             if len(resp['inputs']['Scenario']['Site'][site_key]) == 0 :
#                                 for _ in range(max_order):
#                                     resp['inputs']['Scenario']['Site'][site_key].append({})
#                             for i in range(max_order):
#                                 resp['inputs']['Scenario']['Site'][site_key][i][k] = resp['outputs']['Scenario']['Site'][site_key][i][k]
#                                 if isinstance(resp['inputs']['Scenario']['Site'][site_key][i][k], list):
#                                     if len(resp['inputs']['Scenario']['Site'][site_key][i][k]) == 1:
#                                         resp['inputs']['Scenario']['Site'][site_key][i][k] = \
#                                             resp['inputs']['Scenario']['Site'][site_key][i][k][0]
#                                 if k not in ['pv_name']:
#                                     del resp['outputs']['Scenario']['Site'][site_key][i][k]
#
#                     # special handling for inputs that can be scalar or array,
#                     # (which we have to make an array in database)
#                     else:
#                         resp['inputs']['Scenario']['Site'][site_key][k] = resp['outputs']['Scenario']['Site'][site_key][k]
#                         if isinstance(resp['inputs']['Scenario']['Site'][site_key][k], list):
#                             if len(resp['inputs']['Scenario']['Site'][site_key][k]) == 1:
#                                 resp['inputs']['Scenario']['Site'][site_key][k] = \
#                                     resp['inputs']['Scenario']['Site'][site_key][k][0]
#                             elif len(resp['inputs']['Scenario']['Site'][site_key][k]) == 0:
#                                 del resp['inputs']['Scenario']['Site'][site_key][k]
#                         del resp['outputs']['Scenario']['Site'][site_key][k]
#                 except KeyError:  # known exception for k = urdb_response (user provided blended rates)
#                     resp['inputs']['Scenario']['Site'][site_key][k] = None
#
#     # add try/except for get fail / bad run_uuid
#     site_keys = ['PV', 'Storage', 'Financial', 'LoadProfile', 'LoadProfileBoilerFuel', 'LoadProfileChillerThermal',
#                  'ElectricTariff', 'FuelTariff', 'Generator', 'Wind', 'CHP', 'Boiler', 'ElectricChiller',
#                  'AbsorptionChiller', 'HotTES', 'ColdTES']
#
#     resp = dict()
#     resp['outputs'] = dict()
#     resp['outputs']['Scenario'] = dict()
#     resp['outputs']['Scenario']['Profile'] = dict()
#     resp['inputs'] = dict()
#     resp['inputs']['Scenario'] = dict()
#     resp['inputs']['Scenario']['Site'] = dict()
#     resp['messages'] = dict()
#
#     try:
#         scenario_model = Scenario.objects.get(run_uuid=run_uuid)
#     except Exception as e:
#         if isinstance(e, models.ObjectDoesNotExist):
#             resp['messages']['error'] = (
#                 "run_uuid {} not in database. "
#                 "You may have hit the results endpoint too quickly after POST'ing scenario, "
#                 "you may have a typo in your run_uuid, or the scenario was deleted.").format(run_uuid)
#             resp['outputs']['Scenario']['status'] = 'error'
#             return resp
#         else:
#             raise Exception
#     scenario_data = remove_ids(model_to_dict(scenario_model))
#     del scenario_data['job_type']
#     resp['outputs']['Scenario'] = scenario_data
#     resp['outputs']['Scenario']['run_uuid'] = str(run_uuid)
#     resp['outputs']['Scenario']['Site'] = remove_ids(model_to_dict(SiteInputs.objects.get(run_uuid=run_uuid)))
#
#     financial_record = Financial.objects.filter(run_uuid=run_uuid) or {}
#     if financial_record is not {}:
#         resp['outputs']['Scenario']['Site']['Financial'] = remove_ids(model_to_dict(financial_record[0]))
#
#     loadprofile_record = LoadProfileInputs.objects.filter(run_uuid=run_uuid) or {}
#     if loadprofile_record is not {}:
#         resp['outputs']['Scenario']['Site']['LoadProfile'] = remove_ids(model_to_dict(loadprofile_record[0]))
#
#     lpbf_record = LoadProfileBoilerFuel.objects.filter(run_uuid=run_uuid) or {}
#     if not lpbf_record == {}:
#         resp['outputs']['Scenario']['Site']['LoadProfileBoilerFuel'] = remove_ids(model_to_dict(lpbf_record[0]))
#
#     lpct_record = LoadProfileChillerThermal.objects.filter(run_uuid=run_uuid) or {}
#     if not lpct_record  == {}:
#         resp['outputs']['Scenario']['Site']['LoadProfileChillerThermal'] = remove_ids(model_to_dict(lpct_record[0]))
#
#     etariff_record = ElectricTariffInputs.objects.filter(run_uuid=run_uuid) or {}
#     if not etariff_record == {}:
#         resp['outputs']['Scenario']['Site']['ElectricTariff'] = remove_ids(model_to_dict(etariff_record[0]))
#
#     fueltariff_record = FuelTariff.objects.filter(run_uuid=run_uuid) or {}
#     if not fueltariff_record == {}:
#         resp['outputs']['Scenario']['Site']['FuelTariff'] = remove_ids(model_to_dict(fueltariff_record[0]))
#
#     storage_record = Storage.objects.filter(run_uuid=run_uuid) or {}
#     if not storage_record == {}:
#         resp['outputs']['Scenario']['Site']['Storage'] = remove_ids(model_to_dict(storage_record[0]))
#
#     generator_record = Generator.objects.filter(run_uuid=run_uuid) or {}
#     if not generator_record == {}:
#         resp['outputs']['Scenario']['Site']['Generator'] = remove_ids(model_to_dict(generator_record[0]))
#
#     wind_record = Wind.objects.filter(run_uuid=run_uuid) or {}
#     if not wind_record == {}:
#         resp['outputs']['Scenario']['Site']['Wind'] = remove_ids(model_to_dict(wind_record[0]))
#
#     chp_record = CHP.objects.filter(run_uuid=run_uuid) or {}
#     if not chp_record == {}:
#         resp['outputs']['Scenario']['Site']['CHP'] = remove_ids(model_to_dict(chp_record[0]))
#
#     boiler_record = Boiler.objects.filter(run_uuid=run_uuid) or {}
#     if not boiler_record == {}:
#         resp['outputs']['Scenario']['Site']['Boiler'] = remove_ids(model_to_dict(boiler_record[0]))
#
#     echiller_record = ElectricChiller.objects.filter(run_uuid=run_uuid) or {}
#     if not echiller_record == {}:
#         resp['outputs']['Scenario']['Site']['ElectricChiller'] = remove_ids(model_to_dict(echiller_record[0]))
#
#     achiller_record = AbsorptionChiller.objects.filter(run_uuid=run_uuid) or {}
#     if not achiller_record == {}:
#         resp['outputs']['Scenario']['Site']['AbsorptionChiller'] = remove_ids(model_to_dict(achiller_record[0]))
#
#     hottes_record = HotTES.objects.filter(run_uuid=run_uuid) or {}
#     if not hottes_record == {}:
#         resp['outputs']['Scenario']['Site']['HotTES'] = remove_ids(model_to_dict(hottes_record[0]))
#
#     coldtes_record = ColdTES.objects.filter(run_uuid=run_uuid) or {}
#     if not coldtes_record == {}:
#         resp['outputs']['Scenario']['Site']['ColdTES'] = remove_ids(model_to_dict(coldtes_record[0]))
#
#     resp['outputs']['Scenario']['Site']['PV'] = []
#     for x in PV.objects.filter(run_uuid=run_uuid).order_by('pv_number'):
#         resp['outputs']['Scenario']['Site']['PV'].append(remove_ids(model_to_dict(x)))
#
#     profile_data = Profile.objects.filter(run_uuid=run_uuid)
#     if len(profile_data) > 0:
#         resp['outputs']['Scenario']['Profile'] = remove_ids(model_to_dict(profile_data[0]))
#
#     for m in Message.objects.filter(run_uuid=run_uuid).values('message_type', 'message'):
#         resp['messages'][m['message_type']] = m['message']
#
#     for scenario_key in nested_input_definitions['Scenario'].keys():
#         if scenario_key.islower():
#             resp['inputs']['Scenario'][scenario_key] = resp['outputs']['Scenario'][scenario_key]
#             del resp['outputs']['Scenario'][scenario_key]
#
#     for site_key in nested_input_definitions['Scenario']['Site'].keys():
#         if site_key.islower():
#             resp['inputs']['Scenario']['Site'][site_key] = resp['outputs']['Scenario']['Site'][site_key]
#             del resp['outputs']['Scenario']['Site'][site_key]
#
#         elif site_key in site_keys:
#             move_outs_to_ins(site_key, resp=resp)
#
#     if len(resp['inputs']['Scenario']['Site']['PV']) == 1:
#         resp['inputs']['Scenario']['Site']['PV'] = resp['inputs']['Scenario']['Site']['PV'][0]
#     resp['outputs']['Scenario']['Site']['PV'] = [remove_number('pv_number', x) for x in resp['outputs']['Scenario']['Site']['PV']]
#     if len(resp['outputs']['Scenario']['Site']['PV']) == 1:
#         resp['outputs']['Scenario']['Site']['PV'] = resp['outputs']['Scenario']['Site']['PV'][0]
#
#     if resp['inputs']['Scenario']['Site']['LoadProfile'].get('doe_reference_name') == '':
#         del resp['inputs']['Scenario']['Site']['LoadProfile']['doe_reference_name']
#
#     #Preserving Backwards Compatability
#     resp['inputs']['Scenario']['Site']['LoadProfile']['outage_start_hour'] = resp['inputs']['Scenario']['Site']['LoadProfile'].get('outage_start_time_step')
#     if resp['inputs']['Scenario']['Site']['LoadProfile']['outage_start_hour'] is not None:
#         resp['inputs']['Scenario']['Site']['LoadProfile']['outage_start_hour'] -= 1
#     resp['inputs']['Scenario']['Site']['LoadProfile']['outage_end_hour'] = resp['inputs']['Scenario']['Site']['LoadProfile'].get('outage_end_time_step')
#     if resp['inputs']['Scenario']['Site']['LoadProfile']['outage_end_hour'] is not None:
#         resp['inputs']['Scenario']['Site']['LoadProfile']['outage_end_hour'] -= 1
#     return resp
