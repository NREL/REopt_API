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
from reo.src.load_profile import BuiltInProfile, LoadProfile
from reo.src.load_profile_boiler_fuel import LoadProfileBoilerFuel
from reo.models import URDBError
from reo.nested_inputs import nested_input_definitions
from reo.api import UUIDFilter
from reo.models import ModelManager
from reo.exceptions import UnexpectedError  #, RequestError  # should we save bad requests? could be sql injection attack?
from reo.src.emissions_calculator import EmissionsCalculator
import logging
log = logging.getLogger(__name__)
from reo.src.techs import Generator, CHP, ElectricChiller, AbsorptionChiller, Boiler
from reo.src.emissions_calculator import EmissionsCalculator
from django.http import HttpResponse
from django.template import  loader
import pandas as pd
import numpy as np
import calendar
import datetime


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


def health(request):
    return HttpResponse("OK")


def errors(request, page_uuid):

    template= loader.get_template("errors.html")
    return HttpResponse(template.render())


def help(request):

    try:
        response = copy.deepcopy(nested_input_definitions)
        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({"Error": "Unexpected error in help endpoint: {}".format(e.args[0])}, status=500)


def invalid_urdb(request):

    try:
        # invalid set is populated by the urdb validator, hard problems defined in csv
        invalid_set = list(set([i.label for i in URDBError.objects.filter(type='Error')]))
        return JsonResponse({"Invalid IDs": list(set(invalid_set + hard_problem_labels))})

    except Exception as e:
        return JsonResponse({"Error": "Unexpected error in invalid_urdb endpoint: {}".format(e.args[0])}, status=500)


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
        return JsonResponse({"Error. Missing": str(e.args[0])}, status=500)

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=500)

    except Exception as e:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in annual_kwh endpoint. Check log for more."}, status=500)



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
        return JsonResponse({"Error. Missing": str(e.args[0])}, status=500)

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=500)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected Error. Please contact reopt@nrel.gov."}, status=500)


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
        return JsonResponse(resp, status=500)


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


def simulated_load(request):
    try:
        latitude = float(request.GET['latitude'])  # need float to convert unicode
        longitude = float(request.GET['longitude'])
        load_type = request.GET.get('load_type')

        if 'doe_reference_name' in request.GET.keys():
            doe_reference_name = [request.GET.get('doe_reference_name')]
            percent_share_list = [100.0]
        elif 'doe_reference_name[0]' in request.GET.keys():
            idx = 0
            doe_reference_name = []
            percent_share_list = []
            while 'doe_reference_name[{}]'.format(idx) in request.GET.keys():
                doe_reference_name.append(request.GET['doe_reference_name[{}]'.format(idx)])
                if 'percent_share[{}]'.format(idx) not in request.GET.keys():
                    raise ValueError("The number of percent_share entries does not match that of the number of doe_reference_name entries")
                percent_share_list.append(float(request.GET['percent_share[{}]'.format(idx)]))
                idx += 1
        else:
            doe_reference_name = None

        if doe_reference_name is not None:
            for drn in doe_reference_name:
                if drn not in BuiltInProfile.default_buildings:
                    raise ValueError("Invalid doe_reference_name - {}. Select from the following: {}"
                             .format(drn, BuiltInProfile.default_buildings))

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
            #Annual loads
            if 'annual_kwh' in request.GET.keys():
                annual_kwh = [float(request.GET.get('annual_kwh'))]
            elif 'annual_kwh[0]' in request.GET.keys():
                idx = 0
                annual_kwh = []
                while 'annual_kwh[{}]'.format(idx) in request.GET.keys():
                    annual_kwh.append(float(request.GET['annual_kwh[{}]'.format(idx)]))
                    idx += 1
            else:
                annual_kwh = None

            if annual_kwh is not None:
                if len(annual_kwh) != len(doe_reference_name):
                    raise ValueError("The number of annual_kwh entries does not match that of the number of doe_reference_name entries")

            #Monthly loads
            monthly_totals_kwh = None
            if 'monthly_totals_kwh' in request.GET.keys():
                monthly_totals_kwh = [float(request.GET.get('monthly_totals_kwh'))]
            elif 'monthly_totals_kwh[0]' in request.GET.keys():
                monthly_totals_kwh  = [request.GET.get('monthly_totals_kwh[{}]'.format(i)) for i in range(12)]
                if None in monthly_totals_kwh:
                    bad_index = monthly_totals_kwh.index(None)
                    raise ValueError("monthly_totals_kwh must contain a value for each month. {} is null".format('monthly_totals_kwh[{}]'.format(bad_index)))
                monthly_totals_kwh = [float(i) for i in monthly_totals_kwh]
            else:
                monthly_totals_kwh = None

            b = LoadProfile(dfm=None, latitude=latitude, longitude=longitude, doe_reference_name=doe_reference_name,
                           annual_kwh=annual_kwh, monthly_totals_kwh=monthly_totals_kwh, critical_load_pct=0,
                           percent_share=percent_share_list)

            lp = b.load_list

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

            #Annual loads
            if 'annual_mmbtu' in request.GET.keys():
                annual_mmbtu = [float(request.GET.get('annual_mmbtu'))]
            elif 'annual_mmbtu[0]' in request.GET.keys():
                idx = 0
                annual_mmbtu = []
                while 'annual_mmbtu[{}]'.format(idx) in request.GET.keys():
                    annual_mmbtu.append(float(request.GET['annual_mmbtu[{}]'.format(idx)]))
                    idx += 1
            else:
                annual_mmbtu = None

            if annual_mmbtu is not None:
                if len(annual_mmbtu) != len(doe_reference_name):
                    raise ValueError("The number of annual_mmbtu entries does not match that of the number of doe_reference_name entries")

            #Monthly loads
            if 'monthly_mmbtu' in request.GET.keys():
                monthly_mmbtu = [float(request.GET.get('monthly_mmbtu'))]
            elif 'monthly_mmbtu[0]' in request.GET.keys():
                monthly_mmbtu  = [request.GET.get('monthly_mmbtu[{}]'.format(i)) for i in range(12)]
                if None in monthly_mmbtu:
                    bad_index = monthly_mmbtu.index(None)
                    raise ValueError("monthly_mmbtu must contain a value for each month. {} is null".format('monthly_mmbtu[{}]'.format(bad_index)))
                monthly_mmbtu = [float(i) for i in monthly_mmbtu]
            else:
                monthly_mmbtu = None

            b = LoadProfileBoilerFuel(dfm=None, latitude=latitude, longitude=longitude, doe_reference_name=doe_reference_name,
                           annual_mmbtu=annual_mmbtu, monthly_mmbtu=monthly_mmbtu, time_steps_per_hour=1,
                           percent_share_list=percent_share_list)

            lp = b.load_list

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

                lp = [annual_fraction]*8760

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


            if doe_reference_name is not None:
                if len(doe_reference_name) > 1:
                    raise ValueError("Cooling load series does not support hybrid load profiles")

                doe_reference_name = doe_reference_name[0]

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

            else:
                raise ValueError("Please supply an annual_fraction, monthly_fraction series or doe_reference_name")

    except KeyError as e:
        return JsonResponse({"Error. Missing": str(e.args[0])}, status=500)

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=500)

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.error(debug_msg)
        return JsonResponse({"Error": "Unexpected Error. Please check your input parameters and contact reopt@nrel.gov if problems persist."}, status=500)


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
        return JsonResponse({"Error": str(e.args[0])}, status=500)

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in generator_efficiency endpoint. Check log for more."}, status=500)

def chp_defaults(request):
    """
    This provides the default input values for CHP based the following:
        1. Prime mover and size class
        2. Prime mover and average heating load
    If both size class and average heating load are given, the size class will be used.
    Boiler efficiency is assumed and may not be consistent with actual input value.

    The year input is required for getting the chp_unavailability_hourly series output, otherwise it will return [] for that.
    """
    prime_mover_defaults_all = copy.deepcopy(CHP.prime_mover_defaults_all)
    n_classes = {pm: len(CHP.class_bounds[pm]) for pm in CHP.class_bounds.keys()}

    try:
        prime_mover = request.GET.get('prime_mover')
        avg_boiler_fuel_load_mmbtu_per_hr = request.GET.get('avg_boiler_fuel_load_mmbtu_per_hr')
        size_class = request.GET.get('size_class')
        year = request.GET.get('year')
        if prime_mover is not None:
            # Calculate heuristic CHP size based on average thermal load, using the default size class efficiency data
            if avg_boiler_fuel_load_mmbtu_per_hr is not None:
                avg_boiler_fuel_load_mmbtu_per_hr = float(avg_boiler_fuel_load_mmbtu_per_hr)
                boiler_effic = 0.8
                therm_effic = prime_mover_defaults_all[prime_mover]['thermal_effic_full_load'][CHP.default_chp_size_class[prime_mover]]
                elec_effic = prime_mover_defaults_all[prime_mover]['elec_effic_full_load'][CHP.default_chp_size_class[prime_mover]]
                avg_heating_thermal_load_mmbtu_per_hr = avg_boiler_fuel_load_mmbtu_per_hr * boiler_effic
                chp_fuel_rate_mmbtu_per_hr = avg_heating_thermal_load_mmbtu_per_hr / therm_effic
                chp_elec_size_heuristic_kw = chp_fuel_rate_mmbtu_per_hr * elec_effic * 1.0E6 / 3412.0
            else:
                chp_elec_size_heuristic_kw = None
            # If size class is specified use that and ignore heuristic CHP sizing for determining size class
            if size_class is not None:
                size_class = int(size_class)
                if (size_class < 0) or (size_class >= n_classes[prime_mover]):
                    raise ValueError('The size class input is outside the valid range for ' + str(prime_mover))
            # If size class is not specified, heuristic sizing based on avg thermal load and size class 0 efficiencies
            elif avg_boiler_fuel_load_mmbtu_per_hr is not None and size_class is None:
                # With heuristic size, find the suggested size class
                if chp_elec_size_heuristic_kw < CHP.class_bounds[prime_mover][1][1]:
                    # If smaller than the upper bound of the smallest class, assign the smallest class
                    size_class = 1
                elif chp_elec_size_heuristic_kw >= CHP.class_bounds[prime_mover][n_classes[prime_mover] - 1][0]:
                    # If larger than or equal to the lower bound of the largest class, assign the largest class
                    size_class = n_classes[prime_mover] - 1  # Size classes are zero-indexed
                else:
                    # For middle size classes
                    for sc in range(2, n_classes[prime_mover] - 1):
                        if (chp_elec_size_heuristic_kw >= CHP.class_bounds[prime_mover][sc][0]) and \
                                (chp_elec_size_heuristic_kw < CHP.class_bounds[prime_mover][sc][1]):
                            size_class = sc
            else:
                size_class = CHP.default_chp_size_class[prime_mover]
            prime_mover_defaults = {param: prime_mover_defaults_all[prime_mover][param][size_class]
                                    for param in prime_mover_defaults_all[prime_mover].keys()}
            if year is not None:
                year = int(year)
                # TODO put in "prime_mover" instead of hard-coded "recip_engine" for path (after adding other prime_mover unavailability periods)
                chp_unavailability_path = os.path.join('input_files', 'CHP', 'recip_engine_unavailability_periods.csv')
                chp_unavailability_periods = pd.read_csv(chp_unavailability_path)
                if calendar.isleap(year):  # Remove last day of the year if leap year
                    end_date = "12/31/"+str(year)
                else:
                    end_date = "1/1/"+str(year+1)
                dt_profile = pd.date_range(start='1/1/'+str(year), end=end_date, freq="1H", closed="left")
                chp_unavailability_hourly = pd.Series(np.zeros(8760), index=dt_profile)
                for i in range(len(chp_unavailability_periods)):
                    month = chp_unavailability_periods["Month"][i]
                    day_of_month = calendar.Calendar().monthdayscalendar(year=year,month=month)[chp_unavailability_periods["Start Week of Month"][i]][chp_unavailability_periods["Start Day of Week"][i]]
                    hour_of_day = chp_unavailability_periods["Start Hour"][i]
                    start_datetime = datetime.datetime(year=year, month=month, day=day_of_month, hour=hour_of_day)
                    duration = pd.to_timedelta(chp_unavailability_periods["Duration"][i])
                    chp_unavailability_hourly[start_datetime:start_datetime+duration-datetime.timedelta(hours=1)] = 1.0
                    chp_unavailability_hourly_list = list(chp_unavailability_hourly)
            else:
                chp_unavailability_hourly_list = []
        else:
            raise ValueError("Missing prime_mover type query parameter.")

        response = JsonResponse(
            {"prime_mover": prime_mover,
             "size_class": size_class,
             "default_inputs": prime_mover_defaults,
             "chp_size_based_on_avg_heating_load_kw": chp_elec_size_heuristic_kw,
             "size_class_bounds": CHP.class_bounds,
             "chp_unavailability_hourly": chp_unavailability_hourly_list
             }
        )
        return response

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=500)

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in chp_defaults endpoint. Check log for more."}, status=500)


def chiller_defaults(request):
    """
    This provides the following default parameters for electric and absorption chiller:
        1. COP of electric chiller (ElectricChiller.chiller_cop) based on peak cooling thermal load
        2. COP of absorption chiller (AbsorptionChiller.chiller_cop) based on hot_water_or_steam input or prime_mover
            CapEx (AbsorptionChiller.installed_cost_us_dollars_per_ton) and
                OpEx (AbsorptionChiller.om_cost_us_dollars_per_ton) of absorption chiller based on peak cooling thermal
                load

    Required inputs:
        1. max_elec_chiller_elec_load

    Optional inputs:
        1. hot_water_or_steam (Boiler.existing_boiler_production_type_steam_or_hw)
            a. If not provided, hot_water is assumed
        2. prime_mover (CHP.prime_mover)
            a. If hot_water_or_steam is provided, this is not used
            b. If hot_water_or_steam is NOT provided and prime_mover is, this will refer to
                boiler_type_by_chp_pm_defaults
        3. Max cooling capacity (ElectricChiller.max_thermal_factor_on_peak_load) as a ratio of peak cooling load
            a. If not entered, assume 1.25

    """
    elec_chiller_cop_defaults = copy.deepcopy(ElectricChiller.electric_chiller_cop_defaults)
    absorp_chiller_cost_defaults_all = copy.deepcopy(AbsorptionChiller.absorption_chiller_cost_defaults)
    absorp_chiller_cop_defaults = copy.deepcopy(AbsorptionChiller.absorption_chiller_cop_defaults)
    boiler_type_by_chp_pm_defaults = copy.deepcopy(Boiler.boiler_type_by_chp_prime_mover_defaults)

    try:
        max_elec_chiller_elec_load = request.GET.get('max_elec_chiller_elec_load')
        hot_water_or_steam = request.GET.get('hot_water_or_steam')
        prime_mover = request.GET.get('prime_mover')
        max_cooling_factor = request.GET.get('max_cooling_factor', 1.25)

        if max_elec_chiller_elec_load is None:
            raise ValueError("Missing required max_elec_chiller_elec_load query parameter.")
        else:
            max_chiller_thermal_capacity = float(max_elec_chiller_elec_load) * \
                                            elec_chiller_cop_defaults['convert_elec_to_thermal'] / 3.51685 * \
                                            float(max_cooling_factor)
            max_cooling_load_tons = float(max_elec_chiller_elec_load) * \
                                            elec_chiller_cop_defaults['convert_elec_to_thermal'] / 3.51685

            # Electric chiller COP
            if max_chiller_thermal_capacity < 100.0:
                elec_chiller_cop = elec_chiller_cop_defaults["less_than_100_tons"]
            else:
                elec_chiller_cop = elec_chiller_cop_defaults["greater_than_100_tons"]

            # Absorption chiller costs
            if hot_water_or_steam is not None:
                defaults_sizes = absorp_chiller_cost_defaults_all[hot_water_or_steam]
                absorp_chiller_cop = absorp_chiller_cop_defaults[hot_water_or_steam]
            elif prime_mover is not None:
                defaults_sizes = absorp_chiller_cost_defaults_all[boiler_type_by_chp_pm_defaults[prime_mover]]
                absorp_chiller_cop = absorp_chiller_cop_defaults[boiler_type_by_chp_pm_defaults[prime_mover]]
            else:
                # If hot_water_or_steam and CHP prime_mover are not provided, use hot_water defaults
                defaults_sizes = absorp_chiller_cost_defaults_all["hot_water"]
                absorp_chiller_cop = absorp_chiller_cop_defaults["hot_water"]

            if max_cooling_load_tons <= defaults_sizes[0][0]:
                absorp_chiller_capex = defaults_sizes[0][1]
                absorp_chiller_opex = defaults_sizes[0][2]
            elif max_cooling_load_tons >= defaults_sizes[-1][0]:
                absorp_chiller_capex = defaults_sizes[-1][1]
                absorp_chiller_opex = defaults_sizes[-1][2]
            else:
                for size in range(1, len(defaults_sizes)):
                    if max_cooling_load_tons > defaults_sizes[size - 1][0] and \
                            max_cooling_load_tons <= defaults_sizes[size][0]:
                        slope_capex = (defaults_sizes[size][1] - defaults_sizes[size - 1][1]) / \
                                      (defaults_sizes[size][0] - defaults_sizes[size - 1][0])
                        slope_opex = (defaults_sizes[size][2] - defaults_sizes[size - 1][2]) / \
                                     (defaults_sizes[size][0] - defaults_sizes[size - 1][0])
                        absorp_chiller_capex = defaults_sizes[size - 1][1] + slope_capex * \
                                               (max_cooling_load_tons - defaults_sizes[size - 1][0])
                        absorp_chiller_opex = defaults_sizes[size - 1][2] + slope_opex * \
                                              (max_cooling_load_tons - defaults_sizes[size - 1][0])

        response = JsonResponse(
            {"PeakCoolingLoadTons": max_cooling_load_tons,
                "ElectricChiller": {
                 "MaxCapacityTons": max_chiller_thermal_capacity,
                 "chiller_cop": elec_chiller_cop
                },
            "AbsorptionChiller": {
                "chiller_cop": absorp_chiller_cop,
                "installed_cost_us_dollars_per_ton": absorp_chiller_capex,
                "om_cost_us_dollars_per_ton": absorp_chiller_opex
                }
            }
        )

        return response

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=500)

    except Exception:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in chiller_defaults endpoint. Check log for more."}, status=500)
