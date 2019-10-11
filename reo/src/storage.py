from reo.src.dat_file_manager import big_number
from reo.nested_inputs import macrs_five_year, macrs_seven_year


class StorageIncentives(object):
        
    def __init__(self, macrs_option_years, macrs_bonus_pct, total_itc_pct, total_rebate_us_dollars_per_kw,
                 macrs_itc_reduction=0.5):  # should we expose macrs_itc_reduction to users?
        
        self.itc_pct = total_itc_pct
        self.itc_max = big_number
        
        self.rebate = total_rebate_us_dollars_per_kw
        self.rebate_max = big_number
        self.macrs_bonus_pct = macrs_bonus_pct
        self.macrs_itc_reduction = macrs_itc_reduction

        if macrs_option_years == 5:
            self.macrs_schedule = macrs_five_year
        elif macrs_option_years == 7:
            self.macrs_schedule = macrs_seven_year
        elif macrs_option_years == 0:
            self.macrs_bonus_pct = 0
            self.macrs_itc_reduction = 0
            self.macrs_schedule = [0]
        else:
            raise ValueError("macrs_option_years must be 0, 5 or 7.")
    

class Storage(object):
    """
    REopt class for energy storage.
    All default values in kwargs set by validator using nested_input_definitions.
    """

    def __init__(self, dfm, min_kw, max_kw, min_kwh, max_kwh,
                 internal_efficiency_pct, inverter_efficiency_pct, rectifier_efficiency_pct,
                 soc_min_pct, soc_init_pct, canGridCharge,
                 installed_cost_us_dollars_per_kw, installed_cost_us_dollars_per_kwh,
                 replace_cost_us_dollars_per_kw, replace_cost_us_dollars_per_kwh,
                 inverter_replacement_year, battery_replacement_year,
                 **kwargs):

        self.min_kw = min_kw
        self.max_kw = max_kw
        self.min_kwh = min_kwh
        self.max_kwh = max_kwh

        self.internal_efficiency_pct = internal_efficiency_pct
        self.inverter_efficiency_pct = inverter_efficiency_pct
        self.rectifier_efficiency_pct = rectifier_efficiency_pct
        self.roundtrip_efficiency = internal_efficiency_pct * inverter_efficiency_pct * rectifier_efficiency_pct

        self.soc_min_pct = soc_min_pct
        self.soc_init_pct = soc_init_pct
        self.canGridCharge = canGridCharge

        self.installed_cost_us_dollars_per_kw = installed_cost_us_dollars_per_kw
        self.installed_cost_us_dollars_per_kwh = installed_cost_us_dollars_per_kwh
        self.replace_cost_us_dollars_per_kw = replace_cost_us_dollars_per_kw
        self.replace_cost_us_dollars_per_kwh = replace_cost_us_dollars_per_kwh
        self.inverter_replacement_year = inverter_replacement_year
        self.battery_replacement_year = battery_replacement_year

        self.incentives = StorageIncentives(**kwargs)

        dfm.add_storage(self)
