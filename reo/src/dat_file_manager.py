import os
import copy
from reo.src.urdb_parse import UrdbParse
from reo.utilities import annuity, annuity_degr, degradation_factor, slope, intercept, insert_p_after_u_bp, insert_p_bp, \
    insert_u_after_p_bp, insert_u_bp, setup_capital_cost_incentive
max_incentive = 1e10

big_number = 1e10
squarefeet_to_acre = 2.2957e-5


def _write_var(f, var, dat_var):
    f.write(dat_var + ": [\n")
    if isinstance(var, list):
        for v in var:
            if isinstance(v, list):  # elec_tariff contains list of lists
                f.write('[')
                for i in v:
                    f.write(str(i) + ' ')
                f.write(']\n')
            else:
                f.write(str(v) + "\n")
    else:
        f.write(str(var) + "\n")
    f.write("]\n")


def write_to_dat(path, var, dat_var, mode='w'):
    cmd_line_vars = (
        'DemandBinCount',
        'FuelBinCount',
        'NumRatchets',
    )
    with open(path, mode) as f:
        if dat_var in cmd_line_vars:
            f.write(dat_var + '=' + str(var) + '\n')
        else:
            _write_var(f, var, dat_var)


class DatFileManager:
    """
    writes dat files and creates command line strings for dat file paths
    """
    pv = None
    pvnm = None
    wind = None
    windnm = None
    generator = None
    util = None
    storage = None
    site = None
    elec_tariff = None

    available_techs = ['pv', 'pvnm', 'wind', 'windnm', 'generator', 'util']  # order is critical for REopt!
    available_tech_classes = ['PV', 'WIND', 'GENERATOR', 'UTIL']  # this is a REopt 'class', not a python class
    available_loads = ['retail', 'wholesale', 'export', 'storage']  # order is critical for REopt!
    bau_techs = ['util']
    NMILRegime = ['BelowNM', 'NMtoIL', 'AboveIL']

    def __init__(self, run_id, paths, n_timesteps=8760):
        self.run_id = run_id
        self.paths = paths
        self.n_timesteps = n_timesteps
        self.pwf_e = 0  # used in results.py -> outage_costs.py to escalate & discount avoided outage costs
        file_tail = str(run_id) + '.dat'
        file_tail_bau = str(run_id) + '_bau.dat'

        self.command_line_args = list()
        self.command_line_args_bau = list()

        self.DAT = [None] * 20
        self.DAT_bau = [None] * 20

        self.file_constant = os.path.join(paths['inputs'], 'constant_' + file_tail)
        self.file_constant_bau = os.path.join(paths['inputs'], 'constant_' + file_tail_bau)
        self.file_economics = os.path.join(paths['inputs'], 'economics_' + file_tail)
        self.file_economics_bau = os.path.join(paths['inputs'], 'economics_' + file_tail_bau)
        self.file_load_profile = os.path.join(paths['inputs'], 'Load8760_' + file_tail)
        self.file_load_size = os.path.join(paths['inputs'], 'LoadSize_' + file_tail)
        self.file_load_profile_bau = os.path.join(paths['inputs'], 'Load8760_' + file_tail_bau)
        self.file_load_size_bau = os.path.join(paths['inputs'], 'LoadSize_' + file_tail_bau)
        self.file_gis = os.path.join(paths['inputs'], "GIS_" + file_tail)
        self.file_gis_bau = os.path.join(paths['inputs'], "GIS_" + file_tail_bau)
        self.file_storage = os.path.join(paths['inputs'], 'storage_' + file_tail)
        self.file_storage_bau = os.path.join(paths['inputs'], 'storage_' + file_tail_bau)
        self.file_max_size = os.path.join(paths['inputs'], 'maxsizes_' + file_tail)
        self.file_max_size_bau = os.path.join(paths['inputs'], 'maxsizes_' + file_tail_bau)
        self.file_NEM = os.path.join(paths['inputs'], 'NMIL_' + file_tail)
        self.file_NEM_bau = os.path.join(paths['inputs'], 'NMIL_' + file_tail_bau)

        self.file_demand_periods = os.path.join(paths['utility'], 'TimeStepsDemand.dat')
        self.file_demand_rates = os.path.join(paths['utility'], 'DemandRate.dat')
        self.file_demand_rates_monthly = os.path.join(paths['utility'], 'DemandRateMonth.dat')
        self.file_demand_ratchets_monthly = os.path.join(paths['utility'], 'TimeStepsDemandMonth.dat')
        self.file_demand_lookback = os.path.join(paths['utility'], 'LookbackMonthsAndPercent.dat')
        self.file_demand_num_ratchets = os.path.join(paths['utility'], 'NumRatchets.dat')
        self.file_energy_rates = os.path.join(paths['utility'], 'FuelCost.dat')
        self.file_energy_rates_bau = os.path.join(paths['utility'], 'FuelCostBase.dat')
        self.file_energy_tiers_num = os.path.join(paths['utility'], 'bins.dat')
        self.file_energy_burn_rate = os.path.join(paths['utility'], 'FuelBurnRate.dat')
        self.file_energy_burn_rate_bau = os.path.join(paths['utility'], 'FuelBurnRateBase.dat')
        self.file_max_in_tiers = os.path.join(paths['utility'], 'UtilityTiers.dat')
        self.file_export_rates = os.path.join(paths['utility'], 'ExportRates.dat')
        self.file_export_rates_bau = os.path.join(paths['utility'], 'ExportRatesBase.dat')
        
        self.DAT[0] = "DAT1=" + "'" + self.file_constant + "'"
        self.DAT_bau[0] = "DAT1=" + "'" + self.file_constant_bau + "'"
        self.DAT[1] = "DAT2=" + "'" + self.file_economics + "'"
        self.DAT_bau[1] = "DAT2=" + "'" + self.file_economics_bau + "'"
        self.DAT[2] = "DAT3=" + "'" + self.file_load_size + "'"
        self.DAT_bau[2] = "DAT3=" + "'" + self.file_load_size_bau + "'"
        self.DAT[3] = "DAT4=" + "'" + self.file_load_profile + "'"
        self.DAT_bau[3] = "DAT4=" + "'" + self.file_load_profile_bau + "'"
        self.DAT[4] = "DAT5=" + "'" + self.file_gis + "'"
        self.DAT_bau[4] = "DAT5=" + "'" + self.file_gis_bau + "'"
        self.DAT[5] = "DAT6=" + "'" + self.file_storage + "'"
        self.DAT_bau[5] = "DAT6=" + "'" + self.file_storage_bau + "'"
        self.DAT[6] = "DAT7=" + "'" + self.file_max_size + "'"
        self.DAT_bau[6] = "DAT7=" + "'" + self.file_max_size_bau + "'"
        self.DAT[16] = "DAT17=" + "'" + self.file_NEM + "'"
        self.DAT_bau[16] = "DAT17=" + "'" + self.file_NEM_bau + "'"

        self.command_line_args.append("ScenarioNum=" + str(run_id))
        self.command_line_args_bau.append("ScenarioNum=" + str(run_id))

    def add_load(self, load): 
        #  fill in W, X, S bins
        for _ in range(self.n_timesteps * 3):
            load.load_list.append(big_number)
                              
        write_to_dat(self.file_load_profile, load.load_list, "LoadProfile")
        write_to_dat(self.file_load_size, load.annual_kwh, "AnnualElecLoad")

        write_to_dat(self.file_load_profile_bau, load.bau_load_list, "LoadProfile")
        write_to_dat(self.file_load_size_bau, load.bau_annual_kwh, "AnnualElecLoad")

    def add_pv(self, pv):
        junk = pv.prod_factor  # avoids redundant PVWatts call for pvnm
        self.pv = pv
        self.pvnm = copy.deepcopy(pv)
        self.pvnm.nmil_regime = 'NMtoIL'

        if self.pv.existing_kw > 0:
            self.bau_techs = ['pv', 'pvnm', 'util']

    def add_wind(self, wind):
        self.wind = wind
        self.windnm = copy.deepcopy(wind)
        self.windnm.nmil_regime = 'NMtoIL'

    def add_util(self, util):
        self.util = util

    def add_generator(self, generator):
        self.generator = generator

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

        write_to_dat(self.file_storage, storage.soc_min_pct, 'StorageMinChargePcent', mode='a')
        write_to_dat(self.file_storage_bau, storage.soc_min_pct, 'StorageMinChargePcent', mode='a')

        write_to_dat(self.file_storage, storage.soc_init_pct, 'InitSOC', mode='a')
        write_to_dat(self.file_storage_bau, storage.soc_init_pct, 'InitSOC', mode='a')

        # efficiencies are defined in finalize method because their arrays depend on which Techs are defined

    def add_elec_tariff(self, elec_tariff):
        self.elec_tariff = elec_tariff
            
    def _get_REopt_pwfs(self, techs):

        sf = self.site.financial
        pwf_owner = annuity(sf.analysis_years, 0, sf.owner_discount_pct) # not used in REopt
        pwf_offtaker = annuity(sf.analysis_years, 0, sf.offtaker_discount_pct)  # not used in REopt
        pwf_om = annuity(sf.analysis_years, sf.om_cost_escalation_pct, sf.owner_discount_pct)
        pwf_e = annuity(sf.analysis_years, sf.escalation_pct, sf.offtaker_discount_pct)
        self.pwf_e = pwf_e
        # pwf_op = annuity(sf.analysis_years, sf.escalation_pct, sf.owner_discount_pct)

        if pwf_owner == 0 or sf.owner_tax_pct == 0:
            two_party_factor = 0
        else:
            two_party_factor = (pwf_offtaker * sf.offtaker_tax_pct) \
                                / (pwf_owner * sf.owner_tax_pct)

        levelization_factor = list()
        production_incentive_levelization_factor = list()

        for tech in techs:

            if eval('self.' + tech) is not None:

                if tech in ['pv', 'pvnm']:  # pv has degradation

                    #################
                    # NOTE: I don't think that levelization factors should include an escalation rate.  The degradation
                    # does not escalate in out years.
                    ################
                    degradation_pct = eval('self.' + tech + '.degradation_pct')
                    levelization_factor.append(round(degradation_factor(sf.analysis_years, degradation_pct), 5))
                    production_incentive_levelization_factor.append(
                        round(degradation_factor(eval('self.' + tech + '.incentives.production_based.years'),
                                                 degradation_pct), 5))
                    ################
                else:

                    levelization_factor.append(1.0)
                    production_incentive_levelization_factor.append(1.0)

        return levelization_factor, production_incentive_levelization_factor, pwf_e, pwf_om, two_party_factor

    def _get_REopt_production_incentives(self, techs):

        sf = self.site.financial
        pwf_prod_incent = list()
        prod_incent_rate = list()
        max_prod_incent = list()
        max_size_for_prod_incent = list()

        for tech in techs:

            if eval('self.' + tech) is not None:
                
                if tech not in ['util', 'generator']:

                    # prod incentives don't need escalation
                    pwf_prod_incent.append(
                        annuity(eval('self.' + tech + '.incentives.production_based.years'),
                                0, sf.offtaker_discount_pct)
                    )
                    max_prod_incent.append(
                        eval('self.' + tech + '.incentives.production_based.max_us_dollars_per_kw')
                    )
                    max_size_for_prod_incent.append(
                        eval('self.' + tech + '.incentives.production_based.max_kw')
                    )
    
                    for load in self.available_loads:
                        prod_incent_rate.append(
                            eval('self.' + tech + '.incentives.production_based.us_dollars_per_kw')
                        )
    
                else:
    
                    pwf_prod_incent.append(0)
                    max_prod_incent.append(0)
                    max_size_for_prod_incent.append(0)
    
                    for load in self.available_loads:
                        prod_incent_rate.append(0)
                    
        return pwf_prod_incent, prod_incent_rate, max_prod_incent, max_size_for_prod_incent
        
    def _get_REopt_cost_curve(self, techs):

        regions = ['utility', 'state', 'federal', 'combined']
        cap_cost_slope = list()
        cap_cost_x = list()
        cap_cost_yint = list()
        n_segments_out = 0
        n_segments = None
        tech_to_size = float(big_number/1e4)  # sized such that default max incentives will not create breakpoint

        # generating existing_kw_flag for padding the cost curve values of wind for the case when pv_existing_kw > 0
        for tech in techs:

            if eval('self.' + tech) is not None and tech not in ['util', 'generator']:

                existing_kw = 0
                if hasattr(eval('self.' + tech), 'existing_kw'):
                    if eval('self.' + tech + '.existing_kw') is not None:
                        existing_kw_flag = True

        for tech in techs:

            if eval('self.' + tech) is not None and tech not in ['util', 'generator']:

                existing_kw = 0
                if hasattr(eval('self.' + tech), 'existing_kw'):
                    if eval('self.' + tech + '.existing_kw') is not None:
                        existing_kw = eval('self.' + tech + '.existing_kw')

                tech_cost = eval('self.' + tech + '.installed_cost_us_dollars_per_kw')
                tech_incentives = dict()
                
                for region in regions[:-1]:
                    tech_incentives[region] = dict()

                    if region == 'federal' or region == 'total':
                        tech_incentives[region]['%'] = eval('self.' + tech + '.incentives.' + region + '.itc')
                        tech_incentives[region]['%_max'] = eval('self.' + tech + '.incentives.' + region + '.itc_max')
                    else: # region == 'state' or region == 'utility'
                        tech_incentives[region]['%'] = eval('self.' + tech + '.incentives.' + region + '.ibi')
                        tech_incentives[region]['%_max'] = eval('self.' + tech + '.incentives.' + region + '.ibi_max')

                    tech_incentives[region]['rebate'] = eval('self.' + tech + '.incentives.' + region + '.rebate')
                    tech_incentives[region]['rebate_max'] = eval('self.' + tech + '.incentives.' + region + '.rebate_max')

                    # Workaround to consider fact that REopt incentive calculation works best if "unlimited" incentives are entered as 0
                    if tech_incentives[region]['%_max'] == max_incentive:
                        tech_incentives[region]['%_max'] = 0
                    if tech_incentives[region]['rebate_max'] == max_incentive:
                        tech_incentives[region]['rebate_max'] = 0

                # Intermediate Cost curve
                xp_array_incent = dict()
                xp_array_incent['utility'] = [0.0, tech_to_size]  #kW
                yp_array_incent = dict()
                yp_array_incent['utility'] = [0.0, tech_to_size * tech_cost]  #$

                # Final cost curve
                cost_curve_bp_x = [0]
                cost_curve_bp_y = [0]

                for r in range(len(regions)-1):

                    region = regions[r]  # regions = ['utility', 'state', 'federal', 'combined']
                    next_region = regions[r + 1]

                    # Apply incentives, initialize first value
                    xp_array_incent[next_region] = [0]
                    yp_array_incent[next_region] = [0]
        
                    # percentage based incentives
                    p = float(tech_incentives[region]['%'])
                    p_cap = float(tech_incentives[region]['%_max'])
        
                    # rebates, for some reason called 'u' in REopt
                    u = float(tech_incentives[region]['rebate'])
                    u_cap = float(tech_incentives[region]['rebate_max'])
        
                    # reset switches and break point counter
                    switch_percentage = False
                    switch_rebate = False

                    if p == 0 or p_cap == 0:
                        switch_percentage = True
                    if u == 0 or u_cap == 0:
                        switch_rebate = True

                    # start at second point, first is always zero
                    for point in range(1, len(xp_array_incent[region])):

                        # previous points
                        xp_prev = xp_array_incent[region][point - 1]
                        yp_prev = yp_array_incent[region][point - 1]
        
                        # current, unadjusted points
                        xp = xp_array_incent[region][point]
                        yp = yp_array_incent[region][point]
        
                        # initialize the adjusted points on cost curve
                        xa = xp
                        ya = yp
        
                        # initialize break points
                        u_xbp = 0
                        u_ybp = 0
                        p_xbp = 0
                        p_ybp = 0
        
                        if not switch_rebate:
                            u_xbp = u_cap / u
                            u_ybp = slope(xp_prev, yp_prev, xp, yp) * u_xbp + intercept(xp_prev, yp_prev, xp, yp)
        
                        if not switch_percentage:
                            p_xbp = (p_cap / p - intercept(xp_prev, yp_prev, xp, yp)) / slope(xp_prev, yp_prev, xp, yp)
                            p_ybp = p_cap / p
        
                        if ((p * yp) < p_cap or p_cap == 0) and ((u * xp) < u_cap or u_cap == 0):
                            ya = yp - (p * yp + u * xp)
                        elif (p * yp) < p_cap and (u * xp) >= u_cap:
                            if not switch_rebate:
                                if u * xp != u_cap:
                                    xp_array_incent, yp_array_incent = \
                                        insert_u_bp(xp_array_incent, yp_array_incent, next_region, u_xbp, u_ybp, p, u_cap)
                                switch_rebate = True
                            ya = yp - (p * yp + u_cap)
                        elif (p * yp) >= p_cap and (u * xp) < u_cap:
                            if not switch_percentage:
                                if p * yp != p_cap:
                                    xp_array_incent, yp_array_incent = \
                                        insert_p_bp(xp_array_incent, yp_array_incent, next_region, p_xbp, p_ybp, u, p_cap)
                                switch_percentage = True
                            ya = yp - (p_cap + xp * u)
                        elif p * yp >= p_cap and u * xp >= u_cap:
                            if not switch_rebate and not switch_percentage:
                                if p_xbp == u_xbp:
                                    xp_array_incent, yp_array_incent = \
                                        insert_u_bp(xp_array_incent, yp_array_incent, next_region, u_xbp, u_ybp, p, u_cap)
                                    switch_percentage = True
                                    switch_rebate = True
                                elif p_xbp < u_xbp:
                                    if p * yp != p_cap:
                                        xp_array_incent, yp_array_incent = \
                                            insert_p_bp(xp_array_incent, yp_array_incent, next_region, p_xbp, p_ybp, u,
                                                        p_cap)
                                    switch_percentage = True
                                    if u * xp != u_cap:
                                        xp_array_incent, yp_array_incent = \
                                            insert_u_after_p_bp(xp_array_incent, yp_array_incent, next_region, u_xbp, u_ybp,
                                                                p, p_cap, u_cap)
                                    switch_rebate = True
                                else:
                                    if u * xp != u_cap:
                                        xp_array_incent, yp_array_incent = \
                                            insert_u_bp(xp_array_incent, yp_array_incent, next_region, u_xbp, u_ybp, p, u_cap)
                                    switch_rebate = True
                                    if p * yp != p_cap:
                                        xp_array_incent, yp_array_incent = \
                                            insert_p_after_u_bp(xp_array_incent, yp_array_incent, next_region, p_xbp, p_ybp,
                                                                u, u_cap, p_cap)
                                    switch_percentage = True
                            elif switch_rebate and not switch_percentage:
                                if p * yp != p_cap:
                                    xp_array_incent, yp_array_incent = \
                                        insert_p_after_u_bp(xp_array_incent, yp_array_incent, next_region, p_xbp, p_ybp, u,
                                                            u_cap, p_cap)
                                switch_percentage = True
                            elif switch_percentage and not switch_rebate:
                                if u * xp != u_cap:
                                    xp_array_incent, yp_array_incent = \
                                        insert_u_after_p_bp(xp_array_incent, yp_array_incent, next_region, u_xbp, u_ybp, p,
                                                            p_cap, u_cap)
                                switch_rebate = True
        
                            # Finally compute adjusted values
                            if p_cap == 0:
                                ya = yp - (p * yp + u_cap)
                            elif u_cap == 0:
                                ya = yp - (p_cap + u * xp)
                            else:
                                ya = yp - (p_cap + u_cap)

                        xp_array_incent[next_region].append(xa)
                        yp_array_incent[next_region].append(ya)

                        # compute cost curve, funky logic in REopt ignores everything except xa, ya
                        if region == 'federal':
                            cost_curve_bp_x.append(xa)
                            cost_curve_bp_y.append(ya)

                tmp_cap_cost_slope = list()
                tmp_cap_cost_yint = list()

                for seg in range(1, len(cost_curve_bp_x)):
                    tmp_slope = round((cost_curve_bp_y[seg] - cost_curve_bp_y[seg - 1]) /
                                      (cost_curve_bp_x[seg] - cost_curve_bp_x[seg - 1]), 0)
                    tmp_y_int = round(cost_curve_bp_y[seg] - tmp_slope * cost_curve_bp_x[seg], 0)
        
                    tmp_cap_cost_slope.append(tmp_slope)
                    tmp_cap_cost_yint.append(tmp_y_int)

                n_segments =len(tmp_cap_cost_slope)

                # Following logic modifies the cap cost segments to account for the tax benefits of the ITC and MACRs
                updated_cap_cost_slope = list()
                updated_y_intercept = list()

                for s in range(n_segments):
                    
                    if cost_curve_bp_x[s + 1] > 0:
                        # Remove federal incentives for ITC basis and tax benefit calculations
                        itc = eval('self.' + tech + '.incentives.federal.itc')
                        rebate_federal = eval('self.' + tech + '.incentives.federal.rebate')
                        itc_unit_basis = (tmp_cap_cost_slope[s] + rebate_federal) / (1 - itc)

                    sf = self.site.financial
                    updated_slope = setup_capital_cost_incentive(itc_unit_basis,  # input tech cost with incentives, but no ITC
                                                                 0,
                                                                 sf.analysis_years,
                                                                 sf.owner_discount_pct,
                                                                 sf.owner_tax_pct,
                                                                 itc,
                                                                 eval('self.' + tech + '.incentives.macrs_schedule'),
                                                                 eval('self.' + tech + '.incentives.macrs_bonus_pct'),
                                                                 eval('self.' + tech + '.incentives.macrs_itc_reduction'))

                    # The way REopt incentives currently work, the federal rebate is the only incentive that doesn't reduce ITC basis
                    updated_slope -= rebate_federal
                    updated_cap_cost_slope.append(updated_slope)

                for p in range(1, n_segments + 1):
                    cost_curve_bp_y[p] = cost_curve_bp_y[p - 1] + updated_cap_cost_slope[p - 1] * \
                                                                  (cost_curve_bp_x[p] - cost_curve_bp_x[p - 1])
                    updated_y_intercept.append(cost_curve_bp_y[p] - updated_cap_cost_slope[p - 1] * cost_curve_bp_x[p])
        
                tmp_cap_cost_slope = updated_cap_cost_slope
                tmp_cap_cost_yint = updated_y_intercept

                """
                Adjust first cost curve segment to account for existing_kw.
                NOTE:
                - first X "breakpoint" and y-intercept must ALWAYS be zero (to be compatible with REopt constraints and
                    costing formulation.
                - if existing_kw > 0, then the first slope must also be zero (cannot be negative!).

                Steps:
                    1. find the segment for existing_kw
                    2. find the y-value for existing_kw (which is an x-value)
                    3. set the cost curve to x-axis from zero kw up to existing_kw
                    4. shift the rest of the cost curve down by the y-value found in step 2
                    5. reset n_segments (existing_kw can add a breakpoint, or take them away)
                """
                if existing_kw > 0:

                    # find the first index in cost_curve_bp_x that is larger than existing_kw, then reset cost curve
                    for i, bp in enumerate(cost_curve_bp_x[1:]):  # need to make sure existing_kw is never larger then last bp
                        if bp <= existing_kw:
                            continue
                        else:
                            y_shift = -(tmp_cap_cost_slope[i] * existing_kw + tmp_cap_cost_yint[i])
                            tmp_cap_cost_slope = [0] + tmp_cap_cost_slope[i:]
                            tmp_cap_cost_yint = [0] + [y + y_shift for y in tmp_cap_cost_yint[i:]]
                            cost_curve_bp_x = [0, existing_kw] + cost_curve_bp_x[i+1:]
                            n_segments = len(tmp_cap_cost_slope)
                            break

                elif existing_kw_flag:

                    for i, bp in enumerate(cost_curve_bp_x[1:]):  # need to make sure existing_kw is never larger then last bp
                        tmp_cap_cost_slope = tmp_cap_cost_slope[i:] + [1] # adding 1 as the slope for wind's second segment
                        tmp_cap_cost_yint = [0] + [big_number]    
                        cost_curve_bp_x = [0] + [cost_curve_bp_x[i+1]] + [cost_curve_bp_x[-1]+1]
                        n_segments = len(tmp_cap_cost_slope)
                        break


                # append the current Tech's segments to the arrays that will be passed to REopt

                cap_cost_slope += tmp_cap_cost_slope
                cap_cost_yint += tmp_cap_cost_yint
                cap_cost_x += cost_curve_bp_x

                # Have to take n_segments as the maximum number across all technologies
                n_segments_out = max(n_segments, n_segments_out)

            elif eval('self.' + tech) is not None and tech in ['util', 'generator']:

                if n_segments is None:  # only util in techs (usually BAU case)
                    n_segments = 1

                for seg in range(n_segments):
                    cap_cost_slope.append(0)
                    cap_cost_yint.append(0)

                for seg in range(n_segments + 1):
                    x = 0
                    if len(cap_cost_x) > 0 and cap_cost_x[-1] == 0:
                        x = big_number
                    cap_cost_x.append(x)

                # Have to take n_segments as the maximum number across all technologies
                n_segments_out = max(n_segments, n_segments_out)

        return cap_cost_slope, [0]+cap_cost_x[1:], cap_cost_yint, n_segments_out

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
        om_cost_us_dollars_per_kw = list()

        for tech in techs:

            if eval('self.' + tech) is not None:

                tech_is_grid.append(int(eval('self.' + tech + '.is_grid')))
                derate.append(eval('self.' + tech + '.derate'))
                om_cost_us_dollars_per_kw.append(eval('self.' + tech + '.om_cost_us_dollars_per_kw'))

                for load in self.available_loads:

                    eta_storage_in.append(self.storage.rectifier_efficiency_pct *
                                          self.storage.internal_efficiency_pct**0.5 if load == 'storage' else 1)

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
                        tech_to_load[-1] = int(self.storage.canGridCharge)

        for load in self.available_loads:
            # eta_storage_out is array(Load) of real
            eta_storage_out.append(self.storage.inverter_efficiency_pct * self.storage.internal_efficiency_pct**0.5
                                   if load == 'storage' else 1)

        # In BAU case, storage.dat must be filled out for REopt initializations, but max size is set to zero

        return prod_factor, tech_to_load, tech_is_grid, derate, eta_storage_in, eta_storage_out, om_cost_us_dollars_per_kw

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
        tech_class_min_size = list()  # array(TechClass)
        tech_to_tech_class = list()  # array(Tech, TechClass)

        for tc in self.available_tech_classes:

            if eval('self.' + tc.lower()) is not None and tc.lower() in techs:
                tech_class_min_size.append(eval('self.' + tc.lower() + '.min_kw'))
            else:
                tech_class_min_size.append(0)

        for tech in techs:

            if eval('self.' + tech) is not None:

                for tc in self.available_tech_classes:

                    if eval('self.' + tech + '.reopt_class').upper() == tc.upper():
                        tech_to_tech_class.append(1)
                    else:
                        tech_to_tech_class.append(0)

        return tech_class_min_size, tech_to_tech_class

    def _get_REopt_tech_max_sizes_min_turn_down(self, techs, bau=False):
        max_sizes = list()
        min_turn_down = list()
        for tech in techs:

            if eval('self.' + tech) is not None:
                existing_kw = 0
                if hasattr(eval('self.' + tech), 'existing_kw'):
                    if eval('self.' + tech + '.existing_kw') is not None:
                        existing_kw = eval('self.' + tech + '.existing_kw')

                site_kw_max = eval('self.' + tech + '.max_kw')

                if hasattr(tech, 'min_turn_down'):
                    min_turn_down.append(eval('self.' + tech + '.min_turn_down'))
                else:
                    min_turn_down.append(0)
                
                if eval('self.' + tech + '.acres_per_kw') is not None:

                    if eval('self.' + tech + '.kw_per_square_foot') is not None:

                        if self.site.roof_squarefeet is not None and self.site.land_acres is not None:
                            # don't restrict unless they specify both land_area and roof_area,
                            # otherwise one of them is "unlimited" in UI
                            roof_max_kw = self.site.roof_squarefeet * eval('self.' + tech + '.kw_per_square_foot')
                            land_max_kw = self.site.land_acres / eval('self.' + tech + '.acres_per_kw')
                            site_kw_max = max(roof_max_kw + land_max_kw, existing_kw)

                if bau and existing_kw > 0:  # existing PV in BAU scenario
                    max_sizes.append(existing_kw)
                else:
                    max_sizes.append(min(eval('self.' + tech + '.max_kw'), site_kw_max))

        return max_sizes, min_turn_down

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

        tech_class_min_size, tech_to_tech_class = self._get_REopt_tech_classes(self.available_techs)
        tech_class_min_size_bau, tech_to_tech_class_bau = self._get_REopt_tech_classes(self.bau_techs)

        prod_factor, tech_to_load, tech_is_grid, derate, eta_storage_in, eta_storage_out, om_cost_us_dollars_per_kw = \
            self._get_REopt_array_tech_load(self.available_techs)
        prod_factor_bau, tech_to_load_bau, tech_is_grid_bau, derate_bau, eta_storage_in_bau, eta_storage_out_bau, \
            om_dollars_per_kw_bau = \
            self._get_REopt_array_tech_load(self.bau_techs)
        
        max_sizes, min_turn_down = self._get_REopt_tech_max_sizes_min_turn_down(self.available_techs)
        max_sizes_bau, min_turn_down_bau = self._get_REopt_tech_max_sizes_min_turn_down(self.bau_techs, bau=True)

        levelization_factor, production_incentive_levelization_factor, pwf_e, pwf_om, two_party_factor \
            = self._get_REopt_pwfs(self.available_techs)
        levelization_factor_bau, production_incentive_levelization_factor_bau, pwf_e_bau, pwf_om_bau, two_party_factor_bau \
            = self._get_REopt_pwfs(self.bau_techs)
        
        pwf_prod_incent, prod_incent_rate, max_prod_incent, max_size_for_prod_incent \
            = self._get_REopt_production_incentives(self.available_techs)
        pwf_prod_incent_bau, prod_incent_rate_bau, max_prod_incent_bau, max_size_for_prod_incent_bau \
            = self._get_REopt_production_incentives(self.bau_techs)
        
        cap_cost_slope, cap_cost_x, cap_cost_yint, n_segments = self._get_REopt_cost_curve(self.available_techs)
        self.command_line_args.append("CapCostSegCount=" + str(n_segments))
        cap_cost_slope_bau, cap_cost_x_bau, cap_cost_yint_bau, n_segments_bau = self._get_REopt_cost_curve(self.bau_techs)
        self.command_line_args_bau.append("CapCostSegCount=" + str(n_segments_bau))

        sf = self.site.financial
        StorageCostPerKW = setup_capital_cost_incentive(self.storage.installed_cost_us_dollars_per_kw,  # use full cost as basis
                                                        self.storage.replace_cost_us_dollars_per_kw,
                                                        self.storage.inverter_replacement_year,
                                                        sf.owner_discount_pct,
                                                        sf.owner_tax_pct,
                                                        self.storage.incentives.itc_pct,
                                                        self.storage.incentives.macrs_schedule,
                                                        self.storage.incentives.macrs_bonus_pct,
                                                        self.storage.incentives.macrs_itc_reduction)
        StorageCostPerKW -= self.storage.incentives.rebate
        StorageCostPerKWH = setup_capital_cost_incentive(self.storage.installed_cost_us_dollars_per_kwh,  # there are no cash incentives for kwh
                                                         self.storage.replace_cost_us_dollars_per_kwh,
                                                         self.storage.battery_replacement_year,
                                                         sf.owner_discount_pct,
                                                         sf.owner_tax_pct,
                                                         self.storage.incentives.itc_pct,
                                                         self.storage.incentives.macrs_schedule,
                                                         self.storage.incentives.macrs_bonus_pct,
                                                         self.storage.incentives.macrs_itc_reduction)

        # DAT1 = constant.dat, contains parameters that others depend on for initialization
        write_to_dat(self.file_constant, reopt_techs, 'Tech')
        write_to_dat(self.file_constant, tech_is_grid, 'TechIsGrid', mode='a')
        write_to_dat(self.file_constant, load_list, 'Load', mode='a')
        write_to_dat(self.file_constant, tech_to_load, 'TechToLoadMatrix', mode='a')
        write_to_dat(self.file_constant, self.available_tech_classes, 'TechClass', mode='a')
        write_to_dat(self.file_constant, self.NMILRegime, 'NMILRegime', mode='a')
        write_to_dat(self.file_constant, derate, 'TurbineDerate', mode='a')
        write_to_dat(self.file_constant, tech_to_tech_class, 'TechToTechClassMatrix', mode='a')

        write_to_dat(self.file_constant_bau, reopt_techs_bau, 'Tech')
        write_to_dat(self.file_constant_bau, tech_is_grid_bau, 'TechIsGrid', mode='a')
        write_to_dat(self.file_constant_bau, load_list, 'Load', mode='a')
        write_to_dat(self.file_constant_bau, tech_to_load_bau, 'TechToLoadMatrix', mode='a')
        write_to_dat(self.file_constant_bau, self.available_tech_classes, 'TechClass', mode='a')
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
        write_to_dat(self.file_max_size, min_turn_down, 'MinTurndown', mode='a')

        write_to_dat(self.file_max_size_bau, max_sizes_bau, 'MaxSize')
        write_to_dat(self.file_max_size_bau, 0, 'MinStorageSizeKW', mode='a')
        write_to_dat(self.file_max_size_bau, 0, 'MaxStorageSizeKW', mode='a')
        write_to_dat(self.file_max_size_bau, 0, 'MinStorageSizeKWH', mode='a')
        write_to_dat(self.file_max_size_bau, 0, 'MaxStorageSizeKWH', mode='a')
        write_to_dat(self.file_max_size_bau, tech_class_min_size_bau, 'TechClassMinSize', mode='a')
        write_to_dat(self.file_max_size_bau, min_turn_down_bau, 'MinTurndown', mode='a')
        
        # economics.dat
        write_to_dat(self.file_economics, levelization_factor, 'LevelizationFactor')
        write_to_dat(self.file_economics, production_incentive_levelization_factor, 'LevelizationFactorProdIncent', mode='a')
        write_to_dat(self.file_economics, pwf_e, 'pwf_e', mode='a')
        write_to_dat(self.file_economics, pwf_om, 'pwf_om', mode='a')
        write_to_dat(self.file_economics, two_party_factor, 'two_party_factor', mode='a')
        write_to_dat(self.file_economics, pwf_prod_incent, 'pwf_prod_incent', mode='a')
        write_to_dat(self.file_economics, prod_incent_rate, 'ProdIncentRate', mode='a')
        write_to_dat(self.file_economics, max_prod_incent, 'MaxProdIncent', mode='a')
        write_to_dat(self.file_economics, max_size_for_prod_incent, 'MaxSizeForProdIncent', mode='a')
        write_to_dat(self.file_economics, cap_cost_slope, 'CapCostSlope', mode='a')
        write_to_dat(self.file_economics, cap_cost_x, 'CapCostX', mode='a')
        write_to_dat(self.file_economics, cap_cost_yint, 'CapCostYInt', mode='a')
        write_to_dat(self.file_economics, sf.owner_tax_pct, 'r_tax_owner', mode='a')
        write_to_dat(self.file_economics, sf.offtaker_tax_pct, 'r_tax_offtaker', mode='a')
        write_to_dat(self.file_economics, StorageCostPerKW, 'StorageCostPerKW', mode='a')
        write_to_dat(self.file_economics, StorageCostPerKWH, 'StorageCostPerKWH', mode='a')
        write_to_dat(self.file_economics, om_cost_us_dollars_per_kw, 'OMperUnitSize', mode='a')
        write_to_dat(self.file_economics, sf.analysis_years, 'analysis_years', mode='a')

        write_to_dat(self.file_economics_bau, levelization_factor_bau, 'LevelizationFactor')
        write_to_dat(self.file_economics_bau, production_incentive_levelization_factor_bau, 'LevelizationFactorProdIncent', mode='a')
        write_to_dat(self.file_economics_bau, pwf_e_bau, 'pwf_e', mode='a')
        write_to_dat(self.file_economics_bau, pwf_om_bau, 'pwf_om', mode='a')
        write_to_dat(self.file_economics_bau, two_party_factor_bau, 'two_party_factor', mode='a')
        write_to_dat(self.file_economics_bau, pwf_prod_incent_bau, 'pwf_prod_incent', mode='a')
        write_to_dat(self.file_economics_bau, prod_incent_rate_bau, 'ProdIncentRate', mode='a')
        write_to_dat(self.file_economics_bau, max_prod_incent_bau, 'MaxProdIncent', mode='a')
        write_to_dat(self.file_economics_bau, max_size_for_prod_incent_bau, 'MaxSizeForProdIncent', mode='a')
        write_to_dat(self.file_economics_bau, cap_cost_slope_bau, 'CapCostSlope', mode='a')
        write_to_dat(self.file_economics_bau, cap_cost_x_bau, 'CapCostX', mode='a')
        write_to_dat(self.file_economics_bau, cap_cost_yint_bau, 'CapCostYInt', mode='a')
        write_to_dat(self.file_economics_bau, sf.owner_tax_pct, 'r_tax_owner', mode='a')
        write_to_dat(self.file_economics_bau, sf.offtaker_tax_pct, 'r_tax_offtaker', mode='a')
        write_to_dat(self.file_economics_bau, StorageCostPerKW, 'StorageCostPerKW', mode='a')
        write_to_dat(self.file_economics_bau, StorageCostPerKWH, 'StorageCostPerKWH', mode='a')
        write_to_dat(self.file_economics_bau, om_dollars_per_kw_bau, 'OMperUnitSize', mode='a')
        write_to_dat(self.file_economics_bau, sf.analysis_years, 'analysis_years', mode='a')

        # elec_tariff args
        parser = UrdbParse(paths=self.paths, big_number=big_number, elec_tariff=self.elec_tariff,
                           techs=[tech for tech in self.available_techs if eval('self.' + tech) is not None],
                           bau_techs=[tech for tech in self.bau_techs if eval('self.' + tech) is not None],
                           loads=self.available_loads, gen=self.generator)

        tariff_args = parser.parse_rate(self.elec_tariff.utility_name, self.elec_tariff.rate_name)

        self.command_line_args.append('NumRatchets=' + str(tariff_args.demand_num_ratchets))
        self.command_line_args.append('FuelBinCount=' + str(tariff_args.energy_tiers_num))
        self.command_line_args.append('DemandBinCount=' + str(tariff_args.demand_tiers_num))
        self.command_line_args.append('DemandMonthsBinCount=' + str(tariff_args.demand_month_tiers_num))

        self.command_line_args_bau.append('NumRatchets=' + str(tariff_args.demand_num_ratchets))
        self.command_line_args_bau.append('FuelBinCount=' + str(tariff_args.energy_tiers_num))
        self.command_line_args_bau.append('DemandBinCount=' + str(tariff_args.demand_tiers_num))
        self.command_line_args_bau.append('DemandMonthsBinCount=' + str(tariff_args.demand_month_tiers_num))

        ta = tariff_args
        write_to_dat(self.file_demand_rates_monthly, ta.demand_rates_monthly, 'DemandRatesMonth')
        write_to_dat(self.file_demand_rates, ta.demand_rates_tou, 'DemandRates')
        # write_to_dat(self.file_demand_rates, ta.demand_min, 'MinDemand', 'a')  # not used in REopt
        write_to_dat(self.file_demand_periods, ta.demand_ratchets_tou, 'TimeStepRatchets')
        write_to_dat(self.file_demand_num_ratchets, ta.demand_num_ratchets, 'NumRatchets')
        write_to_dat(self.file_max_in_tiers, ta.demand_max_in_tiers, 'MaxDemandInTier')
        write_to_dat(self.file_max_in_tiers, ta.energy_max_in_tiers, 'MaxUsageInTier', 'a')
        write_to_dat(self.file_max_in_tiers, ta.demand_month_max_in_tiers, 'MaxDemandMonthsInTier', 'a')
        write_to_dat(self.file_energy_rates, ta.energy_rates, 'FuelRate')
        write_to_dat(self.file_energy_rates, ta.energy_avail, 'FuelAvail', 'a')
        write_to_dat(self.file_energy_rates, ta.fixed_monthly_charge, 'FixedMonthlyCharge', 'a')
        write_to_dat(self.file_energy_rates, ta.annual_min_charge, 'AnnualMinCharge', 'a')
        write_to_dat(self.file_energy_rates, ta.min_monthly_charge, 'MonthlyMinCharge', 'a')
        write_to_dat(self.file_energy_rates_bau, ta.energy_rates_bau, 'FuelRate')
        write_to_dat(self.file_energy_rates_bau, ta.energy_avail_bau, 'FuelAvail', 'a')
        write_to_dat(self.file_energy_rates_bau, ta.fixed_monthly_charge, 'FixedMonthlyCharge', 'a')
        write_to_dat(self.file_energy_rates_bau, ta.annual_min_charge, 'AnnualMinCharge', 'a')
        write_to_dat(self.file_energy_rates_bau, ta.min_monthly_charge, 'MonthlyMinCharge', 'a')
        write_to_dat(self.file_export_rates, ta.export_rates, 'ExportRates')
        write_to_dat(self.file_export_rates_bau, ta.export_rates_bau, 'ExportRates')
        write_to_dat(self.file_demand_lookback, ta.demand_lookback_months, 'DemandLookbackMonths')
        write_to_dat(self.file_demand_lookback, ta.demand_lookback_percent, 'DemandLookbackPercent', 'a')
        write_to_dat(self.file_demand_ratchets_monthly, ta.demand_ratchets_monthly, 'TimeStepRatchetsMonth')
        write_to_dat(self.file_energy_tiers_num, ta.energy_tiers_num, 'FuelBinCount')
        write_to_dat(self.file_energy_tiers_num, ta.demand_tiers_num, 'DemandBinCount', 'a')
        write_to_dat(self.file_energy_burn_rate, ta.energy_burn_rate, 'FuelBurnRateM')
        write_to_dat(self.file_energy_burn_rate_bau, ta.energy_burn_rate_bau, 'FuelBurnRateM')
        write_to_dat(self.file_energy_burn_rate, ta.energy_burn_intercept, 'FuelBurnRateB', 'a')
        write_to_dat(self.file_energy_burn_rate_bau, ta.energy_burn_intercept_bau, 'FuelBurnRateB', 'a')

        # time_steps_per_hour
        self.command_line_args.append('TimeStepCount=' + str(self.n_timesteps))
        self.command_line_args.append('TimeStepScaling=' + str(8760.0/self.n_timesteps))

        self.command_line_args_bau.append('TimeStepCount=' + str(self.n_timesteps))
        self.command_line_args_bau.append('TimeStepScaling=' + str(8760.0/self.n_timesteps))