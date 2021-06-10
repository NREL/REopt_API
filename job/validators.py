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
import logging
from job.models import Scenario, SiteInputs, OptimizationInputs, LoadProfileInputs, ElectricTariffInputs, \
    FinancialInputs, BaseModel
from django.core.exceptions import ValidationError
log = logging.getLogger(__name__)


def scrub_fields(obj: BaseModel, raw_fields: dict):
    valid_fields = [f.name for f in obj._meta.fields[2:]]
    types = [str(type(f)) for f in obj._meta.fields[2:]]
    types_dict = {k: v for k, v in zip(valid_fields, types)}

    scrubbed_dict = dict()
    for k, v in raw_fields.items():
        if k in valid_fields:
            scrubbed_dict[k] = v
            if "ArrayField" in types_dict[k] and not isinstance(v, list):
                scrubbed_dict[k] = [v]
    return scrubbed_dict


class InputValidator(object):

    def __init__(self, raw_inputs: dict, run_uuid: str):
        """
        Validate user inputs
        Used in job/api.py to:
        1. Clean each Model's individual fields, which checks:
            - required inputs provided
            - inputs have correct types
            - inputs within min/max limits
            - fills in default values
        2. Check requirements across each Model's fields
            - eg. if user provides outage_start_time_step then must also provide outage_start_end_step
        3. Check requirements across Model fields
            - eg. the time_steps_per_hour must align with the length of loads_kw
        """
        self.validation_errors = []
        self.models = []
        self.objects = (
            Scenario,
            SiteInputs,
            OptimizationInputs,
            LoadProfileInputs,
            ElectricTariffInputs,
            FinancialInputs
        )
        
        scrubbed_inputs = dict()
        for obj in self.objects:
            if obj.name in raw_inputs.keys():

                scrubbed_inputs[obj.name] = scrub_fields(obj, raw_inputs[obj.name])

                self.models.append(
                    obj.create(run_uuid=run_uuid, **scrubbed_inputs[obj.name])
                )
            else:
                # THIS WILL ONLY WORK IF MODEL HAS DEFAULTS FOR ALL REQUIRED FIELDS?
                self.models.append(
                    obj.create(run_uuid=run_uuid)
                )
        self.scrubbed_inputs = scrubbed_inputs

    def clean_fields(self):
        """
        Run all models' clean_fields methods
        :return: None
        """
        for model in self.models:
            try:
                model.clean_fields()
            except ValidationError as ve:
                self.validation_errors.append(
                    {model.name: ve.message_dict}
                )

    def clean(self):
        """
        Run all models' clean methods
        :return: None
        """
        for model in self.models:
            try:
                model.clean()
            except ValidationError as ve:
                self.validation_errors.append(
                    {model.name: ve.message_dict}
                )

    def cross_clean(self):
        """
        Validation that requires comparing fields from more than one model
        :return: None
        """
        pass

    def save(self):
        """
        Save all values to database
        :return: None
        """
        for model in self.models:
            model.save()

    @property
    def is_valid(self):
        if self.validation_errors:
            return False
        return True

    @property
    def dict(self):
        d = dict()
        for model in self.models:
            d[model.name] = model.dict
        return d