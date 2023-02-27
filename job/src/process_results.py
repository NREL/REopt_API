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
from job.models import REoptjlMessageOutputs, FinancialOutputs, APIMeta, PVOutputs, ElectricStorageOutputs, ElectricTariffOutputs, SiteOutputs,\
    ElectricUtilityOutputs, GeneratorOutputs, ElectricLoadOutputs, WindOutputs, FinancialInputs, ElectricUtilityInputs, ExistingBoilerOutputs,\
    CHPInputs, CHPOutputs, ExistingChillerOutputs, CoolingLoadOutputs, HeatingLoadOutputs, HotThermalStorageOutputs, ColdThermalStorageOutputs, \
    BoilerOutputs, SteamTurbineOutputs
import logging
log = logging.getLogger(__name__)
import sys
import traceback

def process_results(results: dict, run_uuid: str) -> None:
    """
    Saves the results returned from the Julia API in the backend database.
    Called in job/run_jump_model (a celery task)
    """


    meta = APIMeta.objects.get(run_uuid=run_uuid)
    meta.status = results.get("status")
    meta.save(update_fields=["status"])

    if "Messages" in results.keys():
        REoptjlMessageOutputs.create(meta=meta, **results["Messages"]).save()
    if results.get("status") != "error":
        FinancialOutputs.create(meta=meta, **results["Financial"]).save()
        ElectricTariffOutputs.create(meta=meta, **results["ElectricTariff"]).save()
        ElectricUtilityOutputs.create(meta=meta, **results["ElectricUtility"]).save()
        ElectricLoadOutputs.create(meta=meta, **results["ElectricLoad"]).save()
        SiteOutputs.create(meta=meta, **results["Site"]).save()
        if "PV" in results.keys():
            if isinstance(results["PV"], dict):
                PVOutputs.create(meta=meta, **results["PV"]).save()
            elif isinstance(results["PV"], list):
                for pvdict in results["PV"]:
                    PVOutputs.create(meta=meta, **pvdict).save()
        if "ElectricStorage" in results.keys():
            ElectricStorageOutputs.create(meta=meta, **results["ElectricStorage"]).save()
        if "Generator" in results.keys():
            GeneratorOutputs.create(meta=meta, **results["Generator"]).save()
        if "Wind" in results.keys():
            WindOutputs.create(meta=meta, **results["Wind"]).save()
        if "Boiler" in results.keys():
            BoilerOutputs.create(meta=meta, **results["Boiler"]).save()
        if "ExistingBoiler" in results.keys():
            ExistingBoilerOutputs.create(meta=meta, **results["ExistingBoiler"]).save()
        if "ExistingChiller" in results.keys():
            ExistingChillerOutputs.create(meta=meta, **results["ExistingChiller"]).save()
        if "HotThermalStorage" in results.keys():
            HotThermalStorageOutputs.create(meta=meta, **results["HotThermalStorage"]).save()
        if "ColdThermalStorage" in results.keys():
            ColdThermalStorageOutputs.create(meta=meta, **results["ColdThermalStorage"]).save()
        if "HeatingLoad" in results.keys():
            HeatingLoadOutputs.create(meta=meta, **results["HeatingLoad"]).save()
        if "CoolingLoad" in results.keys():
            CoolingLoadOutputs.create(meta=meta, **results["CoolingLoad"]).save()
        if "CHP" in results.keys():
            CHPOutputs.create(meta=meta, **results["CHP"]).save()
        if "SteamTurbine" in results.keys():
            SteamTurbineOutputs.create(meta=meta, **results["SteamTurbine"]).save()
        # TODO process rest of results

def update_inputs_in_database(inputs_to_update: dict, run_uuid: str) -> None:
    """
    Updates inputs in the backend database with values returned from Julia.
    This is needed for inputs that have defaults calculated in the REopt Julia package, 
    which currently is those that use EASIUR or AVERT data.
    Called in job/run_jump_model (a celery task)
    """

    try:
        # get input models that need updating
        FinancialInputs.objects.filter(meta__run_uuid=run_uuid).update(**inputs_to_update["Financial"])
        ElectricUtilityInputs.objects.filter(meta__run_uuid=run_uuid).update(**inputs_to_update["ElectricUtility"])
        if inputs_to_update["CHP"]:  # Will be an empty dictionary if CHP is not considered
            CHPInputs.objects.filter(meta__run_uuid=run_uuid).update(**inputs_to_update["CHP"])
    except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(
                                                                            exc_type, 
                                                                            exc_value.args[0],
                                                                            traceback.format_tb(exc_traceback)
                                                                        )
            log.debug(debug_msg)

