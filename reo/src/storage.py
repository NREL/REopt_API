from reo.src.dat_file_manager import DatFileManager
big_number = 1000000


class Storage(object):
    """
    REopt class for energy storage
    """

    def __init__(self, min_kw=0, max_kw=big_number, min_kwh=0, max_kwh=big_number,
                 batt_efficiency=0.90, batt_inverter_efficiency=0.96, batt_rectifier_efficiency=0.96,
                 soc_min=0.2, soc_init=0.5,
                 can_grid_charge=True,
                 **kwargs):

        self.min_kw = min_kw
        self.max_kw = max_kw
        self.min_kwh = min_kwh
        self.max_kwh = max_kwh

        self.batt_efficiency = batt_efficiency
        self.batt_inverter_efficiency = batt_inverter_efficiency
        self.batt_rectifier_efficiency = batt_rectifier_efficiency

        self.soc_min = soc_min
        self.soc_init = soc_init

        self.can_grid_charge = can_grid_charge

        DatFileManager().add_storage(self)
