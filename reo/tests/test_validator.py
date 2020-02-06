import json
import os
import copy
from django.test import TestCase
from reo.validators import ValidateNestedInput


class InputValidatorTests(TestCase):

    def setUp(self):
        post_file = os.path.join('reo', 'tests', 'posts', 'nestedPOST.json')
        self.post = json.load(open(post_file, 'r'))


    @staticmethod
    def get_validator(post):
        validator = ValidateNestedInput(post)
        return validator

    def test_add_blended_to_urdb(self):
        """
        try setting the add blended to urdb rate without sufficient input
        also confirm that blended fields must be 12 entries long each
        :return: None
        """

        self.post['Scenario']['Site']['ElectricTariff']['add_blended_rates_to_urdb_rate'] = True
        self.post['Scenario']['Site']['ElectricTariff']['blended_monthly_rates_us_dollars_per_kwh'] = None
        self.post['Scenario']['Site']['ElectricTariff']['blended_monthly_demand_charges_us_dollars_per_kw'] = None
        validator = self.get_validator(self.post)
        assert(any("add_blended_rates_to_urdb_rate is set to \'true\' yet missing valid entries for the following inputs: " in e for e in validator.errors['input_errors']))

        self.post['Scenario']['Site']['ElectricTariff']['add_blended_rates_to_urdb_rate'] = True
        self.post['Scenario']['Site']['ElectricTariff']['blended_monthly_rates_us_dollars_per_kwh'] = [0]*12
        self.post['Scenario']['Site']['ElectricTariff']['blended_monthly_demand_charges_us_dollars_per_kw'] = None
        validator = self.get_validator(self.post)
        assert(any("add_blended_rates_to_urdb_rate is set to \'true\' yet missing valid entries for the following inputs: " in e for e in validator.errors['input_errors']))

        self.post['Scenario']['Site']['ElectricTariff']['add_blended_rates_to_urdb_rate'] = True
        self.post['Scenario']['Site']['ElectricTariff']['blended_monthly_rates_us_dollars_per_kwh'] = None
        self.post['Scenario']['Site']['ElectricTariff']['blended_monthly_demand_charges_us_dollars_per_kw'] = [0]*12
        validator = self.get_validator(self.post)
        assert(any("add_blended_rates_to_urdb_rate is set to \'true\' yet missing valid entries for the following inputs: " in e for e in validator.errors['input_errors']))

        self.post['Scenario']['Site']['ElectricTariff']['add_blended_rates_to_urdb_rate'] = True
        self.post['Scenario']['Site']['ElectricTariff']['blended_monthly_rates_us_dollars_per_kwh'] = [0]*12
        self.post['Scenario']['Site']['ElectricTariff']['blended_monthly_demand_charges_us_dollars_per_kw'] = [0]*5
        validator = self.get_validator(self.post)
        assert(any("array needs to contain 12 valid numbers." in e for e in validator.errors['input_errors']))

        self.post['Scenario']['Site']['ElectricTariff']['add_blended_rates_to_urdb_rate'] = True
        self.post['Scenario']['Site']['ElectricTariff']['blended_monthly_rates_us_dollars_per_kwh'] = [0]*5
        self.post['Scenario']['Site']['ElectricTariff']['blended_monthly_demand_charges_us_dollars_per_kw'] = [0]*12
        validator = self.get_validator(self.post)
        assert(any("array needs to contain 12 valid numbers." in e for e in validator.errors['input_errors']))

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
            post = copy.deepcopy(self.post)
            post['Scenario']['Site']['LoadProfile']['loads_kw'] = list(range(length))
            validator = self.get_validator(post)

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
            post = copy.deepcopy(self.post)
            post['Scenario']['Site']['LoadProfile']['critical_loads_kw'] = list(range(length))
            validator = self.get_validator(post)

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

    def test_warnings_for_mismatch_of_time_steps_per_hour_and_resolution_of_time_of_export_rate(self):
        post = copy.deepcopy(self.post)
        rates = ["wholesale_rate_us_dollars_per_kwh", "wholesale_rate_above_site_load_us_dollars_per_kwh"]
        for time_steps_per_hour in [1, 2, 4]:
            post["Scenario"]["time_steps_per_hour"] = time_steps_per_hour
            for resolution in [1, 2, 4]:
                if time_steps_per_hour == resolution:
                    continue
                for rate in rates:
                    post["Scenario"]["Site"]["ElectricTariff"][rate] = [1.1] * 8760 * resolution
                validator = self.get_validator(post)
                self.assertEquals(validator.isValid, True)
                up_or_down = "Upsampled"
                if resolution > time_steps_per_hour:
                    up_or_down = "Downsampled"
                self.assertTrue(all(
                    test_str in validator.warnings['Following inputs were resampled:']['ElectricTariff']
                    for test_str in ["{} {}".format(up_or_down, rate) for rate in rates]
                ))
