import json
import os
from django.test import TestCase
from reo.validators import ValidateNestedInput


class InputValidatorTests(TestCase):

    def setUp(self):
        post_file = os.path.join('reo', 'tests', 'nestedPOST.json')
        self.post = json.load(open(post_file, 'r'))

    @staticmethod
    def get_validator(post):
        validator = ValidateNestedInput(post)
        return validator

    def test_different_load_profiles(self):
        """
        try different lengths of load profiles, where the following are valid:
        - 8760 (hourly)
        - 17520 (30 min)
        - 35040 (15 min)
        also confirm that down-sampling is working (15 and 30 minute data are converted to hourly).
        :return: None
        """
        good_lengths = [8760, 17520, 35040]
        bad_lengths = [8759, 17521]

        for length in bad_lengths + good_lengths:
            self.post['Scenario']['Site']['LoadProfile']['loads_kw'] = list(range(length))
            validator = self.get_validator(self.post)

            if length in good_lengths:
                self.assertEquals(validator.isValid, True)
                # check downsampling
                if length > 8760:
                    self.assertEquals(
                        len(validator.input_dict['Scenario']['Site']['LoadProfile']['loads_kw']),
                        8760
                    )

            elif length in bad_lengths:
                self.assertEquals(validator.isValid, False)
                assert(any('Invalid length for loads_kw' in e for e in validator.errors['input_errors']))

    def test_different_critical_load_profiles(self):
        """
        try different lengths of critical load profiles, where the following are valid:
        - 8760 (hourly)
        - 17520 (30 min)
        - 35040 (15 min)
        also confirm that down-sampling is working (15 and 30 minute data are converted to hourly).
        :return: None
        """
        good_lengths = [8760, 17520, 35040]
        bad_lengths = [8759, 17521]

        for length in bad_lengths + good_lengths:
            self.post['Scenario']['Site']['LoadProfile']['critical_loads_kw'] = list(range(length))
            validator = self.get_validator(self.post)

            if length in good_lengths:
                self.assertEquals(validator.isValid, True)
                # check downsampling
                if length > 8760:
                    self.assertEquals(
                        len(validator.input_dict['Scenario']['Site']['LoadProfile']['critical_loads_kw']),
                        8760
                    )

            elif length in bad_lengths:
                self.assertEquals(validator.isValid, False)
                assert(any('Invalid length for critical_loads_kw' in e for e in validator.errors['input_errors']))
