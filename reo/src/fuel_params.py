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
import os
import operator
import calendar
import numpy
import logging
log = logging.getLogger(__name__)

class FuelParams:
    """
    Sub-function of DataManager.

    Used for fuel burning parameters, fuel cost, and CHP thermal production and power derate

    """
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    def __init__(self, big_number, fuel_tariff, generator=None, chp=None, boiler=None):
        self.big_number = big_number

        # Make certain techs an attribute of this class
        self.generator = generator
        self.chp = chp
        self.boiler = boiler

        self.fuel_costs = []
        self.fuel_costs_bau = []
        self.fuel_burn_slope = []
        self.fuel_burn_slope_bau = []
        self.fuel_burn_intercept = []
        self.fuel_burn_intercept_bau = []
        self.fuel_limit = []
        self.fuel_limit_bau = []

        # Assign monthly fuel rates for boiler and chp and then convert to timestep intervals
        self.boiler_fuel_blended_monthly_rates_us_dollars_per_mmbtu = fuel_tariff.monthly_rates('boiler')
        self.chp_fuel_blended_monthly_rates_us_dollars_per_mmbtu = fuel_tariff.monthly_rates('chp')
        self.chp_fuel_rate_array = []
        self.boiler_fuel_rate_array = []
        for month in range(0, 12):
            # Create full length (timestep) array of NG cost in $/MMBtu
            self.boiler_fuel_rate_array.extend([self.boiler_fuel_blended_monthly_rates_us_dollars_per_mmbtu[month]] *
                                      self.days_in_month[month] * 24 * self.time_steps_per_hour)
            self.chp_fuel_rate_array.extend([self.chp_fuel_blended_monthly_rates_us_dollars_per_mmbtu[month]] *
                                      self.days_in_month[month] * 24 * self.time_steps_per_hour)
            if self.generator is not None:
                self.generator_fuel_rate_array = [self.generator.diesel_fuel_cost_us_dollars_per_gallon for _ in range(8760 * self.time_steps_per_hour)]

        # Unique parameters for CHP
        if chp is not None:
            self.chp_fuel_burn_intercept = [chp.fuel_burn_intercept]
            self.chp_thermal_prod_slope = [chp.thermal_prod_slope]
            self.chp_thermal_prod_intercept = [chp.thermal_prod_intercept]
            self.chp_derate = [chp.derate]
        else:
            self.chp_fuel_burn_intercept = list()
            self.chp_thermal_prod_slope = list()
            self.chp_thermal_prod_intercept = list()
            self.chp_derate = list()

    def _get_fuel_burning_tech_params(self, techs):
        """
        In the Julia model we have:
         - FuelCost = AxisArray(d["FuelCost"], d["FuelType"])
         - FuelLimit: AxisArray(d["FuelLimit"], d["FuelType"])
         - FuelType: Array{String,1}
         - TechsByFuelType: AxisArray(d["TechsByFuelType"], d["FuelType"])
        :return: fuel_costs, fuel_limit, fuel_types, techs_by_fuel_type (all lists)
        """

        for tech in techs:
            # have to rubber stamp other tech values for each energy tier so that array is filled appropriately
            if tech.lower() == 'generator':
                # generator fuel is not free anymore since generator is also a design variable
                self.fuel_costs = operator.add(self.fuel_costs, self.generator_fuel_rate_array)
                self.fuel_burn_slope.append(self.generator.fuel_slope)
                self.fuel_burn_intercept.append(self.generator.fuel_intercept)
                self.fuel_limit.append(self.generator_fuel_avail)
                # TODO figure out how to populate fuel costs for all fb techs
                self.techs_by_fuel_type.append([tech.upper()])
                self.fuel_types.append("DIESEL")
            elif tech.lower() == 'boiler':
                self.fuel_costs = operator.add(self.fuel_costs, self.boiler_fuel_rate_array)
                self.fuel_burn_slope.append(1 / self.boiler_efficiency)
                self.fuel_limit.append(self.big_number)
                self.techs_by_fuel_type.append([tech.upper()])
                self.fuel_types.append("BOILERFUEL")
            elif tech.lower() == 'chp':
                self.fuel_costs = operator.add(self.fuel_costs, self.chp_fuel_rate_array)
                self.fuel_burn_slope.append(self.chp.fuel_burn_slope)
                self.fuel_burn_intercept.append(self.chp.fuel_burn_intercept[0])
                self.fuel_limit.append(self.big_number)
                self.techs_by_fuel_type.append([tech.upper()])
                self.fuel_types.append("CHPFUEL")


        return self.fuel_costs, self.fuel_limit, self.fuel_types, self.techs_by_fuel_type, self.fuel_burn_rate, \
               self.fuel_burn_intercept