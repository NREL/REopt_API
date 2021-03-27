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
import pandas as pd
import logging
from reo.models import ScenarioModel

log = logging.getLogger(__name__)
year = 2021
"""
The year is used to create instantiate the future costs object with the appropriate cost forecasts.
Note that there is only data for 2021 currently.
"""


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


class FutureCostsJob(BaseModel, models.Model):
    name = "FutureCostsJob"

    run_uuid = models.UUIDField(unique=True)
    description = models.TextField(blank=True)
    status = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    # TODO: allow user provided future costs?

    base_scenario = models.OneToOneField(
        ScenarioModel,
        to_field='run_uuid',
        on_delete=models.CASCADE,
    )
    base_year = models.IntegerField()

    future_scenario1 = models.OneToOneField(
        ScenarioModel,
        related_name="future_scenario1",
        to_field='run_uuid',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    future_year1 = models.IntegerField(
        blank=True,
        null=True
    )

    def clean(self):
        if not self.base_year:
            self.base_year = int(self.base_scenario.created.year)


class CostForecasts(object):

    reopt_size_class_to_dGen_hub_height = {
        'residential': 20,
        'commercial': 40,
        'medium': 50,
        'large': 80,
    }

    def __init__(self, year: int):
        self.wind_costs = pd.read_csv("futurecosts/cost_data/{}/wind_prices.csv".format(year))

    def wind(self, year: int, type: str, size_class: str) -> float:
        assert year in self.wind_costs.year.to_list()
        assert type in ["capital_cost_dollars_per_kw", "fixed_om_dollars_per_kw_per_yr"]
        assert size_class in self.reopt_size_class_to_dGen_hub_height.keys()
        height = self.reopt_size_class_to_dGen_hub_height[size_class]
        return self.wind_costs[
            self.wind_costs.default_tower_height_m == height
        ].loc[year, type]

"""
1. get Wind.size_class from the original scenario inputs (if Wind.max_kw > 0)
2. translate to dGen hub height
3. take wind forecasts from csv/df for dGen hub height 
"""

cost_forecasts = CostForecasts(year=year)
