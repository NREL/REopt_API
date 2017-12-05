from api_definitions import inputs, outputs
from django.shortcuts import render
import json
from django.http import HttpResponse
from validators import REoptResourceValidation
from django.http import JsonResponse
from src.load_profile import BuiltInProfile
from models import URDBError
import csv
import os
from utilities import API_Error
from nested_inputs import nested_input_definitions
from reo.models import ModelManager
import sys, traceback

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


def check_inputs(request):

    checker = REoptResourceValidation()
    errors = {"Errors": {}}

    bdy = unicode(request.body, 'latin-1')
    parsed_request = json.loads(bdy)
    
    scrubbed_request = {}
    for k, v in parsed_request.items():
        if k in inputs(full_list=True).keys():
            scrubbed_request[k] = v
        else:
            errors["Errors"][k] = ["Not  Valid Input Name"]
    
    errors = checker.check_individual(scrubbed_request, errors)

    if errors == {}:
        return HttpResponse(json.dumps({"Errors": {}}), content_type='application/json')
    else:
        return HttpResponse(json.dumps(errors), content_type='application/json')


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

    try:
        run_uuid = request.GET.get('run_uuid')

        d = ModelManager.make_response(run_uuid)
        # import pdb; pdb.set_trace()

        response = JsonResponse(
            d,
        )
        print d
        return response
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        return JsonResponse({str(exc_type): repr(traceback.format_tb(exc_traceback)),
                             'message': e.message})
