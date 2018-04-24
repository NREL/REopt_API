from reo.src.dat_file_manager import big_number
from reo.src.pvwatts import PVWatts
from reo.src.incentives import Incentives
from reo.src.ventyx import Ventyx


class Tech(object):
    """
    base class for REopt energy generation technology
    """

    def __init__(self, min_kw=0, max_kw=big_number, installed_cost_us_dollars_per_kw=big_number,
                 om_cost_us_dollars_per_kw=0, *args, **kwargs):

        self.min_kw = min_kw
        self.max_kw = max_kw
        self.installed_cost_us_dollars_per_kw = installed_cost_us_dollars_per_kw
        self.om_cost_us_dollars_per_kw = om_cost_us_dollars_per_kw

        self.loads_served = ['retail', 'wholesale', 'export', 'storage']
        self.nmil_regime = None
        self.reopt_class = ""
        self.is_grid = False
        self.derate = 1
        self.acres_per_kw = None  # for land constraints
        self.kw_per_square_foot = None  # for roof constraints

        self.kwargs = kwargs

    @property
    def prod_factor(self):
        """
        Production Factor.  Combination of resource, efficiency, and availability.
        :return: prod_factor
        """
        return None

    def can_serve(self, load):
        if load in self.loads_served:
            return True
        return False

class Util(Tech):

    def __init__(self, dfm, outage_start_hour=None, outage_end_hour=None):
        super(Util, self).__init__(max_kw=12000000)

        self.outage_start_hour = outage_start_hour
        self.outage_end_hour = outage_end_hour
        self.loads_served = ['retail', 'storage']
        self.is_grid = True
        self.derate = 0

        dfm.add_util(self)

    @property
    def prod_factor(self):

        grid_prod_factor = [1.0 for _ in range(8760)]

        if self.outage_start_hour is not None and self.outage_end_hour is not None:  # "turn off" grid resource
            grid_prod_factor[self.outage_start_hour:self.outage_end_hour] = [0]*(self.outage_end_hour - self.outage_start_hour)

        return grid_prod_factor


class PV(Tech):

    def __init__(self, dfm, degradation_pct, acres_per_kw=6e-3, kw_per_square_foot=0.01, existing_kw=0, **kwargs):
        super(PV, self).__init__(**kwargs)

        self.degradation_pct = degradation_pct
        self.nmil_regime = 'BelowNM'
        self.reopt_class = 'PV'
        self.acres_per_kw = acres_per_kw
        self.kw_per_square_foot = kw_per_square_foot
        self.incentives = Incentives(**kwargs)

        self.pvwatts_prod_factor = None
        self.existing_kw = existing_kw
        self.min_kw += existing_kw

        if self.max_kw < self.existing_kw:
            self.max_kw = self.existing_kw

        dfm.add_pv(self)

    @property
    def prod_factor(self):

        if self.pvwatts_prod_factor is None:
            pvwatts = PVWatts(**self.kwargs)
            self.pvwatts_prod_factor = pvwatts.pv_prod_factor
        return self.pvwatts_prod_factor


class Wind(Tech):

    def __init__(self, dfm, acres_per_kw=.03, **kwargs):
        super(Wind, self).__init__(**kwargs)

        self.nmil_regime = 'BelowNM'
        self.reopt_class = 'WIND'
        self.acres_per_kw = acres_per_kw
        self.incentives = Incentives(**kwargs)

        self.ventyx = None
        dfm.add_wind(self)

    @property
    def prod_factor(self):
        if self.ventyx is None:
            self.ventyx = Ventyx()
        return self.ventyx.wind_prod_factor
