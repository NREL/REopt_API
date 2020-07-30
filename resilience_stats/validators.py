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
# https://docs.djangoproject.com/en/1.8/ref/validators/
import sys
import uuid

from django.core.exceptions import ValidationError

from reo.exceptions import UnexpectedError


def validate_run_uuid(run_uuid):
    try:
        uuid.UUID(run_uuid)  # raises ValueError if not valid uuid
    except ValueError as e:
        if e.args[0] == "badly formed hexadecimal UUID string":
            raise ValidationError("Error:" + str(e.args[0]))
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value.args[0], exc_traceback, task='resilience_stats', run_uuid=run_uuid)
            err.save_to_db()
            raise ValidationError("Error" + str(err.message))


def validate_RunOutput_for_outage_simulator(ro):
    if ro.pv_kw is None:
        raise ValidationError('proforma validators','Scenario pv_kw undefined')

    if ro.batt_kwh is None:
        raise ValidationError('proforma validators','Scenario batt_kwh undefined')

    if ro.batt_kw is None:
        raise ValidationError('proforma validators','Scenario batt_kw undefined')

    if ro.load_8760_kw is None:
        raise ValidationError('proforma validators','Scenario load profile undefined')

    if ro.pv_kw > 0 and ro.pv_kw_ac_hourly is None:
        raise ValidationError('proforma validators','Scenario PV production undefined (with pv_kw > 0)')

    if ro.crit_load_factor is None:
        raise ValidationError('proforma validators','Scenario critical load factor undefined')

    if ro.batt_kw > 0 and ro.batt_efficiency is None:
        raise ValidationError('proforma validators','Scenario battery efficiency undefined (with batt_kw > 0)')

    if ro.batt_kw > 0 and ro.batt_inverter_efficiency is None:
        raise ValidationError('proforma validators','Scenario battery inverter efficiency undefined (with batt_kw > 0)')

    if ro.batt_kw > 0 and ro.batt_rectifier_efficiency is None:
        raise ValidationError('proforma validators','Scenario battery rectifier efficiency undefined (with batt_kw > 0)')

    if ro.year_one_battery_soc_series is not None:
        if len(ro.load_8760_kw) != len(ro.year_one_battery_soc_series):
            raise ValidationError('proforma validators','Scenario load profile does not have the same number of time steps as battery state-of-charge')
