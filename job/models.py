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
import math
from django.db import models
from django.db.models.fields import NOT_PROVIDED
from django.contrib.postgres.fields import *
# TODO rm picklefield from requirements.txt once v1 is retired (replaced with JSONfield)
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from job.urdb_rate_validator import URDB_RateValidator,URDB_LabelValidator
import copy
import logging

log = logging.getLogger(__name__)

"""
Guidance:
- start all Model fields with required fields (do not need to include `blank` b/c the default value of blank is False)
- TextField and CharField should not have null=True
- description: use square brackets for units, eg. [dollars per kWh]
- Output models need to have null=True, blank=True for cases when results are not generated 
"""
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
        d.pop("meta_id", None)
        return d

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        return obj

    def info_dict(self):
        """
        :return: dict with keys for each model field and sub-dicts for the settings for each key, such as help_text
        """
        d = dict()
        possible_sets = getattr(self, "possible_sets", None)
        if possible_sets is not None:
            d["possible_sets"] = possible_sets

        for field in self._meta.fields:
            if field.attname.endswith("id"): continue
            d[field.attname] = dict()
            if "Outputs" not in getattr(self, "key", ""):
                d[field.attname]["required"] = not field.blank and field.default == NOT_PROVIDED
            if field.choices is not None:
                d[field.attname]["choices"] = [t[0] for t in field.choices]
            if not field.default == NOT_PROVIDED and field.default != list:
                try:
                    d[field.attname]["default"] = field.default.value
                except:
                    d[field.attname]["default"] = field.default
            if len(field.help_text) > 0:
                d[field.attname]["help_text"] = field.help_text
            for val in field.validators:
                if val.limit_value not in (-2147483648, 2147483647):  # integer limits
                    d[field.attname][val.code] = val.limit_value
        return d
    

class APIMeta(BaseModel, models.Model):
    """
    Values created by API for each scenario (no user input values). 
    Returned from job/<run_uuid>/results at the top level.
    """
    key = "APIMeta"

    run_uuid = models.UUIDField(unique=True)
    api_version = models.IntegerField(default=2)
    user_uuid = models.TextField(
        blank=True,
        default="",
        help_text="The assigned unique ID of a signed in REopt user."
    )
    webtool_uuid = models.TextField(
        blank=True,
        default="",
        help_text=("The unique ID of a scenario created by the REopt Lite Webtool. Note that this ID can be shared by "
                   "several REopt Lite API Scenarios (for example when users select a 'Resilience' analysis more than "
                   "one REopt API Scenario is created).")
    )
    job_type = models.TextField(
        default='developer.nrel.gov'
    )
    status = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    reopt_version = models.TextField(
        blank=True,
        default="",
        help_text="Version number of the Julia package for REopt that is used to solve the problem."
    )


class UserProvidedMeta(BaseModel, models.Model):
    """
    User provided values that are not necessary for running REopt
    """
    key = "Meta"

    meta = models.OneToOneField(
        APIMeta,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="UserProvidedMeta"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional user defined description."
    )
    address = models.TextField(
        blank=True,
        help_text="Optional user defined address (street address, city, state or zip code)"
    )


class Settings(BaseModel, models.Model):
    key = "Settings"

    meta = models.OneToOneField(
        APIMeta,
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

    run_bau = models.BooleanField(
        blank=True,
        null=True,
        default=True,
        help_text=("If True then the Business-As-Usual scenario is also solved to provide additional outputs such as "
                   "the LCC and BAU costs.")
    )

    off_grid_flag = models.BooleanField(
        default=False,
        blank=True,
        help_text=("Set to true to enable off-grid analyses")
    )

    def clean(self):
        if self.off_grid_flag:
            self.run_bau = False

class SiteInputs(BaseModel, models.Model):
    key = "Site"

    meta = models.OneToOneField(
        APIMeta,
        on_delete=models.CASCADE,
        related_name="SiteInputs",
        primary_key=True
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

"""
# TODO should we move the emissions_calculator to Julia? 
# Or is it supplanted by new emissions capabilities (not in develop/master as of 21.09.02)?

class SiteOutputs(BaseModel, models.Model):
    key = "SiteOutputs"

    meta = models.OneToOneField(
        APIMeta,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="SiteOutputs"
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

    meta = models.OneToOneField(
        APIMeta,
        on_delete=models.CASCADE,
        related_name="FinancialInputs",
        primary_key=True
    )

    analysis_years = models.IntegerField(
        default=25,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(75)
        ],
        blank=True,
        help_text="Analysis period in years. Must be integer."
    )
    elec_cost_escalation_pct = models.FloatField(
        default=0.023,
        validators=[
            MinValueValidator(-1),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Annual nominal utility electricity cost escalation rate."
    )
    offtaker_discount_pct = models.FloatField(
        default=0.083,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text=("Nominal energy offtaker discount rate. In single ownership model the offtaker is also the "
                   "generation owner.")
    )
    offtaker_tax_pct = models.FloatField(
        default=0.26,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(0.999)
        ],
        blank=True,
        help_text="Host tax rate"
    )
    om_cost_escalation_pct = models.FloatField(
        default=0.025,
        validators=[
            MinValueValidator(-1),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text="Annual nominal O&M cost escalation rate"
    )
    owner_discount_pct = models.FloatField(
        default=0.083,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text=("Nominal generation owner discount rate. Used for two party financing model. In two party ownership "
                   "model the offtaker does not own the generator(s).")
    )
    owner_tax_pct = models.FloatField(
        default=0.26,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(0.999)
        ],
        blank=True,
        help_text=("Generation owner tax rate. Used for two party financing model. In two party ownership model the "
                   "offtaker does not own the generator(s).")
    )
    third_party_ownership = models.BooleanField(
        default=False,
        blank=True,
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
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        blank=True,
        help_text=("Additional cost, in percent of non-islandable capital costs, to make a distributed energy system "
                   "islandable from the grid and able to serve critical loads. Includes all upgrade costs such as "
                   "additional laber and critical load panels.")
    )

    offgrid_other_capital_costs = models.FloatField(
            validators=[
                MinValueValidator(0),
                MaxValueValidator(1e6)
            ],
            blank=True,
            null=True,
            default=0.0,
            help_text=("Only applicable when off_grid_flag is true, applies a straight-line depreciation to this capex cost, reducing taxable income.")
    )

    offgrid_other_annual_costs = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1e6)
        ],
        blank=True,
        null=True,
        default=0.0,
        help_text=("Only applicable when off_grid_flag is true. Considered tax deductible for owner. Costs are per year.")
    )

    # boiler_fuel_escalation_pct = models.FloatField(
    #     default=0.034,
    #     validators=[
    #         MinValueValidator(-1),
    #         MaxValueValidator(1)
    #     ],
    #     blank=True,
    #     help_text=("Annual nominal boiler fuel cost escalation rate")
    # )
    # chp_fuel_escalation_pct = models.FloatField(
    #     default=0.034,
    #     validators=[
    #         MinValueValidator(-1),
    #         MaxValueValidator(1)
    #     ],
    #     blank=True,
    #     help_text=("Annual nominal chp fuel cost escalation rate")
    # )

    def clean(self):
        if not self.third_party_ownership:
            self.owner_tax_pct = self.offtaker_tax_pct
            self.owner_discount_pct = self.offtaker_discount_pct


class FinancialOutputs(BaseModel, models.Model):
    key = "FinancialOutputs"

    meta = models.OneToOneField(
        APIMeta,
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
    lifecycle_capital_costs_plus_om_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Capital cost for all technologies plus present value of operations and maintenance over anlaysis period"
    )
    lifecycle_om_costs_before_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business-as-usual present value of operations and maintenance over analysis period",
    )
    lifecycle_capital_costs = models.FloatField(
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
    lifecycle_om_costs_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Life cycle operations and maintenance cost over analysis period after tax."
    )
    year_one_om_costs_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Year one operations and maintenance cost after tax."
    )
    lifecycle_om_costs_before_tax = models.FloatField(
        null=True, blank=True,
        help_text="Life cycle operations and maintenance cost over analysis period before tax."
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
    lifecycle_generation_tech_capital_costs = models.FloatField(
        null=True, blank=True,
        help_text=("Component of lifecycle costs, this value is the net capital costs for all generation technologies"
                    "Costs are given in present value, including replacement costs and incentives."
                    "This value does not include offgrid_other_capital_costs.")
    )
    lifecycle_storage_capital_costs = models.FloatField(
        null=True, blank=True,
        help_text=("Component of lifecycle costs, this value is the Net capital costs for all storage technologies"
                    "Value is in present value, including replacement costs and incentives."
                    "This value does not include offgrid_other_capital_costs.")
    )
    lifecycle_om_costs_after_tax = models.FloatField(
        null=True, blank=True,
        help_text=("Component of lifecycle costs, this value is the present value of all O&M costs, after tax.")
    )
    lifecycle_fuel_costs_after_tax = models.FloatField(
        null=True, blank=True,
        help_text=("Component of lifecycle costs, this value is the present value of all fuel costs over the analysis period, after tax.")
    )

    lifecycle_chp_standby_cost_after_tax = models.FloatField(
        null=True, blank=True,
        help_text=("Component of lifecycle costs, this value is the present value of all CHP standby charges, after tax.")
    )
    lifecycle_elecbill_after_tax = models.FloatField(
        null=True, blank=True,
        help_text=("Component of lifecycle costs, this value is the present value of all electric utility charges, after tax.")
    )
    lifecycle_production_incentive_after_tax = models.FloatField(
        null=True, blank=True,
        help_text=("Component of lifecycle costs, this value is the present value of all production-based incentives, after tax.")
    )
    lifecycle_offgrid_other_annual_costs_after_tax = models.FloatField(
        null=True, blank=True,
        help_text=("Component of lifecycle costs, this value is the present value of offgrid_other_annual_costs over the analysis period, after tax.")
    )
    lifecycle_offgrid_other_capital_costs = models.FloatField(
        null=True, blank=True,
        help_text=("Component of lifecycle costs, this value is equal to offgrid_other_capital_costs with straight line depreciation applied"
                    " over analysis period. The depreciation expense is assumed to reduce the owner's taxable income.")
    )
    lifecycle_outage_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Component of lifecycle costs, expected outage cost.")
    )
    lifecycle_MG_upgrade_and_fuel_cost = models.FloatField(
        null=True, blank=True,
        help_text=("Component of lifecycle costs, this is the cost to upgrade generation and storage technologies to be included in microgrid"
                    "plus present value of microgrid fuel costs.")
    )
    replacements_future_cost_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Future cost of replacing storage and/or generator systems, after tax."
    )
    replacements_present_cost_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Present value cost of replacing storage and/or generator systems, after tax."
    )
    offgrid_microgrid_lcoe_dollars_per_kwh = models.FloatField(
        null=True, blank=True,
        help_text="Levelized cost of electricity for modeled off-grid system."
    )

class ElectricLoadInputs(BaseModel, models.Model):
    key = "ElectricLoad"

    meta = models.OneToOneField(
        APIMeta,
        on_delete=models.CASCADE,
        related_name="ElectricLoadInputs",
        primary_key=True
    )

    possible_sets = [
        ["loads_kw"],
        ["doe_reference_name", "monthly_totals_kwh"],
        ["annual_kwh", "doe_reference_name"],
        ["doe_reference_name"],
        ["blended_doe_reference_names", "blended_doe_reference_percents"]
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
        help_text=("Annual site energy consumption from electricity, in kWh, used to scale simulated default building "
                   "load profile for the site's climate zone")
    )
    doe_reference_name = models.TextField(
        null=False,
        blank=True,  # TODO do we have to include "" in choices for blank=True to work?
        choices=DOE_REFERENCE_NAME.choices,
        help_text=("Simulated load profile from DOE Commercial Reference Buildings "
                   "https://energy.gov/eere/buildings/commercial-reference-buildings")
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
        # default=0.5,
        help_text="Critical load factor is multiplied by the typical load to determine the critical load that must be "
                  "met during an outage. Value must be between zero and one, inclusive."

    )

    operating_reserve_required_pct = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=""

    )

    min_load_met_annual_pct = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        help_text=""

    )

    blended_doe_reference_names = ArrayField(
        models.TextField(
            choices=DOE_REFERENCE_NAME.choices,
            blank=True
        ),
        default=list,
        blank=True,
        help_text=("Used in concert with blended_doe_reference_percents to create a blended load profile from multiple "
                   "DoE Commercial Reference Buildings.")
    )
    blended_doe_reference_percents = ArrayField(
        models.FloatField(
            null=True, blank=True,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(1.0)
            ],
        ),
        default=list,
        blank=True,
        help_text=("Used in concert with blended_doe_reference_names to create a blended load profile from multiple "
                   "DoE Commercial Reference Buildings. Must sum to 1.0.")
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

    def clean(self):
        error_messages = {}

        # possible sets for defining load profile
        if not at_least_one_set(self.dict, self.possible_sets):
            error_messages["required inputs"] = \
                "Must provide at least one set of valid inputs from {}.".format(self.possible_sets)

        if len(self.blended_doe_reference_names) > 0 and self.doe_reference_name == "":
            if len(self.blended_doe_reference_names) != len(self.blended_doe_reference_percents):
                error_messages["blended_doe_reference_names"] = \
                    "The number of blended_doe_reference_names must equal the number of blended_doe_reference_percents."
            if not math.isclose(sum(self.blended_doe_reference_percents),  1.0):
                error_messages["blended_doe_reference_percents"] = "Sum must = 1.0."

        if self.doe_reference_name != "" or \
                len(self.blended_doe_reference_names) > 0:
            self.year = 2017  # the validator provides an "info" message regarding this

        if error_messages:
            raise ValidationError(error_messages)


class ElectricLoadOutputs(BaseModel, models.Model):
    key = "ElectricLoadOutputs"

    meta = models.OneToOneField(
        APIMeta,
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
    offgrid_load_met_pct = models.FloatField(
        null=True, blank=True,
        help_text="Percentage of total electric load met on an annual basis, for off-grid scenarios only"
    )
    offgrid_annual_oper_res_required_series_kwh = ArrayField(
        models.FloatField(
            null=True, blank=True
        ),
        default=list,
        help_text="Total operating reserves required on an annual basis, for off-grid scenarios only"
    )
    offgrid_annual_oper_res_provided_series_kwh = ArrayField(
        models.FloatField(
            null=True, blank=True
        ),
        default=list,
        help_text="Total operating reserves provided on an annual basis, for off-grid scenarios only"
    )
    offgrid_load_met_series_kw = ArrayField(
        models.FloatField(
            null=True, blank=True
        ),
        default=list,
        help_text="Percentage of total electric load met on an annual basis, for off-grid scenarios only"
    )

class ElectricTariffInputs(BaseModel, models.Model):
    key = "ElectricTariff"

    meta = models.OneToOneField(
        APIMeta,
        on_delete=models.CASCADE,
        related_name="ElectricTariffInputs",
        primary_key=True
    )

    possible_sets = [
        ["urdb_response"],
        ["monthly_demand_rates", "monthly_energy_rates"],
        ["blended_annual_energy_rate", "blended_annual_demand_rate"],
        ["urdb_label"],
        ["urdb_utility_name", "urdb_rate_name"],
        ["tou_energy_rates_per_kwh"]
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
        help_text=("Label attribute of utility rate structure from Utility Rate Database API "
                   "https://openei.org/services/doc/rest/util_rates/?version=8")
    )
    urdb_response = models.JSONField(
        null=True, blank=True,
        help_text=("Utility rate structure from Utility Rate Database API "
                   "https://openei.org/services/doc/rest/util_rates/?version=8")
    )
    urdb_rate_name = models.TextField(
        blank=True,
        help_text="Name of utility rate from Utility Rate Database https://openei.org/wiki/Utility_Rate_Database"
    )
    urdb_utility_name = models.TextField(
        blank=True,
        help_text="Name of Utility from Utility Rate Database https://openei.org/wiki/Utility_Rate_Database"
    )
    blended_annual_demand_rate = models.FloatField(
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
        help_text=("Price of electricity sold back to the grid above the site load, regardless of net metering. Can be "
                   "a scalar value, which applies for all-time, or an array with time-sensitive values. If an array is "
                   "input then it must have a length of 8760, 17520, or 35040. The inputed array values are up/down-"
                   "sampled using mean values to match the Scenario time_steps_per_hour.")
    )
    tou_energy_rates_per_kwh = ArrayField(
        models.FloatField(blank=True),
        default=list,
        blank=True,
        help_text=("Time-of-use energy rates, provided by user. Must be an array with length equal to number of "
                   "time steps per year. Hourly or 15 minute rates allowed.")
    )
    add_monthly_rates_to_urdb_rate = models.BooleanField(
        blank=True,
        default=False,
        help_text=("Set to true to add the monthly blended energy rates and demand charges to the URDB rate schedule. "
                   "Otherwise, blended rates will only be considered if a URDB rate is not provided.")

    )
    add_tou_energy_rates_to_urdb_rate = models.BooleanField(
        blank=True,
        default=False,
        help_text=("Set to true to add tou_energy_rates_per_kwh to the URDB rate schedule. Otherwise, tou energy rates "
                   "will only be considered if a URDB rate is not provided.")

    )
    coincident_peak_load_active_time_steps = ArrayField(
        ArrayField(
            models.IntegerField(blank=True),
            blank=True,
            default=list,
            validators=[
                MinValueValidator(1)
            ]
        ),
        blank=True,
        default=list,
        help_text=("The optional coincident_peak_load_charge_per_kw will apply to the max grid-purchased "
                   "power during these time steps. Note time steps are indexed to a base of 1 not 0.")
    )
    coincident_peak_load_charge_per_kw = ArrayField(
        models.FloatField(
            blank=True,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(1.0e8)
            ],
        ),
        null=True, blank=True,
        default=list,
        help_text=("Optional coincident peak demand charge that is applied to the max load during the time_steps "
                   "specified in coincident_peak_load_active_time_steps")
    )
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
    #               "constant fraction that will be applied across all time_steps, or an annual timeseries array at an "
    #               "hourly (8,760 samples), 30 minute (17,520 samples), or 15 minute (35,040 samples) resolution.")
    # )

    def clean(self):
        error_messages = {}

        # possible sets for defining tariff
        if not at_least_one_set(self.dict, self.possible_sets):
            error_messages["required inputs"] = \
                f"Must provide at least one set of valid inputs from {self.possible_sets}."

        for possible_set in self.possible_sets:
            if len(possible_set) == 2:  # check dependencies
                if (possible_set[0] and not possible_set[1]) or (not possible_set[0] and possible_set[1]):
                    error_messages["required inputs"] = f"Must provide both {possible_set[0]} and {possible_set[1]}"

        if len(self.wholesale_rate) == 1:
            self.wholesale_rate = self.wholesale_rate * 8760  # upsampling handled in InputValidator.cross_clean

        if len(self.coincident_peak_load_charge_per_kw) > 0:
            if len(self.coincident_peak_load_active_time_steps) != len(self.coincident_peak_load_charge_per_kw):
                error_messages["coincident peak"] = (
                    "The number of rates in coincident_peak_load_charge_per_kw must match the number of "
                    "timestep sets in coincident_peak_load_active_time_steps")

        if self.urdb_label is not None:
            label_checker = URDB_LabelValidator(self.urdb_label)
            if label_checker.errors:
                error_messages["urdb_label"] = label_checker.errors
        if self.urdb_response is not None:
            try:
                rate_checker = URDB_RateValidator(**self.urdb_response)
                if rate_checker.errors:
                    error_messages["urdb_response"] = rate_checker.errors
            except:
                error_messages["urdb_response"] = "Error parsing urdb_response. Please check the keys and values."
        
        if error_messages:
            raise ValidationError(error_messages)

    def save(self, *args, **kwargs):
        """
        Special case for coincident_peak_load_active_time_steps: back-end database requires that
        "multidimensional arrays must have array expressions with matching dimensions"
        so we fill the arrays that are shorter than the longest arrays with repeats of the last value.
        By repeating the last value we do not have to deal with a mix of data types in the arrays and it does not
        affect the constraints in REopt.
        """
        if len(self.coincident_peak_load_active_time_steps) > 0:
            max_length = max(len(inner_array) for inner_array in self.coincident_peak_load_active_time_steps)
            for inner_array in self.coincident_peak_load_active_time_steps:
                if len(inner_array) != max_length:
                    for _ in range(max_length - len(inner_array)):
                        inner_array.append(inner_array[-1])
        super(ElectricTariffInputs, self).save(*args, **kwargs)

    @property
    def dict(self):
        """
        Serialize Django Model.__dict__, custom implementation for ElectricTariffInputs
        NOTE: to get correct field types you must run self.clean_fields() first (eg. convert int to float)
        :return: dict
        """
        d = copy.deepcopy(self.__dict__)
        if "coincident_peak_load_active_time_steps" in d.keys():
            # filter out repeated values created to make the inner arrays have equal length
            d["coincident_peak_load_active_time_steps"] = \
                [list(set(l)) for l in d["coincident_peak_load_active_time_steps"]]
        d.pop("_state", None)
        d.pop("id", None)
        d.pop("basemodel_ptr_id", None)
        d.pop("meta_id", None)
        return d


class ElectricUtilityInputs(BaseModel, models.Model):
    key = "ElectricUtility"

    meta = models.OneToOneField(
        APIMeta,
        on_delete=models.CASCADE,
        related_name="ElectricUtilityInputs",
        primary_key=True
    )

    outage_start_time_step = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1)
            # max value validated in InputValidator b/c it requires Settings.time_steps_per_hour
        ],
        help_text="Time step that grid outage starts. Must be less than or equal to outage_end_time_step."
    )
    outage_end_time_step = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1)
            # max value validated in InputValidator b/c it requires Settings.time_steps_per_hour
        ],
        help_text="Time step that grid outage ends. Must be greater than or equal to outage_start_time_step."
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
        error_messages = {}

        # outage start/end time step dependencies
        if self.outage_start_time_step and self.outage_end_time_step is None:
            error_messages["outage_end_time_step"] = "Got outage_start_time_step but no outage_end_time_step."

        if self.outage_end_time_step and self.outage_start_time_step is None:
            error_messages["outage_start_time_step"] = "Got outage_end_time_step but no outage_start_time_step."

        if self.outage_start_time_step is not None and self.outage_end_time_step is not None:
            if self.outage_start_time_step > self.outage_end_time_step:
                error_messages["outage start/stop time steps"] = \
                    ('outage_end_time_step must be larger than or equal to outage_start_time_step.')

        if error_messages:
            raise ValidationError(error_messages)


class ElectricUtilityOutputs(BaseModel, models.Model):
    key = "ElectricUtilityOutputs"

    meta = models.OneToOneField(
        APIMeta,
        on_delete=models.CASCADE,
        related_name="ElectricUtilityOutputs",
        primary_key=True
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

    meta = models.OneToOneField(
        APIMeta,
        on_delete=models.CASCADE,
        related_name="ElectricTariffOutputs",
        primary_key=True
    )

    emissions_region = models.TextField(
        null=True,
        blank=True
    )
    year_one_energy_cost_before_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal year one utility energy cost"
    )
    year_one_demand_cost_before_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal year one utility demand cost"
    )
    year_one_fixed_cost_before_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal year one utility fixed cost"
    )
    year_one_min_charge_adder_before_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal year one utility minimum charge adder"
    )
    year_one_energy_cost_before_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual year one utility energy cost"
    )
    year_one_demand_cost_before_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual year one utility demand cost"
    )
    year_one_fixed_cost_before_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual year one utility fixed cost"
    )
    year_one_min_charge_adder_before_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual year one utility minimum charge adder"
    )
    lifecycle_energy_cost_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal life cycle utility energy cost, after-tax"
    )
    lifecycle_demand_cost_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal life cycle utility demand cost, after-tax"
    )
    lifecycle_fixed_cost_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal life cycle utility fixed cost, after-tax"
    )
    lifecycle_min_charge_adder_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal life cycle utility minimum charge adder, after-tax"
    )
    lifecycle_energy_cost_after_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual life cycle utility energy cost, after-tax"
    )
    lifecycle_demand_cost_after_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual life cycle lifecycle utility demand cost, after-tax"
    )
    lifecycle_fixed_cost_after_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual life cycle utility fixed cost, after-tax"
    )
    lifecycle_min_charge_adder_after_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual life cycle utility minimum charge adder, after-tax"
    )
    lifecycle_export_benefit_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal life cycle value of exported energy, after-tax"
    )
    lifecycle_export_benefit_after_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual life cycle value of exported energy, after-tax"
    )
    year_one_bill_before_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal year one utility bill"
    )
    year_one_bill_before_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual year one utility bill"
    )
    year_one_export_benefit_before_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal year one value of exported energy"
    )
    year_one_export_benefit_before_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual year one value of exported energy"
    )
    year_one_energy_cost_series_per_kwh = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list, blank=True,
        help_text="Optimal year one hourly energy costs"
    )
    year_one_demand_cost_series_per_kw = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list, blank=True,
        help_text="Optimal year one hourly demand costs"
    )
    year_one_coincident_peak_cost_before_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal year one coincident peak charges"
    )
    year_one_coincident_peak_cost_before_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual year one coincident peak charges"
    )
    lifecycle_coincident_peak_cost_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal total coincident peak charges over the analysis period, after-tax"
    )
    lifecycle_coincident_peak_cost_after_tax_bau = models.FloatField(
        null=True, blank=True,
        help_text="Business as usual life cycle coincident peak charges, after-tax"
    )
    year_one_chp_standby_cost_before_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal year one standby charge cost incurred by CHP"
    )
    lifecycle_chp_standby_cost_after_tax = models.FloatField(
        null=True, blank=True,
        help_text="Optimal life cycle standby charge cost incurred by CHP, after-tax"
    )


class PVInputs(BaseModel, models.Model):
    key = "PV"
    meta = models.ForeignKey(
        to=APIMeta,
        on_delete=models.CASCADE,
        related_name="PVInputs",
        unique=False
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
    prod_factor_series = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list, blank=True,
        help_text=("Optional user-defined production factors. Must be normalized to units of kW-AC/kW-DC nameplate, "
                   "representing the AC power (kW) output per 1 kW-DC of system capacity in each time step. "
                   "The series must be one year (January through December) of hourly, 30-minute, or 15-minute PV "
                   "generation data.")
    )
    can_net_meter = models.BooleanField(
        blank=True,
        help_text=("True/False for if technology has option to participate in net metering agreement with utility. "
                   "Note that a technology can only participate in either net metering or wholesale rates (not both).")
    )
    can_wholesale = models.BooleanField(
        blank=True,
        help_text=("True/False for if technology has option to export energy that is compensated at the wholesale_rate. "
                   "Note that a technology can only participate in either net metering or wholesale rates (not both).")
    )
    can_export_beyond_nem_limit = models.BooleanField(
        blank=True,
        help_text=("True/False for if technology can export energy beyond the annual site load (and be compensated for "
                   "that energy at the export_rate_beyond_net_metering_limit).")
    )
    can_curtail = models.BooleanField(
        default=True,
        blank=True,
        help_text="True/False for if technology has the ability to curtail energy production."
    )

    operating_reserve_required_pct = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0)
        ],
        blank=True,
        null=True,
        help_text=""
    )


class PVOutputs(BaseModel, models.Model):
    key = "PVOutputs"
    meta = models.ForeignKey(
        to=APIMeta,
        on_delete=models.CASCADE,
        related_name="PVOutputs",
        unique=False
    )
    name = models.TextField(
        blank=True,
        default="PV",
        help_text="PV description for distinguishing between multiple PV models"
    )
    size_kw = models.FloatField(null=True, blank=True)
    lifecycle_om_cost_after_tax = models.FloatField(null=True, blank=True)
    lifecycle_om_cost_bau = models.FloatField(null=True, blank=True)
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

    meta = models.OneToOneField(
        APIMeta,
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
    prod_factor_series = ArrayField(
        models.FloatField(
            blank=True
        ),
        default=list, blank=True,
        help_text=("Optional user-defined production factors. Must be normalized to units of kW-AC/kW-DC nameplate, "
                   "representing the AC power (kW) output per 1 kW-DC of system capacity in each time step. "
                   "The series must be one year (January through December) of hourly, 30-minute, or 15-minute PV "
                   "generation data.")
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
    meta = models.OneToOneField(
        APIMeta,
        on_delete=models.CASCADE,
        related_name="WindOutputs",
        primary_key=True
    )

    size_kw = models.FloatField(null=True, blank=True)
    lifecycle_om_cost_after_tax = models.FloatField(null=True, blank=True)
    year_one_om_cost_before_tax = models.FloatField(null=True, blank=True)
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


class ElectricStorageInputs(BaseModel, models.Model):
    key = "ElectricStorage"

    meta = models.OneToOneField(
        APIMeta,
        on_delete=models.CASCADE,
        related_name="ElectricStorageInputs",
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
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0)
        ],
        blank=True,
        help_text="Battery state of charge at first hour of optimization as fraction of energy capacity."
    )
    can_grid_charge = models.BooleanField(
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


class ElectricStorageOutputs(BaseModel, models.Model):
    key = "ElectricStorageOutputs"
    meta = models.OneToOneField(
        APIMeta,
        on_delete=models.CASCADE,
        related_name="ElectricStorageOutputs",
        primary_key=True
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
    initial_capital_cost = models.FloatField(null=True, blank=True)
    maintenance_cost = models.FloatField(null=True, blank=True)
    state_of_health = ArrayField(
        models.FloatField(null=True, blank=True),
        blank=True, default=list
    )


class GeneratorInputs(BaseModel, models.Model):
    key = "Generator"

    meta = models.OneToOneField(
        APIMeta,
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
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(10.0)
        ],
        blank=True,
        null=True,
        help_text="Generator fuel consumption curve y-intercept in gallons per hour."
    )
    fuel_avail_gal = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        help_text="On-site generator fuel available in gallons."
    )
    min_turn_down_pct = models.FloatField(
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
    replacement_year = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        blank=True,
        null=True,
        help_text=""
    )

    replace_cost_per_kw = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1.0e9)
        ],
        blank=True,
        null=True,
        help_text=""
    )

    def clean(self):
        if self.max_kw > 0 or self.existing_kw > 0:
            total_kw = self.min_kw + self.existing_kw
            if total_kw <= 40:
                m = 0.068
                b = 0.0125
            elif total_kw <= 80:
                m = 0.066
                b = 0.0142
            elif total_kw <= 150:
                m = 0.0644
                b = 0.0095
            elif total_kw <= 250:
                m = 0.0648
                b = 0.0067
            elif total_kw <= 750:
                m = 0.0656
                b = 0.0048
            elif total_kw <= 1500:
                m = 0.0657
                b = 0.0043
            else:
                m = 0.0657
                b = 0.004
            if self.fuel_slope_gal_per_kwh == 0:
                self.fuel_slope_gal_per_kwh = m
            if self.fuel_intercept_gal_per_hr is None:
                self.fuel_intercept_gal_per_hr = b


class GeneratorOutputs(BaseModel, models.Model):
    key = "GeneratorOutputs"
    meta = models.OneToOneField(
        APIMeta,
        on_delete=models.CASCADE,
        related_name="GeneratorOutputs",
        primary_key=True
    )

    average_annual_fuel_used_gal = models.FloatField(null=True, blank=True)
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
    year_one_variable_om_cost_before_tax = models.FloatField(null=True, blank=True)
    year_one_variable_om_cost_bau = models.FloatField(null=True, blank=True)
    year_one_fuel_cost_before_tax = models.FloatField(null=True, blank=True)
    year_one_fuel_cost_bau = models.FloatField(null=True, blank=True)
    year_one_fixed_om_cost_before_tax = models.FloatField(null=True, blank=True)
    year_one_fixed_om_cost_bau = models.FloatField(null=True, blank=True)
    lifecycle_variable_om_cost_after_tax = models.FloatField(null=True, blank=True)
    lifecycle_variable_om_cost_bau = models.FloatField(null=True, blank=True)
    lifecycle_fuel_cost_after_tax = models.FloatField(null=True, blank=True)
    lifecycle_fuel_cost_bau = models.FloatField(null=True, blank=True)
    lifecycle_fixed_om_cost_after_tax = models.FloatField(null=True, blank=True)
    lifecycle_fixed_om_cost_bau = models.FloatField(null=True, blank=True)
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
    meta = models.ForeignKey(
        APIMeta,
        on_delete=models.CASCADE,
        unique=False,
        related_name="Message"
    )
    message_type = models.TextField(default='')
    message = models.TextField(default='')

# TODO other necessary models from reo/models.py


def get_input_dict_from_run_uuid(run_uuid:str):
    """
    Construct the input dict for REopt.run_reopt
    """
    # get inputs that are always created with one DB transaction
    meta = APIMeta.objects.select_related(
        "Settings",
        'FinancialInputs', 
        'SiteInputs',
        'ElectricLoadInputs',
    ).get(run_uuid=run_uuid)

    def filter_none_and_empty_array(d:dict):
        return {k: v for (k, v) in d.items() if v not in [None, [], {}]}

    d = dict()
    d["user_uuid"] = meta.user_uuid
    d["Settings"] = filter_none_and_empty_array(meta.Settings.dict)
    d["Financial"] = filter_none_and_empty_array(meta.FinancialInputs.dict)
    d["Site"] = filter_none_and_empty_array(meta.SiteInputs.dict)
    d["ElectricLoad"] = filter_none_and_empty_array(meta.ElectricLoadInputs.dict)

    # We have to try for the following objects because they may or may not be defined
    try:
        pvs = meta.PVInputs.all()
        if len(pvs) == 1:
            d["PV"] = filter_none_and_empty_array(pvs[0].dict)
        elif len(pvs) > 1:
            d["PV"] = []
            for pv in pvs:
                d["PV"].append(filter_none_and_empty_array(pv.dict))
    except: pass

    # Try to get electric tariff as it may be missing in off-grid scenarios
    try: d["ElectricTariff"] = filter_none_and_empty_array(meta.ElectricTariffInputs.dict)
    except: pass

    try: d["ElectricUtility"] = filter_none_and_empty_array(meta.ElectricUtilityInputs.dict)
    except: pass

    try: d["ElectricStorage"] = filter_none_and_empty_array(meta.ElectricStorageInputs.dict)
    except: pass

    try: d["Generator"] = filter_none_and_empty_array(meta.GeneratorInputs.dict)
    except: pass

    try: d["Wind"] = filter_none_and_empty_array(meta.WindInputs.dict)
    except: pass
    
    return d
