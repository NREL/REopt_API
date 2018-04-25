import csv
import os
import sys
import traceback as tb
import uuid
from django.http import JsonResponse
from src.load_profile import BuiltInProfile
from models import URDBError
from nested_inputs import nested_input_definitions
from reo.models import ModelManager
from reo.exceptions import UnexpectedError  #, RequestError  # should we save bad requests? could be sql injection attack?
from reo.log_levels import log
import copy

# loading the labels of hard problems - doing it here so loading happens once on startup
hard_problems_csv = os.path.join('reo', 'hard_problems.csv')
hard_problem_labels = [i[0] for i in csv.reader(open(hard_problems_csv, 'rb'))]


def help(request):

    try:
        response = copy.deepcopy(nested_input_definitions)
        del response['Scenario']['Site']['Wind']
        return JsonResponse(response)

    except Exception:
        return JsonResponse({"Error": "Unexpected Error. Please contact reopt@nrel.gov."})


def invalid_urdb(request):

    try:
        # invalid set is populated by the urdb validator, hard problems defined in csv
        invalid_set = list(set([i.label for i in URDBError.objects.filter(type='Error')]))
        return JsonResponse({"Invalid IDs": list(set(invalid_set + hard_problem_labels))})
        
    except Exception:
        return JsonResponse({"Error": "Unexpected Error. Please contact reopt@nrel.gov."})


def annual_kwh(request):

    try:
        latitude = float(request.GET['latitude'])  # need float to convert unicode
        longitude = float(request.GET['longitude'])
        doe_reference_name = request.GET['doe_reference_name']

        if doe_reference_name.lower() not in BuiltInProfile.default_buildings:
            raise ValueError("Invalid doe_reference_name. Select from the following: {}"
                             .format(BuiltInProfile.default_buildings))

        if latitude > 90 or latitude < -90:
            raise ValueError("latitude out of acceptable range (-90 <= latitude <= 90)")

        if longitude > 180 or longitude < -180:
            raise ValueError("longitude out of acceptable range (-180 <= longitude <= 180)")

        b = BuiltInProfile(latitude=latitude, longitude=longitude, doe_reference_name=doe_reference_name)
        
        response = JsonResponse(
            {'annual_kwh': b.annual_kwh,
             'city': b.city},
        )
        return response

    except KeyError as e:
        return JsonResponse({"Error. Missing": str(e.message)})

    except ValueError as e:
        return JsonResponse({"Error": str(e.message)})

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value,
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected Error. Please contact reopt@nrel.gov."})


def results(request, run_uuid):

    def make_error_resp(msg):
        resp = dict()
        resp['messages'] = {'error': msg}
        resp['outputs'] = dict()
        resp['outputs']['Scenario'] = dict()
        resp['outputs']['Scenario']['status'] = 'error'
        return resp

    try:
        uuid.UUID(run_uuid)  # raises ValueError if not valid uuid

    except ValueError as e:
        if e.message == "badly formed hexadecimal UUID string":
            resp = make_error_resp(e.message)
            return JsonResponse(resp, status=400)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value, exc_traceback, task='results', run_uuid=run_uuid)
            err.save_to_db()
            return JsonResponse({"Error": str(err.message)}, status=400)

    try:
        d = ModelManager.make_response(run_uuid)  # ModelManager has some internal exception handling

        response = JsonResponse(d)
        return response

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='reo.views.results', run_uuid=run_uuid)
        err.save_to_db()
        resp = make_error_resp(err.message)
        return JsonResponse(resp)


def simulated_load(request):
    try:
        latitude = float(request.GET['latitude'])  # need float to convert unicode
        longitude = float(request.GET['longitude'])
        doe_reference_name = request.GET['doe_reference_name']

        if doe_reference_name.lower() not in BuiltInProfile.default_buildings:
            raise ValueError("Invalid doe_reference_name. Select from the following: {}"
                             .format(BuiltInProfile.default_buildings))

        if latitude > 90 or latitude < -90:
            raise ValueError("latitude out of acceptable range (-90 <= latitude <= 90)")

        if longitude > 180 or longitude < -180:
            raise ValueError("longitude out of acceptable range (-180 <= longitude <= 180)")

        b = BuiltInProfile(latitude=latitude, longitude=longitude, doe_reference_name=doe_reference_name)
        lp = b.built_in_profile

        response = JsonResponse(
            {'loads_kw': [round(ld, 3) for ld in lp],
             'annual_kwh': b.annual_kwh,
             'min_kw': round(min(lp), 3),
             'mean_kw': round(sum(lp) / len(lp), 3),
             'max_kw': round(max(lp), 3),
             }
        )
        return response

    except KeyError as e:
        return JsonResponse({"Error. Missing": str(e.message)})

    except ValueError as e:
        return JsonResponse({"Error": str(e.message)})

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value,
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected Error. Please contact reopt@nrel.gov."})
