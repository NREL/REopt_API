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
import io
import json
import sys
import numpy as np
from django.http import JsonResponse
from reo.exceptions import UnexpectedError


def check_load_builder_inputs(loads_table):
    required_inputs = ["Power (W)", "Quantity", "% Run Time", "Start Mo.", "Stop Mo.", "Start Hr.", "Stop Hr."]
    for load in loads_table:
        inputs = load.keys()
        for required_input in required_inputs:
            if required_input in inputs:
                pass
            else:
                return False
    return True


def validate_load_builder_inputs(loads_table):
    numeric_inputs = ["Power (W)", "Quantity", "% Run Time"]
    hour_inputs = ["Start Hr.", "Stop Hr."]
    month_inputs = ["Start Mo.", "Stop Mo."]
    required_hours = list(np.linspace(0,24,25).astype(int))
    required_months= ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for load in loads_table:

        for numeric_input in numeric_inputs:
            try:
                float(load[numeric_input])
            except:
                return False

        for month_input in month_inputs:
            if load[month_input] not in required_months:
                return False

        for hour_input in hour_inputs:
            if int(load[hour_input]) not in required_hours:
                return False

    return True


def load_builder(request):
    """
    Convert the SolarResilient Component Load Builder CSV into an 8760 Load
    :param request:
    :return: 8760 list for critical_load_kw input into REOpt
    """
    try:
        if request.method == 'POST':
            post = request.body
            try:
                # Try to import JSON, then try to import CSV
                try:
                    loads_table = json.loads(post)
                except:
                    loads_table = post.decode("utf-8")
                finally:
                    if not isinstance(loads_table, list):
                        csv_reader = csv.DictReader(io.StringIO(loads_table))
                        loads_table = list(csv_reader)
            except:
                return JsonResponse({"Error": "Invalid JSON or CSV"})

            # Validation
            if not check_load_builder_inputs(loads_table):
                return JsonResponse({"Error": "There are missing required inputs. Must include the following: 'Power (W)', 'Quantity', '% Run Time', 'Start Mo.', 'Stop Mo.', 'Start Hr.', 'Stop Hr.'"})
            if not validate_load_builder_inputs(loads_table):
                return JsonResponse({"Error": "Some input values are invalid"})

            # Run conversion and respond
            loads_kw = convert_loads(loads_table)
            return JsonResponse({"critical_loads_kw": loads_kw})

        else:
            return JsonResponse({"Error": "Must POST a JSON based on the SolarResilient component based load builder downloadable CSV"})

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = UnexpectedError(exc_type, exc_value, exc_traceback, task='load_builder')
        err.save_to_db()
        return JsonResponse({"Error": err.message}, status=500)


def convert_loads(loads_table):
    """
    Generates critical load profile from critical load builder
    :param loads_table: (json string) contain data from load table
    :return: (1 list) hourly load values (8,760 values) in kw
    """

    class Load:
        def __init__(self, power_total, start_hour, stop_hour, start_month, stop_month):
            self.power_total = power_total
            self.start_hour = start_hour
            self.stop_hour = stop_hour
            self.start_month = start_month
            self.stop_month = stop_month

    def translate_months(string):
        """
        Translate month names to number
        :param string: (str) name of month
        :return: (int) number of month
        """
        switcher = {
            "January": 0,
            "February": 1,
            "March": 2,
            "April": 3,
            "May": 4,
            "June": 5,
            "July": 6,
            "August": 7,
            "September": 8,
            "October": 9,
            "November": 10,
            "December": 11,
        }
        return switcher.get(string, 0)

    loads = []
    for row in loads_table:
        power = int(row["Power (W)"]) * int(row["Quantity"]) * (float(row["% Run Time"]) / 100) / 1000  # total hourly power in kW
        # checks if stop_month has a smaller value than start_month
        start_mo = int(translate_months(row["Start Mo."]))
        stop_mo = int(translate_months(row["Stop Mo."]))
        months = []
        if start_mo < stop_mo:
            months.append((start_mo, stop_mo))
        else:
            months.append((start_mo, 11))
            months.append((0, stop_mo))
        # check if fixture/appliance is running over midnight
        start_hr = int(row["Start Hr."])
        stop_hr = int(row["Stop Hr."])
        hours = []
        if start_hr <= stop_hr:
            hours.append((start_hr, stop_hr))
        else:
            hours.append((start_hr, 24))
            hours.append((0, stop_hr))
        for (start_mo, stop_mo) in months:
            for (start_hr, stop_hr) in hours:
                loads.append(Load(power, start_hr, stop_hr, start_mo, stop_mo))
    loads_kw = []
    days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    for month in range(12):
        number_days = days_per_month[month]
        for days in range(number_days):
            for hr in range(24):
                hour_load = 0
                for load in loads:
                    if load.start_month <= month and load.stop_month >= month:
                        if load.start_hour <= hr and load.stop_hour > hr:
                            hour_load += load.power_total
                loads_kw.append(hour_load)
    return loads_kw
