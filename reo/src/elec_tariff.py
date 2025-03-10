# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
import re
import copy
import logging
log = logging.getLogger(__name__)


class ElecTariff(object):

    def __init__(self, dfm, run_id, wholesale_rate_us_dollars_per_kwh, wholesale_rate_above_site_load_us_dollars_per_kwh,
                 net_metering_limit_kw, interconnection_limit_kw, load_year, time_steps_per_hour,
                 blended_monthly_rates_us_dollars_per_kwh=None, blended_monthly_demand_charges_us_dollars_per_kw=None,
                 urdb_response=None, add_blended_rates_to_urdb_rate=None, blended_annual_rates_us_dollars_per_kwh=None,
                 blended_annual_demand_charges_us_dollars_per_kw=None, add_tou_energy_rates_to_urdb_rate=None,
                 tou_energy_rates_us_dollars_per_kwh=None, 
                 emissions_factor_series_lb_CO2_per_kwh=None,
                 emissions_factor_series_lb_NOx_per_kwh=None,
                 emissions_factor_series_lb_SO2_per_kwh=None,
                 emissions_factor_series_lb_PM25_per_kwh=None,
                 coincident_peak_load_active_timesteps=None, coincident_peak_load_charge_us_dollars_per_kw=None,
                 chp_allowed_to_export=None,
                 emissions_factor_CO2_pct_decrease=None, 
                 emissions_factor_NOx_pct_decrease=None, 
                 emissions_factor_SO2_pct_decrease=None, 
                 emissions_factor_PM25_pct_decrease=None, 
                 **kwargs):
        """
        Electricity Tariff object for creating inputs to REopt
        :param dfm: Object, DataManager
        :param run_id: str, run uuid
        :param wholesale_rate_us_dollars_per_kwh: float or list of float
        :param wholesale_rate_above_site_load_us_dollars_per_kwh: float or list of float
        :param net_metering_limit_kw: float
        :param load_year: int
        :param time_steps_per_hour: int
        :param blended_monthly_rates_us_dollars_per_kwh: list of float, length = 12
        :param blended_monthly_demand_charges_us_dollars_per_kw: list of float, length = 12
        :param urdb_response: dict, response from Utility Rate Database
        :param add_blended_rates_to_urdb_rate: bool
        :param blended_annual_rates_us_dollars_per_kwh: float
        :param blended_annual_demand_charges_us_dollars_per_kw: float
        :param coincident_peak_load_active_timesteps: list of float or list of list of float
        :param coincident_peak_load_charge_us_dollars_per_kw: float or list of float
        :param kwargs:  not used
        """
        self.run_id = run_id
        self.wholesale_rate = wholesale_rate_us_dollars_per_kwh
        self.wholesale_rate_above_site_load = wholesale_rate_above_site_load_us_dollars_per_kwh
        self.time_steps_per_hour = time_steps_per_hour
        self.load_year = load_year
        self.tou_energy_rates = tou_energy_rates_us_dollars_per_kwh
        self.add_tou_energy_rates_to_urdb_rate = add_tou_energy_rates_to_urdb_rate
        self.override_urdb_rate_with_tou_energy_rates = False

        if coincident_peak_load_charge_us_dollars_per_kw is not None \
                and coincident_peak_load_active_timesteps is not None:
            self.coincident_peak_num_periods = len(coincident_peak_load_charge_us_dollars_per_kw)
            self.coincident_peak_load_charge_us_dollars_per_kw = coincident_peak_load_charge_us_dollars_per_kw
            self.coincident_peak_load_active_timesteps = coincident_peak_load_active_timesteps
        else:
            self.coincident_peak_num_periods = 0
            self.coincident_peak_load_charge_us_dollars_per_kw = []
            self.coincident_peak_load_active_timesteps = []

        if urdb_response is not None:
            log.info("Parsing URDB rate")
            if self.tou_energy_rates is not None and self.add_tou_energy_rates_to_urdb_rate is False:
                self.override_urdb_rate_with_tou_energy_rates = True
                # option of adding tou energy rate to urdb rate is implemented in UrdbParse.prepare_energy_costs
            elif add_blended_rates_to_urdb_rate:
                self.add_tou_energy_rates_to_urdb_rate = False
                urdb_response = self.update_urdb_with_monthly_energy_and_demand(
                    urdb_response, blended_monthly_rates_us_dollars_per_kwh,
                    blended_monthly_demand_charges_us_dollars_per_kw)

        elif blended_monthly_rates_us_dollars_per_kwh is not None \
                and blended_monthly_demand_charges_us_dollars_per_kw is not None:
            self.add_tou_energy_rates_to_urdb_rate = False
            log.info("Making URDB rate from monthly blended data")
            urdb_response = self.make_urdb_rate(blended_monthly_rates_us_dollars_per_kwh,
                                                blended_monthly_demand_charges_us_dollars_per_kw)

        elif blended_annual_rates_us_dollars_per_kwh is not None \
                and blended_annual_demand_charges_us_dollars_per_kw is not None:
            self.add_tou_energy_rates_to_urdb_rate = False
            blended_monthly_rates_us_dollars_per_kwh = 12 * [blended_annual_rates_us_dollars_per_kwh]
            blended_monthly_demand_charges_us_dollars_per_kw = 12 * [blended_annual_demand_charges_us_dollars_per_kw]
            log.info("Making URDB rate from annual blended data")
            urdb_response = self.make_urdb_rate(blended_monthly_rates_us_dollars_per_kwh,
                                                blended_monthly_demand_charges_us_dollars_per_kw)

        self.utility_name = re.sub(r'\W+', '', str(urdb_response.get('utility')))
        self.rate_name = re.sub(r'\W+', '', str(urdb_response.get('name')))
        self.urdb_response = urdb_response
        self.net_metering_limit_kw = net_metering_limit_kw
        self.interconnection_limit_kw = interconnection_limit_kw
        self.emissions_factor_series_lb_CO2_per_kwh = emissions_factor_series_lb_CO2_per_kwh
        self.emissions_factor_series_lb_NOx_per_kwh = emissions_factor_series_lb_NOx_per_kwh
        self.emissions_factor_series_lb_SO2_per_kwh = emissions_factor_series_lb_SO2_per_kwh
        self.emissions_factor_series_lb_PM25_per_kwh = emissions_factor_series_lb_PM25_per_kwh
        self.emissions_factor_CO2_pct_decrease = emissions_factor_CO2_pct_decrease
        self.emissions_factor_NOx_pct_decrease = emissions_factor_NOx_pct_decrease
        self.emissions_factor_SO2_pct_decrease = emissions_factor_SO2_pct_decrease
        self.emissions_factor_PM25_pct_decrease = emissions_factor_PM25_pct_decrease 

        # Standby charges for CHP
        self.chp_standby_rate_us_dollars_per_kw_per_month = kwargs['chp_standby_rate_us_dollars_per_kw_per_month']
        if kwargs.get('chp_does_not_reduce_demand_charges') in [None, False]:
            self.chp_does_not_reduce_demand_charges = 0
        else:
            self.chp_does_not_reduce_demand_charges = 1
        
        self.chp_allowed_to_export = chp_allowed_to_export

        dfm.add_elec_tariff(self)

    def update_urdb_with_monthly_energy_and_demand(self, urdb_rate, monthly_energy, monthly_demand):
        # Make sure at least monthly energy and demand are captured
        if 'flatdemandmonths' not in urdb_rate.keys():
            urdb_rate['flatdemandstructure'] = [[{'rate': 0.0}]]
            urdb_rate['flatdemandmonths'] = [0 for _ in range(0, 12)]

        if 'energyratestructure' not in urdb_rate.keys():
            urdb_rate['energyratestructure'] = [[{'rate': 0.0}]]
            urdb_rate['energyweekdayschedule'] = [[0 for _ in range(0, 24)] for __ in range(0, 12)]
            urdb_rate['energyweekendschedule'] = [[0 for _ in range(0, 24)] for __ in range(0, 12)]

        # Add Demand Charges
        updated_rates = []
        rate_adj_combos = []
        for position, monthly_rate_id in enumerate(urdb_rate['flatdemandmonths']):
            adj = monthly_demand[position]
            original_rate_id = urdb_rate['flatdemandmonths'][position]
            rates = copy.deepcopy(urdb_rate['flatdemandstructure'][original_rate_id])
            combo = [original_rate_id, adj]
            if combo not in rate_adj_combos:
                rate_adj_combos.append(combo)
                for r in rates:
                    if "adj" in r.keys():
                        r['adj'] += adj
                    else:
                        r['adj'] = adj
                updated_rates.append(rates)
            rate_id = rate_adj_combos.index(combo)
            urdb_rate['flatdemandmonths'][position] = rate_id
        urdb_rate['flatdemandstructure'] = updated_rates

        # Add Energy Charges
        added_charges_set, schedules = monthly_energy, ['energyweekdayschedule', 'energyweekendschedule']
        
        if 'energyratestructure' in urdb_rate.keys():
            updated_rates = []
            rate_adj_combos = []
            for schedule in schedules:
                if schedule in urdb_rate.keys():
                    for position, month in enumerate(urdb_rate[schedule]): 
                        for original_rate_id in list(set(month)):
                            adj = added_charges_set[position]
                            rates = copy.deepcopy(urdb_rate['energyratestructure'][original_rate_id])
                            combo = [original_rate_id, adj]
                            if combo not in rate_adj_combos:
                                rate_adj_combos.append(combo)
                                for r in rates:                    
                                    if "adj" in r.keys():
                                        r['adj'] += adj
                                    else:
                                        r['adj'] = adj
                                updated_rates.append(rates)
                            rate_id = rate_adj_combos.index(combo)
                            for ii, entry in enumerate(month):
                                if entry == original_rate_id:
                                    month[ii] = rate_id
                    urdb_rate['energyratestructure'] = updated_rates
       
        return urdb_rate

    def make_urdb_rate(self, blended_utility_rate, demand_charge):

        urdb_rate = {}

        # energy rate
        energyratestructure = []
        energyweekdayschedule = []
        energyweekendschedule = []

        flatdemandstructure = []
        flatdemandmonths = []

        unique_energy_rates = set(blended_utility_rate)
        unique_demand_rates = set(demand_charge)

        for energy_rate in unique_energy_rates:
            rate = [{'rate': energy_rate, 'unit': 'kWh'}]
            energyratestructure.append(rate)

        for demand_rate in unique_demand_rates:
            rate = [{'rate': demand_rate}]
            flatdemandstructure.append(rate)

        for month in range(0, 12):
            energy_period = 0
            demand_period = 0
            for energy_rate in unique_energy_rates:
                if energy_rate == blended_utility_rate[month]:
                    tmp = [energy_period for _ in range(0,24)]
                    energyweekdayschedule.append(tmp)
                    energyweekendschedule.append(tmp)
                energy_period += 1
            for demand_rate in unique_demand_rates:
                if demand_rate == demand_charge[month]:
                    flatdemandmonths.append(demand_period)
                demand_period += 1

        # ouput
        urdb_rate['energyweekdayschedule'] = energyweekdayschedule
        urdb_rate['energyweekendschedule'] = energyweekendschedule
        urdb_rate['energyratestructure'] = energyratestructure
        urdb_rate['utility'] = 'user rate'
        urdb_rate['name'] = 'user rate'

        if sum(unique_demand_rates) > 0:
            urdb_rate['flatdemandstructure'] = flatdemandstructure
            urdb_rate['flatdemandmonths'] = flatdemandmonths
            urdb_rate['flatdemandunit'] = 'kW'

        urdb_rate['label'] = self.run_id
        urdb_rate['name'] = "Custom_rate_" + str(self.run_id)
        urdb_rate['utility'] = "Custom_utility_" + str(self.run_id)
        return urdb_rate
