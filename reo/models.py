from django.db import models
from django.contrib.postgres.fields import *
from api_definitions import *
import json
from picklefield.fields import PickledObjectField
from library import *


# Create your models here.
class RunInput(models.Model):

    user_id = models.TextField(blank=True, default='')
    api_version = models.TextField(blank=True, default='', null=False)

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
    load_8760_kw = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    load_monthly_kwh = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    utility_name = models.TextField(blank=True, default='')
    rate_name = models.TextField(blank=True, default='')
    blended_utility_rate = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    demand_charge = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])

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
    batt_itc_federal = models.FloatField(null=True, blank=True)
    batt_itc_state = models.FloatField(null=True, blank=True)
    batt_itc_utility = models.FloatField(null=True, blank=True)

    batt_itc_federal_max = models.FloatField(null=True, blank=True)
    batt_itc_state_max = models.FloatField(null=True, blank=True)
    batt_itc_utility_max = models.FloatField(null=True, blank=True)

    batt_rebate_federal = models.FloatField(null=True, blank=True)
    batt_rebate_state = models.FloatField(null=True, blank=True)
    batt_rebate_utility = models.FloatField(null=True, blank=True)

    batt_rebate_federal_max = models.FloatField(null=True, blank=True)
    batt_rebate_state_max = models.FloatField(null=True, blank=True)
    batt_rebate_utility_max = models.FloatField(null=True, blank=True)

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

        run_set = DatLibrary(self.id, response_inputs)

        # Log POST request
        run_set.log_post(json_POST)

        # Run Optimization
        output_dictionary = run_set.run()
        
        if "ERROR" in output_dictionary.keys():
            return output_dictionary

        output_dictionary['api_version'] = self.api_version

        result = RunOutput(**output_dictionary)
        result.save()

        return result


class RunOutput(models.Model):

    run_input_id = models.IntegerField(null=False)
    user_id = models.TextField(default='', null=True, blank=True)
    api_version = models.TextField(blank=True, default='', null=False)

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
    load_8760_kw = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    load_monthly_kwh = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    utility_name = models.TextField(blank=True, default='')
    rate_name = models.TextField(blank=True, default='')
    blended_utility_rate = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    demand_charge = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])

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
    batt_itc_federal = models.FloatField(null=True, blank=True)
    batt_itc_state = models.FloatField(null=True, blank=True)
    batt_itc_utility = models.FloatField(null=True, blank=True)

    batt_itc_federal_max = models.FloatField(null=True, blank=True)
    batt_itc_state_max = models.FloatField(null=True, blank=True)
    batt_itc_utility_max = models.FloatField(null=True, blank=True)

    batt_rebate_federal = models.FloatField(null=True, blank=True)
    batt_rebate_state = models.FloatField(null=True, blank=True)
    batt_rebate_utility = models.FloatField(null=True, blank=True)

    batt_rebate_federal_max = models.FloatField(null=True, blank=True)
    batt_rebate_state_max = models.FloatField(null=True, blank=True)
    batt_rebate_utility_max = models.FloatField(null=True, blank=True)

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
    pv_kw = models.FloatField(null=True, blank=True)
    batt_kw = models.FloatField(null=True, blank=True)
    batt_kwh = models.FloatField(null=True, blank=True)
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
    average_yearly_pv_energy_produced = models.FloatField(null=True, blank=True)

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

    # Resilience
    outage_start = models.IntegerField(null=True, blank=True)
    outage_end = models.IntegerField(null=True, blank=True)
    crit_load_factor = models.FloatField(null=True, blank=True)

    def to_dictionary(self):
        output = {'run_input_id': self.run_input_id,
                  'api_version': self.api_version}

        for k in inputs(full_list=True).keys() + outputs().keys():
            if hasattr(self, k):
                output[k] = getattr(self, k)
            else:
                output[k] = 0
        return output
