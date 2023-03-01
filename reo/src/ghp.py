import numpy as np
import copy
from reo.utilities import MMBTU_TO_KWH, TONHOUR_TO_KWHT
from reo.src.incentives import Incentives, IncentivesNoProdBased
from reo.src.data_manager import big_number


class GHPGHX:
        
    def __init__(self, dfm, response, **kwargs):
        # Multiple GHP design choices/options strategy: make a GHPGHX object FOR EACH (in scenario.py)
        # Loop through range(len(response)) in data_manager to build array inputs for REopt
        self.ghp_uuid = response["ghp_uuid"]
        # Inputs of GHPGHX, which are still needed in REopt
        self.heating_thermal_mmbtu_per_hr = response["inputs"]["heating_thermal_load_mmbtu_per_hr"]
        self.heating_thermal_kw = list(np.array(self.heating_thermal_mmbtu_per_hr) * MMBTU_TO_KWH)
        self.cooling_thermal_ton = response["inputs"]["cooling_thermal_load_ton"]
        self.cooling_thermal_kw = list(np.array(self.cooling_thermal_ton) * TONHOUR_TO_KWHT)
        # Outputs of GHPGHX, such as number of bores for GHX size
        self.number_of_boreholes = response["outputs"]["number_of_boreholes"]
        self.length_boreholes_ft = response["outputs"]["length_boreholes_ft"]
        self.yearly_total_electric_consumption_series_kw = response["outputs"]["yearly_total_electric_consumption_series_kw"]
        self.peak_combined_heatpump_thermal_ton = response["outputs"]["peak_combined_heatpump_thermal_ton"]
        # TODO replace dummy values below with GhpGhx.jl response fields
        self.yearly_auxiliary_boiler_consumption_series_mmbtu_per_hour = [5.0] * 8760 #response["outputs"]["yearly_auxiliary_boiler_consumption_series_mmbtu_per_hour"]
        self.yearly_auxiliary_cooling_tower_consumption_series_ton = [20.0] * 8760 #response["outputs"]["yearly_auxiliary_cooling_tower_consumption_series_ton"]
        self.peak_auxiliary_boiler_mmbtu_per_hour = 5.0 #response["outputs"]["peak_auxiliary_boiler_mmbtu_per_hour"]
        self.peak_auxiliary_cooling_tower_ton = 20.0 #response["outputs"]["peak_auxiliary_cooling_tower_ton"]

        if kwargs.get("require_ghp_purchase"):
            self.require_ghp_purchase = 1
        else:
            self.require_ghp_purchase = 0
        self.installed_cost_heatpump_us_dollars_per_ton = kwargs.get("installed_cost_heatpump_us_dollars_per_ton")
        self.heatpump_capacity_sizing_factor_on_peak_load = kwargs.get("heatpump_capacity_sizing_factor_on_peak_load")
        self.installed_cost_ghx_us_dollars_per_ft = kwargs.get("installed_cost_ghx_us_dollars_per_ft")
        self.installed_cost_building_hydronic_loop_us_dollars_per_sqft = kwargs.get("installed_cost_building_hydronic_loop_us_dollars_per_sqft")
        self.om_cost_us_dollars_per_sqft_year = kwargs.get("om_cost_us_dollars_per_sqft_year")
        self.building_sqft = kwargs.get("building_sqft")
        # TODO is_hybrid_ghx will be moved to the ghpghx_inputs field
        self.is_hybrid_ghx = kwargs.get("is_hybrid_ghx")
        self.aux_heater_type = kwargs.get("aux_heater_type")
        self.aux_heater_installed_cost_us_dollars_per_mmbtu_per_hr = kwargs.get("aux_heater_installed_cost_us_dollars_per_mmbtu_per_hr")
        self.aux_heater_thermal_efficiency = kwargs.get("aux_heater_thermal_efficiency")
        self.aux_cooler_installed_cost_us_dollars_per_ton = kwargs.get("aux_cooler_installed_cost_us_dollars_per_ton")
        self.aux_cooler_energy_use_intensity_kwe_per_kwt = kwargs.get("aux_cooler_energy_use_intensity_kwe_per_kwt")         

        # Heating and cooling loads served and electricity consumed by GHP
        # TODO with hybrid with auxiliary/supplemental heating/cooling devices, we may want to separate out/distiguish that energy
        self.heating_thermal_load_served_kw = self.heating_thermal_kw
        self.cooling_thermal_load_served_kw = self.cooling_thermal_kw
        self.electric_consumption_kw = self.yearly_total_electric_consumption_series_kw

        # Change units basis from ton to kW to use existing Incentives class
        self.kwargs_mod = copy.deepcopy(kwargs)
        for region in ["federal", "state", "utility"]:
            self.kwargs_mod[region + "_rebate_us_dollars_per_kw"] = kwargs.get(region + "_rebate_us_dollars_per_ton")
        self.incentives = IncentivesNoProdBased(**self.kwargs_mod)
        
        self.setup_installed_cost_curve()

        self.setup_om_cost()

        # TODO finish fuel/cost/emissions
        # if self.aux_heater_type == "natural_gas":
        #     self.fuel_burn_series_mmbtu_per_hour = [self.yearly_auxiliary_boiler_consumption_series_mmbtu_per_hour[i] / self.aux_heater_thermal_efficiency 
        #                                                 for i in range(len(self.yearly_auxiliary_boiler_consumption_series_mmbtu_per_hour))]
        #     self.aux_heater_yearly_fuel_burn_mmbtu = sum(self.fuel_burn_series_mmbtu_per_hour)
        #     self.yearly_emissions_lb_CO2 = dfm.boiler.emissions_factor_lb_CO2_per_mmbtu * self.aux_heater_yearly_fuel_burn_mmbtu
        #     self.yearly_emissions_lb_NOx = dfm.boiler.emissions_factor_lb_NOx_per_mmbtu * self.aux_heater_yearly_fuel_burn_mmbtu
        #     self.yearly_emissions_lb_SOx = dfm.boiler.emissions_factor_lb_SOx_per_mmbtu * self.aux_heater_yearly_fuel_burn_mmbtu
        #     self.yearly_emissions_lb_PM25 = dfm.boiler.emissions_factor_lb_PM25_per_mmbtu * self.aux_heater_yearly_fuel_burn_mmbtu


        dfm.add_ghp(self)
    
    def setup_installed_cost_curve(self):
        # GHX and GHP sizing metrics for cost calculations
        self.total_ghx_ft = self.number_of_boreholes * self.length_boreholes_ft
        self.heatpump_peak_tons = self.peak_combined_heatpump_thermal_ton
        
        # Use initial cost curve to leverage existing incentives-based cost curve method in data_manager
        # The GHX and hydronic loop cost are the y-intercepts ([$]) of the cost for each design
        self.ghx_cost = self.total_ghx_ft * self.installed_cost_ghx_us_dollars_per_ft
        self.hydronic_loop_cost = self.building_sqft * self.installed_cost_building_hydronic_loop_us_dollars_per_sqft
        self.aux_heater_cost = self.aux_heater_installed_cost_us_dollars_per_mmbtu_per_hr * self.peak_auxiliary_boiler_mmbtu_per_hour
        self.aux_cooler_cost = self.aux_cooler_installed_cost_us_dollars_per_ton * self.peak_auxiliary_cooling_tower_ton

        # The DataManager._get_REopt_cost_curve method expects at least a two-point tech_size_for_cost_curve to
        #   to use the first value of installed_cost_us_dollars_per_kw as an absolute $ value and
        #   the initial slope is based on the heat pump size (e.g. $/ton) of the cost curve for
        #   building a rebate-based cost curve if there are less-than big_number maximum incentives
        self.tech_size_for_cost_curve = [0.0, big_number]
        self.installed_cost_us_dollars_per_kw = [self.ghx_cost + self.hydronic_loop_cost + 
                                                 self.aux_heater_cost + self.aux_cooler_cost, 
                                                 self.installed_cost_heatpump_us_dollars_per_ton]

        # Using a separate call to _get_REopt_cost_curve in data_manager for "ghp" (not included in "available_techs")
        #    and then use the value below for heat pump capacity to calculate the final absolute cost for GHP

        # Use this with the cost curve to determine absolute cost
        self.heatpump_capacity_tons = self.heatpump_peak_tons * self.heatpump_capacity_sizing_factor_on_peak_load

    def setup_om_cost(self):
        # O&M Cost
        self.om_cost_year_one = self.building_sqft * self.om_cost_us_dollars_per_sqft_year