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
import csv
import os
import sys
import traceback as tb
import uuid
import copy
from django.http import JsonResponse
from reo.src.load_profile import BuiltInProfile
from reo.models import URDBError
from reo.nested_inputs import nested_input_definitions
from reo.api import UUIDFilter
from reo.models import ModelManager
from reo.exceptions import UnexpectedError  #, RequestError  # should we save bad requests? could be sql injection attack?
from reo.src.emissions_calculator import EmissionsCalculator
import logging
log = logging.getLogger(__name__)
from reo.src.techs import Generator
from django.http import HttpResponse
from django.template import  loader


# loading the labels of hard problems - doing it here so loading happens once on startup
hard_problems_csv = os.path.join('reo', 'hard_problems.csv')
hard_problem_labels = [i[0] for i in csv.reader(open(hard_problems_csv, 'r'))]


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

    except Exception as e:
        return JsonResponse({"Error": "Unexpected error in help endpoint: {}".format(e.args[0])})


def invalid_urdb(request):

    try:
        # invalid set is populated by the urdb validator, hard problems defined in csv
        invalid_set = list(set([i.label for i in URDBError.objects.filter(type='Error')]))
        return JsonResponse({"Invalid IDs": list(set(invalid_set + hard_problem_labels))})
        
    except Exception as e:
        return JsonResponse({"Error": "Unexpected error in invalid_urdb endpoint: {}".format(e.args[0])})


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
        return JsonResponse({"Error. Missing": str(e.args[0])})

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])})

    except Exception as e:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in annual_kwh endpoint. Check log for more."})


def remove(request, run_uuid):
    try:
        ModelManager.remove(run_uuid)  # ModelManager has some internal exception handling
        return JsonResponse({"Success":True}, status=204)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value.args[0], tb.format_tb(exc_traceback), task='reo.views.results', run_uuid=run_uuid)
        err.save_to_db()
        resp = make_error_resp(err.message)
        return JsonResponse(resp)


def results(request, run_uuid):
    try:
        uuid.UUID(run_uuid)  # raises ValueError if not valid uuid

    except ValueError as e:
        if e.args[0] == "badly formed hexadecimal UUID string":
            resp = make_error_resp(e.args[0])
            return JsonResponse(resp, status=400)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value.args[0], tb.format_tb(exc_traceback), task='results', run_uuid=run_uuid)
            err.save_to_db()
            return JsonResponse({"Error": str(err.args[0])}, status=400)

    try:
        d = ModelManager.make_response(run_uuid)  # ModelManager has some internal exception handling

        response = JsonResponse(d)
        return response

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value.args[0], tb.format_tb(exc_traceback), task='reo.views.results', run_uuid=run_uuid)
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
            string_array = request.GET.get('monthly_totals_kwh')
            if string_array is not None:
                monthly_totals_kwh = [float(v) for v in string_array.strip('[]').split(',')]
            else:
                monthly_totals_kwh = None
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
        return JsonResponse({"Error. Missing": str(e.args[0])})

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])})

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.error(debug_msg)
        return JsonResponse({"Error": "Unexpected error in simulated_load endpoint. Check log for more."})


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
        return JsonResponse({"Error": str(e.args[0])})

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in generator_efficiency endpoint. Check log for more."})

def emissions_profile(request):
    try:
        latitude = float(request.GET['latitude'])  # need float to convert unicode
        longitude = float(request.GET['longitude'])

        ec = EmissionsCalculator(latitude=latitude,longitude=longitude)
        
        try: 
            response = JsonResponse({   
                    'region_abbr': ec.region_abbr,
                    'region': ec.region,
                    'emissions_series_lb_CO2_per_kWh': ec.emissions_series,
                    'units': 'Pounds Carbon Dioxide Equivalent',
                    'description': 'Regional hourly grid emissions factor for EPA AVERT regions.',
                    'meters_to_region': ec.meters_to_region
                })
            return response
        except AttributeError as e:
            return JsonResponse({"Error": str(e.args[0])}, status=500)
    
    except KeyError as e:
        return JsonResponse({"Error. Missing Parameter": str(e.args[0])}, status=500)

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=500)

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.error(debug_msg)
        return JsonResponse({"Error": "Unexpected Error. Please check your input parameters and contact reopt@nrel.gov if problems persist."}, status=500)