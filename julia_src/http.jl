using HTTP, JSON
include("REopt.jl")

using .REopt

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

function health(req::HTTP.Request)
    return HTTP.Response(200, JSON.json(Dict("Julia-api"=>"healthy!")))
end

# define REST endpoints to dispatch to "service" functions
const ROUTER = HTTP.Router()

HTTP.@register(ROUTER, "POST", "/job", job)
HTTP.@register(ROUTER, "GET", "/health", health)
HTTP.serve(ROUTER, "0.0.0.0", 8081)
# TODO sometimes the server is not ready even though all containers are running?