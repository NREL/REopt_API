import numpy as np
import copy
from reo.utilities import MMBTU_TO_KWH, TONHOUR_TO_KWHT
from reo.src.incentives import Incentives, IncentivesNoProdBased

big_number = 1.0e10

class GHPGHXInputs:
    """
    Map the GHPGHX inputs to the objects in this class
    """

    def __init__(self, inputs, **kwargs):
        #TODO Add ALL the input fields for the GHPGHX model
        #   (and maybe also the calculated parameters which are kind of calculated inputs)
        self.heating_thermal_mmbtu_per_hr = inputs["heating_thermal_load_mmbtu_per_hr"]
        self.heating_thermal_kw = self.heating_thermal_mmbtu_per_hr * MMBTU_TO_KWH
        self.cooling_thermal_ton = inputs["cooling_thermal_load_ton"]
        self.cooling_thermal_kw = self.cooling_thermal_ton * TONHOUR_TO_KWHT

class GHPGHXResponse:
    """
    Define the GHPGHX response parameters that would go to REopt
    """

    def __init__(self, response, **kwargs):       
        self.n_bores = response["N_Bores"]
        self.length_boreholes = response["Length_Boreholes"]


class GHPGHX:
        
    def __init__(self, dfm, ghp_design_number, inputs, response, **kwargs):
        # Multiple GHP design choices/options strategy: make a GHPGHX object FOR EACH (in scenario.py)
        # Loop through range(len(response)) in data_manager to create N GHPGHX objects and build array inputs for REopt
        self.ghp_design_number = ghp_design_number
        self.inputs = GHPGHXInputs(inputs)  # This is a single dictionary where the **kwargs/POST is a list_of_dict
        self.response = GHPGHXResponse(response)  # This is a single dictionary where the **kwargs/POST is a list_of_dict

        self.installed_cost_heatpump_us_dollars_per_ton = kwargs.get("installed_cost_heatpump_us_dollars_per_ton")
        self.heatpump_capacity_sizing_factor_on_peak_load = kwargs.get("heatpump_capacity_sizing_factor_on_peak_load")
        self.installed_cost_ghx_us_dollars_per_ft = kwargs.get("installed_cost_ghx_us_dollars_per_ft")
        self.installed_cost_building_hydronic_loop_us_dollars_per_sqft = kwargs.get("installed_cost_building_hydronic_loop_us_dollars_per_sqft")
        self.om_cost_us_dollars_per_sqft_year = kwargs.get("om_cost_us_dollars_per_sqft_year")
        self.building_sqft = kwargs.get("building_sqft")

        # Change units basis from ton to kW to use existing Incentives class
        self.kwargs_mod = copy.deepcopy(kwargs)
        for region in ["federal", "state", "utility"]:
            self.kwargs_mod[region + "_rebate_us_dollars_per_kw"] = kwargs.get(region + "_rebate_us_dollars_per_ton")
        self.incentives = IncentivesNoProdBased(**self.kwargs_mod)
        
        self.setup_installed_cost_curve()

        self.setup_om_cost()

        dfm.add_ghp(self)
    
    def setup_installed_cost_curve(self):
        # GHX and GHP sizing metrics for cost calculations
        self.total_ghx_ft = self.response.n_bores * self.response.length_boreholes
        self.heatpump_peak_tons = np.max(np.array(self.inputs.heating_thermal_kw) + 
                                                np.array(self.inputs.cooling_thermal_kw)) / TONHOUR_TO_KWHT
        
        # Use initial cost curve to leverage existing incentives-based cost curve method in data_manager
        # The GHX and hydronic loop cost are the y-intercepts ([$]) of the cost for each design
        self.ghx_cost = self.total_ghx_ft * self.installed_cost_ghx_us_dollars_per_ft
        self.hydronic_loop_cost = self.building_sqft * self.installed_cost_building_hydronic_loop_us_dollars_per_sqft

        # The DataManager._get_REopt_cost_curve method expects at least a two-point tech_size_for_cost_curve to
        #   to use the first value of installed_cost_us_dollars_per_kw as an absolute $ value and
        #   the initial slope is based on the heat pump size (e.g. $/ton) of the cost curve for
        #   building a rebate-based cost curve if there are less-than big_number maximum incentives
        self.tech_size_for_cost_curve = [0.0, big_number]
        self.installed_cost_us_dollars_per_kw = [self.ghx_cost + self.hydronic_loop_cost, 
                                                self.installed_cost_heatpump_us_dollars_per_ton]

        # TODO use a separate call to _get_REopt_cost_curve in data_manager for "ghp" (not included in "available_techs")
        #    and then use the value below for heat pump capacity to calculate the final absolute cost for GHP

        # Use this with the cost curve to determine absolute cost
        self.heatpump_capacity_tons = self.heatpump_peak_tons * self.heatpump_capacity_sizing_factor_on_peak_load

    def setup_om_cost(self):
        # O&M Cost
        self.om_cost_yearly = self.building_sqft * self.om_cost_us_dollars_per_sqft_year