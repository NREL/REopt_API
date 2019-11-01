#=
reopt:
- Julia version: 1.2
- Author: nlaws
- Date: 2019-11-01
=#
using JuMP
using Xpress


function reopt(data)
function reopt(data; array)
    MAXTIME = data["inputs"]["Scenario"]["timeout_seconds"]
    REopt = direct_model(Xpress.Optimizer(MAXTIME=MAXTIME))
    @objective(REopt, Min, 1)
    optimize!(REopt)
    if termination_status(REopt) == MOI.OPTIMAL
        status = "optimal"
    else
        status = "not optimal"
    end
    data["outputs"]["Scenario"]["status"] = status
    return data
end