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
import logging
from django.db import models
from django.contrib.postgres.fields import *
from django.forms.models import model_to_dict
from picklefield.fields import PickledObjectField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

log = logging.getLogger(__name__)


class GHPGHXModel(models.Model):
    # Inputs
    # user = models.ForeignKey(User, null=True, blank=True)
    ghp_uuid = models.UUIDField(primary_key=True, unique=True, editable=False)
    status = models.TextField(blank=True, default="")
    latitude = models.FloatField(null=True, blank=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        help_text="Latitude of the site")
    longitude = models.FloatField(null=True, blank=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        help_text="Longitude of the site")
    
    # Parameters
    borehole_depth_ft = models.FloatField(null=True, blank=True, 
        default=400.0, validators=[MinValueValidator(10.0), MaxValueValidator(600.0)],
        help_text="Vertical depth of each borehole [ft]")
    ghx_header_depth_ft = models.FloatField(null=True, blank=True, 
        default=4.0, validators=[MinValueValidator(0.1), MaxValueValidator(50.0)],
        help_text="Depth under the ground of the GHX header pipe [ft]")
    borehole_spacing_ft = models.FloatField(null=True, blank=True, 
        default=20.0, validators=[MinValueValidator(1.0), MaxValueValidator(100.0)],
        help_text="Distance from the centerline of each borehole to the centerline of its adjacent boreholes [ft]")
    borehole_diameter_inch = models.FloatField(null=True, blank=True, 
        default=1.66, validators=[MinValueValidator(0.25), MaxValueValidator(24.0)],
        help_text="Diameter of the borehole/well drilled in the ground [in]")
    borehole_choices = [("rectangular", "rectangular"),
                        ("hexagonal", "hexagonal")]
    borehole_spacing_type = models.TextField(blank=True,
        default="rectangular", choices=borehole_choices,
        help_text="Borehole spacing pattern type: rectangular or hexagonal")
    ghx_pipe_outer_diameter_inch = models.FloatField(null=True, blank=True, 
        default=1.66, validators=[MinValueValidator(0.25), MaxValueValidator(24.0)],
        help_text="Outer diameter of the GHX pipe [in]")
    ghx_pipe_wall_thickness_inch = models.FloatField(null=True, blank=True, 
        default=0.16, validators=[MinValueValidator(0.01), MaxValueValidator(5.0)],
        help_text="Wall thickness of the GHX pipe [in]")
    ghx_pipe_thermal_conductivity_btu_per_hr_ft_f = models.FloatField(null=True, blank=True, 
        default=0.25, validators=[MinValueValidator(0.01), MaxValueValidator(10.0)],
        help_text="Thermal conductivity of the GHX pipe [Btu/(hr-ft-degF)]")
    ghx_shank_space_inch = models.FloatField(null=True, blank=True, 
        default=2.5, validators=[MinValueValidator(0.5), MaxValueValidator(100.0)],
        help_text="Distance between the centerline of the upwards and downwards u-tube legs [in]")
    ground_thermal_conductivity_btu_per_hr_ft_f = models.FloatField(null=True, blank=True, 
        default=0.98, validators=[MinValueValidator(0.01), MaxValueValidator(15.0)],
        help_text="Thermal conductivity of the ground surrounding the borehole field [Btu/(hr-ft-degF)]")
    ground_mass_density_lb_per_ft3 = models.FloatField(null=True, blank=True,
        default=162.3, validators=[MinValueValidator(10.0), MaxValueValidator(500.0)],
        help_text="Mass density of the ground surrounding the borehole field [lb/ft^3]")
    ground_specific_heat_btu_per_lb_f = models.FloatField(null=True, blank=True, 
        default=0.211, validators=[MinValueValidator(0.01), MaxValueValidator(5.0)],
        help_text="Specific heat of the ground surrounding the borehole field")
    grout_thermal_conductivity_btu_per_hr_ft_f = models.FloatField(null=True, blank=True, 
        default=1.0, validators=[MinValueValidator(0.01), MaxValueValidator(10.0)],
        help_text="Thermal conductivity of the grout material in a borehole [Btu/(hr-ft-degF)]")
    ghx_fluid_specific_heat_btu_per_lb_f = models.FloatField(null=True, blank=True, 
        default=1.0, validators=[MinValueValidator(0.1), MaxValueValidator(10.0)],
        help_text="Specific heat of the fluid in the GHX (nominally water) [Btu/(lb-degF)]")
    ghx_fluid_mass_density_lb_per_ft3 = models.FloatField(null=True, blank=True, 
        default=62.4, validators=[MinValueValidator(1.0), MaxValueValidator(200.0)],
        help_text="Mass density of the fluid in the GHX (nominally water) [lb/ft^3]")
    ghx_fluid_thermal_conductivity_btu_per_hr_ft_f = models.FloatField(null=True, blank=True, 
        default=0.36, validators=[MinValueValidator(0.01), MaxValueValidator(5.0)],
        help_text="Thermal conductivity of the fluid in the GHX (nominally water) [Btu/(hr-ft-degF)]")
    ghx_fluid_dynamic_viscosity_lbm_per_ft_hr = models.FloatField(null=True, blank=True, 
        default=1.58, validators=[MinValueValidator(0.1), MaxValueValidator(10.0)],
        help_text="Dynamic viscosity of the fluid in the GHX (nominally water) [lb/(ft-hr)]")
    ghx_fluid_flow_rate_gpm_per_ton = models.FloatField(null=True, blank=True, 
        default=2.5, validators=[MinValueValidator(0.1), MaxValueValidator(10.0)],
        help_text="Volumetric flow rate of the fluid in the GHX per peak ton heating/cooling [GPM/ton]")
    ghx_pump_power_watt_per_gpm = models.FloatField(null=True, blank=True, 
        default=15.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Pumping power required for a given volumetric flow rate of the fluid in the GHX [Watt/GPM]")
    ghx_pump_min_speed_fraction = models.FloatField(null=True, blank=True, 
        default=0.1, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="The minimum turndown fraction of the pump. 1.0 is a constant speed pump.")
    ghx_pump_power_exponent = models.FloatField(null=True, blank=True, 
        default=2.2, validators=[MinValueValidator(0.1), MaxValueValidator(10.0)],
        help_text="The pump power curve exponent")
    max_eft_allowable_f = models.FloatField(null=True, blank=True, 
        default=104.0, validators=[MinValueValidator(0.0), MaxValueValidator(150.0)],
        help_text="Maximum allowable entering fluid temperature (EFT) of the heat pump (used in cooling dominated loads) [degF]")
    min_eft_allowable_f = models.FloatField(null=True, blank=True, 
        default=23.0, validators=[MinValueValidator(-50.0), MaxValueValidator(100.0)],
        help_text="Minimum allowable entering fluid temperature (EFT) of the heat pump (used in heating dominated loads) [degF]")
    
    # Array/Dict inputs
    heating_thermal_load_mmbtu_per_hr = ArrayField(models.FloatField(null=True, blank=True), 
        default=list, null=True, blank=True,
        help_text="Hourly heating thermal load that GHP serves [MMBtu/hr]")
    # Heating **fuel** load and boiler_efficiency may be given instead of **thermal** load
    heating_fuel_load_mmbtu_per_hr = ArrayField(models.FloatField(null=True, blank=True), 
        default=list, null=True, blank=True,
        help_text="Hourly heating fuel load that GHP serves [MMBtu/hr]")
    existing_boiler_efficiency = models.FloatField(null=True, blank=True,
        default=0.8, validators=[MinValueValidator(0.01), MaxValueValidator(1.0)],
        help_text="Efficiency of the existing boiler/heater serving the heating load")
    cooling_thermal_load_ton = ArrayField(models.FloatField(null=True, blank=True), 
        default=list, null=True, blank=True,
        help_text="Hourly cooling thermal load that GHP serves [ton]")
    ambient_temperature_f = ArrayField(models.FloatField(null=True, blank=True), 
        default=list, null=True, blank=True,
        help_text="Hourly outdoor air dry bulb temperature, typically TMY3 data [degF]")
    cop_map_eft_heating_cooling = ArrayField(
        PickledObjectField(null=True, editable=True), null=True,
        help_text="Heat pump coefficient of performance (COP) map: list of dictionaries, each with 3 keys: 1) EFT, 2) HeatingCOP, 3) CoolingCOP")

    """
    TODO define custom clean_cop_map()
    def clean_cop_map(self):
        for pt in range(length(cop_map_eft_heating_cooling)):
            # Check that float values are present for each of the expected 3 key entries
            # Check if temps are in ascending order
            # Check min/max values
    
    TODO still have a validators.py that we import from if we want custom validators (might not need for GHPGHX app) 
    that can be reused easily by adding to model fields option validators=[validator1, validator2, etc]
    in that validators.py, we need to "from django.core.exceptions import ValidationError" to raise 
    ValidationError for those custom ones

    TODO define clean() method for validating related fields, such as ghx_pipe_outer_diameter_inch and ghx_shank_space_inch
    def clean(self):
        if ghx_shank_space_inch + 0.0001 < ghx_pipe_outer_diameter_inch
            raise ValidationError("Invalid shank space and ghx pipe diameter - pipes would interfere!)
    """

    # Model Settings
    simulation_years = models.IntegerField(null=True, blank=True, 
        default=25, validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text="The time span for which GHX is sized to meet the entering fluid temperature constraints [year]")
    solver_eft_tolerance_f = models.FloatField(null=True, blank=True, 
        default=0.1, validators=[MinValueValidator(0.001), MaxValueValidator(5.0)],
        help_text="Tolerance for GHX sizing based on the entering fluid temperature limits [degF]")
    ghx_model_choices = [("TESS", "TESS"),
                         ("DST", "DST")]        
    ghx_model = models.TextField(blank=True,
        default="TESS", choices=ghx_model_choices,
        help_text="GHX model to use in the simulation: TESS or DST")
    dst_ghx_timesteps_per_hour = models.IntegerField(null=True, blank=True, 
        default=12, validators=[MinValueValidator(1), MaxValueValidator(60)],
        help_text="Time steps per hour to use for the DST GHX model")
    tess_ghx_minimum_timesteps_per_hour = models.IntegerField(null=True, blank=True, 
        default=1, validators=[MinValueValidator(1), MaxValueValidator(60)],
        help_text="Minimum time steps per hour to use for the TESS GHX model; the model will decide if more is needed each hour")
    max_sizing_iterations = models.IntegerField(null=True, blank=True, 
        default=15, validators=[MinValueValidator(1), MaxValueValidator(15)],
        help_text="Maximum number of sizing iterations before the GHPGHX model times out")
    init_sizing_factor_ft_per_peak_ton = models.FloatField(null=True, blank=True, 
        default=246.1, validators=[MinValueValidator(1.0), MaxValueValidator(5000.0)],
        help_text="Initial guess of total feet of GHX boreholes (total feet = N bores * Length bore) based on peak ton heating/cooling [ft/ton]")

    # Outputs/results - need to move these from "inputs to outputs" in ModelManager.make_response
    number_of_boreholes = models.FloatField(null=True, blank=True,
        help_text="Minimum required number of boreholes to meet heat pump EWT constraints")
    length_boreholes_ft = models.FloatField(null=True, blank=True,
        help_text="Length of each borehole, drilled vertically in the ground [ft]")
    yearly_heating_heatpump_electric_consumption_series_kw = ArrayField(models.FloatField(null=True, blank=True), 
        default=list, null=True, blank=True,
        help_text="Hourly heating heat pump electric consumption, average across simulation years [kW]")
    yearly_cooling_heatpump_electric_consumption_series_kw = ArrayField(models.FloatField(null=True, blank=True), 
        default=list, null=True, blank=True,
        help_text="Hourly cooling heat pump electric consumption, average across simulation years [kW]")
    yearly_ghx_pump_electric_consumption_series_kw = ArrayField(models.FloatField(null=True, blank=True), 
        default=list, null=True, blank=True,
        help_text="Hourly GHX pump electric consumption, average across simulation years [kW]")
    yearly_total_electric_consumption_series_kw = ArrayField(models.FloatField(null=True, blank=True), 
        default=list, null=True, blank=True,
        help_text="Hourly total GHP electric consumption, average across simulation years [kW]")
    yearly_total_electric_consumption_kwh = models.FloatField(null=True, blank=True, 
        help_text="Total yearly electric consumption by GHPGHX system [kWh]")
    peak_heating_heatpump_thermal_ton = models.FloatField(null=True, blank=True, 
        help_text="Peak heating heat pump thermal load served [ton]")
    peak_cooling_heatpump_thermal_ton = models.FloatField(null=True, blank=True, 
        help_text="Peak cooling heat pump thermal load served [ton]")
    peak_combined_heatpump_thermal_ton = models.FloatField(null=True, blank=True, 
        help_text="Peak combined heating/cooling heat pump thermal load served [ton]")
    max_eft_f = models.FloatField(null=True, blank=True, 
        help_text="Maximum entering fluid temperature (to heat pump, from ghx) throughout the GHPGHX simulation period")
    min_eft_f = models.FloatField(null=True, blank=True, 
        help_text="Minimum entering fluid temperature (to heat pump, from ghx) throughout the GHPGHX simulation period")
    heating_cop_avg = models.FloatField(null=True, blank=True, 
        help_text="Average heating heatpump system coefficient of performance (COP) (includes ghx pump allocation)")
    cooling_cop_avg = models.FloatField(null=True, blank=True, 
        help_text="Average cooling heatpump system coefficient of performance (COP) (includes ghx pump allocation)")
    solved_eft_error_f = models.FloatField(null=True, blank=True,
        help_text="Error between the solved GHPGHX system EFT and the max or min limit for EFT")


class ModelManager(object):

    def __init__(self):
        self.ghpghxM = None

    @staticmethod
    def make_response(ghp_uuid):
        """
        Reconstruct response dictionary from postgres tables (django models).
        # TODO Make sure the NOTE below is not relevant for ghpghx because it uses primary_key=True for ghp_uuid
        NOTE: postgres column type UUID is not JSON serializable. Work-around is removing those columns and then
              adding back into outputs->Scenario as string.
        :param ghp_uuid:
        :return: nested dictionary matching nested_output_definitions
        """

        resp = dict()
        resp["ghp_uuid"] = str(ghp_uuid)
        resp["outputs"] = dict()
        resp["inputs"] = dict()
        resp["messages"] = dict()

        try:
            ghpghx_model = GHPGHXModel.objects.get(ghp_uuid=ghp_uuid)
        except Exception as e:
            if isinstance(e, models.ObjectDoesNotExist):
                resp['messages']['error'] = (
                    "ghp_uuid {} not in database. "
                    "You may have hit the results endpoint too quickly after POST'ing scenario, "
                    "you may have a typo in your ghp_uuid, or the scenario was deleted.").format(ghp_uuid)
                resp['status'] = 'error'
                return resp
            else:
                raise Exception
        #ghpghx_data = remove_ids(model_to_dict(ghpghx_model))
        ghpghx_data = model_to_dict(ghpghx_model)

        # Listed here to separate outputs from the model, so need to keep this update with added outputs to model
        output_fields = ["number_of_boreholes",
                        "length_boreholes_ft", 
                        "yearly_heating_heatpump_electric_consumption_series_kw",
                        "yearly_cooling_heatpump_electric_consumption_series_kw",
                        "yearly_ghx_pump_electric_consumption_series_kw",
                        "yearly_total_electric_consumption_series_kw",
                        "yearly_total_electric_consumption_kwh",
                        "peak_heating_heatpump_thermal_ton",
                        "peak_cooling_heatpump_thermal_ton",
                        "peak_combined_heatpump_thermal_ton",
                        "max_eft_f",
                        "min_eft_f",
                        "heating_cop_avg",
                        "cooling_cop_avg",
                        "solved_eft_error_f"]

        resp["inputs"] = ghpghx_data
        del resp["inputs"]["status"]
        for out in output_fields:
            resp["outputs"][out] = ghpghx_data[out]
            del resp["inputs"][out]

        return resp


