# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
import copy
import numpy as np
import logging
from reo.models import AbsorptionChillerModel
from reo.nested_inputs import macrs_five_year, macrs_seven_year
log = logging.getLogger(__name__)


def calculate_proforma_metrics(data):
    """
    Recreates the ProForma spreadsheet calculations to get the simple payback period, irr, net present cost (3rd
    party case), and payment to third party (3rd party case)
    :param data: dict a complete response from the REopt API for a successfully completed job
    :return: float, the simple payback of the system, if the system recuperates its costs
    """
    # Sort out the inputs and outputs by model so that all needed data is in consolidated locations
    time_steps_per_hour = data['inputs']['Scenario']['time_steps_per_hour']
    electric_tariff = copy.deepcopy(data['outputs']['Scenario']['Site']['ElectricTariff'])
    electric_tariff.update(data['inputs']['Scenario']['Site']['ElectricTariff'])
    financials = copy.deepcopy(data['outputs']['Scenario']['Site']['Financial'])
    financials.update(data['inputs']['Scenario']['Site']['Financial'])
    pvs = copy.deepcopy(data['outputs']['Scenario']['Site']['PV'])
    if type(pvs) == dict:
        pvs = [pvs]
    in_pvs = copy.deepcopy(data['inputs']['Scenario']['Site']['PV'])
    if type(data['inputs']['Scenario']['Site']['PV']) == dict:
        in_pvs = [in_pvs]
    for i, pv in enumerate(in_pvs):
        pvs[i].update(pv)
    wind = copy.deepcopy(data['outputs']['Scenario']['Site']['Wind'])
    wind.update(data['inputs']['Scenario']['Site']['Wind'])
    storage = copy.deepcopy(data['outputs']['Scenario']['Site']['Storage'])
    storage.update(data['inputs']['Scenario']['Site']['Storage'])
    generator = copy.deepcopy(data['outputs']['Scenario']['Site']['Generator'])
    generator.update(data['inputs']['Scenario']['Site']['Generator'])
    years = financials['analysis_years']
    third_party = financials['third_party_ownership']

    chp = copy.deepcopy(data['outputs']['Scenario']['Site']['CHP'])
    chp.update(data['inputs']['Scenario']['Site']['CHP'])
    absorption_chiller = copy.deepcopy(data['outputs']['Scenario']['Site']['AbsorptionChiller'])
    absorp_chl = AbsorptionChillerModel.objects.filter(run_uuid=data['outputs']['Scenario']['run_uuid'])[0]
    absorption_chiller.update(data['inputs']['Scenario']['Site']['AbsorptionChiller'])
    # Need to update two cost input attributes which are calculated in techs.py and updated in scenario.py
    absorption_chiller.update({"installed_cost_us_dollars_per_ton": absorp_chl.installed_cost_us_dollars_per_ton,
                               "om_cost_us_dollars_per_ton": absorp_chl.om_cost_us_dollars_per_ton})
    hot_tes = copy.deepcopy(data['outputs']['Scenario']['Site']['HotTES'])
    hot_tes.update(data['inputs']['Scenario']['Site']['HotTES'])
    cold_tes = copy.deepcopy(data['outputs']['Scenario']['Site']['ColdTES'])
    cold_tes.update(data['inputs']['Scenario']['Site']['ColdTES'])
    fuel_tariff = copy.deepcopy(data['outputs']['Scenario']['Site']['FuelTariff'])
    fuel_tariff.update(data['inputs']['Scenario']['Site']['FuelTariff'])
    ghp = copy.deepcopy(data['outputs']['Scenario']['Site']['GHP'])
    ghp.update(data['inputs']['Scenario']['Site']['GHP'])
    steam_turbine = copy.deepcopy(data['outputs']['Scenario']['Site']['SteamTurbine'])
    steam_turbine.update(data['inputs']['Scenario']['Site']['SteamTurbine'])

    # Create placeholder variables to store summed totals across all relevant techs
    federal_itc = 0
    om_series = np.array([0.0 for _ in range(years)])
    om_series_bau = np.array([0.0 for _ in range(years)])
    total_pbi = np.array([0.0 for _ in range(years)])
    total_pbi_bau = np.array([0.0 for _ in range(years)])
    total_depreciation = np.array([0.0 for _ in range(years)])
    total_ibi_and_cbi = 0

    # calculate PV capital costs, o+m costs, incentives, and depreciation
    for pv in pvs:
        new_kw = (pv.get('size_kw') or 0) - (pv.get('existing_kw') or 0)
        total_kw = pv.get('size_kw') or 0
        existing_kw = pv.get('existing_kw') or 0
        # existing PV is considered free
        capital_costs = new_kw * pv['installed_cost_us_dollars_per_kw']
        # assume owner is responsible for both new and existing PV maintenance in optimal case
        if third_party:
            annual_om = -1 * new_kw * pv['om_cost_us_dollars_per_kw']
        else:
            annual_om = -1 * total_kw * pv['om_cost_us_dollars_per_kw']
        annual_om_bau = -1 * existing_kw * pv['om_cost_us_dollars_per_kw']
        om_series += np.array \
            ([annual_om * ( 1 +financials['om_cost_escalation_pct'] )**yr for yr in range(1, years +1)])
        om_series_bau += np.array \
            ([annual_om_bau * ( 1 +financials['om_cost_escalation_pct'] )**yr for yr in range(1, years+1)])
        # incentive calculations, in the spreadsheet utility incentives are applied first
        utility_ibi = min(capital_costs * pv['utility_ibi_pct'], pv['utility_ibi_max_us_dollars'])
        utility_cbi = min(new_kw * pv['utility_rebate_us_dollars_per_kw'], pv['utility_rebate_max_us_dollars'])
        state_ibi = min((capital_costs - utility_ibi - utility_cbi) * pv['state_ibi_pct'], pv['state_ibi_max_us_dollars'])
        state_cbi = min(new_kw * pv['state_rebate_us_dollars_per_kw'], pv['state_rebate_max_us_dollars'])
        federal_cbi = new_kw * pv['federal_rebate_us_dollars_per_kw']
        ibi = utility_ibi + state_ibi
        cbi = utility_cbi + federal_cbi + state_cbi
        total_ibi_and_cbi += (ibi + cbi)
        pbi_series = np.array([])
        pbi_series_bau = np.array([])
        existing_energy_bau = (pv.get('year_one_energy_produced_bau_kwh') or 0) if third_party else 0
        # Production-based incentives
        for yr in range(years):
            if yr < pv['pbi_years']:
                degredation_pct = ( 1- (pv['degradation_pct']) )**yr
                base_pbi = min \
                    (pv['pbi_us_dollars_per_kwh'] * ((pv['year_one_energy_produced_kwh'] or 0) - existing_energy_bau) * \
                               degredation_pct,  pv['pbi_max_us_dollars'] * degredation_pct )
                base_pbi_bau = min(pv['pbi_us_dollars_per_kwh'] * (pv.get('year_one_energy_produced_bau_kwh') or 0) * \
                                   degredation_pct,  pv['pbi_max_us_dollars'] * degredation_pct )
                pbi_series = np.append(pbi_series, base_pbi)
                pbi_series_bau = np.append(pbi_series_bau, base_pbi_bau)
            else:
                pbi_series = np.append(pbi_series, 0.0)
                pbi_series_bau = np.append(pbi_series_bau, 0.0)
        total_pbi += pbi_series
        total_pbi_bau += pbi_series_bau
        # Depreciation
        if pv['macrs_option_years'] in [5 ,7]:
            if pv['macrs_option_years'] == 5:
                schedule = macrs_five_year
            elif pv['macrs_option_years'] == 7:
                schedule = macrs_seven_year
            else:
                schedule = []
            federal_itc_basis = capital_costs - state_ibi - utility_ibi - state_cbi - utility_cbi - federal_cbi
            federal_itc_amount = pv['federal_itc_pct'] * federal_itc_basis
            federal_itc += federal_itc_amount
            macrs_bonus_basis = federal_itc_basis - \
                        (federal_itc_basis * pv['federal_itc_pct'] * pv['macrs_itc_reduction'])
            macrs_basis = macrs_bonus_basis * (1 - pv['macrs_bonus_pct'])
            depreciation_schedule = np.array([0.0 for _ in range(years)])
            for i, r in enumerate(schedule):
                if i < len(depreciation_schedule):
                    depreciation_schedule[i] = macrs_basis * r
            depreciation_schedule[0] += (pv['macrs_bonus_pct'] * macrs_bonus_basis)
            total_depreciation += depreciation_schedule

    # calculate Wind capital costs, o+m costs, incentives, and depreciation
    if (wind['size_kw'] or 0) > 0:
        total_kw = wind.get('size_kw') or 0
        capital_costs = total_kw * wind['installed_cost_us_dollars_per_kw']
        annual_om = -1 * total_kw * wind['om_cost_us_dollars_per_kw']
        om_series += np.array(
            [annual_om * (1 + financials['om_cost_escalation_pct']) ** yr for yr in range(1, years + 1)])
        utility_ibi = min(capital_costs * wind['utility_ibi_pct'], wind['utility_ibi_max_us_dollars'])
        utility_cbi = min(total_kw * wind['utility_rebate_us_dollars_per_kw'], wind['utility_rebate_max_us_dollars'])
        state_ibi = min((capital_costs - utility_ibi - utility_cbi) * wind['state_ibi_pct'],
                        wind['state_ibi_max_us_dollars'])
        state_cbi = min(total_kw * wind['state_rebate_us_dollars_per_kw'], wind['state_rebate_max_us_dollars'])
        federal_cbi = total_kw * wind['federal_rebate_us_dollars_per_kw']
        ibi = utility_ibi + state_ibi
        cbi = utility_cbi + federal_cbi + state_cbi
        total_ibi_and_cbi += (ibi + cbi)
        # Production-based incentives
        pbi_series = np.array([])
        for yr in range(years):
            if yr < wind['pbi_years']:
                base_pbi = min(wind['pbi_us_dollars_per_kwh'] * (wind['year_one_energy_produced_kwh'] or 0),
                               wind['pbi_max_us_dollars'])
                pbi_series = np.append(pbi_series, base_pbi)
            else:
                pbi_series = np.append(pbi_series, 0.0)
        total_pbi += pbi_series
        # Depreciation
        if wind['macrs_option_years'] in [5, 7]:
            if wind['macrs_option_years'] == 5:
                schedule = macrs_five_year
            elif wind['macrs_option_years'] == 7:
                schedule = macrs_seven_year
            else:
                schedule = []
            federal_itc_basis = capital_costs - state_ibi - utility_ibi - state_cbi - utility_cbi - federal_cbi
            federal_itc_amount = wind['federal_itc_pct'] * federal_itc_basis
            federal_itc += federal_itc_amount
            macrs_bonus_basis = federal_itc_basis - (
                        federal_itc_basis * wind['federal_itc_pct'] * wind['macrs_itc_reduction'])
            macrs_basis = macrs_bonus_basis * (1 - wind['macrs_bonus_pct'])
            depreciation_schedule = np.array([0.0 for _ in range(years)])
            for i, r in enumerate(schedule):
                if i < len(depreciation_schedule):
                    depreciation_schedule[i] = macrs_basis * r
            depreciation_schedule[0] += (wind['macrs_bonus_pct'] * macrs_bonus_basis)
            total_depreciation += depreciation_schedule

    # calculate Storage capital costs, o+m costs, incentives, and depreciation
    if (storage['size_kw'] or 0) > 0:
        total_kw = storage.get('size_kw') or 0
        total_kwh = storage.get('size_kwh') or 0
        capital_costs = (total_kw * storage['installed_cost_us_dollars_per_kw']) + (
                    total_kwh * storage['installed_cost_us_dollars_per_kwh'])
        battery_replacement_year = int(storage['battery_replacement_year'])
        battery_replacement_cost = -1 * ((total_kw * storage['replace_cost_us_dollars_per_kw']) + (
                    total_kwh * storage['replace_cost_us_dollars_per_kwh']))
        om_series += np.array(
            [0 if yr != battery_replacement_year else battery_replacement_cost for yr in range(1, years + 1)])

        # storage only has cbi in the API
        cbi = (total_kw * storage['total_rebate_us_dollars_per_kw']) + (
                    total_kwh * (storage.get('total_rebate_us_dollars_per_kw') or 0))
        total_ibi_and_cbi += (cbi)
        # Depreciation
        if storage['macrs_option_years'] in [5, 7]:
            if storage['macrs_option_years'] == 5:
                schedule = macrs_five_year
            elif storage['macrs_option_years'] == 7:
                schedule = macrs_seven_year
            else:
                schedule = []
            federal_itc_basis = capital_costs - cbi
            federal_itc_amount = storage['total_itc_pct'] * federal_itc_basis
            federal_itc += federal_itc_amount
            macrs_bonus_basis = federal_itc_basis - (
                        federal_itc_basis * storage['total_itc_pct'] * storage['macrs_itc_reduction'])
            macrs_basis = macrs_bonus_basis * (1 - storage['macrs_bonus_pct'])
            depreciation_schedule = np.array([0.0 for _ in range(years)])
            for i, r in enumerate(schedule):
                if i < len(depreciation_schedule):
                    depreciation_schedule[i] = macrs_basis * r
            depreciation_schedule[0] += (storage['macrs_bonus_pct'] * macrs_bonus_basis)
            total_depreciation += depreciation_schedule

    # calculate Generator capital costs, o+m costs, incentives, and depreciation
    if (generator['size_kw'] or 0) > 0:
        total_kw = generator.get('size_kw') or 0
        new_kw = (generator.get('size_kw') or 0) - (generator.get('existing_kw') or 0)
        existing_kw = generator.get('existing_kw') or 0

        # In the two party case the developer does not include the fuel cost in their costs
        # It is assumed that the offtaker will pay for this at a rate that is not marked up
        # to cover developer profits
        if not third_party:
            annual_om = -1 * ((total_kw * generator['om_cost_us_dollars_per_kw']) +
                              (generator['year_one_variable_om_cost_us_dollars']) +
                              (generator['year_one_fuel_cost_us_dollars']))

            annual_om_bau = -1 * ((existing_kw * generator['om_cost_us_dollars_per_kw']) +
                                  (generator['existing_gen_year_one_variable_om_cost_us_dollars']) +
                                  (generator['existing_gen_year_one_fuel_cost_us_dollars']))
        else:
            annual_om = -1 * ((total_kw * generator['om_cost_us_dollars_per_kw']) +
                              (generator['year_one_variable_om_cost_us_dollars']))

            annual_om_bau = -1 * ((existing_kw * generator['om_cost_us_dollars_per_kw']) +
                                  (generator['existing_gen_year_one_variable_om_cost_us_dollars']))

        om_series += np.array(
            [annual_om * (1 + financials['om_cost_escalation_pct']) ** yr for yr in range(1, years + 1)])
        om_series_bau += np.array(
            [annual_om_bau * (1 + financials['om_cost_escalation_pct']) ** yr for yr in range(1, years + 1)])

    # calculate CHP capital costs, o+m costs, incentives, and depreciation
    if (chp['size_kw'] or 0) > 0:
        total_kw = chp.get('size_kw') or 0
        total_supp_fire_kw = chp.get('size_supplementary_firing_kw') or 0
        total_kwh = chp.get('year_one_electric_energy_produced_kwh') or 0
        total_runtime = sum(np.array(chp.get('year_one_electric_production_series_kw') or []) > 0) / float(
            time_steps_per_hour)
        # Calculate capital cost from cost curve list
        cost_list = chp.get("installed_cost_us_dollars_per_kw") or []
        size_list = chp.get("tech_size_for_cost_curve") or []
        chp_size = total_kw
        if len(cost_list) > 1:
            if chp_size <= size_list[0]:
                capital_costs = chp_size * cost_list[0]  # Currently not handling non-zero cost ($) for 0 kW size input
            elif chp_size > size_list[-1]:
                capital_costs = chp_size * cost_list[-1]
            else:
                capital_costs = 0
                for s in range(1, len(size_list)):
                    if (chp_size > size_list[s - 1]) and (chp_size <= size_list[s]):
                        slope = (cost_list[s] * size_list[s] - cost_list[s - 1] * size_list[s - 1]) / \
                                (size_list[s] - size_list[s - 1])
                        capital_costs += cost_list[s - 1] * size_list[s - 1] + (chp_size - size_list[s - 1]) * slope
        else:
            capital_costs = (cost_list[0] or 0) * (chp_size or 0)
        capital_costs += total_supp_fire_kw * chp.get('supplementary_firing_capital_cost_per_kw')
        annual_om = (-1 * total_kw * chp['om_cost_us_dollars_per_kw']) + \
                    (-1 * total_kwh * chp['om_cost_us_dollars_per_kwh']) + \
                    (-1 * total_runtime * total_kw * chp['om_cost_us_dollars_per_hr_per_kw_rated'])
        om_series += np.array(
            [annual_om * (1 + financials['om_cost_escalation_pct']) ** yr for yr in range(1, years + 1)])
        if not third_party:
            om_series += np.array([-1 * (fuel_tariff.get("year_one_chp_fuel_cost_us_dollars") or 0) * (
                        1 + financials['chp_fuel_escalation_pct']) ** yr for yr in range(1, years + 1)])
            om_series += np.array([-1 * (fuel_tariff.get("year_one_boiler_fuel_cost_us_dollars") or 0) * (
                        1 + financials['boiler_fuel_escalation_pct']) ** yr for yr in range(1, years + 1)])
            om_series_bau += np.array([-1 * (fuel_tariff.get("year_one_boiler_fuel_cost_bau_us_dollars") or 0) * (
                        1 + financials['boiler_fuel_escalation_pct']) ** yr for yr in range(1, years + 1)])
        utility_ibi = min(capital_costs * chp['utility_ibi_pct'], chp['utility_ibi_max_us_dollars'])
        utility_cbi = min(total_kw * chp['utility_rebate_us_dollars_per_kw'], chp['utility_rebate_max_us_dollars'])
        state_ibi = min((capital_costs - utility_ibi - utility_cbi) * chp['state_ibi_pct'],
                        chp['state_ibi_max_us_dollars'])
        state_cbi = min(total_kw * chp['state_rebate_us_dollars_per_kw'], chp['state_rebate_max_us_dollars'])
        federal_cbi = total_kw * chp['federal_rebate_us_dollars_per_kw']
        ibi = utility_ibi + state_ibi
        cbi = utility_cbi + federal_cbi + state_cbi
        total_ibi_and_cbi += (ibi + cbi)
        # Production-based incentives
        pbi_series = np.array([])
        for yr in range(years):
            if yr < chp['pbi_years']:
                base_pbi = min(chp['pbi_us_dollars_per_kwh'] * (total_kwh or 0), \
                               chp['pbi_max_us_dollars'])
                pbi_series = np.append(pbi_series, base_pbi)
            else:
                pbi_series = np.append(pbi_series, 0.0)
        total_pbi += pbi_series
        # Depreciation
        if chp['macrs_option_years'] in [5, 7]:
            if chp['macrs_option_years'] == 5:
                schedule = macrs_five_year
            elif chp['macrs_option_years'] == 7:
                schedule = macrs_seven_year
            else:
                schedule = []
            federal_itc_basis = capital_costs - state_ibi - utility_ibi - state_cbi - utility_cbi - federal_cbi
            federal_itc_amount = chp['federal_itc_pct'] * federal_itc_basis
            federal_itc += federal_itc_amount
            macrs_bonus_basis = federal_itc_basis - (
                        federal_itc_basis * chp['federal_itc_pct'] * chp['macrs_itc_reduction'])
            macrs_basis = macrs_bonus_basis * (1 - chp['macrs_bonus_pct'])
            depreciation_schedule = np.array([0.0 for _ in range(years)])
            for i, r in enumerate(schedule):
                depreciation_schedule[i] = macrs_basis * r
            depreciation_schedule[0] += (chp['macrs_bonus_pct'] * macrs_bonus_basis)
            total_depreciation += depreciation_schedule

    # calculate Absorption Chiller capital costs, o+m costs, incentives, and depreciation
    if (absorption_chiller['size_ton'] or 0) > 0:
        total_kw = absorption_chiller.get('size_ton') or 0
        capital_costs = total_kw * absorption_chiller['installed_cost_us_dollars_per_ton']
        annual_om = -1 * total_kw * absorption_chiller['om_cost_us_dollars_per_ton']
        om_series += np.array(
            [annual_om * (1 + financials['om_cost_escalation_pct']) ** yr for yr in range(1, years + 1)])

        # Absorption Chiller does not have complex incentives, only MACRS
        ibi = 0
        cbi = 0
        total_ibi_and_cbi = 0

        # Depreciation
        if absorption_chiller['macrs_option_years'] in [5, 7]:
            if absorption_chiller['macrs_option_years'] == 5:
                schedule = macrs_five_year
            elif absorption_chiller['macrs_option_years'] == 7:
                schedule = macrs_seven_year
            else:
                schedule = []
            macrs_bonus_basis = capital_costs
            macrs_basis = macrs_bonus_basis * (1 - absorption_chiller['macrs_bonus_pct'])
            depreciation_schedule = np.array([0.0 for _ in range(years)])
            for i, r in enumerate(schedule):
                depreciation_schedule[i] = macrs_basis * r
            depreciation_schedule[0] += (absorption_chiller['macrs_bonus_pct'] * macrs_bonus_basis)
            total_depreciation += depreciation_schedule

    # calculate Hot TES capital costs, o+m costs, incentives, and depreciation
    if (hot_tes['size_gal'] or 0) > 0:
        total_gal = hot_tes.get('size_gal')
        capital_costs = total_gal * hot_tes['installed_cost_us_dollars_per_gal']
        annual_om = -1 * total_gal * hot_tes['om_cost_us_dollars_per_gal']
        om_series += np.array(
            [annual_om * (1 + financials['om_cost_escalation_pct']) ** yr for yr in range(1, years + 1)])
        # Depreciation
        if hot_tes['macrs_option_years'] in [5, 7]:
            if hot_tes['macrs_option_years'] == 5:
                schedule = macrs_five_year
            elif hot_tes['macrs_option_years'] == 7:
                schedule = macrs_seven_year
            else:
                schedule = []
            macrs_bonus_basis = capital_costs
            macrs_basis = macrs_bonus_basis * (1 - hot_tes['macrs_bonus_pct'])
            depreciation_schedule = np.array([0.0 for _ in range(years)])
            for i, r in enumerate(schedule):
                depreciation_schedule[i] = macrs_basis * r
            depreciation_schedule[0] += (hot_tes['macrs_bonus_pct'] * macrs_bonus_basis)
            total_depreciation += depreciation_schedule

    # calculate Cold TES capital costs, o+m costs, incentives, and depreciation
    if (cold_tes['size_gal'] or 0) > 0:
        total_gal = cold_tes.get('size_gal')
        capital_costs = total_gal * cold_tes['installed_cost_us_dollars_per_gal']
        annual_om = -1 * total_gal * cold_tes['om_cost_us_dollars_per_gal']
        om_series += np.array(
            [annual_om * (1 + financials['om_cost_escalation_pct']) ** yr for yr in range(1, years + 1)])
        # Depreciation
        if cold_tes['macrs_option_years'] in [5, 7]:
            if cold_tes['macrs_option_years'] == 5:
                schedule = macrs_five_year
            elif cold_tes['macrs_option_years'] == 7:
                schedule = macrs_seven_year
            else:
                schedule = []
            macrs_bonus_basis = capital_costs
            macrs_basis = macrs_bonus_basis * (1 - cold_tes['macrs_bonus_pct'])
            depreciation_schedule = np.array([0.0 for _ in range(years)])
            for i, r in enumerate(schedule):
                depreciation_schedule[i] = macrs_basis * r
            depreciation_schedule[0] += (cold_tes['macrs_bonus_pct'] * macrs_bonus_basis)
            total_depreciation += depreciation_schedule

    # calculate GHP capital costs, o+m costs, incentives, and depreciation
    if (ghp['size_heat_pump_ton'] or 0) > 0:
        total_ton = ghp.get('size_heat_pump_ton') or 0
        total_ghx_feet = ghp["ghpghx_chosen_outputs"].get("length_boreholes_ft") or 0
        building_sqft = ghp["building_sqft"]
        capital_costs = total_ton * ghp['installed_cost_heatpump_us_dollars_per_ton'] + \
                        total_ghx_feet * ghp["installed_cost_ghx_us_dollars_per_ft"] + \
                        building_sqft * ghp["installed_cost_building_hydronic_loop_us_dollars_per_sqft"]
        annual_om = -1 * building_sqft * ghp['om_cost_us_dollars_per_sqft_year']
        om_series += np.array(
            [annual_om * (1 + financials['om_cost_escalation_pct']) ** yr for yr in range(1, years + 1)])
        utility_ibi = min(capital_costs * ghp['utility_ibi_pct'], ghp['utility_ibi_max_us_dollars'])
        utility_cbi = min(total_ton * ghp['utility_rebate_us_dollars_per_ton'], ghp['utility_rebate_max_us_dollars'])
        state_ibi = min((capital_costs - utility_ibi - utility_cbi) * ghp['state_ibi_pct'], ghp['state_ibi_max_us_dollars'])
        state_cbi = min(total_ton * ghp['state_rebate_us_dollars_per_ton'], ghp['state_rebate_max_us_dollars'])
        federal_cbi = total_ton * ghp['federal_rebate_us_dollars_per_ton']
        ibi = utility_ibi + state_ibi
        cbi = utility_cbi + federal_cbi + state_cbi
        total_ibi_and_cbi += (ibi + cbi)

        # Depreciation
        if ghp['macrs_option_years'] in [5, 7]:
            if ghp['macrs_option_years'] == 5:
                schedule = macrs_five_year
            elif ghp['macrs_option_years'] == 7:
                schedule = macrs_seven_year
            else:
                schedule = []
            federal_itc_basis = capital_costs - state_ibi - utility_ibi - state_cbi - utility_cbi - federal_cbi
            federal_itc_amount = ghp['federal_itc_pct'] * federal_itc_basis
            federal_itc += federal_itc_amount

            macrs_bonus_basis = federal_itc_basis - (federal_itc_basis * ghp['federal_itc_pct'] * ghp['macrs_itc_reduction'])
            macrs_bonus_basis = capital_costs

            macrs_basis = macrs_bonus_basis * (1 - ghp['macrs_bonus_pct'])
            depreciation_schedule = np.array([0.0 for _ in range(years)])
            for i, r in enumerate(schedule):
                depreciation_schedule[i] = macrs_basis * r
            depreciation_schedule[0] += (ghp['macrs_bonus_pct'] * macrs_bonus_basis)
            total_depreciation += depreciation_schedule

    # calculate SteamTurbine capital costs, o+m costs, incentives, and depreciation
    if (steam_turbine['size_kw'] or 0) > 0:
        total_kw = steam_turbine.get('size_kw') or 0
        total_kwh = steam_turbine.get('year_one_electric_energy_produced_kwh') or 0
        capital_costs = total_kw * steam_turbine['installed_cost_us_dollars_per_kw']
        annual_om = -1 * total_kw * steam_turbine['om_cost_us_dollars_per_kw'] + \
                    -1 * total_kwh * steam_turbine['om_cost_us_dollars_per_kwh']
        om_series += np.array(
            [annual_om * (1 + financials['om_cost_escalation_pct']) ** yr for yr in range(1, years + 1)])
        if not third_party:
            om_series += np.array([-1 * (fuel_tariff.get("year_one_boiler_fuel_cost_us_dollars") or 0) * (
                        1 + financials['boiler_fuel_escalation_pct']) ** yr for yr in range(1, years + 1)])
            om_series_bau += np.array([-1 * (fuel_tariff.get("year_one_boiler_fuel_cost_bau_us_dollars") or 0) * (
                        1 + financials['boiler_fuel_escalation_pct']) ** yr for yr in range(1, years + 1)])
        # Steam turbine does not have complex incentives, just MACRS
        ibi = 0
        cbi = 0
        total_ibi_and_cbi = 0

        # Depreciation
        if steam_turbine['macrs_option_years'] in [5, 7]:
            if steam_turbine['macrs_option_years'] == 5:
                schedule = macrs_five_year
            elif steam_turbine['macrs_option_years'] == 7:
                schedule = macrs_seven_year
            else:
                schedule = []
            macrs_bonus_basis = capital_costs
            depreciation_schedule = np.array([0.0 for _ in range(years)])
            for i, r in enumerate(schedule):
                depreciation_schedule[i] = macrs_basis * r
            depreciation_schedule[0] += (steam_turbine['macrs_bonus_pct'] * macrs_bonus_basis)
            total_depreciation += depreciation_schedule

    # Optimal Case calculations
    electricity_bill_series = np.array([-1 * electric_tariff['year_one_bill_us_dollars'] * \
                                        (1 + financials['escalation_pct']) ** yr for yr in range(1, years + 1)])
    export_credit_series = np.array([-1 * electric_tariff['year_one_export_benefit_us_dollars'] * \
                                     (1 + financials['escalation_pct']) ** yr for yr in range(1, years + 1)])

    # In the two party case the electricity and export credits are incurred by the offtaker not the developer
    if third_party:
        total_operating_expenses = om_series
    else:
        total_operating_expenses = electricity_bill_series + export_credit_series + om_series

    # Set tax rate based off ownership type
    if third_party:
        tax_pct = financials['owner_tax_pct']
    else:
        tax_pct = financials['offtaker_tax_pct']

    # Apply taxes to operating expenses
    if tax_pct > 0:
        deductable_operating_expenses_series = copy.deepcopy(total_operating_expenses)
    else:
        deductable_operating_expenses_series = np.array([0] * years)

    operating_expenses_after_tax = (total_operating_expenses - deductable_operating_expenses_series) + (
                deductable_operating_expenses_series * (1 - tax_pct))
    total_cash_incentives = total_pbi * (1 - tax_pct)
    total_depreciation = total_depreciation * tax_pct
    free_cashflow = total_depreciation + total_cash_incentives + operating_expenses_after_tax
    free_cashflow[0] += federal_itc
    free_cashflow = np.append([(-1 * financials['initial_capital_costs']) + total_ibi_and_cbi], free_cashflow)
    # At this point the logic branches based on third-party ownership or not - see comments
    net_present_cost = None
    annualized_payment_to_third_party_us_dollars = None
    developer_free_cashflow = None
    # get cumulative cashflow for developer
    if third_party:
        developer_free_cashflow = copy.deepcopy(free_cashflow)
        discounted_developer_cashflow = [v / ((1 + financials['owner_discount_pct']) ** yr) for yr, v in
                                         enumerate(developer_free_cashflow)]
        net_present_cost = sum(discounted_developer_cashflow) * -1
        if financials['owner_discount_pct'] != 0:
            capital_recovery_factor = (financials['owner_discount_pct'] * (
                        1 + financials['owner_discount_pct']) ** years) / \
                                      ((1 + financials['owner_discount_pct']) ** years - 1) / (1 - tax_pct)
        else:
            capital_recovery_factor = (1 / years) / (1 - tax_pct)
        annualized_payment_to_third_party_us_dollars = net_present_cost * capital_recovery_factor
        annual_income_from_host = -1 * sum(discounted_developer_cashflow) * capital_recovery_factor * (1 - tax_pct)
        developer_free_cashflow[1:] += annual_income_from_host
        irr = np.irr(developer_free_cashflow)
        cumulative_cashflow = np.cumsum(developer_free_cashflow)
        net_free_cashflow = developer_free_cashflow
        developer_free_cashflow = [round(i, 2) for i in developer_free_cashflow]
        electricity_bill_bau_series_bau = np.array([-1 * electric_tariff['year_one_bill_bau_us_dollars'] * \
                                                    (1 + financials['escalation_pct']) ** yr for yr in
                                                    range(1, years + 1)])
        export_credit_bau_series_bau = np.array([electric_tariff['total_export_benefit_bau_us_dollars'] * \
                                                 (1 + financials['escalation_pct']) ** yr for yr in
                                                 range(1, years + 1)])
        electricity_bill_series = np.array([-1 * electric_tariff['year_one_bill_us_dollars'] * \
                                            (1 + financials['escalation_pct']) ** yr for yr in range(1, years + 1)])
        export_credit_series = np.array([electric_tariff['total_export_benefit_us_dollars'] * \
                                         (1 + financials['escalation_pct']) ** yr for yr in range(1, years + 1)])
        annual_income_from_host_series = [-1 * annualized_payment_to_third_party_us_dollars for _ in range(years)]
        existing_genertor_fuel_cost_series = np.array([-1 * generator['existing_gen_year_one_fuel_cost_us_dollars'] * \
                                                       (1 + financials['om_cost_escalation_pct']) ** yr for yr in
                                                       range(1, years + 1)])
        genertor_fuel_cost_series = np.array([-1 * generator['year_one_fuel_cost_us_dollars'] * \
                                              (1 + financials['om_cost_escalation_pct']) ** yr for yr in
                                              range(1, years + 1)])
        net_energy_costs = -electricity_bill_bau_series_bau - export_credit_bau_series_bau + electricity_bill_series + \
                           export_credit_series + annual_income_from_host_series - existing_genertor_fuel_cost_series + \
                           genertor_fuel_cost_series
        if financials['owner_tax_pct'] > 0:
            deductable_net_energy_costs = copy.deepcopy(net_energy_costs)
        else:
            deductable_net_energy_costs = np.array([0] * years)

        offtaker_free_cashflow = [round(i, 2) for i in [0] + list(
            electricity_bill_series + export_credit_series + genertor_fuel_cost_series + annual_income_from_host_series)]
        offtaker_discounted_cashflow = None
        offtaker_free_cashflow_bau = [round(i, 2) for i in [0] + list(
            electricity_bill_bau_series_bau + export_credit_bau_series_bau + existing_genertor_fuel_cost_series)]
        offtaker_discounted_cashflow_bau = None
    else:
        # get cumulative cashflow for offtaker
        electricity_bill_bau_series_bau = np.array([-1 * electric_tariff['year_one_bill_bau_us_dollars'] * \
                                                    (1 + financials['escalation_pct']) ** yr for yr in
                                                    range(1, years + 1)])
        export_credit_bau_series_bau = np.array([electric_tariff['total_export_benefit_bau_us_dollars'] * \
                                                 (1 + financials['escalation_pct']) ** yr for yr in
                                                 range(1, years + 1)])
        total_operating_expenses_bau = electricity_bill_bau_series_bau + export_credit_bau_series_bau + om_series_bau
        total_cash_incentives_bau = total_pbi_bau * (1 - financials['offtaker_tax_pct'])
        if financials['offtaker_tax_pct'] > 0:
            deductable_operating_expenses_series_bau = copy.deepcopy(total_operating_expenses_bau)
        else:
            deductable_operating_expenses_series_bau = np.array([0] * years)
        operating_expenses_after_tax_bau = (total_operating_expenses_bau - deductable_operating_expenses_series_bau) + (
                    deductable_operating_expenses_series_bau * (1 - financials['offtaker_tax_pct']))
        free_cashflow_bau = operating_expenses_after_tax_bau + total_cash_incentives_bau
        free_cashflow_bau = np.append([0], free_cashflow_bau)
        offtaker_free_cashflow = list([round(i, 2) for i in free_cashflow])
        offtaker_discounted_cashflow = [round(v / ((1 + financials['offtaker_discount_pct']) ** yr), 2) for yr, v in
                                        enumerate(offtaker_free_cashflow)]
        offtaker_free_cashflow_bau = list([round(i, 2) for i in free_cashflow_bau])
        offtaker_discounted_cashflow_bau = [round(v / ((1 + financials['offtaker_discount_pct']) ** yr), 2) for yr, v in
                                            enumerate(free_cashflow_bau)]
        # difference optimal and BAU
        net_free_cashflow = free_cashflow - free_cashflow_bau
        irr = np.irr(net_free_cashflow)
        cumulative_cashflow = np.cumsum(net_free_cashflow)

    # At this point we have the cumulative_cashflow for the developer or offtaker so the payback calculation is the same
    if cumulative_cashflow[-1] < 0:  # case where the system does not pay itself back in the analysis period
        return None, None, round(net_present_cost, 4) if net_present_cost is not None else None, \
               round(annualized_payment_to_third_party_us_dollars,
                     4) if annualized_payment_to_third_party_us_dollars is not None else None, \
               offtaker_free_cashflow, offtaker_free_cashflow_bau, offtaker_discounted_cashflow, offtaker_discounted_cashflow_bau, \
               developer_free_cashflow
    simple_payback_years = 0
    for i in range(1, years + 1):
        # add years where the cumulative cashflow is negative
        if cumulative_cashflow[i] < 0:
            simple_payback_years += 1
        # fractionally add years where the cumulative cashflow became positive
        elif (cumulative_cashflow[i - 1] < 0) and (cumulative_cashflow[i] > 0):
            simple_payback_years += -(cumulative_cashflow[i - 1] / net_free_cashflow[i])
        # skip years where cumulative cashflow is positive and the previous year's is too

    return round(simple_payback_years, 4), round(irr, 4), round(net_present_cost,
                                                                4) if net_present_cost is not None else None, \
           round(annualized_payment_to_third_party_us_dollars,
                 4) if annualized_payment_to_third_party_us_dollars is not None else None, \
           offtaker_free_cashflow, offtaker_free_cashflow_bau, offtaker_discounted_cashflow, offtaker_discounted_cashflow_bau, \
           developer_free_cashflow
