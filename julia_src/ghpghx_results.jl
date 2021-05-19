
Base.@kwdef mutable struct ResultsStruct
    # These get modified by the function below
    # Some of these values are required inputs, those that do not have "= value"
    X_Now::Array{Float64, 1}
    FX_Now::Array{Float64, 1}
    N_Bores::Array{Int64, 1}
    N_Bores_Final::Int64 = 0
    FX_Final::Float64 = 0.0
    Length_Boreholes::Float64 = 0.0
    StorageVolume::Float64 = 0.0
    Depth_DST::Float64 = 0.0
    Mdot_Borehole::Float64 = 0.0
    Radius_Field::Float64 = 0.0
    N_Circuits::Int64 = 0
    L_Circuit::Float64 = 0.0
    Mass_Circuit::Float64 = 0.0

    # These get reset each sizing iteration
    Tmax_GHX::Float64 = -9.99e20
    Tmin_GHX::Float64 = 9.99e20
    Power_GHXPump::Float64 = 0.0
    Qfluid_GHXPump::Float64 = 0.0
    Power_WSHP_H::Float64 = 0.0
    Power_WSHP_C::Float64 = 0.0
    LoadMet_WSHP_H::Float64 = 0.0
    LoadMet_WSHP_C::Float64 = 0.0
    Q_Rejected_Total::Float64 = 0.0
    Q_Absorbed_Total::Float64 = 0.0
    Q_GHX_Net::Float64 = 0.0
    Q_GHX_In::Float64 = 0.0
    Q_GHX_Top::Float64 = 0.0
    Q_GHX_Sides::Float64 = 0.0
    Q_GHX_Bottom::Float64 = 0.0
    Q_GHX_Stored::Float64 = 0.0
    Qf_GHX_Stored::Float64 = 0.0

    # Array results
    total_hours::Int64  # Required argument to be passed by InputsStruct
    P_GHXPump_Hourly::Array{Float64, 1} = zeros(total_hours)
    P_WSHPh_Hourly::Array{Float64, 1} = zeros(total_hours)
    P_WSHPc_Hourly::Array{Float64, 1} = zeros(total_hours)
    Qh_Hourly::Array{Float64, 1} = zeros(total_hours)
    Qc_Hourly::Array{Float64, 1} = zeros(total_hours)  # And Q_Heat/Q_Cool is the input kJ/hr
    EWT::Array{Float64, 1} = zeros(total_hours)
end

function init_sizing!(r::ResultsStruct, p::InputsStruct, size_iter::Int64)
    #Changes each sizing iteration
    r.N_Bores[size_iter] = floor(r.X_Now[size_iter] / p.Depth_Bores) + 1
    r.Length_Boreholes = r.X_Now[size_iter] / r.N_Bores[size_iter]
    if p.SpacingType == 1
        r.StorageVolume = r.Length_Boreholes * r.N_Bores[size_iter] * pi * (p.BoreSpacing * 0.525)^2
    else
        r.StorageVolume = p.BoreSpacing^2 * r.Length_Boreholes * r.N_Bores[size_iter]
    end
    r.Depth_DST = 1.5 * r.Length_Boreholes
    r.Mdot_Borehole = p.Mdot_GHXPump / r.N_Bores[size_iter] * p.N_Series
    r.Radius_Field = (r.StorageVolume / (pi * r.Length_Boreholes))^0.5
    r.N_Circuits = r.N_Bores[size_iter] / p.N_Series
    r.L_Circuit = 2.0 * p.N_Series * r.Length_Boreholes + (p.N_Series - 1) / p.N_Series * r.Radius_Field
    r.Mass_Circuit = r.L_Circuit * pi * p.Ri_Pipe^2 * p.Rho_GHXFluid
    nothing
end

# Extract the required results for REopt average hourly
function get_ghpghx_results_for_reopt(r::ResultsStruct, p::InputsStruct)
    results_dict = Dict{Any,Any}()
    results_dict["number_of_boreholes"] = r.N_Bores_Final
    results_dict["length_boreholes_ft"] = r.Length_Boreholes
    results_dict["yearly_heating_heatpump_electric_consumption_series_kw"] = zeros(8760)
    results_dict["yearly_cooling_heatpump_electric_consumption_series_kw"] = zeros(8760)
    results_dict["yearly_ghx_pump_electric_consumption_series_kw"] = zeros(8760)
    # Get average electric consumption
    for yr in 1:p.simulation_years
        results_dict["yearly_heating_heatpump_electric_consumption_series_kw"] += r.P_WSHPh_Hourly[(yr-1)*8760+1:yr*8760] / p.simulation_years
        results_dict["yearly_cooling_heatpump_electric_consumption_series_kw"] += r.P_WSHPc_Hourly[(yr-1)*8760+1:yr*8760] / p.simulation_years
        results_dict["yearly_ghx_pump_electric_consumption_series_kw"] = r.P_GHXPump_Hourly[(yr-1)*8760+1:yr*8760] / p.simulation_years
    end
    results_dict["ewt_error"] = r.FX_Final
    return results_dict
end
