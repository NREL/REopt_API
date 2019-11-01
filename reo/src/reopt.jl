#=
reopt:
- Julia version: 1.2
- Author: nlaws
- Date: 2019-11-01
=#


function reopt(data)
   data["outputs"]["Scenario"]["status"] = "optimal"
   return data
end