from reo.src.dat_file_manager import DatFileManager
from reo.src.incentives import Incentives
big_number = 100000  # should this be the 1e10 in DFM? typically use smaller battery max?


class Storage(object):
    """
    REopt class for energy storage
    """

    def __init__(self, min_kw=0, max_kw=big_number, min_kwh=0, max_kwh=big_number,
                 efficiency=0.90, inverter_efficiency=0.96, rectifier_efficiency=0.96,
                 soc_min=0.2, soc_init=0.5,
                 can_grid_charge=True,
                 level_count=1, level_coefs=(-1, 0),
                 us_dollar_per_kw=1000, us_dollar_per_kwh=500,
                 replace_us_dollar_per_kw=200, replace_us_dollar_per_kwh=200,
                 replace_kw_years=10, replace_kwh_years=10,
                 **kwargs):

        self.min_kw = min_kw
        self.max_kw = max_kw
        self.min_kwh = min_kwh
        self.max_kwh = max_kwh

        self.efficiency = efficiency
        self.inverter_efficiency = inverter_efficiency
        self.rectifier_efficiency = rectifier_efficiency
        self.roundtrip_efficiency = efficiency * inverter_efficiency * rectifier_efficiency

        self.soc_min = soc_min
        self.soc_init = soc_init

        self.can_grid_charge = can_grid_charge

        self.level_count = level_count
        self.level_coefs = level_coefs

        self.us_dollar_per_kw = us_dollar_per_kw
        self.us_dollar_per_kwh = us_dollar_per_kwh
        self.replace_us_dollar_per_kw = replace_us_dollar_per_kw
        self.replace_us_dollar_per_kwh = replace_us_dollar_per_kwh
        self.replace_kw_years = replace_kw_years
        self.replace_kwh_years = replace_kwh_years

        self.incentives = Incentives(kwargs, tech='batt', macrs_years=kwargs.get('batt_macrs_schedule'),
                                     macrs_bonus_fraction=kwargs.get('batt_macrs_bonus_fraction') or 0.5,
                                     macrs_itc_reduction=kwargs.get('batt_macrs_itc_reduction') or 0.5,)

        DatFileManager().add_storage(self)
