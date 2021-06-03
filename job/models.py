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
# from django.contrib.postgres.fields import *
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
        ],
        help_text="The approximate latitude of the site in decimal degrees."
    )
    longitude = models.FloatField(
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ],
        help_text="The approximate longitude of the site in decimal degrees."
    )
    address = models.TextField(
        blank=True,
        help_text="A user defined address as optional metadata (street address, city, state or zip code)"
    )
    land_acres = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0e6)
        ],
        help_text="Land area in acres available for PV panel siting."
    )
    roof_squarefeet = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0e9)
        ],
        help_text="Area of roof in square feet available for PV siting"
    )
    year_one_emissions_bau_lb_C02 = models.FloatField(null=True, blank=True)
    outdoor_air_temp_degF = ArrayField(models.FloatField(blank=True, null=True), default=list, null=True)
    elevation_ft = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(15000.0)
        ],
        default=0.0,
        help_text="Site elevation (above sea sevel), units of feet."
    )
    renewable_electricity_energy_pct = models.FloatField(null=True, blank=True)


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

    monthly_totals_kwh = ArrayField(
        models.FloatField(
            default=1.0e8,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(1.0e8)
            ],
            blank=True
        ),
        default=list,
        help_text=("Monthly site energy consumption from electricity series (an array 12 entries long), in kWh, used "
                   "to scale simulated default building load profile for the site's climate zone"),
        null=True,
        blank=True
    )
    loads_kw = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list,
        help_text=("Typical load over all hours in one year. Must be hourly (8,760 samples), 30 minute (17,"
                   "520 samples), or 15 minute (35,040 samples). All non-net load values must be greater than or "
                   "equal to zero. "
                   ),
        null=True,
        blank=True
    )
    critical_loads_kw = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list,
        help_text=("Critical load during an outage period. Must be hourly (8,760 samples), 30 minute (17,520 samples),"
                   "or 15 minute (35,040 samples). All non-net load values must be greater than or equal to zero."
                   ),
        null=True,
        blank=True
    )
    loads_kw_is_net = models.BooleanField(
        null=True,
        blank=True,
        default=True,
        help_text=("If there is existing PV, must specify whether provided load is the net load after existing PV or "
                   "not.")
    )
    critical_loads_kw_is_net = models.BooleanField(
        null=True,
        blank=True,
        default=False,
        help_text=("If there is existing PV, must specify whether provided load is the net load after existing PV or "
                   "not.")
    )
    outage_start_time_step = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(35040)
        ],
        help_text="Time step that grid outage starts. Must be less than outage_end."
    )

    outage_end_time_step = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(35040)
        ],
        help_text="Time step that grid outage ends. Must be greater than outage_start."
    )
    critical_load_pct = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(2)
        ],
        default=0.5,
        help_text="Critical load factor is multiplied by the typical load to determine the critical load that must be "
                  "met during an outage. Value must be between zero and one, inclusive."

    )
    outage_is_major_event = models.BooleanField(
        null=True,
        blank=True,
        default=True,
        help_text="Boolean value for if outage is a major event, which affects the avoided_outage_costs_us_dollars. If "
                  "True, the avoided outage costs are calculated for a single outage occurring in the first year of "
                  "the analysis_years. If False, the outage event is assumed to be an average outage event that occurs "
                  "every year of the analysis period. In the latter case, the avoided outage costs for one year are "
                  "escalated and discounted using the escalation_pct and offtaker_discount_pct to account for an "
                  "annually recurring outage. (Average outage durations for certain utility service areas can be "
                  "estimated using statistics reported on EIA form 861.)"
    )

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
    # Inputs
    run_uuid = models.UUIDField(unique=True)
    urdb_utility_name = models.TextField(
        blank=True,
        help_text=("Name of Utility from  <a href='https: //openei.org/wiki/Utility_Rate_Database' target='blank'>"
                  "Utility Rate Database</a>")
    )
    urdb_rate_name = models.TextField(
        blank=True,
        help_text=("Name of utility rate from  <a href='https: //openei.org/wiki/Utility_Rate_Database' target='blank'>"
                  "Utility Rate Database</a>")
    )
    urdb_label = models.TextField(
        blank=True,
        help_text=("Label attribute of utility rate structure from <a href='https: //openei.org/services/doc/rest/util_"
                  "rates/?version=3' target='blank'>Utility Rate Database API</a>")
    )
    blended_monthly_rates_us_dollars_per_kwh = ArrayField(
        models.FloatField(blank=True),
        default=list,
        null=True,
        help_text=("Array (length of 12) of blended energy rates (total monthly energy in kWh divided by monthly cost "
                  "in $)")
    )

    blended_monthly_demand_charges_us_dollars_per_kw = ArrayField(
        models.FloatField(null=True, blank=True),
        default=list,
        null=True,
        help_text=("Array (length of 12) of blended demand charges (demand charge cost in $ divided by monthly peak "
                  "demand in kW)")
    )

    blended_annual_rates_us_dollars_per_kwh = models.FloatField(
        blank=True,
        default=0,
        null=True,
        help_text="Annual blended energy rate (total annual energy in kWh divided by annual cost in $)"
    )

    blended_annual_demand_charges_us_dollars_per_kw = models.FloatField(
        blank=True,
        default=0,
        null=True,
        help_text="Annual blended demand rates (annual demand charge cost in $ divided by annual peak demand in kW)"
    )
    net_metering_limit_kw = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        default=0,
        null=True,
        blank=True,
        help_text="Upper limit on the total capacity of technologies that can participate in net metering agreement."
    )
    interconnection_limit_kw = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        default=1.0e8,
        null=True,
        blank=True,
        help_text="Limit on system capacity size that can be interconnected to the grid"
    )
    wholesale_rate_us_dollars_per_kwh = ArrayField(
        models.FloatField(null=True, blank=True),
        validators=[
            MinValueValidator(0)
        ],
        default=0,
        help_text=("Price of electricity sold back to the grid in absence of net metering or above net metering limit. "
                  " The total annual kWh that can be compensated under this rate is restricted to the total annual "
                  "site-load in kWh. Can be a scalar value, which applies for all-time, or an array with time-sensitive"
                  " values. If an array is input then it must have a length of 8760, 17520, or 35040. The inputed array"
                  "values are up/down-sampled using mean values to match the Scenario time_steps_per_hour. ")

    )
    wholesale_rate_above_site_load_us_dollars_per_kwh = ArrayField(
        models.FloatField(null=True,
                          blank=True,
                          default=list),
        validators=[
            MinValueValidator(0)
        ],
        default=0,
        help_text=("Price of electricity sold back to the grid above the site load, regardless of net metering.  Can be "
                  "a scalar value, which applies for all-time, or an array with time-sensitive values. If an array is "
                  "input then it must have a length of 8760, 17520, or 35040. The inputed array values are up/down-"
                  "sampled using mean values to match the Scenario time_steps_per_hour.")

    )
    urdb_response = PickledObjectField(
        null=True,
        editable=True,
        blank=True,
        help_text=("Utility rate structure from <a href='https: //openei.org/services/doc/rest/util_rates/?version=3' "
                  "target='blank'>Utility Rate Database API</a>")

    )
    add_blended_rates_to_urdb_rate = models.BooleanField(
        null=True,
        blank=True,
        default=False,
        help_text=("Set to 'true' to add the monthly blended energy rates and demand charges to the URDB rate schedule. "
                  "Otherwise, blended rates will only be considered if a URDB rate is not provided. ")

    )
    add_tou_energy_rates_to_urdb_rate = models.BooleanField(
        null=True,
        blank=True,
        default=False,
        help_text=("Set to 'true' to add the tou  energy rates to the URDB rate schedule. Otherwise, tou energy rates "
                  "will only be considered if a URDB rate is not provided. ")

    )
    tou_energy_rates_us_dollars_per_kwh = ArrayField(
        models.FloatField(
            null=True,
            blank=True),
        null=True,
        default=list,
        help_text=("Time-of-use energy rates, provided by user. Must be an array with length equal to number of "
                  "timesteps per year. Hourly or 15 minute rates allowed.")

    )
    emissions_factor_series_lb_CO2_per_kwh = ArrayField(
        models.FloatField(
            null=True,
            blank=True),
        null=True,
        default=list,
        help_text=("Carbon Dioxide emissions factor over all hours in one year. Can be provided as either a single "
                  "constant fraction that will be applied across all timesteps, or an annual timeseries array at an "
                  "hourly (8,760 samples), 30 minute (17,520 samples), or 15 minute (35,040 samples) resolution."),

    )
    chp_standby_rate_us_dollars_per_kw_per_month = models.FloatField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1000)
        ],
        default=0,
        help_text="Standby rate charged to CHP based on CHP electric power size"

    )

    chp_does_not_reduce_demand_charges = models.BooleanField(
        null=True,
        blank=True,
        default=False,
        help_text="Boolean indicator if CHP does not reduce demand charges"
    )

    emissions_region = models.TextField(
        null=True,
        blank=True
    )
    coincident_peak_load_active_timesteps = ArrayField(
        ArrayField(
            models.FloatField(
                null=True,
                blank=True),
            null=True,
            default=list),
        null=True,
        default=list,
        help_text=("The optional coincident_peak_load_charge_us_dollars_per_kw will apply at the max grid-purchased "
                  "power during these timesteps. Note timesteps are indexed to a base of 1 not 0.")

    )
    coincident_peak_load_charge_us_dollars_per_kw = ArrayField(
        models.FloatField(
            null=True,
            blank=True,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(1.0e8)
            ],
        ),
        null=True,
        default=list,
        help_text=("Optional coincident peak demand charge that is applied to the max load during the timesteps "
                  "specified in coincident_peak_load_active_timesteps")
    )

    def clean(self):
        error_messages = []

        # possible sets for defining tariff
        if not at_least_one_set(self.dict, self.possible_sets):
            error_messages.append((
                "Must provide at valid at least one set of valid inputs from {}.".format(self.possible_sets)
            ))

        if error_messages:
            raise ValidationError(' & '.join(error_messages))


class LoadProfileChillerThermalInputs(BaseModel, models.Model):
    # Inputs
    run_uuid = models.UUIDField(unique=True)
    loads_ton = ArrayField(
        models.FloatField(
            null=True,
            blank=True),
        default=list,
        null=True,
        help_text="Typical electric chiller load for all hours in one year."
    )
    annual_tonhour = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e8)
        ],
        help_text=("Annual electric chiller energy consumption, in ton-hours, used to scale simulated default electric "
                   "chiller load profile for the site's climate zone")

    )
    monthly_tonhour = ArrayField(
        models.FloatField(
            blank=True,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(1.0e8)
            ]
        ),
        default=list,
        null=True,
        help_text=("Monthly electric chiller energy consumption series (an array 12 entries long), in ton-hours, used "
                   "to scale simulated default electric chiller load profile for the site's climate zone")

    )
    annual_fraction = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=("Annual electric chiller energy consumption scalar (i.e. fraction of total electric load, used to "
                   "scale simulated default electric chiller load profile for the site's climate zone"),

    )
    monthly_fraction = ArrayField(
        models.FloatField(
            blank=True,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(1)
            ]
        ),
        default=list,
        null=True,
        help_text=("Monthly electric chiller energy consumption scalar series (i.e. 12 fractions of total electric "
                  "load by month), used to scale simulated default electric chiller load profile for the site's "
                  "climate zone.")

    )
    loads_fraction = ArrayField(
        models.FloatField(
            blank=True,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(1.0e8)
            ]
        ),
        default=list,
        null=True,
        help_text=("Typical electric chiller load proporion of electric load series (unit is a percent) for all time "
                   "steps in one year.")
    )
    doe_reference_name = ArrayField(
        models.TextField(null=True, blank=True), default=list, null=True)
    percent_share = ArrayField(
        models.FloatField(
            null=True,
            blank=True,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(100)
            ]
        ),
        default=list,
        null=True,
        help_text=("Percentage share of the types of building for creating hybrid simulated building and campus "
                   "profiles.")
    )
    chiller_cop = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(20)
        ],
        help_text=("Existing electric chiller system coefficient of performance - conversion of electricity to usable "
                   "cooling thermal energy")
    )

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj
