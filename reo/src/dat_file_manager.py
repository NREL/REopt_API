import os
import copy
from reo.log_levels import log
from reo.utilities import annuity, annuity_degr

big_number = 1e10
squarefeet_to_acre = 2.2957e-5

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
        else:
            # if passing a new run_id, replace old DFM with new one
            # probably only used when running tests, but could have application for parallel runs
            if 'run_id' in kwargs:
                    if kwargs['run_id'] != cls._instances.values()[0].run_id:
                        cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DatFileManager:
    """
    writes dat files and creates command line strings for dat file paths
    """

    __metaclass__ = Singleton
    DAT = [None] * 20
    DAT_bau = [None] * 20
    pv = None
    pvnm = None
    util = None
    storage = None
    site = None

    available_techs = ['pv', 'pvnm', 'util']  # order is critical for REopt!
    available_tech_classes = ['PV', 'UTIL']  # this is a REopt 'class', not a python class
    available_loads = ['retail', 'wholesale', 'export', 'storage']  # order is critical for REopt!
    bau_techs = ['util']
    NMILRegime = ['BelowNM', 'NMtoIL', 'AboveIL']
    
    def __init__(self, run_id, inputs_path, n_timesteps=8760):
        self.run_id = run_id
        self.n_timesteps = n_timesteps
        file_tail = str(run_id) + '.dat'
        file_tail_bau = str(run_id) + '_bau.dat'
        
        self.file_constant = os.path.join(inputs_path, 'constant_' + file_tail)
        self.file_constant_bau = os.path.join(inputs_path, 'constant_' + file_tail_bau)
        self.file_economics = os.path.join(inputs_path, 'economics_' + file_tail)
        self.file_economics_bau = os.path.join(inputs_path, 'economics_' + file_tail_bau)
        self.file_load_profile = os.path.join(inputs_path, 'Load8760_' + file_tail)
        self.file_load_size = os.path.join(inputs_path, 'LoadSize_' + file_tail)
        self.file_gis = os.path.join(inputs_path, "GIS_" + file_tail)
        self.file_gis_bau = os.path.join(inputs_path, "GIS_" + file_tail_bau)
        self.file_storage = os.path.join(inputs_path, 'storage_' + file_tail)
        self.file_storage_bau = os.path.join(inputs_path, 'storage_' + file_tail_bau)
        self.file_max_size = os.path.join(inputs_path, 'maxsizes_' + file_tail)
        self.file_max_size_bau = os.path.join(inputs_path, 'maxsizes_' + file_tail_bau)
        self.file_NEM = os.path.join(inputs_path, 'NMIL_' + file_tail)
        self.file_NEM_bau = os.path.join(inputs_path, 'NMIL_' + file_tail_bau)
        
        self.DAT[0] = "DAT1=" + "'" + self.file_constant + "'"
        self.DAT_bau[0] = "DAT1=" + "'" + self.file_constant_bau + "'"
        self.DAT[1] = "DAT2=" + "'" + self.file_economics + "'"
        self.DAT_bau[1] = "DAT2=" + "'" + self.file_economics_bau + "'"
        self.DAT[2] = "DAT3=" + "'" + self.file_load_size + "'"
        self.DAT_bau[2] = self.DAT[2]
        self.DAT[3] = "DAT4=" + "'" + self.file_load_profile + "'"
        self.DAT_bau[3] = self.DAT[3]
        self.DAT[4] = "DAT5=" + "'" + self.file_gis + "'"
        self.DAT_bau[4] = "DAT5=" + "'" + self.file_gis_bau + "'"
        self.DAT[5] = "DAT6=" + "'" + self.file_storage + "'"
        self.DAT_bau[5] = "DAT6=" + "'" + self.file_storage_bau + "'"
        self.DAT[6] = "DAT7=" + "'" + self.file_max_size + "'"
        self.DAT_bau[6] = "DAT7=" + "'" + self.file_max_size_bau + "'"
        self.DAT[16] = "DAT17=" + "'" + self.file_NEM + "'"
        self.DAT_bau[16] = "DAT17=" + "'" + self.file_NEM_bau + "'"

    def _check_complete(self):
        if any(d is None for d in self.DAT) or any(d is None for d in self.DAT_bau):
            return False
        return True

    def add_load(self, load): 
        #  fill in W, X, S bins
        for _ in range(8760 * 3):
            load.load_list.append(big_number)
                              
        write_to_dat(self.file_load_profile, load.load_list, "LoadProfile")
        write_to_dat(self.file_load_size, load.annual_kwh, "AnnualElecLoad")

    def add_economics(self, economics_dict):
        for k, v in economics_dict.iteritems():
            try:
                write_to_dat(self.file_economics, v, k, 'a')
            except:
                log('ERROR', 'Error writing economics for ' + k)


        # Economics.setup_financial_parameters
        sf = self.site.financials
        pwf_owner = annuity(sf.analysis_period, 0, sf.owner_discount_rate_nominal) # not used in REopt
        pwf_offtaker = annuity(sf.analysis_period, 0, sf.offtaker_discount_rate_nominal) # not used in REopt
        pwf_om = annuity(sf.analysis_period, sf.rate_inflation, sf.owner_discount_rate_nominal)
        pwf_e = annuity(sf.analysis_period, sf.rate_escalation_nominal, sf.offtaker_discount_rate_nominal)
        pwf_op = annuity(sf.analysis_period, sf.rate_escalation_nominal, sf.owner_discount_rate_nominal)

        if pwf_owner == 0 or sf.owner_tax_rate == 0:
            two_party_factor = 0
        else:
            two_party_factor = (pwf_offtaker * sf.offtaker_tax_rate) \
                                / (pwf_owner * sf.owner_tax_rate)


        levelization_factor = list()
        production_incentive_levelization_factor = list()

        for tech in self.available_techs:

            if eval('self.' + tech) is not None:

                if tech != 'util':

                    #################
                    # NOTE: economics.py uses real rates to calculate pv_levelization_factor and
                    #       pv_levelization_factor_production_incentive, changed to nominal for consistency,
                    #       which may break some tests.
                    ################
                    levelization_factor.append(
                        round(
                            annuity_degr(sf.analysis_period, sf.rate_escalation_nominal,
                                         sf.offtaker_discount_rate_nominal,
                                         -eval('self.' + tech + '.degradation_rate'))
                            , 5
                        )
                    )
                    production_incentive_levelization_factor.append(
                        round(
                            annuity_degr(eval('self.' + tech + '.incentives.production_based.duration_years'),
                                         sf.rate_escalation_nominal, sf.offtaker_discount_rate_nominal,
                                         -eval('self.' + tech + '.degradation_rate')) / \
                            annuity(eval('self.' + tech + '.incentives.production_based.duration_years'),
                                    sf.rate_escalation_nominal, sf.offtaker_discount_rate_nominal)
                            , 5
                        )
                    )
                    #################
                    ################
                elif tech == 'util':

                    levelization_factor.append(self.util.degradation_rate)
                    production_incentive_levelization_factor.append(1.0)

    def add_pv(self, pv):
        self.pv = pv
        self.pvnm = copy.deepcopy(pv)
        self.pvnm.nmil_regime = 'NMtoIL'

    def add_util(self, util):
        self.util = util

    def add_site(self, site):
        self.site = site

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
        :return: prod_factor, tech_to_load, tech_is_grid, derate, etaStorIn, etaStorOut
        """
        prod_factor = list()
        tech_to_load = list()
        tech_is_grid = list()
        derate = list()
        eta_storage_in = list()
        eta_storage_out = list()
        om_dollars_per_kw = list()

        for tech in techs:

            if eval('self.' + tech) is not None:

                tech_is_grid.append(int(eval('self.' + tech + '.is_grid')))
                derate.append(eval('self.' + tech + '.derate'))
                om_dollars_per_kw.append(eval('self.' + tech + '.om_dollars_per_kw'))

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

        return prod_factor, tech_to_load, tech_is_grid, derate, eta_storage_in, eta_storage_out, om_dollars_per_kw

    def _get_REopt_techs(self, techs):
        reopt_techs = list()
        for tech in techs:

            if eval('self.' + tech) is not None:

                reopt_techs.append(tech.upper() if tech is not 'util' else tech.upper() + '1')

        return reopt_techs

    def _get_REopt_tech_classes(self, techs):
        """
        
        :param techs: list of strings, eg. ['pv', 'pvnm', 'util']
        :return: tech_classes, tech_class_min_size, tech_to_tech_class
        """
        tech_classes = list()
        tech_class_min_size = list()
        tech_to_tech_class = list()
        for tech in techs:

            if eval('self.' + tech) is not None:

                for tc in self.available_tech_classes:

                    if tech.upper() == tc:
                        tech_classes.append(tc)
                        tech_class_min_size.append(eval('self.' + tech + '.min_kw'))

                    if eval('self.' + tech + '.reopt_class').upper() == tc.upper():
                        tech_to_tech_class.append(1)
                    else:
                        tech_to_tech_class.append(0)

        return tech_classes, tech_class_min_size, tech_to_tech_class

    def _get_REopt_tech_max_sizes(self, techs):
        max_sizes = list()
        for tech in techs:

            if eval('self.' + tech) is not None:

                site_kw_max = eval('self.' + tech + '.max_kw')
                
                if eval('self.' + tech + '.acres_per_kw') is not None:

                    if self.site.roof_squarefeet is not None and self.site.land_acres is not None:
                        # don't restrict unless they specify both land_area and roof_area,
                        # otherwise one of them is "unlimited" in UI
                        acres_available = self.site.roof_squarefeet * squarefeet_to_acre \
                                          + self.site.land_acres
                        site_kw_max = acres_available / eval('self.' + tech + '.acres_per_kw')

                max_sizes.append(min(eval('self.' + tech + '.max_kw'), site_kw_max))

        return max_sizes

    def finalize(self):
        """
        necessary for writing out parameters that depend on which Techs are defined
        eg. in REopt ProdFactor: array (Tech,Load,TimeStep).
        Note: whether or not a given Tech can serve a given Load can also be controlled via TechToLoadMatrix
        :return: None
        """

        reopt_techs = self._get_REopt_techs(self.available_techs)
        reopt_techs_bau = self._get_REopt_techs(self.bau_techs)

        load_list = ['1R', '1W', '1X', '1S']  # same for BAU

        reopt_tech_classes, tech_class_min_size, tech_to_tech_class = self._get_REopt_tech_classes(self.available_techs)
        reopt_tech_classes_bau, tech_class_min_size_bau, tech_to_tech_class_bau = self._get_REopt_tech_classes(self.bau_techs)
        reopt_tech_classes_bau = ['PV', 'UTIL']  # not sure why bau needs PV tech class?

        prod_factor, tech_to_load, tech_is_grid, derate, eta_storage_in, eta_storage_out, om_dollars_per_kw = \
            self._get_REopt_array_tech_load(self.available_techs)
        prod_factor_bau, tech_to_load_bau, tech_is_grid_bau, derate_bau, eta_storage_in_bau, eta_storage_out_bau, \
            om_dollars_per_kw_bau = \
            self._get_REopt_array_tech_load(self.bau_techs)
        
        max_sizes = self._get_REopt_tech_max_sizes(self.available_techs)
        max_sizes_bau = self._get_REopt_tech_max_sizes(self.bau_techs)

        # DAT1 = constant.dat, contains parameters that others depend on for initialization
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

        # maxsizes.dat
        write_to_dat(self.file_max_size, max_sizes, 'MaxSize')
        write_to_dat(self.file_max_size, self.storage.min_kw, 'MinStorageSizeKW', mode='a')
        write_to_dat(self.file_max_size, self.storage.max_kw, 'MaxStorageSizeKW', mode='a')
        write_to_dat(self.file_max_size, self.storage.min_kwh, 'MinStorageSizeKWH', mode='a')
        write_to_dat(self.file_max_size, self.storage.max_kwh, 'MaxStorageSizeKWH', mode='a')
        write_to_dat(self.file_max_size, tech_class_min_size, 'TechClassMinSize', mode='a')

        write_to_dat(self.file_max_size_bau, max_sizes_bau, 'MaxSize')
        write_to_dat(self.file_max_size_bau, 0, 'MinStorageSizeKW', mode='a')
        write_to_dat(self.file_max_size_bau, 0, 'MaxStorageSizeKW', mode='a')
        write_to_dat(self.file_max_size_bau, 0, 'MinStorageSizeKWH', mode='a')
        write_to_dat(self.file_max_size_bau, 0, 'MaxStorageSizeKWH', mode='a')
        write_to_dat(self.file_max_size_bau, tech_class_min_size_bau, 'TechClassMinSize', mode='a')
