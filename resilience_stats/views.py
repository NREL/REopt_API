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
            """ Check to see if resilience scenario system sizes are the same as financial scenario sizes """
            financial_uuid = request.GET['financial_uuid']  # TODO: validate financial_uuid

            scenario = ScenarioModel.objects.get(run_uuid=financial_uuid)
            if scenario.status == "Optimizing...":
                raise ScenarioOptimizing
            elif "error" in scenario.status.lower():
                raise ScenarioErrored

            # retrieve sizes from db
            resilience_result = ModelManager.make_response(run_uuid)
            financial_result = ModelManager.make_response(financial_uuid)

            resilience_sizes = parse_system_sizes(resilience_result["outputs"]["Scenario"]["Site"])
            financial_sizes = parse_system_sizes(financial_result["outputs"]["Scenario"]["Site"])

            survives = True
            if resilience_sizes.keys() == financial_sizes.keys():
                for tech, resil_size in resilience_sizes.items():
                    if float(resil_size - financial_sizes[tech]) / float(max(resil_size, 1)) > 1.0e-3:
                        survives = False
                        break
            else:
                survives = False

            results = {"survives_specified_outage": survives}

        else:
            with_tech = True
            bau = False
            if request.GET.get('bau') in ["True", "true", "1"]:
                bau = True
            try:  # see if ResilienceModel already created
                rm = ResilienceModel.objects.get(scenariomodel=scenario)
                results = model_to_dict(rm)

                if bau and "probs_of_surviving_bau" not in results:
                    with_tech = False
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
                scenarios_dict = dict()
                # if with_tech and bau:
                pool = Pool(processes=2 if with_tech and bau else 1)
                # else:
                #     pool = Pool(processes=1)

                if with_tech:
                    scenarios_dict["with_tech"] = {
                        "batt_kwh": batt.size_kwh or 0,
                        "batt_kw": batt.size_kw or 0,
                        "pv_kw_ac_hourly": pv.year_one_power_production_series_kw,
                        "wind_kw_ac_hourly": wind.year_one_power_production_series_kw,
                        "init_soc": batt.year_one_soc_series_pct,
                        "critical_loads_kw": load_profile.critical_load_series_kw,
                        "batt_roundtrip_efficiency": batt_roundtrip_efficiency,
                        "diesel_kw": gen.size_kw or 0,
                        "fuel_available": gen.fuel_avail_gal,
                        "b": gen.fuel_intercept_gal_per_hr,
                        "m": gen.fuel_slope_gal_per_kwh,
                        "diesel_min_turndown": gen.min_turn_down_pct
                    }

                if bau:
                    # only PV and diesel generator may have existing size
                    scenarios_dict["bau"] = {
                        "batt_kwh": 0,
                        "batt_kw": 0,
                        "pv_kw_ac_hourly": [p / pv.size_kw * pv.existing_kw for p in pv.year_one_power_production_series_kw],
                        "critical_loads_kw": load_profile.critical_load_series_kw,
                        "diesel_kw": gen.existing_kw or 0,
                        "fuel_available": gen.fuel_avail_gal,
                        "b": gen.fuel_intercept_gal_per_hr,
                        "m": gen.fuel_slope_gal_per_kwh,
                        "diesel_min_turndown": gen.min_turn_down_pct
                    }

                p = {name: pool.apply_async(simulate_outage, tuple(), kwargs) for name, kwargs in scenarios_dict.items()}
                pool.close()
                pool.join()

                for k, v in p.items():
                    if k == 'with_tech':
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
