# from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import *
import uuid
from picklefield.fields import PickledObjectField
import numpy as np


class URDBError(models.Model):

    label = models.TextField(blank=True, default='')
    type = models.TextField(blank=True, default='')
    message = models.TextField(blank=True, default='')


class FinancialModel(models.Model):
    analysis_years = models.IntegerField()
    escalation_pct = models.FloatField()
    owner_tax_pct = models.FloatField()
    om_cost_growth_pct = models.FloatField()
    offtaker_discount_pct = models.FloatField()
    offtaker_tax_pct = models.FloatField()
    owner_discount_pct = models.FloatField(null=True)
    owner_tax_pct = models.FloatField(null=True)


class LoadProfileModel(models.Model):
    doe_reference_name = models.TextField(null=True, blank=True, default='')
    annual_kwh = models.FloatField(null=True, blank=True)
    year = models.IntegerField(default=2018)
    monthly_totals_kwh = ArrayField(models.FloatField(blank=True), default=[])
    loads_kw = ArrayField(models.FloatField(blank=True), default=[])
    outage_start_hour = models.IntegerField(null=True, blank=True)
    outage_end_hour = models.IntegerField(null=True, blank=True)
    critical_load_pct = models.FloatField()


class ElectricTariffModel(models.Model):
    urdb_utilty_name = models.TextField(blank=True, default='')
    urdb_rate_name = models.TextField(blank=True, default='')
    urdb_label = models.TextField(blank=True, default='')
    blended_monthly_rates_us_dollars_per_kwh = ArrayField(models.FloatField(blank=True), default=[])
    monthly_demand_charges_us_dollars_per_kw = ArrayField(models.FloatField(blank=True), default=[])
    net_metering_limit_kw = models.FloatField()
    interconnection_limit_kw = models.FloatField()
    wholesale_rate_us_dollars_per_kwh = models.FloatField()
    urdb_response = PickledObjectField(null=True)


class PVModel(models.Model):
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
    degradation_pct = models.FloatField(null=True,blank=True)
    azimuth = models.FloatField()
    losses = models.FloatField()
    array_type = models.IntegerField()
    module_type = models.IntegerField()
    gcr = models.FloatField()
    dc_ac_ratio = models.FloatField()
    inv_eff = models.FloatField()
    radius = models.FloatField()
    tilt = models.FloatField()
    

class WindModel(models.Model):
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


class StorageModel(models.Model):
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
    total_itc_pct = models.IntegerField()
    total_rebate_us_dollars_per_kw = models.IntegerField()


class SiteModel(models.Model):
    latitude = models.FloatField()  # required
    longitude = models.FloatField()  # required
    land_acres = models.FloatField(null=True, blank=True)
    roof_squarefeet = models.FloatField(null=True, blank=True)
    Financial = models.ForeignKey(FinancialModel)
    LoadProfile = models.ForeignKey(LoadProfileModel)
    ElectricTariff = models.ForeignKey(ElectricTariffModel)
    PV = models.ForeignKey(PVModel)
    Wind = models.ForeignKey(WindModel)
    Storage = models.ForeignKey(StorageModel)


class ScenarioModel(models.Model):

    # user = models.ForeignKey(User, null=True, blank=True)  # not used
    timeout_seconds = models.IntegerField(default=295)
    time_steps_per_hour = models.IntegerField(default=8760)
    Site = models.ForeignKey(SiteModel)


class REoptPost(models.Model):

    Scenario = models.ForeignKey(ScenarioModel)
    created = models.DateTimeField(auto_now_add=True)


class MessagesModel(models.Model):
    warnings = PickledObjectField(null=True)
    errors = models.TextField(blank=True)


class LoadProfileOutputModel(models.Model):
    year_one_electric_load_series_kw = ArrayField(models.FloatField(blank=True), default=[])


class FinancialOutputModel(models.Model):
    lcc_us_dollars = models.FloatField(null=True, blank=True)
    lcc_bau_us_dollars = models.FloatField(null=True, blank=True)
    npv_us_dollars = models.FloatField(null=True, blank=True)
    net_capital_costs_plus_om_us_dollars = models.FloatField(null=True, blank=True)


class PVOutputModel(models.Model):
    size_kw = models.FloatField(null=True, blank=True)
    average_yearly_energy_produced_kwh = models.FloatField(null=True, blank=True)
    average_yearly_energy_exported_kwh = models.FloatField(null=True, blank=True)
    year_one_energy_produced_kwh = models.FloatField(null=True, blank=True)
    year_one_power_production_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_battery_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_grid_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)


class WindOutputModel(models.Model):
    size_kw = models.FloatField(null=True, blank=True)
    average_yearly_energy_produced_kwh = models.FloatField(null=True, blank=True)
    average_yearly_energy_exported_kwh = models.FloatField(null=True, blank=True)
    year_one_energy_produced_kwh = models.FloatField(null=True, blank=True)
    year_one_power_production_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_battery_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_grid_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)


class StorageOutputModel(models.Model):
    size_kw = models.FloatField(null=True, blank=True)
    size_kwh = models.FloatField(null=True, blank=True)
    year_one_to_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_grid_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_soc_series_pct = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)


class ElectricTariffOutputModel(models.Model):
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
    total_min_charge_adder_bau_us_dollars = models.FloatField(null=True, blank=True)
    year_one_bill_us_dollars = models.FloatField(null=True, blank=True)
    year_one_bill_bau_us_dollars = models.FloatField(null=True, blank=True)
    year_one_export_benefit_us_dollars = models.FloatField(null=True, blank=True)
    year_one_energy_cost_series_us_dollars_per_kwh = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_demand_cost_series_us_dollars_per_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_battery_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_energy_supplied_kwh = models.FloatField(null=True, blank=True)


class SiteOutputModel(models.Model):
    LoadProfile = models.ForeignKey(LoadProfileOutputModel)
    Financial = models.ForeignKey(FinancialOutputModel)
    PV = models.ForeignKey(PVOutputModel)
    Wind = models.ForeignKey(WindOutputModel)
    Storage = models.ForeignKey(StorageOutputModel)
    ElectricTariff = models.ForeignKey(ElectricTariffOutputModel)


class ScenarioOutputModel(models.Model):
    status = models.TextField(null=True, blank=True)
    Site = models.ForeignKey(SiteOutputModel)


class OutputModel(models.Model):
    Scenario = models.ForeignKey(ScenarioOutputModel, null=True, blank=True)


class REoptResponse(models.Model):

    messages = models.ForeignKey(MessagesModel)
    inputs = models.ForeignKey(REoptPost)
    outputs = models.ForeignKey(OutputModel)
    id = models.UUIDField(primary_key=True, unique=True)
    api_version = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
        
    @property
    def pv_installed_cost(self):
        return self.pv_kw * self.pv_cost

    @property
    def battery_installed_cost(self):
        return self.batt_kw * self.batt_cost_kw + self.batt_kwh * self.batt_cost_kwh
    
    @property    
    def total_capital_costs(self):
        return self.pv_installed_cost + self.battery_installed_cost

    @property
    def year_one_bill(self):
        return self.year_one_demand_cost + self.year_one_energy_cost + \
               self.year_one_fixed_cost + self.year_one_min_charge_adder

    @property
    def year_one_bill_bau(self):
        return self.year_one_demand_cost_bau + self.year_one_energy_cost_bau + \
               self.year_one_fixed_cost_bau + self.year_one_min_charge_adder_bau
    @property
    def year_one_savings(self):
        return self.year_one_bill_bau - self.year_one_bill

    @property
    def macrs_five_year(self):
        return [0.2, 0.32, 0.192, 0.1152, 0.1152, 0.0576]  # IRS pub 946
    @property
    def macrs_seven_year(self):
        return [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446]
    
    @property
    def techs(self):
        return ['PV', 'BATT']

    def load_incentives(self):

        self.incentives = dict()
        
        for t in self.techs:

            self.incentives[t] = {}
            
            if t == 'PV':

                self.incentives[t]['tech_cost'] = self.pv_installed_cost
                self.incentives[t]['tech_size'] = self.pv_kw

                # MACRS
                self.incentives[t]['macrs_schedule'] = self.pv_macrs_schedule
                self.incentives[t]['bonus_fraction'] = self.pv_macrs_bonus_fraction
                self.incentives[t]['macrs_itc_reduction'] = self.pv_macrs_itc_reduction

                # tax credits
                self.incentives[t]['itc_fed_percent'] = self.pv_itc_federal
                self.incentives[t]['itc_fed_percent_maxvalue'] = self.pv_itc_federal_max

                # cash incentives
                self.incentives[t]['ibi_sta_percent'] = self.pv_ibi_state
                self.incentives[t]['ibi_sta_percent_maxvalue'] = self.pv_ibi_state_max
                self.incentives[t]['ibi_uti_percent'] = self.pv_ibi_utility
                self.incentives[t]['ibi_uti_percent_maxvalue'] = self.pv_ibi_utility_max

                # capacity based incentives
                self.incentives[t]['cbi_fed_amount'] = self.pv_rebate_federal
                self.incentives[t]['cbi_fed_maxvalue'] = self.pv_rebate_federal_max
                self.incentives[t]['cbi_sta_amount'] = self.pv_rebate_state
                self.incentives[t]['cbi_sta_maxvalue'] = self.pv_rebate_state_max
                self.incentives[t]['cbi_uti_amount'] = self.pv_rebate_utility
                self.incentives[t]['cbi_uti_maxvalue'] = self.pv_rebate_utility_max

                # production based incentives
                self.incentives[t]['pbi_combined_amount'] = self.pv_pbi
                self.incentives[t]['pbi_combined_maxvalue'] = self.pv_pbi_max
                self.incentives[t]['pbi_combined_term'] = self.pv_pbi_years

            elif t == 'BATT':

                self.incentives[t]['tech_cost'] = self.battery_installed_cost
                self.incentives[t]['tech_size'] = self.batt_kw

                # MACRS
                self.incentives[t]['macrs_schedule'] = self.batt_macrs_schedule
                self.incentives[t]['bonus_fraction'] = self.batt_macrs_bonus_fraction
                self.incentives[t]['macrs_itc_reduction'] = self.batt_macrs_itc_reduction

                # tax credits
                self.incentives[t]['itc_fed_percent'] = self.batt_itc_total

                # capacity based incentives
                self.incentives[t]['cbi_fed_amount'] = self.batt_rebate_total

                # production based incentives
                self.incentives[t]['pbi_combined_amount'] = 0
                self.incentives[t]['pbi_combined_maxvalue'] = 0
                self.incentives[t]['pbi_combined_term'] = 0

        # tax credits reduce depreciation and ITC basis
            self.incentives[t]['itc_fed_percent_deprbas_fed'] = True

            # cash incentive is taxable
            self.incentives[t]['ibi_sta_percent_tax_fed'] = True
            self.incentives[t]['ibi_uti_percent_tax_fed'] = True

            self.incentives[t]['cbi_fed_tax_fed'] = True
            self.incentives[t]['cbi_sta_tax_fed'] = True
            self.incentives[t]['cbi_uti_tax_fed'] = True

            self.incentives[t]['pbi_combined_tax_fed'] = True

            # incentive reduces depreciation and ITC basis
            self.incentives[t]['ibi_sta_percent_deprbas_fed'] = False
            self.incentives[t]['ibi_uti_percent_deprbas_fed'] = False

            self.incentives[t]['cbi_fed_deprbas_fed'] = False
            self.incentives[t]['cbi_sta_deprbas_fed'] = False
            self.incentives[t]['cbi_uti_deprbas_fed'] = False

            # Assume state MACRS the same as fed
            self.incentives[t]['state_depreciation_equals_federal'] = True

             # calculated values
            self.incentives[t]['federal_itc_basis'] = self.federal_itc_basis(t)
            self.incentives[t]['federal_depreciation_basis'] = self.federal_depreciation_basis(t)

    def pbi_calculate(self, tech, year, annual_energy):

        pbi_amount = 0
        if year <= self.incentives[tech]['pbi_combined_term']:
            pbi_amount = min(self.incentives[tech]['pbi_combined_amount'] * annual_energy, self.incentives[tech]['pbi_combined_maxvalue'])
        return pbi_amount

    def federal_taxable_income_before_deductions(self, tech):

        taxable_income = 0
        tech_cost = self.incentives[tech]['tech_cost']
        tech_kw = self.incentives[tech]['tech_size']

        state_ibi = min(self.incentives[tech]['ibi_sta_percent'] * tech_cost,
                        self.incentives[tech]['ibi_sta_percent_maxvalue'])
        utility_ibi = min(self.incentives[tech]['ibi_uti_percent'] * tech_cost,
                          self.incentives[tech]['ibi_uti_percent_maxvalue'])
        federal_cbi = min(self.incentives[tech]['cbi_fed_amount'] * tech_kw,
                          self.incentives[tech]['cbi_fed_maxvalue'])
        state_cbi = min(self.incentives[tech]['cbi_sta_amount'] * tech_kw,
                        self.incentives[tech]['cbi_sta_maxvalue'])
        utility_cbi = min(self.incentives[tech]['cbi_uti_amount'] * tech_kw,
                          self.incentives[tech]['cbi_uti_maxvalue'])

        if self.incentives[tech]['ibi_sta_percent_tax_fed']:
            taxable_income += state_ibi
        if self.incentives[tech]['ibi_uti_percent_tax_fed']:
            taxable_income += utility_ibi
        if self.incentives[tech]['cbi_fed_tax_fed']:
            taxable_income += federal_cbi
        if self.incentives[tech]['cbi_sta_tax_fed']:
            taxable_income += state_cbi
        if self.incentives[tech]['cbi_uti_tax_fed']:
            taxable_income += utility_cbi

        return taxable_income

    def federal_depreciation_basis(self, tech):

        tech_cost = self.incentives[tech]['tech_cost']

        federal_itc = min(self.incentives[tech]['itc_fed_percent'] * tech_cost,
                          self.incentives[tech]['itc_fed_percent_maxvalue'])
        itc_federal = 0

        if self.incentives[tech]['itc_fed_percent_deprbas_fed']:
            itc_federal = self.incentives[tech]['macrs_itc_reduction'] * federal_itc

        federal_itc_basis = self.federal_itc_basis(tech)
        basis = federal_itc_basis - itc_federal

        return basis

    def federal_depreciation_amount_total(self, year):

        depreciation_amount = 0
        for tech in self.techs:
            bonus_fraction = 0
            macrs_schedule = self.incentives[tech]['macrs_schedule']

            macrs_schedule_array = []
            if macrs_schedule == 5:
                macrs_schedule_array = self.macrs_five_year
            elif macrs_schedule == 7:
                macrs_schedule_array = self.macrs_seven_year

            depreciation_basis = self.incentives[tech]['federal_depreciation_basis']
            if year == 1:
                bonus_fraction = self.incentives[tech]['bonus_fraction']
            if year <= len(macrs_schedule_array) and macrs_schedule > 0:
                depreciation_amount += depreciation_basis * (macrs_schedule_array[year - 1] + bonus_fraction)

        return depreciation_amount

    def federal_itc_basis(self, tech):

        # reduce the itc basis
        ibi_state = 0
        ibi_util = 0
        cbi_fed = 0
        cbi_state = 0
        cbi_util = 0

        tech_cost = self.incentives[tech]['tech_cost']
        tech_kw = self.incentives[tech]['tech_size']

        state_ibi = min(self.incentives[tech]['ibi_sta_percent'] * tech_cost,
                        self.incentives[tech]['ibi_sta_percent_maxvalue'])
        utility_ibi = min(self.incentives[tech]['ibi_uti_percent'] * tech_cost,
                          self.incentives[tech]['ibi_uti_percent_maxvalue'])
        federal_cbi = min(self.incentives[tech]['cbi_fed_amount'] * tech_kw,
                          self.incentives[tech]['cbi_fed_maxvalue'])
        state_cbi = min(self.incentives[tech]['cbi_sta_amount'] * tech_kw,
                        self.incentives[tech]['cbi_sta_maxvalue'])
        utility_cbi = min(self.incentives[tech]['cbi_uti_amount'] * tech_kw,
                          self.incentives[tech]['cbi_uti_maxvalue'])

        if self.incentives[tech]['ibi_sta_percent_deprbas_fed']:
            ibi_state = state_ibi
        if self.incentives[tech]['ibi_uti_percent_deprbas_fed']:
            ibi_util = utility_ibi
        if self.incentives[tech]['cbi_fed_deprbas_fed']:
            cbi_fed = federal_cbi
        if self.incentives[tech]['cbi_sta_deprbas_fed']:
            cbi_state = state_cbi
        if self.incentives[tech]['cbi_uti_deprbas_fed']:
            cbi_util = utility_cbi

        return tech_cost - ibi_state - ibi_util - cbi_fed - cbi_state - cbi_util

    def federal_itc_total(self):

        federal_itc = 0
        for tech in self.techs:
            tech_cost = self.incentives[tech]['tech_cost']
            federal_itc += min(self.incentives[tech]['itc_fed_percent'] * tech_cost,
                               self.incentives[tech]['itc_fed_percent_maxvalue'])
        return federal_itc

    def total_cash_incentives(self, tech):

        tech_cost = self.incentives[tech]['tech_cost']
        tech_kw = self.incentives[tech]['tech_size']

        state_ibi = float(min(self.incentives[tech]['ibi_sta_percent'] * tech_cost,
                        self.incentives[tech]['ibi_sta_percent_maxvalue']))
        utility_ibi = float(min(self.incentives[tech]['ibi_uti_percent'] * tech_cost,
                          self.incentives[tech]['ibi_uti_percent_maxvalue']))
        federal_cbi = float(min(self.incentives[tech]['cbi_fed_amount'] * tech_kw,
                          self.incentives[tech]['cbi_fed_maxvalue']))
        state_cbi = float(min(self.incentives[tech]['cbi_sta_amount'] * tech_kw,
                        self.incentives[tech]['cbi_sta_maxvalue']))
        utility_cbi = float(min(self.incentives[tech]['cbi_uti_amount'] * tech_kw,
                          self.incentives[tech]['cbi_uti_maxvalue']))

        return state_ibi + utility_ibi + federal_cbi + state_cbi + utility_cbi

    def compute_cashflow(self):
        self.load_incentives()

        n_cols = self.analysis_period + 1

        # row_vectors to match template spreadsheet
        zero_list = [0] * n_cols
        annual_energy = list(zero_list)
        bill_without_system = list(zero_list)
        bill_with_system = list(zero_list)
        exports_with_system = list(zero_list)
        value_of_savings = list(zero_list)
        o_and_m_capacity_cost = list(zero_list)
        batt_kw_replacement_cost = list(zero_list)
        batt_kwh_replacement_cost = list(zero_list)
        total_operating_expenses = list(zero_list)
        tech_operating_expenses = dict()
        total_deductible_expenses = list(zero_list)
        debt_amount = list(zero_list)
        pre_tax_cash_flow = list(zero_list)
        total_cash_incentives = list(zero_list)
        total_production_based_incentives = list(zero_list)
        federal_taxable_income_before_deductions = list(zero_list)
        federal_depreciation_amount = list(zero_list)
        federal_total_deductions = list(zero_list)
        federal_income_tax = list(zero_list)
        federal_tax_liability = list(zero_list)
        after_tax_annual_costs = list(zero_list)
        after_tax_value_of_energy = list(zero_list)
        after_tax_cash_flow = list(zero_list)
        net_annual_costs_with_system = list(zero_list)
        net_annual_costs_without_system = list(zero_list)

        # incentives, tax credits, depreciation
        federal_itc = self.federal_itc_total()

        # year 0 initializations
        total_cash_incentives[0] = sum([self.total_cash_incentives(tech) for tech in self.techs])
        debt_amount[0] = self.total_capital_costs - total_cash_incentives[0]
        pre_tax_cash_flow[0] = -debt_amount[0]
        after_tax_annual_costs[0] = total_cash_incentives[0] - self.total_capital_costs
        after_tax_cash_flow[0] = after_tax_annual_costs[0]
        net_annual_costs_with_system[0] = after_tax_annual_costs[0]
        net_annual_costs_without_system[0] = 0

        # year 1 initializations
        nominal_escalation_modifier = 1 + self.rate_escalation
        inflation_modifier = 1 + self.om_cost_growth_pct
        annual_energy[1] = self.year_one_energy_produced
        federal_taxable_income_before_deductions[1] = sum([self.federal_taxable_income_before_deductions(tech) for tech in self.techs])

        for year in range(1, n_cols):

            inflation_modifier_n = inflation_modifier ** year
            nominal_escalation_modifier_n = nominal_escalation_modifier ** year
            degradation_modifier = 1 - self.pv_degradation_pct

            if year > 1:
                annual_energy[year] = annual_energy[year - 1] * (1 - self.pv_degradation_pct)

            # Bill savings
            bill_without_system[year] = self.year_one_bill_bau * nominal_escalation_modifier_n
            bill_with_system[year] = self.year_one_bill * nominal_escalation_modifier_n
            exports_with_system[year] = self.year_one_export_benefit * nominal_escalation_modifier_n * degradation_modifier
            value_of_savings[year] = bill_without_system[year] - (bill_with_system[year] + exports_with_system[year])

            # Operating Expenses
            o_and_m_capacity_cost[year] = self.pv_om * self.pv_kw * inflation_modifier_n

            if self.batt_replacement_year_kw == year:
                batt_kw_replacement_cost[year] = self.batt_replacement_cost_kw * self.batt_kw

            if self.batt_replacement_year_kwh == year:
                batt_kwh_replacement_cost[year] = self.batt_replacement_cost_kwh * self.batt_kwh

            tech_operating_expenses['PV'] = o_and_m_capacity_cost[year]
            tech_operating_expenses['BATT'] = batt_kw_replacement_cost[year] + batt_kwh_replacement_cost[year]
            total_operating_expenses[year] = sum(tech_operating_expenses.values())

            # Tax deductible operating expenses
            for tech in self.techs:
                total_deductible_expenses[year] += tech_operating_expenses[tech]

            # Pre-tax cash flow
            pre_tax_cash_flow[year] = -(total_operating_expenses[year])

            # Direct cash incentives
            total_production_based_incentives[year] = self.pbi_calculate('PV', year, annual_energy[year])
            total_cash_incentives[year] += total_production_based_incentives[year]

            # Federal income tax
            if self.incentives['PV']['pbi_combined_tax_fed']:
                federal_taxable_income_before_deductions[year] += total_cash_incentives[year]

            federal_itc_to_apply = 0
            if year == 1:
                federal_itc_to_apply = federal_itc

            federal_depreciation_amount[year] = self.federal_depreciation_amount_total(year)
            federal_total_deductions[year] = total_deductible_expenses[year] + federal_depreciation_amount[year]
            federal_income_tax[year] = (federal_taxable_income_before_deductions[year]-federal_total_deductions[year]) * self.owner_tax_pct
            federal_tax_liability[year] = -federal_income_tax[year] + federal_itc_to_apply

            # After tax calculation
            after_tax_annual_costs[year] = pre_tax_cash_flow[year] + \
                                           total_cash_incentives[year] + \
                                           federal_tax_liability[year]

            after_tax_value_of_energy[year] = value_of_savings[year] * (1 - self.owner_tax_pct)
            after_tax_cash_flow[year] = after_tax_annual_costs[year] + after_tax_value_of_energy[year]

            net_annual_costs_without_system[year] = -bill_without_system[year] * (1 - self.owner_tax_pct)
            net_annual_costs_with_system[year] = after_tax_annual_costs[year] - (bill_with_system[year] + exports_with_system[year]) * (1 - self.owner_tax_pct)

        # Additional Unit test outputs
        self.fed_pv_depr_basis_calc = self.incentives['PV']['federal_depreciation_basis']
        self.fed_pv_itc_basis_calc = self.incentives['PV']['federal_itc_basis']
        self.fed_batt_depr_basis_calc = self.incentives['BATT']['federal_depreciation_basis']
        self.fed_batt_itc_basis_calc = self.incentives['BATT']['federal_itc_basis']
        self.pre_tax_cash_flow = pre_tax_cash_flow
        self.direct_cash_incentives = total_cash_incentives
        self.federal_tax_liability = federal_tax_liability
        self.bill_with_sys = bill_with_system
        self.exports_with_sys = exports_with_system
        self.bill_bau = bill_without_system
        self.total_operating_expenses = total_operating_expenses
        self.after_tax_annual_costs = after_tax_annual_costs
        self.after_tax_value = after_tax_value_of_energy
        self.after_tax_cash_flow = after_tax_cash_flow
        self.net_annual_cost_without_sys = net_annual_costs_without_system
        self.net_annual_cost_with_sys = net_annual_costs_with_system

        # compute outputs
        try:
            self.irr = np.irr(after_tax_cash_flow)
        except ValueError:
            self.irr = 0
            log("ERROR", "IRR calculation failed to compute a real number")

        if math.isnan(self.irr):
            self.irr = 0

        self.npv = np.npv(self.owner_discount_pct, after_tax_cash_flow)
        self.lcc = -np.npv(self.owner_discount_pct, net_annual_costs_with_system)
        self.lcc_bau = -np.npv(self.owner_discount_pct, net_annual_costs_without_system)


class WorkingResponse(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, null=False)
    api_version = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    inputs = PickledObjectField(null=True)
    outputs = PickledObjectField(null=True)
    messages = PickledObjectField(null=True)
