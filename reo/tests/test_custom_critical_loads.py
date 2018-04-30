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

    def test_different_critical_load_profiles(self):
        """
        try different lengths of critical load profiles, where the following are valid (longer than outage period):
        - 490 ( minimum required length for outage period )
        - 500
        - 8760
        :return: None
        """
        good_lengths = [490, 500, 8760]
        bad_lengths = [250, 489]

        for length in bad_lengths + good_lengths:
            self.post['Scenario']['Site']['LoadProfile']['critical_loads_kw'] = list(range(length))
            validator = self.get_validator(self.post)

            if length in good_lengths:
                self.assertEquals(validator.isValid, True)

            elif length in bad_lengths:
                self.assertEquals(validator.isValid, False)
                assert(any('Invalid length for critical_loads_kw' in e for e in validator.errors['input_errors']))
