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
from job.models import FinancialOutputs, Scenario, PVOutputs, StorageOutputs, ElectricTariffOutputs,\
    ElectricUtilityOutputs


def process_results(results: dict, run_uuid: str) -> None:
    """
    Saves the results returned from the Julia API in the backend database.
    Called in job/run_jump_model (a celery task)
    """
    s = Scenario.objects.get(run_uuid=run_uuid)
    s.status = results.get("status")
    s.save(update_fields=["status"])
    FinancialOutputs.create(scenario=s, **results["Financial"]).save()
    ElectricTariffOutputs.create(scenario=s, **results["ElectricTariff"]).save()
    ElectricUtilityOutputs.create(scenario=s, **results["ElectricUtility"]).save()
    if "PV" in results.keys():
        PVOutputs.create(scenario=s, **results["PV"]).save()
    if "Storage" in results.keys():
        StorageOutputs.create(scenario=s, **results["Storage"]).save()
    # TODO process rest of results
