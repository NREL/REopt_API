using HTTP, JSON
include("REopt.jl")

using .REopt

function job(req::HTTP.Request)
    d = JSON.parse(String(req.body))
    m = xpress_model(100.0, 0.001)  # TODO add timeout and tolerance to data dict
    results = reopt(m, d)
    # TODO @info run_uuid and status
    return HTTP.Response(200, JSON.json(results))
end

# define REST endpoints to dispatch to "service" functions
const ROUTER = HTTP.Router()

HTTP.@register(ROUTER, "POST", "/job", job)
HTTP.serve(ROUTER, "0.0.0.0", 8081)
# TODO sometimes the server is not ready even though all containers are running?