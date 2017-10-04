from tastypie.validation import Validation
import numpy as np
from api_definitions import inputs
from log_levels import log
from urdb_logger import log_urdb_errors
from nested_inputs import nested_inputs
import copy

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
                if type(item)==list:
                    if len(item)!=expected_counts[level]:
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
                if len(r)==0:
                    self.errors.append('Missing rate information for rate ' + str(i) + ' in ' + rate)
                    valid = False
                num_max_tags = 0
                for ii, t in enumerate(r):
                    if t.get('max') is not None:
                        num_max_tags +=1
                    if t.get('rate') is None and t.get('sell') is None and t.get('adj') is None:
                        self.errors.append('Missing rate/sell/adj attributes for tier ' + str(ii) + " in rate " + str(i) + ' ' + rate)
                        valid = False
                if len(r)>1:
                    num_missing_max_tags = len(r)- 1 - num_max_tags
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
                    if period > len(getattr(self,rate)) - 1 or period < 0:
                        self.errors.append(
                            '%s contains value %s which has no associated rate in %s' % (schedules, period, rate))
                        valid = False
                return valid
            else:
                self.warnings.append('{} does not exist to check {}'.format(rate,schedules))
        return False


class REoptResourceValidation(Validation):

    def check_individual(self, input_dictionary, errors):

        for key, value in input_dictionary.items():

            if key not in inputs(full_list=True):
                errors = self.append_errors(errors, key, ['This key name does not match a valid web input.'])
                logstring = "Key: '" + str(key) + "' does not match a valid input!"
                log("ERROR", logstring)
               # raise BadRequest(logstring)

            if value is None and key in inputs(just_required=True).keys():
                if inputs()[key].get('swap_for') is None:
                    errors = self.append_errors(errors, key, ['This input is required and cannot be null.'])
                    logstring = "Value for key: " + str(key) + " is required and cannot be null!"
                    log("ERROR", logstring)
                #    raise BadRequest(logstring)

            else:
                field_def = inputs(full_list=True).get(key)
                if field_def is not None:
                    format_errors = self.check_input_format(key,value,field_def)
                    if not format_errors:
                        if 'max' in field_def and field_def['max'] is not None:
                            max_value = field_def['max']
                            # handle case that one input depends upon another
                            if type(field_def['max']) == str and field_def['max'] in input_dictionary:
                                field_def_depend = inputs(full_list=True)[field_def['max']]
                                max_value = field_def_depend['default']
                                if input_dictionary[field_def['max']] is not None:
                                    max_value = input_dictionary[field_def['max']]

                            format_errors += self.check_max(key, value, field_def, max_value)

                        if 'min' in field_def and field_def['min'] is not None:
                            format_errors += self.check_min(key, value, field_def)

                        if 'restrict_to' in field_def and field_def['restrict_to'] is not None:
                            format_errors += self.check_restrict_to(key, value, field_def['restrict_to'])

                        if 'length' in field_def and field_def['length'] is not None:
                            format_errors += self.check_length(key, value, field_def['length'])

                    # specific_errors
                    if format_errors:
                        errors = self.append_errors(errors, key, format_errors)
                        # raise BadRequest(format_errors)
        return errors

    def is_valid(self, bundle, request=None):

        errors = {}

        rate_data = bundle.data.get('urdb_rate')
        if rate_data is not None and type(rate_data).__name__=='dict':
                rate_checker = URDB_RateValidator(**rate_data)
                if rate_checker.errors:
                    errors = self.append_errors(errors,"URDB Rate Errors",rate_checker.errors)

        missing_required = self.missing_required(bundle.data.keys())

        if missing_required:
            message = list(set([self.get_missing_required_message(m) for  m in missing_required]))
            errors = self.append_errors(errors,"Missing_Required",message)

        remaining_keys = list( set(inputs(full_list=True)) - set(inputs(just_required=True)) )
        missing_dependencies = self.missing_dependencies(remaining_keys)

        if missing_dependencies:
            message = [self.get_missing_dependency_message(m) for m in missing_dependencies]
            errors = self.append_errors(errors, "Missing_Dependencies", message)

        errors = self.check_individual(bundle.data, errors)

        return errors

    def check_input_format(self,key,value,field_definition):

        invalid_msg = 'Invalid format: Expected %s, got %s'\
                      % (field_definition['type'].__name__, type(value).__name__)
        
        try:
            
            new_value = field_definition['type'](value)
            
            if value not in [new_value]:
                return [invalid_msg]

            return []

        except Exception as e:
            if value is None:
                return []
            return [invalid_msg]

    def check_min(self, key, value, fd):
        new_value = value
        if fd.get('pct') is True:
            if value > 1:
                new_value = value*0.01

        if new_value < fd['min'] and value is not None:
            if not fd.get('pct'):
                return ['Invalid value: %s: %s is less than the minimum, %s' % (key, value, fd['min'])]
            else:
                return ['Invalid value: %s: %s is less than the minimum, %s %%' % (key, value, fd['min'] * 100)]
        return []

    def check_max(self, key, value, fd, max_value):
        new_value = value
        if fd.get('pct') is True:
            if value > 1:
                new_value = value * 0.01

        if new_value > fd['max'] and value is not None:
            if not fd.get('pct'):
                return ['Invalid value: %s: %s is greater than the  maximum, %s' % (key, value, fd['max'])]
            else:
                return ['Invalid value: %s: %s is greater than the  maximum, %s %%' % (key, value, fd['max']*100)]
        return []

    def check_restrict_to(self, key, value, range):
        if value not in range and value is not None:
            return ['Invalid value: %s: %s is not in %s' % (key, value, range)]
        return []

    def append_errors(self, errors, key, value):
        if 'Error' in errors.keys():
            if key not in errors["Error"].keys():
                errors["Error"][key] = value
            else:
                errors["Error"][key] += value
        else:
            errors['Error']  =  {key: value}
        return errors

    def get_missing_required_message(self, input):
        definition_values = inputs(full_list=True)
        depends = definition_values[input].get('depends_on')
 
        if depends is not None:
            fields = sorted([input] + depends)
            input = fields[0]
            depends = fields[1:]

        swap = definition_values[input].get('swap_for')
        alt_field = definition_values[input].get('alt_field')

        message = "(" + input
       
        if alt_field is not None:
            message += " (or %s)" % (alt_field)
      
        if depends is not None:
            message += ' and ' + ",".join(depends) + ")"
 
        if swap is not None:
            message += " OR (%s)" % ( " and ".join(swap)  )
                	
        return message

    def get_missing_dependency_message(self, input):
        definition_values = inputs(full_list=True)[input]

        dependency_of = []
        for k, v in inputs(full_list=True).items():
            value = v.get('depends_on')
            if value is not None:
                if input in value:
                    dependency_of.append(k)
        return "%s (%s depend(s) on this input.)" % (input, "  and ".join(dependency_of))

    def missing_dependencies(self, key_list, exclude=[]):
        # Check if field depends on non-required fields
        missing = []
        for k in key_list:  # all possible inputs
            if k not in exclude:
                d = inputs(full_list=True)[k].get('depends_on')
                if d is not None:
                    if set(d) & set(key_list) != set(d) and d not in missing:
                        missing+=d        
            return missing

    def swaps_exists(self, key_list, f):
        swap = inputs(full_list=True)[f].get('swap_for')
        swap_exists = False

        if swap is not None and any(s in key_list for s in swap):
            swap_exists = True
        return swap_exists

    def missing_required(self,key_list):
        required = inputs(just_required=True)
        used_swaps = []
        output = []
        
        for field in required.keys():
            check_swaps = False
            if field not in used_swaps: 
                if field in key_list:
                    dependent = required[field].get('depends_on')
                    if dependent is not None:
                        for d in dependent:
                            if d not in key_list:
                                alt = inputs(full_list=True)[d].get('alt_field')
                                if alt is not None: 
                                   if alt not in key_list: 
                                        check_swaps=True      
                                else:
                                    check_swaps=True
                else:
                    check_swaps=True

                if check_swaps:
                    swap = required[field].get('swap_for')
                    if swap is not None:
                        for s in swap:
                            if s not in key_list:
                                output.append(field)
                                used_swaps += swap
                                break
                    else:
                        output.append(field)
        return set(output)

    def check_length(self, key, value, correct_length):
        if len(value) != correct_length:
            return ['Invalid number of values for %s: entered %s values, %s required' % (key, len(value), correct_length)]
        return []


class ValidateNestedInput():
        # ASSUMPTIONS:
        # User only has to specify each attribute once
        # User at minimum only needs to pass in required information, failing to input in a required attribute renders the whole input invalid
        # User can assume default values exist for all non-required attributes
        # User can assume null or unspecified attributes will be converted to defaults
        # User needs to manually overwrite defaults (with zero's) to negate their effect (pass in a federal itc of 0% to model without federal itc)

        # PV and Battery are only created if they are defined in the _tech_set attribute


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

        #           all keys in the value dictionary that start in upper case recursivley follow this logic

        #       if the key does not end in "s" and the value is null:
        #           the object will be created with default values (barring required attributes)

        #       if the key ends in "s" and is not null:
        #           the value is a list of objects to be created of that singular key type or null
        #           if the key is not present in the JSON input or if the list is empty or null, the API will create any default objects that REopt needs

        #   if a key starts with a lowercase letter:
        #       it is an attribute of an object
        #       it's name ends in the units of that attibute
        #       if it is a list - _list is in the name
        #       if it is a json to be parsed into a dictionary - _json is in the name
        #       if it is a boolean - name is camelCase starting with can
        #       if it ends in _pct or _rate - values must be between -1 and 1 inclusive
        #       abbreviations in the name are avoided (exceptions include common units/terms like pct, soc...)
        #       if it is a required attribute and the value is null or the key value pair does not exist, the entire input is invalid
        #       if it is not a required attribute and the value is null or the key does not exist, default values will be used

        #   if a key starts with an underscore:
        #       it it a placeholder, does not create a object and is not an attribute
        #
        #       if it ends in 's' it maps to a list of dictionaries, each only having keys that are objects to create, otherwise it maps to single dictionary with all keys being objects to create


        # EXAMPLE 1 - BASIC POST


        # {
        #     "Scenario": {
        #         "Site": {
        #             "latitude": 40, "longitude": -123, "LoadProfile": {"building_type": "hospital", "load_size": 10000},
        #             "Utility": {"urdb_rate_json": {}}
        #             }
        #         }, "_tech_set": {}
        #     }
        #
        # # EXAMPLE 2 - BASIC POST - PV ONLY
        # {
        #     "Scenario": {
        #         "Site": {
        #             "latitude": 40, "longitude": -123, "LoadProfile": {"building_type": "hospital", "load_size": 10000},
        #             "Utility": {"urdb_rate_json": {}}, "_tech_set": {"PV": {}}
        #             }
        #         }
        #     }
        #
        # # EXAMPLE 3 - BASIC POST - NO FED ITC FOR PV
        # {
        #     "Scenario": {
        #         "Site": {
        #             "latitude": 40, "longitude": -123, "LoadProfile": {"building_type": "hospital", "load_size": 10000},
        #             "Utility": {"urdb_rate_json": {}},
        #             "_tech_set": {"PV": {"InvestmentIncentive": {"value_max_us_dollar_per_kw": 0}}, "Battery": {}}
        #             }
        #         }
        #     }


    def __init__(self, input, nested=False):
        self.web_inputs = nested_inputs
        self.input = input

        if not nested:
            self.input = self.to_nested_format()

        self.input_data_errors = []
        self.urdb_errors = []
        self.input_as_none = []
        self.input_not_allowed = []

        self.recursively_check_objectnames_and_values(self.input, self.input, self.remove_invalid_keys)
        self.recursively_check_objectnames_and_values(self.input, self.input, self.remove_nones)
        self.recursively_check_objectnames_and_values(self.input, self.input, self.convert_data_types)
        self.recursively_check_objectnames_and_values(self.template, self.input, self.fillin_default_objects)

    @property
    def isValid(self):

        self.recursively_check_objectnames_and_values(self.template, self.input, self.check_special_data_types)
        self.recursively_check_objectnames_and_values(self.template, self.input, self.check_min_max_restrictions)
        self.recursively_check_objectnames_and_values(self.template, self.input, self.check_required_attributes)
        if self.input_data_errors or self.urdb_errors:
            return False

        return True

    @property
    def error_response(self):
        return {"Input Errors":self.errors, "Warnings":self.warnings}

    def warning_message(self, warnings):
        output = {}
        for a,b in warnings:
            if b not in output:
                output[b] = [a]
            else:
                output[b].append(a)
        return output

    @property
    def errors(self):
        output = {}

        if self.urdb_errors:
            output["URDB Errors"] = self.urdb_errors

        if self.input_data_errors:
            output["Data Validation Errors"] = self.input_data_errors

        return output

    @property
    def warnings(self):
        return { "Defaults will be used for": self.warning_message(self.input_as_none), 'Following Inputs Are Not Allowed':self.warning_message(self.input_not_allowed) }

    @property
    def template(self):
        return {"Scenario":
                    {"Site":{
                            "ElectricTariff":{},
                            "LoadProfile":{},
                            "Financial":{},
                            "_tech_set":{

                                "PV":{
                                    "PVWatt":{},
                                    },

                                "Storage":{
                                    }
                                }
                            }
                        }
                    }

    def isPlaceholderKey(self,k):
        if k[0]=='_':
            return True
        return False

    def isSingularKey(self,k):
        if self.isPlaceholderKey(k):
            return False
        return k[0] == k[0].upper() and k[-1]!='s'

    def isPluralKey(self,k):
        if self.isPlaceholderKey(k):
            return False
        return k[0] == k[0].upper() and k[-1]=='s'

    def isAttribute(self,k):
        if self.isPlaceholderKey(k):
            return False
        return k[0] == k[0].lower()

    def recursively_check_objectnames_and_values(self, object_name_source_dict, values_source_dict, key_value_function, location=[]):

        try:
            for template_k, template_values in object_name_source_dict.items():

                real_values = values_source_dict.get(template_k)

                if self.isPluralKey(template_k):
                    singular_k = template_k[:-1]
                    for i, item in enumerate(real_values):
                        new_location = copy.copy(location)
                        new_location.append([template_k,i])
                        key_value_function(singular_k, item, location = new_location)
                        self.recursively_check_objectnames_and_values(object_name_source_dict[template_k][0], item, key_value_function,  location = new_location )

                elif self.isSingularKey(template_k):
                    new_location = copy.copy(location)
                    new_location.append([template_k,None])
                    key_value_function(template_k, real_values,  location = new_location )
                    self.recursively_check_objectnames_and_values(object_name_source_dict[template_k], real_values or {}, key_value_function, location = new_location)

                elif self.isPlaceholderKey(template_k):
                    new_location = copy.copy(location)
                    new_location.append([template_k,None])
                    self.recursively_check_objectnames_and_values(object_name_source_dict[template_k], real_values or {}, key_value_function, location = new_location)
        except:
            self.input_data_errors.append('Input JSON does not match template %s' % (self.template))

    def update_attribute_value(self, location, attribute, value):

        dictionary = self.input

        for key_num_pair in location:
            dictionary = dictionary[key_num_pair[0]]
            if key_num_pair[1] is not None:
                dictionary = dictionary[key_num_pair[1]]

        dictionary[attribute] = value

    def delete_attribute(self, location, parent_key, key):
        dictionary = self.input

        for key_num_pair in location:
            dictionary = dictionary[key_num_pair[0]]

            if key_num_pair[1] is not None:
                dictionary=dictionary[key_num_pair[1]]

        if key in dictionary.keys():
            del dictionary[key]

    def location_string(self,location):
        return "/".join([i[0] if i[1] is None else "%s(%s)"%(i[0],i[1]) for i in location])

    def remove_nones(self, object_name, object_dictionary, location = []):
        if object_dictionary is not None:
            for attribute_name,attribute_value in object_dictionary.items():
                if self.isAttribute(attribute_name):
                    if attribute_value is None:
                        self.delete_attribute(location, object_name, attribute_name)
                        self.input_not_allowed.append([attribute_name,self.location_string(location)])


    def remove_invalid_keys(self, object_name, object_dictionary, location = []):
        if object_dictionary is not None:
            for attribute_name,attribute_value in object_dictionary.items():
                if self.isAttribute(attribute_name):
                    if attribute_name not in self.web_inputs[object_name].keys():
                        self.delete_attribute(location,object_name, attribute_name)
                        self.input_as_none.append([attribute_name,self.location_string(location)])

    def check_min_max_restrictions(self, object_name, object_dictionary, location = []):
        if object_dictionary is not None:
            for attribute_name,attribute_value in object_dictionary.items():
                if self.isAttribute(attribute_name):
                    try:
                        data_validators = self.web_inputs[object_name][attribute_name]

                        if data_validators.get('min') is not None:
                            if attribute_value < data_validators['min']:
                                self.input_data_errors.append('%s value (%s) in %s exceeds allowable min %s' % (attribute_name, attribute_value, self.location_string(location), data_validators['min']))

                        if data_validators.get('max') is not None:
                            if attribute_value > data_validators['max']:
                                self.input_data_errors.append('%s value (%s) in %s exceeds allowable max %s' % (attribute_name, attribute_value, self.location_string(location), data_validators['max']))

                        if data_validators.get('restrict_to') is not None:
                            if attribute_value not in data_validators['restrict_to']:
                                self.input_data_errors.append('%s value (%s) in %s not in allowable inputs - %s' % (attribute_name, attribute_value, self.location_string(location), data_validators['restrict_to']))

                    except:
                         self.input_data_errors.append('Could not check min/max/restrictions on %s (%s) in %s' % (attribute_name,attribute_value, self.location_string(location)))

    def check_special_data_types(self, object_name, object_dictionary, location = []):
        if object_dictionary is not None:
            for attribute_name,attribute_value in object_dictionary.items():
                if self.isAttribute(attribute_name):

                    if attribute_name == 'urdb_response' and attribute_value is not None:
                        try:
                            rate_checker = URDB_RateValidator(**attribute_value)
                            if rate_checker.errors:
                                self.urdb_errors.append(rate_checker.errors)
                        except:
                            self.urdb_errors.append('Error parsing urdb rate in %s ' % (self.location_string(location)))


    def convert_data_types(self, object_name, object_dictionary, location = []):
        if object_dictionary is not None:
            for attribute_name,attribute_value in object_dictionary.items():
                if self.isAttribute(attribute_name):
                    try:
                        data_validators = self.web_inputs[object_name][attribute_name]
                        attribute_type = data_validators['type']
                        new_value = attribute_type(attribute_value)
                        self.update_attribute_value(location,attribute_name, new_value)

                    except:
                        self.input_data_errors.append('Could not convert %s (%s) in %s to %s' % (attribute_name,attribute_value, self.location_string(location),str(attribute_type).split(' ')[1]))

    def fillin_default_objects(self, object_name, object_dictionary, location = []):

        if object_name in ['Scenario','Site','LoadProfile','ElectricTariff','Financial', 'PVWatt']:
            if object_dictionary is None:
                self.update_attribute_value(location[:-1], object_name, {})


    def check_required_attributes(self, object_name, object_dictionary, location = []):

            def check_options(options, keys):
                missing = [[]]
                input_set = [list(set(o) - set(keys)) for o in options]
                if [] not in input_set:
                    missing = []
                    for i, pair in enumerate(input_set):
                        if pair not in missing:
                            missing.append(pair)
                return missing

            object_dictionary = object_dictionary or {}
            keys = object_dictionary.keys()

            missing = [[]]

            if object_name == "Scenario":
                missing = [list(set(('Site',)) - set(keys))]

            if object_name == "Site":
                missing = [list(set(('latitude' , 'longitude' , "LoadProfile" , "ElectricTariff","_tech_set")) - set(keys))]

            if object_name ==  "LoadProfile":
                options =  [['doe_reference_name','annual_kwh'],['doe_reference_name','monthly_totals_kwh'],['loads_kw']]
                missing = check_options(options,keys)

            if object_name == "ElectricTariff":
                options = [["blended_monthly_rates_us_dollars_per_kwh", "monthly_demand_charges_us_dollars_per_kw"], ["urdb_response"]]
                missing = check_options(options, keys)


            if missing != [[]]:
                message = ' OR '.join([' and '.join(m) for m in missing if m])
                self.input_data_errors.append('Missing Required for %s%s: %s' % (object_name, ' in ' + self.location_string(location) if len(location)>1 else '', message) )

    def to_nested_format(self):
        i = self.input

        return {
            "Scenario": {

                "timeout_seconds": i.get("timeout"),
                "user_id": i.get("user_id"),
                "time_steps_per_hour": i.get("time_steps_per_hour"),

                "Site": {
                    "latitude": i.get("latitude"),
                    "longitude": i.get("longitude"),
                    "land_acres": i.get("land_area"),
                    "roof_squarefeet": i.get("roof_area"),
                    "outage_start_hour": i.get("outage_start"),
                    "outage_end_hour": i.get("outage_end"),
                    "critical_load_pct": i.get("crit_load_factor"),

                    "LoadProfile":
                        {
                            "doe_reference_name": i.get("load_profile_name"),
                            "annual_kwh": i.get("load_size"),
                            "year": i.get("load_year"),
                            "monthly_totals_kwh": i.get("load_monthly_kwh"),
                            "loads_kw": i.get("load_8760_kw"),
                        },

                    "Financial":
                        {
                            "om_cost_growth_pct": i.get("om_cost_growth_rate"),
                            "escalation_pct": i.get("rate_escalation"),
                            "owner_tax_pct": i.get("owner_tax_rate"),
                            "offtaker_tax_pct": i.get("offtaker_tax_rate"),
                            "owner_discount_pct": i.get("owner_discount_rate"),
                            "offtaker_discount_pct": i.get("offtaker_discount_rate"),
                            "analysis_period_years": i.get("analysis_period"),
                        },

                    "ElectricTariff":
                        {
                            "urdb_utilty_name": i.get("utility_name"),
                            "urdb_rate_name": i.get("rate_name"),
                            "urdb_response": i.get("urdb_rate"),
                            "blended_monthly_rates_us_dollars_per_kwh": i.get("blended_utility_rate"),
                            "monthly_demand_charges_us_dollars_per_kw": i.get("demand_charge"),
                            "net_metering_limit_kw": i.get("net_metering_limit"),
                            "wholesale_rate_us_dollars_per_kwh": i.get("wholesale_rate"),
                            "interconnection_limit_kw": i.get("interconnection_limit"),
                        },

                    "_tech_set": {
                            "PV":
                                {
                                    "min_kw": i.get("pv_kw_min"),
                                    "max_kw": i.get("pv_kw_max"),
                                    "installed_cost_us_dollars_per_kw": i.get("pv_cost"),
                                    "om_cost_us_dollars_per_kw": i.get("pv_om"),
                                    "degradation_pct": i.get("pv_degradation_rate"),

                                    "PVWatt":{
                                        "azimuth": i.get("azimuth"),
                                        "losses": i.get("losses"),
                                        "array_type": i.get("array_type"),
                                        "module_type": i.get("module_type"),
                                        "gcr": i.get("gcr"),
                                        "dc_ac_ratio": i.get("dc_ac_ratio"),
                                        "inv_eff": i.get("inv_eff"),
                                        "radius": i.get("radius"),
                                        "tilt": i.get("tilt"),
                                    },

                                    "macrs_option_years": i.get("pv_macrs_schedule"),
                                    "macrs_bonus_pct": i.get("pv_macrs_bonus_fraction"),
                                    "federal_itc_pct":i.get("pv_itc_federal"),
                                    "state_ibi_pct": i.get("pv_itc_state"),
                                    "state_ibi_max_us_dollars": i.get("pv_ibi_state_max"),
                                    "utility_ibi_pct": i.get("pv_ibi_utility"),
                                    "utility_ibi_max_us_dollars": i.get("pv_ibi_utility_max"),
                                    "federal_rebate_us_dollars_per_kw": i.get("pv_rebate_federal"),
                                    "state_rebate_us_dollars_per_kw": i.get("pv_rebate_state"),
                                    "state_rebate_max_us_dollars": i.get("pv_rebate_state_max"),
                                    "utility_rebate_us_dollars_per_kw": i.get("pv_rebate_utility"),
                                    "utility_rebate_max_us_dollars":i.get("pv_rebate_utility_max"),
                                    "pbi_us_dollars_per_kwh": i.get("pv_pbi"),
                                    "pbi_max_us_dollars": i.get("pv_pbi_max"),
                                    "pbi_years": i.get("pv_pbi_years"),
                                    "pbi_system_max_kw": i.get("pv_pbi_system_max"),

                                },

                            "Wind":
                                {
                                    "min_kw": i.get("wind_kw_min"),
                                    "max_kw": i.get("wind_kw_max"),
                                    "installed_cost_us_dollars_per_kw": i.get("wind_cost"),
                                    "om_cost_us_dollars_per_kw": i.get("wind_om"),
                                    "degradation_pct": i.get("wind_degradation_rate"),
                                    "macrs_option_years": i.get("wind_macrs_schedule"),
                                    "macrs_bonus_pct": i.get("wind_macrs_bonus_fraction"),
                                    "federal_itc_pct": i.get("wind_itc_federal"),
                                    "state_ibi_pct": i.get("wind_ibi_state"),
                                    "state_ibi_max_us_dollars": i.get("wind_ibi_state_max"),
                                    "utility_ibi_pct": i.get("wind_ibi_utility"),
                                    "utility_ibi_max_us_dollars": i.get("wind_ibi_utility_max"),
                                    "federal_rebate_us_dollars_per_kw": i.get("wind_rebate_federal"),
                                    "state_rebate_us_dollars_per_kw": i.get("wind_rebate_state"),
                                    "state_rebate_max_us_dollars": i.get("wind_rebate_state_max"),
                                    "utility_rebate_us_dollars_per_kw": i.get("wind_rebate_utility"),
                                    "utility_rebate_max_us_dollars": i.get("wind_rebate_utility_max"),
                                    "pbi_us_dollars_per_kwh": i.get("wind_pbi"),
                                    "pbi_max_us_dollars": i.get("wind_pbi_max"),
                                    "pbi_years": i.get("wind_pbi_years"),
                                    "pbi_system_max_kw": i.get("wind_pbi_system_max"),

                            "Storage":
                                {
                                    "min_kw": i.get("batt_kw_min"),
                                    "max_kw": i.get("batt_kw_max"),
                                    "min_kwh": i.get("batt_kwh_min"),
                                    "max_kwh": i.get("batt_kwh_max"),
                                    "internal_efficiency_pct": i.get("batt_efficiency"),
                                    "inverter_efficiency_pct": i.get("batt_inverter_efficiency"),
                                    "rectifier_efficiency_pct": i.get("batt_rectifier_efficiency"),
                                    "soc_min_pct": i.get("batt_soc_min"),
                                    "soc_init_pct": i.get("batt_soc_init"),
                                    "canGridCharge": i.get("batt_can_gridcharge"),
                                    "installed_cost_us_dollars_per_kw": i.get("batt_cost_kw"),
                                    "installed_cost_us_dollars_per_kwh": i.get("batt_cost_kwh"),
                                    "replace_cost_us_dollars_per_kw": i.get("batt_replacement_cost_kw"),
                                    "replace_cost_us_dollars_per_kwh": i.get("batt_replacement_cost_kwh"),
                                    "inverter_replacement_year": i.get("batt_replacement_year_kw"),
                                    "battery_replacement_year": i.get("batt_replacement_year_kwh"),
                                    "macrs_option_years": i.get("batt_macrs_schedule"),
                                    "macrs_bonus_pct": i.get("batt_macrs_bonus_fraction"),
                                    "total_itc_pct":  i.get("batt_itc_total"),
                                    "total_rebate_us_dollars_per_kw": i.get("batt_rebate_total"),

                                }
                            }
                    },
                }
            }
        }
