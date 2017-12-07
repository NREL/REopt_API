# from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import *
from django.forms.models import model_to_dict
from picklefield.fields import PickledObjectField
from reo.nested_inputs import nested_input_definitions


class URDBError(models.Model):

    label = models.TextField(blank=True, default='')
    type = models.TextField(blank=True, default='')
    message = models.TextField(blank=True, default='')


class ScenarioModel(models.Model):

    # Inputs
    # user = models.ForeignKey(User, null=True, blank=True)
    run_uuid = models.UUIDField(unique=True)
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

    #Inputs
    run_uuid = models.UUIDField(unique=True)
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

    #Input
    run_uuid = models.UUIDField(unique=True)
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
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


class LoadProfileModel(models.Model):
    
    #Inputs
    run_uuid = models.UUIDField(unique=True)
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
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


class ElectricTariffModel(models.Model):
    
    #Inputs
    run_uuid = models.UUIDField(unique=True)
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
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


class PVModel(models.Model):

    #Inputs
    run_uuid = models.UUIDField(unique=True)
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
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj
    

class WindModel(models.Model):

    #Inputs
    run_uuid = models.UUIDField(unique=True)
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
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


class StorageModel(models.Model):

    #Inputs
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
    total_itc_pct = models.IntegerField()
    total_rebate_us_dollars_per_kw = models.IntegerField()

    #Outputs
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


class MessageModel(models.Model):
    """
    For Example:
    {"messages":{
                "warnings": "This is a warning message.",
                "errors": "REopt had an error."
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
    post = PickledObjectField()
    errors = models.TextField()

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()

        return obj


def attribute_inputs(inputs):
    return {k:v for k,v in inputs.items() if k[0]==k[0].lower() and v is not None}


class ErrorModel(models.Model):

    task = models.TextField(blank=True, default='')
    name = models.TextField(blank=True, default='')
    run_uuid = models.TextField(blank=True, default='')
    message = models.TextField(blank=True, default='')
    traceback = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, **kwargs):
        # not sure why, (or how to stop it), celery re-raises an exception a couple times and thus multiple
        # ErrorModel's are being saved to the database, so...
        if len(cls.objects.filter(run_uuid=kwargs['run_uuid'])) == 0:
            obj = cls(**kwargs)
            obj.save()
        # and if you include the following `else` statement, then celery raises PicklingError on the Exception object

        # else:
        #     obj = cls.objects.get(run_uuid=kwargs['run_uuid'])

        return None


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
        scenario_dict = data["outputs"]['Scenario'].copy()
        scenario_dict.update(d)

        self.scenarioM = ScenarioModel.create(**attribute_inputs(scenario_dict))
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
        for message_type, message in data['messages'].iteritems():
            MessageModel.create(run_uuid=self.scenarioM.run_uuid, message_type=message_type, message=message)

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
        SiteModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']))
        FinancialModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['Financial']))
        LoadProfileModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['LoadProfile']))
        ElectricTariffModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['ElectricTariff']))
        PVModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['PV']))
        WindModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['Wind']))
        StorageModel.objects.filter(run_uuid=run_uuid).update(**attribute_inputs(d['Site']['Storage']))

        for message_type, message in data['messages'].iteritems():
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
        for message_type, message in data['messages'].iteritems():
            if len(MessageModel.objects.filter(run_uuid=run_uuid, message=message)) > 0:
                # message already saved
                pass
            else:
                MessageModel.create(run_uuid=run_uuid, message_type=message_type, message=message)

    @staticmethod
    def make_response(run_uuid):
        """
        Reconstruct response dictionary from postgres tables (django models).
        NOTE: postgres column type UUID is not JSON serializable. Work-around is removing those columns and then
              adding back into outputs->Scenario as string.
        :param run_uuid:
        :return:
        """

        def remove_ids(d):
            del d['run_uuid']
            del d['id']
            return d
        
        def move_outs_to_ins(site_key, resp):

            resp['inputs']['Scenario']['Site'][site_key] = dict()

            for k in nested_input_definitions['Scenario']['Site'][site_key].iterkeys():

                try:
                    resp['inputs']['Scenario']['Site'][site_key][k] = resp['outputs']['Scenario']['Site'][site_key][k]
                    del resp['outputs']['Scenario']['Site'][site_key][k]
                except KeyError:  # known exception for k = urdb_response (user provided blended rates)
                    resp['inputs']['Scenario']['Site'][site_key][k] = None
        
        # add try/except for get fail / bad run_uuid
        site_keys = ['PV', 'Storage', 'Financial', 'LoadProfile', 'ElectricTariff']
        
        resp = dict()
        resp['outputs'] = dict()
        resp['inputs'] = dict()
        resp['inputs']['Scenario'] = dict()
        resp['inputs']['Scenario']['Site'] = dict()
        resp['messages'] = dict()
        
        resp['outputs']['Scenario'] = remove_ids(model_to_dict(ScenarioModel.objects.get(run_uuid=run_uuid)))
        resp['outputs']['Scenario']['run_uuid'] = str(run_uuid)
        resp['outputs']['Scenario']['Site'] = remove_ids(model_to_dict(SiteModel.objects.get(run_uuid=run_uuid)))
        resp['outputs']['Scenario']['Site']['Financial'] = remove_ids(model_to_dict(FinancialModel.objects.get(run_uuid=run_uuid)))
        resp['outputs']['Scenario']['Site']['LoadProfile'] = remove_ids(model_to_dict(LoadProfileModel.objects.get(run_uuid=run_uuid)))
        resp['outputs']['Scenario']['Site']['ElectricTariff'] = remove_ids(model_to_dict(ElectricTariffModel.objects.get(run_uuid=run_uuid)))
        resp['outputs']['Scenario']['Site']['PV'] = remove_ids(model_to_dict(PVModel.objects.get(run_uuid=run_uuid)))
        resp['outputs']['Scenario']['Site']['Storage'] = remove_ids(model_to_dict(StorageModel.objects.get(run_uuid=run_uuid)))

        wind_dict = remove_ids(model_to_dict(WindModel.objects.get(run_uuid=run_uuid)))

        if wind_dict['max_kw'] > 0:
            resp['outputs']['Scenario']['Site']['Wind'] = wind_dict
            site_keys.append('Wind')

        for m in MessageModel.objects.filter(run_uuid=run_uuid).values('message_type', 'message'):

            resp['messages'][m['message_type']] = m['message']
            
        for scenario_key in nested_input_definitions['Scenario'].iterkeys():

            if scenario_key.islower():
                resp['inputs']['Scenario'][scenario_key] = resp['outputs']['Scenario'][scenario_key]
                del resp['outputs']['Scenario'][scenario_key]

        for site_key in nested_input_definitions['Scenario']['Site'].iterkeys():

            if site_key.islower():
                resp['inputs']['Scenario']['Site'][site_key] = resp['outputs']['Scenario']['Site'][site_key]
                del resp['outputs']['Scenario']['Site'][site_key]

            elif site_key in site_keys:

                move_outs_to_ins(site_key, resp=resp)

        return resp

        # if not scenario_inputs['Site']['Wind']['max_kw'] > 0:
        #     data = remove_wind(data, output_format, model_solved)
        #     # need to delete wind messages, but intertwined with other messages from validator
        #
        # if output_format == 'flat':
        #     # fill in outputs with inputs
        #     for arg, defs in flat_inputs(full_list=True).iteritems():
        #         data[arg] = bundle.data.get(arg) or defs.get("default")
        #     # backwards compatibility for webtool, copy all "outputs" to top level of response dict
        #     if model_solved:
        #         data.update(optimization_results['flat'])
        #     data.update(scenario_outputs)


# def remove_wind(output_dictionary, output_format='nested'):
#     if output_format == 'nested':
#         del output_dictionary['inputs']['Scenario']['Site']["Wind"]
#         del output_dictionary['outputs']['Scenario']['Site']["Wind"]
#
#     if output_format == 'flat':
#         for key in ['wind_cost', 'wind_om', 'wind_kw_max', 'wind_kw_min', 'wind_itc_federal', 'wind_ibi_state',
#                     'wind_ibi_utility', 'wind_itc_federal_max', 'wind_ibi_state_max', 'wind_ibi_utility_max',
#                     'wind_rebate_federal', 'wind_rebate_state', 'wind_rebate_utility', 'wind_rebate_federal_max',
#                     'wind_rebate_state_max', 'wind_rebate_utility_max', 'wind_pbi', 'wind_pbi_max',
#                     'wind_pbi_years', 'wind_pbi_system_max', 'wind_macrs_schedule', 'wind_macrs_bonus_fraction']:
#             if key in output_dictionary['inputs'].keys():
#                 del output_dictionary['inputs'][key]
#             if key in output_dictionary['outputs'].keys():
#                 del output_dictionary['outputs'][key]
#
#     return output_dictionary
