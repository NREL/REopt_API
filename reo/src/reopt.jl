#=
reopt:
- Julia version: 1.2
- Author: nlaws
- Date: 2019-11-01
=#
using JuMP
using Xpress


function reopt(data)
   data["outputs"]["Scenario"]["status"] = "optimal"
    MAXTIME = data["inputs"]["Scenario"]["timeout_seconds"]
    REopt = direct_model(Xpress.Optimizer(MAXTIME=MAXTIME))
    @objective(REopt, Min, 1)
    optimize!(REopt)
    return data
end