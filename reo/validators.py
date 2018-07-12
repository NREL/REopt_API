import numpy as np
import pandas as pd
from urdb_logger import log_urdb_errors
from nested_inputs import nested_input_definitions, list_of_float
#Note: list_of_float is actually needed
import os
import csv
import copy

hard_problems_csv = os.path.join('reo', 'hard_problems.csv')
hard_problem_labels = [i[0] for i in csv.reader(open(hard_problems_csv, 'rb'))]


class URDB_RateValidator:

    error_folder = 'urdb_rate_errors'

    def __init__(self,_log_errors=True, **kwargs):
        """
        Takes a dictionary parsed from a URDB Rate Json response 
        - See http://en.openei.org/services/doc/rest/util_rates/?version=3

        Rates may or mat not have the following keys:

            label                       Type: string
            utility                     Type: string
            name                        Type: string
            uri                         Type: URI
            approved                    Type: boolean
            startdate                   Type: integer
            enddate                     Type: integer
            supercedes                  Type: string
            sector                      Type: string
            description                 Type: string
            source                      Type: string
            sourceparent                Type: URI
            basicinformationcomments    Type: string
            peakkwcapacitymin           Type: decimal
            peakkwcapacitymax           Type: decimal
            peakkwcapacityhistory       Type: decimal
            peakkwhusagemin             Type: decimal
            peakkwhusagemax             Type: decimal
            peakkwhusagehistory         Type: decimal
            voltageminimum              Type: decimal
            voltagemaximum              Type: decimal
            voltagecategory             Type: string
            phasewiring                 Type: string
            flatdemandunit              Type: string
            flatdemandstructure         Type: array
            demandrateunit              Type: string
            demandweekdayschedule       Type: array
            demandratchetpercentage     Type: array
            demandwindow                Type: decimal
            demandreactivepowercharge   Type: decimal
            coincidentrateunit          Type: string
            coincidentratestructure     Type: array
            coincidentrateschedule      Type: array
            demandattrs                 Type: array
            demandcomments              Type: string
            usenetmetering              Type: boolean
            energyratestructure         Type: array
            energyweekdayschedule       Type: array
            energyweekendschedule       Type: array
            energyattrs                 Type: array
            energycomments              Type: string
            fixedmonthlycharge          Type: decimal
            minmonthlycharge            Type: decimal
            annualmincharge             Type: decimal
        """
        self.errors = []                             #Catch Errors - write to output file
        self.warnings = []                           #Catch Warnings 
        for key in kwargs:                           #Load in attributes          
            setattr(self, key, kwargs[key])

        self.validate()                              #Validate attributes

        if _log_errors:
            log_urdb_errors(self.label, self.errors, self.warnings)

    def validate(self):
         
        # Check if in known hard problems
        if self.label in hard_problem_labels:
            self.errors.append("URDB Rate (label={}) is currently restricted due to performance limitations".format(self.label))

         # Validate each attribute with custom valdidate function
        for key in dir(self):                      
            v = 'validate_' + key
            if hasattr(self, v):
                getattr(self, v)()

    @property
    def dependencies(self):
        # map to tell if a field requires one or more other fields
        return {
            
            'demandweekdayschedule': ['demandratestructure'],
            'demandweekendschedule': ['demandratestructure'],
            'demandratestructure':['demandweekdayschedule','demandweekendschedule'],
            'energyweekdayschedule': ['energyratestructure'],
            'energyweekendschedule': ['energyratestructure'],
            'energyratestructure':['energyweekdayschedule','energyweekendschedule'],
            'flatdemandmonths': ['flatdemandstructure'],
            'flatdemandstructure': ['flatdemandmonths'],
        }

    @property
    def isValid(self):
        #True if no errors found during validation on init
        return self.errors == []

    # CUSTOM VALIDATION FUNCTIONS FOR EACH URDB ATTRIBUTE name validate_<attribute name>
    
    def validate_demandratestructure(self):
        name = 'demandratestructure'
        if self.validDependencies(name):
            self.validRate(name)

    def validate_demandweekdayschedule(self):
        name = 'demandweekdayschedule'
        self.validCompleteHours(name, [12,24]) 
        if self.validDependencies(name):
            self.validSchedule(name, 'demandratestructure')

    def validate_demandweekendschedule(self):
        name = 'demandweekendschedule'
        self.validCompleteHours(name, [12,24])
        if self.validDependencies(name):
            self.validSchedule(name, 'demandratestructure')

    def validate_energyweekendschedule(self):
        name = 'energyweekendschedule'
        self.validCompleteHours(name, [12,24])  
        if self.validDependencies(name):
            self.validSchedule(name, 'energyratestructure')

    def validate_energyweekdayschedule(self):
        name = 'energyweekdayschedule'
        self.validCompleteHours(name, [12,24])  
        if self.validDependencies(name):
            self.validSchedule(name, 'energyratestructure')

    def validate_energyratestructure(self):
        name = 'energyratestructure'
        if self.validDependencies(name):
            self.validRate(name)

    def validate_flatdemandstructure(self):
        name = 'flatdemandstructure'
        if self.validDependencies(name):
            self.validRate(name)

    def validate_flatdemandmonths(self):
        name = 'flatdemandmonths'
        self.validCompleteHours(name, [12])
        if self.validDependencies(name):
            self.validSchedule(name, 'flatdemandstructure')

    def validate_coincidentratestructure(self):
        name = 'coincidentratestructure'
        if self.validDependencies(name):
            self.validRate(name)

    def validate_coincidentrateschedule(self):
        name = 'coincidentrateschedule'
        if self.validDependencies(name):
            self.validSchedule(name, 'flatdemandstructure')


    #### FUNCTIONS TO VALIDATE ATTRIBUTES ####
    
    def validDependencies(self, name):
        # check that all dependent attributes exist
        # return Boolean if any errors found
        
        all_dependencies = self.dependencies.get(name)
        valid = True
        if all_dependencies is not None:    
            for d in all_dependencies:
                error = False
                if hasattr(self,d):
                    if getattr(self,d) is None:
                        error = True
                else:
                    error=True
                
                if error:
                    self.errors.append("Missing %s a dependency of %s" % (d, name))
                    valid = False
        
        return valid

    def validCompleteHours(self, schedule_name,expected_counts):
        # check that each array in a schedule contains the correct number of entries
        # return Boolean if any errors found
       
        if hasattr(self,schedule_name):
            valid = True
            schedule = getattr(self,schedule_name)
            
            def recursive_search(item,level=0, entry=0):
                if type(item) == list:
                    if len(item) != expected_counts[level]:
                        msg = 'Entry {} {}{} does not contain {} entries'.format(entry,'in sublevel ' + str(level)+ ' ' if level>0 else '', schedule_name, expected_counts[level])
                        self.errors.append(msg)
                        valid = False 
                    for ii,subitem in enumerate(item):
                        recursive_search(subitem,level=level+1, entry=ii)
            recursive_search(schedule)
        return valid 
    
    def validRate(self, rate):
        # check that each  tier in rate structure array has a rate attribute, and that all rates except one contain a 'max' attribute
        # return Boolean if any errors found
        if hasattr(self,rate):
            valid = True
            
            for i, r in enumerate(getattr(self, rate)):
                if len(r) == 0:
                    self.errors.append('Missing rate information for rate ' + str(i) + ' in ' + rate)
                    valid = False
                num_max_tags = 0
                for ii, t in enumerate(r):
                    if t.get('max') is not None:
                        num_max_tags +=1
                    if t.get('rate') is None and t.get('sell') is None and t.get('adj') is None:
                        self.errors.append('Missing rate/sell/adj attributes for tier ' + str(ii) + " in rate " + str(i) + ' ' + rate)
                        valid = False
                if len(r) > 1:
                    num_missing_max_tags = len(r) - 1 - num_max_tags
                    if num_missing_max_tags > 0:
                        self.errors.append("Missing 'max' tag for {} tiers in rate {} for {}".format( num_missing_max_tags, i, rate ))
                        valid = False
            return valid
        return False

    def validSchedule(self, schedules, rate):
        # check that each rate an a schedule array has a valid set of tiered rates in the associated rate struture attribute
        # return Boolean if any errors found
        if hasattr(self,schedules):
            valid = True
            s = getattr(self, schedules)
            if isinstance(s[0],list):
                s = np.concatenate(s)

            periods = list(set(s))

            # Loop though all periond and catch error if if exists
            if hasattr(self,rate):
                for period in periods:
                    if period > len(getattr(self, rate)) - 1 or period < 0:
                        self.errors.append(
                            '%s contains value %s which has no associated rate in %s' % (schedules, period, rate))
                        valid = False
                return valid
            else:
                self.warnings.append('{} does not exist to check {}'.format(rate,schedules))
        return False


class ValidateNestedInput:
        # ASSUMPTIONS:
        # User only has to specify each attribute once
        # User at minimum only needs to pass in required information, failing to input in a required attribute renders the whole input invalid
        # User can assume default values exist for all non-required attributes
        # User can assume null or unspecified attributes will be converted to defaults
        # User needs to manually overwrite defaults (with zero's) to negate their effect (pass in a federal itc of 0% to model without federal itc)

        # Wind turned off by default, PV and Battery created by default

        # LOGIC
        #   To easily map dictionaries into objects and maintain relationships between objects:

        #   if a key starts with a capital letter:
        #       the singular form of the key name must match exactly the name of a src object
        #       the key maps to a dictionary which will be used as a **kwargs input (along with any other necessary previously created objects) to the key"s object creation function
        #       if the key is not present in the JSON input or it is set to null, the API will create the object(s) with default values, unless required attributes are needed

        #       if the key does not end in "s" and the value is not null:
        #           all keys in the value dictionary that start in lower case are attributes of that object
        #               if an attribute is not required and not defined in the dictionary or defined as null, default values will be used later in the code for these values
        #               if an attribtue is required and not defined or defined as null, the entire input is invalid

        #       if the key does not end in "s" and the value is null:
        #           the object will be created with default values (barring required attributes)

        #       if the key ends in "s" and is not null:
        #           the value is a list of objects to be created of that singular key type or null
        #           if the key is not present in the JSON input or if the list is empty or null, the API will create any default objects that REopt needs

        #   if a key starts with a lowercase letter:
        #       it is an attribute of an object
        #       it's name ends in the units of that attibute
        #       if it is a boolean - name is camelCase starting with can
        #       if it ends in _pct - values must be between -1 and 1 inclusive
        #       abbreviations in the name are avoided (exceptions include common units/terms like pct, soc...)
        #       if it is a required attribute and the value is null or the key value pair does not exist, the entire input is invalid
        #       if it is not a required attribute and the value is null or the key does not exist, default values will be used


        # EXAMPLE 1 - BASIC POST


        # {
        #     "Scenario": {
        #         "Site": {
        #             "latitude": 40, "longitude": -123, "LoadProfile": {"building_type": "hospital", "load_size": 10000},
        #             "Utility": {"urdb_rate_json": {}}
        #             }
        #         },
        #     }
        #
        # # EXAMPLE 2 - BASIC POST - PV ONLY
        # {
        #     "Scenario": {
        #         "Site": {
        #             "latitude": 40, "longitude": -123, "LoadProfile": {"building_type": "hospital", "load_size": 10000},
        #             "Utility": {"urdb_rate_json": {}}, "Storage":{'max_kw':0}
        #             }
        #         }
        #     }
        #
        # # EXAMPLE 3 - BASIC POST - NO FED ITC FOR PV, run battery and pv, no wind
        # {
        #     "Scenario": {
        #         "Site": {
        #             "latitude": 40, "longitude": -123, "LoadProfile": {"building_type": "hospital", "load_size": 10000},
        #             "Utility": {"urdb_rate_json": {}}, "PV": {"itc_federal_us_dollars_per_kw": 0}}
        #             }
        #         }
        #     }

        def __init__(self, input_dict):

            self.nested_input_definitions = nested_input_definitions

            self.input_data_errors = []
            self.urdb_errors = []
            self.input_as_none = []
            self.invalid_inputs = []

            self.defaults_inserted = []

            self.input_dict = dict()
            self.input_dict['Scenario'] = input_dict.get('Scenario') or {}

            for k,v in input_dict.items():
                if k != 'Scenario':
                    self.invalid_inputs.append([k, ["Top Level"]])

            self.recursively_check_input_by_objectnames_and_values(self.nested_input_definitions, self.remove_invalid_keys)
            self.recursively_check_input_by_objectnames_and_values(self.input_dict, self.remove_nones)
            self.recursively_check_input_by_objectnames_and_values(self.nested_input_definitions, self.convert_data_types)
            self.recursively_check_input_by_objectnames_and_values(self.nested_input_definitions, self.fillin_defaults)
            self.recursively_check_input_by_objectnames_and_values(self.nested_input_definitions, self.check_special_data_types)
            self.recursively_check_input_by_objectnames_and_values(self.nested_input_definitions, self.check_min_max_restrictions)
            self.recursively_check_input_by_objectnames_and_values(self.nested_input_definitions, self.check_required_attributes)

        @property
        def isValid(self):
            if self.input_data_errors or self.urdb_errors:
                return False

            return True

        @property
        def messages(self):
            output = {}
           
            if self.errors != {}:
                output = self.errors

            if self.warnings != {}:
                output['warnings'] = self.warnings

            return output

        def warning_message(self, warnings):
            """
                   Convert a list of lists into a dictionary
                   :param warnings: list - item 1 argument, item 2 location
                   :return: message - 'Scenario>Site: latitude and longitude'
            """
            output = {}
            for arg, path in warnings:
                if 'wind' not in arg.lower():
                    if 'wind' not in [p.lower() for p in path]:
                        path = ">".join(path)
                        if path not in output:
                            output[path] = arg
                        else:
                            output[path] += ' AND ' + arg

            return output

        @property
        def errors(self):
            output = {}

            if self.input_data_errors:
                output["error"] = "Invalid inputs. See 'input_errors'."
                output["input_errors"] = self.input_data_errors

            if self.urdb_errors and self.input_data_errors:
                output["input_errors"] += self.urdb_errors
            
            elif self.urdb_errors:
                output["error"]= "Invalid inputs. See 'input_errors'."
                output["input_errors"] = self.urdb_errors

            return output

        @property 
        def warnings(self):
            output = {}

            if bool(self.defaults_inserted):
                output["Default values used for the following:"] = self.warning_message(self.defaults_inserted)

            if bool(self.invalid_inputs):
                output["Following inputs are invalid:"] = self.warning_message(self.invalid_inputs)

            return output

        def isSingularKey(self, k):
            return k[0] == k[0].upper() and k[-1] != 's'

        def isPluralKey(self, k):
            return k[0] == k[0].upper() and k[-1] == 's'

        def isAttribute(self, k):
            return k[0] == k[0].lower()

        def recursively_check_input_by_objectnames_and_values(self, nested_template, comparison_function,
                                                              nested_dictionary_to_check=None, object_name_path=[]):
            # nested template is the nested dictionary that is read to get the order in which objects are nested in each other
            # nested_dictionary_to_check contains the values for those objects,
            # think of it as scrolling through the template to get the name of the object and values you're looking for and
            # then checking the corresponding value in the nested_dictionary_to_check
            # the key_value_function tells the algorithm what to do when you have the object name (PV) and the user supplied values ('max_kw':0)
            # nested_dictionary_to_check can be updated based on the key value function

            if nested_dictionary_to_check is None:
                nested_dictionary_to_check = self.input_dict

            for template_k, template_values in nested_template.items():

                real_values = nested_dictionary_to_check.get(template_k)

                if self.isSingularKey(template_k):

                    comparison_function(object_name_path=object_name_path + [template_k],
                                        template_values=template_values, real_values=real_values)
                    
                    self.recursively_check_input_by_objectnames_and_values(nested_template[template_k],
                                                                           comparison_function, real_values or {},
                                                                           object_name_path=object_name_path + [
                                                                               template_k])

        def update_attribute_value(self, object_name_path, attribute, value):

            dictionary = self.input_dict

            for name in object_name_path:
                dictionary = dictionary[name]

            dictionary[attribute] = value

        def delete_attribute(self, object_name_path, key):

            dictionary = self.input_dict

            for name in object_name_path:
                dictionary = dictionary[name]

            if key in dictionary.keys():
                del dictionary[key]

        def object_name_string(self, object_name_path):
            return '>'.join(object_name_path)

        def test_data(self, definition_attribute):
            test_data_list = []

            if definition_attribute == 'min':
                def swap_logic(object_name_path, name, definition, current_value):
                    attribute_min = definition.get('min')
                    if attribute_min is not None:
                        new_value = attribute_min - 1
                        self.update_attribute_value(object_name_path, name, new_value)
                        test_data_list.append([name, copy.deepcopy(self.input_dict)])
                        self.update_attribute_value(object_name_path, name, current_value)

            if definition_attribute == 'max':
                def swap_logic(object_name_path, name, definition, current_value):
                    attribute_max = definition.get('max')
                    if attribute_max is not None:
                        new_value = attribute_max + 1
                        self.update_attribute_value(object_name_path, name, new_value)
                        test_data_list.append([name, copy.deepcopy(self.input_dict)])
                        self.update_attribute_value(object_name_path, name, current_value)

            if definition_attribute == 'restrict_to':
                def swap_logic(object_name_path, name, definition, current_value):
                    attribute = definition.get('restrict_to')
                    if attribute is not None:
                        new_value = "OOPS"
                        self.update_attribute_value(object_name_path, name, new_value)
                        test_data_list.append([name, copy.deepcopy(self.input_dict)])
                        self.update_attribute_value(object_name_path, name, current_value)

            if definition_attribute == 'type':
                def swap_logic(object_name_path, name, definition, current_value):
                    attribute_type = eval(definition['type'])
                    value = attribute_type(current_value)
                    if isinstance(value, float) or isinstance(value, int) or isinstance(value, dict) or isinstance(
                            value, bool):
                        new_value = "OOPS"
                        self.update_attribute_value(object_name_path, name, new_value)
                        test_data_list.append([name, copy.deepcopy(self.input_dict)])
                        self.update_attribute_value(object_name_path, name, value)

            def add_invalid_data(object_name_path, template_values=None, real_values=None):
                if real_values is not None:
                    for name, value in template_values.items():
                        if self.isAttribute(name):
                            swap_logic(object_name_path, name, value, real_values.get(name))

            self.recursively_check_input_by_objectnames_and_values(self.nested_input_definitions, add_invalid_data)

            # test_data_list is a list of lists, with each sub list a pair of [str, dict],
            # where the str is an input param, dict is an entire post with a bad value for that input param
            return test_data_list


#Following functions go into recursively_check_input_by_objectnames_and_values on instantiation and validation to check an object name and set of values
#    object_name_path is the location of the object name as in ["Scenario", "Site"]
#    template_values is the reference dictionary for checking as in {'latitude':{'type':'float',...}...} from the nested dictionary
#    real_values are the values from the input to check and/or modify  like {'latitude':39.345678,...}

        def remove_nones(self, object_name_path, template_values=None, real_values=None):
            if real_values is not None:
                for name, value in real_values.items():
                    if self.isAttribute(name):
                        if value is None:
                            self.delete_attribute(object_name_path, name)
                            self.input_as_none.append([name, object_name_path[-1]])

        def remove_invalid_keys(self, object_name_path, template_values=None, real_values=None):
            if real_values is not None:
                for name, value in real_values.items():
                    if self.isAttribute(name):
                        if name not in template_values.keys():
                            self.delete_attribute(object_name_path, name)
                            self.invalid_inputs.append([name, object_name_path])
        
        def check_min_max_restrictions(self, object_name_path, template_values=None, real_values=None):
            if real_values is not None:
                for name, value in real_values.items():
                    if self.isAttribute(name):

                        data_validators = template_values[name]

                        try:
                            value == eval(data_validators['type'])(value)

                            if data_validators.get('min') is not None:
                                if value < data_validators['min']:
                                    self.input_data_errors.append('%s value (%s) in %s exceeds allowable min %s' % (
                                    name, value, self.object_name_string(object_name_path), data_validators['min']))

                            if data_validators.get('max') is not None:
                                if value > data_validators['max']:
                                    self.input_data_errors.append('%s value (%s) in %s exceeds allowable max %s' % (
                                    name, value, self.object_name_string(object_name_path), data_validators['max']))

                        except:
                            self.input_data_errors.append('Could not check min/max on %s (%s) in %s' % (
                            name, value, self.object_name_string(object_name_path)))

                        if data_validators.get('restrict_to') is not None:
                            if value not in data_validators['restrict_to']:
                                self.input_data_errors.append('%s value (%s) in %s not in allowable inputs - %s' % (
                                name, value, self.object_name_string(object_name_path), data_validators['restrict_to']))

        def check_special_data_types(self, object_name_path, template_values=None, real_values=None):
            """
            Validate special data types.
            :param object_name_path: list of strings, eg. ["Scenario", "Site", "Wind"]
            :param template_values: not used in this function, placeholder for usage in
                self.recursively_check_input_by_objectnames_and_values
            :param real_values: dict, posted values starting at the end of the object_name_path with defaults filled in
            :return: None
            """
            if real_values is not None:

                urdb_response = real_values.get('urdb_response')
                if urdb_response is not None:
                    
                    if real_values.get('urdb_utility_name') is None:
                        self.update_attribute_value(object_name_path, 'urdb_utility_name', urdb_response.get('utility'))
                    
                    if real_values.get('urdb_rate_name') is None:
                        self.update_attribute_value(object_name_path, 'urdb_rate_name', urdb_response.get('name'))
                    
                    try:
                        rate_checker = URDB_RateValidator(**urdb_response)
                        if rate_checker.errors:
                            self.urdb_errors += rate_checker.errors
                    except:
                        self.urdb_errors += 'Error parsing urdb rate in %s ' % (object_name_path)

                load_profile = real_values.get('loads_kw')
                if load_profile not in [None, []]:
                    n = len(load_profile)

                    if n == 8760:
                        pass

                    elif n == 17520:  # downsample 30 minute data
                        index = pd.date_range('1/1/2000', periods=n, freq='30T')
                        series = pd.Series(load_profile, index=index)
                        series = series.resample('1H').mean()
                        self.update_attribute_value(object_name_path, 'loads_kw', series.tolist())

                    elif n == 35040:  # downsample 15 minute data
                        index = pd.date_range('1/1/2000', periods=n, freq='15T')
                        series = pd.Series(load_profile, index=index)
                        series = series.resample('1H').mean()
                        self.update_attribute_value(object_name_path, 'loads_kw', series.tolist())

                    else:
                        self.input_data_errors.append("Invalid length for loads_kw. Load profile must be hourly (8,760 samples), 30 minute (17,520 samples), or 15 minute (35,040 samples)")

                critical_load_profile = real_values.get('critical_loads_kw')
                if critical_load_profile not in [None, []]:
                    n = len(critical_load_profile)

                    if n == 8760:
                        pass

                    elif n == 17520:  # downsample 30 minute data
                        index = pd.date_range('1/1/2000', periods=n, freq='30T')
                        series = pd.Series(critical_load_profile, index=index)
                        series = series.resample('1H').mean()
                        self.update_attribute_value(object_name_path, 'critical_loads_kw', series.tolist())

                    elif n == 35040:  # downsample 15 minute data
                        index = pd.date_range('1/1/2000', periods=n, freq='15T')
                        series = pd.Series(critical_load_profile, index=index)
                        series = series.resample('1H').mean()
                        self.update_attribute_value(object_name_path, 'critical_loads_kw', series.tolist())

                    else:
                        self.input_data_errors.append("Invalid length for critical_loads_kw. Critical load profile must be hourly (8,760 samples), 30 minute (17,520 samples), or 15 minute (35,040 samples)")

                if object_name_path[-1] == 'Wind':

                    if real_values.get("resource_meters_per_sec") is None \
                            and self.input_dict['Scenario']['Site']['Wind']['max_kw'] > 0:
                        """
                        Validate that provided lat/lon lies within the wind toolkit data set. 
                        If the location is not within the dataset, then return input_data_error.
                        If the location is within the dataset, add the resource_meters_per_sec to the Wind inputs so 
                        that we only query the database once.
                        """
                        from reo.src.wind_resource import get_wind_resource
                        from reo.src.techs import Wind

                        try:
                            wind_meters_per_sec = get_wind_resource(
                                latitude=self.input_dict['Scenario']['Site']['latitude'],
                                longitude=self.input_dict['Scenario']['Site']['longitude'],
                                hub_height_meters=Wind.size_class_to_hub_height[self.input_dict['Scenario']['Site']['Wind']['size_class']],
                                time_steps_per_hour=self.input_dict['Scenario']['time_steps_per_hour']
                            )
                            self.update_attribute_value(object_name_path, 'resource_meters_per_sec', wind_meters_per_sec)

                        except ValueError:
                            self.input_data_errors.append("Latitude/longitude is outside of wind resource dataset bounds. Please provide Wind.resource_meters_per_sec")

        def convert_data_types(self, object_name_path, template_values=None, real_values=None):
            if real_values is not None:
                for name, value in real_values.items():
                    if self.isAttribute(name):
                        try:
                            data_validators = template_values[name]
                            attribute_type = eval(data_validators['type'])
                            new_value = attribute_type(value)
                            if not isinstance(new_value, bool):
                                self.update_attribute_value(object_name_path, name, new_value)
                            else:
                                if value not in [True, False, 1, 0]:
                                    self.input_data_errors.append('Could not convert %s (%s) in %s to %s' % (
                                    name, value, self.object_name_string(object_name_path),
                                    str(attribute_type).split(' ')[1]))

                        except:
                            
                            self.input_data_errors.append('Could not convert %s (%s) in %s to %s' % (
                            name, value, self.object_name_string(object_name_path), str(attribute_type).split(' ')[1]))

        def fillin_defaults(self, object_name_path, template_values=None, real_values=None):
            
            if real_values is None:
                real_values = {}
                self.update_attribute_value(object_name_path[:-1], object_name_path[-1], real_values)

            for template_key, template_value in template_values.items():
                if self.isAttribute(template_key):
                    default = template_value.get('default')
                    if default is not None and real_values.get(template_key) is None:
                        if isinstance(default, str):  # special case for PV.tilt.default = "Site latitude"
                            if " " in default:
                                d = self.input_dict['Scenario']
                                for key in default.split(' '):
                                    d = d.get(key)
                                default = d
                        self.update_attribute_value(object_name_path, template_key, default)
                        self.defaults_inserted.append([template_key, object_name_path])

                if self.isSingularKey(template_key):
                    if template_key not in real_values.keys():
                        self.update_attribute_value(object_name_path, template_key, {})
                        self.defaults_inserted.append([template_key, object_name_path])

        def check_required_attributes(self, object_name_path, template_values=None, real_values=None):
           
            final_message = ''

            # conditional check for complex cases where replacements are available for attributes and there are dependent attributes (annual_kwh and doe_reference_building_name)
            all_missing_attribute_sets = []
            
            for key,value in template_values.items():
                
                if self.isAttribute(key):

                    missing_attribute_sets = []
                    replacements = value.get('replacement_sets')
                    depends_on = value.get('depends_on') or []

                    if replacements is not None:
                        current_set = [key] + depends_on
                        
                        if list(set(current_set)-set(real_values.keys())) != []:
                            for replace in replacements:
                                missing = list(set(replace)-set(real_values.keys()))
                                
                                if missing == []:
                                    missing_attribute_sets = []
                                    break
                                
                                else:
                                    replace = sorted(replace)
                                    if replace not in missing_attribute_sets:
                                        missing_attribute_sets.append(replace)
                        
                    else:
                        if real_values.get(key) is not None:
                            missing = []
                            for dependent_key in depends_on:
                                if real_values.get(dependent_key) is None:
                                    missing.append(dependent_key)
                            
                            if missing !=[]:
                                missing_attribute_sets.append(missing)

                    if len(missing_attribute_sets) > 0:
                        missing_attribute_sets = sorted(missing_attribute_sets)
                        message =  '(' + ' OR '.join([' and '.join(missing_set) for missing_set in missing_attribute_sets]) + ')'
                        if message not in all_missing_attribute_sets:
                            all_missing_attribute_sets.append(message)

            if len(all_missing_attribute_sets) > 0:
                final_message = " AND ".join(all_missing_attribute_sets)

            # check simple required attributes
            missing = []
            for template_key, template_value in template_values.items():
                if self.isAttribute(template_key):
                    if template_value.get('required') == True:
                        if real_values.get(template_key) is None:
                            missing.append(template_key)

            if len(missing) > 0:
                message = ' and '.join(missing)
                if final_message != '':
                    final_message += ' and ' + message
                else:
                    final_message = message

            if final_message != '':
                self.input_data_errors.append('Missing Required for %s: %s' % (self.object_name_string(object_name_path), final_message))
