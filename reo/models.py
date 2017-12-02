# from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import *
import uuid
from picklefield.fields import PickledObjectField


class URDBError(models.Model):

    label = models.TextField(blank=True, default='')
    type = models.TextField(blank=True, default='')
    message = models.TextField(blank=True, default='')


class ScenarioModel(models.Model):

    # Inputs
    # user = models.ForeignKey(User, null=True, blank=True)
    run_uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    api_version = models.TextField(null=True, blank=True, default='')
    user_id = models.TextField(null=True, blank=True)
    
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

    #Relationships
    scenario_model = models.ForeignKey(
        ScenarioModel,
        on_delete=models.CASCADE,
        default=None
    )

    #Inputs
    latitude = models.FloatField()
    longitude = models.FloatField()
    land_acres = models.FloatField(null=True, blank=True)
    roof_squarefeet = models.FloatField(null=True, blank=True)
    
    @classmethod
    def create(cls, scenario_model=None, **kwargs):
        obj = cls(scenario_model=scenario_model, **kwargs)
        obj.save()

        return obj


class FinancialModel(models.Model):
    #Relationships
    site_model = models.ForeignKey(
        SiteModel,
        on_delete=models.CASCADE,
        default=None
    )

    #Input
    analysis_years = models.IntegerField()
    escalation_pct = models.FloatField()
    om_cost_escalation_pct = models.FloatField()
    offtaker_discount_pct = models.FloatField()
    offtaker_tax_pct = models.FloatField()
    owner_discount_pct = models.FloatField(null=True)
    owner_tax_pct = models.FloatField(null=True)

    #Outputs
    lcc_us_dollars = models.FloatField(null=True, blank=True)
    lcc_bau_us_dollars = models.FloatField(null=True, blank=True)
    npv_us_dollars = models.FloatField(null=True, blank=True)
    net_capital_costs_plus_om_us_dollars = models.FloatField(null=True, blank=True)
    

    @classmethod
    def create(cls, site_model=None, **kwargs):
        obj = cls(site_model=site_model, **kwargs)
        obj.save()

        return obj


class LoadProfileModel(models.Model):
    #Relationships
    site_model = models.ForeignKey(
        SiteModel,
        on_delete=models.CASCADE,
        default=None
    )
    
    #Inputs
    doe_reference_name = models.TextField(null=True, blank=True, default='')
    annual_kwh = models.FloatField(null=True, blank=True)
    year = models.IntegerField(default=2018)
    monthly_totals_kwh = ArrayField(models.FloatField(blank=True), default=[])
    loads_kw = ArrayField(models.FloatField(blank=True), default=[])
    outage_start_hour = models.IntegerField(null=True, blank=True)
    outage_end_hour = models.IntegerField(null=True, blank=True)
    critical_load_pct = models.FloatField()

    #Outputs
    year_one_electric_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), default=[])

    @classmethod
    def create(cls, site_model=None, **kwargs):
        obj = cls(site_model=site_model, **kwargs)
        obj.save()

        return obj


class ElectricTariffModel(models.Model):
    
    #Relationships
    site_model = models.ForeignKey(
        SiteModel,
        on_delete=models.CASCADE,
        default=None
    )
    
    #Inputs
    urdb_utilty_name = models.TextField(blank=True, default='')
    urdb_rate_name = models.TextField(blank=True, default='')
    urdb_label = models.TextField(blank=True, default='')
    blended_monthly_rates_us_dollars_per_kwh = ArrayField(models.FloatField(blank=True), default=[])
    blended_monthly_demand_charges_us_dollars_per_kw = ArrayField(models.FloatField(blank=True), default=[])
    net_metering_limit_kw = models.FloatField()
    interconnection_limit_kw = models.FloatField()
    wholesale_rate_us_dollars_per_kwh = models.FloatField()
    urdb_response = PickledObjectField(null=True)

    #Ouptuts
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

    @classmethod
    def create(cls, site_model=None, **kwargs):
        obj = cls(site_model=site_model, **kwargs)
        obj.save()

        return obj


class PVModel(models.Model):
    #Relationships
    site_model = models.ForeignKey(
        SiteModel,
        on_delete=models.CASCADE,
        default=None
    )

    #Inputs
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

    #Outputs
    size_kw = models.FloatField(null=True, blank=True)
    average_yearly_energy_produced_kwh = models.FloatField(null=True, blank=True)
    average_yearly_energy_exported_kwh = models.FloatField(null=True, blank=True)
    year_one_energy_produced_kwh = models.FloatField(null=True, blank=True)
    year_one_power_production_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_battery_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_grid_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    

    @classmethod
    def create(cls, site_model=None, **kwargs):
        obj = cls(site_model=site_model, **kwargs)
        obj.save()

        return obj
    

class WindModel(models.Model):
    #Relationships
    site_model = models.ForeignKey(
        SiteModel,
        on_delete=models.CASCADE,
        default=None
    )

    #Inputs
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

    #Outputs
    size_kw = models.FloatField(null=True, blank=True)
    average_yearly_energy_produced_kwh = models.FloatField(null=True, blank=True)
    average_yearly_energy_exported_kwh = models.FloatField(null=True, blank=True)
    year_one_energy_produced_kwh = models.FloatField(null=True, blank=True)
    year_one_power_production_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_battery_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_grid_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)

    @classmethod
    def create(cls, site_model=None, **kwargs):
        obj = cls(site_model=site_model, **kwargs)
        obj.save()

        return obj


class StorageModel(models.Model):
    #Relationships
    site_model = models.ForeignKey(
        SiteModel,
        on_delete=models.CASCADE,
        default=None
    )

    #Inputs
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

    #Outputs
    size_kw = models.FloatField(null=True, blank=True)
    size_kwh = models.FloatField(null=True, blank=True)
    year_one_to_load_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_to_grid_series_kw = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    year_one_soc_series_pct = ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True)
    
    @classmethod
    def create(cls, site_model=None, **kwargs):
        obj = cls(site_model=site_model, **kwargs)
        obj.save()

        return obj


class MessagesTypeModel(models.Model): 

    description = models.TextField(blank=True, default='')

    @classmethod
    def create(cls, text):
        objs = cls.objects.filter(description=text)
        if len(objs) > 0:
            return objs[0]
        else:

            obj = cls(description=text)
            obj.save()

        return obj


class MessagesGroupTypeModel(models.Model):

    description = models.TextField(blank=True, default='')

    @classmethod
    def create(cls, text):
        objs = cls.objects.filter(description=text)
        if len(objs) > 0:
            return objs[0]
        else:

            obj = cls(description=text)
            obj.save()

        return obj


class MessagesModel(models.Model):
    #Relationships
    scenario_model = models.ForeignKey(
        ScenarioModel,
        # to_field = 'run_uuid',
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True
    )

    messages_type_model = models.ForeignKey(
        MessagesTypeModel,
        on_delete=models.CASCADE,
        default=None
    )

    messages_group_type_model = models.ForeignKey(
        MessagesGroupTypeModel,
        on_delete=models.CASCADE,
        default=None
    )

    description = models.TextField(blank=True, default='')

    @classmethod
    def create(cls, scenario_model=None, messages_type_model=None,messages_group_type_model=None, **kwargs):
        obj = cls(scenario_model=scenario_model, messages_type_model=messages_type_model,
                  messages_group_type_model=messages_group_type_model, **kwargs)
        obj.save()

        return obj

    @classmethod
    def save_set(cls, message_dictionary, scenario_model=None):
        
        for k, v in message_dictionary.items():
            messages_type_model = MessagesTypeModel.create(text=k)
            if isinstance(v, dict):
                for kk, vv in v.items():
                    message_group_type_model = MessagesGroupTypeModel.create(text=kk)
                    obj = cls.create(scenario_model=scenario_model, messages_type_model=messages_type_model,
                                     messages_group_type_model=message_group_type_model, description=vv)
                    obj.save()

            else:
                message_group_type_model = MessagesGroupTypeModel.create(text="Other")
                obj = cls.create(scenario_model=scenario_model, messages_type_model=messages_type_model,
                                 messages_group_type_model=message_group_type_model, description=v)
                obj.save()


class BadPost(models.Model):
    run_uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    post = PickledObjectField()
    errors = models.TextField()

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


def attribute_inputs(inputs):
    return {k:v for k,v in inputs.items() if k[0]==k[0].lower() and v is not None}


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
        self.messagesM = None

    def create_and_save(self, data):
        """
        create and save models
        saves input json to db tables
        :param data: dict, constructed in api.py, mirrors reopt api response structure
        """
        d = data["inputs"]['Scenario']
        self.scenarioM = ScenarioModel.create(**attribute_inputs(d))
        self.siteM = SiteModel.create(scenario_model=self.scenarioM, **attribute_inputs(d['Site']))
        self.financialM = FinancialModel.create(site_model=self.siteM,
                                                **attribute_inputs(d['Site']['Financial']))
        self.load_profileM = LoadProfileModel.create(site_model=self.siteM,
                                                     **attribute_inputs(d['Site']['LoadProfile']))
        self.electric_tariffM = ElectricTariffModel.create(site_model=self.siteM,
                                                           **attribute_inputs(d['Site']['ElectricTariff']))
        self.pvM = PVModel.create(site_model=self.siteM, **attribute_inputs(d['Site']['PV']))
        self.windM = WindModel.create(site_model=self.siteM, **attribute_inputs(d['Site']['Wind']))
        self.storageM = StorageModel.create(site_model=self.siteM, **attribute_inputs(d['Site']['Storage']))
        self.messagesM = MessagesModel
        self.messagesM.save_set(data['messages'], scenario_model=self.scenarioM)

    def update(self, data):
        """
        save Scenario results in database
        :param data: dict, constructed in api.py, mirrors reopt api response structure
        :return: None
        """
        d = data["outputs"]["Scenario"]
        ScenarioModel.objects.filter(id=self.scenarioM.id).update(**attribute_inputs(d))
        SiteModel.objects.filter(id=self.siteM.id).update(**attribute_inputs(d['Site']))
        FinancialModel.objects.filter(id=self.financialM.id).update(**attribute_inputs(d['Site']['Financial']))
        LoadProfileModel.objects.filter(id=self.load_profileM.id).update(
            **attribute_inputs(d['Site']['LoadProfile']))
        ElectricTariffModel.objects.filter(id=self.electric_tariffM.id).update(
            **attribute_inputs(d['Site']['ElectricTariff']))
        PVModel.objects.filter(id=self.pvM.id).update(**attribute_inputs(d['Site']['PV']))
        WindModel.objects.filter(id=self.windM.id).update(**attribute_inputs(d['Site']['Wind']))
        StorageModel.objects.filter(id=self.storageM.id).update(**attribute_inputs(d['Site']['Storage']))
        # the next line will create redundant 'messages' if any values were also passed in the create_and_save call
        self.messagesM.save_set(data['messages'], scenario_model=self.scenarioM)

    def update_errors_status(self, data):
        """
        save Scenario results in database
        :param data: dict, constructed in api.py, mirrors reopt api response structure
        :return: None
        """
        d = data["outputs"]["Scenario"]
        ScenarioModel.objects.filter(id=self.scenarioM.id).update(**attribute_inputs(d))
        self.messagesM.save_set(data['messages'], scenario_model=self.scenarioM)
