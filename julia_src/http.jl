using HTTP, JSON, JuMP
using HiGHS, Cbc, SCIP
using GhpGhx
import REopt as reoptjl  # For REopt.jl, needed because we still have local REopt.jl module for V1/V2
using DotEnv
DotEnv.load!()

const test_nrel_developer_api_key = ENV["NREL_DEVELOPER_API_KEY"]

include("os_solvers.jl")

# Load Xpress only if it is installed, as indicated by ENV["XPRESS_INSTALLED"]="True"
xpress_installed = get(ENV, "XPRESS_INSTALLED", "False")
if xpress_installed == "True"
    using Xpress
    include("REopt.jl")
    include("xpress_functions.jl")  # Includes both get_solver_model(XpressModel) and job endpoint for v1/v2
else
    @warn "Xpress solver is not setup, so only Settings.solver_choice = 'HiGHS', 'Cbc', or 'SCIP' options are available."
end

function reopt(req::HTTP.Request)
    d = JSON.parse(String(req.body))
	error_response = Dict()
    if !isempty(get(d, "api_key", ""))
        ENV["NREL_DEVELOPER_API_KEY"] = pop!(d, "api_key")
    else
        ENV["NREL_DEVELOPER_API_KEY"] = test_nrel_developer_api_key
        delete!(d, "api_key")
    end
    settings = d["Settings"]
    solver_name = get(settings, "solver_name", "HiGHS")    
    if solver_name == "Xpress" && !(xpress_installed=="True")
        solver_name = "HiGHS"
        @warn "Changing solver_name from Xpress to $solver_name because Xpress is not installed. Next time 
                Specify Settings.solver_name = 'HiGHS' or 'Cbc' or 'SCIP'"
    end
	timeout_seconds = pop!(settings, "timeout_seconds")
	optimality_tolerance = pop!(settings, "optimality_tolerance")
    solver_attributes = SolverAttributes(timeout_seconds, optimality_tolerance)    
	run_bau = pop!(settings, "run_bau")
	ms = nothing
	if run_bau
		m1 = get_solver_model(get_solver_model_type(solver_name), solver_attributes)
		m2 = get_solver_model(get_solver_model_type(solver_name), solver_attributes)
		ms = [m1, m2]
	else
		ms = get_solver_model(get_solver_model_type(solver_name), solver_attributes)
	end
	@info "Starting REopt with $(solver_name) solver..."
    results = Dict()
	inputs_with_defaults_set_in_julia = Dict()
	model_inputs = nothing
	# Catch handled/unhandled exceptions in data pre-processing, JuMP setup
	try
		model_inputs = reoptjl.REoptInputs(d)
	catch e
		@error "Something went wrong during REopt inputs processing!" exception=(e, catch_backtrace())
        error_response["error"] = sprint(showerror, e)
	end
	
	if isa(model_inputs, Dict) && model_inputs["status"] == "error"
		results = model_inputs
	else
		# Catch handled/unhandled exceptions in optimization
		try
			results = reoptjl.run_reopt(ms, model_inputs)
			inputs_with_defaults_from_easiur = [
				:NOx_grid_cost_per_tonne, :SO2_grid_cost_per_tonne, :PM25_grid_cost_per_tonne, 
				:NOx_onsite_fuelburn_cost_per_tonne, :SO2_onsite_fuelburn_cost_per_tonne, :PM25_onsite_fuelburn_cost_per_tonne,
				:NOx_cost_escalation_rate_fraction, :SO2_cost_escalation_rate_fraction, :PM25_cost_escalation_rate_fraction
			]
			inputs_with_defaults_from_avert_or_cambium = [
				:emissions_factor_series_lb_CO2_per_kwh, :emissions_factor_series_lb_NOx_per_kwh,
				:emissions_factor_series_lb_SO2_per_kwh, :emissions_factor_series_lb_PM25_per_kwh
			]
            if haskey(d, "CHP")
                inputs_with_defaults_from_chp = [
                    :installed_cost_per_kw, :tech_sizes_for_cost_curve, :om_cost_per_kwh, 
                    :electric_efficiency_full_load, :thermal_efficiency_full_load, :min_allowable_kw,
                    :cooling_thermal_factor, :min_turn_down_fraction, :unavailability_periods, :max_kw,
                    :size_class, :electric_efficiency_half_load, :thermal_efficiency_half_load
                ]
                chp_dict = Dict(key=>getfield(model_inputs.s.chp, key) for key in inputs_with_defaults_from_chp)
            else
                chp_dict = Dict()
            end
			if haskey(d, "SteamTurbine")
				inputs_with_defaults_from_steamturbine = [
					:size_class, :gearbox_generator_efficiency, :isentropic_efficiency, 
					:inlet_steam_pressure_psig, :inlet_steam_temperature_degF, :installed_cost_per_kw, :om_cost_per_kwh, 
					:outlet_steam_pressure_psig, :net_to_gross_electric_ratio, :electric_produced_to_thermal_consumed_ratio,
                    :thermal_produced_to_thermal_consumed_ratio
				]
				steamturbine_dict = Dict(key=>getfield(model_inputs.s.steam_turbine, key) for key in inputs_with_defaults_from_steamturbine)
			else
				steamturbine_dict = Dict()
			end
            if haskey(d, "GHP")
                inputs_with_defaults_from_ghp = [
                    :space_heating_efficiency_thermal_factor,
                    :cooling_efficiency_thermal_factor
                ]
                ghp_dict = Dict(key=>getfield(model_inputs.s.ghp_option_list[1], key) for key in inputs_with_defaults_from_ghp)
            else
                ghp_dict = Dict()
            end
            if haskey(d, "ASHPSpaceHeater")
                inputs_with_defaults_from_ashp = [
                    :max_ton, :installed_cost_per_ton, :om_cost_per_ton, 
                    :macrs_option_years, :macrs_bonus_fraction, :can_supply_steam_turbine,
                    :can_serve_process_heat, :can_serve_dhw, :can_serve_space_heating, :can_serve_cooling,
                    :back_up_temp_threshold_degF, :sizing_factor, :heating_cop_reference, :heating_cf_reference,
                    :heating_reference_temps_degF, :cooling_cop_reference, :cooling_cf_reference, 
                    :cooling_reference_temps_degF
                ]
                ashp_dict = Dict(key=>getfield(model_inputs.s.ashp, key) for key in inputs_with_defaults_from_ashp)
            else
                ashp_dict = Dict()
            end
            if haskey(d, "ASHPWaterHeater")
                inputs_with_defaults_from_ashp_wh = [
                    :max_ton, :installed_cost_per_ton, :om_cost_per_ton, 
                    :macrs_option_years, :macrs_bonus_fraction, :can_supply_steam_turbine,
                    :can_serve_process_heat, :can_serve_dhw, :can_serve_space_heating, :can_serve_cooling,
                    :back_up_temp_threshold_degF, :sizing_factor, :heating_cop_reference, :heating_cf_reference,
                    :heating_reference_temps_degF
                ]
                ashp_wh_dict = Dict(key=>getfield(model_inputs.s.ashp_wh, key) for key in inputs_with_defaults_from_ashp_wh)
            else
                ashp_wh_dict = Dict()
            end
            if haskey(d, "CoolingLoad")
                inputs_with_defaults_from_chiller = [
                    :cop
                ]
                chiller_dict = Dict(key=>getfield(model_inputs.s.existing_chiller, key) for key in inputs_with_defaults_from_chiller)
            else
                chiller_dict = Dict()
            end
            if !isnothing(model_inputs.s.site.outdoor_air_temperature_degF)
                site_dict = Dict(:outdoor_air_temperature_degF => model_inputs.s.site.outdoor_air_temperature_degF)
            else
                site_dict = Dict()
            end
			inputs_with_defaults_set_in_julia = Dict(
				"Financial" => Dict(key=>getfield(model_inputs.s.financial, key) for key in inputs_with_defaults_from_easiur),
				"ElectricUtility" => Dict(key=>getfield(model_inputs.s.electric_utility, key) for key in inputs_with_defaults_from_avert_or_cambium),
                "Site" => site_dict,
                "CHP" => chp_dict,
				"SteamTurbine" => steamturbine_dict,
                "GHP" => ghp_dict,
                "ExistingChiller" => chiller_dict,
                "ASHPSpaceHeater" => ashp_dict,
                "ASHPWaterHeater" => ashp_wh_dict
			)
		catch e
			@error "Something went wrong in REopt optimization!" exception=(e, catch_backtrace())
			error_response["error"] = sprint(showerror, e) # append instead of rewrite?
		end
	end
    
	if typeof(ms) <: AbstractArray
		finalize(backend(ms[1]))
		finalize(backend(ms[2]))
		empty!(ms[1])
		empty!(ms[2])
	else
		finalize(backend(ms))
		empty!(ms)
	end
    GC.gc()

    if isempty(error_response)
        @info "REopt model solved with status $(results["status"])."
        response = Dict(
            "results" => results,
            "reopt_version" => string(pkgversion(reoptjl))
        )
		if results["status"] == "error"
			if !isempty(inputs_with_defaults_set_in_julia)
				response["inputs_with_defaults_set_in_julia"] = inputs_with_defaults_set_in_julia
			end
			return HTTP.Response(400, JSON.json(response))
		else
            response["inputs_with_defaults_set_in_julia"] = inputs_with_defaults_set_in_julia
			return HTTP.Response(200, JSON.json(response))
		end
    else
        @info "An error occured in the Julia code."
        error_response["reopt_version"] = string(pkgversion(reoptjl))
        return HTTP.Response(500, JSON.json(error_response))
    end
end

function erp(req::HTTP.Request)
	erp_inputs = JSON.parse(String(req.body))

    @info "Starting ERP..."
    error_response = Dict()
    results = Dict()
    try
		results = reoptjl.backup_reliability(erp_inputs)
        results["reopt_version"] = string(pkgversion(reoptjl))
    catch e
        @error "Something went wrong in the ERP Julia code!" exception=(e, catch_backtrace())
        error_response["error"] = sprint(showerror, e)
        error_response["reopt_version"] = string(pkgversion(reoptjl))
    end
    GC.gc()
    if isempty(error_response)
        @info "ERP ran successfully."
        return HTTP.Response(200, JSON.json(results))
    else
        return HTTP.Response(500, JSON.json(error_response))
    end
end

function ghpghx(req::HTTP.Request)
    inputs_dict = JSON.parse(String(req.body))
    pop!(inputs_dict, "status")
    @info "Starting GHPGHX"
    results, inputs_params = GhpGhx.ghp_model(inputs_dict)
    # Create a dictionary of the results data needed for REopt
    ghpghx_results = GhpGhx.get_results_for_reopt(results, inputs_params)
    @info "GHPGHX model solved"
    return HTTP.Response(200, JSON.json(ghpghx_results))
end

function chp_defaults(req::HTTP.Request)
    d = JSON.parse(String(req.body))
    string_vals = ["hot_water_or_steam", "prime_mover"]
    float_vals = ["avg_boiler_fuel_load_mmbtu_per_hour",
                "boiler_efficiency",
                "avg_electric_load_kw",
                "max_electric_load_kw",
                "thermal_efficiency"]
    int_vals = ["size_class"]
    bool_vals = ["is_electric_only"]
    all_vals = vcat(string_vals, float_vals, int_vals, bool_vals)
    # Process .json inputs and convert to correct type if needed
    for k in all_vals
        if !haskey(d, k)
            if !(k == "thermal_efficiency")  # thermal_efficiency is of type Float64 (incl NaN), so it can't be "nothing"
                d[k] = nothing
            end
        elseif !isnothing(d[k])
            if k in float_vals && typeof(d[k]) == String
                d[k] = parse(Float64, d[k])
            elseif k in int_vals && typeof(d[k]) == String
                d[k] = parse(Int64, d[k])
            elseif k in bool_vals && typeof(d[k]) == String
                d[k] = parse(Bool, d[k])
            end
        end
    end

    @info "Getting CHP defaults..."
    data = Dict()
    error_response = Dict()
    try
        d_symb = reoptjl.dictkeys_tosymbols(d)
        if haskey(d_symb, :prime_mover) && d_symb[:prime_mover] == "steam_turbine"
            # delete!(d_symb, :prime_mover)
            data = reoptjl.get_steam_turbine_defaults_size_class(;
                    avg_boiler_fuel_load_mmbtu_per_hour=get(d_symb, :avg_boiler_fuel_load_mmbtu_per_hour, nothing),
                    size_class=get(d_symb, :size_class, nothing))
        else
            data = reoptjl.get_chp_defaults_prime_mover_size_class(;d_symb...)
        end
    catch e
        @error "Something went wrong in the chp_defaults endpoint" exception=(e, catch_backtrace())
        error_response["error"] = sprint(showerror, e)
    end
    if isempty(error_response)
        @info "CHP defaults determined."
		response = data
        return HTTP.Response(200, JSON.json(response))
    else
        @info "An error occured in the chp_defaults endpoint"
        return HTTP.Response(500, JSON.json(error_response))
    end
end

function absorption_chiller_defaults(req::HTTP.Request)
	d = JSON.parse(String(req.body))
    keys = ["thermal_consumption_hot_water_or_steam", 
            "chp_prime_mover",
            "boiler_type",
            "load_max_tons"]
    # Process .json inputs and convert to correct type if needed
    for k in keys
        if !haskey(d, k)
            d[k] = nothing
        elseif !isnothing(d[k])
            if k in ["load_max_tons"] && typeof(d[k]) == String
                d[k] = parse(Float64, d[k])
            elseif k in ["load_max_tons"] && typeof(d[k]) == Int64
                d[k] = convert(Float64, d[k])
            end
        end
    end

    @info "Getting AbsorptionChiller defaults..."
    data = Dict()
    error_response = Dict()
    try
        data = reoptjl.get_absorption_chiller_defaults(;
			thermal_consumption_hot_water_or_steam=d["thermal_consumption_hot_water_or_steam"],
			chp_prime_mover=d["chp_prime_mover"],
			boiler_type=d["boiler_type"],
			load_max_tons=d["load_max_tons"])
    catch e
        @error "Something went wrong in the absorption_chiller_defaults" exception=(e, catch_backtrace())
        error_response["error"] = sprint(showerror, e)
    end
    if isempty(error_response)
        @info "AbsorptionChiller defaults determined."
		response = data
        return HTTP.Response(200, JSON.json(response))
    else
        @info "An error occured in the absorption_chiller_defaults endpoint"
        return HTTP.Response(500, JSON.json(error_response))
    end
end

function avert_emissions_profile(req::HTTP.Request)
    d = JSON.parse(String(req.body))
    @info "Getting AVERT emissions profiles..."
    data = Dict()
    error_response = Dict()
    try
		latitude = typeof(d["latitude"]) == String ? parse(Float64, d["latitude"]) : d["latitude"]
		longitude = typeof(d["longitude"]) == String ? parse(Float64, d["longitude"]) : d["longitude"]
        load_year = typeof(d["load_year"]) == String ? parse(Int, d["load_year"]) : d["load_year"]

        data = reoptjl.avert_emissions_profiles(;latitude=latitude, longitude=longitude, time_steps_per_hour=1, load_year=load_year)
        if haskey(data, "error")
            @info "An error occured getting the AVERT emissions data"
            return HTTP.Response(400, JSON.json(data))
        end
    catch e
        @error "Something went wrong getting the AVERT emissions data" exception=(e, catch_backtrace())
        error_response["error"] = sprint(showerror, e)
        return HTTP.Response(500, JSON.json(error_response))
    end
    @info "AVERT emissions profile determined."
    return HTTP.Response(200, JSON.json(data))
end

function cambium_emissions_profile(req::HTTP.Request)
    d = JSON.parse(String(req.body))
    @info "Getting Cambium CO2 emissions profile..."
    data = Dict()
    error_response = Dict()
    try
        latitude = typeof(d["latitude"]) == String ? parse(Float64, d["latitude"]) : d["latitude"]
		longitude = typeof(d["longitude"]) == String ? parse(Float64, d["longitude"]) : d["longitude"]
        start_year = typeof(d["start_year"]) == String ? parse(Int, d["start_year"]) : d["start_year"]
        lifetime = typeof(d["lifetime"]) == String ? parse(Int, d["lifetime"]) : d["lifetime"]
        load_year = typeof(d["load_year"]) == String ? parse(Int, d["load_year"]) : d["load_year"]

        data = reoptjl.cambium_emissions_profile(;scenario= d["scenario"],
                                                location_type = d["location_type"],  
                                                latitude=latitude, 
                                                longitude=longitude, 
                                                start_year=start_year,
                                                lifetime=lifetime,
                                                metric_col=d["metric_col"],
                                                grid_level=d["grid_level"],
                                                time_steps_per_hour=1, 
                                                load_year=load_year
                                                )
        if haskey(data, "error")
            @info "An error occured getting the Cambium emissions data"
            return HTTP.Response(400, JSON.json(data))
        end
    catch e
        @error "Something went wrong getting the Cambium emissions data" exception=(e, catch_backtrace())
        error_response["error"] = sprint(showerror, e)
        return HTTP.Response(500, JSON.json(error_response))
    end
    @info "Cambium emissions profile determined."
    return HTTP.Response(200, JSON.json(data))
end

function easiur_costs(req::HTTP.Request)
    d = JSON.parse(String(req.body))
    @info "Getting EASIUR health emissions cost data..."
    data = Dict()
    error_response = Dict()
    try
		latitude = typeof(d["latitude"]) == String ? parse(Float64, d["latitude"]) : d["latitude"]
		longitude = typeof(d["longitude"]) == String ? parse(Float64, d["longitude"]) : d["longitude"]
		inflation = typeof(d["inflation"]) == String ? parse(Float64, d["inflation"]) : d["inflation"]
        data = reoptjl.easiur_data(;latitude=latitude, longitude=longitude, inflation=inflation)
        if haskey(data, "error")
            @info "An error occured getting the health emissions cost data"
            return HTTP.Response(400, JSON.json(data))
        end
    catch e
        @error "Something went wrong getting the health emissions cost data" exception=(e, catch_backtrace())
        error_response["error"] = sprint(showerror, e)
        return HTTP.Response(500, JSON.json(error_response))
    end
    @info "Health emissions cost data determined."
    return HTTP.Response(200, JSON.json(data))
end

function simulated_load(req::HTTP.Request)
    d = JSON.parse(String(req.body))

    # Arrays in d are being parsed as type Vector{Any} instead of fixed type Vector{String or <:Real} without conversion
    for key in ["doe_reference_name", "cooling_doe_ref_name"]
        if key in keys(d) && typeof(d[key]) <: Vector{}
            d[key] = convert(Vector{String}, d[key])
        end
    end

    # Convert vectors which come in as Vector{Any} to Vector{Float} (within Vector{<:Real})
    vector_types = ["percent_share", "cooling_pct_share", "monthly_totals_kwh", "monthly_mmbtu", 
                    "monthly_tonhour", "addressable_load_fraction"]
    for key in vector_types
        if key in keys(d) && typeof(d[key]) <: Vector{}
            d[key] = convert(Vector{Real}, d[key])
        elseif key in keys(d) && key == "addressable_load_fraction"
            # Scalar version of input, convert Any to Real
            d[key] = convert(Real, d[key])
        end
    end 

    @info "Getting CRB Loads..."
    data = Dict()
    error_response = Dict()
    try
        data = reoptjl.simulated_load(d)
    catch e
        @error "Something went wrong in the simulated_load" exception=(e, catch_backtrace())
        error_response["error"] = sprint(showerror, e)
    end
    if isempty(error_response)
        @info "CRB Loads determined."
		response = data
        return HTTP.Response(200, JSON.json(response))
    else
        @info "An error occured in the simulated_load endpoint"
        return HTTP.Response(500, JSON.json(error_response))
    end
end

function ghp_efficiency_thermal_factors(req::HTTP.Request)
    d = JSON.parse(String(req.body))

    @info "Getting ghp_efficiency_thermal_factors..."
    # The REopt.jl function assumes the REopt input dictionary is being mutated, so put in that form
    data = Dict([("Site", Dict([("latitude", d["latitude"]), ("longitude", d["longitude"])])),
                 ("SpaceHeatingLoad", Dict([("doe_reference_name", d["doe_reference_name"])])),
                 ("CoolingLoad", Dict([("doe_reference_name", d["doe_reference_name"])])),
                 ("GHP", Dict())])
    error_response = Dict()
    nearest_city = ""
    climate_zone = ""
    try
        for factor in ["space_heating", "cooling"]
            nearest_city, climate_zone = reoptjl.assign_thermal_factor!(data, factor)
        end        
    catch e
        @error "Something went wrong in the ghp_efficiency_thermal_factors" exception=(e, catch_backtrace())
        error_response["error"] = sprint(showerror, e)
    end
    if isempty(error_response)
        @info "ghp_efficiency_thermal_factors determined."
		response = Dict([("doe_reference_name", d["doe_reference_name"]),
                            ("nearest_city", nearest_city),
                            ("climate_zone", climate_zone), 
                          data["GHP"]...])
        return HTTP.Response(200, JSON.json(response))
    else
        @info "An error occured in the ghp_efficiency_thermal_factors endpoint"
        return HTTP.Response(500, JSON.json(error_response))
    end
end

function ground_conductivity(req::HTTP.Request)
    d = JSON.parse(String(req.body))

    @info "Getting ground_conductivity..."
    error_response = Dict()
    nearest_city = ""
    climate_zone = ""
    ground_thermal_conductivity = 0.01
    try
        nearest_city, climate_zone = reoptjl.find_ashrae_zone_city(d["latitude"], d["longitude"], get_zone=true)    
        ground_thermal_conductivity = GhpGhx.ground_k_by_climate_zone[climate_zone]
    catch e
        @error "Something went wrong in the ground_conductivity" exception=(e, catch_backtrace())
        error_response["error"] = sprint(showerror, e)
    end
    if isempty(error_response)
        @info "ground_conductivity determined."
		response = Dict([("climate_zone", climate_zone),
                         ("nearest_city", nearest_city),
                         ("thermal_conductivity", ground_thermal_conductivity)])
        return HTTP.Response(200, JSON.json(response))
    else
        @info "An error occured in the ground_conductivity endpoint"
        return HTTP.Response(500, JSON.json(error_response))
    end
end

function health(req::HTTP.Request)
    return HTTP.Response(200, JSON.json(Dict("Julia-api"=>"healthy!")))
end

function get_existing_chiller_default_cop(req::HTTP.Request)
    d = JSON.parse(String(req.body))
    chiller_cop = nothing

    for key in ["existing_chiller_max_thermal_factor_on_peak_load","max_load_kw","max_load_kw_thermal"]
        if !(key in keys(d))
            d[key] = nothing
        end
    end
    
    @info "Getting default existing chiller COP..."
    error_response = Dict()
    try
        # Have to specify "REopt.get_existing..." because http function has the same name
        chiller_cop = reoptjl.get_existing_chiller_default_cop(;
                existing_chiller_max_thermal_factor_on_peak_load=d["existing_chiller_max_thermal_factor_on_peak_load"], 
                max_load_kw=d["max_load_kw"],
                max_load_kw_thermal=d["max_load_kw_thermal"])      
    catch e
        @error "Something went wrong in the get_existing_chiller_default_cop" exception=(e, catch_backtrace())
        error_response["error"] = sprint(showerror, e)
    end
    if isempty(error_response)
        @info("Default existing chiller COP detected.")
        response = Dict([("existing_chiller_cop", chiller_cop)])
        return HTTP.Response(200, JSON.json(response))
    else
        @info "An error occured in the get_existing_chiller_default_cop endpoint"
        return HTTP.Response(500, JSON.json(error_response))
    end
end    

function get_ashp_defaults(req::HTTP.Request)
    d = JSON.parse(String(req.body))
    defaults = nothing

    if !("load_served" in keys(d))
        @info("ASHP load served not provided. Using default of SpaceHeating.")
        d["load_served"] = "SpaceHeating"
    end 
    if !("force_into_system" in keys(d))
        @info("ASHP force_into_system not provided. Using default of false.")
        d["force_into_system"] = false
    end 
    
    @info "Getting default ASHP attributes..."
    error_response = Dict()
    try
        # Have to specify "REopt.get_existing..." because http function has the same name
        defaults = reoptjl.get_ashp_defaults(d["load_served"],d["force_into_system"])      
    catch e
        @error "Something went wrong in the get_ashp_defaults endpoint" exception=(e, catch_backtrace())
        error_response["error"] = sprint(showerror, e)
    end
    if isempty(error_response)
        @info("ASHP defaults obtained.")
        response = defaults
        return HTTP.Response(200, JSON.json(response))
    else
        @info "An error occured in the get_ashp_defaults endpoint"
        return HTTP.Response(500, JSON.json(error_response))
    end
end


function job_no_xpress(req::HTTP.Request)
    error_response = Dict("error" => "V1 and V2 not available without Xpress installation.")
    return HTTP.Response(500, JSON.json(error_response))
end

# define REST endpoints to dispatch to "service" functions
const ROUTER = HTTP.Router()

if xpress_installed == "True"
    HTTP.register!(ROUTER, "POST", "/job", job)
else
    HTTP.register!(ROUTER, "POST", "/job", job_no_xpress)
end
HTTP.register!(ROUTER, "POST", "/reopt", reopt)
HTTP.register!(ROUTER, "POST", "/erp", erp)
HTTP.register!(ROUTER, "POST", "/ghpghx", ghpghx)
HTTP.register!(ROUTER, "GET", "/chp_defaults", chp_defaults)
HTTP.register!(ROUTER, "GET", "/avert_emissions_profile", avert_emissions_profile)
HTTP.register!(ROUTER, "GET", "/cambium_emissions_profile", cambium_emissions_profile)
HTTP.register!(ROUTER, "GET", "/easiur_costs", easiur_costs)
HTTP.register!(ROUTER, "GET", "/simulated_load", simulated_load)
HTTP.register!(ROUTER, "GET", "/absorption_chiller_defaults", absorption_chiller_defaults)
HTTP.register!(ROUTER, "GET", "/ghp_efficiency_thermal_factors", ghp_efficiency_thermal_factors)
HTTP.register!(ROUTER, "GET", "/ground_conductivity", ground_conductivity)
HTTP.register!(ROUTER, "GET", "/health", health)
HTTP.register!(ROUTER, "GET", "/get_existing_chiller_default_cop", get_existing_chiller_default_cop)
HTTP.register!(ROUTER, "GET", "/get_ashp_defaults", get_ashp_defaults)
HTTP.serve(ROUTER, "0.0.0.0", 8081, reuseaddr=true)
