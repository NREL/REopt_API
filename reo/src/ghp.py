import numpy as np
from reo.utilities import MMBTU_TO_KWH, TONHOUR_TO_KWHT

class GHPGHXInputs:
    """
    Map the GHPGHX inputs to the objects in this class
    """

    def __init__(self, inputs):
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

    def __init__(self, inputs, results, **kwargs):       
        self.n_bores = results["N_Bores"]
        self.bore_depth = results["Length_Boreholes"]
        
        self.building_sqft = kwargs.get("building_sqft")
        self.installed_cost_ghx_us_dollars_per_ft = kwargs.get("installed_cost_ghx_us_dollars_per_ft")

        self.inputs = GHPGHXInputs(inputs)

        # Calculations for costing
        self.total_ghx_ft = self.n_bores * self.bore_depth
        self.heatpump_capacity_tons = np.max(np.array(self.inputs.heating_thermal_kw) + 
                                                np.array(self.inputs.cooling_thermal_kw)) / TONHOUR_TO_KWHT

        self.calc_cost()
    
    def calc_cost(self):
        # TODO somehow integrate capital costing into existing cost calcs in data_manager
        self.ghx_cost = self.total_ghx_ft * self.installed_cost_ghx_us_dollars_per_ft
