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
import pickle
from django.http import JsonResponse
from reo.src.load_profile import BuiltInProfile
from reo.src.load_profile_boiler_fuel import LoadProfileBoilerFuel
from reo.models import URDBError
from reo.nested_inputs import nested_input_definitions
from reo.api import UUIDFilter
from reo.models import ModelManager
from reo.exceptions import UnexpectedError  #, RequestError  # should we save bad requests? could be sql injection attack?
import logging
log = logging.getLogger(__name__)
from reo.src.techs import Generator
from reo.src.emissions_calculator import EmissionsCalculator
from django.http import HttpResponse
from django.template import  loader
from input_files.CHP import chp_input_defaults


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



def annual_mmbtu(request):
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

        b = LoadProfileBoilerFuel(dfm=None, latitude=latitude, longitude=longitude,
                                  doe_reference_name=[doe_reference_name], time_steps_per_hour=1)
        
        response = JsonResponse(
            {'annual_mmbtu': b.annual_mmbtu,
             'city': b.nearest_city},
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
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected Error. Please contact reopt@nrel.gov."})        


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
            return JsonResponse({"Error": str(e.args[0])})
    
    except KeyError as e:
        return JsonResponse({"Error. Missing Parameter": str(e.args[0])})

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])})

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.error(debug_msg)
        return JsonResponse({"Error": "Unexpected Error. Please check your input parameters and contact reopt@nrel.gov if problems persist."})


def simulated_load(request):
    try:
        latitude = float(request.GET['latitude'])  # need float to convert unicode
        longitude = float(request.GET['longitude'])
        doe_reference_name = request.GET['doe_reference_name']
        load_type = request.GET.get('load_type')

        if load_type is None:
            load_type = 'electric'

        if latitude > 90 or latitude < -90:
            raise ValueError("latitude out of acceptable range (-90 <= latitude <= 90)")

        if longitude > 180 or longitude < -180:
            raise ValueError("longitude out of acceptable range (-180 <= longitude <= 180)")

        if load_type not in ['electric','heating','cooling']:
            raise ValueError("load_type parameter must be one of the folloing: 'heating', 'cooling', or 'electric'."
                             " If load_type is not specified, 'electric' is assumed.")

        if load_type == "electric":
            if doe_reference_name not in BuiltInProfile.default_buildings:
                raise ValueError("Invalid doe_reference_name. Select from the following: {}"
                             .format(BuiltInProfile.default_buildings))

            try:  # annual_kwh is optional. if not provided, then DOE reference value is used.
                annual_kwh = float(request.GET['annual_kwh'])
            except KeyError:
                annual_kwh = None
            
            try:  # monthly_totals_kwh is optional. if not provided, then DOE reference value is used.
                monthly_totals_kwh = None
                if 'monthly_totals_kwh' in request.GET.keys():
                    string_array = request.GET.get('monthly_totals_kwh')
                    if string_array is not None:
                        monthly_totals_kwh = [float(v) for v in string_array.strip('[]').split(',')]
                elif 'monthly_totals_kwh[0]' in request.GET.keys():
                    monthly_totals_kwh  = [request.GET.get('monthly_totals_kwh[{}]'.format(i)) for i in range(12)]
                    if None in monthly_totals_kwh:
                        bad_index = monthly_totals_kwh.index(None)
                        raise ValueError("monthly_totals_kwh must contain a value for each month. {} is null".format('monthly_totals_kwh[{}]'.format(bad_index)))
                    monthly_totals_kwh = [float(i) for i in monthly_totals_kwh]
                    
            except KeyError:
                monthly_totals_kwh = None
            
            b = LoadProfile(dfm=None, latitude=latitude, longitude=longitude, doe_reference_name=[doe_reference_name],
                           annual_kwh=annual_kwh, monthly_totals_kwh=monthly_totals_kwh, critical_load_pct=0)
            
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

        if load_type == "heating":

            if doe_reference_name not in BuiltInProfile.default_buildings:
                raise ValueError("Invalid doe_reference_name. Select from the following: {}"
                             .format(BuiltInProfile.default_buildings))

            try:  # annual_kwh is optional. if not provided, then DOE reference value is used.
                annual_mmbtu = float(request.GET['annual_mmbtu'])
            except KeyError:
                annual_mmbtu = None

            try:  # monthly_totals_kwh is optional. if not provided, then DOE reference value is used.
                monthly_mmbtu = None
                if 'monthly_mmbtu' in request.GET.keys():
                    string_array = request.GET.get('monthly_mmbtu')
                    if string_array is not None:
                        monthly_mmbtu = [float(v) for v in string_array.strip('[]').split(',')]
                elif 'monthly_mmbtu[0]' in request.GET.keys():
                    monthly_mmbtu  = [request.GET.get('monthly_mmbtu[{}]'.format(i)) for i in range(12)]
                    if None in monthly_mmbtu:
                        bad_index = monthly_mmbtu.index(None)
                        raise ValueError("monthly_mmbtu must contain a value for each month. {} is null".format('monthly_mmbtu[{}]'.format(bad_index)))
                    monthly_mmbtu = [float(i) for i in monthly_mmbtu]
            except KeyError:
                monthly_mmbtu = None

            b = LoadProfileBoilerFuel(dfm=None, latitude=latitude, longitude=longitude, doe_reference_name=[doe_reference_name],
                           annual_mmbtu=annual_mmbtu, monthly_mmbtu=monthly_mmbtu, time_steps_per_hour=1)
            
            lp = b.built_in_profile
            
            response = JsonResponse(
                {'loads_mmbtu': [round(ld, 3) for ld in lp],
                 'annual_mmbtu': b.annual_mmbtu,
                 'min_mmbtu': round(min(lp), 3),
                 'mean_mmbtu': round(sum(lp) / len(lp), 3),
                 'max_mmbtu': round(max(lp), 3),
                 }
                )

            return response

        if load_type == "cooling":

            if request.GET.get('annual_fraction') is not None:  # annual_kwh is optional. if not provided, then DOE reference value is used.
                
                annual_fraction = float(request.GET['annual_fraction'])

                lp = [0.5]*8760
                
                response = JsonResponse(
                    {'loads_fraction': [round(ld, 3) for ld in lp],
                     'annual_fraction': round(sum(lp) / len(lp), 3),
                     'min_fraction': round(min(lp), 3),
                     'mean_fraction': round(sum(lp) / len(lp), 3),
                     'max_fraction': round(max(lp), 3),
                     }
                    )

                return response

            if (request.GET.get('monthly_fraction') is not None) or (request.GET.get('monthly_fraction[0]') is not None):  # annual_kwh is optional. if not provided, then DOE reference value is used.
                
                if 'monthly_fraction' in request.GET.keys():                
                    string_array = request.GET.get('monthly_fraction')
                    monthly_fraction = [float(v) for v in string_array.strip('[]').split(',')]

                elif 'monthly_fraction[0]' in request.GET.keys():
                    monthly_fraction  = [request.GET.get('monthly_fraction[{}]'.format(i)) for i in range(12)]
                    if None in monthly_fraction:
                        bad_index = monthly_fraction.index(None)
                        raise ValueError("monthly_fraction must contain a value for each month. {} is null".format('monthly_fraction[{}]'.format(bad_index)))
                    monthly_fraction = [float(i) for i in monthly_fraction]
                

                days_in_month = {   0:31,
                                    1:28,
                                    2:31,
                                    3:30,
                                    4:31,
                                    5:30,
                                    6:31,
                                    7:31,
                                    8:30,
                                    9:31,
                                    10:30,
                                    11:31}
                lp = []
                for i in range(12):
                    lp += [monthly_fraction[i]] * days_in_month[i] *24
                
                response = JsonResponse(
                    {'loads_fraction': [round(ld, 3) for ld in lp],
                     'annual_fraction': round(sum(lp) / len(lp), 3),
                     'min_fraction': round(min(lp), 3),
                     'mean_fraction': round(sum(lp) / len(lp), 3),
                     'max_fraction': round(max(lp), 3),
                     }
                    )

                return response
            
            if doe_reference_name not in BuiltInProfile.default_buildings:
                raise ValueError("Invalid doe_reference_name. Select from the following: {}"
                             .format(BuiltInProfile.default_buildings))
                
            b = BuiltInProfile(
                    {},
                    "Cooling8760_fraction_",
                    latitude = latitude,
                    longitude = longitude,
                    doe_reference_name = doe_reference_name,                    
                    annual_energy = 1,
                    monthly_totals_energy = None)

            
            lp = b.built_in_profile
            
            response = JsonResponse(
                {'loads_fraction': [round(ld, 3) for ld in lp],
                 'annual_fraction': round(sum(lp) / len(lp), 3),
                 'min_fraction': round(min(lp), 3),
                 'mean_fraction': round(sum(lp) / len(lp), 3),
                 'max_fraction': round(max(lp), 3),
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

def chp_defaults(request):
    """
    This provides the default input values for CHP based the following:
        1. Prime mover and size class
        2. Prime mover and average heating load
    If both size class and average heating load are given, the size class will be used.
    Boiler efficiency is assumed and may not be consistent with actual input value.
    """
    chp_defaults_dict_pickle = os.path.join('input_files', 'CHP', 'chp_input_defaults_all.pickle')
    with open(chp_defaults_dict_pickle, 'rb') as handle:
        prime_mover_defaults_all = pickle.load(handle)

    try:
        prime_mover = request.GET.get('prime_mover')
        avg_boiler_fuel_load_mmbtu_per_hr = request.GET.get('avg_boiler_fuel_load_mmbtu_per_hr')
        size_class = request.GET.get('size_class')

        if prime_mover is not None:
            # Calculate heuristic CHP size based on average thermal load, using average efficiencies across all size ranges
            if avg_boiler_fuel_load_mmbtu_per_hr is not None:
                avg_boiler_fuel_load_mmbtu_per_hr = float(avg_boiler_fuel_load_mmbtu_per_hr)
                boiler_effic = 0.8
                therm_effic = prime_mover_defaults_all[prime_mover]['thermal_effic_full_load'][0]
                elec_effic = prime_mover_defaults_all[prime_mover]['elec_effic_full_load'][0]
                avg_heating_thermal_load_mmbtu_per_hr = avg_boiler_fuel_load_mmbtu_per_hr * boiler_effic
                chp_fuel_rate_mmbtu_per_hr = avg_heating_thermal_load_mmbtu_per_hr / therm_effic
                chp_elec_size_heuristic_kw = chp_fuel_rate_mmbtu_per_hr * elec_effic * 1.0E6 / 3412.0
            else:
                chp_elec_size_heuristic_kw = None
            # If size class is specified use that and ignore heuristic CHP sizing for determining size class
            if size_class is not None:
                size_class = int(size_class)
                if (size_class < 0) or (size_class >= chp_input_defaults.n_classes[prime_mover]):
                    raise ValueError('The size class input is outside the valid range for ' + str(prime_mover))
            # If size class is not specified, heuristic sizing based on avg thermal load and size class 0 efficiencies
            elif avg_boiler_fuel_load_mmbtu_per_hr is not None and size_class is None:
                # With heuristic size, find the suggested size class
                if chp_elec_size_heuristic_kw < chp_input_defaults.class_bounds[prime_mover][1][1]:
                    # If smaller than the upper bound of the smallest class, assign the smallest class
                    size_class = 1
                elif chp_elec_size_heuristic_kw >= chp_input_defaults.class_bounds[prime_mover][chp_input_defaults.n_classes[prime_mover] - 1][0]:
                    # If larger than or equal to the lower bound of the largest class, assign the largest class
                    size_class = chp_input_defaults.n_classes[prime_mover] - 1  # Size classes are zero-indexed
                else:
                    # For middle size classes
                    for sc in range(2, chp_input_defaults.n_classes[prime_mover] - 1):
                        if (chp_elec_size_heuristic_kw >= chp_input_defaults.class_bounds[prime_mover][sc][0]) and \
                                (chp_elec_size_heuristic_kw < chp_input_defaults.class_bounds[prime_mover][sc][1]):
                            size_class = sc
            else:
                size_class = chp_input_defaults.default_chp_size_class[prime_mover]
            prime_mover_defaults = {param: prime_mover_defaults_all[prime_mover][param][size_class]
                                    for param in prime_mover_defaults_all[prime_mover].keys()}
        else:
            raise ValueError("Missing prime_mover type query parameter.")

        response = JsonResponse(
            {"prime_mover": prime_mover,
             "size_class": size_class,
             "default_inputs": prime_mover_defaults,
             "chp_size_based_on_avg_heating_load_kw": chp_elec_size_heuristic_kw,
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
        return JsonResponse({"Error": "Unexpected Error. Please contact reopt@nrel.gov."}, status=500)