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
import re
import copy
import logging
import pandas as pd
import numpy as np
log = logging.getLogger(__name__)


class ResourceAdequacy(object):

    def __init__(self, dfm, run_id, load_year, ra_energy_pricing_us_dollars_per_kwh=None, ra_demand_pricing_us_dollars_per_kw=None,
                 ra_event_day_flags_boolean=None, ra_lookback_days=None, **kwargs):
        """
        Re object for creating inputs to REopt
        :param dfm: Object, DataManager
        :param run_id: str, run uuid
        :param ra_energy_pricing_us_dollars_per_kwh: list of float, length = 8760
        :param ra_demand_pricing_us_dollars_per_kw: list of float, length = 12
        :param ra_event_day_flags_boolean: list of int (0/1's), length = 8760
        :param ra_lookback_days: float
        :param load_year: int
        :param kwargs:  not used
        """
        self.run_id = run_id
        self.ra_energy_pricing = ra_energy_pricing_us_dollars_per_kwh
        self.ra_event_day_flags = ra_event_day_flags_boolean
        self.ra_lookback_days = ra_lookback_days
        self.ra_moo_hours = 4 #must offer obligation window length
        self.load_year = load_year
        #calc event starts and lookback timesteps
        self.ra_event_start_times, self.ra_lookback_periods = self.calculate_event_start_and_lookback()
        #reindex the list based on months that events occur in
        self.ra_demand_pricing = dict()
        for key in self.ra_event_start_times.keys():
            self.ra_demand_pricing[key] = ra_demand_pricing_us_dollars_per_kw[key-1]

        dfm.add_resource_adequacy(self)

    def calculate_event_start_and_lookback(self):

        dti = pd.date_range(str(self.load_year), periods=8760, freq="H")
        df_event_days = pd.DataFrame(self.ra_event_day_flags, dti, columns=['event_day'])
        df_event_days['day_of_week'] = df_event_days.index.dayofweek
        df_event_days['ts'] = np.arange(df_event_days.shape[0])

        ra_event_start_times = dict()
        ra_lookback_periods = dict()

        month_number = 0
        for i in range(len(df_event_days.index)):
            if df_event_days.event_day.values[i]==1:
                if month_number != df_event_days.index[i].month:
                    month_number = df_event_days.index[i].month
                    ra_event_start_times[month_number] = []
                    ra_lookback_periods[month_number] = []
                ra_event_start_times[month_number].append(i)
                
                day = 0
                daysused = 0
                look_back_hours = []
                while daysused <= self.ra_lookback_days-1:
                    if i-day * 24 >= 0:
                        if (df_event_days.day_of_week.values[i-day*24]<5) & (df_event_days.event_day.values[i-day*24]!=True):
                            look_back_hours.append(df_event_days.ts.values[i-day*24])
                            daysused += 1
                    else:
                        if (df_event_days.day_of_week.values[8760 + i-day*24]<5) & (df_event_days.event_day.values[8760 + i-day*24]!=True):
                            look_back_hours.append(df_event_days.ts.values[8760 + i-day*24])
                            daysused += 1
                    day += 1
                ra_lookback_periods[month_number].append(look_back_hours)
       
        return ra_event_start_times, ra_lookback_periods
