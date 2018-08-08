import re
from reo.log_levels import log


class ElecTariff(object):

    def __init__(self, dfm, run_id, wholesale_rate_us_dollars_per_kwh, net_metering_limit_kw, load_year,
                 time_steps_per_hour, urdb_label=None, urdb_utility_name=None, urdb_rate_name=None,
                 blended_monthly_rates_us_dollars_per_kwh=None, blended_monthly_demand_charges_us_dollars_per_kw=None,
                 urdb_response=None, **kwargs):

        self.run_id = run_id
        self.wholesale_rate = wholesale_rate_us_dollars_per_kwh
        self.time_steps_per_hour = time_steps_per_hour
        self.load_year = load_year

        self.net_metering = False
        if net_metering_limit_kw > 0:
            self.net_metering = True

        if urdb_response is not None:
            log.info("Parsing URDB rate")
        
        else:
            log.info("Making URDB rate from blended data")
            urdb_response = self.make_urdb_rate(blended_monthly_rates_us_dollars_per_kwh, blended_monthly_demand_charges_us_dollars_per_kw)

        self.utility_name = re.sub(r'\W+', '', str(urdb_response.get('utility')))
        self.rate_name = re.sub(r'\W+', '', str(urdb_response.get('name')))
        self.urdb_response = urdb_response

        dfm.add_elec_tariff(self)

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
                    tmp = [energy_period] * 24
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
