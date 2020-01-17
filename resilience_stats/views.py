import uuid
import sys
from django.http import JsonResponse
from reo.models import ScenarioModel, PVModel, StorageModel, LoadProfileModel, GeneratorModel, FinancialModel, WindModel
from resilience_stats.models import ResilienceModel
from resilience_stats.outage_simulator_LF import simulate_outage
from reo.exceptions import UnexpectedError, REoptError
from django.forms.models import model_to_dict
from reo.utilities import annuity
from reo.models import ModelManager
from django.db import IntegrityError
from multiprocessing import Pool


class ScenarioOptimizing(Exception):
    pass


class ScenarioErrored(Exception):
    pass


def parse_system_sizes(site):
    size_dict = dict()
    if "Generator" in site:
        size_dict["Generator"] = site["Generator"]["size_kw"]
    if "Storage" in site:
        size_dict["Storage_kw"] = site["Storage"]["size_kw"]
        size_dict["Storage_kwh"] = site["Storage"]["size_kwh"]
    if "Wind" in site:
        size_dict["Wind"] = site["Wind"]["size_kw"]
    if "PV" in site:
        size_dict["PV"] = site["PV"]["size_kw"]
    return size_dict

def resilience_stats(request, run_uuid=None, financial_check=None):
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
        if e.args[0] == "badly formed hexadecimal UUID string":
            return JsonResponse({"Error": str(e.args[0])}, status=400)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value.args[0], exc_traceback, task='resilience_stats', run_uuid=run_uuid)
            err.save_to_db()
            return JsonResponse({"Error": str(err.message)}, status=400)

    try:  # to run outage simulator
        scenario = ScenarioModel.objects.get(run_uuid=run_uuid)
        if scenario.status == "Optimizing...":
            raise ScenarioOptimizing
        elif "error" in scenario.status.lower():
            raise ScenarioErrored

        if financial_check == "financial_check":
            query = request.GET
            financial_uuid = query['financial_uuid']

            scenario = ScenarioModel.objects.get(run_uuid=financial_uuid)
            if scenario.status == "Optimizing...":
                raise ScenarioOptimizing
            elif "error" in scenario.status.lower():
                raise ScenarioErrored

            ## retrieve sizes from db
            resilience_result = ModelManager.make_response(run_uuid)
            financial_result = ModelManager.make_response(financial_uuid)

            resilience_size = parse_system_sizes(resilience_result["outputs"]["Scenario"]["Site"])
            financial_size = parse_system_sizes(financial_result["outputs"]["Scenario"]["Site"])

            results = simulate_outage(
                resilience_run_site_result=resilience_size,
                financial_run_site_result=financial_size,
                financial_check=financial_check
            )

            results = {"survives_specified_outage": results}

        else:
            try:
                query = request.GET
                bau = query['bau'] in ["True", "true", "1"]
            except:
                bau = False

            wtch = True
            try:  # see if ResilienceModel already created
                rm = ResilienceModel.objects.get(scenariomodel=scenario)
                results = model_to_dict(rm)

                if bau and "probs_of_surviving_bau" not in results:
                    wtch = False
                    raise Exception('no resilience_stat_bau in database')

                if not bau:
                    for k, v in results.items():
                        if k[-4:] == "_bau":
                            results.pop(k)

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
                results = dict()
                kwargs_dict = dict()
                # if wtch and bau:
                pool = Pool(processes=2 if wtch and bau else 1)
                # else:
                #     pool = Pool(processes=1)

                if wtch:
                    kwargs = {
                        "batt_kwh": batt.size_kwh or 0,
                        "batt_kw": batt.size_kw or 0,
                        "pv_kw_ac_hourly": pv.year_one_power_production_series_kw,
                        "wind_kw_ac_hourly": wind.year_one_power_production_series_kw,
                        "init_soc": batt.year_one_soc_series_pct,
                        "critical_loads_kw": load_profile.critical_load_series_kw,
                        "batt_roundtrip_efficiency": batt_roundtrip_efficiency,
                        "diesel_kw": gen.size_kw,
                        "fuel_available": gen.fuel_avail_gal,
                        "b": gen.fuel_intercept_gal_per_hr,
                        "m": gen.fuel_slope_gal_per_kwh,
                        "diesel_min_turndown": gen.min_turn_down_pct
                    }
                    kwargs_dict["wtch"] = kwargs

                if bau:
                    # only PV and diesel generator may have existing size
                    kwargs = {
                        "batt_kwh": 0,
                        "batt_kw": 0,
                        "pv_kw_ac_hourly": [p*pv.size_kw*pv.existing_kw for p in pv.year_one_power_production_series_kw],
                        "critical_loads_kw": load_profile.critical_load_series_kw,
                        "diesel_kw": gen.existing_kw,
                        "fuel_available": gen.fuel_avail_gal,
                        "b": gen.fuel_intercept_gal_per_hr,
                        "m": gen.fuel_slope_gal_per_kwh,
                        "diesel_min_turndown": gen.min_turn_down_pct
                    }
                    kwargs_dict["bau"] = kwargs

                p = {k: pool.apply_async(simulate_outage, tuple(), v) for k, v in kwargs_dict.items()}
                pool.close()
                pool.join()

                for k, v in p.items():
                    if k == 'wtch':
                        results.update(v.get())
                    if k == 'bau':
                        results.update({key+'_bau': val for key, val in v.get().items()})

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

                results.update({"present_worth_factor": present_worth_factor,
                            "avg_critical_load": avg_critical_load,
                            })

                try:
                    # new model
                    try:
                        rm = ResilienceModel.create(scenariomodel=scenario)
                    except Exception as e:
                        if isinstance(e, REoptError):
                            return JsonResponse({"Error": e.message}, status=500)
                        raise e
                    ResilienceModel.objects.filter(id=rm.id).update(**results)
                    
                except IntegrityError:
                    # have run resiliense_stat & bau=false
                    # return both w/tech and bau
                    ResilienceModel.objects.filter(id=rm.id).update(**results)
                    rm = ResilienceModel.objects.get(scenariomodel=scenario)
                    results = model_to_dict(rm)

                    # remove items that user does not need
                    del results['scenariomodel']
                    del results['id']

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
            err = UnexpectedError(exc_type, exc_value.args[0], exc_traceback, task='resilience_stats', run_uuid=run_uuid)
            err.save_to_db()
            return JsonResponse({"Error": err.message}, status=500)
