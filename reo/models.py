from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import *
import uuid
from picklefield.fields import PickledObjectField
from library import DatLibrary
from utilities import is_error
import numpy as np



class RunInput(models.Model):

    user = models.ForeignKey(User, null=True) 
    api_version = models.TextField(blank=True, default='', null=False)
    timeout = models.IntegerField(blank=True, default=295, null=True)

    # Non-hooked up inputs
    time_steps_per_hour = models.IntegerField(null=True, blank=True)

    # Site Information
    latitude = models.FloatField(null=True,blank=True)
    longitude = models.FloatField(null=True, blank=True)
    land_area = models.FloatField(null=True,blank=True)
    roof_area = models.FloatField(null=True,blank=True)
    urdb_rate = PickledObjectField(null=True)
    load_profile_name = models.TextField(null=True, blank=True, default='')
    load_size = models.FloatField(null=True, blank=True)
    load_year = models.IntegerField(null=True, blank=True, default=2018)
    load_8760_kw = ArrayField(models.FloatField(blank=True), null=True, blank=True, default=[])
    load_monthly_kwh = ArrayField(models.FloatField(blank=True), null=True, blank=True, default=[])
    utility_name = models.TextField(blank=True, default='')
    rate_name = models.TextField(blank=True, default='')
    blended_utility_rate = ArrayField(models.FloatField(blank=True), null=True, blank=True, default=[])
    demand_charge = ArrayField(models.FloatField(blank=True), null=True, blank=True, default=[])

    # Financial Inputs
    analysis_period = models.IntegerField(null=True, blank=True)
    offtaker_discount_rate = models.FloatField(null=True, blank=True)
    offtaker_tax_rate = models.FloatField(null=True,blank=True)
    owner_discount_rate = models.FloatField(null=True, blank=True)
    owner_tax_rate = models.FloatField(null=True,blank=True)
    rate_escalation = models.FloatField(null=True,blank=True)
    rate_inflation = models.FloatField(null=True,blank=True)

    # Grid connection inputs
    net_metering_limit = models.FloatField(null=True,blank=True)
    wholesale_rate = models.FloatField(null=True,blank=True)
    interconnection_limit = models.FloatField(null=True,blank=True)

    # PV Cost
    pv_cost = models.FloatField(null=True,blank=True)
    pv_om = models.FloatField(null=True,blank=True)

    # PV Technology
    pv_kw_max = models.FloatField(null=True,blank=True)
    pv_kw_min = models.FloatField(null=True,blank=True)
    module_type = models.IntegerField(null=True, blank=True)
    azimuth = models.FloatField(null=True, blank=True)
    losses = models.FloatField(null=True, blank=True)
    dc_ac_ratio = models.FloatField(null=True, blank=True)
    gcr = models.FloatField(null=True, blank=True)
    dataset = models.TextField(blank=True, default='')
    inv_eff = models.FloatField(null=True, blank=True)
    system_capacity = models.FloatField(null=True, blank=True)
    array_type = models.IntegerField(null=True, blank=True)
    timeframe = models.TextField(blank=True, default='')
    radius = models.FloatField(null=True, blank=True)
    tilt = models.FloatField(null=True, blank=True)
    pv_degradation_rate = models.FloatField(null=True,blank=True)

    # PV Capital Cost Based Incentives
    pv_itc_federal = models.FloatField(null=True, blank=True)
    pv_itc_state = models.FloatField(null=True, blank=True)
    pv_itc_utility = models.FloatField(null=True, blank=True)

    pv_itc_federal_max = models.FloatField(null=True, blank=True)
    pv_itc_state_max = models.FloatField(null=True, blank=True)
    pv_itc_utility_max = models.FloatField(null=True, blank=True)

    pv_rebate_federal = models.FloatField(null=True, blank=True)
    pv_rebate_state = models.FloatField(null=True, blank=True)
    pv_rebate_utility = models.FloatField(null=True, blank=True)

    pv_rebate_federal_max = models.FloatField(null=True, blank=True)
    pv_rebate_state_max = models.FloatField(null=True, blank=True)
    pv_rebate_utility_max = models.FloatField(null=True, blank=True)

    # PV Production Based Incentives
    pv_pbi = models.FloatField(null=True, blank=True)
    pv_pbi_max = models.FloatField(null=True, blank=True)
    pv_pbi_years = models.FloatField(null=True, blank=True)
    pv_pbi_system_max = models.FloatField(null=True, blank=True)

    # PV MACRS
    pv_macrs_schedule = models.IntegerField(null=True, blank=True)
    pv_macrs_bonus_fraction = models.FloatField(null=True, blank=True)

    # Battery Costs
    batt_cost_kwh = models.FloatField(null=True,blank=True)
    batt_cost_kw = models.FloatField(null=True,blank=True)
    batt_replacement_cost_kw = models.FloatField(null=True, blank=True)
    batt_replacement_cost_kwh = models.FloatField(null=True, blank=True)
    batt_replacement_year_kw = models.IntegerField(null=True, blank=True)
    batt_replacement_year_kwh = models.IntegerField(null=True, blank=True)

    # Battery Technology
    batt_kw_max = models.FloatField(null=True,blank=True)
    batt_kw_min = models.FloatField(null=True,blank=True)
    batt_kwh_max = models.FloatField(null=True,blank=True)
    batt_kwh_min = models.FloatField(null=True,blank=True)
    batt_efficiency = models.FloatField(null=True,blank=True)
    batt_inverter_efficiency = models.FloatField(null=True,blank=True)
    batt_rectifier_efficiency = models.FloatField(null=True,blank=True)
    batt_soc_min = models.FloatField(null=True,blank=True)
    batt_soc_init = models.FloatField(null=True,blank=True)
    batt_can_gridcharge = models.FloatField(null=True,blank=True)

    # Battery Capital Cost Incentives
    batt_itc_total = models.FloatField(null=True, blank=True)
    batt_rebate_total = models.FloatField(null=True, blank=True)

    # Battery MACRS
    batt_macrs_schedule = models.IntegerField(null=True,blank=True)
    batt_macrs_bonus_fraction = models.FloatField(null=True, blank=True)
    batt_macrs_itc_reduction = models.FloatField(null=True, blank=True)

    # Resilience
    outage_start = models.IntegerField(null=True, blank=True)
    outage_end = models.IntegerField(null=True, blank=True)
    crit_load_factor = models.FloatField(null=True, blank=True)

    # Metadata
    created = models.DateTimeField(auto_now_add=True)

    def create_output(self, fields, json_POST):
        response_inputs = {f: getattr(self, f) for f in fields}

        run_uuid = uuid.uuid4()
        run_input_id = self.id

        run_set = DatLibrary(run_uuid, run_input_id, response_inputs)

        # Log POST request
        run_set.log_post(json_POST)

        # Run Optimization
        output_dictionary = run_set.run()
        error = is_error(output_dictionary)
        if error:
            return error

        # API level outputs
        output_dictionary['api_version'] = self.api_version
        output_dictionary['uuid'] = run_uuid

        result = RunOutput(**output_dictionary)
        result.save()

        return result
    
class RunOutput(models.Model):

    user = models.ForeignKey(User, null=True) 

    uuid = models.UUIDField(default=uuid.uuid4, null=False)
    run_input_id = models.IntegerField(null=False)
    api_version = models.TextField(blank=True, default='', null=False)
    timeout = models.IntegerField(blank=True, default=295, null=True)

    # Non-hooked up inputs
    time_steps_per_hour = models.IntegerField(null=True, blank=True)

    # Site Information
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    land_area = models.FloatField(null=True, blank=True)
    roof_area = models.FloatField(null=True, blank=True)
    urdb_rate = PickledObjectField(null=True)
    load_profile_name = models.TextField(null=True, blank=True, default='')
    load_size = models.FloatField(null=True, blank=True)
    load_year = models.IntegerField(null=True, blank=True, default=2018)
    load_8760_kw = ArrayField(models.FloatField(blank=True), null=True, blank=True, default=[])
    load_monthly_kwh = ArrayField(models.FloatField(blank=True), null=True, blank=True, default=[])
    utility_name = models.TextField(blank=True, default='')
    rate_name = models.TextField(blank=True, default='')
    blended_utility_rate = ArrayField(models.FloatField(blank=True), null=True, blank=True, default=[])
    demand_charge = ArrayField(models.FloatField(blank=True), null=True, blank=True, default=[])
    pv_kw_ac_hourly = ArrayField(models.FloatField(blank=True), null=True, blank=True, default=[])

    # Financial Inputs
    analysis_period = models.IntegerField(null=True, blank=True)
    offtaker_discount_rate = models.FloatField(null=True, blank=True)
    offtaker_tax_rate = models.FloatField(null=True, blank=True)
    owner_discount_rate = models.FloatField(null=True, blank=True)
    owner_tax_rate = models.FloatField(null=True, blank=True)
    rate_escalation = models.FloatField(null=True, blank=True)
    rate_inflation = models.FloatField(null=True, blank=True)

    # Grid connection inputs
    net_metering_limit = models.FloatField(null=True, blank=True)
    wholesale_rate = models.FloatField(null=True, blank=True)
    interconnection_limit = models.FloatField(null=True, blank=True)

    # PV Cost
    pv_cost = models.FloatField(null=True, blank=True)
    pv_om = models.FloatField(null=True, blank=True)

    # PV Technology
    pv_kw_max = models.FloatField(null=True, blank=True)
    pv_kw_min = models.FloatField(null=True, blank=True)
    module_type = models.IntegerField(null=True, blank=True)
    azimuth = models.FloatField(null=True, blank=True)
    losses = models.FloatField(null=True, blank=True)
    dc_ac_ratio = models.FloatField(null=True, blank=True)
    gcr = models.FloatField(null=True, blank=True)
    dataset = models.TextField(blank=True, default='')
    inv_eff = models.FloatField(null=True, blank=True)
    system_capacity = models.FloatField(null=True, blank=True)
    array_type = models.IntegerField(null=True, blank=True)
    timeframe = models.TextField(blank=True, default='')
    radius = models.FloatField(null=True, blank=True)
    tilt = models.FloatField(null=True, blank=True)
    pv_degradation_rate = models.FloatField(null=True, blank=True)

    # PV Capital Cost Based Incentives
    pv_itc_federal = models.FloatField(null=True, blank=True)
    pv_itc_state = models.FloatField(null=True, blank=True)
    pv_itc_utility = models.FloatField(null=True, blank=True)

    pv_itc_federal_max = models.FloatField(null=True, blank=True)
    pv_itc_state_max = models.FloatField(null=True, blank=True)
    pv_itc_utility_max = models.FloatField(null=True, blank=True)

    pv_rebate_federal = models.FloatField(null=True, blank=True)
    pv_rebate_state = models.FloatField(null=True, blank=True)
    pv_rebate_utility = models.FloatField(null=True, blank=True)

    pv_rebate_federal_max = models.FloatField(null=True, blank=True)
    pv_rebate_state_max = models.FloatField(null=True, blank=True)
    pv_rebate_utility_max = models.FloatField(null=True, blank=True)

    # PV Production Based Incentives
    pv_pbi = models.FloatField(null=True, blank=True)
    pv_pbi_max = models.FloatField(null=True, blank=True)
    pv_pbi_years = models.FloatField(null=True, blank=True)
    pv_pbi_system_max = models.FloatField(null=True, blank=True)

    # PV MACRS
    pv_macrs_schedule = models.IntegerField(null=True, blank=True)
    pv_macrs_bonus_fraction = models.FloatField(null=True, blank=True)
    pv_macrs_itc_reduction = models.FloatField(null=True, blank=True)

    # Battery Costs
    batt_cost_kwh = models.FloatField(null=True, blank=True)
    batt_cost_kw = models.FloatField(null=True, blank=True)
    batt_replacement_cost_kw = models.FloatField(null=True, blank=True)
    batt_replacement_cost_kwh = models.FloatField(null=True, blank=True)
    batt_replacement_year_kw = models.IntegerField(null=True, blank=True)
    batt_replacement_year_kwh = models.IntegerField(null=True, blank=True)

    # Battery Technology
    batt_kw_max = models.FloatField(null=True, blank=True)
    batt_kw_min = models.FloatField(null=True, blank=True)
    batt_kwh_max = models.FloatField(null=True, blank=True)
    batt_kwh_min = models.FloatField(null=True, blank=True)
    batt_efficiency = models.FloatField(null=True, blank=True)
    batt_inverter_efficiency = models.FloatField(null=True, blank=True)
    batt_rectifier_efficiency = models.FloatField(null=True, blank=True)
    batt_soc_min = models.FloatField(null=True, blank=True)
    batt_soc_init = models.FloatField(null=True, blank=True)
    batt_can_gridcharge = models.FloatField(null=True, blank=True)

    # Battery Capital Cost Incentives
    batt_itc_total = models.FloatField(null=True, blank=True)
    batt_rebate_total = models.FloatField(null=True, blank=True)

    # Battery MACRS
    batt_macrs_schedule = models.IntegerField(null=True, blank=True)
    batt_macrs_bonus_fraction = models.FloatField(null=True, blank=True)
    batt_macrs_itc_reduction = models.FloatField(null=True, blank=True)

    # Metadata
    created = models.DateTimeField(auto_now_add=True)

    # Output
    status = models.TextField(null=True, blank=True)
    lcc = models.FloatField(null=True, blank=True)
    lcc_bau = models.FloatField(null=True, blank=True)
    npv = models.FloatField(null=True, blank=True)
    irr = models.FloatField(null=True, blank=True)
    year_one_utility_kwh = models.FloatField(null=True, blank=True)
    pv_kw = models.FloatField(null=True, blank=True, default=0)
    batt_kw = models.FloatField(null=True, blank=True, default=0)
    batt_kwh = models.FloatField(null=True, blank=True, default=0)
    year_one_energy_cost = models.FloatField(null=True, blank=True)
    year_one_demand_cost = models.FloatField(null=True, blank=True)
    year_one_energy_cost_bau = models.FloatField(null=True, blank=True)
    year_one_demand_cost_bau = models.FloatField(null=True, blank=True)

    year_one_payments_to_third_party_owner = models.FloatField(null=True, blank=True)
    total_energy_cost = models.FloatField(null=True, blank=True)
    total_demand_cost = models.FloatField(null=True, blank=True)
    total_energy_cost_bau = models.FloatField(null=True, blank=True)
    total_demand_cost_bau = models.FloatField(null=True, blank=True)

    total_payments_to_third_party_owner = models.FloatField(null=True, blank=True)
    net_capital_costs_plus_om = models.FloatField(null=True, blank=True)
    average_yearly_pv_energy_produced = models.FloatField(null=True, blank=True)  # once wind is added, this will include wind production
    average_annual_energy_exported = models.FloatField(null=True, blank=True)

    year_one_electric_load_series = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_pv_to_battery_series = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_pv_to_load_series = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_pv_to_grid_series = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_grid_to_load_series = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_grid_to_battery_series = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_battery_to_load_series = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_battery_to_grid_series = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_battery_soc_series = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_energy_cost_series = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_demand_cost_series = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_datetime_start = models.DateTimeField(null=True, blank=True)

    year_one_export_benefit = models.FloatField(null=True, blank=True)
    year_one_energy_produced = models.FloatField(null=True, blank=True)

    # Resilience
    outage_start = models.IntegerField(null=True, blank=True)
    outage_end = models.IntegerField(null=True, blank=True)

    crit_load_factor = models.FloatField(null=True, blank=True)
    
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
        return  self.year_one_demand_cost + self.year_one_energy_cost

    @property
    def year_one_bill_bau(self):
        return self.year_one_demand_cost_bau + self.year_one_energy_cost_bau
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
    def owner_discount_rate_nominal(self):
        return (1 + self.owner_discount_rate) * (1 + self.rate_inflation) - 1
    
    @property
    def rate_escalation_nominal(self):
        return (1 + self.rate_escalation) * (1 + self.rate_inflation) - 1
    
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

                # cash incentives (need to rename state, util from ITC)
                self.incentives[t]['ibi_sta_percent'] = self.pv_itc_state
                self.incentives[t]['ibi_sta_percent_maxvalue'] = self.pv_itc_state_max
                self.incentives[t]['ibi_uti_percent'] = self.pv_itc_utility
                self.incentives[t]['ibi_uti_percent_maxvalue'] = self.pv_itc_utility_max

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
                #self.incentives[t]['itc_fed_percent_maxvalue'] = self.batt_itc_federal_max

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
        nominal_escalation_modifier = 1 + self.rate_escalation_nominal
        inflation_modifier = 1 + self.rate_inflation
        annual_energy[1] = self.year_one_energy_produced
        federal_taxable_income_before_deductions[1] = sum([self.federal_taxable_income_before_deductions(tech) for tech in self.techs])

        for year in range(1, n_cols):

            inflation_modifier_n = inflation_modifier ** year
            nominal_escalation_modifier_n = nominal_escalation_modifier ** year
            degradation_modifier = 1 - self.pv_degradation_rate

            if year > 1:
                annual_energy[year] = annual_energy[year - 1] * (1 - self.pv_degradation_rate)

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
            federal_income_tax[year] = (federal_taxable_income_before_deductions[year]-federal_total_deductions[year]) * self.owner_tax_rate
            federal_tax_liability[year] = -federal_income_tax[year] + federal_itc_to_apply

            # After tax calculation
            after_tax_annual_costs[year] = pre_tax_cash_flow[year] + \
                                           total_cash_incentives[year] + \
                                           federal_tax_liability[year]

            after_tax_value_of_energy[year] = value_of_savings[year] * (1 - self.owner_tax_rate)
            after_tax_cash_flow[year] = after_tax_annual_costs[year] + after_tax_value_of_energy[year]

            net_annual_costs_without_system[year] = -bill_without_system[year] * (1 - self.owner_tax_rate)
            net_annual_costs_with_system[year] = after_tax_annual_costs[year] - (bill_with_system[year] + exports_with_system[year]) * (1 - self.owner_tax_rate)

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

        self.npv = np.npv(self.owner_discount_rate_nominal, after_tax_cash_flow)
        self.lcc = -np.npv(self.owner_discount_rate_nominal, net_annual_costs_with_system)
        self.lcc_bau = -np.npv(self.owner_discount_rate_nominal, net_annual_costs_without_system)

