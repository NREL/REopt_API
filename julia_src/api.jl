using Genie, Genie.Router, Genie.Requests, Genie.Renderer.Json
include("REopt.jl")
using .REopt

Genie.config.run_as_server = true

route("/jsonpayload", method = POST) do
  data = jsonpayload() # Dict{String,Any}
  m = xpress_model(100.0, 0.001)  # TODO add timeout and tolerance to data dict
  results = reopt(m, data)
"""
1. json to dict?
2. get results
3. return

...

multi thread bau scenario
"""
  json(results)
end

Genie.startup(8081)