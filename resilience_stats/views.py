import uuid
import sys
from django.http import JsonResponse
from reo.models import ScenarioModel, PVModel, StorageModel, LoadProfileModel, GeneratorModel, FinancialModel, WindModel
from models import ResilienceModel
from outage_simulator_LF import simulate_outage
from reo.exceptions import UnexpectedError
from django.forms.models import model_to_dict
from reo.utilities import annuity


class ScenarioOptimizing(Exception):
    pass


class ScenarioErrored(Exception):
    pass


def resilience_stats(request, run_uuid, financial_outage_sim=None):
    """
    Run outage simulator for given run_uuid
    :param request:
    :param run_uuid:
    :return: {"resilience_by_timestep",
              "resilience_hours_min",
              "resilience_hours_max",
              "resilience_hours_avg",
              "outage_durations",
              "probs_of_surviving",
             }
    """

    try:
        uuid.UUID(run_uuid)  # raises ValueError if not valid uuid

    except ValueError as e:
        if e.message == "badly formed hexadecimal UUID string":
            return JsonResponse({"Error": str(e.message)}, status=400)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value, exc_traceback, task='resilience_stats', run_uuid=run_uuid)
            err.save_to_db()
            return JsonResponse({"Error": str(err.message)}, status=400)

    try:  # to run outage simulator
        scenario = ScenarioModel.objects.get(run_uuid=run_uuid)
        if scenario.status == "Optimizing...":
            raise ScenarioOptimizing
        elif "error" in scenario.status.lower():
            raise ScenarioErrored

        try:  # see if ResilienceModel already created
            rm = ResilienceModel.objects.get(scenariomodel=scenario)
            results = model_to_dict(rm)
            # remove items that user does not need
            del results['scenariomodel']
            del results['id']

        except:
            load_profile = LoadProfileModel.objects.filter(run_uuid=scenario.run_uuid).first()
            gen = GeneratorModel.objects.filter(run_uuid=scenario.run_uuid).first()
            batt = StorageModel.objects.filter(run_uuid=scenario.run_uuid).first()
            pv = PVModel.objects.filter(run_uuid=scenario.run_uuid).first()
            financial = FinancialModel.objects.filter(run_uuid=scenario.run_uuid).first()
            wind = WindModel.objects.filter(run_uuid=scenario.run_uuid).first()

            batt_roundtrip_efficiency = batt.internal_efficiency_pct \
                                        * batt.inverter_efficiency_pct \
                                        * batt.rectifier_efficiency_pct

            results = simulate_outage(
                batt_kwh=batt.size_kwh or 0,
                batt_kw=batt.size_kw or 0,
                pv_kw_ac_hourly=pv.year_one_power_production_series_kw,
                wind_kw_ac_hourly=wind.year_one_power_production_series_kw,
                init_soc=batt.year_one_soc_series_pct,
                critical_loads_kw=load_profile.critical_load_series_kw,
                batt_roundtrip_efficiency=batt_roundtrip_efficiency,
                diesel_kw=gen.size_kw,
                fuel_available=gen.fuel_avail_gal,
                b=gen.fuel_intercept_gal_per_hr,
                m=gen.fuel_slope_gal_per_kwh,
                diesel_min_turndown=gen.min_turn_down_pct,
                financial_outage_sim=financial_outage_sim
            )

            """ add avg_crit_ld and pwf to results so that avoided outage cost can be determined as:
                    avoided_outage_costs_us_dollars = resilience_hours_avg * 
                                                      value_of_lost_load_us_dollars_per_kwh * 
                                                      avg_crit_ld *
                                                      present_worth_factor 
            """
            avg_critical_load = round(sum(load_profile.critical_load_series_kw) /
                                      len(load_profile.critical_load_series_kw), 5)

            if load_profile.outage_is_major_event:
                # assume that outage occurs only once in analysis period
                present_worth_factor = 1
            else:
                present_worth_factor = annuity(financial.analysis_years, financial.escalation_pct,
                                               financial.offtaker_discount_pct)

            if financial_outage_sim == "financial_outage_sim":
                results = {"survives_specified_outage": results}
            else:
                results.update({"present_worth_factor": present_worth_factor,
                            "avg_critical_load": avg_critical_load,
                            })

            rm = ResilienceModel.create(scenariomodel=scenario)
            ResilienceModel.objects.filter(id=rm.id).update(**results)

        results.update({"help_text": "The present_worth_factor and avg_critical_load are provided such that one can calculate an avoided outage cost in dollars by multiplying a value of load load ($/kWh) times the avg_critical_load, resilience_hours_avg, and present_worth_factor. Note that if the outage event is 'major', i.e. only occurs once, then the present_worth_factor is 1."
                        })

        response = JsonResponse(results)
        return response

    except ScenarioOptimizing:
        return JsonResponse({"Error": "The scenario is still optimizing. Please try again later."},
                            content_type='application/json', status=500)

    except ScenarioErrored:
        return JsonResponse({"Error": "An error occured in the scenario. Please check the messages from your results."},
                            content_type='application/json', status=500)

    except Exception as e:

        if type(e).__name__ == 'DoesNotExist':
            msg = "Scenario {} does not exist.".format(run_uuid)
            return JsonResponse({"Error": msg}, content_type='application/json', status=404)


        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value, exc_traceback, task='resilience_stats', run_uuid=run_uuid)
            err.save_to_db()
            return JsonResponse({"Error": err.message}, status=500)
