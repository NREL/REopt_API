import os
from log_levels import log


def _write_var(f, var, dat_var):
    f.write(dat_var + ": [\n")
    if isinstance(var, list):
        for i in var:
            f.write(str(i) + "\n")
    else:
        f.write(str(var) + "\n")
    f.write("]\n")


def write_single_variable(path, var, dat_var, mode='w'):
    with open(path, mode) as f:
        _write_var(f, var, dat_var)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DatFileManager():
    """
    writes dat files and creates command line strings for dat file paths
    """

    __metaclass__ = Singleton
    run_id = None
    path_inputs = None
    n_timesteps = 8760
    max_big_number = 100000000
    DAT = [None] * 20
    DAT_bau = [None] * 20
    pv = None
    pvnm = None
    util = None
    available_techs = ['pv', 'pvnm', 'util']  # order is critical for REopt!
    available_loads = ['retail', 'wholesale', 'export', 'storage']  # order is critical for REopt!
    bau_techs = ['util']

    def _add_constants(self):
        pass

    def _check_complete(self):
        if any(d is None for d in self.DAT) or any(d is None for d in self.DAT_bau):
            return False
        return True

    def add_load(self, load):
        file_load_profile = os.path.join(self.path_inputs, 'Load8760_' + str(self.run_id) + '.dat')
        file_load_size = os.path.join(self.path_inputs, 'LoadSize_' + str(self.run_id) + '.dat')

        #  fill in W, X, S bins
        for _ in range(8760 * 3):
            load.load_list.append(self.max_big_number)

        write_single_variable(file_load_profile, load.load_list, "LoadProfile")
        write_single_variable(file_load_size, load.annual_kwh, "AnnualElecLoad")

        self.DAT[2] = "DAT3=" + "'" + file_load_size + "'"
        self.DAT_bau[2] = self.DAT[2]
        self.DAT[3] = "DAT4=" + "'" + file_load_profile + "'"
        self.DAT_bau[3] = self.DAT[3]

    def add_economics(self, economics_dict):
        file_path = os.path.join(self.path_inputs, 'economics_' + str(self.run_id) + '.dat'),
        for k, v in economics_dict.iteritems():
            try:
                write_single_variable(file_path, v, k, 'a')
            except:
                log('ERROR', 'Error writing economics for ' + k)

    def add_pv(self, pv):
        self.pv = pv
        self.pvnm = self.pv

    def add_util(self, util):
        self.util = util

    def add_maxsizes(self):
        pass

    def add_nmil(self):
        pass

    def add_storage(self):
        pass

    def _get_REopt_prodfactor(self, techs):
        prod_factor = []
        for tech in techs:

            if eval('self.' + tech) is not None:

                for load in self.available_loads:

                    if eval('self.' + tech + '.can_serve(' + '"' + load + '"' + ')'):
                        for pf in eval('self.' + tech + '.prod_factor'):
                            prod_factor.append(pf)
                    else:
                        for _ in range(self.n_timesteps):
                            prod_factor.append(0)
        return prod_factor

    def finalize(self):
        """
        necessary for writing out ProdFactor, which depends on Techs and Loads
        i.e. in REopt ProdFactor: array (Tech,Load,TimeStep).
        Note: whether or not a given Tech can serve a given Load can also be controlled via TechToLoadMatrix
        :return: None
        """

        prod_factor = self._get_REopt_prodfactor(self.available_techs)
        prod_factor_bau = self._get_REopt_prodfactor(self.bau_techs)

        file_gis = os.path.join(self.path_inputs, "GIS_" + str(self.run_id) + ".dat")
        file_gis_bau = os.path.join(self.path_inputs, "GIS_" + str(self.run_id) + "_bau.dat")

        write_single_variable(file_gis, prod_factor, "ProdFactor")
        write_single_variable(file_gis_bau, prod_factor_bau, "ProdFactor")

        self.DAT[4] = "DAT5=" + "'" + file_gis + "'"
        self.DAT_bau[4] = "DAT5=" + "'" + file_gis_bau + "'"
