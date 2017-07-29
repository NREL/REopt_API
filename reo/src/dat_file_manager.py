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

    file_constant = os.path.join(path_inputs, 'constant_' + str(run_id) + '.dat')
    file_constant_bau = os.path.join(path_inputs, 'constant_' + str(run_id) + '_bau.dat')
    file_load_profile = os.path.join(path_inputs, 'Load8760_' + str(run_id) + '.dat')
    file_load_size = os.path.join(path_inputs, 'LoadSize_' + str(run_id) + '.dat')
    file_gis = os.path.join(path_inputs, "GIS_" + str(run_id) + ".dat")
    file_gis_bau = os.path.join(path_inputs, "GIS_" + str(run_id) + "_bau.dat")
    file_storage = os.path.join(path_inputs, 'storage_' + str(run_id) + '.dat')
    file_storage_bau = os.path.join(path_inputs, 'storage_' + str(run_id) + '_bau.dat')
    file_NEM = os.path.join(path_inputs, 'NMIL_' + str(run_id) + '.dat')
    file_NEM_bau = os.path.join(path_inputs, 'NMIL_' + str(run_id) + '_bau.dat')
    
    DAT[0] = "DAT1=" + "'" + file_constant + "'"
    DAT_bau[0] = "DAT1=" + "'" + file_constant_bau + "'"
    DAT[2] = "DAT3=" + "'" + file_load_size + "'"
    DAT_bau[2] = DAT[2]
    DAT[3] = "DAT4=" + "'" + file_load_profile + "'"
    DAT_bau[3] = DAT[3]
    DAT[4] = "DAT5=" + "'" + file_gis + "'"
    DAT_bau[4] = "DAT5=" + "'" + file_gis_bau + "'"
    DAT[5] = "DAT6=" + "'" + file_storage + "'"
    DAT_bau[5] = "DAT6=" + "'" + file_storage_bau + "'"
    DAT[16] = "DAT17=" + "'" + file_NEM + "'"
    DAT_bau[16] = "DAT17=" + "'" + file_NEM_bau + "'"

    def _check_complete(self):
        if any(d is None for d in self.DAT) or any(d is None for d in self.DAT_bau):
            return False
        return True

    def add_load(self, load):

        #  fill in W, X, S bins
        for _ in range(8760 * 3):
            load.load_list.append(self.big_number)

        write_to_dat(self.file_load_profile, load.load_list, "LoadProfile")
        write_to_dat(self.file_load_size, load.annual_kwh, "AnnualElecLoad")

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

        # constant.dat contains NMILRegime
        # NMIL.dat contains NMILLimits and TechToNMILMapping

        TechToNMILMapping = self._get_REopt_techToNMILMapping(self.available_techs)
        TechToNMILMapping_bau = self._get_REopt_techToNMILMapping(self.bau_techs)

        write_to_dat(self.file_NEM,
                              [net_metering_limit, interconnection_limit, interconnection_limit*10],
                              'NMILLimits')
        write_to_dat(self.file_NEM, TechToNMILMapping, 'TechToNMILMapping', mode='a')

        write_to_dat(self.file_NEM_bau,
                              [net_metering_limit, interconnection_limit, interconnection_limit*10],
                              'NMILLimits')
        write_to_dat(self.file_NEM_bau, TechToNMILMapping_bau, 'TechToNMILMapping', mode='a')

    def add_storage(self, storage):
        self.storage = storage

        batt_level_coef = list()
        for batt_level in range(storage.level_count):
            for coef in storage.level_coefs:
                batt_level_coef.append(coef)

        # storage_bau.dat gets same definitions as storage.dat so that initializations don't fail in bau case
        # however, storage is typically 'turned off' by having max size set to zero in maxsizes_bau.dat
        write_to_dat(self.file_storage, batt_level_coef, 'BattLevelCoef')
        write_to_dat(self.file_storage_bau, batt_level_coef, 'BattLevelCoef')

        write_to_dat(self.file_storage, storage.soc_min, 'StorageMinChargePcent', mode='a')
        write_to_dat(self.file_storage_bau, storage.soc_min, 'StorageMinChargePcent', mode='a')

        write_to_dat(self.file_storage, storage.soc_init, 'InitSOC', mode='a')
        write_to_dat(self.file_storage_bau, storage.soc_init, 'InitSOC', mode='a')

        # efficiencies are defined in finalize method because their arrays depend on which Techs are defined

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

    def _get_REopt_array_tech_load(self, techs):
        """
        Many arrays are built from Tech and Load. As many as possible are defined here to reduce for-loop iterations
        :param techs: list of strings, eg. ['pv', 'pvnm', 'util']
        :return: prod_factor, tech_to_load, derate, etaStorIn, etaStorOut
        """
        prod_factor = list()
        tech_to_load = list()
        derate = list()
        eta_storage_in = list()
        eta_storage_out = list()

        for tech in techs:

            if eval('self.' + tech) is not None:

                derate.append(eval('self.' + tech + '.derate'))

                for load in self.available_loads:
                    
                    eta_storage_in.append(self.storage.roundtrip_efficiency if load == 'storage' else 1)
                    eta_storage_out.append(self.storage.roundtrip_efficiency if load == 'storage' else 1)
                    # only eta_storage_in is used in REopt currently

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

        return prod_factor, tech_to_load, derate, eta_storage_in, eta_storage_out

    def _get_REopt_techs(self, techs):
        reopt_techs = list()
        for tech in techs:

            if eval('self.' + tech) is not None:

                reopt_techs.append(tech.upper() if tech is not 'util' else tech.upper() + '1')

        return reopt_techs

    def _get_REopt_tech_classes(self, techs):
        """
        
        :param techs: list of strings, eg. ['pv', 'pvnm', 'util']
        :return: tech_classes, tech_to_tech_class
        """
        tech_classes = list()
        tech_to_tech_class = list()
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

        prod_factor, tech_to_load, derate, eta_storage_in, eta_storage_out = \
            self._get_REopt_array_tech_load(self.available_techs)
        prod_factor_bau, tech_to_load_bau, derate_bau, eta_storage_in_bau, eta_storage_out_bau = \
            self._get_REopt_array_tech_load(self.bau_techs)

        write_to_dat(self.file_constant, reopt_techs, 'Tech')
        write_to_dat(self.file_constant, tech_is_grid, 'TechIsGrid', mode='a')
        write_to_dat(self.file_constant, load_list, 'Load', mode='a')
        write_to_dat(self.file_constant, tech_to_load, 'TechToLoadMatrix', mode='a')
        write_to_dat(self.file_constant, reopt_tech_classes, 'TechClass', mode='a')
        write_to_dat(self.file_constant, self.NMILRegime, 'NMILRegime', mode='a')
        write_to_dat(self.file_constant, derate, 'TurbineDerate', mode='a')
        write_to_dat(self.file_constant, tech_to_tech_class, 'TechToTechClassMatrix', mode='a')

        write_to_dat(self.file_constant_bau, reopt_techs_bau, 'Tech')
        write_to_dat(self.file_constant_bau, tech_is_grid_bau, 'TechIsGrid', mode='a')
        write_to_dat(self.file_constant_bau, load_list, 'Load', mode='a')
        write_to_dat(self.file_constant_bau, tech_to_load_bau, 'TechToLoadMatrix', mode='a')
        write_to_dat(self.file_constant_bau, reopt_tech_classes_bau, 'TechClass', mode='a')
        write_to_dat(self.file_constant_bau, self.NMILRegime, 'NMILRegime', mode='a')
        write_to_dat(self.file_constant_bau, derate_bau, 'TurbineDerate', mode='a')
        write_to_dat(self.file_constant_bau, tech_to_tech_class_bau, 'TechToTechClassMatrix', mode='a')

        # ProdFactor stored in GIS.dat
        write_to_dat(self.file_gis, prod_factor, "ProdFactor")
        write_to_dat(self.file_gis_bau, prod_factor_bau, "ProdFactor")

        # storage.dat
        write_to_dat(self.file_storage, eta_storage_in, 'EtaStorIn', mode='a')
        write_to_dat(self.file_storage, eta_storage_out, 'EtaStorOut', mode='a')
        write_to_dat(self.file_storage_bau, eta_storage_in_bau, 'EtaStorIn', mode='a')
        write_to_dat(self.file_storage_bau, eta_storage_out_bau, 'EtaStorOut', mode='a')
