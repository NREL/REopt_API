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
class FuelTariff(object):
    """
    Contains information relevant to construct a fuel tariff

    """

    def __init__(self, dfm, time_steps_per_hour, existing_boiler_fuel_type=None,
                 boiler_fuel_blended_annual_rates_us_dollars_per_mmbtu=None,
                 boiler_fuel_blended_monthly_rates_us_dollars_per_mmbtu=None,
                 chp_fuel_type=None, chp_fuel_blended_annual_rates_us_dollars_per_mmbtu=None,
                 chp_fuel_blended_monthly_rates_us_dollars_per_mmbtu=None, **kwargs):

        self.time_steps_per_hour = time_steps_per_hour
        self.existing_boiler_fuel_type = existing_boiler_fuel_type
        self.boiler_fuel_blended_annual_rates_us_dollars_per_mmbtu = boiler_fuel_blended_annual_rates_us_dollars_per_mmbtu
        self.boiler_fuel_blended_monthly_rates_us_dollars_per_mmbtu = boiler_fuel_blended_monthly_rates_us_dollars_per_mmbtu

        self.chp_fuel_type = chp_fuel_type
        self.chp_fuel_blended_annual_rates_us_dollars_per_mmbtu = chp_fuel_blended_annual_rates_us_dollars_per_mmbtu
        self.chp_fuel_blended_monthly_rates_us_dollars_per_mmbtu = chp_fuel_blended_monthly_rates_us_dollars_per_mmbtu

        dfm.add_fuel_tariff(self)

    def fuel_emissions(self):
        # Insert CO2 emissions calculations?
        pass

    # Depending on the user input for fuel cost, whether monthly or annual, convert to monthly
    def monthly_rates(self, tech):
        if sum(eval('self.' + tech + '_fuel_blended_monthly_rates_us_dollars_per_mmbtu')) >= 0.01:
            monthly_rate = eval('self.' + tech + '_fuel_blended_monthly_rates_us_dollars_per_mmbtu')
        else:
            monthly_rate = [eval('self.' + tech + '_fuel_blended_annual_rates_us_dollars_per_mmbtu')] * 12

        return monthly_rate


