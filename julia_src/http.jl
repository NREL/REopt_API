using HTTP, JSON
using JuMP, Xpress
include("REopt.jl")
import REoptLite

function job(req::HTTP.Request)
    d = JSON.parse(String(req.body))
    timeout = pop!(d, "timeout_seconds")
    tol = pop!(d, "tolerance")
    m = REopt.xpress_model(timeout, tol)
    @info "Starting REopt with timeout of $(timeout) seconds..."
	error_response = Dict()
	results = Dict()
	try
    	results = REopt.reopt(m, d)
	catch e
		@error "Something went wrong in the Julia code!" exception=(e, catch_backtrace())
		error_response["error"] = sprint(showerror, e)
	end
	finalize(backend(m))
	GC.gc()
	if isempty(error_response)
    	@info "REopt model solved with status $(results["status"])."
    	return HTTP.Response(200, JSON.json(results))
	else
		@info "An error occured in the Julia code."
		return HTTP.Response(500, JSON.json(error_response))
	end
end

function reopt(req::HTTP.Request)
    d = JSON.parse(String(req.body))
	settings = d["Settings"]
	timeout_seconds = -pop!(settings, "timeout_seconds")
	optimality_tolerance = pop!(settings, "optimality_tolerance")
	ms = nothing
	if get(settings, "run_bau", true)
		m1 = direct_model(
			Xpress.Optimizer(
				MAXTIME = timeout_seconds,
				MIPRELSTOP = optimality_tolerance,
				OUTPUTLOG = 0
			)
		)
		m2 = direct_model(
			Xpress.Optimizer(
				MAXTIME = timeout_seconds,
				MIPRELSTOP = optimality_tolerance,
				OUTPUTLOG = 0
			)
		)
		ms = [m1, m2]
	else
		ms = direct_model(
			Xpress.Optimizer(
				MAXTIME = timeout_seconds,
				MIPRELSTOP = optimality_tolerance,
				OUTPUTLOG = 0
			)
		)
	end
    @info "Starting REopt..."
    error_response = Dict()
    results = Dict()
    try
        results = REoptLite.run_reopt(ms, d)
    catch e
        @error "Something went wrong in the Julia code!" exception=(e, catch_backtrace())
        error_response["error"] = sprint(showerror, e)
    end
	if ms <: AbstractArray
		finalize(backend(ms[1]))
		finalize(backend(ms[2]))
	else
		finalize(backend(ms))
	end
    GC.gc()
    if isempty(error_response)
        @info "REopt model solved with status $(results["status"])."
        return HTTP.Response(200, JSON.json(results))
    else
        @info "An error occured in the Julia code."
        return HTTP.Response(500, JSON.json(error_response))
    end
end

function health(req::HTTP.Request)
    return HTTP.Response(200, JSON.json(Dict("Julia-api"=>"healthy!")))
end

# define REST endpoints to dispatch to "service" functions
const ROUTER = HTTP.Router()

HTTP.@register(ROUTER, "POST", "/job", job)
HTTP.@register(ROUTER, "POST", "/reopt", reopt)
HTTP.@register(ROUTER, "GET", "/health", health)
HTTP.serve(ROUTER, "0.0.0.0", 8081, reuseaddr=true)
