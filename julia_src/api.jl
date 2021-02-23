using Genie, Genie.Router, Genie.Requests, Genie.Renderer.Json

route("/jsonpayload", method = POST) do
  @show jsonpayload()
  @show rawpayload()

  json("Hello $(jsonpayload()["name"])")
end

up()