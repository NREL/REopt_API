# Using same struct type from REopt utils.jl
# Warning: I've seen notes of Base.@kwdef not being officially supported (not documented)
"""
    InputsStruct

This struct defines the inputs for the GHPGHX module
"""
Base.@kwdef struct InputsStruct
    ##### These are the exact /ghpghx POST names from the API #####
    # Parameters
    borehole_depth_ft::Float64
    ghx_header_depth_ft::Float64
    borehole_spacing_ft::Float64
    borehole_diameter_inch::Float64
    borehole_spacing_type::String  # "rectangular" or "hexagonal"
    ghx_pipe_outer_diameter_inch::Float64
    ghx_pipe_wall_thickness_inch::Float64
    ghx_pipe_thermal_conductivity_btu_per_hr_ft_f::Float64
    ghx_shank_space_inch::Float64
    ground_thermal_conductivity_btu_per_hr_ft_f::Float64
    ground_mass_density_lb_per_ft3::Float64
    ground_specific_heat_btu_per_lb_f::Float64
    grout_thermal_conductivity_btu_per_hr_ft_f::Float64
    ghx_fluid_specific_heat_btu_per_lb_f::Float64
    ghx_fluid_mass_density_lb_per_ft3::Float64
    ghx_fluid_thermal_conductivity_btu_per_hr_ft_f::Float64
    ghx_fluid_dynamic_viscosity_lbm_per_ft_hr::Float64
    ghx_fluid_flow_rate_gpm_per_ton::Float64
    ghx_pump_power_watt_per_gpm::Float64
    ghx_pump_min_speed_fraction::Float64
    ghx_pump_power_exponent::Float64
    max_eft_allowable_f::Float64
    min_eft_allowable_f::Float64
    
    # Array/Dict inputs
    heating_thermal_load_mmbtu_per_hr::Array{Float64,1}
    cooling_thermal_load_ton::Array{Float64,1}
    ambient_temperature_f::Array{Float64,1}
    cop_map_eft_heating_cooling::Array{Any,1}

    # Model Settings
    simulation_years::Int64  # Number of years for GHP-GHX model
    solver_eft_tolerance_f::Float64  # Tolerance for the EFT error to accept a GHX sizing solution
    solver_eft_tolerance::Float64  # Convert to degC
    ghx_model::String  # "TESS" or "DST"
    dst_ghx_timesteps_per_hour::Int64
    tess_ghx_minimum_timesteps_per_hour::Int64
    max_sizing_iterations::Int64
    init_sizing_factor_ft_per_peak_ton::Float64
    
    ##### These are the variable names used in the GHPGHX, kept from TESS ######
    # TODO eventually just use the API names above in GHPGHX to remove redundancy (BUT WOULD HAVE TO DEAL WITH UNITS CONVERSION STILL)  
    I_Configuration::Int64 = 1  #!1=Decentralized WSHPs, 2=Decentralized WWHPs, 3=Centralized WWHPs, 4=Centralized WWHPs with HRC
    Depth_Bores::Float64 #!Depth of the boreholes (ft)
    Depth_Header::Float64  #!Depth of the ground heat exchanger headers below grade (ft)
    BoreSpacing::Float64  #!Spacing between boreholes (ft)
    SpacingType::Int64  # Spacing type (1=rectangular, 2 = hexagonal)
    Radius_Bores::Float64  #!Radius of the boreholes (in)
    Ro_Pipe::Float64  #!Outer radius of individual u-tube pipe (in)
    Ri_Pipe::Float64  #!Inner radius of individual u-tube pipe (in)
    K_Pipe::Float64  #!Thermal conductivity of pipe material (BTU/h.ft.F)
    Center_Center_Distance::Float64  #!Distance between centers of upwards and downwards u-tube legs (in)
    K_Soil::Float64  #!Thermal conductivity of the soil (BTU/h.ft.F)
    Rho_Soil::Float64  #!Density of the soil (lbm/ft3)
    Cp_Soil::Float64  #!Specific heat of the soil (BTU/lbm.F)
    K_Grout::Float64  #!Thermal conductivity of the borehole grout (BTU/h.ft.F)
    T_Ground::Float64  #!Average soil surface temperature over the year (F)
    Tamp_Ground::Float64  #!Amplitude of soil surface temperature over the year (Delta_F)
    DayMin_Surface::Float64  #!Day of minimum soil surface temperature (day)
    Cp_GHXFluid::Float64 #!Specific heat of the ground heat exchanger fluid (BTU/lbm.F)
    Rho_GHXFluid::Float64  #!Density of the ground heat exchanger fluid (lbm/ft3)
    K_GHXFluid::Float64  #!Thermal conductivity of the ground heat exchanger fluid (BTU/h.ft.F)
    Mu_GHXFluid::Float64  #!Dynamic viscosity of the ground heat exchanger fluid (lbm/ft.h)
    GPMperTon_WSHP::Float64  #!Nominal flow rate of the water source heat pumps (gpm/ton)
    WattPerGPM_GHXPump::Float64  #!Nominal ground loop pump power (Watt/gpm)
    fMin_VSP_GHXPump::Float64  #!Minimum ground heat exchanger pump speed for variable speed option (set to 1 if constant speed pumps)
    Exponent_GHXPump::Float64  #!Exponent for relationship between ground heat exchanger pump power and ground heat exchanger pump flow rate
    Tmax_Sizing::Float64  #!Maximum allowable return fluid temperature from the ground loop (F)
    Tmin_Sizing::Float64  #!Minimum allowable return fluid temperature from the ground loop (F)    

    # Additional parameters and site data
    HeatingThermalLoadKW::Array{Float64, 1}  # Heating thermal load to be served by GHP
    CoolingThermalLoadKW::Array{Float64, 1}  # Cooling thermal load to be served by GHP
    AmbientTemperature::Array{Float64, 1}  # Dry-bulb outdoor air temperature in degrees Fahrenheit 
    HeatPumpCOPMap::Array{Float64, 2}  # Includes heating and cooling heat pump COP versus EWT (degF)

    # These are defined based on the above inputs and processed in the function below
    TON_TO_KW::Float64 # [kw/ton]
    MMBTU_TO_KWH::Float64  # [kwh/MMBtu]
    METER_TO_FEET::Float64  # [ft/m]

    PeakTons_WSHP_H::Float64
    PeakTons_WSHP_C::Float64
    PeakTons_WSHP_GHX::Float64
    X_init::Float64
    N_Series::Int64
    N_Radial::Int64
    N_Vertical::Int64
    RhoCp_Soil::Float64
    DayMin_DST::Float64
    GPM_GHXPump::Float64
    Prated_GHXPump::Float64
    LPS_GHXPump::Float64
    Mdot_GHXPump::Float64
end

"""
    InputsProcess(d::Dict)

Performs unit conversions, name conversions, and additional processing of inputs.

"""
function InputsProcess(d::Dict)   
    # Converts dictionary to allow String or Symbol for keys and Any type for values
    d = convert(Dict{Union{String, Symbol}, Any}, d)

    # Constants
    d[:TON_TO_KW] = 3.5169  # [kw/ton]
    d[:MMBTU_TO_KWH] = 293.07  # [kwh/MMBtu]
    d[:METER_TO_FEET] = 3.28084  # [ft/m]

    # Convert API inputs to GHPGHX variable names, and units from English to SI
    d[:Depth_Bores] =  d["borehole_depth_ft"] / d[:METER_TO_FEET]  # [m]
    d[:Depth_Header] = d["ghx_header_depth_ft"] / d[:METER_TO_FEET]  # [m]
    d[:BoreSpacing] = d["borehole_spacing_ft"] / d[:METER_TO_FEET]  # [m]
    if d["borehole_spacing_type"] == "rectangular"
        d[:SpacingType] = 1
    else
        d[:SpacingType] = 2
    end
    d[:Radius_Bores] = d["borehole_diameter_inch"] / 2.0 / 12.0 / d[:METER_TO_FEET]  # [m]
    d[:Ro_Pipe] = d["ghx_pipe_outer_diameter_inch"] / 2.0 / 12.0 / d[:METER_TO_FEET]  # [m]
    d[:Ri_Pipe] = (d["ghx_pipe_outer_diameter_inch"] / 2.0 - d["ghx_pipe_wall_thickness_inch"]) / 12.0 / d[:METER_TO_FEET]  # [m]
    d[:K_Pipe] = d["ghx_pipe_thermal_conductivity_btu_per_hr_ft_f"] * 1.055 * d[:METER_TO_FEET] * 1.8  # [kJ/h.m.K]
    d[:Center_Center_Distance] = d["ghx_shank_space_inch"] / 12.0 / d[:METER_TO_FEET]  # [m]
    d[:K_Soil] = d["ground_thermal_conductivity_btu_per_hr_ft_f"] * 1.055 * d[:METER_TO_FEET] * 1.8  # [kJ/h.m]
    d[:Rho_Soil] = d["ground_mass_density_lb_per_ft3"] * 35.31467 / 2.20462  # [kg/m3]
    d[:Cp_Soil] = d["ground_specific_heat_btu_per_lb_f"] * 1.8 * 2.20462 * 1.055  # [kJ/kg.K]
    d[:K_Grout] = d["grout_thermal_conductivity_btu_per_hr_ft_f"] * 1.055 * d[:METER_TO_FEET] * 1.8  # [kJ/h.m.K]    
    # See processing of ambient temperature for temperature parameters
    d[:Cp_GHXFluid] = d["ghx_fluid_specific_heat_btu_per_lb_f"] * 1.8 * 2.20462 * 1.055  # [kJ/kg.K]
    d[:Rho_GHXFluid] = d["ghx_fluid_mass_density_lb_per_ft3"] * 35.31467 / 2.20462  # [kg/m3]
    d[:K_GHXFluid] = d["ghx_fluid_thermal_conductivity_btu_per_hr_ft_f"] * 1.055 * d[:METER_TO_FEET] * 1.8  # [kJ/h.m.K]
    d[:Mu_GHXFluid] = d["ghx_fluid_dynamic_viscosity_lbm_per_ft_hr"] * d[:METER_TO_FEET] / 2.20462  # [kg/h.m]
    d[:GPMperTon_WSHP] = d["ghx_fluid_flow_rate_gpm_per_ton"]
    d[:WattPerGPM_GHXPump] = d["ghx_pump_power_watt_per_gpm"]
    d[:fMin_VSP_GHXPump] = d["ghx_pump_min_speed_fraction"]
    d[:Exponent_GHXPump] = d["ghx_pump_power_exponent"]
    d[:Tmax_Sizing] = (d["max_eft_allowable_f"] - 32.0) / 1.8  # [C]
    d[:Tmin_Sizing] = (d["min_eft_allowable_f"] - 32.0) / 1.8  # [C]
    d[:solver_eft_tolerance] = d["solver_eft_tolerance_f"] / 1.8  # [C]

    # Convert array input units to SI
    d[:HeatingThermalLoadKW] = d["heating_thermal_load_mmbtu_per_hr"] * d[:MMBTU_TO_KWH]
    d[:CoolingThermalLoadKW] = d["cooling_thermal_load_ton"] * d[:TON_TO_KW]
    d[:AmbientTemperature] = (d["ambient_temperature_f"] .- 32.0) / 1.8  # [C]

    # Use AmbientTemperature to calculate other temperature parameters
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    avg_temp_month = zeros(12)
    for (mo,days) in enumerate(days_in_month)
        hour_start = sum(days_in_month[1:mo-1]) * 24 + 1  # mo=1 results in 0 + 1 = 1
        hour_end = sum(days_in_month[1:mo]) * 24
        avg_temp_month[mo] = sum(d[:AmbientTemperature][hour_start:hour_end]) / (days * 24)
    end
    
    d[:T_Ground] = sum(d[:AmbientTemperature]) / (365 * 24)  # [C]
    d[:Tamp_Ground] =  (maximum(avg_temp_month) - minimum(avg_temp_month)) / 2  # [C]
    d[:DayMin_Surface] = convert(Int64, round(argmin(d[:AmbientTemperature]) / 24))  # day of year

    # Convert COP map list_of_dict to Array{Float64, 2}
    d[:HeatPumpCOPMap] = zeros(Float64, length(d["cop_map_eft_heating_cooling"]), 3)
    for i in 1:length(d["cop_map_eft_heating_cooling"])
        d[:HeatPumpCOPMap][i,1] = d["cop_map_eft_heating_cooling"][i]["eft"]
        d[:HeatPumpCOPMap][i,2] = d["cop_map_eft_heating_cooling"][i]["heat_cop"]
        d[:HeatPumpCOPMap][i,3] = d["cop_map_eft_heating_cooling"][i]["cool_cop"]
    end

    # Find peak heating, cooling, and combined for initial sizing guess
    d[:PeakTons_WSHP_H] = maximum(d[:HeatingThermalLoadKW]) / d[:TON_TO_KW]
    d[:PeakTons_WSHP_C] = maximum(d["cooling_thermal_load_ton"])
    d[:PeakTons_WSHP_GHX] = maximum(d[:HeatingThermalLoadKW] + d[:CoolingThermalLoadKW]) / d[:TON_TO_KW]
    d[:X_init] = d["init_sizing_factor_ft_per_peak_ton"] / d[:METER_TO_FEET] * d[:PeakTons_WSHP_GHX]  # [m]
    
    # Set some intermediate conditions
    d[:N_Series] = 1
    d[:N_Radial] = d[:N_Series]
    d[:N_Vertical] = 50
    d[:RhoCp_Soil] = d[:Rho_Soil] * d[:Cp_Soil]
    d[:DayMin_DST] = 270.0 - d[:DayMin_Surface]
    d[:GPM_GHXPump] = d[:GPMperTon_WSHP] * d[:PeakTons_WSHP_GHX]
    d[:Prated_GHXPump] = d[:WattPerGPM_GHXPump] * 3.6 * d[:GPM_GHXPump]
    d[:LPS_GHXPump] = d[:GPM_GHXPump] / 60 / 264.172 * 1000.0
    d[:Mdot_GHXPump] = d[:GPM_GHXPump] * 60 / 264.172 * d[:Rho_GHXFluid]
    
    # Convert all Dict key strings to symbols which is required for kwargs inputs of InputsStruct
    d = string_dictkeys_tosymbols(d)

    # Report which field is missing
    d = filter_dict_to_match_struct_field_names(d, InputsStruct)
    
    # Pass/return InputsStruct (after ";" means kwargs, "..." => "splat" Dict into individual terms)
    return InputsStruct(;d...) 
end

"""
    string_dictkeys_tosymbols(d::Dict)

Assists in using a Dict as an input to instantiate the struct.

"""
function string_dictkeys_tosymbols(d::Dict)
    d2 = Dict()
    for (k, v) in d
        d2[Symbol(k)] = v
    end
    return d2
end

"""
    filter_dict_to_match_struct_field_names(d::Dict, s::DataType)

Filter the input dict to match the struct field names, and provide a warning if inputs are missing.

"""
function filter_dict_to_match_struct_field_names(d::Dict, s::DataType)
    f = fieldnames(s)
    d2 = Dict()
    for k in f
        if haskey(d, k)
            d2[k] = d[k]
        else
            @warn "inputs.jl: dict is missing InputsStruct field $(k)!"
        end
    end
    return d2
end