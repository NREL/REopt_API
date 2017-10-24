from tastypie.validation import Validation
import numpy as np
from api_definitions import inputs
from log_levels import log
from urdb_logger import log_urdb_errors
from nested_inputs import nested_input_definitions, flat_to_nested
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

    def check_input_format(self, key, value, field_definition):

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

    def get_missing_required_message(self, input_arg):
        definition_values = inputs(full_list=True)
        depends = definition_values[input_arg].get('depends_on')
 
        if depends is not None:
            fields = sorted([input_arg] + depends)
            input_arg = fields[0]
            depends = fields[1:]

        swap = definition_values[input_arg].get('swap_for')
        alt_field = definition_values[input_arg].get('alt_field')

        message = "(" + input_arg
       
        if alt_field is not None:
            message += " (or %s)" % (alt_field)
      
        if depends is not None:
            message += ' and ' + ",".join(depends) + ")"
 
        if swap is not None:
            message += " OR (%s)" % ( " and ".join(swap)  )
                	
        return message

    def get_missing_dependency_message(self, input_arg):
        definition_values = inputs(full_list=True)[input_arg]

        dependency_of = []
        for k, v in inputs(full_list=True).items():
            value = v.get('depends_on')
            if value is not None:
                if input_arg in value:
                    dependency_of.append(k)
        return "%s (%s depend(s) on this input.)" % (input_arg, "  and ".join(dependency_of))

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

    def missing_required(self, key_list):
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

    def __init__(self, input_dict, nested=False):
        self.nested_input_definitions = nested_input_definitions
        self.input_dict = input_dict

        if not nested:
            self.input_dict = flat_to_nested(input_dict)

        self.input_data_errors = []
        self.urdb_errors = []
        self.input_as_none = []
        self.invalid_inputs = []
        self.defaults_inserted = []

        self.recursively_check_input(nested_template=self.nested_input_definitions,
                                     comparison_function=self.remove_invalid_keys)

        self.recursively_check_input(nested_template=self.input_dict,
                                     comparison_function=self.remove_nones)

        self.recursively_check_input(nested_template=self.nested_input_definitions,
                                     comparison_function=self.convert_data_types)

        self.recursively_check_input(nested_template=self.nested_input_definitions,
                                     comparison_function=self.fillin_defaults)

    def recursively_check_input(self, nested_template, comparison_function, nested_dictionary_to_check=None,
                                object_name_path=[]):
        """

        :param nested_template: nested dictionary that is read to get the order in which objects are nested in each
            other.
        :param comparison_function: tells the algorithm what to do when you have the object name (PV) and the user
            supplied values ('max_kw':0).
        :param nested_dictionary_to_check: input dictionary values
        :param object_name_path: list of str, keys that access the values that are being validated
        :return:
        """

        if nested_dictionary_to_check is None:
            nested_dictionary_to_check = self.input_dict

        for template_key, template_values in nested_template.items():

            input_values = nested_dictionary_to_check.get(template_key, {})

            if self.isSingularKey(template_key):
                comparison_function(object_name_path=object_name_path + [template_key],
                                    template_values=template_values, input_values=input_values)

                self.recursively_check_input(nested_template[template_key], comparison_function,
                                             nested_dictionary_to_check=input_values or {},
                                             object_name_path=object_name_path + [template_key]
                                             )

    @property
    def isValid(self):

        self.recursively_check_input(self.nested_input_definitions, self.check_special_data_types)
        self.recursively_check_input(self.nested_input_definitions, self.check_min_max_restrictions)
        self.recursively_check_input(self.nested_input_definitions, self.check_required_attributes)

        if self.input_data_errors or self.urdb_errors:
            return False

        return True

    """
    The following 7 functions are used as `comparison_function`s in self.recursively_check_input, in the same order.
    """
    def remove_invalid_keys(self, object_name_path, template_values, input_values):

        for name in input_values.keys():
            if self.isAttribute(name):
                if name not in template_values.keys():
                    self.delete_attribute(object_name_path, name)
                    self.invalid_inputs.append([name, object_name_path])

    def remove_nones(self, object_name_path, template_values, input_values):

        for name, value in input_values.items():
            if self.isAttribute(name):
                if value is None:
                    self.delete_attribute(object_name_path, name)
                    self.input_as_none.append([name, object_name_path[-1]])

    def convert_data_types(self, object_name_path, template_values=None, input_values=None):
        if input_values is not None:
            for name, value in input_values.items():
                if self.isAttribute(name):
                    try:
                        data_validators = template_values[name]
                        attribute_type = data_validators['type']
                        new_value = attribute_type(value)
                        if not isinstance(new_value, bool):
                            self.update_attribute_value(object_name_path, name, new_value)
                        else:
                            if value not in [True, False, 1, 0]:
                                self.input_data_errors.append('Could not convert %s (%s) in %s to %s' % (name, value, self.object_name_string(object_name_path),str(attribute_type).split(' ')[1]))

                    except:
                        self.input_data_errors.append('Could not convert %s (%s) in %s to %s' % (name, value, self.object_name_string(object_name_path), str(attribute_type).split(' ')[1]))

    def fillin_defaults(self, object_name_path, template_values, input_values):
        for template_key, template_value in template_values.items():

            if self.isAttribute(template_key):
                default = template_value.get('default')
                if default is not None and input_values.get(template_key) is None:
                    self.update_attribute_value(object_name_path, template_key, default)
                    self.defaults_inserted.append([template_key, object_name_path])

            if self.isSingularKey(template_key):
                if template_key not in input_values.keys():
                    self.update_attribute_value(object_name_path, template_key, {})
                    self.defaults_inserted.append([template_key, object_name_path])

    def check_special_data_types(self, object_name_path, template_values=None, input_values=None):
        if input_values is not None:
            urdb_response = input_values.get('urdb_response')
            if urdb_response is not None:
                try:
                    rate_checker = URDB_RateValidator(**urdb_response)
                    if rate_checker.errors:
                        self.urdb_errors.append(rate_checker.errors)
                except:
                    self.urdb_errors.append('Error parsing urdb rate in %s ' % (object_name_path))

    def check_min_max_restrictions(self, object_name_path, template_values, input_values=None):
        if input_values is not None:
            for name, value in input_values.items():
                if self.isAttribute(name):
                    # need to remove invalid keys first
                    data_validators = template_values[name]  # assumes that input_values only has keys that align with template

                    try:
                        value == data_validators['type'](value)

                        if data_validators.get('min') is not None:
                            if value < data_validators['min']:
                                self.input_data_errors.append('%s value (%s) in %s exceeds allowable min %s' % (name, value, self.object_name_string(object_name_path), data_validators['min']))

                        if data_validators.get('max') is not None:
                            if value > data_validators['max']:
                                self.input_data_errors.append('%s value (%s) in %s exceeds allowable max %s' % (name, value, self.object_name_string(object_name_path), data_validators['max']))

                    except:
                        self.input_data_errors.append('Could not check min/max on %s (%s) in %s' % (name, value, self.object_name_string(object_name_path)))


                    if data_validators.get('restrict_to') is not None:
                        if value not in data_validators['restrict_to']:
                            self.input_data_errors.append('%s value (%s) in %s not in allowable inputs - %s' % (name, value, self.object_name_string(object_name_path), data_validators['restrict_to']))

    def check_required_attributes(self, object_name_path, template_values=None, input_values=None):

            final_message = ''

            #conditional check for complex cases where key match at least one valid set
            def check_satisfies_one_input_set(valid_input_sets, keys):

                set_check_results = []
                for valid_set in valid_input_sets:
                    set_check_results.append(list(set(valid_set) - set(keys)))

                if [] not in set_check_results:
                    needed_keys = []
                    for check_result in set_check_results:
                        needed_keys.append(' and '.join(check_result))

                    message = ' OR '.join(needed_keys)
                    return message

                return ''


            keys = input_values.keys()

            if object_name_path[-1] ==  "LoadProfile":
                must_match_one_of_these_valid_sets =  [['doe_reference_name','annual_kwh'],['doe_reference_name','monthly_totals_kwh'],['loads_kw']]
                final_message = check_satisfies_one_input_set(must_match_one_of_these_valid_sets, keys)

            if object_name_path[-1] == "ElectricTariff":
                must_match_one_of_these_valid_sets = [["blended_monthly_rates_us_dollars_per_kwh", "monthly_demand_charges_us_dollars_per_kw"], ["urdb_response"]]
                final_message = check_satisfies_one_input_set(must_match_one_of_these_valid_sets, keys)

            #check simple required attributes

            missing = []
            for template_key,template_value in template_values.items():
                if self.isAttribute(template_key):
                    if template_value.get('required')==True:
                        if input_values.get(template_key) is None:
                            missing.append(template_key)

            if len(missing) > 0:
                message = ' and '.join(missing)
                if final_message != '':
                    final_message += ' and ' + message
                else:
                    final_message = message

            if final_message != '':
                self.input_data_errors.append('Missing Required for %s: %s' % (self.object_name_string(object_name_path),final_message))

    @property
    def error_response(self):
        return {"Input Errors": self.errors, "Warnings": self.warnings}

    @staticmethod
    def warning_message(warnings):
        """
        Convert a list of lists into a dictionary
        :param warnings: list of lists, where each interior list contains two values: the first value is the name of a
            argument, the second value is the path to that argument in the nested input
        :return: dictionary with keys for the nested paths and values for the arguments contained at those paths
        """
        output = {}
        for arg, path in warnings:
            path = ">".join(path)
            if path not in output:
                output[path] = arg
            else:
                output[path] += ' AND ' + arg

        return output

    @property
    def errors(self):
        output = {}

        if self.urdb_errors:
            output["URDB Errors"] = self.urdb_errors

        if self.input_data_errors:
            output["Input Errors"] = self.input_data_errors

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
        """
        test if string k is capitalized and the last char is not 's'
        :param k: string to test
        :return: True/False
        """
        return k[0] == k[0].upper() and k[-1] != 's'

    def isPluralKey(self, k):
        """
        test if string k is capitalized and the last char is 's'
        :param k: string to test
        :return: True/False
        """
        return k[0] == k[0].upper() and k[-1] == 's'

    def isAttribute(self, k):
        """
        tests if string k is lower case
        :param k: string to test
        :return: True/False
        """
        return k[0] == k[0].lower()

    def update_attribute_value(self, object_name_path, attribute, value):

        dictionary = self.input_dict

        for name in object_name_path:
            dictionary = dictionary.get(name, {})

        dictionary[attribute] = value

    def delete_attribute(self, object_name_path, key):
        """
        Delete key in self.input_dict
        :param object_name_path: list of strings, which are the ordered keys to access the value in self.input_dict
        :param key: str, key to delete in self.input_dict
        :return: None
        """

        dictionary = self.input_dict

        for name in object_name_path:
            dictionary = dictionary[name]

        if key in dictionary.keys():
            del dictionary[key]

    def object_name_string(self, object_name_path):
        return '>'.join(object_name_path)

    def test_data(self, definition_attribute):

        self.test_data_list = []

        if definition_attribute == 'min':
            def swap_logic(object_name_path, name, definition, current_value):
                attribute_min = definition.get('min')
                if attribute_min is not None:
                    new_value = attribute_min - 1
                    self.update_attribute_value(object_name_path, name, new_value)
                    self.test_data_list.append([name, copy.deepcopy(self.input_dict)])
                    self.update_attribute_value(object_name_path, name, current_value)

        if definition_attribute == 'max':
            def swap_logic(object_name_path, name, definition, current_value):
                attribute_max = definition.get('max')
                if attribute_max is not None:
                    new_value = attribute_max + 1
                    self.update_attribute_value(object_name_path, name, new_value)
                    self.test_data_list.append([name, copy.deepcopy(self.input_dict)])
                    self.update_attribute_value(object_name_path, name, current_value)

        if definition_attribute == 'restrict_to':
            def swap_logic(object_name_path, name, definition, current_value):
                attribute = definition.get('restrict_to')
                if attribute is not None:
                    new_value = "OOPS"
                    self.update_attribute_value(object_name_path, name, new_value)
                    self.test_data_list.append([name, copy.deepcopy(self.input_dict)])
                    self.update_attribute_value(object_name_path, name, current_value)

        if definition_attribute == 'type':
            def swap_logic(object_name_path, name, definition, current_value):
                attribute_type = definition['type']
                value = attribute_type(current_value)
                if isinstance(value, float) or isinstance(value, int) or isinstance(value, dict) or isinstance(value, bool):
                    new_value = "OOPS"
                    self.update_attribute_value(object_name_path, name, new_value)
                    self.test_data_list.append([name, copy.deepcopy(self.input_dict)])
                    self.update_attribute_value(object_name_path, name, value)

        def add_invalid_data(object_name_path, template_values, input_values=None):
            if input_values is not None:
                for name, value in template_values.items():
                    if self.isAttribute(name):
                        swap_logic(object_name_path, name, value, input_values.get(name))

        self.recursively_check_input(self.nested_input_definitions, add_invalid_data)

        return self.test_data_list
