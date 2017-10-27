import logging
import os
import uuid
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import ModelResource
from validators import REoptResourceValidation, ValidateNestedInput
from log_levels import log
from utilities import API_Error
from scenario import Scenario
from reo.models import REoptPost, REoptResponse, MessagesModel, FinancialModel, LoadProfileModel, ElectricTariffModel, \
    PVModel, WindModel, StorageModel, SiteModel, ScenarioModel, OutputModel, ScenarioOutputModel, SiteOutputModel, \
    PVOutputModel, WindOutputModel, StorageOutputModel, FinancialOutputModel, ElectricTariffOutputModel, \
    LoadProfileOutputModel, WorkingResponse


api_version = "version 1.0.0"


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
        queryset = REoptPost.objects.all()
        resource_name = 'reopt'
        allowed_methods = ['post']
        detail_allowed_methods = []
        object_class = REoptPost
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

            if bundle.errors:
                raise ImmediateHttpResponse(response=self.error_response(bundle.request, bundle.errors))

            input_validator = ValidateNestedInput(bundle.data, nested=False)

        else:  # nested input
            input_validator = ValidateNestedInput(bundle.data, nested=True)

        # Return  Results
        output_model = self.create_output(bundle.data, input_validator)
        bundle.obj = output_model
        bundle.data = {k: v for k, v in output_model.__dict__.items() if not k.startswith('_')}
        bundle.data['id'] = 1  # get error without this line?

        return self.full_hydrate(bundle)

    def create_output(self, json_POST, input_validator):

        run_uuid = uuid.uuid4()
        if not input_validator.isValid:
            output_dictionary = {
                "messages": input_validator.error_response,
                "inputs": json_POST,
                "outputs": {"Scenario":{}}
            }
        else:
            try: # should return output structure to match new nested_outputs, even with exception
                s = Scenario(run_uuid=run_uuid, inputs_dict=input_validator.input_dict['Scenario'])

                # Log POST request
                s.log_post(json_POST)

                # Run Optimization
                output_dictionary = dict()
                output_dictionary['outputs'] = s.run()
                output_dictionary['inputs'] = json_POST
                output_dictionary['messages'] = input_validator.warnings

            except Exception as e:
                output_dictionary = {
                    "messages": {
                        "error": API_Error(e).response,
                        "warnings": input_validator.warnings,
                    },
                "outputs": {"Scenario":{}}
                }

        # output_dictionary['messages'] = MessagesModel()
        # messages.save()

        # output_dictionary['inputs'] = self.create_input_models(input_validator.input_dict)
        # output_dictionary['outputs'] = self.create_output_models(reopt_outputs)
        output_dictionary["inputs"] = json_POST
        output_dictionary["outputs"]["Scenario"]["uuid"] = run_uuid
        output_dictionary["outputs"]["Scenario"]["api_version"] = api_version

        # result = REoptResponse(**output_dictionary)
        result = WorkingResponse(**output_dictionary)
        # result.save()

        return result

    @staticmethod
    def create_input_models(d):
        """
        sub-dictionaries must be saved before passing to higher level keys in the nested format (django db protections)
        :param d: validated input dictionary
        :return: REoptPost instance, which becomes the 'inputs' in the REoptResponse
        """
        Financial = FinancialModel(**d['Scenario']['Site']['Financial'])
        Financial.save()
        LoadProfile = LoadProfileModel(**d['Scenario']['Site']['LoadProfile'])
        LoadProfile.save()
        ElectricTariff = ElectricTariffModel(**d['Scenario']['Site']['ElectricTariff'])
        ElectricTariff.save()
        PV = PVModel(**d['Scenario']['Site']['PV'])
        PV.save()
        Wind = WindModel(**d['Scenario']['Site']['Wind'])
        Wind.save()
        Storage = StorageModel(**d['Scenario']['Site']['Storage'])
        Storage.save()

        """
        Cannot pass redundant keys to django models, so the next two `for` loops remove all of the upper case keys,
        such that only the lower case "attributes" of the model are unpacked in the Model instantiation
        """
        site_vals = dict()
        for k, v in d['Scenario']['Site'].items():
            if k.islower():
                site_vals.update({k:v})
        Site = SiteModel(Financial=Financial, LoadProfile=LoadProfile, ElectricTariff=ElectricTariff, PV=PV, Wind=Wind,
                         Storage=Storage, **site_vals)
        Site.save()

        scenario_vals = dict()
        for k, v in d['Scenario'].items():
            if k.islower():
                scenario_vals.update({k:v})
        Scenario = ScenarioModel(Site=Site, **scenario_vals)
        Scenario.save()

        post = REoptPost(Scenario=Scenario)
        post.save()
        return post
    
    @staticmethod
    def create_output_models(r):
        """

        :param r: Scenario.run response
        :return: OutputModel to be saved in REoptResponse as 'outputs'
        """
        Financial = FinancialOutputModel(**r['Scenario']['Site']['Financial'])
        Financial.save()
        LoadProfile = LoadProfileOutputModel(**r['Scenario']['Site']['LoadProfile'])
        LoadProfile.save()
        ElectricTariff = ElectricTariffOutputModel(**r['Scenario']['Site']['ElectricTariff'])
        ElectricTariff.save()
        PV = PVOutputModel(**r['Scenario']['Site']['PV'])
        PV.save()
        Wind = WindOutputModel(**r['Scenario']['Site']['Wind'])
        Wind.save()
        Storage = StorageOutputModel(**r['Scenario']['Site']['Storage'])
        Storage.save()

        """
        Cannot pass redundant keys to django models, so the next two `for` loops remove all of the upper case keys,
        such that only the lower case "attributes" of the model are unpacked in the Model instantiation
        """
        site_vals = dict()
        for k, v in r['Scenario']['Site'].items():
            if k.islower():
                site_vals.update({k: v})
        Site = SiteOutputModel(Financial=Financial, LoadProfile=LoadProfile, ElectricTariff=ElectricTariff, PV=PV,
                               Wind=Wind, Storage=Storage, **site_vals)
        Site.save()

        scenario_vals = dict()
        for k, v in r['Scenario'].items():
            if k.islower():
                scenario_vals.update({k: v})
        Scenario = ScenarioOutputModel(Site=Site, **scenario_vals)
        Scenario.save()

        output = OutputModel(Scenario=Scenario)
        output.save()
        return output
