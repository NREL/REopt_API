import sys
import json
from django.http import JsonResponse
from reo.models import ScenarioModel, SiteModel, LoadProfileModel, PVModel, StorageModel, WindModel, FinancialModel, ElectricTariffModel
from reo.exceptions import UnexpectedError
from reo.models import ModelManager


def update_user_id(request):
    """
    update the user_id associated with a Scenario run_uuid
    :param request POST:
        {
            "user_id",
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
                    user_id = str(data['user_id'])
                    run_uuid = str(data['run_uuid'])
                    try:
                        # import pdb; pdb.set_trace()
                        ModelManager.update_user_id(user_id, run_uuid)
                        response = JsonResponse(
                            {"Success": "user_id for run_uuid {} has been set to {}".format(run_uuid, user_id)})
                        return response
                    except:
                        return JsonResponse({"Error": "run_uuid does not exist"})
                except:
                    return JsonResponse({"Error": "Invalid inputs: must provide user_id and run_uuid key value pairs"})
            except:
                return JsonResponse({"Error": "Invalid JSON"})
        else:
            return JsonResponse({"Error": "Must POST a JSON with user_id and run_uuid key value pairs"})

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='update_user_id')
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=500)

def summary(request, user_id):
    """
    Retrieve a summary of scenarios for given user_id
    :param request:
    :param user_id:
    :return:
        {
            "user_id",
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
        scenarios = ScenarioModel.objects.filter(user_id=user_id).order_by('-created')
        json = {"user_id": user_id, "scenarios": []}

        if len(scenarios) == 0:
            response = JsonResponse({"Error": "No scenarios found for user '{}'".format(user_id)}, content_type='application/json', status=404)
            return response

        for scenario in scenarios:
            results = {}

            site = SiteModel.objects.filter(run_uuid=scenario.run_uuid).first()
            load = LoadProfileModel.objects.filter(run_uuid=scenario.run_uuid).first()
            batt = StorageModel.objects.filter(run_uuid=scenario.run_uuid).first()
            pv = PVModel.objects.filter(run_uuid=scenario.run_uuid).first()
            wind = WindModel.objects.filter(run_uuid=scenario.run_uuid).first()
            financial = FinancialModel.objects.filter(run_uuid=scenario.run_uuid).first()
            tariff = ElectricTariffModel.objects.filter(run_uuid=scenario.run_uuid).first()

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
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='summary', user_id=user_id)
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=500)
