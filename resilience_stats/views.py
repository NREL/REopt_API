import uuid
import sys
from django.http import JsonResponse
from reo.models import ScenarioModel, SiteModel, PVModel, StorageModel, LoadProfileModel
from models import ResilienceModel
from outage_simulator import simulate_outage
from reo.exceptions import UnexpectedError


def resilience_stats(request):

    try:  # to get run_uuid
        run_uuid = request.GET['run_uuid']
        uuid.UUID(run_uuid)  # raises ValueError if not valid uuid

    except KeyError:
        msg = "run_uuid parameter not provided."
        return JsonResponse({"Error": str(msg)}, status=400)

    except ValueError as e:
        if e.message == "badly formed hexadecimal UUID string":
            return JsonResponse({"Error": str(e.message)}, status=400)
        else:
            if 'run_uuid' not in locals() or 'run_uuid' not in globals():
                run_uuid = "unable to get run_uuid from request"
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value, exc_traceback, task='reo.views.results', run_uuid=run_uuid)
            err.save_to_db()
            return JsonResponse({"Error": str(err.message)}, status=400)

    except Exception:
        if 'run_uuid' not in locals() or 'run_uuid' not in globals():
            run_uuid = "unable to get run_uuid from request"

        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='reo.views.results', run_uuid=run_uuid)
        err.save_to_db()
        return JsonResponse({"Error": err.message})

    try:  # to run outage simulator
        scenario = ScenarioModel.objects.get(run_uuid=run_uuid)

        rm = ResilienceModel.create(scenariomodel=scenario)
        site = SiteModel.objects.filter(run_uuid=scenario.run_uuid).first()
        batt = StorageModel.objects.filter(run_uuid=scenario.run_uuid).first()
        pv = PVModel.objects.filter(run_uuid=scenario.run_uuid).first()
        load_profile = LoadProfileModel.objects.filter(run_uuid=scenario.run_uuid).first()

        batt_roundtrip_efficiency = batt.internal_efficiency_pct \
                                    * batt.inverter_efficiency_pct \
                                    * batt.rectifier_efficiency_pct
        results = simulate_outage(
            pv_kw=pv.size_kw or 0,
            batt_kwh=batt.size_kwh or 0,
            batt_kw=batt.size_kw or 0,
            load=load_profile.year_one_electric_load_series_kw,
            pv_kw_ac_hourly=pv.year_one_power_production_series_kw,
            init_soc=batt.year_one_soc_series_pct,
            crit_load_factor=load_profile.critical_load_pct,
            batt_roundtrip_efficiency=batt_roundtrip_efficiency,
        )

        ResilienceModel.objects.filter(id=rm.id).update(**results)

        response = JsonResponse(results)
        return response

    except Exception:
        if 'run_uuid' not in locals():
            run_uuid = "unable to get run_uuid from request"

        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='reo.views.results', run_uuid=run_uuid)
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=500)
