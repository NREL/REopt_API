from tastypie.validation import Validation
import numpy as np
from api_definitions import inputs
from log_levels import log
from urdb_logger import log_urdb_errors

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
    
    def validate_energyweekdayschedule(self):
        name = 'energyweekdayschedule'
        if self.validDependencies(name):
            self.validSchedule(name, 'energyratestructure')

    def validate_energyweekendschedule(self):
        name = 'energyweekendschedule'
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

    def validRate(self, rate):
        # check that each  tier in rate structure array has a rate attribute
        # return Boolean if any errors found
        if hasattr(self,rate):
            valid = True
            for i, r in enumerate(getattr(self, rate)):
                if len(r)==0:
                    self.errors.append('Missing rate information for rate ' + str(i) + ' in ' + rate)
                    valid = False
                for ii, t in enumerate(r):
                    if t.get('rate') is None and t.get('sell') is None and t.get('adj') is None:
                        self.errors.append('Missing rate/sell/adj attributes for tier ' + str(ii) + " in rate " + str(i) + ' ' + rate)
                        valid = False
            return valid
        return False

    def validSchedule(self, schedules, rate):
        # check that each rate an a schedule array has a valid set of tiered rates in the associated rate struture attribute
        # return Boolean if any errors found
        if hasattr(self,schedules):
            valid = True
            s = getattr(self, schedules)
            if np.array(s).ndim > 1:
                s = np.concatenate(s)

            periods = list(set(s))

            # Loop though all periond and catch error if if exists
            for period in periods:
                if period > len(getattr(self,rate)) - 1 or period < 0:
                    self.errors.append(
                        '%s contains value %s which has no associated rate in %s' % (schedules, period, rate))
                    valid = False
            return valid
        return False


class REoptResourceValidation(Validation):

    def check_individual(self, input_dictionary, errors):

        for key, value in input_dictionary.items():

            if key not in inputs(full_list=True):
                errors = self.append_errors(errors, key, ['This key name does not match a valid input.'])
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
                field_def = inputs(full_list=True)[key]
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
