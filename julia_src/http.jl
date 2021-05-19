using HTTP, JSON
include("REopt.jl")
include("GHPGHX.jl")

using .REopt
using .GHPGHX

function job(req::HTTP.Request)
    d = JSON.parse(String(req.body))
    timeout = pop!(d, "timeout_seconds")
    tol = pop!(d, "tolerance")
    m = xpress_model(timeout, tol)
    @info "Starting REopt with timeout of $(timeout) seconds..."
    results = reopt(m, d)
    @info "REopt model solved with status $(results["status"])."
    return HTTP.Response(200, JSON.json(results))
end

function ghpghx(req::HTTP.Request)
    inputs_dict = JSON.parse(String(req.body))
    @info "Starting GHPGHX" #with timeout of $(timeout) seconds..."
    results, inputs_params = GHPGHX.ghp_model(inputs_dict)
    # Create a dictionary of the results data needed for REopt
    ghpghx_results = GHPGHX.get_ghpghx_results_for_reopt(results, inputs_params)
    @info "GHPGHX model solved" #with status $(results["status"])."
    return HTTP.Response(200, JSON.json(ghpghx_results))
end

function health(req::HTTP.Request)
    return HTTP.Response(200, JSON.json(Dict("Julia-api"=>"healthy!")))
end

# define REST endpoints to dispatch to "service" functions
const ROUTER = HTTP.Router()

HTTP.@register(ROUTER, "POST", "/job", job)
HTTP.@register(ROUTER, "POST", "/ghpghx", ghpghx)
HTTP.@register(ROUTER, "GET", "/health", health)
HTTP.serve(ROUTER, "0.0.0.0", 8081, reuseaddr=true)
