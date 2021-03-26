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
from django.db import models
import copy
import logging
from reo.models import ScenarioModel

log = logging.getLogger(__name__)


def at_least_one_set(model, possible_sets):
    case = False
    for list_of_keys in possible_sets:
        if all(model.get(key) not in [None, ""] for key in list_of_keys):
            case = True
            break
    return case


class BaseModel(object):

    @property
    def dict(self):
        """
        Serialize Django Model.__dict__
        NOTE: to get correct field types you must run self.clean_fields() first (eg. convert int to float)
        :return: dict
        """
        d = copy.deepcopy(self.__dict__)
        d.pop("_state", None)
        d.pop("id", None)
        d.pop("basemodel_ptr_id", None)
        d.pop("run_uuid", None)
        return d

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        return obj


class FutureCosts(BaseModel, models.Model):
    name = "FutureCosts"

    run_uuid = models.UUIDField(unique=True)

    base_scenario = models.OneToOneField(
        ScenarioModel,
        to_field='run_uuid',
        on_delete=models.CASCADE,
    )
    # api_version = models.IntegerField(default=1)
    # user_uuid = models.TextField(
    #     null=True,
    #     blank=True,
    #     help_text="The assigned unique ID of a signed in REopt user."
    # )
    # webtool_uuid = models.TextField(
    #     null=True,
    #     blank=True,
    #     help_text=("The unique ID of a scenario created by the REopt Lite Webtool. Note that this ID can be shared by "
    #                "several REopt Lite API Scenarios (for example when users select a 'Resilience' analysis more than "
    #                "one REopt API Scenario is created).")
    # )
    # job_type = models.TextField(
    #     default='developer.nrel.gov'
    # )
    # description = models.TextField(blank=True)
    status = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
