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
import pandas as pd
from job.models import Scenario, SiteInputs, Settings, ElectricLoadInputs, ElectricTariffInputs, \
    FinancialInputs, BaseModel, Message
from django.core.exceptions import ValidationError
log = logging.getLogger(__name__)


def scrub_fields(obj: BaseModel, raw_fields: dict):
    valid_fields = [f.name for f in obj._meta.fields[1:]]
    types = [str(type(f)) for f in obj._meta.fields[1:]]
    types_dict = {k: v for k, v in zip(valid_fields, types)}

    scrubbed_dict = dict()
    for k, v in raw_fields.items():
        if k in valid_fields:
            scrubbed_dict[k] = v
            if "ArrayField" in types_dict[k] and not isinstance(v, list):
                scrubbed_dict[k] = [v]
    return scrubbed_dict


class InputValidator(object):

    def __init__(self, raw_inputs: dict):
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
        # TODO figure out how to align with MessagesModel from v1 with validation errors, resampling messages, etc.
        self.validation_errors = dict()
        self.resampling_messages = dict()
        self.models = dict()
        self.objects = (
            Scenario,
            SiteInputs,
            Settings,
            ElectricLoadInputs,
            ElectricTariffInputs,
            FinancialInputs
        )
        
        scrubbed_inputs = dict()
        scrubbed_inputs[Scenario.name] = scrub_fields(Scenario, raw_inputs[Scenario.name])
        scenario = Scenario.create(**scrubbed_inputs[Scenario.name])
        self.models[Scenario.name] = scenario
        scenario.save()  # must save the Scenario first to use it as a OneToOneField in other models

        for obj in self.objects:
            if obj == Scenario: continue
            if obj.name in raw_inputs.keys():

                scrubbed_inputs[obj.name] = scrub_fields(obj, raw_inputs[obj.name])

                self.models[obj.name] = obj.create(scenario=scenario, **scrubbed_inputs[obj.name])
            else:
                # THIS WILL ONLY WORK IF MODEL HAS DEFAULTS FOR ALL REQUIRED FIELDS?
                self.models[obj.name] = obj.create(scenario=scenario)

        self.scrubbed_inputs = scrubbed_inputs

    @property
    def messages(self):
        """
        Warnings to be passed to the user from the results endpoint (in the "messages").
        NOTE: no need for including errors here since we do not create a Scenario when there are errors.
            The errors are returned to the user in job/api.py
        :return: dict with str keys and values, which are saved in the Message model for each Scenario
        """
        msg_dict = dict()

        if self.resampling_messages:
            msg_dict["resampled inputs"] = self.resampling_messages

        return msg_dict

    def clean_fields(self):
        """
        Run all models' clean_fields methods
        :return: None
        """
        for model in self.models.values():
            try:
                model.clean_fields()
            except ValidationError as ve:
                self.validation_errors[model.name] = ve.message_dict

    def clean(self):
        """
        Run all models' clean methods
        :return: None
        """
        for model in self.models.values():
            try:
                model.clean()
            except ValidationError as ve:
                self.validation_errors[model.name] = ve.message_dict

    def cross_clean(self):
        """
        Validation that requires comparing fields from more than one model
        :return: None
        """

        """
        Time series values are up or down sampled to align with Settings.time_steps_per_hour
        """
        for key, time_series in zip(
            ["ElectricLoad", "ElectricLoad"],
            ["loads_kw",      "critical_loads_kw"]
        ):
            if len(self.models[key].__getattribute__(time_series)) > 0:
                resampled_series, resampling_msg, err_msg = validate_time_series(
                    self.models[key].__getattribute__(time_series), self.models["Settings"].time_steps_per_hour
                )
                if resampling_msg:
                    self.models[key].__setattr__(time_series, resampled_series)
                    self.resampling_messages[key] = {time_series: resampling_msg}
                if err_msg:
                    if key not in self.validation_errors.keys():
                        self.validation_errors[key] = {time_series: err_msg}
                    else:
                        self.validation_errors[key].update({time_series: err_msg})

    def save(self):
        """
        Save all values to database
        :return: None
        """
        for model in self.models.values():
            model.save()
        for msg_type, msg in self.messages.items():
            msg_model = Message.create(scenario=self.models["Scenario"], message_type=msg_type, message=msg)
            msg_model.save()

    @property
    def is_valid(self):
        if self.validation_errors:
            return False
        return True

    @property
    def dict(self):
        d = dict()
        for model in self.models.values:
            d[model.name] = model.dict
        return d


def validate_time_series(series: list, time_steps_per_hour: int) -> (list, str, str):
    """
    Used to check that an input time series has hourly, 30 minute, or 15 minute resolution and if the time series
    resolution matches the time_steps_per_hour (one of [1,2,4]).
    Time series that do not match the time_steps_per_hour are up- or down-sampled to match the time_steps_per_hour.
    Note that this is different from the v1 validate_8760 method, which only down-sampled and left it to each object
    (such as the LoadProfileBoilerFuel) to up-sample.
    This method is used in job/models.py, in models with time series values when their clean methods are called.
    :param series: list of floats
    :param time_steps_per_hour: int, one of [1,2,4]
    :return: (list, str, str) for the resampled series (if necessary) and the resampling message and exception
        respectively. Either message can be empty, i.e. "". For example, "" if no exception, o.w. an error message to
        append to the InputValidator.validation_errors.
    TODO: add resampling messages to messages returned to user
    TODO: does the resampling here match what is done in each of the time-series objects in v1?
    """
    n = len(series)
    length_list = [8760, 17520, 35040]
    if n not in length_list:
        return (series, "",
            (f"Invalid length. Samples must be hourly (8,760 samples), 30 minute (17,520 samples), "
             "or 15 minute (35,040 samples)"))
    
    time_steps_per_hour_in_series = n / 8760
    if time_steps_per_hour_in_series == time_steps_per_hour:
        return series, "", ""

    if time_steps_per_hour < time_steps_per_hour_in_series:
        resampling_msg = f"Downsampled to match time_steps_per_hour via average."
        index = pd.date_range('1/1/2000', periods=n, freq=f'{int(60/time_steps_per_hour_in_series)}T')
        s = pd.Series(series, index=index)
        s = s.resample(f'{int(60/time_steps_per_hour)}T').mean()
        return s.tolist(), resampling_msg, ""
    
    # time_steps_per_hour > time_steps_per_hour_in_series
    resampling_msg = f"Upsampled to match time_steps_per_hour via forward-fill."
    resampled_val = [x for x in series for _ in range(int(time_steps_per_hour/time_steps_per_hour_in_series))]
    return resampled_val, resampling_msg, ""
