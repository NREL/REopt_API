# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
import numpy as np
import pandas as pd
from .urdb_logger import log_urdb_errors
from .nested_inputs import nested_input_definitions, list_of_float, list_of_str
#Note: list_of_float is actually needed
import os
import csv
import copy
from reo.src.urdb_rate import Rate
import re
import uuid
from reo.src.techs import Generator
from reo.nested_inputs import max_big_number
from reo.src.emissions_calculator import EmissionsCalculator

hard_problems_csv = os.path.join('reo', 'hard_problems.csv')
hard_problem_labels = [i[0] for i in csv.reader(open(hard_problems_csv, 'r'))]


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
        kwargs.setdefault("label", "custom")
        for key in kwargs:                           #Load in attributes
            setattr(self, key, kwargs[key])

        self.validate()                              #Validate attributes

        if _log_errors:
            if len(self.errors + self.warnings) > 0:
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
        self.list_or_dict_objects = ['PV']
        self.nested_input_definitions = nested_input_definitions
        self.input_data_errors = []
        self.urdb_errors = []
        self.input_as_none = []
        self.invalid_inputs = []
        self.resampled_inputs = []
        self.emission_warning = []
        self.defaults_inserted = []
        self.input_dict = dict()
        if type(input_dict) is not dict:
            self.input_data_errors.append("POST must contain a valid JSON formatted accoring to format described in https://developer.nrel.gov/docs/energy-optimization/reopt-v1/")
        else:        
            self.input_dict['Scenario'] = input_dict.get('Scenario') or {}
            for k,v in input_dict.items():
                if k != 'Scenario':
                    self.invalid_inputs.append([k, ["Top Level"]])

            self.check_object_types(self.input_dict)
        if self.isValid:
            self.recursively_check_input_dict(self.nested_input_definitions, self.remove_invalid_keys)
            self.recursively_check_input_dict(self.nested_input_definitions, self.remove_nones)
            self.recursively_check_input_dict(self.nested_input_definitions, self.convert_data_types)
            self.recursively_check_input_dict(self.nested_input_definitions, self.fillin_defaults)
            self.recursively_check_input_dict(self.nested_input_definitions, self.check_min_max_restrictions)
            self.recursively_check_input_dict(self.nested_input_definitions, self.check_required_attributes)
            self.recursively_check_input_dict(self.nested_input_definitions, self.check_special_cases)

            self.recursively_check_input_dict(self.nested_input_definitions, self.add_number_to_listed_inputs)

            if type(self.input_dict['Scenario']['Site']['PV']) == dict:
                self.input_dict['Scenario']['Site']['PV']['pv_number'] = 1
                self.input_dict['Scenario']['Site']['PV'] = [self.input_dict['Scenario']['Site']['PV']]

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
            output["error"] = "Invalid inputs. See 'input_errors'."
            output["input_errors"] = self.urdb_errors

        return output

    @property
    def warnings(self):
        output = {}

        if bool(self.defaults_inserted):
            output["Default values used for the following:"] = self.warning_message(self.defaults_inserted)

        if bool(self.invalid_inputs):
            output["Following inputs are invalid:"] = self.warning_message(self.invalid_inputs)

        if bool(self.resampled_inputs):
            output["Following inputs were resampled:"] = self.warning_message(self.resampled_inputs)

        if bool(self.emission_warning):
            output["Emissons Warning"] = {"error":self.emission_warning}

        return output

    def isSingularKey(self, k):
        """
        True if the string `k` is upper case and does not end with "s"
        :param k: str
        :return: True/False
        """
        return k[0] == k[0].upper() and k[-1] != 's'

    def isPluralKey(self, k):
        return k[0] == k[0].upper() and k[-1] == 's'

    def isAttribute(self, k):
        return k[0] == k[0].lower()

    def check_object_types(self, nested_dictionary_to_check, object_name_path=[]):
        """
        Checks that all keys (i.e. Scenario, Site) are valid dicts or lists. This function only checks object names
        and does not validate attributes

        :param nested_dictionary_to_check: data to be validated; default is self.input_dict
        :param object_name_path: list of str, used to keep track of keys necessary to access a value to check in the
                nested_template / nested_dictionary_to_check
        :return: None
        """

        # Loop through all keys in the dictionary
        for name in nested_dictionary_to_check.keys():
            # If the key is an object name (i.e. Scnenario, Wind) continue
            if self.isSingularKey(name):
                # get the value of the key
                real_input_value = nested_dictionary_to_check.get(name)

                # assume the value is fine until we catch an error
                continue_checking = True

                # Assess all possible value data type scenartio
                # catch the case were the value is ok:
                #     dicts are always allowed
                #     Nones are ok too, they will get filled in with default values at first then later checked for required attributes
                if type(real_input_value) == dict or real_input_value is None:
                    pass
                # catch list case
                elif type(real_input_value) == list:
                    # if the object is not one that support a list input flag an error
                    if name not in self.list_or_dict_objects:
                        message = "A list of inputs is not allowed for {}".format(">".join(object_name_path + [name]))
                        self.input_data_errors.append(message)
                        continue_checking = False
                    else:
                        # if the object supports list input, but contains anything other than dicts flag an error
                        if len(real_input_value) > 0:
                            if False in [type(x)==dict for x in real_input_value]:
                                message = "Lists for {} must only contain hashes of key/value pairs. No other data types are allowed (i.e. list, float, int) ".format(">".join(object_name_path + [name]))
                                self.input_data_errors.append(message)
                                continue_checking = False
                # catch all other data types and flag them as an error
                else:
                    valid_types = "hash of key and value pairs,"
                    if name not in self.list_or_dict_objects:
                        valid_types += " or a list"
                    message = "Invalid data type ({}) for {}. Must be {}".format(type(real_input_value).__name__, ">".join(object_name_path + [name]), valid_types)
                    self.input_data_errors.append(message)
                    continue_checking = False

                # if no error has been thrown continue recursively checking the nested dict
                if continue_checking:
                        if type(real_input_value) == list:
                            for rv in real_input_value:
                                self.check_object_types(rv or {}, object_name_path=object_name_path + [name])
                        else:
                            self.check_object_types(real_input_value or {}, object_name_path=object_name_path + [name])

    def recursively_check_input_dict(self, nested_template, comparison_function, nested_dictionary_to_check=None,
                                        object_name_path=[]):
        """
        Recursively perform comparison_function on nested_dictionary_to_check using nested_template as a guide for
        the (key: value) pairs to be checked in nested_dictionary_to_check.
        comparison_function's include
            - remove_invalid_keys
            - remove_nones
            - convert_data_types
            - fillin_defaults
            - check_min_max_restrictions
            - check_required_attributes
            - add_invalid_data (for testing)
        :param nested_template: nested dictionary, used as guide for checking nested_dictionary_to_check
        :param comparison_function: one of the input data validation tasks listed above
        :param nested_dictionary_to_check: data to be validated; default is self.input_dict
        :param object_name_path: list of str, used to keep track of keys necessary to access a value to check in the
                nested_template / nested_dictionary_to_check
        :return: None
        """
        # this is a dict of input values from the user
        if nested_dictionary_to_check is None:
            nested_dictionary_to_check = self.input_dict

        # this is a corresponding dict from the input definitions used to validate structure and content
        # template is a list to handle cases where the input is a list
        if type(nested_template) == dict:
            nested_template = [nested_template]

        # catch case there there is no nested template
        if nested_template is None:
            nested_template = [{}]

        # Loop through template structure so we catch all possible keys even if the user does not provide them
        for template in nested_template:
            for template_k, template_values in template.items():
                # at a key value pair, get the real value a user input (can be None)
                real_input_values = nested_dictionary_to_check.get(template_k)

                # start checking assuming that the input is fine and a list
                # for each of coding we will populate real_values_list with a list
                continue_checking = True
                input_isDict = False
                real_values_list = None

                # if the value is a dict make it a list and update the dict or list indicator
                if type(real_input_values) == dict:
                    input_isDict = True
                    real_values_list = [real_input_values]
                # if the value is a list just update the real_values_list variable
                if type(real_input_values) == list:
                    real_values_list = real_input_values

                # if the value is a None make it a list with one dict in it
                if real_input_values is None:
                    input_isDict = True
                    real_values_list = [{}]

                # if the key is an object name apply the comparison function to all key/value pairs in each dict in the list of values
                if self.isSingularKey(template_k):

                    # number is indexed on 1, used currently only for telling PV's apart
                    for number, real_values in enumerate(real_values_list):
                        number += 1
                        # real values will always be a list per validation above
                        comparison_function(object_name_path=object_name_path + [template_k],
                                            template_values=template_values, real_values=real_values,
                                            number=number, input_isDict=input_isDict)

                        # recursively apply this function to the real values dict
                        self.recursively_check_input_dict(template[template_k], comparison_function,
                                                            real_values or {},
                                                            object_name_path=object_name_path + [template_k])

                    # if at the end of validation we are left with a list containing one dict, convert the entry fot the object back to
                    # a dict from a list
                    if len(real_values_list) == 1:
                        nested_dictionary_to_check[template_k] = real_values_list[0]

    def update_attribute_value(self, object_name_path, number, attribute, value):
        """
        updates an attribute in the user input dictionary
        :param definition_attribute: str, key for input parameter validation dict, eg. {'type':'float', ... }
        :param object_name_path: list of str, used to keep track of keys necessary to access a value in a nested dict
        :param number: int, used to keep track of order in list inputs (i.e. PV))
        :param attribute: str, this is the name of the key to update
        :param number: int, this is the order of the object in a list, defaulted to 1 in recursively_check_input_dict function
        :param value: any, new value for the attribute
        """
        to_update = self.input_dict

        for name in object_name_path:
            name = name.split(' ')[0]
            to_update = to_update[name]

        if number == 1 and type(to_update) == dict:
            to_update[attribute] = value
        else:
            to_update[number-1][attribute] = value

    def delete_attribute(self, object_name_path, number, attribute):
        """
        deletes an attribute in the user input dictionary
        :param definition_attribute: str, key for input parameter validation dict, eg. {'type':'float', ... }
        :param object_name_path: list of str, used to keep track of keys necessary to access a value in a nested dict
        :param number: int, used to keep track of order in list inputs (i.e. PV))
        :param attribute: str, this is the name of the key to delete
        :param number: int, this is the order of the object in a list, defaulted to 1 in recursively_check_input_dict function
        """
        to_update = self.input_dict

        for name in object_name_path:
            name = name.split(' ')[0]
            to_update = to_update[name]

        if number == 1 and type(to_update) == dict:
            if attribute in to_update.keys():
                del to_update[attribute]
        else:
            if attribute in to_update[number-1].keys():
                del to_update[number-1][attribute]

    def object_name_string(self, object_name_path):
        return '>'.join(object_name_path)

    def test_data(self, definition_attribute):
        """
        Used only in reo.tests.test_reopt_url. Does not actually validate inputs.
        :param definition_attribute: str, key for input parameter validation dict, eg. {'type':'float', ... }
        :return: test_data_list is a list of lists, with each sub list a pair of [str, dict],
            where the str is an input param, dict is an entire post with a bad value for that input param
        """
        test_data_list = []
        number = 1
        def swap_logic(object_name_path, name, definition, good_val, validation_attribute, number =1):
            """
            append `name` and a nested-dict (post) to test_data_list with a bad value inserted into the post for
            the input at object_name_path: name
            :param object_name_path: list of str, eg. ["Scenario", "Site", "PV"]
            :param name: str, input value to replace with bad value, eg. "latitude"
            :param definition: dict with input parameter validation values, eg. {'type':'float', ... }
            :param good_val: the good value for the input parameter
            :param validation_attribute: str, ['min', 'max', 'restrict_to', 'type']
            :return: None
            """
            attribute = definition.get(validation_attribute)
            if attribute is not None:
                bad_val = None
                if validation_attribute == 'min':
                    bad_val = attribute - 1
                    if isinstance(good_val, list):
                        bad_val= [bad_val]
                if validation_attribute == 'max':
                    bad_val = attribute + 1
                    if isinstance(good_val, list):
                        bad_val = [bad_val]
                if validation_attribute == 'restrict_to':
                    bad_val = "OOPS"
                if validation_attribute == 'type':
                    if type(attribute) != list and 'list_of_float' != attribute:
                        if any(isinstance(good_val, x) for x in [float, int, dict, bool]):
                            bad_val = "OOPS"
                    elif 'list_of_float' in attribute or 'list_of_float' == attribute:
                        if isinstance(good_val, list):
                            bad_val = "OOPS"

                if bad_val is not None:
                    self.update_attribute_value(object_name_path, number, name, bad_val)
                    test_data_list.append([name, copy.deepcopy(self.input_dict)])
                    self.update_attribute_value(object_name_path, number, name, good_val)

        def add_invalid_data(object_name_path, template_values=None, real_values=None, number=number, input_isDict=None):
            if real_values is not None:
                for name, value in template_values.items():
                    if self.isAttribute(name):
                        swap_logic(object_name_path, name, value, real_values.get(name),
                                    validation_attribute=definition_attribute, number=number)

        self.recursively_check_input_dict(self.nested_input_definitions, add_invalid_data)

        return test_data_list

    def add_number_to_listed_inputs(self, object_name_path, template_values=None, real_values=None, number=1, input_isDict=None):
        """
        comparison function to add a number to each dict in a list (i.e. pv_number to each PV)
        :param object_name_path: list of str, location of an object in self.input_dict being validated,
            eg. ["Scenario", "Site", "PV"]
        :param template_values: reference dictionary for checking real_values, for example
            {'latitude':{'type':'float',...}...}, which comes from nested_input_definitions
        :param real_values: dict, the attributes corresponding to the object at object_name_path within the
            input_dict to check and/or modify. For example, with a object_name_path of ["Scenario", "Site", "PV"]
                the real_values would look like: {'latitude': 39.345678, 'longitude': -90.3, ... }
        :param number: int, order of the dict in the list
        :param input_isDict: bool, indicates if the object input came in as a dict or list
        :return: None
        """
        if real_values is not None and input_isDict==False:
            object_name_path[-1].lower()
            self.update_attribute_value(object_name_path, number, object_name_path[-1].lower() + '_number', number)

    def remove_nones(self, object_name_path, template_values=None, real_values=None, number=1, input_isDict=None):
        """
        comparison_function for recursively_check_input_dict.
        remove any `None` values from the input_dict.
        this step is important to prevent exceptions in later validation steps.
        :param object_name_path: list of str, location of an object in self.input_dict being validated,
            eg. ["Scenario", "Site", "PV"]
        :param template_values: reference dictionary for checking real_values, for example
            {'latitude':{'type':'float',...}...}, which comes from nested_input_definitions
        :param real_values: dict, the attributes corresponding to the object at object_name_path within the
            input_dict to check and/or modify. For example, with a object_name_path of ["Scenario", "Site", "PV"]
                the real_values would look like: {'latitude': 39.345678, 'longitude': -90.3, ... }
        :param number: int, order of the dict in the list
        :param input_isDict: bool, indicates if the object input came in as a dict or list
        :return: None
        """
        if real_values is not None:
            rv = copy.deepcopy(real_values)
            for name, value in rv.items():
                if self.isAttribute(name):
                    if value is None:
                        self.delete_attribute(object_name_path, number, name)
                        if input_isDict == True or input_isDict==None:
                            self.input_as_none.append([name, object_name_path[-1]])
                        if input_isDict == False:
                            self.input_as_none.append([name, object_name_path[-1] + ' (number {})'.format(number)])

    def remove_invalid_keys(self, object_name_path, template_values=None, real_values=None, number=1, input_isDict=None):
        """
        comparison_function for recursively_check_input_dict.
        remove any input values provided by user that are not included in nested_input_definitions.
        this step is important to protect against sql injections and other similar cyber-attacks.
        :param object_name_path: list of str, location of an object in self.input_dict being validated,
            eg. ["Scenario", "Site", "PV"]
        :param template_values: reference dictionary for checking real_values, for example
            {'latitude':{'type':'float',...}...}, which comes from nested_input_definitions
        :param real_values: dict, the attributes corresponding to the object at object_name_path within the
            input_dict to check and/or modify. For example, with a object_name_path of ["Scenario", "Site", "PV"]
                the real_values would look like: {'latitude': 39.345678, 'longitude': -90.3, ... }
        :param number: int, order of the dict in the list
        :param input_isDict: bool, indicates if the object input came in as a dict or list
        :return: None
        """
        if real_values is not None:
            rv = copy.deepcopy(real_values)
            for name, value in rv.items():
                if self.isAttribute(name):
                    if name not in template_values.keys():
                        self.delete_attribute(object_name_path, number, name)
                        if input_isDict == True or input_isDict==None:
                            self.invalid_inputs.append([name, object_name_path])
                        if input_isDict == False:
                            object_name_path[-1] = object_name_path[-1] + ' (number {})'.format(number)
                            self.invalid_inputs.append([name, object_name_path])

    def check_special_cases(self, object_name_path, template_values=None, real_values=None, number=1, input_isDict=None):
        """
        checks special input requirements not otherwise programatically captured by nested input definitions

        :param object_name_path: list of str, location of an object in self.input_dict being validated,
            eg. ["Scenario", "Site", "PV"]
        :param template_values: reference dictionary for checking real_values, for example
            {'latitude':{'type':'float',...}...}, which comes from nested_input_definitions
        :param real_values: dict, the attributes corresponding to the object at object_name_path within the
            input_dict to check and/or modify. For example, with a object_name_path of ["Scenario", "Site", "PV"]
                the real_values would look like: {'latitude': 39.345678, 'longitude': -90.3, ... }
        :param number: int, order of the dict in the list
        :param input_isDict: bool, indicates if the object input came in as a dict or list
        :return: None
        """
        if object_name_path[-1] == "Scenario":
            if real_values.get('user_uuid') is not None:
                self.validate_user_uuid(user_uuid=real_values['user_uuid'], err_msg = "user_uuid must be a valid UUID")
            if real_values.get('description') is not None:
                self.validate_text_fields(str = real_values['description'],
                                            pattern = r'^[-0-9a-zA-Z.  $:;)(*&#_!@]*$',
                            err_msg = "description can include enlisted special characters: [-0-9a-zA-Z.  $:;)(*&#_!@] and can have 0-9, a-z, A-Z, periods, and spaces.")

        if object_name_path[-1] == "Site":
            if real_values.get('address') is not None:
                self.validate_text_fields(str = real_values['address'], pattern = r'^[0-9a-zA-Z. ]*$',
                            err_msg = "Site address must not include special characters. Restricted to 0-9, a-z, A-Z, periods, and spaces.")
        
        if object_name_path[-1] == "PV":
            if real_values.get("prod_factor_series_kw") == []:
                del real_values["prod_factor_series_kw"]

            if any((isinstance(real_values['max_kw'], x) for x in [float, int])):
                if real_values['max_kw'] > 0:
                    if real_values.get("prod_factor_series_kw"):
                        self.validate_8760(real_values.get("prod_factor_series_kw"),
                                                            "PV", "prod_factor_series_kw", self.input_dict['Scenario']['time_steps_per_hour'])
    
        if object_name_path[-1] == "Wind":
            if any((isinstance(real_values['max_kw'], x) for x in [float, int])):
                if real_values['max_kw'] > 0:

                    if real_values.get("prod_factor_series_kw") == []:
                        del real_values["prod_factor_series_kw"]

                    if real_values.get("prod_factor_series_kw"):
                        self.validate_8760(real_values.get("prod_factor_series_kw"),
                                            "Wind", "prod_factor_series_kw", self.input_dict['Scenario']['time_steps_per_hour'])

                    if real_values.get("wind_meters_per_sec"):
                        self.validate_8760(real_values.get("wind_meters_per_sec"),
                                            "Wind", "wind_meters_per_sec", self.input_dict['Scenario']['time_steps_per_hour'])

                        self.validate_8760(real_values.get("wind_direction_degrees"),
                                            "Wind", "wind_direction_degrees", self.input_dict['Scenario']['time_steps_per_hour'])

                        self.validate_8760(real_values.get("temperature_celsius"),
                                            "Wind", "temperature_celsius", self.input_dict['Scenario']['time_steps_per_hour'])

                        self.validate_8760(real_values.get("pressure_atmospheres"),
                                            "Wind", "pressure_atmospheres", self.input_dict['Scenario']['time_steps_per_hour'])
                    else:
                        from reo.src.wind_resource import get_conic_coords

                        if self.input_dict['Scenario']['Site']['Wind'].get('size_class') is None:
                            """
                            size_class is determined by average load. If using simulated load, then we have to get the ASHRAE
                            climate zone from the DeveloperREOapi in order to determine the load profile (done in BuiltInProfile).
                            In order to avoid redundant external API calls, when using the BuiltInProfile here we save the
                            BuiltInProfile in the inputs as though a user passed in the profile as their own. This logic used to be
                            handled in reo.src.load_profile, but due to the need for the average load here, the work-flow has been
                            modified.
                            """

                            avg_load_kw = 0
                            if self.input_dict['Scenario']['Site']['LoadProfile'].get('annual_kwh') is not None:
                                annual_kwh_list = self.input_dict['Scenario']['Site']['LoadProfile'].get('annual_kwh')
                                percent_share_list = self.input_dict['Scenario']['Site']['LoadProfile'].get('percent_share')
                                # Find weighted avg for hybrid load profile
                                avg_load_kw = sum(
                                    [annual_kwh_list[i] * percent_share_list[i] / 100 for i in range(len(annual_kwh_list))]) / 8760

                            elif self.input_dict['Scenario']['Site']['LoadProfile'].get('annual_kwh') is None and self.input_dict['Scenario']['Site']['LoadProfile'].get('doe_reference_name') is not None:
                                from reo.src.load_profile import BuiltInProfile
                                default_annual_kwh_list = []
                                doe_reference_name_list = self.input_dict['Scenario']['Site']['LoadProfile']['doe_reference_name']
                                percent_share_list = self.input_dict['Scenario']['Site']['LoadProfile']['percent_share']
                                for i in range(len(doe_reference_name_list)):
                                    self.input_dict['Scenario']['Site']['LoadProfile']['doe_reference_name'] = doe_reference_name_list[i]
                                    b = BuiltInProfile(latitude=self.input_dict['Scenario']['Site']['latitude'],longitude=self.input_dict['Scenario']['Site']['longitude'], **self.input_dict['Scenario']['Site']['LoadProfile'])
                                    default_annual_kwh_list.append(b.default_annual_kwh)
                                avg_load_kw = sum([default_annual_kwh_list[i] * percent_share_list[i] / 100 for i in range(len(default_annual_kwh_list))]) / 8760
                                # resetting the doe_reference_name key to its original list
                                # form for further processing in loadprofile.py file
                                self.input_dict['Scenario']['Site']['LoadProfile'][
                                    'doe_reference_name'] = doe_reference_name_list

                            elif self.input_dict['Scenario']['Site']['LoadProfile'].get('loads_kw') in [None,[]]:
                                from reo.src.load_profile import BuiltInProfile
                                b = BuiltInProfile(latitude=self.input_dict['Scenario']['Site']['latitude'],
                                                    longitude=self.input_dict['Scenario']['Site']['longitude'],
                                                    **self.input_dict['Scenario']['Site']['LoadProfile']
                                                    )
                                self.input_dict['Scenario']['Site']['LoadProfile']['loads_kw'] = b.built_in_profile

                                avg_load_kw = sum(self.input_dict['Scenario']['Site']['LoadProfile']['loads_kw'])\
                                                / len(self.input_dict['Scenario']['Site']['LoadProfile']['loads_kw'])

                            if avg_load_kw <= 12.5:
                                self.input_dict['Scenario']['Site']['Wind']['size_class'] = 'residential'
                            elif avg_load_kw <= 100:
                                self.input_dict['Scenario']['Site']['Wind']['size_class'] = 'commercial'
                            elif avg_load_kw <= 1000:
                                self.input_dict['Scenario']['Site']['Wind']['size_class'] = 'medium'
                            else:
                                self.input_dict['Scenario']['Site']['Wind']['size_class'] = 'large'
                        try:
                            get_conic_coords(
                                lat=self.input_dict['Scenario']['Site']['latitude'],
                                lng=self.input_dict['Scenario']['Site']['longitude'])
                        except Exception as e:
                            self.input_data_errors.append(e.args[0])

        if object_name_path[-1] == "Generator":
            if self.isValid:
                
                fuel_conversion_per_gal = {
                    'diesel_oil': 22.51
                }

                if self.input_dict['Scenario']['Site']['Generator'].get('emissions_factor_lb_CO2_per_gal') is None:
                    self.update_attribute_value(object_name_path, number, 'emissions_factor_lb_CO2_per_gal', fuel_conversion_per_gal.get('diesel_oil'))
                
                if (real_values["max_kw"] > 0 or real_values["existing_kw"] > 0):
                    # then replace zeros in default burn rate and slope, and set min/max kw values appropriately for
                    # REopt (which need to be in place before data is saved and passed on to celery tasks)
                    gen = real_values
                    m, b = Generator.default_fuel_burn_rate(gen["min_kw"] + gen["existing_kw"])
                    if gen["fuel_slope_gal_per_kwh"] == 0:
                        gen["fuel_slope_gal_per_kwh"] = m
                    if gen["fuel_intercept_gal_per_hr"] == 0:
                        gen["fuel_intercept_gal_per_hr"] = b

        if object_name_path[-1] == "LoadProfile":
            if self.isValid:
                if real_values.get('outage_start_hour') is not None and real_values.get('outage_end_hour') is not None:
                    if real_values.get('outage_start_hour') == real_values.get('outage_end_hour'):
                        self.input_data_errors.append('LoadProfile outage_start_hour and outage_end_hour cannot be the same')
                if type(real_values.get('percent_share')) in [float, int]:
                    if real_values.get('percent_share') == 100:
                        real_values['percent_share'] = [100]
                        self.update_attribute_value(object_name_path, number, 'percent_share', [100.0])
                    else:
                        self.input_data_errors.append(
                        'The percent_share input for a load profile must be be 100 or a list of numbers that sums to 100.')

                if len(real_values.get('percent_share')) > 0:
                    percent_share_sum = sum(real_values['percent_share'])
                    if percent_share_sum != 100.0:
                        self.input_data_errors.append(
                        'The sum of elements of percent share list for hybrid load profile should be 100.')

                if real_values.get('annual_kwh') is not None:
                    if type(real_values['annual_kwh']) is not list:
                        self.update_attribute_value(object_name_path, number, 'annual_kwh', [real_values['annual_kwh']])

                if real_values.get('doe_reference_name') is not None:
                    if type(real_values['doe_reference_name']) is not list:
                        self.update_attribute_value(object_name_path, number, 'doe_reference_name',[real_values['doe_reference_name']])

                    if len(real_values.get('doe_reference_name')) > 1:
                        if len(real_values.get('doe_reference_name')) != len(real_values.get('percent_share')):
                            self.input_data_errors.append(
                            'The length of doe_reference_name and percent_share lists should be equal for constructing hybrid load profile')

                if real_values.get('annual_kwh') is not None:
                    if len(real_values.get('doe_reference_name')) != len(real_values.get('annual_kwh')):
                        self.input_data_errors.append('The length of doe_reference_name and annual_kwh lists should be equal for constructing hybrid load profile')

        if object_name_path[-1] == "ElectricTariff":
            electric_tariff = real_values

            if (len(electric_tariff.get('emissions_factor_series_lb_CO2_per_kwh') or []) == 0):
                if (self.input_dict['Scenario']['Site'].get('latitude') is not None) and \
                    (self.input_dict['Scenario']['Site'].get('longitude') is not None):
                    ec = EmissionsCalculator(   latitude=self.input_dict['Scenario']['Site']['latitude'], 
                                                    longitude=self.input_dict['Scenario']['Site']['longitude'],
                                                    time_steps_per_hour = self.input_dict['Scenario']['time_steps_per_hour'])
                    emissions_series = None
                    try:
                        emissions_series = ec.emissions_series
                        emissions_region = ec.region
                    except AttributeError as e:
                        # Emissions warning is a specific type of warning that we check for and display to the users when it occurs
                        # since at this point the emissions are not required to do a run it simply
                        # tells the user why we could not get an emission series and results in emissions not being 
                        # calculated, but does not prevent the run from optimizing
                        self.emission_warning = str(e.args[0])

                    if emissions_series is not None:
                        self.update_attribute_value(object_name_path, number, 'emissions_factor_series_lb_CO2_per_kwh', 
                            emissions_series)
                        self.update_attribute_value(object_name_path, number, 'emissions_region', 
                            emissions_region)
            else:
                self.validate_8760(electric_tariff['emissions_factor_series_lb_CO2_per_kwh'], 
                    "ElectricTariff", 
                    'emissions_factor_series_lb_CO2_per_kwh', 
                    self.input_dict['Scenario']['time_steps_per_hour'])
 

            if electric_tariff.get('urdb_response') is not None:
                self.validate_urdb_response()

            elif electric_tariff.get('urdb_label','') != '':
                rate = Rate(rate=electric_tariff.get('urdb_label'))
                if rate.urdb_dict is None:
                    self.urdb_errors.append(
                        "Unable to download {} from URDB. Please check the input value for 'urdb_label'."
                        .format(electric_tariff.get('urdb_label'))
                    )
                else:
                    electric_tariff['urdb_response'] = rate.urdb_dict
                    self.validate_urdb_response()

            elif electric_tariff.get('urdb_utility_name','') != '' and electric_tariff.get('urdb_rate_name','') != '':
                rate = Rate(util=electric_tariff.get('urdb_utility_name'), rate=electric_tariff.get('urdb_rate_name'))

                if rate.urdb_dict is None:
                    self.urdb_errors.append(
                        "Unable to download {} from URDB. Please check the input values for 'urdb_utility_name' and 'urdb_rate_name'."
                        .format(electric_tariff.get('urdb_rate_name'))
                    )
                else:
                    electric_tariff['urdb_response'] = rate.urdb_dict
                    self.validate_urdb_response()

            if electric_tariff['add_blended_rates_to_urdb_rate']:
                monthly_energy = electric_tariff.get('blended_monthly_rates_us_dollars_per_kwh', True)
                monthly_demand = electric_tariff.get('blended_monthly_demand_charges_us_dollars_per_kw', True)
                urdb_rate = electric_tariff.get('urdb_response', True)

                if monthly_demand==True or monthly_energy==True or urdb_rate==True:
                    missing_keys = []
                    if monthly_demand==True:
                        missing_keys.append('blended_monthly_demand_charges_us_dollars_per_kw')
                    if monthly_energy==True:
                        missing_keys.append('blended_monthly_rates_us_dollars_per_kwh')
                    if urdb_rate==True:
                        missing_keys.append("urdb_response OR urdb_label OR urdb_utility_name and urdb_rate_name")

                    self.input_data_errors.append('add_blended_rates_to_urdb_rate is set to "true" yet missing valid entries for the following inputs: {}'.format(', '.join(missing_keys)))

            for blended in ['blended_monthly_demand_charges_us_dollars_per_kw','blended_monthly_rates_us_dollars_per_kwh']:
                if electric_tariff.get(blended) is not None:
                    if type(electric_tariff.get(blended)) is not list:
                        self.input_data_errors.append('{} needs to be an array that contains 12 valid numbers.'.format(blended) )
                    elif len(electric_tariff.get(blended)) != 12:
                        self.input_data_errors.append('{} array needs to contain 12 valid numbers.'.format(blended) )

            if electric_tariff.get('tou_energy_rates_us_dollars_per_kwh') is not None:
                self.validate_8760(electric_tariff.get('tou_energy_rates_us_dollars_per_kwh'), "ElectricTariff",
                                    'tou_energy_rates_us_dollars_per_kwh',
                                    self.input_dict['Scenario']['time_steps_per_hour'])
                if len(electric_tariff.get('tou_energy_rates_us_dollars_per_kwh')) not in [8760, 35040]:
                    self.input_data_errors.append("length of tou_energy_rates_us_dollars_per_kwh must be 8760 or 35040")
                if len(electric_tariff.get('tou_energy_rates_us_dollars_per_kwh')) == 35040 \
                    and self.input_dict['Scenario']['time_steps_per_hour'] != 4:
                    self.input_data_errors.append(("tou_energy_rates_us_dollars_per_kwh has 35040 time steps but "
                            "Scenario.time_steps_per_hour is not 4. These values must be aligned."))

            if electric_tariff['add_tou_energy_rates_to_urdb_rate']:
                tou_energy = electric_tariff.get('tou_energy_rates_us_dollars_per_kwh', True)
                urdb_rate = electric_tariff.get('urdb_response', True)

                if tou_energy is True or urdb_rate is True:
                    missing_keys = []
                    if tou_energy is True:
                        missing_keys.append('tou_energy_rates_us_dollars_per_kwh')
                    if urdb_rate is True:
                        missing_keys.append("urdb_response OR urdb_label OR urdb_utility_name and urdb_rate_name")
                    self.input_data_errors.append((
                        'add_blended_rates_to_urdb_rate is set to "true" yet missing valid entries for the '
                        'following inputs: {}').format(', '.join(missing_keys)))
            for key_name in ['wholesale_rate_us_dollars_per_kwh',
                                'wholesale_rate_above_site_load_us_dollars_per_kwh']:
                if type(electric_tariff.get(key_name)) == list:
                    ts_per_hour = self.input_dict['Scenario'].get('time_steps_per_hour') or \
                                    self.nested_input_definitions['Scenario']['time_steps_per_hour']['default']
                    if len(electric_tariff.get(key_name)) == 1:
                        self.update_attribute_value(object_name_path, number, key_name,
                                                    electric_tariff.get(key_name) * 8760 * ts_per_hour)
                    else:
                        self.validate_8760(attr=electric_tariff.get(key_name), obj_name=object_name_path[-1],
                                            attr_name=key_name,
                                            time_steps_per_hour=ts_per_hour, number=number,
                                            input_isDict=input_isDict)

        if object_name_path[-1] == "LoadProfile":
            for lp in ['critical_loads_kw', 'loads_kw']:
                if real_values.get(lp) not in [None, []]:
                    self.validate_8760(real_values.get(lp), "LoadProfile", lp, self.input_dict['Scenario']['time_steps_per_hour'])
                    isnet = real_values.get(lp + '_is_net')
                    if isnet is None:
                        isnet = True
                    if not isnet:
                        # next line can fail if non-numeric values are passed in for (critical_)loads_kw
                        if self.isValid:
                            if min(real_values.get(lp)) < 0:
                                self.input_data_errors.append("{} must contain loads greater than or equal to zero.".format(lp))

            if real_values.get('doe_reference_name') is not None:
                real_values['year'] = 2017
                # Use 2017 b/c it is most recent year that starts on a Sunday and all reference profiles start on
                # Sunday

    def check_min_max_restrictions(self, object_name_path, template_values=None, real_values=None, number=1, input_isDict=None):
        """
        comparison_function for recursively_check_input_dict.
        check all min/max constraints for input values defined in nested_input_definitions.
        create error message if user provided inputs are outside of allowable bounds.
        :param object_name_path: list of str, location of an object in self.input_dict being validated,
            eg. ["Scenario", "Site", "PV"]
        :param template_values: reference dictionary for checking real_values, for example
            {'latitude':{'type':'float',...}...}, which comes from nested_input_definitions
        :param real_values: dict, the attributes corresponding to the object at object_name_path within the
            input_dict to check and/or modify. For example, with a object_name_path of ["Scenario", "Site", "PV"]
                the real_values would look like: {'latitude': 39.345678, 'longitude': -90.3, ... }
        :param number: int, order of the dict in the list
        :param input_isDict: bool, indicates if the object input came in as a dict or list
        :return: None
        """
        if real_values is not None:
            for name, value in real_values.items():
                if self.isAttribute(name):
                    data_validators = template_values[name]

                    if "list_of_float" in data_validators['type'] and isinstance(value, list):
                        if data_validators.get('min') is not None:
                            if any([v < data_validators['min'] for v in value]):
                                if input_isDict or input_isDict is None:
                                    self.input_data_errors.append(
                                        'At least one value in %s (from %s) exceeds allowable min of %s' % (
                                            name, self.object_name_string(object_name_path), data_validators['min']))
                                if input_isDict is False:
                                    self.input_data_errors.append(
                                        'At least one value in %s (from %s number %s) exceeds allowable min of %s' % (
                                            name, self.object_name_string(object_name_path), number, data_validators['min']))

                        if data_validators.get('max') is not None:
                            if any([v > data_validators['max'] for v in value]):
                                if input_isDict or input_isDict is None:
                                    self.input_data_errors.append(
                                        'At least one value in %s (from %s) exceeds allowable max of %s' % (
                                            name, self.object_name_string(object_name_path), data_validators['max']))
                                if input_isDict is False:
                                    self.input_data_errors.append(
                                        'At least one value in %s (from %s number %s) exceeds allowable max of %s' % (
                                            name, self.object_name_string(object_name_path), number, data_validators['max']))
                        continue
                    elif "list_of_str" in data_validators['type'] and isinstance(value, list):
                        data_type = list
                    elif isinstance(data_validators['type'], list) and 'float' in data_validators['type']:
                        data_type = float
                    elif isinstance(data_validators['type'], list) and 'str' in data_validators['type']:
                        data_type = str
                    else:
                        data_type = eval(data_validators['type'])

                    try:  # to convert input value to restricted type
                        value = data_type(value)
                    except:
                        self.input_data_errors.append('Could not check min/max on %s (%s) in %s' % (
                        name, value, self.object_name_string(object_name_path)))
                    else:
                        if data_validators.get('min') is not None:
                            if value < data_validators['min']:
                                if input_isDict or input_isDict is None:
                                    self.input_data_errors.append('%s value (%s) in %s exceeds allowable min %s' % (
                                    name, value, self.object_name_string(object_name_path), data_validators['min']))
                                if input_isDict is False:
                                    self.input_data_errors.append('%s value (%s) in %s (number %s) exceeds allowable min %s' % (
                                    name, value, self.object_name_string(object_name_path), number, data_validators['min']))

                        if data_validators.get('max') is not None:
                            if value > data_validators['max']:
                                if input_isDict or input_isDict is None:
                                    self.input_data_errors.append('%s value (%s) in %s exceeds allowable max %s' % (
                                    name, value, self.object_name_string(object_name_path), data_validators['max']))
                                if input_isDict is False:
                                    self.input_data_errors.append('%s value (%s) in %s (number %s) exceeds allowable max %s' % (
                                    name, value, self.object_name_string(object_name_path), number, data_validators['max']))

                    if data_validators.get('restrict_to') is not None:
                        # Handle both cases: 1. val is of 'type' 2. List('type')
                        # Approach: Convert case 1 into case 2
                        value = [value] if not isinstance(value, list) else value
                        for val in value:
                            if val not in data_validators['restrict_to']:
                                if input_isDict == True or input_isDict == None:
                                    self.input_data_errors.append(
                                        '%s value (%s) in %s not in allowable inputs - %s' % (
                                            name, value, self.object_name_string(object_name_path),
                                            data_validators['restrict_to']))
                                if input_isDict == False:
                                    self.input_data_errors.append(
                                        '%s value (%s) in %s (number %s) exceeds allowable max %s' % (
                                            name, value, self.object_name_string(object_name_path), number,
                                            data_validators['max']))

    def convert_data_types(self, object_name_path, template_values=None, real_values=None, number=1, input_isDict=None):
        """
        comparison_function for recursively_check_input_dict.
        try to convert input values to the expected python data type, create error message if conversion fails.
        :param object_name_path: list of str, location of an object in self.input_dict being validated,
            eg. ["Scenario", "Site", "PV"]
        :param template_values: reference dictionary for checking real_values, for example
            {'latitude':{'type':'float',...}...}, which comes from nested_input_definitions
        :param real_values: dict, the attributes corresponding to the object at object_name_path within the
            input_dict to check and/or modify. For example, with a object_name_path of ["Scenario", "Site", "PV"]
                the real_values would look like: {'latitude': 39.345678, 'longitude': -90.3, ... }
        :param number: int, order of the dict in the list
        :param input_isDict: bool, indicates if the object input came in as a dict or list
        :return: None
        """
        if real_values is not None:
            for name, value in real_values.items():
                if self.isAttribute(name):
                    make_array = False
                    attribute_type = template_values[name]['type']  # attribute_type's include list_of_float
                    if isinstance(attribute_type, list) and \
                            all([x in attribute_type for x in ['float', 'list_of_float']]):
                        if isinstance(value, list):
                            try:
                                series = pd.Series(value)
                                if series.isnull().values.any():
                                    raise NotImplementedError
                                new_value = list_of_float(value)
                            except ValueError:
                                if input_isDict or input_isDict is None:
                                    self.input_data_errors.append(
                                        'Could not convert %s (%s) in %s to list of floats' % (name, value,
                                                            self.object_name_string(object_name_path))
                                    )
                                if input_isDict is False:
                                    self.input_data_errors.append(
                                        'Could not convert %s (%s) in %s (number %s) to list of floats' % (name, value,
                                                            self.object_name_string(object_name_path), number)
                                    )
                                continue  # both continue statements should be in a finally clause, ...
                            except NotImplementedError:
                                if input_isDict or input_isDict is None:
                                    self.input_data_errors.append(
                                        '%s in %s contains at least one NaN value.' % (name,
                                        self.object_name_string(object_name_path))
                                    )
                                if input_isDict is False:
                                    self.input_data_errors.append(
                                        '%s in %s (number %s) contains at least one NaN value.' % (name,
                                        self.object_name_string(object_name_path), number)
                                    )
                                continue  # both continue statements should be in a finally clause, ...
                            else:
                                self.update_attribute_value(object_name_path, number, name, new_value)
                                continue  # ... but python 2.7  does not support continue in finally clauses
                        else:
                            attribute_type = 'float'
                            make_array = True


                    if isinstance(attribute_type, list) and \
                            all([x in attribute_type for x in ['str', 'list_of_str']]):
                        if isinstance(value, list):
                            try:
                                series = pd.Series(value)
                                if series.isnull().values.any():
                                    raise NotImplementedError

                                new_value = list_of_str(value)
                            except ValueError:
                                if input_isDict or input_isDict is None:
                                    self.input_data_errors.append(
                                        'Could not convert %s (%s) in %s to list of strings' % (name, value,
                                                                                                self.object_name_string(
                                                                                                    object_name_path))
                                    )
                                if input_isDict is False:
                                    self.input_data_errors.append(
                                        'Could not convert %s (%s) in %s (number %s) to list of strings' % (
                                        name, value,
                                        self.object_name_string(object_name_path), number)
                                    )
                                continue  # both continue statements should be in a finally clause, ...
                            except NotImplementedError:
                                if input_isDict or input_isDict is None:
                                    self.input_data_errors.append(
                                        '%s in %s contains at least one NaN value.' % (name,
                                                                                        self.object_name_string(
                                                                                            object_name_path))
                                    )
                                if input_isDict is False:
                                    self.input_data_errors.append(
                                        '%s in %s (number %s) contains at least one NaN value.' % (name,
                                                                                                    self.object_name_string(
                                                                                                        object_name_path),
                                                                                                    number)
                                    )
                                continue  # both continue statements should be in a finally clause, ...
                            else:
                                self.update_attribute_value(object_name_path, number, name, new_value)
                                continue  # ... but python 2.7  does not support continue in finally clauses
                        else:
                            attribute_type = 'str'
                            make_array = True

                    attribute_type = eval(attribute_type)  # convert string to python type
                    try:  # to convert input value to type defined in nested_input_definitions
                        new_value = attribute_type(value)
                    except:  # if fails for any reason record that the conversion failed
                        if input_isDict or input_isDict is None:
                            self.input_data_errors.append('Could not convert %s (%s) in %s to %s' % (name, value,
                                        self.object_name_string(object_name_path), str(attribute_type).split(' ')[1]))
                        if input_isDict is False:
                            self.input_data_errors.append('Could not convert %s (%s) in %s (number %s) to %s' % (name, value,
                                        self.object_name_string(object_name_path), number , str(attribute_type).split(' ')[1]))
                    else:
                        if not isinstance(new_value, bool):
                            if make_array:
                                new_value = [new_value]
                            self.update_attribute_value(object_name_path, number, name, new_value)
                        else:
                            if value not in [True, False, 1, 0]:
                                if input_isDict or input_isDict is None:
                                    self.input_data_errors.append('Could not convert %s (%s) in %s to %s' % (
                                    name, value, self.object_name_string(object_name_path),
                                    str(attribute_type).split(' ')[1]))
                                if input_isDict is False:
                                    self.input_data_errors.append('Could not convert %s (%s) in %s (number %s) to %s' % (
                                    name, value, self.object_name_string(object_name_path), number,
                                    str(attribute_type).split(' ')[1]))


    def fillin_defaults(self, object_name_path, template_values=None, real_values=None,  number=1, input_isDict=None):
        """
        comparison_function for recursively_check_input_dict.
        fills in default values for inputs that user does not provide.
        :param object_name_path: list of str, location of an object in self.input_dict being validated,
            eg. ["Scenario", "Site", "PV"]
        :param template_values: reference dictionary for checking real_values, for example
            {'latitude':{'type':'float',...}...}, which comes from nested_input_definitions
        :param real_values: dict, the attributes corresponding to the object at object_name_path within the
            input_dict to check and/or modify. For example, with a object_name_path of ["Scenario", "Site", "PV"]
                the real_values would look like: {'latitude': 39.345678, 'longitude': -90.3, ... }
        :param number: int, order of the dict in the list
        :param input_isDict: bool, indicates if the object input came in as a dict or list
        :return: None
        """
        if real_values is None:
            real_values = {}
            self.update_attribute_value(object_name_path[:-1], number, object_name_path[-1], real_values)

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
                    if isinstance(template_value.get('type'), list) and "list_of_float" in template_value.get('type'):
                        # then input can be float or list_of_float, but for database we have to use only one type
                        default = [default]
                    self.update_attribute_value(object_name_path, number, template_key, default)
                    if input_isDict or input_isDict is None:
                        self.defaults_inserted.append([template_key, object_name_path])
                    if input_isDict is False:
                        object_name_path[-1] = object_name_path[-1] + ' (number {})'.format(number)
                        self.defaults_inserted.append([template_key, object_name_path])
            if self.isSingularKey(template_key):
                if template_key not in real_values.keys():
                    self.update_attribute_value(object_name_path, number, template_key, {})
                    if input_isDict or input_isDict is None:
                        self.defaults_inserted.append([template_key, object_name_path])
                    if input_isDict is False:
                        object_name_path[-1] = object_name_path[-1] + ' (number {})'.format(number)
                        self.defaults_inserted.append([template_key, object_name_path])

    def check_required_attributes(self, object_name_path, template_values=None, real_values=None,  number=1, input_isDict=None):
        """
        comparison_function for recursively_check_input_dict.
        confirm that required inputs were provided by user. If not, create message to provide to user.
        :param object_name_path: list of str, location of an object in self.input_dict being validated,
            eg. ["Scenario", "Site", "PV"]
        :param template_values: reference dictionary for checking real_values, for example
            {'latitude':{'type':'float',...}...}, which comes from nested_input_definitions
        :param real_values: dict, the attributes corresponding to the object at object_name_path within the
            input_dict to check and/or modify. For example, with a object_name_path of ["Scenario", "Site", "PV"]
                the real_values would look like: {'latitude': 39.345678, 'longitude': -90.3, ... }
        :param number: int, order of the dict in the list
        :param input_isDict: bool, indicates if the object input came in as a dict or list
        :return: None
        """
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
            if input_isDict or input_isDict is None:
                self.input_data_errors.append('Missing Required for %s: %s' % (self.object_name_string(object_name_path), final_message))
            if input_isDict is False:
                self.input_data_errors.append('Missing Required for %s (number %s): %s' % (self.object_name_string(object_name_path), number,  final_message))

    def validate_urdb_response(self, number=1):
        urdb_response = self.input_dict['Scenario']['Site']['ElectricTariff'].get('urdb_response')

        if type(urdb_response) == dict:
            if self.input_dict['Scenario']['Site']['ElectricTariff'].get('urdb_utility_name') is None:
                self.update_attribute_value(["Scenario", "Site", "ElectricTariff"], number, 'urdb_utility_name', urdb_response.get('utility'))

            if self.input_dict['Scenario']['Site']['ElectricTariff'].get('urdb_rate_name') is None:
                self.update_attribute_value(["Scenario", "Site", "ElectricTariff"], number,  'urdb_rate_name', urdb_response.get('name'))

            try:
                rate_checker = URDB_RateValidator(**urdb_response)
                if rate_checker.errors:
                    self.urdb_errors.append(rate_checker.errors)
            except:
                self.urdb_errors.append('Error parsing urdb rate in %s ' % (["Scenario", "Site", "ElectricTariff"]))

    def validate_8760(self, attr, obj_name, attr_name, time_steps_per_hour, number=1, input_isDict=None):
        """
        This method is for the case that a user uploads a time-series that has either 30 minute or 15 minute
        resolution, but wants to run an hourly REopt model. If time_steps_per_hour = 1 then we downsample the user's
        time-series to an 8760. If time_steps_per_hour != 1 then we do nothing since the resolution of time-series
        relative to time_steps_per_hour is handled within each time-series' implementation.
        :param attr: list of floats
        :param obj_name: str, parent object name from nested_inputs (eg. "LoadProfile")
        :param attr_name: str, name of time-series (eg. "critical_loads_kw")
        :param time_steps_per_hour: int, [1, 2, 4]
        :param number: int, order of the dict in the list
        :param input_isDict: bool, indicates if the object input came in as a dict or list
        :return: None
        """
        n = len(attr)
        length_list = [8760, 17520, 35040]

        if time_steps_per_hour != 1:
            if n not in length_list:
                self.input_data_errors.append((
                    "Invalid length for {}. Samples must be hourly (8,760 samples), 30 minute (17,520 samples), "
                    "or 15 minute (35,040 samples)").format(attr_name)
                )
            elif attr_name in ["wholesale_rate_us_dollars_per_kwh", "wholesale_rate_above_site_load_us_dollars_per_kwh"]:
                if time_steps_per_hour != n/8760:
                    if time_steps_per_hour == 2 and n/8760 == 4:
                        if input_isDict or input_isDict is None:
                            self.resampled_inputs.append(
                                ["Downsampled {} from 15 minute resolution to 30 minute resolution to match time_steps_per_hour via average.".format(attr_name), [obj_name]])
                        if input_isDict is False:
                            self.resampled_inputs.append(
                                ["Downsampled {} from 15 minute resolution to 30 minute resolution to match time_steps_per_hour via average.".format(attr_name), [obj_name + ' (number %s)'.format(number)]])
                        index = pd.date_range('1/1/2000', periods=n, freq='15T')
                        series = pd.Series(attr, index=index)
                        series = series.resample('30T').mean()
                        resampled_val = series.tolist()
                    elif time_steps_per_hour == 4 and n/8760 == 2:
                        if input_isDict or input_isDict is None:
                            self.resampled_inputs.append(
                                ["Upsampled {} from 30 minute resolution to 15 minute resolution to match time_steps_per_hour via forward-fill.".format(attr_name), [obj_name]])
                        if input_isDict is False:
                            self.resampled_inputs.append(
                                ["Upsampled {} from 30 minute resolution to 15 minute resolution to match time_steps_per_hour via forward-fill.".format(attr_name), [obj_name + ' (number %s)'.format(number)]])

                        resampled_val = [x for x in attr for _ in [1, 2]]
                    elif time_steps_per_hour == 4 and n/8760 == 1:
                        if input_isDict or input_isDict is None:
                            self.resampled_inputs.append(
                                ["Upsampled {} from hourly resolution to 15 minute resolution to match time_steps_per_hour via forward-fill.".format(attr_name), [obj_name]])
                        if input_isDict is False:
                            self.resampled_inputs.append(
                                ["Upsampled {} from hourly resolution to 15 minute resolution to match time_steps_per_hour via forward-fill.".format(attr_name), [obj_name + ' (number %s)'.format(number)]])

                        resampled_val = [x for x in attr for _ in [1, 2, 3, 4]]
                    else:  # time_steps_per_hour == 2 and n/8760 == 1:
                        if input_isDict or input_isDict is None:
                            self.resampled_inputs.append(
                                ["Upsampled {} from hourly resolution to 30 minute resolution to match time_steps_per_hour via forward-fill.".format(attr_name), [obj_name]])
                        if input_isDict is False:
                            self.resampled_inputs.append(
                                ["Upsampled {} from hourly resolution to 30 minute resolution to match time_steps_per_hour via forward-fill.".format(attr_name), [obj_name + ' (number %s)'.format(number)]])

                        resampled_val = [x for x in attr for _ in [1, 2]]
                    self.update_attribute_value(["Scenario", "Site", obj_name], number, attr_name, resampled_val)

        elif n == 8760:
            pass  # because n/8760 == time_steps_per_hour ( = 1 )

        elif n in [17520, 35040]:
            resolution_minutes = int(60/(n/8760))
            if input_isDict or input_isDict is None:
                self.resampled_inputs.append(
                    ["Downsampled {} from {} minute resolution to hourly resolution to match time_steps_per_hour via average.".format(
                        attr_name, resolution_minutes), [obj_name]])
            if input_isDict is False:
                self.resampled_inputs.append(
                    ["Downsampled {} from {} minute resolution to hourly resolution to match time_steps_per_hour via average.".format(
                        attr_name, resolution_minutes), [obj_name + ' (number {})'.format(number)]])

            index = pd.date_range('1/1/2000', periods=n, freq='{}T'.format(resolution_minutes))
            series = pd.Series(attr, index=index)
            series = series.resample('1H').mean()
            self.update_attribute_value(["Scenario", "Site", obj_name], number, attr_name, series.tolist())
        else:
            if input_isDict or input_isDict is None:
                self.input_data_errors.append("Invalid length for {}. Samples must be hourly (8,760 samples), 30 minute (17,520 samples), or 15 minute (35,040 samples)".format(attr_name))
            if input_isDict is False:
                self.input_data_errors.append("Invalid length for {}. Samples must be hourly (8,760 samples), 30 minute (17,520 samples), or 15 minute (35,040 samples)".format(attr_name + ' (number {})'.format(number)))

    def validate_text_fields(self, pattern=r'^[-0-9a-zA-Z  $:;)(*&#!@]*$', str="", err_msg=""):
        match = re.search(pattern, str)
        if match:
            pass
        else:
            self.input_data_errors.append(err_msg)

    def validate_user_uuid(self, user_uuid="", err_msg=""):
        try:
            uuid.UUID(user_uuid)  # raises ValueError if not valid uuid
        except:
            self.input_data_errors.append(err_msg)
