import csv
import os
import sys
import traceback as tb
import uuid
import copy
from django.http import JsonResponse
from src.load_profile import BuiltInProfile
from models import URDBError
from nested_inputs import nested_input_definitions
from reo.api import UUIDFilter
from reo.models import ModelManager
from reo.exceptions import UnexpectedError  #, RequestError  # should we save bad requests? could be sql injection attack?
from reo.log_levels import log
from reo.src.techs import Generator

from django.http import HttpResponse,Http404
from django.template import  loader


# loading the labels of hard problems - doing it here so loading happens once on startup
hard_problems_csv = os.path.join('reo', 'hard_problems.csv')
hard_problem_labels = [i[0] for i in csv.reader(open(hard_problems_csv, 'rb'))]

def make_error_resp(msg):
        resp = dict()
        resp['messages'] = {'error': msg}
        resp['outputs'] = dict()
        resp['outputs']['Scenario'] = dict()
        resp['outputs']['Scenario']['status'] = 'error'
        return resp

def errors(request, page_uuid):
    
    template= loader.get_template("errors.html")
    return HttpResponse(template.render())
    

def help(request):

    try:
        response = copy.deepcopy(nested_input_definitions)
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

        if doe_reference_name not in BuiltInProfile.default_buildings:
            raise ValueError("Invalid doe_reference_name. Select from the following: {}"
                             .format(BuiltInProfile.default_buildings))

        if latitude > 90 or latitude < -90:
            raise ValueError("latitude out of acceptable range (-90 <= latitude <= 90)")

        if longitude > 180 or longitude < -180:
            raise ValueError("longitude out of acceptable range (-180 <= longitude <= 180)")

        uuidFilter = UUIDFilter('no_id')
        log.addFilter(uuidFilter)
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
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.message,
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected Error. Please contact reopt@nrel.gov."})


def remove(request, run_uuid):
    try:
        ModelManager.remove(run_uuid)  # ModelManager has some internal exception handling
        return JsonResponse({"Success":True}, status=204)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value.message, exc_traceback, task='reo.views.results', run_uuid=run_uuid)
        err.save_to_db()
        resp = make_error_resp(err.message)
        return JsonResponse(resp)

def results(request, run_uuid):

    try:
        uuid.UUID(run_uuid)  # raises ValueError if not valid uuid

    except ValueError as e:
        if e.message == "badly formed hexadecimal UUID string":
            resp = make_error_resp(e.message)
            return JsonResponse(resp, status=400)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value.message, exc_traceback, task='results', run_uuid=run_uuid)
            err.save_to_db()
            return JsonResponse({"Error": str(err.message)}, status=400)

    try:
        d = ModelManager.make_response(run_uuid)  # ModelManager has some internal exception handling

        response = JsonResponse(d)
        return response

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value.message, exc_traceback, task='reo.views.results', run_uuid=run_uuid)
        err.save_to_db()
        resp = make_error_resp(err.message)
        return JsonResponse(resp)


def simulated_load(request):
    try:
        latitude = float(request.GET['latitude'])  # need float to convert unicode
        longitude = float(request.GET['longitude'])
        doe_reference_name = request.GET['doe_reference_name']

        try:  # annual_kwh is optional. if not provided, then DOE reference value is used.
            annual_kwh = float(request.GET['annual_kwh'])
        except KeyError:
            annual_kwh = None

        try:  # monthly_totals_kwh is optional. if not provided, then DOE reference value is used.
            monthly_totals_kwh = float(request.GET['monthly_totals_kwh'])
        except KeyError:
            monthly_totals_kwh = None

        if doe_reference_name not in BuiltInProfile.default_buildings:
            raise ValueError("Invalid doe_reference_name. Select from the following: {}"
                             .format(BuiltInProfile.default_buildings))

        if latitude > 90 or latitude < -90:
            raise ValueError("latitude out of acceptable range (-90 <= latitude <= 90)")

        if longitude > 180 or longitude < -180:
            raise ValueError("longitude out of acceptable range (-180 <= longitude <= 180)")

        b = BuiltInProfile(latitude=latitude, longitude=longitude, doe_reference_name=doe_reference_name,
                           annual_kwh=annual_kwh, monthly_totals_kwh=monthly_totals_kwh)
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
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.message,
                                                                            tb.format_tb(exc_traceback))
        log.error(debug_msg)
        return JsonResponse({"Error": "Unexpected Error. Please check your input parameters and contact reopt@nrel.gov if problems persist."})


def generator_efficiency(request):
    """
    From Navigant report / dieselfuelsupply.com, fitting a curve to the partial to full load points:

        CAPACITY RANGE      m [gal/kW]  b [gal]
        0 < C <= 40 kW	    0.068	    0.0125
        40 < C <= 80 kW	    0.066	    0.0142
        80 < C <= 150 kW	0.0644	    0.0095
        150 < C <= 250 kW	0.0648	    0.0067
        250 < C <= 750 kW	0.0656	    0.0048
        750 < C <= 1500 kW	0.0657	    0.0043
        1500 < C  kW	    0.0657	    0.004
    """
    try:
        generator_kw = float(request.GET['generator_kw'])  # need float to convert unicode

        if generator_kw <= 0:
            raise ValueError("Invalid generator_kw, must be greater than zero.")

        m, b = Generator.default_fuel_burn_rate(generator_kw)

        response = JsonResponse(
            {'slope_gal_per_kwh': m,
             'intercept_gal_per_hr': b,
             }
        )
        return response

    except ValueError as e:
        return JsonResponse({"Error": str(e.message)})

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.message,
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected Error. Please contact reopt@nrel.gov."})
