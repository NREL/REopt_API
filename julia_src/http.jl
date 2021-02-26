using HTTP, JSON
include("REopt.jl")

using .REopt

function job(req::HTTP.Request)
    d = JSON.parse(String(req.body))
    # TODO pass through timeout and tolerance
    m = xpress_model(420.0, 0.001)  # TODO add timeout and tolerance to data dict
    results = reopt(m, d)
    # TODO @info run_uuid and status
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