using Genie, Genie.Router, Genie.Requests, Genie.Renderer.Json

Genie.config.run_as_server = true

route("/jsonpayload", method = POST) do
  @show jsonpayload()
  @show rawpayload()

  json("Hello $(jsonpayload()["name"])")
end

Genie.startup()