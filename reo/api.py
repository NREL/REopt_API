import json
import uuid
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse, HttpResponse
from tastypie.resources import ModelResource
from validators import REoptResourceValidation, ValidateNestedInput
from log_levels import setup_logging
from utilities import API_Error, attribute_inputs
from scenario import Scenario
from reo.models import MessagesModel, FinancialModel, LoadProfileModel, ElectricTariffModel, \
    PVModel, WindModel, StorageModel, SiteModel, ScenarioModel
from api_definitions import inputs as flat_inputs


api_version = "version 1.0.0"
saveToDb = True



class RunInputResource(ModelResource):

    class Meta:
        setup_logging()
        queryset = ScenarioModel.objects.all()
        resource_name = 'reopt'
        allowed_methods = ['post']
        detail_allowed_methods = []
        object_class = ScenarioModel
        authorization = ReadOnlyAuthorization()
        serializer = Serializer(formats=['json'])
        always_return_data = True
        validation = REoptResourceValidation()
        
    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj['id']

        return kwargs

    def get_object_list(self, request):
        return [request]

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)

    def obj_create(self, bundle, **kwargs):
        
        if 'Scenario' not in bundle.data.keys():
            self.is_valid(bundle)  # runs REoptResourceValidation
            output_format = 'flat'

            if bundle.errors:
                raise ImmediateHttpResponse(response=self.error_response(bundle.request, bundle.errors))

            input_validator = ValidateNestedInput(bundle.data, nested=False)

        else:  # nested input
            output_format = 'nested'
            input_validator = ValidateNestedInput(bundle.data, nested=True)

        # Return  Results
        output_model = self.create_output(input_validator, output_format)

        raise ImmediateHttpResponse(HttpResponse(json.dumps(output_model), content_type='application/json', status=201))

    def create_output(self, input_validator, output_format):

        run_uuid = uuid.uuid4()
        meta = {'run_uuid': str(run_uuid), 'api_version': api_version}
      
        output_dictionary = dict()
        output_dictionary["inputs"] = input_validator.input_for_response
        output_dictionary['outputs'] = {"Scenario": meta}
        output_dictionary["messages"] = input_validator.messages

        if input_validator.isValid:
            try:
               
                scenario_inputs = input_validator.input_dict['Scenario']

                windEnabled = scenario_inputs['Site']['Wind']['max_kw'] > 0
                
                if saveToDb:
                    self.save_scenario_inputs(scenario_inputs)

                s = Scenario(run_uuid=run_uuid, inputs_dict=scenario_inputs)

                # Log POST request
                s.log_post_in(input_validator.input_dict)

                # Run Optimization
                optimization_results = s.run()

                optimization_results['flat'].update(meta)
                optimization_results['flat']['uuid'] = meta['run_uuid']
                optimization_results['nested']['Scenario'].update(meta)
                output_dictionary['outputs'] = optimization_results[output_format]

                if saveToDb:
                    self.save_scenario_outputs(optimization_results['nested']['Scenario'])
               
                if not windEnabled:
                    output_dictionary = self.remove_wind(output_dictionary, output_format)
               
            except Exception as e:
                
                output_dictionary["messages"] = {
                        "error": API_Error(e).response,
                        "warnings": input_validator.warnings,
                    }


        if saveToDb:
            if len(ScenarioModel.objects.filter(run_uuid=run_uuid))==0:
                ScenarioModel.create(**meta)

            messages = MessagesModel.save_set(output_dictionary['messages'], scenario_uuid=run_uuid)

        if output_format == 'flat':
            # fill in outputs with inputs
            for arg, defs in flat_inputs(full_list=True).iteritems():
                output_dictionary['outputs'][arg] = output_dictionary["inputs"].get(arg) or defs.get("default")
            # backwards compatibility for webtool, copy all "outputs" to top level of response dict
            output_dictionary.update(output_dictionary['outputs'])

        s.log_post_out(output_dictionary)
        return output_dictionary

    @staticmethod
    def remove_wind(output_dictionary, output_format):
        if output_format == 'nested':
            del output_dictionary['inputs']['Scenario']['Site']["Wind"]
            del output_dictionary['outputs']['Scenario']['Site']["Wind"]
        
        if output_format=='flat':
            for key in ['wind_cost', 'wind_om', 'wind_kw_max', 'wind_kw_min', 'wind_itc_federal', 'wind_ibi_state',
                        'wind_ibi_utility', 'wind_itc_federal_max', 'wind_ibi_state_max', 'wind_ibi_utility_max',
                        'wind_rebate_federal', 'wind_rebate_state', 'wind_rebate_utility', 'wind_rebate_federal_max',
                        'wind_rebate_state_max', 'wind_rebate_utility_max', 'wind_pbi', 'wind_pbi_max',
                        'wind_pbi_years', 'wind_pbi_system_max', 'wind_macrs_schedule', 'wind_macrs_bonus_fraction']:
                if key in output_dictionary['inputs'].keys():
                    del output_dictionary['inputs'][key]
                if key in output_dictionary['outputs'].keys():
                    del output_dictionary['outputs'][key]

        return output_dictionary

    def save_scenario_inputs(self, d):
        """
        saves input json to db tables
        :param d: validated input dictionary
        :return: None
        """
        self.scenarioM = ScenarioModel.create(**attribute_inputs(d))
        self.siteM = SiteModel.create(scenario_model=self.scenarioM, **attribute_inputs(d['Site']))
        self.financialM = FinancialModel.create(site_model=self.siteM, **attribute_inputs(d['Site']['Financial']))
        self.load_profileM = LoadProfileModel.create(site_model=self.siteM, **attribute_inputs(d['Site']['LoadProfile']))
        self.electric_tariffM = ElectricTariffModel.create(site_model=self.siteM, **attribute_inputs(d['Site']['ElectricTariff']))
        self.pvM = PVModel.create(site_model=self.siteM, **attribute_inputs(d['Site']['PV']))
        self.windM = WindModel.create(site_model=self.siteM, **attribute_inputs(d['Site']['Wind']))
        self.storageM = StorageModel.create(site_model =self.siteM, **attribute_inputs(d['Site']['Storage']))

    def save_scenario_outputs(self, d):
        """

        :param r: Scenario.run response
        :return: OutputModel to be saved in REoptResponse as 'outputs'
        """        
        
        ScenarioModel.objects.filter(id=self.scenarioM.id).update(**attribute_inputs(d))   
        SiteModel.objects.filter(id=self.siteM.id).update(**attribute_inputs(d['Site']))
        FinancialModel.objects.filter(id=self.financialM.id).update(**attribute_inputs(d['Site']['Financial']))
        LoadProfileModel.objects.filter(id=self.load_profileM.id).update(**attribute_inputs(d['Site']['LoadProfile']))
        ElectricTariffModel.objects.filter(id=self.electric_tariffM.id).update(**attribute_inputs(d['Site']['ElectricTariff']))
        PVModel.objects.filter(id=self.pvM.id).update(**attribute_inputs(d['Site']['PV']))
        WindModel.objects.filter(id=self.windM.id).update(**attribute_inputs(d['Site']['Wind']))
        StorageModel.objects.filter(id=self.storageM.id).update(**attribute_inputs(d['Site']['Storage']))
