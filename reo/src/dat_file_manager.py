import os
import copy
from reo.log_levels import log


def _write_var(f, var, dat_var):
    f.write(dat_var + ": [\n")
    if isinstance(var, list):
        for i in var:
            f.write(str(i) + "\n")
    else:
        f.write(str(var) + "\n")
    f.write("]\n")


def write_to_dat(path, var, dat_var, mode='w'):
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
    big_number = 1e8
    DAT = [None] * 20
    DAT_bau = [None] * 20
    pv = None
    pvnm = None
    util = None
    storage = None

    available_techs = ['pv', 'pvnm', 'util']  # order is critical for REopt!
    available_tech_classes = ['PV', 'UTIL']  # this is a REopt 'class', not a python class
    available_loads = ['retail', 'wholesale', 'export', 'storage']  # order is critical for REopt!
    bau_techs = ['util']
    NMILRegime = ['BelowNM', 'NMtoIL', 'AboveIL']

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
            load.load_list.append(self.big_number)

        write_to_dat(file_load_profile, load.load_list, "LoadProfile")
        write_to_dat(file_load_size, load.annual_kwh, "AnnualElecLoad")

        self.DAT[2] = "DAT3=" + "'" + file_load_size + "'"
        self.DAT_bau[2] = self.DAT[2]
        self.DAT[3] = "DAT4=" + "'" + file_load_profile + "'"
        self.DAT_bau[3] = self.DAT[3]

    def add_economics(self, economics_dict):
        file_path = os.path.join(self.path_inputs, 'economics_' + str(self.run_id) + '.dat'),
        for k, v in economics_dict.iteritems():
            try:
                write_to_dat(file_path, v, k, 'a')
            except:
                log('ERROR', 'Error writing economics for ' + k)

    def add_pv(self, pv):
        self.pv = pv
        self.pvnm = copy.deepcopy(pv)
        self.pvnm.nmil_regime = 'NMtoIL'

    def add_util(self, util):
        self.util = util

    def add_maxsizes(self):
        pass

    def add_net_metering(self, net_metering_limit, interconnection_limit):

        # constant.dat contains NMILRegime and TechToNMILMapping
        # NMIL.dat contains NMILLimits
        # placing all three in NMIL.dat will require a new NMIL_bau.dat

        TechToNMILMapping = self._get_REopt_techToNMILMapping(self.available_techs)
        TechToNMILMapping_bau = self._get_REopt_techToNMILMapping(self.bau_techs)

        file_NEM = os.path.join(self.path_inputs, 'NMIL_' + str(self.run_id) + '.dat')
        file_NEM_bau = os.path.join(self.path_inputs, 'NMIL_' + str(self.run_id) + '_bau.dat')

        write_to_dat(file_NEM,
                              [net_metering_limit, interconnection_limit, interconnection_limit*10],
                              'NMILLimits')
        write_to_dat(file_NEM, TechToNMILMapping, 'TechToNMILMapping', mode='a')

        write_to_dat(file_NEM_bau,
                              [net_metering_limit, interconnection_limit, interconnection_limit*10],
                              'NMILLimits')
        write_to_dat(file_NEM_bau, TechToNMILMapping_bau, 'TechToNMILMapping', mode='a')

        self.DAT[16] = "DAT17=" + "'" + file_NEM + "'"
        self.DAT_bau[16] = "DAT17=" + "'" + file_NEM_bau + "'"

    def add_storage(self, storage):
        self.storage = storage

    def _get_REopt_techToNMILMapping(self, techs):
        TechToNMILMapping = list()

        for tech in techs:

            if eval('self.' + tech) is not None:

                tech_regime = eval('self.' + tech + '.nmil_regime')

                for regime in self.NMILRegime:
                    if regime == tech_regime:
                        TechToNMILMapping.append(1)
                    else:
                        TechToNMILMapping.append(0)
        return TechToNMILMapping

    def _get_REopt_prodfactor_techToLoad_derate(self, techs):
        """
        building prod_factor and tech_to_load concurrently for speed (they require the same for-loops)
        :param techs: list of strings, eg. ['pv', 'pvnm', 'util']
        :return: prod_factor, tech_to_load, derate
        """
        prod_factor = []
        tech_to_load = []
        derate = []

        for tech in techs:

            if eval('self.' + tech) is not None:

                derate.append(eval('self.' + tech + '.derate'))

                for load in self.available_loads:

                    if eval('self.' + tech + '.can_serve(' + '"' + load + '"' + ')'):

                        for pf in eval('self.' + tech + '.prod_factor'):
                            prod_factor.append(pf)

                        tech_to_load.append(1)

                    else:

                        for _ in range(self.n_timesteps):
                            prod_factor.append(0)

                        tech_to_load.append(0)

                    # By default, util can serve storage load.
                    # However, if storage is being modeled it can override grid-charging
                    if tech == 'util' and load == 'storage' and self.storage is not None:
                        tech_to_load[-1] = int(self.storage.can_grid_charge)

        # In BAU case, storage.dat must be filled out for REopt initializations, but max size is set to zero

        return prod_factor, tech_to_load, derate

    def _get_REopt_techs(self, techs):
        reopt_techs = []
        for tech in techs:

            if eval('self.' + tech) is not None:

                reopt_techs.append(tech.upper() if tech is not 'util' else tech.upper() + '1')

        return reopt_techs

    def _get_REopt_tech_classes(self, techs):
        """
        
        :param techs: list of strings, eg. ['pv', 'pvnm', 'util']
        :return: tech_classes, tech_to_tech_class
        """
        tech_classes = []
        tech_to_tech_class = []
        for tech in techs:

            if eval('self.' + tech) is not None:

                for tc in self.available_tech_classes:

                    if tech.upper() == tc:
                        tech_classes.append(tc)

                    if eval('self.' + tech + '.reopt_class').upper() == tc.upper():
                        tech_to_tech_class.append(1)
                    else:
                        tech_to_tech_class.append(0)

        return tech_classes, tech_to_tech_class

    def finalize(self):
        """
        necessary for writing out parameters that depend on which Techs are defined
        eg. in REopt ProdFactor: array (Tech,Load,TimeStep).
        Note: whether or not a given Tech can serve a given Load can also be controlled via TechToLoadMatrix
        :return: None
        """

        # DAT1 = constant.dat, contains parameters that others depend on for initialization
        reopt_techs = self._get_REopt_techs(self.available_techs)
        reopt_techs_bau = self._get_REopt_techs(self.bau_techs)

        tech_is_grid = [int(eval('self.' + tech + '.is_grid')) for tech in reopt_techs]
        tech_is_grid_bau = [int(eval('self.' + tech + '.is_grid')) for tech in reopt_techs_bau]

        load_list = ['1R', '1W', '1X', '1S']  # same for BAU

        reopt_tech_classes, tech_to_tech_class = self._get_REopt_tech_classes(self.available_techs)
        reopt_tech_classes_bau, tech_to_tech_class_bau = self._get_REopt_tech_classes(self.bau_techs)

        prod_factor, tech_to_load, derate = self._get_REopt_prodfactor_techToLoad_derate(self.available_techs)
        prod_factor_bau, tech_to_load_bau, derate_bau = self._get_REopt_prodfactor_techToLoad_derate(self.bau_techs)

        file_constant = os.path.join(self.path_inputs, 'constant_' + str(self.run_id) + '.dat')
        self.DAT[0] = "DAT1=" + "'" + file_constant + "'"
        file_constant_bau = os.path.join(self.path_inputs, 'constant_' + str(self.run_id) + '_bau.dat')
        self.DAT_bau[0] = "DAT1=" + "'" + file_constant_bau + "'"

        write_to_dat(file_constant, reopt_techs, 'Tech')
        write_to_dat(file_constant, tech_is_grid, 'TechIsGrid', mode='a')
        write_to_dat(file_constant, load_list, 'Load', mode='a')
        write_to_dat(file_constant, tech_to_load, 'TechToLoadMatrix', mode='a')
        write_to_dat(file_constant, reopt_tech_classes, 'TechClass', mode='a')
        write_to_dat(file_constant, self.NMILRegime, 'NMILRegime', mode='a')
        write_to_dat(file_constant, derate, 'TurbineDerate', mode='a')
        write_to_dat(file_constant, tech_to_tech_class, 'TechToTechClassMatrix', mode='a')

        write_to_dat(file_constant_bau, reopt_techs_bau, 'Tech')
        write_to_dat(file_constant_bau, tech_is_grid_bau, 'TechIsGrid', mode='a')
        write_to_dat(file_constant_bau, load_list, 'Load', mode='a')
        write_to_dat(file_constant_bau, tech_to_load_bau, 'TechToLoadMatrix', mode='a')
        write_to_dat(file_constant_bau, reopt_tech_classes_bau, 'TechClass', mode='a')
        write_to_dat(file_constant_bau, self.NMILRegime, 'NMILRegime', mode='a')
        write_to_dat(file_constant_bau, derate_bau, 'TurbineDerate', mode='a')
        write_to_dat(file_constant_bau, tech_to_tech_class_bau, 'TechToTechClassMatrix', mode='a')

        # ProdFactor stored in GIS.dat
        file_gis = os.path.join(self.path_inputs, "GIS_" + str(self.run_id) + ".dat")
        file_gis_bau = os.path.join(self.path_inputs, "GIS_" + str(self.run_id) + "_bau.dat")

        write_to_dat(file_gis, prod_factor, "ProdFactor")
        write_to_dat(file_gis_bau, prod_factor_bau, "ProdFactor")

        self.DAT[4] = "DAT5=" + "'" + file_gis + "'"
        self.DAT_bau[4] = "DAT5=" + "'" + file_gis_bau + "'"

