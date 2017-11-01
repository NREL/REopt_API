import logging
import os
import json
import copy
import uuid
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse, HttpResponse
from tastypie.http import HttpCreated
from tastypie.resources import ModelResource
from validators import REoptResourceValidation, ValidateNestedInput
from log_levels import log
from utilities import API_Error, attribute_inputs
from scenario import Scenario
from reo.models import ScenarioModel, MessagesModel, FinancialModel, LoadProfileModel, ElectricTariffModel, \
    PVModel, WindModel, StorageModel, SiteModel, ScenarioModel


api_version = "version 1.0.0"
save_to_db = True

def setup_logging():
    file_logfile = os.path.join(os.getcwd(), "log", "reopt_api.log")
    logging.basicConfig(filename=file_logfile,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M%S %p',
                        level=logging.INFO)
    log("INFO", "Logging setup")


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
                raise ImmediateHttpResponse(response=self.error_response(bundle.request, bundle.error_response))

            input_validator = ValidateNestedInput(bundle.data, nested=False)

        else:  # nested input
            output_format = 'nested'
            input_validator = ValidateNestedInput(bundle.data, nested=True)

        # Return  Results
        output_model = self.create_output(input_validator, output_format)

        raise ImmediateHttpResponse(HttpResponse(json.dumps(output_model), content_type='application/json', status=200))
    

    def create_output(self, input_validator, output_format):

        run_uuid = uuid.uuid4()
        meta = {'run_uuid':str(run_uuid), 'api_version':api_version}
      
        output_dictionary = {}
        output_dictionary["inputs"] = input_validator.input_dict
        output_dictionary['outputs'] = {"Scenario":meta}
        output_dictionary["messages"] = input_validator.messages

        if input_validator.isValid:
            try: # should return output structure to match new nested_outputs, even with exception
               
                scenario_inputs = copy.deepcopy(input_validator.input_dict['Scenario'])
                scenario_inputs.update(meta)
                
                if save_to_db:
                    self.save_scenario_inputs(scenario_inputs)

                s = Scenario(inputs_dict=scenario_inputs)

                # Log POST request
                s.log_post(input_validator.input_dict)

                # Run Optimization
                optimization_results = s.run()
                output_dictionary['outputs'].update(optimization_results[output_format])
                
                if save_to_db:
                    self.save_scenario_outputs(output_dictionary['outputs']['Scenario'])
                
            except Exception as e:
                
                output_dictionary["messages"] = {
                        "error": API_Error(e).response,
                        "warnings": input_validator.warnings,
                    }
        
        if save_to_db:
            if not input_validator.isValid:
                ScenarioModel.create(**meta)

            #Do we want to save messages for invalid posts?
            messages = MessagesModel.save_set(output_dictionary['messages'], scenario_uuid = run_uuid)    

        return output_dictionary

    def save_scenario_inputs(self,d):
        """
        saves input json to db tables
        :param d: validated input dictionary
        :return: None
        """
        self.scenarioM = ScenarioModel.create(**attribute_inputs(d))
        self.siteM = SiteModel.create(scenario_model = self.scenarioM, **attribute_inputs(d['Site']))
        self.financialM = FinancialModel.create(site_model = self.siteM, **attribute_inputs(d['Site']['Financial']))
        self.load_profileM = LoadProfileModel.create(site_model = self.siteM,**attribute_inputs(d['Site']['LoadProfile']))
        self.electric_tariffM = ElectricTariffModel.create(site_model = self.siteM,**attribute_inputs(d['Site']['ElectricTariff']))
        self.pvM = PVModel.create(site_model = self.siteM,**attribute_inputs(d['Site']['PV']))
        self.windM = WindModel.create(site_model = self.siteM,**attribute_inputs(d['Site']['Wind']))    
        self.storageM = StorageModel.create(site_model =self.siteM,**attribute_inputs(d['Site']['Storage']))

    
    def save_scenario_outputs(self,d):
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
