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
import json
from django.http import JsonResponse
from reo.models import ScenarioModel, SiteModel, LoadProfileModel, PVModel, StorageModel, WindModel, GeneratorModel, FinancialModel, ElectricTariffModel, MessageModel
from reo.exceptions import UnexpectedError
from reo.models import ModelManager
from resilience_stats.models import ResilienceModel
import uuid
from summary.models import UserUnlinkedRuns


def add_user_uuid(request):
    """
    update the user_uuid associated with a Scenario run_uuid
    :param request POST:
        {
            "user_uuid",
            "run_uuid"
        }
    :return: None
    """
    try:
        if request.method == 'POST':
            post = request.body
            # Try to import JSON
            try:
                data = json.loads(post)
                try:
                    user_uuid = str(data['user_uuid'])
                    run_uuid = str(data['run_uuid'])
                    uuid.UUID(user_uuid)  # raises ValueError if not valid uuid
                    uuid.UUID(run_uuid)  # raises ValueError if not valid uuid
                    try:
                        scenario = ScenarioModel.objects.filter(run_uuid=run_uuid).first()
                        print (scenario.user_uuid)
                        if scenario.user_uuid is None:
                            ModelManager.add_user_uuid(user_uuid, run_uuid)
                            response = JsonResponse(
                                {"Success": "user_uuid for run_uuid {} has been set to {}".format(run_uuid, user_uuid)})
                            return response
                        else:
                            return JsonResponse({"Error": "a user_uuid already exists for run_uuid {}".format(run_uuid)})
                    except:
                        return JsonResponse({"Error": "run_uuid does not exist"})
                except:
                    return JsonResponse({"Error": "Invalid inputs: must provide user_uuid and run_uuid key value pairs as valid UUIDs"})
            except:
                return JsonResponse({"Error": "Invalid JSON"})
        else:
            return JsonResponse({"Error": "Must POST a JSON with user_uuid and run_uuid key value pairs"})

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='add_user_uuid')
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=500)

def unlink(request, user_uuid, run_uuid):
    """
    Retrieve a summary of scenarios for given user_uuid
    :param request:
    :param user_uuid:
    :return 
        True, bool
    """
    content = {'user_uuid':user_uuid, 'run_uuid':run_uuid}
    for name, check_id in content.items():
        try:
            uuid.UUID(check_id)  # raises ValueError if not valid uuid

        except ValueError as e:
            if e.args[0] == "badly formed hexadecimal UUID string":
                return JsonResponse({"Error": "{} {}".format(name, e.args[0]) }, status=400)
            else:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                if name == 'user_uuid':
                    err = UnexpectedError(exc_type, exc_value, exc_traceback, task='unlink', user_uuid=check_id)
                if name == 'run_uuid':
                    err = UnexpectedError(exc_type, exc_value, exc_traceback, task='unlink', run_uuid=check_id)
                err.save_to_db()
                return JsonResponse({"Error": str(err.message)}, status=400)

    try:
        
        if not ScenarioModel.objects.filter(user_uuid=user_uuid).exists():
            return JsonResponse({"Error":"User {} does not exist".format(user_uuid)}, status=400)

        if not ScenarioModel.objects.filter(run_uuid=run_uuid).exists():
            return JsonResponse({"Error":"Run {} does not exist".format(run_uuid)}, status=400)

        runs = ScenarioModel.objects.filter(run_uuid=run_uuid)
        if runs.exists():
            if runs[0].user_uuid != user_uuid:
                return JsonResponse({"Error":"Run {} is not associated with user {}".format(run_uuid, user_uuid)}, status=400)

        if not UserUnlinkedRuns.objects.filter(run_uuid=run_uuid).exists():
            UserUnlinkedRuns.create(**content)

        return JsonResponse({"Success":True}, status=204)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='unlink', user_uuid=user_uuid)
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=404)


def summary(request, user_uuid):
    """
    Retrieve a summary of scenarios for given user_uuid
    :param request:
    :param user_uuid:
    :return:
        {
            "user_uuid",
            "scenarios":
                [{
                  "run_uuid",                   # Run ID
                  "status",                     # Status
                  "created",                    # Date
                  "description",                # Description
                  "focus",                      # Focus
                  "address",                    # Address
                  "urdb_rate_name",             # Utility Tariff
                  "doe_reference_name",         # Load Profile
                  "npv_us_dollars",             # Net Present Value ($)
                  "net_capital_costs",          # DG System Cost ($)
                  "year_one_savings_us_dollars",# Year 1 Savings ($)
                  "pv_kw",                      # PV Size (kW)
                  "wind_kw",                    # Wind Size (kW)
                  "gen_kw",                     # Generator Size (kW)
                  "batt_kw",                    # Battery Power (kW)
                  "batt_kwh"                    # Battery Capacity (kWh)
                  ""
                }]
        }
    """
    try:
        uuid.UUID(user_uuid)  # raises ValueError if not valid uuid

    except ValueError as e:
        if e.args[0] == "badly formed hexadecimal UUID string":
            return JsonResponse({"Error": str(e.message)}, status=404)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value, exc_traceback, task='summary', user_uuid=user_uuid)
            err.save_to_db()
            return JsonResponse({"Error": str(err.message)}, status=404)

    try:
        scenarios = ScenarioModel.objects.filter(user_uuid=user_uuid).order_by('-created')
        unlinked_run_uuids = [i.run_uuid for i in UserUnlinkedRuns.objects.filter(user_uuid=user_uuid)]
        scenarios = [s for s in scenarios if s.run_uuid not in unlinked_run_uuids]

        json_response = {"user_uuid": user_uuid, "scenarios": []}

        if len(scenarios) == 0:
            response = JsonResponse({"Error": "No scenarios found for user '{}'".format(user_uuid)}, content_type='application/json', status=404)
            return response
        
        scenario_run_uuids =  [s.run_uuid for s in scenarios]
        scenario_run_ids =  [s.id for s in scenarios]

        #saving time by only calling each table once
        messages = MessageModel.objects.filter(run_uuid__in=scenario_run_uuids).values('run_uuid','message_type','message')
        sites = SiteModel.objects.filter(run_uuid__in=scenario_run_uuids).values('run_uuid','address')
        loads = LoadProfileModel.objects.filter(run_uuid__in=scenario_run_uuids).values('run_uuid','outage_start_hour','loads_kw','doe_reference_name')
        batts = StorageModel.objects.filter(run_uuid__in=scenario_run_uuids).values('run_uuid','max_kw','size_kw','size_kwh')
        pvs = PVModel.objects.filter(run_uuid__in=scenario_run_uuids).values('run_uuid','max_kw','size_kw')
        winds = WindModel.objects.filter(run_uuid__in=scenario_run_uuids).values('run_uuid','max_kw','size_kw')
        gens = GeneratorModel.objects.filter(run_uuid__in=scenario_run_uuids).values('run_uuid', 'max_kw', 'size_kw')
        financials = FinancialModel.objects.filter(run_uuid__in=scenario_run_uuids).values('run_uuid','npv_us_dollars','net_capital_costs','lcc_us_dollars','lcc_bau_us_dollars','net_capital_costs_plus_om_us_dollars', 'net_capital_costs','net_om_us_dollars_bau')
        tariffs = ElectricTariffModel.objects.filter(run_uuid__in=scenario_run_uuids).values('run_uuid','urdb_rate_name','year_one_energy_cost_us_dollars','year_one_demand_cost_us_dollars','year_one_fixed_cost_us_dollars','year_one_min_charge_adder_us_dollars','year_one_bill_us_dollars','year_one_energy_cost_bau_us_dollars','year_one_demand_cost_bau_us_dollars','year_one_fixed_cost_bau_us_dollars','year_one_min_charge_adder_bau_us_dollars','year_one_bill_bau_us_dollars')
        resiliences = ResilienceModel.objects.filter(scenariomodel_id__in=scenario_run_ids).values('scenariomodel_id','resilience_hours_avg','resilience_hours_max','resilience_hours_min')

        def get_scenario_data(data, run_uuid):
            if type(data)==dict:
                if str(data.get('run_uuid')) == str(run_uuid):
                    return data
                if str(data.get('scenariomodel_id')) == str(run_uuid):
                    return data
            result = [s for s in data if str(s.get('run_uuid')) == str(run_uuid)]
            if len(result) > 0:
                return result
            result = [s for s in data if str(s.get('scenariomodel_id')) == str(run_uuid)]
            if len(result) > 0:
                return result
            return [{}]

        for scenario in scenarios:
            results = {}
            
            message_set = get_scenario_data(messages, scenario.run_uuid)
            if not type(message_set) == list:
                message_set = [message_set]
            
            site = get_scenario_data(sites, scenario.run_uuid)[0]
            load = get_scenario_data(loads, scenario.run_uuid)[0]
            batt = get_scenario_data(batts, scenario.run_uuid)[0]
            pv = get_scenario_data(pvs, scenario.run_uuid)[0]
            wind = get_scenario_data(winds, scenario.run_uuid)[0]
            gen = get_scenario_data(gens, scenario.run_uuid)[0]
            financial = get_scenario_data(financials, scenario.run_uuid)[0]
            tariff = get_scenario_data(tariffs, scenario.run_uuid)[0]
            resilience = get_scenario_data(resiliences, scenario.id)[0]
            
            # Messages
            results['messages'] = {}
            for message in message_set:
                if len(message.keys()) > 0:
                    results['messages'][message.get('message_type') or "type"] = message.get('message') or ""
            
            # Run ID
            results['run_uuid'] = str(scenario.run_uuid)

            # Status
            results['status'] = scenario.status

            # Date
            results['created'] = scenario.created

            if site:

                # Description
                results['description'] = scenario.description

                # Focus
                if load['outage_start_hour'] is not None:
                    results['focus'] = "Resilience"
                else:
                    results['focus'] = "Financial"

                # Address
                results['address'] = site.get('address')

                # Utility Tariff
                if tariff['urdb_rate_name']:
                    results['urdb_rate_name'] = tariff.get('urdb_rate_name')
                else:
                    results['urdb_rate_name'] = "Custom"

                # Load Profile
                if load['loads_kw']:
                    results['doe_reference_name'] = "Custom"
                else:
                    results['doe_reference_name'] = load.get('doe_reference_name')

                # NPV
                results['npv_us_dollars'] = financial.get('npv_us_dollars')

                # DG System Cost
                results['net_capital_costs'] = financial.get('net_capital_costs')

                # Lifecycle Costs
                results['lcc_us_dollars'] = financial.get('lcc_us_dollars')

                 # Lifecycle Costs BAU
                results['lcc_bau_us_dollars'] = financial.get('lcc_bau_us_dollars')

                #Other Financials
                results['net_capital_costs_plus_om_us_dollars'] = financial.get('net_capital_costs_plus_om_us_dollars')
                results['net_om_us_dollars_bau'] = financial.get('net_om_us_dollars_bau')
                results['net_capital_costs'] = financial.get('net_capital_costs')

                # Year 1 Savings
                year_one_costs = sum(filter(None, [
                    tariff.get('year_one_energy_cost_us_dollars') or 0,
                    tariff.get('year_one_demand_cost_us_dollars') or 0,
                    tariff.get('year_one_fixed_cost_us_dollars') or 0,
                    tariff.get('year_one_min_charge_adder_us_dollars') or 0,
                    tariff.get('year_one_bill_us_dollars') or 0
                    ]))
                
                year_one_costs_bau = sum(filter(None, [
                    tariff.get('year_one_energy_cost_bau_us_dollars') or 0,
                    tariff.get('year_one_demand_cost_bau_us_dollars') or 0,
                    tariff.get('year_one_fixed_cost_bau_us_dollars') or 0,
                    tariff.get('year_one_min_charge_adder_bau_us_dollars') or 0,
                    tariff.get('year_one_bill_bau_us_dollars') or 0
                    ]))
                #Resilience Stats
                results['resilience_hours_min'] = resilience.get('resilience_hours_min') 
                results['resilience_hours_max'] = resilience.get('resilience_hours_max') 
                results['resilience_hours_avg'] = resilience.get('resilience_hours_avg') 

                if results['resilience_hours_max'] is None:
                    results['resilience_hours_max'] = 'not evaluated'
                if results['resilience_hours_min'] is None:
                    results['resilience_hours_min'] = 'not evaluated'
                if results['resilience_hours_avg'] is None:
                    results['resilience_hours_avg'] = 'not evaluated'
                
                results['year_one_savings_us_dollars'] = year_one_costs_bau - year_one_costs

                # PV Size
                if pv is not None:
                    if pv['max_kw'] > 0:
                        results['pv_kw'] = pv.get('size_kw')
                    else:
                        results['pv_kw'] = 'not evaluated'
                else:
                    results['pv_kw'] = 'not evaluated'

                # Wind Size
                if wind is not None:
                    if wind.get('max_kw') or -1 > 0:
                        results['wind_kw'] = wind.get('size_kw')
                    else:
                        results['wind_kw'] = 'not evaluated'
                else:
                    results['wind_kw'] = 'not evaluated'

                # Generator Size
                if gen is not None:
                    if gen.get('max_kw') or -1 > 0:
                        results['gen_kw'] = gen.get('size_kw')
                    else:
                        results['gen_kw'] = 'not evaluated'
                else:
                    results['gen_kw'] = 'not evaluated'

                # Battery Size
                if batt is not None:
                    if batt.get('max_kw') or -1 > 0:
                        results['batt_kw'] = batt.get('size_kw')
                        results['batt_kwh'] = batt.get('size_kwh')
                    else:
                        results['batt_kw'] = 'not evaluated'
                        results['batt_kwh'] = 'not evaluated'
                else:
                    results['batt_kw'] = 'not evaluated'
                    results['batt_kwh'] = 'not evaluated'

            json_response['scenarios'].append(results)
        response = JsonResponse(json_response, status=200)
        return response

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='summary', user_uuid=user_uuid)
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=404)
