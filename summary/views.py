import sys
import json
from django.http import JsonResponse
from reo.models import ScenarioModel, SiteModel, LoadProfileModel, PVModel, StorageModel, WindModel, FinancialModel, ElectricTariffModel, MessageModel
from reo.exceptions import UnexpectedError
from reo.models import ModelManager
import uuid


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
                            print ('None')
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
                  "batt_kw",                    # Battery Power (kW)
                  "batt_kwh"                    # Battery Capacity (kWh)
                  ""
                }]
        }
    """
    try:
        uuid.UUID(user_uuid)  # raises ValueError if not valid uuid

    except ValueError as e:
        if e.message == "badly formed hexadecimal UUID string":
            return JsonResponse({"Error": str(e.message)}, status=400)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value, exc_traceback, task='summary', user_uuid=user_uuid)
            err.save_to_db()
            return JsonResponse({"Error": str(err.message)}, status=400)

    try:
        scenarios = ScenarioModel.objects.filter(user_uuid=user_uuid).order_by('-created')
        json = {"user_uuid": user_uuid, "scenarios": []}

        if len(scenarios) == 0:
            response = JsonResponse({"Error": "No scenarios found for user '{}'".format(user_uuid)}, content_type='application/json', status=404)
            return response
        
        scenario_run_uuids =  [s.run_uuid for s in scenarios]
        
        #saving time by only calling each table once
        def dbToDict(db_results):
            result = {}
            for r in db_results:
                if r in result.keys():
                    result[r.run_uuid] = result[r.run_uuid] + [r]
                else:
                    result[r.run_uuid] = r
            return result

        messages = dbToDict(MessageModel.objects.filter(run_uuid__in=scenario_run_uuids).all())
        sites = dbToDict(SiteModel.objects.filter(run_uuid__in=scenario_run_uuids).all())
        loads = dbToDict(LoadProfileModel.objects.filter(run_uuid__in=scenario_run_uuids).all())
        batts = dbToDict(StorageModel.objects.filter(run_uuid__in=scenario_run_uuids).all())
        pvs = dbToDict(PVModel.objects.filter(run_uuid__in=scenario_run_uuids).all())
        winds = dbToDict(WindModel.objects.filter(run_uuid__in=scenario_run_uuids).all())
        financials = dbToDict(FinancialModel.objects.filter(run_uuid__in=scenario_run_uuids).all())
        tariffs = dbToDict(ElectricTariffModel.objects.filter(run_uuid__in=scenario_run_uuids).all())
        
        for scenario in scenarios:
            results = {}
            
            message_set = messages.get(scenario.run_uuid,[])
            if not type(message_set) == list:
                message_set = [message_set]
            site = sites.get(scenario.run_uuid)
            load = loads.get(scenario.run_uuid)
            batt = batts.get(scenario.run_uuid)
            pv = pvs.get(scenario.run_uuid)
            wind = winds.get(scenario.run_uuid)
            financial = financials.get(scenario.run_uuid)
            tariff = tariffs.get(scenario.run_uuid)
            
            # Messages
            results['messages'] = {}
            for message in message_set:
                results['messages'][message.message_type] = message.message
            
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
                if load.outage_start_hour:
                    results['focus'] = "Resilience"
                else:
                    results['focus'] = "Financial"

                # Address
                results['address'] = site.address

                # Utility Tariff
                if tariff.urdb_rate_name:
                    results['urdb_rate_name'] = tariff.urdb_rate_name
                else:
                    results['urdb_rate_name'] = "Custom"

                # Load Profile
                if load.loads_kw:
                    results['doe_reference_name'] = "Custom"
                else:
                    results['doe_reference_name'] = load.doe_reference_name

                # NPV
                results['npv_us_dollars'] = financial.npv_us_dollars

                # DG System Cost
                results['net_capital_costs'] = financial.net_capital_costs

                # Year 1 Savings
                year_one_costs = sum(filter(None, [
                    tariff.year_one_energy_cost_us_dollars,
                    tariff.year_one_demand_cost_us_dollars,
                    tariff.year_one_fixed_cost_us_dollars,
                    tariff.year_one_min_charge_adder_us_dollars,
                    tariff.year_one_bill_us_dollars
                    ]))
                year_one_costs_bau = sum(filter(None, [
                    tariff.year_one_energy_cost_bau_us_dollars,
                    tariff.year_one_demand_cost_bau_us_dollars,
                    tariff.year_one_fixed_cost_bau_us_dollars,
                    tariff.year_one_min_charge_adder_bau_us_dollars,
                    tariff.year_one_bill_bau_us_dollars
                    ]))
                results['year_one_savings_us_dollars'] = year_one_costs_bau - year_one_costs

                # PV Size
                if pv.max_kw > 0:
                    results['pv_kw'] = pv.size_kw
                else:
                    results['pv_kw'] = 'not evaluated'

                # Wind Size
                if wind.max_kw > 0:
                    results['wind_kw'] = wind.size_kw
                else:
                    results['wind_kw'] = 'not evaluated'

                # Battery Size
                if batt.max_kw > 0:
                    results['batt_kw'] = batt.size_kw
                    results['batt_kwh'] = batt.size_kwh
                else:
                    results['batt_kw'] = 'not evaluated'
                    results['batt_kwh'] = 'not evaluated'


            json['scenarios'].append(results)
        response = JsonResponse(json)
        return response

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='summary', user_uuid=user_uuid)
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=500)
