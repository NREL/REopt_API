import json
import csv
import os
import sys
import traceback
import uuid
from api_definitions import inputs, outputs
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from src.load_profile import BuiltInProfile
from models import URDBError
from utilities import API_Error
from nested_inputs import nested_input_definitions
from reo.models import ModelManager
from reo.exceptions import UnexpectedError, ResultsRequestError

# loading the labels of hard problems - doing it here so loading happens once on startup
hard_problems_csv = os.path.join('reo', 'hard_problems.csv')
hard_problem_labels = [i[0] for i in csv.reader(open(hard_problems_csv, 'rb'))]


def help(request):
    return render(request, 'help.html', {'nested_input_definitions' : json.dumps(nested_input_definitions)})


def index(request):
    api_inputs = {}
    reference = inputs(full_list=True)
    for k, v in reference.items():
        api_inputs[k] = {'req': bool(reference[k].get('req'))}
        api_inputs[k]['type'] = reference[k].get('type').__name__
        api_inputs[k]['description'] = reference[k].get('description')

        units = reference[k].get('units')
        if units:
            api_inputs[k]['description'] = "%s (%s)" % (api_inputs[k]['description'], units)

        api_inputs[k]['validations'] = "min: %s \n max: %s \n restrict to: %s" % (reference[k].get('min'),
                                                                                  reference[k].get('max'),
                                                                                  reference[k].get('restrict_to'))

    api_outputs = outputs()
    return render(request, 'template.html', {'api_inputs': api_inputs, 'api_outputs': api_outputs})


def default_api_inputs(request):
    try:
        defaults = {k:v.get('default') for k,v in inputs(full_list=True).items() if v.get('default') is not None}
        return JsonResponse(defaults)
    except Exception as e:
        return JsonResponse(API_Error(e).response)


def invalid_urdb(request):

    try:
        # invalid set is populated by the urdb validator, hard problems defined in csv
        invalid_set = list(set([i.label for i in URDBError.objects.filter(type='Error')]))
        response = JsonResponse({"Invalid IDs": list(set(invalid_set + hard_problem_labels))})
        return response
        
    except Exception as e:
        return JsonResponse(API_Error(e).response)


def annual_kwh(request):

    try:
        kwargs = {k: v for k, v in request.GET.dict().items() if k in ['latitude', 'longitude', 'doe_reference_name']}

        b = BuiltInProfile(**kwargs)
        
        response = JsonResponse(
            {'annual_kwh': b.annual_kwh,
             'city': b.city},
        )
        return response
    except Exception as e:
        return JsonResponse(API_Error(e).response)


def results(request):

    def make_error_resp(msg):
        resp = dict()
        resp['messages'] = {'error': msg}
        resp['outputs'] = dict()
        resp['outputs']['Scenario'] = dict()
        resp['outputs']['Scenario']['status'] = 'error'
        return resp

    try:
        run_uuid = request.GET['run_uuid']

        uuid.UUID(run_uuid)  # raises ValueError if not valid uuid

        d = ModelManager.make_response(run_uuid)

        if 'error' in d.get('messages'):
            err = ResultsRequestError(message=d['messages']['error'], traceback="REQUEST: {}".format(request.GET))
            err.save_to_db()

        response = JsonResponse(d)
        return response

    except KeyError:
        msg = "run_uuid parameter not provided."
        err = ResultsRequestError(message=msg, traceback="REQUEST: {}".format(request.GET))
        err.save_to_db()
        resp = make_error_resp(msg)
        return JsonResponse(resp, status=400)

    except ValueError as e:
        if e.message == "badly formed hexadecimal UUID string":
            err = ResultsRequestError(message=e.message, traceback="REQUEST: {}".format(request.GET))
            err.save_to_db()
            resp = make_error_resp(e.message)
            return JsonResponse(resp, status=400)

    except Exception:

        if 'run_uuid' not in locals():
            run_uuid = "unable to get run_uuid from request"

        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='reo.views.results', run_uuid=run_uuid, )
        err.save_to_db()

        resp = make_error_resp(err.message)

        return JsonResponse(resp)
