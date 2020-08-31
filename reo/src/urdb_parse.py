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

cum_days_in_yr = numpy.cumsum(calendar.mdays)


class REoptArgs:

    def __init__(self, big_number):

        # these vars are passed to DFM as REopt params, written to dats
        self.demand_rates_monthly = 12 * [0.0]
        """
        demand_ratchets_monthly == TimeStepRatchetsMonth in mosel
        It is not only used for demand rates, but also for summing the energy use in each month for rates with energy
        tiers.
        """
        self.demand_ratchets_monthly = [[] for i in range(12)]  # initialize empty lists to fill with timesteps
        for month in range(12):
            for hour in range(24 * cum_days_in_yr[month]+1, 24 * cum_days_in_yr[month+1]+1):
                self.demand_ratchets_monthly[month].append(hour)
        self.demand_rates_tou = []
        self.demand_ratchets_tou = []
        self.demand_num_ratchets = 0
        self.demand_tiers_num = 1
        self.demand_month_tiers_num = 1
        self.demand_max_in_tiers = 1 * [big_number]
        self.demand_month_max_in_tiers = 1 * [big_number]
        self.demand_lookback_months = []
        self.demand_lookback_percent = 0.0
        self.demand_lookback_range = 0
        self.demand_min = 0

 
        self.energy_costs = []
        self.energy_costs_bau = []
        self.energy_tiers_num = 1
        self.energy_max_in_tiers = 1 * [big_number]
        self.energy_avail = []
        self.energy_avail_bau = []
        self.energy_burn_rate = []
        self.energy_burn_rate_bau = []
        self.energy_burn_intercept = []
        self.energy_burn_intercept_bau = []

        self.fuel_costs = []
        self.fuel_costs_bau = []
        self.grid_export_rates = []
        self.grid_export_rates_bau = []
        self.fuel_limit = []
        self.fuel_limit_bau = []

        self.fixed_monthly_charge = 0
        self.annual_min_charge = 0
        self.min_monthly_charge = 0

        self.chp_standby_rate_us_dollars_per_kw_per_month = 0
        self.chp_does_not_reduce_demand_charges = 0

        # Unique parameters for chp and new boiler/chiller efficiency/cop
        self.chp_thermal_prod_slope = 0.0
        self.chp_thermal_prod_intercept = 0.0
        self.chp_derate = 0.0
        self.boiler_efficiency = 0.32
        self.electric_chiller_cop = 0.32
        self.absorption_chiller_cop = 0.32


class RateData:

    def __init__(self, rate):

        possible_URDB_keys = (
            'utility',
            'rate',
            'sector',
            'label',
            'uri',
            'startdate',
            'enddate',
            'description',
            'usenetmetering',
            'source',
            # demand charges
            'peakkwcapacitymin',
            'peakkwcapacitymax',
            'peakkwcapacityhistory',
            'flatdemandunit',
            'flatdemandstructure',
            'flatdemandmonths',
            'demandrateunit',
            'demandratestructure',
            'demandunits',
            'demandweekdayschedule',
            'demandweekendschedule',
            'demandwindow',
            'demandreactivepowercharge',
            # lookback demand charges
            'lookbackMonths',
            'lookbackPercent',
            'lookbackRange',
            # coincident rates
            'coincidentrateunit',
            'coincidentratestructure',
            'coincidentrateschedule',
            # energy charges
            'peakkwhusagemin',
            'peakkwhusagemax',
            'peakkwhusagehistory',
            'energyratestructure',
            'energyweekdayschedule',
            'energyweekendschedule',
            'energycomments',
            # other charges
            'fixedchargefirstmeter',
            'fixedchargeunits',
            'mincharge',
            'minchargeunits',
            'fixedmonthlycharge',
            'minmonthlycharge',
            'annualmincharge',
        )

        for k in possible_URDB_keys:
            if k in rate:
                setattr(self, k, rate.get(k))
            else:
                setattr(self, k, list())
        
        if self.demandunits == 'hp': #convert hp to KW, assume PF is 1 so no need to convert kVA to kW, as of 01/28/2020 only 3 rates in URDB with hp units
            for period in self.demandratestructure:
                for tier in period:
                    if tier.get('rate') or False != False:
                        tier['rate'] = float(tier['rate']) * 0.7457
                    if tier.get('adj') or False != False:
                        tier['adj'] = float(tier['adj']) * 0.7457

        if self.demandunits == 'hp': #convert hp to KW, assume PF is 1 so no need to convert kVA to kW, as of 01/28/2020 only 3 rates in URDB with hp units
            for period in self.demandratestructure:
                for tier in period:
                    if tier.get('rate') or False != False:
                        tier['rate'] = float(tier['rate']) * 0.7457
                    if tier.get('adj') or False != False:
                        tier['adj'] = float(tier['adj']) * 0.7457


class UrdbParse:
    """
    Sub-function of DataManager.
    Makes all REopt args for dat files in Inputs/Utility directory

    Note: (diesel) generator parameters for mosel are defined here because they depend on number of energy tiers in
    utility rate.
    """
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    def __init__(self, big_number, elec_tariff, fuel_tariff, techs, bau_techs, loads, gen=None, chp=None,
                 boiler=None, electric_chiller=None, absorption_chiller=None):

        self.urdb_rate = elec_tariff.urdb_response
        self.year = elec_tariff.load_year
        self.time_steps_per_hour = elec_tariff.time_steps_per_hour
        self.ts_per_year = 8760 * self.time_steps_per_hour
        self.zero_array = [0.0] * self.ts_per_year
        self.net_metering = elec_tariff.net_metering
        self.wholesale_rate = elec_tariff.wholesale_rate
        self.excess_rate = elec_tariff.wholesale_rate_above_site_load
        self.max_demand_rate = 0.0
        self.big_number = big_number
        self.reopt_args = REoptArgs(big_number)
        self.techs = techs
        self.bau_techs = bau_techs
        self.loads = loads
        self.chp_standby_rate_us_dollars_per_kw_per_month = elec_tariff.chp_standby_rate_us_dollars_per_kw_per_month
        self.chp_does_not_reduce_demand_charges = elec_tariff.chp_does_not_reduce_demand_charges
        self.custom_tou_energy_rates = elec_tariff.tou_energy_rates
        self.add_tou_energy_rates_to_urdb_rate = elec_tariff.add_tou_energy_rates_to_urdb_rate
        self.override_urdb_rate_with_tou_energy_rates = elec_tariff.override_urdb_rate_with_tou_energy_rates
        if gen is not None:
            self.generator_fuel_slope = gen.fuel_slope
            self.generator_fuel_intercept = gen.fuel_intercept
            self.generator_fuel_avail = gen.fuel_avail
            self.diesel_fuel_cost_us_dollars_per_gallon = gen.diesel_fuel_cost_us_dollars_per_gallon
            self.diesel_cost_array = [self.diesel_fuel_cost_us_dollars_per_gallon] * self.ts_per_year
        else:
            self.generator_fuel_slope = 0.0
            self.generator_fuel_intercept = 0.0
            self.generator_fuel_avail = 0.0

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

        if chp is not None:
            self.chp_fuel_burn_slope = chp.fuel_burn_slope
            self.chp_fuel_burn_intercept = [chp.fuel_burn_intercept]
            self.chp_thermal_prod_slope = [chp.thermal_prod_slope]
            self.chp_thermal_prod_intercept = [chp.thermal_prod_intercept]
            self.chp_derate = [chp.derate]
        else:
            self.chp_fuel_burn_slope = 0.0
            self.chp_fuel_burn_intercept = list()
            self.chp_thermal_prod_slope = list()
            self.chp_thermal_prod_intercept = list()
            self.chp_derate = list()

        if boiler is not None:
            self.boiler_efficiency = boiler.boiler_efficiency
        else:
            # Make arbitrary non-zero value (pi/10) to avoid divide-by-zero issue
            self.boiler_efficiency = 0.314

        if electric_chiller is not None:
            self.electric_chiller_cop = electric_chiller.chiller_cop
        else:
            # Make arbitrary non-zero value (pi/10) to avoid divide-by-zero issue
            self.electric_chiller_cop = 0.314

        if absorption_chiller is not None:
            self.absorption_chiller_cop = absorption_chiller.chiller_cop
        else:
            # Make arbitrary non-zero value (pi/10) to avoid divide-by-zero issue
            self.absorption_chiller_cop = 0.314

        log.info("URDB parse with year: " + str(self.year) + " net_metering: " + str(self.net_metering))

        self.energy_rates_summary = []
        self.demand_rates_summary = []
        self.energy_costs = []
        self.has_fixed_demand = "no"
        self.has_tou_demand = "no"
        self.has_demand_tiers = "no"
        self.has_tou_energy = "no"
        self.has_energy_tiers = "no"

        # Count the leap day
        self.is_leap_year = False
        if calendar.isleap(self.year):
            self.is_leap_year = True

        self.last_hour_in_month = []
        for month in range(0, 12):
            days_elapsed = sum(self.days_in_month[0:month + 1])
            self.last_hour_in_month.append((days_elapsed * 24) - 1)

    def parse_rate(self, utility, rate):
        log.info("Processing: " + utility + ", " + rate)

        current_rate = RateData(self.urdb_rate)

        if self.override_urdb_rate_with_tou_energy_rates:
            self.has_tou_energy = "yes"  # all that we need from prepare_summary
            self.demand_rates_summary = self.ts_per_year * [0]  # all that we need from prepare_demand_periods
            self.energy_costs = self.custom_tou_energy_rates  # all that we need from prepare_energy_costs
            # assume no fixed charges
        else:
            self.prepare_summary(current_rate)
            self.prepare_demand_periods(current_rate)  # makes demand rates too
            self.prepare_energy_costs(current_rate)
            self.prepare_fixed_charges(current_rate)

        self.reopt_args.fuel_costs, \
        self.reopt_args.fuel_limit,  \
        self.reopt_args.fuel_types,  \
        self.reopt_args.techs_by_fuel_type,  \
        self.reopt_args.energy_burn_rate, \
        self.reopt_args.energy_burn_intercept, \
        self.reopt_args.energy_costs, \
        self.reopt_args.grid_export_rates, \
        self.reopt_args.rates_by_tech,   \
        self.reopt_args.techs_by_rate,   \
        self.reopt_args.num_sales_tiers, \
        self.reopt_args.chp_thermal_prod_slope, \
        self.reopt_args.chp_thermal_prod_intercept, \
        self.reopt_args.chp_fuel_burn_intercept, \
        self.reopt_args.chp_derate, \
        self.reopt_args.chp_standby_rate_us_dollars_per_kw_per_month, \
        self.reopt_args.chp_does_not_reduce_demand_charges, \
        self.reopt_args.boiler_efficiency, \
        self.reopt_args.electric_chiller_cop, \
        self.reopt_args.absorption_chiller_cop = self.prepare_techs_and_loads(self.techs)

        self.reopt_args.fuel_costs_bau, \
        self.reopt_args.fuel_limit_bau,  \
        self.reopt_args.fuel_types_bau,  \
        self.reopt_args.techs_by_fuel_type_bau,  \
        self.reopt_args.energy_burn_rate_bau, \
        self.reopt_args.energy_burn_intercept_bau, \
        self.reopt_args.energy_costs_bau, \
        self.reopt_args.grid_export_rates_bau, \
        self.reopt_args.rates_by_tech_bau,   \
        self.reopt_args.techs_by_rate_bau,   \
        self.reopt_args.num_sales_tiers_bau, \
        self.reopt_args.chp_thermal_prod_slope_bau, \
        self.reopt_args.chp_thermal_prod_intercept_bau, \
        self.reopt_args.chp_fuel_burn_intercept_bau, \
        self.reopt_args.chp_derate_bau, \
        self.reopt_args.chp_standby_rate_us_dollars_per_kw_per_month_bau, \
        self.reopt_args.chp_does_not_reduce_demand_charges_bau, \
        self.reopt_args.boiler_efficiency_bau, \
        self.reopt_args.electric_chiller_cop_bau, \
        self.reopt_args.absorption_chiller_cop_bau = self.prepare_techs_and_loads(self.bau_techs)
        
        return self.reopt_args

    def prepare_summary(self, current_rate):

        if len(current_rate.energyratestructure) > 0:
            if len(current_rate.energyratestructure[0]) > 1:
                self.has_energy_tiers = "yes"
            # tou energy only if greater than one period
            if len(current_rate.energyratestructure) > 1:
                self.has_tou_energy = "yes"

        if len(current_rate.demandratestructure) > 0:
            if len(current_rate.demandratestructure[0]) > 1:
                self.has_demand_tiers = "yes"
            if len(current_rate.energyratestructure) > 1:
                self.has_tou_demand = "yes"

        if len(current_rate.flatdemandstructure) > 0:
            self.has_fixed_demand = "yes"
            if len(current_rate.flatdemandstructure[0]) > 1:
                self.has_demand_tiers = "yes"

        max_demand_rate = 0.0
        for period in current_rate.demandratestructure:
            for tier in period:
                if 'rate' in tier:
                    rate = float(tier['rate'])
                    if 'adj' in tier:
                        rate += float(tier['adj'])
                    if rate > max_demand_rate:
                        max_demand_rate = rate
        for period in range(0, len(current_rate.flatdemandstructure)):
            for tier in range(0, len(current_rate.flatdemandstructure[period])):
                if 'rate' in current_rate.flatdemandstructure[period][tier]:
                    rate = float(current_rate.flatdemandstructure[period][tier]['rate'])
                    if 'adj' in current_rate.flatdemandstructure[period][tier]:
                        rate += float(current_rate.flatdemandstructure[period][tier]['adj'])
                    if rate > max_demand_rate:
                        max_demand_rate = rate

        self.max_demand_rate = max_demand_rate

    def prepare_energy_costs(self, current_rate):

        n_periods = len(current_rate.energyratestructure)
        if n_periods == 0:
            return

        # parse energy tiers
        energy_tiers = []
        for energy_rate in current_rate.energyratestructure:
            energy_tiers.append(len(energy_rate))

        period_with_max_tiers = energy_tiers.index(max(energy_tiers))
        energy_tier_set = set(energy_tiers)

        if len(energy_tier_set) > 1:
            log.warning("Warning: energy periods contain different numbers of tiers, using limits of period with most tiers")

        self.reopt_args.energy_tiers_num = max(energy_tier_set)

        average_rates = False
        rates = []
        rate_average = 0

        # set energy rate tier(bin) limits
        self.reopt_args.energy_max_in_tiers = []

        for energy_tier in current_rate.energyratestructure[period_with_max_tiers]:
            # energy_tier is a dictionary, eg. {'max': 1000, 'rate': 0.07531, 'adj': 0.0119, 'unit': 'kWh'}
            energy_tier_max = self.big_number

            if 'max' in energy_tier:
                if energy_tier['max'] is not None:
                    energy_tier_max = float(energy_tier['max'])

            if 'rate' in energy_tier or 'adj' in energy_tier:
                self.reopt_args.energy_max_in_tiers.append(energy_tier_max)

            # deal with complex units (can't model exactly, must make average)
            if 'unit' in energy_tier:
                energy_tier_unit = str(energy_tier['unit'])
                # average the prices if we have exotic max usage units
                if energy_tier_unit != 'kWh':
                    average_rates = True

            if 'rate' in energy_tier:
                rates.append(float(energy_tier['rate']))
                if 'adj' in energy_tier:
                    rates[-1] += float(energy_tier['adj'])
            # people put adj but no rate in some rates
            elif 'adj' in energy_tier:
                rates.append(float(energy_tier['adj']))

        if average_rates:
            rate_average = float(sum(rates)) / max(len(rates), 1)
            self.reopt_args.energy_tiers_num = 1
            self.reopt_args.energy_max_in_tiers = []
            self.reopt_args.energy_max_in_tiers.append(self.big_number)
            log.warning("Cannot handle max usage units of " + energy_tier_unit + "! Using average rate")

        for tier in range(0, self.reopt_args.energy_tiers_num):
            hour_of_year = 0
            for month in range(0, 12):
                for day in range(0, self.days_in_month[month]):

                    if calendar.weekday(self.year, month + 1, day + 1) < 5:
                        is_weekday = True
                    else:
                        is_weekday = False

                    for hour in range(0, 24):
                        if is_weekday:
                            period = current_rate.energyweekdayschedule[month][hour]
                        else:
                            period = current_rate.energyweekendschedule[month][hour]

                        # workaround for cases where there are different numbers of tiers in periods
                        n_tiers_in_period = len(current_rate.energyratestructure[period])

                        if n_tiers_in_period == 1:
                            tier_use = 0  # use the first and only tier in the period
                        elif tier > n_tiers_in_period-1:  # 'tier' is indexed on zero
                            tier_use = n_tiers_in_period-1  # use last tier in current period, which has less tiers than the maximum tiers for any period
                        else:
                            tier_use = tier

                        if average_rates:
                            rate = rate_average
                        else:
                            rate = float(current_rate.energyratestructure[period][tier_use].get('rate') or 0)

                        adj = float(current_rate.energyratestructure[period][tier_use].get('adj') or 0)
                        total_rate = rate + adj

                        for step in range(0, self.time_steps_per_hour):
                            if self.add_tou_energy_rates_to_urdb_rate:
                                idx = hour_of_year  # len(self.custom_tou_energy_rates) == 8760:
                                if len(self.custom_tou_energy_rates) == 35040:
                                    idx = hour_of_year * 4 + step
                                total_rate = rate + adj + self.custom_tou_energy_rates[idx]
                            self.energy_costs.append(total_rate)
                        hour_of_year += 1

    def prepare_techs_and_loads(self, techs):

        energy_costs = [round(cost, 5) for cost in self.energy_costs]
        # len(self.energy_costs) = self.ts_per_year * self.reopt_args.energy_tiers_num

        start_index = len(energy_costs) - self.ts_per_year
        self.energy_rates_summary = energy_costs[start_index:len(energy_costs)]  # MOVE ELSEWHERE

        """
        ExportRate should be lowest energy cost for tiered rates. Otherwise, ExportRate can be > FuelRate, which
        leads REopt to export all PV energy produced.
        """
        tier_with_lowest_energy_cost = 0
        if self.reopt_args.energy_tiers_num > 1:
            annual_energy_charge_sums = []
            for i in range(0, len(energy_costs), self.ts_per_year):
                annual_energy_charge_sums.append(
                    sum(energy_costs[i:i+self.ts_per_year])
                )
            tier_with_lowest_energy_cost = annual_energy_charge_sums.index(min(annual_energy_charge_sums))

        negative_energy_costs = [cost * -0.999 for cost in
                                 energy_costs[tier_with_lowest_energy_cost*self.ts_per_year:(tier_with_lowest_energy_cost+1)*self.ts_per_year]]
        positive_energy_costs = [cost * 0.999 for cost in
                                 energy_costs[tier_with_lowest_energy_cost*self.ts_per_year:(tier_with_lowest_energy_cost+1)*self.ts_per_year]]

        # wholesale and excess rates can be either scalar (floats or ints) or lists of floats
        if len(self.wholesale_rate) == 1:
            negative_wholesale_rate_costs = self.ts_per_year * [-1.0 * self.wholesale_rate[0]]
            wholesale_rate_costs = self.ts_per_year * [1.0 * self.wholesale_rate[0]]
        else:
            negative_wholesale_rate_costs = [-1.0 * x for x in self.wholesale_rate]
            wholesale_rate_costs = [1.0 * x for x in self.wholesale_rate]
        if len(self.excess_rate) == 1:
            negative_excess_rate_costs = self.ts_per_year * [-1.0 * self.excess_rate[0]]
            excess_rate_costs = self.ts_per_year * [1.0 * self.excess_rate[0]]
        else:
            negative_excess_rate_costs = [-1.0 * x for x in self.excess_rate]
            excess_rate_costs = [1.0 * x for x in self.excess_rate]

        # FuelCost = array(FuelType, TimeStep) is the cost of electricity from each Tech, so 0's for PV, PVNM
        fuel_costs = list()
        # FuelLimit: array(FuelType)
        fuel_limit = list()
        # Set FuelType
        fuel_types = list()
        # Set TechsByFuelType(FuelType)
        techs_by_fuel_type = list()
        for tech in techs:
            # have to rubber stamp other tech values for each energy tier so that array is filled appropriately
            if tech.lower() == 'generator':
                # generator fuel is not free anymore since generator is also a design variable
                fuel_costs = operator.add(fuel_costs, self.diesel_cost_array)
                fuel_limit.append(self.generator_fuel_avail)
                # TODO figure out how to populate fuel costs for all fb techs
                techs_by_fuel_type.append([tech.upper()])
                fuel_types.append("DIESEL")
            elif tech.lower() == 'boiler':
                fuel_costs = operator.add(fuel_costs, self.boiler_fuel_rate_array)
                fuel_limit.append(self.big_number)
                techs_by_fuel_type.append([tech.upper()])
                fuel_types.append("BOILERFUEL")
            elif tech.lower() == 'chp':
                fuel_costs = operator.add(fuel_costs, self.chp_fuel_rate_array)
                fuel_limit.append(self.big_number)
                techs_by_fuel_type.append([tech.upper()])
                fuel_types.append("CHPFUEL")

        # ExportRate is the value of exporting a Tech to the grid under a certain Load bin
        # If there is net metering and no wholesale rate, appears to be zeros for all but 'PV' at '1W'
        grid_export_rates = list()
        rates_by_tech = list()
        if len(techs) > 0:
            num_sales_tiers = 3
            techs_by_rate = [list(), list(), list()]
            grid_export_rates = operator.add(grid_export_rates, negative_energy_costs)
            grid_export_rates = operator.add(grid_export_rates, negative_wholesale_rate_costs)
            grid_export_rates = operator.add(grid_export_rates, negative_excess_rate_costs)
        else: 
            num_sales_tiers = 0
            techs_by_rate = []
        for tech in techs:
            if self.net_metering and not tech.lower().endswith('nm'):
                rates_by_tech.append([1,3])
                techs_by_rate[0].append(tech.upper())
                techs_by_rate[2].append(tech.upper())
            else:     
                rates_by_tech.append([2,3])
                techs_by_rate[1].append(tech.upper())
                techs_by_rate[2].append(tech.upper())

        # FuelBurnSlope = array(Tech)
        energy_burn_rate = []
        for tech in techs:
            if tech.lower() == 'util':
                energy_burn_rate.append(1.0)
            elif tech.lower() == 'boiler':
                energy_burn_rate.append(1 / self.boiler_efficiency)
            elif tech.lower() == 'generator':
                energy_burn_rate.append(self.generator_fuel_slope)
            elif tech.lower() == 'chp':
                energy_burn_rate.append(self.chp_fuel_burn_slope)
            else:
                energy_burn_rate.append(0.0)

        # FuelBurnYInt = array(Tech)
        energy_burn_intercept = []
        chp_energy_burn_yint = []
        for tech in techs:
            if tech.lower() == 'generator':
                energy_burn_intercept.append(self.generator_fuel_intercept)
            elif tech.lower() == 'chp':
                energy_burn_intercept.append(self.chp_fuel_burn_intercept[0])
                chp_energy_burn_yint.append(self.chp_fuel_burn_intercept)
            else:
                energy_burn_intercept.append(0)

        # CHP-specific parameters
        chp_thermal_prod_slope = self.chp_thermal_prod_slope
        chp_thermal_prod_intercept = self.chp_thermal_prod_intercept
        chp_fuel_burn_intercept = self.chp_fuel_burn_intercept
        chp_derate = self.chp_derate #[az] TODO: where is this used in mosel?
        chp_standby_rate = self.chp_standby_rate_us_dollars_per_kw_per_month
        chp_does_not_reduce_demand_charges = self.chp_does_not_reduce_demand_charges
        boiler_efficiency = self.boiler_efficiency
        electric_chiller_cop = self.electric_chiller_cop
        absorption_chiller_cop = self.absorption_chiller_cop

        return fuel_costs, fuel_limit, fuel_types, techs_by_fuel_type, energy_burn_rate, energy_burn_intercept, \
            energy_costs, grid_export_rates, rates_by_tech, techs_by_rate, num_sales_tiers, \
            chp_thermal_prod_slope, chp_thermal_prod_intercept, chp_fuel_burn_intercept, \
            chp_derate, chp_standby_rate, chp_does_not_reduce_demand_charges, \
            boiler_efficiency, electric_chiller_cop, absorption_chiller_cop

    def prepare_demand_periods(self, current_rate):

        n_flat = len(current_rate.flatdemandstructure)
        n_tou = len(current_rate.demandratestructure)
        n_rates = n_flat + n_tou

        self.demand_rates_summary = self.ts_per_year * [0]

        if n_rates == 0:
            return
        if n_flat > 0:
            self.prepare_demand_tiers(current_rate, n_flat, True)
            self.prepare_flat_demand(current_rate)
        if n_tou > 0:
            self.prepare_demand_tiers(current_rate, n_tou, False)
            self.prepare_tou_demand(current_rate)

        self.prepare_demand_ratchets(current_rate)
        self.prepare_demand_rate_summary()

    def prepare_demand_ratchets(self, current_rate):

        demand_lookback_months = list()
        demand_ratchet_percentages = 12 * [0]
        if len(current_rate.demandratchetpercentage) == 12:
            demand_ratchet_percentages = current_rate.demandratchetpercentage
        demand_lookback_percentage = 0

        # REopt currently only supports one lookback percentage, so use the last one
        for month in range(0, 12):
            if (demand_ratchet_percentages[month] > 0):
                demand_lookback_months.append(month + 1)
                demand_lookback_percentage = demand_ratchet_percentages[month]

        self.reopt_args.demand_lookback_months = demand_lookback_months
        self.reopt_args.demand_lookback_percent = float(demand_lookback_percentage)

    def prepare_demand_tiers(self, current_rate, n_periods, monthly):

        # use same method for monthly and tou tiers, just different names
        if monthly:
            demand_rate_structure = current_rate.flatdemandstructure
            self.reopt_args.demand_month_max_in_tiers = []
        else:
            demand_rate_structure = current_rate.demandratestructure
            self.reopt_args.demand_max_in_tiers = []

        demand_tiers = []
        for demand_rate in demand_rate_structure:
            demand_tiers.append(len(demand_rate))
        demand_tier_set = set(demand_tiers)
        period_with_max_tiers = demand_tiers.index(max(demand_tiers)) #NOTE: this takes the first period if multiple periods have the same number of (max) tiers
        n_tiers = max(demand_tier_set)

        if len(demand_tier_set) > 1:
            log.warning("Warning: multiple lengths of demand tiers, using tiers from the earliest period with the max number of tiers")

            # make the number of tiers the same across all periods by appending on identical tiers
            for r in range(n_periods):
                demand_rate = demand_rate_structure[r]
                demand_rate_new = demand_rate
                n_tiers_in_period = len(demand_rate)
                if n_tiers_in_period != n_tiers:
                    last_tier = demand_rate[n_tiers_in_period - 1]
                    for i in range(0, n_tiers - n_tiers_in_period):
                        demand_rate_new.append(last_tier)
                demand_rate_structure[r] = demand_rate_new

        demand_tiers = {} # for all periods
        demand_maxes = []

        if n_periods > 0:
            for period in range(n_periods):
                demand_max = []
                for tier in range(n_tiers):
                    demand_tier = demand_rate_structure[period][tier]
                    demand_tier_max = self.big_number
                    if 'max' in demand_tier:
                        if demand_tier['max'] is not None:
                            demand_tier_max = float(demand_tier['max'])
                    demand_max.append(demand_tier_max)
                demand_tiers[period] = demand_max
                demand_maxes.append(demand_max[-1])

        # test if the highest tier is the same across all periods
        test_demand_max = set(demand_maxes)
        if len(test_demand_max) > 1:
           log.warning("Warning: highest demand tiers do not match across periods, using max from largest set of tiers")

        if monthly:
            self.reopt_args.demand_month_max_in_tiers = demand_tiers[period_with_max_tiers]
            self.reopt_args.demand_month_tiers_num = n_tiers
        else:
            self.reopt_args.demand_max_in_tiers = demand_tiers[period_with_max_tiers]
            self.reopt_args.demand_tiers_num = n_tiers

    def prepare_flat_demand(self, current_rate):

        self.reopt_args.demand_rates_monthly = []

        for month in range(12):

            for period_idx, seasonal_period in enumerate(current_rate.flatdemandstructure):
                period_in_month = 0
                if len(current_rate.flatdemandmonths) > 0:
                    period_in_month = current_rate.flatdemandmonths[month]

                    if period_in_month == period_idx:

                        for tier in seasonal_period:
                            seasonal_rate = float(tier.get('rate') or 0)
                            seasonal_adj = float(tier.get('adj') or 0)
                            self.reopt_args.demand_rates_monthly.append(seasonal_rate + seasonal_adj)

    def prepare_demand_rate_summary(self):
        """
        adds flat demand rate for each timestep to self.demand_rates_summary
        (which is full of zeros before this step)
        :return:
        """

        for month in range(12):
            flat_rate = self.reopt_args.demand_rates_monthly[month]
            month_hours = self.get_hours_in_month(month)

            for hour in month_hours:
                self.demand_rates_summary[hour] += flat_rate

    def prepare_tou_demand(self, current_rate):
        demand_periods = []
        demand_rates = []

        if type(current_rate.peakkwcapacitymin) is int:
            self.reopt_args.demand_min = current_rate.peakkwcapacitymin

        self.reopt_args.demand_rates = []
        for month in range(12):

            for demand_period in range(len(current_rate.demandratestructure)):

                time_steps = self.get_tou_steps(current_rate, month, demand_period)

                if len(time_steps) > 0:

                    demand_periods.append(time_steps)

                    for tier in current_rate.demandratestructure[demand_period]:

                        tou_rate = float(tier.get('rate') or 0)
                        tou_adj = float(tier.get('adj') or 0)

                        demand_rates.append(tou_rate + tou_adj)

                        for step in time_steps:
                            self.demand_rates_summary[step] += tou_rate + tou_adj

        self.reopt_args.demand_ratchets_tou = demand_periods
        self.reopt_args.demand_rates_tou = demand_rates
        self.reopt_args.demand_num_ratchets = len(demand_periods)

    def prepare_fixed_charges(self, current_rate):
        if not isinstance(current_rate.fixedchargefirstmeter, list):      #URDB v7
            if current_rate.fixedchargeunits == '$/month': # first try $/month, then check if $/day exists, as of 1/28/2020 there were only $/day and $month entries in the URDB
                self.reopt_args.fixed_monthly_charge = current_rate.fixedchargefirstmeter 
            if current_rate.fixedchargeunits == '$/day':
                self.reopt_args.fixed_monthly_charge = current_rate.fixedchargefirstmeter*30.4375 # scalar intended to approximate annual charges over 12 month period, derived from 365.25/12
        else:                                                           #URDB v3, preserve backwards compatability
            if not isinstance(current_rate.fixedmonthlycharge, list):
                self.reopt_args.fixed_monthly_charge = current_rate.fixedmonthlycharge

        if current_rate.mincharge  != []:                               #URDB v7
            if current_rate.minchargeunits == '$/month':
                self.reopt_args.min_monthly_charge = current_rate.mincharge # first try $/month, then check if $/day or $/year exists, as of 1/28/2020 these were the only unit types in the urdb
            if current_rate.minchargeunits == '$/day':
                self.reopt_args.fixed_monthly_charge = current_rate.mincharge*30.4375 # scalar intended to approximate annual charges over 12 month period, derived from 365.25/12
            if current_rate.minchargeunits == '$/year':
                self.reopt_args.annual_min_charge = current_rate.mincharge
        else:                                                           #URDB v3, preserve backwards compatability
            if not isinstance(current_rate.annualmincharge, list):
                self.reopt_args.annual_min_charge = current_rate.annualmincharge
            if not isinstance(current_rate.minmonthlycharge, list):
                self.reopt_args.min_monthly_charge = current_rate.minmonthlycharge

    def get_hours_in_month(self, month):

        hours = []
        hours.append(0)
        for m in range(12):
            hours_previous = hours[m]
            days_in_month = calendar.monthrange(self.year, m + 1)[1]
            # no leap days allowed
            if m == 1 and calendar.isleap(self.year):
                days_in_month -= 1
            hours.append(24 * days_in_month + hours_previous)

        return range(hours[month], hours[month + 1])

    def get_tou_steps(self, current_rate, month, period):
        step_array = []
        start_step = 1
        start_hour = 1

        if month > 0:
            start_hour = self.last_hour_in_month[month - 1] + 1
            start_step = (self.last_hour_in_month[month - 1] + 1) * self.time_steps_per_hour

        hour_of_year = start_hour
        step_of_year = start_step
        for day in range(0, self.days_in_month[month]):

            if calendar.weekday(self.year, month + 1, day + 1) < 5:
                is_weekday = True
            else:
                is_weekday = False

            for hour in range(0, 24):
                for step in range(0, self.time_steps_per_hour):
                    if is_weekday and current_rate.demandweekdayschedule[month][hour] == period:
                        step_array.append(step_of_year)
                    elif not is_weekday and current_rate.demandweekendschedule[month][hour] == period:
                        step_array.append(step_of_year)
                    step_of_year += 1
                hour_of_year += 1
        return step_array
