from tastypie.validation import Validation
from api_definitions import *
from api_input_validation import *

class REoptResourceValidation(Validation):
    def is_valid(self, bundle, request=None):

        errors = {}

        missing_required = self.missing_required(bundle.data.keys())

        if missing_required:
            message = [self.get_missing_required_message(m) for  m in missing_required]
            errors = self.append_errors(errors,"Missing_Required",message)

        missing_dependencies = self.missing_dependencies(bundle.data.keys(),exclude=missing_required)
        if missing_dependencies:
            message = [self.get_missing_dependency_message(m) for m in missing_dependencies]
            errors = self.append_errors(errors, "Missing_Dependencies", message)

        for key, value in bundle.data.items():
            if key not in inputs(full_list=True):
                errors = self.append_errors(errors, key, 'This key name does not match a valid input.')
            else:
                field_def = inputs(full_list=True)[key]
                format_errors =  self.check_input_format(key,value,field_def)

                if not format_errors:

                    if field_def.get('max'):
                        format_errors += self.check_min(key, value, field_def)

                    if field_def.get('min'):
                        format_errors += self.check_max(key, value, field_def)

                    if field_def.get('restrict_to'):
                        format_errors += self.check_restrict_to(key, value, field_def['restrict_to'])

                #specific_errors =
                if format_errors:
                    errors = self.append_errors(errors, key, format_errors)

        return errors

    def check_input_format(self,key,value,field_definition):
        try:
            new_value = field_definition['type'](value)
            if value != new_value:
                return ['Invalid format: Expected %s, got %s'%(field_definition['type'], type(value))]

            if not field_definition['null']:
                if value in [None,'null']:
                    return ['Invalid format: Input cannot be null']

            return []
        except Exception as e:
            return ['Invalid format: Expected %s, got %s'%(field_definition['type'], type(value))]

    def check_min(self, key, value, fd):
        if bool(fd.get('pct')):
            if value > 1:
                value = value*0.01

        if value < fd['min']:
            if not fd.get('pct'):
                return ['Invalid value: %s is less than the minimum, %s' % (value, max)]
            else:
                return ['Invalid value: %s is less than the minimum, %s %%' % (value, max * 100)]
        return []

    def check_max(self, key, value, fd):
        if bool(fd.get('pct')):
            if value > 1:
                value = value * 0.01

        if value > fd['max']:
            if not fd.get('pct'):
                return ['Invalid value: %s is greater than the  maximum, %s' % (value, max)]
            else:
                return ['Invalid value: %s is greater than the  maximum, %s %%' % (value, max*100)]
        return []

    def check_restrict_to(self,key, value, range):
        if value not in range:
            return ['Invalid value: %s is not in %s' % (value, range)]
        return []

    def append_errors(self, errors, key, value):
        if 'Error:' in errors.keys():
            if key not in errors["Error:"].keys():
                errors["Error:"][key] = value
            else:
                errors["Error:"][key] += value
        else:
            errors['Error:']  =  {key: value}
        return errors

    def get_missing_required_message(self, input):
        definition_values = inputs(full_list=True)[input]
        swap = definition_values.get('swap_for')

        message = input
        if swap is not None:
            message +=  " (OR %s)" % (" and ".join(definition_values['swap_for']))
        return message

    def get_missing_dependency_message(self, input):
        definition_values = inputs(full_list=True)[input]

        dependency_of = []
        for k, v in inputs(full_list=True).items():
            value = v.get('depends_on')
            if value is not None:
                if input in value:
                    dependency_of.append(k)
        return "%s (%s depend(s) on  this input.)" % (input, "  and ".join(dependency_of))

    def missing_dependencies(self, key_list,exclude=[]):
        # Check if field depends on non-required fields
        missing = []
        for f in inputs(full_list=True).keys():

            if not self.swaps_exists(key_list,f):
                dependent = inputs(full_list=True)[f].get('depends_on')
                if dependent is not None and f  not in exclude:
                    for d in dependent:
                        if d not in key_list:
                            missing.append(d)
        return missing

    def swaps_exists(self,key_list, f):
        swap = inputs(full_list=True)[f].get('swap_for')
        swap_exists = False
        if swap is not None:
            swap_exists = True
            for ff in swap:
                if ff not in key_list:
                    swap_exists = False
        return swap_exists

    def missing_required(self,key_list):
        missing =  list(set(inputs(just_required=True)) - set(key_list))
        output =[]
        for  field  in  missing:
            #Check if field can  be  swappedout  for others
            if not self.swaps_exists(key_list,field):
                output.append(field)
        return output
