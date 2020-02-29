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
import sys
import logging
from django.db import models
from django.contrib.postgres.fields import ArrayField
from reo.models import ScenarioModel
from reo.exceptions import SaveToDatabase
log = logging.getLogger(__name__)


class ResilienceModel(models.Model):

    scenariomodel = models.OneToOneField(
        ScenarioModel,
        to_field='id',
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True
    )
    # WITH TECH
    resilience_by_timestep = ArrayField(models.FloatField(null=True), null=True)
    resilience_hours_min = models.FloatField(null=True)
    resilience_hours_max = models.FloatField(null=True)
    resilience_hours_avg = models.FloatField(null=True)
    outage_durations = ArrayField(models.FloatField(null=True), null=True)
    probs_of_surviving = ArrayField(models.FloatField(null=True), null=True)
    probs_of_surviving_by_month = ArrayField(ArrayField(models.FloatField(null=True), null=True), null=True)
    probs_of_surviving_by_hour_of_the_day = ArrayField(ArrayField(models.FloatField(null=True), null=True), null=True)
    # BAU
    resilience_by_timestep_bau = ArrayField(models.FloatField(null=True), null=True)
    resilience_hours_min_bau = models.FloatField(null=True)
    resilience_hours_max_bau = models.FloatField(null=True)
    resilience_hours_avg_bau = models.FloatField(null=True)
    outage_durations_bau = ArrayField(models.FloatField(null=True), null=True)
    probs_of_surviving_bau = ArrayField(models.FloatField(null=True), null=True)
    probs_of_surviving_by_month_bau = ArrayField(ArrayField(models.FloatField(null=True), null=True), null=True)
    probs_of_surviving_by_hour_of_the_day_bau = ArrayField(ArrayField(models.FloatField(null=True), null=True),
                                                           null=True)
    present_worth_factor = models.FloatField(null=True)
    avg_critical_load = models.FloatField(null=True)

    @classmethod
    def create(cls, scenariomodel, **kwargs):
        rm = cls(scenariomodel=scenariomodel, **kwargs)
        try:
            rm.save()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = SaveToDatabase(exc_type, exc_value.args[0], exc_traceback, task='resilience_model', run_uuid=scenariomodel.run_uuid)
            err.save_to_db()
            raise err
        return rm
