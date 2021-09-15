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
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
import copy
import sys
import traceback as tb
import warnings
import logging

log = logging.getLogger(__name__)

"""
Running list of changes from v1 to document:
- flattened the input/output structure
- moved any inputs that are not needed for REopt optimization to Scenario
    - moved Site.address to Scenario
- moved Site attributes only needed for CHP to CHP
    - moved Site.elevation_ft to CHP
    - moved Site.outdoor_air_temp_degF to CHP
- Financial.total_om_costs and Financial.year_one_om_costs -> *_after_tax appended to name for clarity
- moved power and energy outputs related to the grid from ElectricTariff to ElectricUtility
- `existing_gen_*` Generator outputs now just have `_bau` appended to the name (removed `existing_gen_`)
- remove "_series" from cashflow outputs
- irr_pct -> internal_rate_of_return
- resilience_check_flag -> bau_critical_load_met
- remove year_one_power_production_series_kw for all techs (b/c it is the sum of other outputs and we want to cut down on the 
    amount of data in every response)
- existing_pv_om_cost -> PV.total_om_cost_bau
- average_yearly_* outputs -> average_annual_* (we had a mix before)
"""

# TODO add related_name field to all OneToOne Scenario's
"""
When editing this file help_text must have the following punctuation:
    1- One line of text must be enclosed by quotes, example:
      help_text="The number of seconds allowed before the optimization times out."
    2- More than one line of text must be enclosed by quotes within parentheses, example: 
      help_text=("The threshold for the difference between the solution's objective value and the best possible "
                 "value at which the solver terminates")

Can we use:
django.db.models.Model
for all that nested_inputs provides, and some validation? YES!

https://docs.djangoproject.com/en/3.1/ref/models/fields/#validators

max/min   https://docs.djangoproject.com/en/3.1/ref/validators/#maxvaluevalidator

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
- start all Model fields with required fields (do not need to include `blank` b/c the default value of blank is False)
- TextField and CharField should not have null=True
- description: use square brackets for units, eg. [dollars per kWh]

Input and Results models
test type validation for multiple fields, need to override clean_fields to go through all fields before raising ValidationError?

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
                errors[f.key] = e.error_list

        if errors:
            raise ValidationError(errors)


Output models need to have null=True, blank=True for cases when results are not generated 
(when errors occur during solve or post-processing)
           
"""
# TODO check all fields (do we really want so many null's allowed? are the blank=True all correct? Can we add more defaults)

MAX_BIG_NUMBER = 1.0e8
MAX_INCENTIVE = 1.0e10
MAX_YEARS = 75


class MACRS_YEARS_CHOICES(models.IntegerChoices):
    ZERO = 0
    FIVE = 5
    SEVEN = 7


def at_least_one_set(model, possible_sets):
    """
    Check if at least one set of possible_sets are defined in the Model.dict
    :param model: BaseModel.dict
    :param possible_sets: list of lists (of str)
    :return: Bool, True if the BaseModel.dict includes non-empty or non-null values for at least one set of keys in
        possible_sets
    """
    case = False
    for list_of_keys in possible_sets:
        if all(model.get(key) not in [None, "", []] for key in list_of_keys):
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
        d.pop("scenario_id", None)
        return d

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        return obj


class Scenario(BaseModel, models.Model):
    """
    All the values specific to API (and not used in Julia package)
    """
    key = "Scenario"

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
    address = models.TextField(
        blank=True,
        help_text="A user defined address as optional metadata (street address, city, state or zip code)"
    )


class Settings(BaseModel, models.Model):
    key = "Settings"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="Settings"
    )

    class TIME_STEP_CHOICES(models.IntegerChoices):
        ONE = 1
        TWO = 2
        FOUR = 4

    timeout_seconds = models.IntegerField(
        default=420,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(420)
        ],
        help_text="The number of seconds allowed before the optimization times out."
    )
    time_steps_per_hour = models.IntegerField(
        default=TIME_STEP_CHOICES.ONE,
        choices=TIME_STEP_CHOICES.choices,
        help_text="The number of time steps per hour in the REopt model."
    )
    optimality_tolerance = models.FloatField(
        default=0.001,
        validators=[
            MinValueValidator(5.0e-6),
            MaxValueValidator(0.05)
        ],
        help_text=("The threshold for the difference between the solution's objective value and the best possible "
                   "value at which the solver terminates")
    )
    add_soc_incentive = models.BooleanField(
        default=True,
        blank=True,
        help_text=("If True, then a small incentive to keep the battery's state of charge high is added to the "
                   "objective of the optimization.")
    )


class SiteInputs(BaseModel, models.Model):
    key = "Site"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="SiteInputs",
    )

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
    land_acres = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1000000)
        ],
        null=True, blank=True,
        help_text="Land area in acres available for PV panel siting"
    )
    roof_squarefeet = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1000000000)
        ],
        null=True, blank=True,
        help_text="Area of roof in square feet available for PV siting"
    )
    # TODO move elevation_ft to CHP model
    # elevation_ft = models.FloatField(
    #     default=0,
    #     validators=[
    #         MinValueValidator(0),
    #         MaxValueValidator(15000)
    #     ],
    #     null=True, blank=True,
    #     help_text="Site elevation (above sea sevel), units of feet"
    # )
    # TODO move outdoor_air_temp_degF to CHP model
    # outdoor_air_temp_degF = ArrayField(
    #     models.FloatField(
    #         null=True, blank=True,
    #         help_text="Hourly outdoor air temperature (dry-bulb)."
    #     ),
    #     default=list, null=True)

"""
# TODO should we move the emissions_calculator to Julia? 
# Or is it supplanted by new emissions capabilities (not in develop/master as of 21.09.02)?

class SiteOutputs(BaseModel, models.Model):
    key = "SiteOutputs"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    year_one_emissions_lb_C02 = models.FloatField(
        null=True, blank=True,
        help_text="Total equivalent pounds of carbon dioxide emitted from the site in the first year."
    )
    year_one_emissions_bau_lb_C02 = models.FloatField(
        null=True, blank=True,
        help_text="Total equivalent pounds of carbon dioxide emittedf rom the site use in the first year in the BAU case."
    )
    renewable_electricity_energy_pct = models.FloatField(
        null=True, blank=True,
        help_text=("Portion of electrictrity use that is derived from on-site "
                    "renewable resource generation in year one. Calculated as "
                    "total PV and Wind generation in year one (including exports), "
                    "divided by the total annual load in year one.")
    )
"""


class FinancialInputs(BaseModel, models.Model):
    key = "Financial"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="FinancialInputs"
    )

    # Inputs
    analysis_years = models.IntegerField(
        default=25,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(75)
        ],
        null=True, blank=True,
        help_text="Analysis period in years. Must be integer."
    )
    elec_cost_escalation_pct = models.FloatField(
        default=0.023,
        validators=[
            MinValueValidator(-1),
            MaxValueValidator(1)
        ],
        null=True, blank=True,
        help_text="Annual nominal utility electricity cost escalation rate."
    )
    offtaker_discount_pct = models.FloatField(
        default=0.083,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        null=True, blank=True,
        help_text=("Nominal energy offtaker discount rate. In single ownership model the offtaker is also the "
                   "generation owner.")
    )
    offtaker_tax_pct = models.FloatField(
        default=0.26,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(0.999)
        ],
        null=True, blank=True,
        help_text="Host tax rate"
    )
    om_cost_escalation_pct = models.FloatField(
        default=0.025,
        validators=[
            MinValueValidator(-1),
            MaxValueValidator(1)
        ],
        null=True, blank=True,
        help_text="Annual nominal O&M cost escalation rate"
    )
    owner_discount_pct = models.FloatField(
        default=0.083,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        null=True, blank=True,
        help_text=("Nominal generation owner discount rate. Used for two party financing model. In two party ownership "
                   "model the offtaker does not own the generator(s).")
    )
    owner_tax_pct = models.FloatField(
        default=0.26,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(0.999)
        ],
        null=True, blank=True,
        help_text=("Generation owner tax rate. Used for two party financing model. In two party ownership model the "
                   "offtaker does not own the generator(s).")
    )
    third_party_ownership = models.BooleanField(
        default=False,
        null=True, blank=True,
        help_text=("Specify if ownership model is direct ownership or two party. In two party model the offtaker does "
                   "not purcharse the generation technologies, but pays the generation owner for energy from the "
                   "generator(s).")
    )
    value_of_lost_load_per_kwh = models.FloatField(
        default=100,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1e6)
        ],
        blank=True,
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
        blank=True,
        help_text=("Additional cost, in percent of non-islandable capital costs, to make a distributed energy system "
                   "islandable from the grid and able to serve critical loads. Includes all upgrade costs such as "
                   "additional laber and critical load panels.")
    )
    # boiler_fuel_escalation_pct = models.FloatField(
    #     default=0.034,
    #     validators=[
    #         MinValueValidator(-1),
    #         MaxValueValidator(1)
    #     ],
    #     null=True, blank=True,
    #     help_text=("Annual nominal boiler fuel cost escalation rate")
    # )
    # chp_fuel_escalation_pct = models.FloatField(
    #     default=0.034,
    #     validators=[
    #         MinValueValidator(-1),
    #         MaxValueValidator(1)
    #     ],
    #     null=True, blank=True,
    #     help_text=("Annual nominal chp fuel cost escalation rate")
    # )


class FinancialOutputs(BaseModel, models.Model):
    key = "FinancialOutputs"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="FinancialOutputs",
        primary_key=True
    )

    lcc = models.FloatField(
        null=True, blank=True,
        help_text="Optimal lifecycle cost"
    )
    lcc_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual lifecycle cost"
    )
    npv = models.FloatField(
        null=True, blank=True,
        help_text="Net present value of savings realized by the project"
    )
    net_capital_costs_plus_om = models.FloatField(
        null=True, blank=True,
        help_text="Capital cost for all technologies plus present value of operations and maintenance over anlaysis period"
    )
    net_om_costs_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business-as-usual present value of operations and maintenance over anlaysis period",
    )
    net_capital_costs = models.FloatField(
        null=True, blank=True,
        help_text="Net capital costs for all technologies, in present value, including replacement costs and incentives."
    )
    microgrid_upgrade_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Cost to make a distributed energy system islandable from the grid. Determined by multiplying the "
            "total capital costs of resultant energy systems from REopt (such as PV and Storage system) with the input "
            "value for microgrid_upgrade_cost_pct (which defaults to 0.30).")
    )
    initial_capital_costs = models.FloatField(
        null=True, blank=True,
        help_text="Up-front capital costs for all technologies, in present value, excluding replacement costs and incentives."
    )
    initial_capital_costs_after_incentives = models.FloatField(
        null=True, blank=True,
        help_text="Up-front capital costs for all technologies, in present value, excluding replacement costs, including incentives."
    )
    replacement_costs = models.FloatField(
        null=True, blank=True,
        help_text="Net replacement costs for all technologies, in future value, excluding incentives."
    )
    om_and_replacement_present_cost_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Net O&M and replacement costs in present value, after-tax."
    )
    total_om_costs_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Total operations and maintenance cost over analysis period after tax."
    )
    year_one_om_costs_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Year one operations and maintenance cost after tax."
    )
    total_om_costs_before_tax = models.FloatField(
        null=True, blank=True,
        help_text="Total operations and maintenance cost over analysis period before tax."
    )
    year_one_om_costs_before_tax = models.FloatField(
        null=True, blank=True,
        help_text="Year one operations and maintenance cost before tax."
    )
    simple_payback_years = models.FloatField(
        null=True, blank=True,
        help_text=("Number of years until the cumulative annual cashflows turn positive. "
            "If the cashflows become negative again after becoming positive (i.e. due to battery repalcement costs)"
            " then simple payback is increased by the number of years that the cash flow "
            "is negative beyond the break-even year.")
    )
    internal_rate_of_return = models.FloatField(
        null=True, blank=True,
        help_text=("internal Rate of Return of the cost-optimal system. In two-party cases the "
                   "developer discount rate is used in place of the offtaker discount rate.")
    )
    net_present_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Present value of the total costs incurred by the third-party owning and operating the "
                    "distributed energy resource assets.")
    )
    annualized_payment_to_third_party = models.FloatField(
        null=True, blank=True,
        help_text=("The annualized amount the host will pay to the third-party owner over the life of the project.")
    )
    offtaker_annual_free_cashflows = ArrayField(
        models.FloatField(
            blank=True
        ), 
        default=list, blank=True,
        help_text=("Annual free cashflows for the host in the optimal case for all analysis years, "
                    "including year 0. Future years have not been discounted to account for the time value of money.")
    )
    offtaker_discounted_annual_free_cashflows = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list, blank=True,
        help_text=("Annual discounted free cashflows for the host in the optimal case for all analysis years, "
                    "including year 0. Future years have been discounted to account for the time value of money.")
    )
    offtaker_annual_free_cashflows_bau = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list, blank=True,
        help_text=("Annual free cashflows for the host in the business-as-usual case for all analysis years, "
                    "including year 0. Future years have not been discounted to account for the time value of "
                    "money. Only calculated in the non-third-party case.")
    )
    offtaker_discounted_annual_free_cashflows_bau = ArrayField(
        models.FloatField(
            null=True, blank=True
        ),
        default=list, blank=True,
        null=True,
        help_text=("Annual discounted free cashflow for the host in the business-as-usual case for all analysis "
                   "years, including year 0. Future years have been discounted to account for the time value of "
                   "money. Only calculated in the non-third-party case.")
    )
    developer_annual_free_cashflows = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list, blank=True,
        help_text=("Annual free cashflow for the developer in the business-as-usual third party case for all "
                   "analysis years, including year 0. Future years have not been discounted to account for "
                   "the time value of money. Only calculated in the third-party case.")
    )
    developer_om_and_replacement_present_cost_after_tax = models.FloatField(
        null=True, blank=True,
        help_text=("Net O&M and replacement costs in present value, after-tax for the third-party developer."
                   "Only calculated in the third-party case.")
    )


class ElectricLoadInputs(BaseModel, models.Model):
    key = "ElectricLoad"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="ElectricLoadInputs",
    )

    possible_sets = [
        ["loads_kw"],
        ["doe_reference_name", "monthly_totals_kwh"],
        ["annual_kwh", "doe_reference_name"],
        ["doe_reference_name"]
    ]

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

    annual_kwh = models.FloatField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100000000)
        ],
        null=True, blank=True,
        help_text=("Annual site energy consumption from electricity, in kWh, used to scale simulated default building load profile for the site's climate zone")
    )
    # TODO make doe_reference_name ArrayField after adding blended profile capability to Julia pkg
    doe_reference_name = models.TextField(
        null=False,
        blank=True,  # TODO do we have to include "" in choices for blank=True to work?
        choices=DOE_REFERENCE_NAME.choices,
        help_text=("Simulated load profile from DOE <a href='https: "
                   "//energy.gov/eere/buildings/commercial-reference-buildings' target='blank'>Commercial Reference "
                   "Buildings</a>")
    )
    year = models.IntegerField(
        default=2020,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9999)
        ],
        null=True, blank=True,
        help_text=("Year of Custom Load Profile. If a custom load profile is uploaded via the loads_kw parameter, it "
                   "is important that this year correlates with the load profile so that weekdays/weekends are "
                   "determined correctly for the utility rate tariff. If a DOE Reference Building profile (aka "
                   "'simulated' profile) is used, the year is set to 2017 since the DOE profiles start on a Sunday.")
    )
    monthly_totals_kwh = ArrayField(
        models.FloatField(
            validators=[
                MinValueValidator(0),
                MaxValueValidator(1.0e8)
            ],
            blank=True
        ),
        default=list, blank=True,
        help_text=("Monthly site energy consumption from electricity series (an array 12 entries long), in kWh, used "
                   "to scale simulated default building load profile for the site's climate zone")
    )
    loads_kw = ArrayField(
        models.FloatField(blank=True),
        default=list, blank=True,
        help_text=("Typical load over all hours in one year. Must be hourly (8,760 samples), 30 minute (17,"
                   "520 samples), or 15 minute (35,040 samples). All non-net load values must be greater than or "
                   "equal to zero. "
                   )
    )
    critical_loads_kw = ArrayField(
        models.FloatField(blank=True),
        default=list, blank=True,
        help_text=("Critical load during an outage period. Must be hourly (8,760 samples), 30 minute (17,520 samples),"
                   "or 15 minute (35,040 samples). All non-net load values must be greater than or equal to zero."
                   )
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
    # outage_is_major_event = models.BooleanField(
    #     null=True,
    #     blank=True,
    #     default=True,
    #     help_text="Boolean value for if outage is a major event, which affects the avoided_outage_costs. If "
    #               "True, the avoided outage costs are calculated for a single outage occurring in the first year of "
    #               "the analysis_years. If False, the outage event is assumed to be an average outage event that occurs "
    #               "every year of the analysis period. In the latter case, the avoided outage costs for one year are "
    #               "escalated and discounted using the escalation_pct and offtaker_discount_pct to account for an "
    #               "annually recurring outage. (Average outage durations for certain utility service areas can be "
    #               "estimated using statistics reported on EIA form 861.)"
    # )
    # percent_share = ArrayField(
    #     models.FloatField(
    #         default=100,
    #         validators=[
    #             MinValueValidator(1),
    #             MaxValueValidator(100)
    #         ],
    #         blank=True
    #     ),
    #     default=list,
    #     null=True, blank=True,
    #     help_text=("Percentage share of the types of building for creating hybrid simulated building and campus "
    #                "profiles.")
    # )

    def clean(self):
        error_messages = []

        # possible sets for defining load profile
        if not at_least_one_set(self.dict, self.possible_sets):
            error_messages.append((
                "Must provide at valid at least one set of valid inputs from {}.".format(self.possible_sets)
            ))

        if error_messages:
            raise ValidationError(' & '.join(error_messages))


class ElectricLoadOutputs(BaseModel, models.Model):
    key = "ElectricLoadOutputs"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="ElectricLoadOutputs"
    )

    load_series_kw = ArrayField(
        models.FloatField(
            null=True, blank=True
        ), 
        default=list,
        help_text="Year one hourly time series of electric load"
    )
    critical_load_series_kw = ArrayField(
        models.FloatField(
            null=True, blank=True
        ), 
        default=list,
        help_text=("Hourly critical load for outage simulator. Values are either uploaded by user, "
                   "or determined from typical load (either uploaded or simulated) and critical_load_pct.")
    )
    annual_calculated_kwh = models.FloatField(
        null=True, blank=True,
        help_text="Annual energy consumption calculated by summing up 8760 load profile"
    )
    bau_critical_load_met = models.BooleanField(
        null=True, blank=True,
        help_text="Boolean for if the critical load is met by the existing technologies in the BAU scenario."
    )
    bau_critical_load_met_time_steps = models.IntegerField(
        null=True, blank=True,
        help_text="Number of time steps the existing system can sustain the critical load."
    )


class ElectricTariffInputs(BaseModel, models.Model):
    key = "ElectricTariff"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="ElectricTariffInputs",
    )

    possible_sets = [
        ["urdb_response"],
        ["monthly_demand_rates", "monthly_energy_rates"],
        ["blended_annual_energy_rate", "blended_annual_demand_charge"],
        ["urdb_label"],
        ["urdb_utility_name", "urdb_rate_name"],
        # ["tou_energy_rates_per_kwh"]
    ]

    monthly_demand_rates = ArrayField(
        models.FloatField(blank=True),
        default=list, blank=True,
        size=12,
        help_text="Array (length of 12) of blended demand charges in dollars per kW"
    )
    monthly_energy_rates = ArrayField(
        models.FloatField(blank=True),
        default=list, blank=True,
        size=12,
        help_text="Array (length of 12) of blended energy rates in dollars per kWh."
    )
    urdb_label = models.TextField(
        blank=True,
        help_text=("Label attribute of utility rate structure from <a href='https://openei.org/services/doc/rest/util_rates/?version=3' target='blank'>Utility Rate Database API</a>")
    )
    urdb_response = PickledObjectField(
        null=True, blank=True,
        editable=True,
        help_text=("Utility rate structure from <a href='https://openei.org/services/doc/rest/util_rates/?version=3' target='blank'>Utility Rate Database API</a>")
    )
    urdb_rate_name = models.TextField(
        blank=True,
        help_text=("Name of utility rate from <a href='https://openei.org/wiki/Utility_Rate_Database' target='blank'>Utility Rate Database</a>")
    )
    urdb_utility_name = models.TextField(
        blank=True,
        help_text=("Name of Utility from <a href='https://openei.org/wiki/Utility_Rate_Database' target='blank'>Utility Rate Database</a>")
    )
    blended_annual_demand_charge = models.FloatField(
        blank=True,
        null=True,
        help_text="Annual blended demand rates (annual demand charge cost in $ divided by annual peak demand in kW)"
    )
    blended_annual_energy_rate = models.FloatField(
        blank=True,
        null=True,
        help_text="Annual blended energy rate (total annual energy in kWh divided by annual cost in $)"
    )
    wholesale_rate = ArrayField(
        models.FloatField(
            blank=True,
            validators=[
                MinValueValidator(0)
            ]
        ),
        default=list, blank=True,
        help_text=("Price of electricity sold back to the grid in absence of net metering."
                  " Can be a scalar value, which applies for all-time, or an array with time-sensitive"
                  " values. If an array is input then it must have a length of 8760, 17520, or 35040. The inputed array"
                  "values are up/down-sampled using mean values to match the Settings.time_steps_per_hour.")
    )
    export_rate_beyond_net_metering_limit = ArrayField(
        models.FloatField(
            blank=True,
            default=0,
            validators=[
                MinValueValidator(0)
            ]
        ),
        default=list,
        blank=True,
        help_text=("Price of electricity sold back to the grid above the site load, regardless of net metering.  Can be "
                  "a scalar value, which applies for all-time, or an array with time-sensitive values. If an array is "
                  "input then it must have a length of 8760, 17520, or 35040. The inputed array values are up/down-"
                  "sampled using mean values to match the Scenario time_steps_per_hour.")
    )
    # tou_energy_rates_per_kwh = ArrayField(
    #     models.FloatField(blank=True),
    #     default=list,
    #     null=True, blank=True,
    #     help_text=("Time-of-use energy rates, provided by user. Must be an array with length equal to number of "
    #               "timesteps per year. Hourly or 15 minute rates allowed.")
    # )
    # add_blended_rates_to_urdb_rate = models.BooleanField(
    #     blank=True,
    #     default=False,
    #     help_text=("Set to 'true' to add the monthly blended energy rates and demand charges to the URDB rate schedule. "
    #               "Otherwise, blended rates will only be considered if a URDB rate is not provided. ")
    #
    # )
    # add_tou_energy_rates_to_urdb_rate = models.BooleanField(
    #     blank=True,
    #     default=False,
    #     help_text=("Set to 'true' to add the tou  energy rates to the URDB rate schedule. Otherwise, tou energy rates "
    #               "will only be considered if a URDB rate is not provided. ")
    #
    # )
    # chp_does_not_reduce_demand_charges = models.BooleanField(
    #     default=False,
    #     blank=True,
    #     help_text=("Boolean indicator if CHP does not reduce demand charges")
    # )
    # chp_standby_rate_per_kw_per_month = models.FloatField(
    #     default=0,
    #     validators=[
    #         MinValueValidator(0),
    #         MaxValueValidator(1000)
    #     ],
    #     null=True, blank=True,
    #     help_text=("Standby rate charged to CHP based on CHP electric power size")
    # )
    # emissions_factor_series_lb_CO2_per_kwh = ArrayField(
    #     models.FloatField(blank=True),
    #     null=True, blank=True,
    #     default=list,
    #     help_text=("Carbon Dioxide emissions factor over all hours in one year. Can be provided as either a single "
    #               "constant fraction that will be applied across all timesteps, or an annual timeseries array at an "
    #               "hourly (8,760 samples), 30 minute (17,520 samples), or 15 minute (35,040 samples) resolution.")
    # )
    # coincident_peak_load_active_timesteps = ArrayField(
    #     ArrayField(
    #         models.FloatField(blank=True),
    #         null=True, blank=True,
    #         default=list),
    #     null=True, blank=True,
    #     default=list,
    #     help_text=("The optional coincident_peak_load_charge_per_kw will apply at the max grid-purchased "
    #               "power during these timesteps. Note timesteps are indexed to a base of 1 not 0.")
    # )
    # coincident_peak_load_charge_per_kw = ArrayField(
    #     models.FloatField(
    #         blank=True,
    #         validators=[
    #             MinValueValidator(0),
    #             MaxValueValidator(1.0e8)
    #         ],
    #     ),
    #     null=True, blank=True,
    #     default=list,
    #     help_text=("Optional coincident peak demand charge that is applied to the max load during the timesteps "
    #               "specified in coincident_peak_load_active_timesteps")
    # )

    def clean(self):
        error_messages = []

        # possible sets for defining tariff
        if not at_least_one_set(self.dict, self.possible_sets):
            error_messages.append((
                "Must provide at valid at least one set of valid inputs from {}.".format(self.possible_sets)
            ))

        for possible_set in self.possible_sets:
            if len(possible_set) == 2:  # check dependencies
                if (possible_set[0] and not possible_set[1]) or (not possible_set[0] and possible_set[1]):
                    error_messages.append(f"Must provide both {possible_set[0]} and {possible_set[1]}")

        if len(self.wholesale_rate) == 1:
            self.wholesale_rate = self.wholesale_rate * 8760  # upsampling handled in InputValidator.cross_clean

        if error_messages:
            raise ValidationError(' & '.join(error_messages))


class ElectricUtilityInputs(BaseModel, models.Model):
    key = "ElectricUtility"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="ElectricUtilityInputs",
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
    interconnection_limit_kw = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        default=1.0e9,
        blank=True,
        help_text="Limit on total system capacity that can be interconnected to the grid"
    )
    net_metering_limit_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        null=True, blank=True,
        help_text="Upper limit on the total capacity of technologies that can participate in net metering agreement."
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
                    'outage_end_time_step must be larger than outage_start_time_step and these inputs '
                    'cannot be equal.'
                ))

        if error_messages:
            raise ValidationError(' & '.join(error_messages))


class ElectricUtilityOutputs(BaseModel, models.Model):
    key = "ElectricUtilityOutputs"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="ElectricUtilityOutputs",
    )

    year_one_to_load_series_kw = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list, blank=True,
        help_text=("Optimal year one grid to load time series")
    )
    year_one_to_load_series_kw_bau = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list, blank=True,
        help_text=("Business as usual year one grid to load time series")
    )
    year_one_to_battery_series_kw = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list, blank=True,
        help_text=("Optimal year one grid to battery time series")
    )
    year_one_energy_supplied_kwh = models.FloatField(
        null=True, blank=True,
        help_text=("Year one energy supplied from grid to load")
    )
    year_one_energy_supplied_kwh_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Year one energy supplied from grid to load")
    )
    year_one_emissions_lb_C02 = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal year one equivalent pounds of carbon dioxide emitted from utility electricity use. "
                    "Calculated from EPA AVERT region hourly grid emissions factor series for the continental US."
                    "In AK and HI, the best available data are EPA eGRID annual averages.")
    )
    year_one_emissions_bau_lb_C02 = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual year one equivalent pounds of carbon dioxide emitted from utility electricity use. "
                    "Calculated from EPA AVERT region hourly grid emissions factor series for the continental US."
                    "In AK and HI, the best available data are EPA eGRID annual averages.")
    )


class ElectricTariffOutputs(BaseModel, models.Model):
    key = "ElectricTariffOutputs"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="ElectricTariffOutputs",
    )

    emissions_region = models.TextField(
        null=True,
        blank=True
    )
    year_one_energy_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal year one utility energy cost")
    )
    year_one_demand_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal year one utility demand cost")
    )
    year_one_fixed_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal year one utility fixed cost")
    )
    year_one_min_charge_adder = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal year one utility minimum charge adder")
    )
    year_one_energy_cost_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual year one utility energy cost")
    )
    year_one_demand_cost_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual year one utility demand cost")
    )
    year_one_fixed_cost_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual year one utility fixed cost")
    )
    year_one_min_charge_adder_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual year one utility minimum charge adder")
    )
    total_energy_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal total utility energy cost over the analysis period, after-tax")
    )
    total_demand_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal total lifecycle utility demand cost over the analysis period, after-tax")
    )
    total_fixed_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal total utility fixed cost over the analysis period, after-tax")
    )
    total_min_charge_adder = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal total utility minimum charge adder over the analysis period, after-tax")
    )
    total_energy_cost_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual total utility energy cost over the analysis period, after-tax")
    )
    total_demand_cost_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual total lifecycle utility demand cost over the analysis period, after-tax")
    )
    total_fixed_cost_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual total utility fixed cost over the analysis period, after-tax")
    )
    total_min_charge_adder_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual total utility minimum charge adder over the analysis period, after-tax")
    )
    total_export_benefit = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal total value of exported energy over the analysis period, after-tax")
    )
    total_export_benefit_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual total value of exported energy over the analysis period, after-tax")
    )
    year_one_bill = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal year one total utility bill")
    )
    year_one_bill_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual year one total utility bill")
    )
    year_one_export_benefit = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal year one value of exported energy")
    )
    year_one_export_benefit_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual year one value of exported energy")
    )
    year_one_energy_cost_series_per_kwh = ArrayField(
        models.FloatField(
            blank=True
        ), 
        default=list, blank=True,
        help_text=("Optimal year one hourly energy costs")
    )
    year_one_demand_cost_series_per_kw = ArrayField(
        models.FloatField(
            blank=True
        ), 
        default=list, blank=True,
        help_text=("Optimal year one hourly demand costs")
    )
    year_one_coincident_peak_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal year one coincident peak charges")
    )
    year_one_coincident_peak_cost_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual year one coincident peak charges")
    )
    total_coincident_peak_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal total coincident peak charges over the analysis period, after-tax")
    )
    total_coincident_peak_cost_bau = models.FloatField(
        null=True, blank=True,
        help_text=("Business as usual total coincident peak charges over the analysis period, after-tax")
    )
    year_one_chp_standby_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal year one standby charge cost incurred by CHP")
    )
    total_chp_standby_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Optimal total standby charge cost incurred by CHP over the analysis period, after-tax")
    )


class PVInputs(BaseModel, models.Model):
    key = "PV"
    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="PVInputs",
        primary_key=True
    )
    
    class ARRAY_TYPE_CHOICES(models.IntegerChoices):
        GROUND_MOUNT_FIXED_OPEN_RACK = 0
        ROOFTOP_FIXED = 1
        GROUND_MOUNT_ONE_AXIS_TRACKING = 2
        ONE_AXIS_BACKTRACKING = 3
        GROUND_MOUNT_TWO_AXIS_TRACKING = 4

    class MODULE_TYPE_CHOICES(models.IntegerChoices):
        STANDARD = 0
        PREMIUM = 1
        THIN_FILM = 2

    class PV_LOCATION_CHOICES(models.TextChoices):
        ROOF = 'roof'
        GROUND = 'ground'
        BOTH = 'both'

    # number = models.IntegerField(
    #     null=True, blank=True,
    #     help_text="Index out of all PV system models"
    # )
    name = models.TextField(
        blank=True,
        default="PV",
        help_text="PV description for distinguishing between multiple PV models"
    )
    existing_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e5)
        ],
        blank=True,
        help_text="Existing PV size"
    )
    min_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Minimum PV size constraint for optimization"
    )
    max_kw = models.FloatField(
        default=1.0e9,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Maximum PV size constraint for optimization. Set to zero to disable PV"
    )
    installed_cost_per_kw = models.FloatField(
        default=1600,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e5)
        ],
        blank=True,
        help_text="Installed PV cost in $/kW"
    )
    om_cost_per_kw = models.FloatField(
        default=16,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e3)
        ],
        blank=True,
        help_text="Annual PV operations and maintenance costs in $/kW"
    )
    macrs_option_years = models.IntegerField(
        default=MACRS_YEARS_CHOICES.FIVE,
        choices=MACRS_YEARS_CHOICES.choices,
        blank=True,
        help_text="Duration over which accelerated depreciation will occur. Set to zero to disable"
    )
    macrs_bonus_pct = models.FloatField(
        default=1.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percent of upfront project costs to depreciate in year one in addition to scheduled depreciation"
    )
    macrs_itc_reduction = models.FloatField(
        default=0.5,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percent of the ITC value by which depreciable basis is reduced"
    )
    federal_itc_pct = models.FloatField(
        default=0.26,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percentage of capital costs that are credited towards federal taxes"
    )
    state_ibi_pct = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percentage of capital costs offset by state incentives"
    )
    state_ibi_max = models.FloatField(
        default=MAX_INCENTIVE,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_INCENTIVE)
        ],
        blank=True,
        help_text="Maximum dollar value of state percentage-based capital cost incentive"
    )
    utility_ibi_pct = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percentage of capital costs offset by utility incentives"
    )
    utility_ibi_max = models.FloatField(
        default=MAX_INCENTIVE,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_INCENTIVE)
        ],
        blank=True,
        help_text="Maximum dollar value of utility percentage-based capital cost incentive"
    )
    federal_rebate_per_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Federal rebates based on installed capacity"
    )
    state_rebate_per_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="State rebate based on installed capacity"
    )
    state_rebate_max = models.FloatField(
        default=MAX_INCENTIVE,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_INCENTIVE)
        ],
        blank=True,
        help_text="Maximum state rebate"
    )
    utility_rebate_per_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Utility rebate based on installed capacity"
    )
    utility_rebate_max = models.FloatField(
        default=MAX_INCENTIVE,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_INCENTIVE)
        ],
        blank=True,
        help_text="Maximum utility rebate"
    )
    production_incentive_per_kwh = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Production-based incentive value"
    )
    production_incentive_max_benefit = models.FloatField(
        default=1.0e9,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Maximum annual value in present terms of production-based incentives"
    )
    production_incentive_years = models.IntegerField(
        default=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        blank=True,
        help_text="Duration of production-based incentives from installation date"
    )
    production_incentive_max_kw = models.FloatField(
        default=1.0e9,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Maximum system size eligible for production-based incentive"
    )
    degradation_pct = models.FloatField(
        default=0.005,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Annual rate of degradation in PV energy production"
    )
    azimuth = models.FloatField(
        default=180,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(360)
        ],
        blank=True,
        help_text=("PV azimuth angle")
    )
    losses = models.FloatField(
        default=0.14,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(0.99)
        ],
        blank=True,
        help_text=("PV system performance losses")
    )
    array_type = models.IntegerField(
        default=ARRAY_TYPE_CHOICES.ROOFTOP_FIXED,
        choices=ARRAY_TYPE_CHOICES.choices,
        blank=True,
        help_text=("PV Watts array type (0: Ground Mount Fixed (Open Rack); 1: Rooftop, Fixed; 2: Ground Mount 1-Axis "
                   "Tracking; 3 : 1-Axis Backtracking; 4: Ground Mount, 2-Axis Tracking)")
    )
    module_type = models.IntegerField(
        default=MODULE_TYPE_CHOICES.STANDARD,
        choices=MODULE_TYPE_CHOICES.choices,
        blank=True,
        help_text="PV module type (0: Standard; 1: Premium; 2: Thin Film)"
    )
    gcr = models.FloatField(
        default=0.4,
        validators=[
            MinValueValidator(0.01),
            MaxValueValidator(0.99)
        ],
        null=True, blank=True,
        help_text=("PV ground cover ratio (photovoltaic array area : total ground area).")
    )
    dc_ac_ratio = models.FloatField(
        default=1.2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(2)
        ],
        blank=True,
        help_text="PV DC-AC ratio"
    )
    inv_eff = models.FloatField(
        default=0.96,
        validators=[
            MinValueValidator(0.9),
            MaxValueValidator(0.995)
        ],
        null=True, blank=True,
        help_text="PV inverter efficiency"
    )
    radius = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0)
        ],
        null=True, blank=True,
        help_text=("Radius, in miles, to use when searching for the closest climate data station. Use zero to use the "
                   "closest station regardless of the distance.")
    )
    tilt = models.FloatField(
        default=0.537,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(90)
        ],
        blank=True,
        help_text="PV system tilt"
    )
    location = models.TextField(
        default=PV_LOCATION_CHOICES.BOTH,
        choices=PV_LOCATION_CHOICES.choices,
        blank=True,
        help_text="Where PV can be deployed. One of [roof, ground, both] with default as both."
    )
    prod_factor_series_kw = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list, blank=True,
        help_text=("Optional user-defined production factors. Entries have units of kWh/kW, representing the energy "
                   "(kWh) output of a 1 kW system in each time step. Must be hourly (8,760 samples), 30 minute "
                   "(17,520 samples), or 15 minute (35,040 samples).")
    )
    can_net_meter = models.BooleanField(
        default=True,
        blank=True,
        help_text=("True/False for if technology has option to participate in net metering agreement with utility. "
                   "Note that a technology can only participate in either net metering or wholesale rates (not both).")
    )
    can_wholesale = models.BooleanField(
        default=True,
        blank=True,
        help_text=("True/False for if technology has option to export energy that is compensated at the wholesale_rate. "
                   "Note that a technology can only participate in either net metering or wholesale rates (not both).")
    )
    can_export_beyond_nem_limit = models.BooleanField(
        default=True,
        blank=True,
        help_text=("True/False for if technology can export energy beyond the annual site load (and be compensated for "
                   "that energy at the export_rate_beyond_net_metering_limit).")
    )
    can_curtail = models.BooleanField(
        default=True,
        blank=True,
        help_text="True/False for if technology has the ability to curtail energy production."
    )


class PVOutputs(BaseModel, models.Model):
    # TODO: how to use ForeignKey for scenario and still get results in view.py?
    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="PVOutputs"
    )
    # Outputs
    size_kw = models.FloatField(null=True, blank=True)
    total_om_cost = models.FloatField(null=True, blank=True)
    total_om_cost_bau = models.FloatField(null=True, blank=True)
#     station_latitude = models.FloatField(null=True, blank=True)
#     station_longitude = models.FloatField(null=True, blank=True)
#     station_distance_km = models.FloatField(null=True, blank=True)
    average_annual_energy_produced_kwh = models.FloatField(null=True, blank=True)
    average_annual_energy_produced_kwh_bau = models.FloatField(null=True, blank=True)
    average_annual_energy_exported_kwh = models.FloatField(null=True, blank=True)
    year_one_energy_produced_kwh = models.FloatField(null=True, blank=True)
    year_one_energy_produced_kwh_bau = models.FloatField(null=True, blank=True)
    year_one_to_battery_series_kw = ArrayField(
        models.FloatField(null=True, blank=True),
        blank=True, default=list
    )
    year_one_to_load_series_kw = ArrayField(
        models.FloatField(null=True, blank=True),
        blank=True, default=list
    )
    year_one_to_grid_series_kw = ArrayField(
        models.FloatField(null=True, blank=True),
        blank=True, default=list
    )
    year_one_curtailed_production_series_kw = ArrayField(
        models.FloatField(null=True, blank=True),
        blank=True, default=list
    )
    lcoe_per_kwh = models.FloatField(null=True, blank=True)


class WindInputs(BaseModel, models.Model):
    key = "Wind"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="WindInputs",
        primary_key=True
    )

    class WIND_SIZE_CLASS_CHOICES(models.TextChoices):
        RESIDENTIAL = 'residential'
        COMMERCIAL = 'commercial'
        MEDIUM = 'medium'
        LARGE = 'large'
        BLANK = ""

    size_class = models.TextField(
        blank=True,
        choices=WIND_SIZE_CLASS_CHOICES.choices,
        default=WIND_SIZE_CLASS_CHOICES.BLANK,
        help_text=('Turbine size-class. One of ["residential", "commercial", "medium", "large"]. If not provided then '
                   'the size_class is determined based on the average electric load.')
    )
    wind_meters_per_sec = ArrayField(
        models.FloatField(null=True, blank=True),
        blank=True,
        default=list,
        help_text="Data downloaded from Wind ToolKit for modeling wind turbine."
    )
    wind_direction_degrees = ArrayField(
        models.FloatField(null=True, blank=True),
        blank=True,
        default=list,
        help_text="Data downloaded from Wind ToolKit for modeling wind turbine."
    )
    temperature_celsius = ArrayField(
        models.FloatField(null=True, blank=True),
        blank=True,
        default=list,
        help_text="Data downloaded from Wind ToolKit for modeling wind turbine."
    )
    pressure_atmospheres = ArrayField(
        models.FloatField(null=True, blank=True),
        blank=True,
        default=list,
        help_text="Data downloaded from Wind ToolKit for modeling wind turbine."
    )
    min_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Minimum PV size constraint for optimization"
    )
    max_kw = models.FloatField(
        default=1.0e9,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Maximum size constraint for optimization."
    )
    installed_cost_per_kw = models.FloatField(
        default=1600,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e5)
        ],
        blank=True,
        help_text="Installed cost in $/kW"
    )
    om_cost_per_kw = models.FloatField(
        default=16,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e3)
        ],
        blank=True,
        help_text="Annual operations and maintenance costs in $/kW"
    )
    macrs_option_years = models.IntegerField(
        default=MACRS_YEARS_CHOICES.FIVE,
        choices=MACRS_YEARS_CHOICES.choices,
        blank=True,
        help_text="Duration over which accelerated depreciation will occur. Set to zero to disable"
    )
    macrs_bonus_pct = models.FloatField(
        default=1.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percent of upfront project costs to depreciate in year one in addition to scheduled depreciation"
    )
    macrs_itc_reduction = models.FloatField(
        default=0.5,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percent of the ITC value by which depreciable basis is reduced"
    )
    federal_itc_pct = models.FloatField(
        default=0.26,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percentage of capital costs that are credited towards federal taxes"
    )
    state_ibi_pct = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percentage of capital costs offset by state incentives"
    )
    state_ibi_max = models.FloatField(
        default=MAX_INCENTIVE,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_INCENTIVE)
        ],
        blank=True,
        help_text="Maximum dollar value of state percentage-based capital cost incentive"
    )
    utility_ibi_pct = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percentage of capital costs offset by utility incentives"
    )
    utility_ibi_max = models.FloatField(
        default=MAX_INCENTIVE,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_INCENTIVE)
        ],
        blank=True,
        help_text="Maximum dollar value of utility percentage-based capital cost incentive"
    )
    federal_rebate_per_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Federal rebates based on installed capacity"
    )
    state_rebate_per_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="State rebate based on installed capacity"
    )
    state_rebate_max = models.FloatField(
        default=MAX_INCENTIVE,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_INCENTIVE)
        ],
        blank=True,
        help_text="Maximum state rebate"
    )
    utility_rebate_per_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Utility rebate based on installed capacity"
    )
    utility_rebate_max = models.FloatField(
        default=MAX_INCENTIVE,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_INCENTIVE)
        ],
        blank=True,
        help_text="Maximum utility rebate"
    )
    production_incentive_per_kwh = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Production-based incentive value"
    )
    production_incentive_max_benefit = models.FloatField(
        default=1.0e9,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Maximum annual value in present terms of production-based incentives"
    )
    production_incentive_years = models.IntegerField(
        default=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        blank=True,
        help_text="Duration of production-based incentives from installation date"
    )
    production_incentive_max_kw = models.FloatField(
        default=1.0e9,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Maximum system size eligible for production-based incentive"
    )
    prod_factor_series_kw = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list, blank=True,
        help_text=("Optional user-defined production factors. Entries have units of kWh/kW, representing the energy "
                   "(kWh) output of a 1 kW system in each time step. Must be hourly (8,760 samples), 30 minute "
                   "(17,520 samples), or 15 minute (35,040 samples).")
    )
    can_net_meter = models.BooleanField(
        default=True,
        blank=True,
        help_text=("True/False for if technology has option to participate in net metering agreement with utility. "
                   "Note that a technology can only participate in either net metering or wholesale rates (not both).")
    )
    can_wholesale = models.BooleanField(
        default=True,
        blank=True,
        help_text=("True/False for if technology has option to export energy that is compensated at the wholesale_rate. "
                   "Note that a technology can only participate in either net metering or wholesale rates (not both).")
    )
    can_export_beyond_nem_limit = models.BooleanField(
        default=True,
        blank=True,
        help_text=("True/False for if technology can export energy beyond the annual site load (and be compensated for "
                   "that energy at the export_rate_beyond_net_metering_limit).")
    )
    can_curtail = models.BooleanField(
        default=True,
        blank=True,
        help_text="True/False for if technology has the ability to curtail energy production."
    )


class WindOutputs(BaseModel, models.Model):
    key = "WindOutputs"
    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="WindOutputs",
        primary_key=True
    )

    size_kw = models.FloatField(null=True, blank=True)
    total_om_cost = models.FloatField(null=True, blank=True)
    year_one_om_cost = models.FloatField(null=True, blank=True)
    average_annual_energy_produced_kwh = models.FloatField(null=True, blank=True)
    average_annual_energy_exported_kwh = models.FloatField(null=True, blank=True)
    year_one_energy_produced_kwh = models.FloatField(null=True, blank=True)
    year_one_to_battery_series_kw = ArrayField(
            models.FloatField(null=True, blank=True), blank=True, default=list)
    year_one_to_load_series_kw = ArrayField(
            models.FloatField(null=True, blank=True), blank=True, default=list)
    year_one_to_grid_series_kw = ArrayField(
            models.FloatField(null=True, blank=True), blank=True, default=list)
    year_one_curtailed_production_series_kw = ArrayField(
            models.FloatField(null=True, blank=True), blank=True, default=list)
    lcoe_per_kwh = models.FloatField(null=True, blank=True)


class StorageInputs(BaseModel, models.Model):
    key = "Storage"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="StorageInputs",
        primary_key=True
    )

    min_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Minimum storage inverter capacity constraint for optimization."
    )
    max_kw = models.FloatField(
        default=1.0e9,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Maximum storage inverter capacity constraint for optimization."
    )
    min_kwh = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Minimum energy storage capacity constraint for optimization."
    )
    max_kwh = models.FloatField(
        default=1.0e6,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Maximum energy storage capacity constraint for optimization."
    )
    internal_efficiency_pct = models.FloatField(
        default=0.975,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0)
        ],
        blank=True,
        help_text="Battery inherent efficiency independent of inverter and rectifier"
    )
    inverter_efficiency_pct = models.FloatField(
        default=0.96,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0)
        ],
        blank=True,
        help_text="Battery inverter efficiency"
    )
    rectifier_efficiency_pct = models.FloatField(
        default=0.96,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0)
        ],
        blank=True,
        help_text="Battery rectifier efficiency"
    )
    soc_min_pct = models.FloatField(
        default=0.2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0)
        ],
        blank=True,
        help_text="Minimum allowable battery state of charge as fraction of energy capacity."
    )
    soc_init_pct = models.FloatField(
        default=0.5,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0)
        ],
        blank=True,
        help_text="Battery state of charge at first hour of optimization as fraction of energy capacity."
    )
    can_grid_charge = models.BooleanField(
        default=True,
        blank=True,
        help_text="Flag to set whether the battery can be charged from the grid, or just onsite generation."
    )
    installed_cost_per_kw = models.FloatField(
        default=840.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e4)
        ],
        blank=True,
        help_text="Total upfront battery power capacity costs (e.g. inverter and balance of power systems)"
    )
    installed_cost_per_kwh = models.FloatField(
        default=420.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e4)
        ],
        blank=True,
        help_text="Total upfront battery costs"
    )
    replace_cost_per_kw = models.FloatField(
        default=410.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e4)
        ],
        blank=True,
        help_text="Battery power capacity replacement cost at time of replacement year"
    )
    replace_cost_per_kwh = models.FloatField(
        default=200.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e4)
        ],
        blank=True,
        help_text="Battery energy capacity replacement cost at time of replacement year"
    )
    inverter_replacement_year = models.IntegerField(
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_YEARS)
        ],
        blank=True,
        help_text="Number of years from start of analysis period to replace inverter"
    )
    battery_replacement_year = models.IntegerField(
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_YEARS)
        ],
        blank=True,
        help_text="Number of years from start of analysis period to replace battery"
    )
    macrs_option_years = models.IntegerField(
        default=MACRS_YEARS_CHOICES.SEVEN,
        choices=MACRS_YEARS_CHOICES.choices,
        blank=True,
        help_text="Duration over which accelerated depreciation will occur. Set to zero to disable"
    )
    macrs_bonus_pct = models.FloatField(
        default=1.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percent of upfront project costs to depreciate in year one in addition to scheduled depreciation"
    )
    macrs_itc_reduction = models.FloatField(
        default=0.5,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percent of the ITC value by which depreciable basis is reduced"
    )
    total_itc_pct = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Total investment tax credit in percent applied toward capital costs"
    )
    total_rebate_per_kw = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Rebate based on installed power capacity"
    )
    total_rebate_per_kwh = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Rebate based on installed energy capacity"
    )


class StorageOutputs(BaseModel, models.Model):
    key = "StorageOutputs"
    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="StorageOutputs",
    )
    size_kw = models.FloatField(null=True, blank=True)
    size_kwh = models.FloatField(null=True, blank=True)
    year_one_soc_series_pct = ArrayField(
        models.FloatField(null=True, blank=True),
        blank=True, default=list
    )
    year_one_to_load_series_kw = ArrayField(
        models.FloatField(null=True, blank=True),
        blank=True, default=list
    )


class GeneratorInputs(BaseModel, models.Model):
    key = "Generator"

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="GeneratorInputs",
        primary_key=True
    )

    existing_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e5)
        ],
        blank=True,
        help_text="Existing diesel generator size"
    )
    min_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Minimum diesel generator size constraint for optimization"
    )
    max_kw = models.FloatField(
        default=1.0e9,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Maximum diesel generator size constraint for optimization. Set to zero to disable PV"
    )
    installed_cost_per_kw = models.FloatField(
        default=500,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0e5)
        ],
        blank=True,
        help_text="Installed diesel generator cost in $/kW"
    )
    om_cost_per_kw = models.FloatField(
        default=10.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0e3)
        ],
        blank=True,
        help_text="Annual diesel generator fixed operations and maintenance costs in $/kW"
    )
    om_cost_per_kwh = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0e3)
        ],
        blank=True,
        help_text="Diesel generator per unit production (variable) operations and maintenance costs in $/kWh"
    )
    fuel_cost_per_gallon = models.FloatField(
        default=3.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0e2)
        ],
        blank=True,
        help_text="Diesel cost in $/gallon"
    )
    fuel_slope_gal_per_kwh = models.FloatField(
        default=0.076,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(10.0)
        ],
        blank=True,
        help_text="Generator fuel burn rate in gallons/kWh."
    )
    fuel_intercept_gal_per_hr = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(10.0)
        ],
        blank=True,
        help_text="Generator fuel consumption curve y-intercept in gallons per hour."
    )
    fuel_avail_gal = models.FloatField(
        default=660.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="On-site generator fuel available in gallons."
    )
    min_turn_down_pct = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ],
        blank=True,
        help_text="Minimum generator loading in percent of capacity (size_kw)."
    )
    only_runs_during_grid_outage = models.BooleanField(
        default=True,
        blank=True,
        help_text="Determines if the generator can run only during grid outage or all the time."
    )
    sells_energy_back_to_grid = models.BooleanField(
        default=False,
        blank=True,
        help_text="Determines if generator can participate in NEM and wholesale markets."
    )
    macrs_option_years = models.IntegerField(
        default=MACRS_YEARS_CHOICES.ZERO,
        choices=MACRS_YEARS_CHOICES.choices,
        blank=True,
        help_text="Duration over which accelerated depreciation will occur. Set to zero to disable"
    )
    macrs_bonus_pct = models.FloatField(
        default=1.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percent of upfront project costs to depreciate in year one in addition to scheduled depreciation"
    )
    macrs_itc_reduction = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percent of the ITC value by which depreciable basis is reduced"
    )
    federal_itc_pct = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percentage of capital costs that are credited towards federal taxes"
    )
    state_ibi_pct = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percentage of capital costs offset by state incentives"
    )
    state_ibi_max = models.FloatField(
        default=MAX_INCENTIVE,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_INCENTIVE)
        ],
        blank=True,
        help_text="Maximum dollar value of state percentage-based capital cost incentive"
    )
    utility_ibi_pct = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Percentage of capital costs offset by utility incentives"
    )
    utility_ibi_max = models.FloatField(
        default=MAX_INCENTIVE,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_INCENTIVE)
        ],
        blank=True,
        help_text="Maximum dollar value of utility percentage-based capital cost incentive"
    )
    federal_rebate_per_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Federal rebates based on installed capacity"
    )
    state_rebate_per_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="State rebate based on installed capacity"
    )
    state_rebate_max = models.FloatField(
        default=MAX_INCENTIVE,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_INCENTIVE)
        ],
        blank=True,
        help_text="Maximum state rebate"
    )
    utility_rebate_per_kw = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Utility rebate based on installed capacity"
    )
    utility_rebate_max = models.FloatField(
        default=MAX_INCENTIVE,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_INCENTIVE)
        ],
        blank=True,
        help_text="Maximum utility rebate"
    )
    production_incentive_per_kwh = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Production-based incentive value"
    )
    production_incentive_max_benefit = models.FloatField(
        default=1.0e9,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Maximum annual value in present terms of production-based incentives"
    )
    production_incentive_years = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        blank=True,
        help_text="Duration of production-based incentives from installation date"
    )
    production_incentive_max_kw = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="Maximum system size eligible for production-based incentive"
    )
    can_net_meter = models.BooleanField(
        default=False,
        blank=True,
        help_text=("True/False for if technology has option to participate in net metering agreement with utility. "
                   "Note that a technology can only participate in either net metering or wholesale rates (not both).")
    )
    can_wholesale = models.BooleanField(
        default=False,
        blank=True,
        help_text=("True/False for if technology has option to export energy that is compensated at the wholesale_rate. "
                   "Note that a technology can only participate in either net metering or wholesale rates (not both).")
    )
    can_export_beyond_nem_limit = models.BooleanField(
        default=False,
        blank=True,
        help_text=("True/False for if technology can export energy beyond the annual site load (and be compensated for "
                   "that energy at the export_rate_beyond_net_metering_limit).")
    )
    can_curtail = models.BooleanField(
        default=False,
        blank=True,
        help_text="True/False for if technology has the ability to curtail energy production."
    )
    # emissions_factor_lb_CO2_per_gal = models.FloatField(null=True, blank=True)


class GeneratorOutputs(BaseModel, models.Model):

    scenario = models.OneToOneField(
        Scenario,
        on_delete=models.CASCADE,
        related_name="GeneratorOutputs",
        primary_key=True,
    )

    fuel_used_gal = models.FloatField(null=True, blank=True)
    fuel_used_gal_bau = models.FloatField(null=True, blank=True)
    size_kw = models.FloatField(null=True, blank=True)
    average_annual_energy_produced_kwh = models.FloatField(null=True, blank=True)
    average_annual_energy_exported_kwh = models.FloatField(null=True, blank=True)
    year_one_energy_produced_kwh = models.FloatField(null=True, blank=True)
    year_one_to_battery_series_kw = ArrayField(
            models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_load_series_kw = ArrayField(
            models.FloatField(null=True, blank=True), null=True, blank=True, default=list)
    year_one_to_grid_series_kw = ArrayField(
            models.FloatField(null=True, blank=True), null=True, blank=True, default=list)
    year_one_variable_om_cost = models.FloatField(null=True, blank=True)
    year_one_variable_om_cost_bau = models.FloatField(null=True, blank=True)
    year_one_fuel_cost = models.FloatField(null=True, blank=True)
    year_one_fuel_cost_bau = models.FloatField(null=True, blank=True)
    year_one_fixed_om_cost = models.FloatField(null=True, blank=True)
    year_one_fixed_om_cost_bau = models.FloatField(null=True, blank=True)
    total_variable_om_cost = models.FloatField(null=True, blank=True)
    total_variable_om_cost_bau = models.FloatField(null=True, blank=True)
    total_fuel_cost = models.FloatField(null=True, blank=True)
    total_fuel_cost_bau = models.FloatField(null=True, blank=True)
    total_fixed_om_cost = models.FloatField(null=True, blank=True)
    total_fixed_om_cost_bau = models.FloatField(null=True, blank=True)
    year_one_emissions_lb_C02 = models.FloatField(null=True, blank=True)
    year_one_emissions_bau_lb_C02 = models.FloatField(null=True, blank=True)


class Message(BaseModel, models.Model):
    """
    For Example:
    {"messages":{
                "warnings": "This is a warning message.",
                "error": "REopt had an error."
                }
    }
    """
    scenario = models.ForeignKey(
        Scenario,
        on_delete=models.CASCADE
    )
    message_type = models.TextField(default='')
    message = models.TextField(default='')
    scenario = models.ForeignKey(
        Scenario,
        on_delete=models.CASCADE
    )
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

"""
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
"""
