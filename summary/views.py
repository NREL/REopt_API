import sys
from django.http import JsonResponse
from django.shortcuts import render
from reo.models import ScenarioModel, PVModel, StorageModel, FinancialModel
from reo.exceptions import UnexpectedError
from django.forms.models import model_to_dict

def summary(request, user_id):
	"""
	Retrieve a summary of scenarios for given user_id
	:param request:
	:param user_id:
	:return: [{
			  "user_id",
			  "run_uuid",
			  "name",
			  "description",
			  "created",
			  "status",
			  "Key Output"
			 }]
	"""
	try:
		scenarios = ScenarioModel.objects.filter(user_id=user_id).order_by('-created')
		json = {"user_id": user_id, "scenarios": []}
		for scenario in scenarios:
			results = {}

			batt = StorageModel.objects.filter(run_uuid=scenario.run_uuid).first()
			pv = PVModel.objects.filter(run_uuid=scenario.run_uuid).first()
			financial = FinancialModel.objects.filter(run_uuid=scenario.run_uuid).first()

			results['run_uuid'] = str(scenario.run_uuid)
			results['created'] = scenario.created
			results['status'] = scenario.status
			results['npv_us_dollars'] = financial.npv_us_dollars
			if pv.max_kw > 0:
				results['pv_kw'] = pv.size_kw
			else:
				results['pv_kw'] = 'not evaluated'
			if batt.max_kw > 0:
				results['batt_kw'] = batt.size_kw
			else:
				results['batt_kw'] = 'not evaluated'

			json['scenarios'].append(results)
		response = JsonResponse(json)
		return response

	except Exception as e:
		return JsonResponse({"Error": e}, status=500)


