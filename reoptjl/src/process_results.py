# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
from reoptjl.models import FinancialOutputs, APIMeta, PVOutputs, ElectricStorageOutputs,\
                        ElectricTariffOutputs, SiteOutputs, ElectricUtilityOutputs,\
                        GeneratorOutputs, ElectricLoadOutputs, WindOutputs, FinancialInputs,\
                        ElectricUtilityInputs, ExistingBoilerOutputs, CHPOutputs, CHPInputs, \
                        ExistingChillerOutputs, CoolingLoadOutputs, HeatingLoadOutputs,\
                        HotThermalStorageOutputs, ColdThermalStorageOutputs, OutageOutputs,\
                        REoptjlMessageOutputs, AbsorptionChillerOutputs, BoilerOutputs, SteamTurbineInputs, \
                        SteamTurbineOutputs, GHPInputs, GHPOutputs, ExistingChillerInputs
import numpy as np
import sys
import traceback as tb
import logging
log = logging.getLogger(__name__)

def process_results(results: dict, run_uuid: str) -> None:
    """
    Saves the results returned from the Julia API in the backend database.
    Called in reoptjl/run_jump_model (a celery task)
    """
    try:
        keys_to_skip = []
        pop_result_keys(results, keys_to_skip)

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
            if "AbsorptionChiller" in results.keys():
                AbsorptionChillerOutputs.create(meta=meta, **results["AbsorptionChiller"]).save()
            if "Outages" in results.keys():
                for multi_dim_array_name in ["unserved_load_series_kw", "unserved_load_per_outage_kwh", 
                                            "storage_discharge_series_kw", "pv_to_storage_series_kw", 
                                            "pv_curtailed_series_kw", "pv_to_load_series_kw", 
                                            "generator_to_storage_series_kw", "generator_curtailed_series_kw", 
                                            "generator_to_load_series_kw", "generator_fuel_used_per_outage_gal",
                                            "chp_to_storage_series_kw", "chp_curtailed_series_kw", 
                                            "chp_to_load_series_kw", "chp_fuel_used_per_outage_mmbtu",
                                            "critical_loads_per_outage_series_kw", "soc_series_fraction"]:
                    if multi_dim_array_name in results["Outages"]:
                        results["Outages"][multi_dim_array_name] = np.transpose(results["Outages"][multi_dim_array_name]).tolist()
                OutageOutputs.create(meta=meta, **results["Outages"]).save()
            if "SteamTurbine" in results.keys():
                SteamTurbineOutputs.create(meta=meta, **results["SteamTurbine"]).save()
            if "GHP" in results.keys():
                GHPOutputs.create(meta=meta, **results["GHP"]).save() 
            # TODO process rest of results
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(
                                                                        exc_type, 
                                                                        exc_value.args[0],
                                                                        tb.format_tb(exc_traceback)
                                                                    )
        log.debug(debug_msg)
        raise e

def pop_result_keys(r:dict, keys_to_skip:list):
    for k in r.keys():
        if (type(r[k])) == dict:
            for s in keys_to_skip:
                r[k].pop(s, None)
        else:
            pass

def update_inputs_in_database(inputs_to_update: dict, run_uuid: str) -> None:
    """
    Updates inputs in the backend database with values returned from Julia.
    This is needed for inputs that have defaults calculated in the REopt Julia package, 
    which currently is those that use EASIUR or AVERT data.
    Called in reoptjl/run_jump_model (a celery task)
    """

    try:
        # get input models that need updating
        FinancialInputs.objects.filter(meta__run_uuid=run_uuid).update(**inputs_to_update["Financial"])
        ElectricUtilityInputs.objects.filter(meta__run_uuid=run_uuid).update(**inputs_to_update["ElectricUtility"])

        if inputs_to_update["CHP"]:  # Will be an empty dictionary if CHP is not considered
            CHPInputs.objects.filter(meta__run_uuid=run_uuid).update(**inputs_to_update["CHP"])
        if inputs_to_update["SteamTurbine"]:  # Will be an empty dictionary if SteamTurbine is not considered
            SteamTurbineInputs.objects.filter(meta__run_uuid=run_uuid).update(**inputs_to_update["SteamTurbine"])
    
        if inputs_to_update["GHP"]:
            GHPInputs.objects.filter(meta__run_uuid=run_uuid).update(**inputs_to_update["GHP"])
        if inputs_to_update["ExistingChiller"]:
            if not ExistingChillerInputs.objects.filter(meta__run_uuid=run_uuid):
                meta = APIMeta.objects.get(run_uuid=run_uuid)
                ExistingChillerInputs.create(meta=meta, **inputs_to_update["ExistingChiller"]).save()
            else:
                ExistingChillerInputs.objects.filter(meta__run_uuid=run_uuid).update(**inputs_to_update["ExistingChiller"])
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(
                                                                        exc_type, 
                                                                        exc_value.args[0],
                                                                        tb.format_tb(exc_traceback)
                                                                    )
        log.debug(debug_msg)
