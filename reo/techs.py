from pvwatts import PVWatts
from dat_file_manager import DatFileManager


class Tech(object):
    """
    base class for REopt energy generation technology
    """

    def __init__(self, min_size=0, max_size=1000000, *args, **kwargs):

        self.min_size = min_size
        self.max_size = max_size
        # self.size_limits = size_limits
        # self.cost_per_kw = cost_per_kw

        # self.fuel_cost = fuel_cost
        # self.om_capacity_cost = om_capacity_cost
        # self.om_variable_cost = om_variable_cost
        #
        # self.efficiency = efficiency
        #
        # self.n_cost_segments = len(cost_per_kw)
        # self.n_fuel_tiers = len(fuel_cost)  # does anything besides UTIL use fuel tiers?

        # self._check_inputs()
        self.kwargs = kwargs

    def _check_inputs(self):

        assert len(self.size_limits) - 1 == len(self.cost_per_kw),\
                "Provided {0} size limits and {1} cost segments.\n\
                 With {0} size limits you must provide {2} cost segments."\
                .format(len(self.size_limits), len(self.cost_per_kw), len(self.cost_per_kw)-1)

        assert self.max_size >= self.min_size,\
                "Last entry in size_limits (max_size) must be greater than or equal to\n\
                 first entry in size_limits (min_size)."

    @property
    def prod_factor(self):
        """
        Production Factor.  Combination of resource, efficiency, and availability.
        :return: prod_factor
        """
        return None


class Util(Tech):

    def __init__(self, outage_start=None, outage_end=None, **kwargs):
        super(Util, self).__init__(**kwargs)
        self.outage_start = outage_start
        self.outage_end = outage_end

        dfm = DatFileManager()
        dfm.add_util(self)

    @property
    def prod_factor(self):

        grid_prod_factor = [1.0 for _ in range(8760)]

        if self.outage_start and self.outage_end:  # "turn off" grid resource
            grid_prod_factor[self.outage_start:self.outage_end] = [0]*(self.outage_end - self.outage_start)
        return grid_prod_factor


class PV(Tech):

    def __init__(self, **kwargs):
        super(PV, self).__init__(**kwargs)

        dfm = DatFileManager()
        dfm.add_pv(self)

    @property
    def prod_factor(self):
        pvwatts = PVWatts(**self.kwargs)
        return pvwatts.pv_prod_factor