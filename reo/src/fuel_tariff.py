# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
class FuelTariff(object):
    """
    Contains information relevant to construct a fuel tariff

    """
    # TODO leverage **kwargs and self.xyz = get.kwargs instead of the tedious manual strategy below
    def __init__(self, dfm, time_steps_per_hour, existing_boiler_fuel_type=None,
                 boiler_fuel_percent_RE=None, boiler_fuel_blended_annual_rates_us_dollars_per_mmbtu=None,
                 boiler_fuel_blended_monthly_rates_us_dollars_per_mmbtu=None,
                 chp_fuel_type=None, chp_fuel_percent_RE=None,
                 chp_fuel_blended_annual_rates_us_dollars_per_mmbtu=None,
                 chp_fuel_blended_monthly_rates_us_dollars_per_mmbtu=None,
                 newboiler_fuel_type=None,
                 newboiler_fuel_percent_RE=None,
                 newboiler_fuel_blended_annual_rates_us_dollars_per_mmbtu=None,
                 newboiler_fuel_blended_monthly_rates_us_dollars_per_mmbtu=None,
                 **kwargs):

        self.time_steps_per_hour = time_steps_per_hour
        self.existing_boiler_fuel_type = existing_boiler_fuel_type
        self.boiler_fuel_percent_RE = boiler_fuel_percent_RE
        self.boiler_fuel_blended_annual_rates_us_dollars_per_mmbtu = boiler_fuel_blended_annual_rates_us_dollars_per_mmbtu
        self.boiler_fuel_blended_monthly_rates_us_dollars_per_mmbtu = boiler_fuel_blended_monthly_rates_us_dollars_per_mmbtu

        self.chp_fuel_type = chp_fuel_type
        self.chp_fuel_percent_RE = chp_fuel_percent_RE
        self.chp_fuel_blended_annual_rates_us_dollars_per_mmbtu = chp_fuel_blended_annual_rates_us_dollars_per_mmbtu
        self.chp_fuel_blended_monthly_rates_us_dollars_per_mmbtu = chp_fuel_blended_monthly_rates_us_dollars_per_mmbtu

        self.newboiler_fuel_type = newboiler_fuel_type
        self.newboiler_fuel_percent_RE = newboiler_fuel_percent_RE
        self.newboiler_fuel_blended_annual_rates_us_dollars_per_mmbtu = newboiler_fuel_blended_annual_rates_us_dollars_per_mmbtu
        self.newboiler_fuel_blended_monthly_rates_us_dollars_per_mmbtu = newboiler_fuel_blended_monthly_rates_us_dollars_per_mmbtu

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


