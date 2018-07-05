import sys
from django.http import JsonResponse
from django.shortcuts import render
from reo.models import ScenarioModel, SiteModel, LoadProfileModel, PVModel, StorageModel, WindModel, FinancialModel, ElectricTariffModel
from reo.exceptions import UnexpectedError
from django.forms.models import model_to_dict

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
				  "run_uuid",					# Run ID
				  "status",						# Status
				  "created",					# Date
				  "description",				# Description
				  "focus",						# Focus
				  "location",					# Location
				  "urdb_rate_name",				# Utility Tariff
				  "doe_reference_name",			# Load Profile
				  "npv_us_dollars",				# Net Present Value ($)
				  "net_capital_costs",			# DG System Cost ($)
				  "year_one_savings_us_dollars",# Year 1 Savings ($)
				  "pv_kw",						# PV Size (kW)
				  "wind_kw",					# Wind Size (kW)
				  "batt_kw",					# Battery Power (kW)
				  "batt_kwh"					# Battery Capacity (kWh)
				  ""
				}]
		}
	"""
	try:
		scenarios = ScenarioModel.objects.filter(user_id=user_id).order_by('-created')
		json = {"user_id": user_id, "scenarios": []}
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
				results['run_description'] = site.run_description

				# Focus
				if load.outage_start_hour:
					results['focus'] = "Resilience"
				else:
					results['focus'] = "Financial"

				# Location
				results['location'] = site.location

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
		return JsonResponse({"Error": e}, status=500)


