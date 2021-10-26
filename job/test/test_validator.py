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
import json
import os
import copy
import uuid
from django.test import TestCase
from job.validators import InputValidator


class InputValidatorTests(TestCase):

    def setUp(self):
        post_file = os.path.join('job', 'test', 'posts', 'validator_post.json')
        self.post = json.load(open(post_file, 'r'))

    def test_elec_load_profile_length_validation_and_resampling(self):
        """
        try different lengths of load profiles, where the following are valid:
        - 8760 (hourly)
        - 17520 (30 min)
        - 35040 (15 min)
        also confirm that up/down-sampling is working.
        :return: None
        """
        good_lengths = [8760, 17520, 35040]
        bad_lengths = [8759, 17521]

        for length in bad_lengths + good_lengths:
            post = copy.deepcopy(self.post)
            post["APIMeta"]["run_uuid"] = uuid.uuid4()
            post['ElectricLoad']['loads_kw'] = list(range(length))
            post['ElectricLoad']['critical_loads_kw'] = list(range(length))
            validator = InputValidator(post)
            validator.clean()
            validator.clean_fields()
            validator.cross_clean()

            if length in good_lengths:
                self.assertEquals(validator.is_valid, True)

                if length > 8760:  # check downsampling
                    self.assertEquals(len(validator.models["ElectricLoad"].loads_kw), 8760)
                    self.assertEquals(len(validator.models["ElectricLoad"].critical_loads_kw), 8760)
                    assert("resampled inputs" in validator.messages)

            elif length in bad_lengths:
                self.assertEquals(validator.is_valid, False)
                assert('Invalid length' in validator.validation_errors['ElectricLoad']['loads_kw'])
                assert('Invalid length' in validator.validation_errors['ElectricLoad']['critical_loads_kw'])

        # check upsampling
        for time_steps_per_hour in [2, 4]:
            post = copy.deepcopy(self.post)
            post["APIMeta"]["run_uuid"] = uuid.uuid4()
            post['ElectricLoad']['loads_kw'] = list(range(8760))
            post['ElectricLoad']['critical_loads_kw'] = list(range(8760))
            post['Settings']['time_steps_per_hour'] = time_steps_per_hour
            validator = InputValidator(post)
            validator.clean()
            validator.clean_fields()
            validator.cross_clean()
            self.assertEquals(validator.is_valid, True)
            self.assertEquals(len(validator.models["ElectricLoad"].loads_kw), time_steps_per_hour*8760)
            self.assertEquals(len(validator.models["ElectricLoad"].critical_loads_kw), time_steps_per_hour*8760)

    def test_bad_blended_profile_inputs(self):
        post = copy.deepcopy(self.post)
        del(post["ElectricLoad"]["doe_reference_name"])
        post["ElectricLoad"]["blended_doe_reference_names"] = ["badname", "LargeOffice"]
        post["ElectricLoad"]["blended_doe_reference_percents"] = [1.5]
        validator = InputValidator(post)
        validator.clean_fields()

        assert("'badname' is not a valid choice"
               in validator.validation_errors['ElectricLoad']['blended_doe_reference_names'][0])
        assert("Ensure this value is less than or equal to 1.0" in
               validator.validation_errors['ElectricLoad']['blended_doe_reference_percents'][0])

        post["ElectricLoad"]["blended_doe_reference_names"] = ["MediumOffice", "LargeOffice"]
        post["ElectricLoad"]["blended_doe_reference_percents"] = [0.5]
        post["APIMeta"]["run_uuid"] = uuid.uuid4()
        validator = InputValidator(post)
        validator.clean_fields()
        validator.clean()

        assert("The number of blended_doe_reference_names must equal the number of blended_doe_reference_percents" in
               validator.validation_errors['ElectricLoad']['blended_doe_reference_names'][0])
        assert("Sum must = 1.0." in
               validator.validation_errors['ElectricLoad']['blended_doe_reference_percents'][0])
