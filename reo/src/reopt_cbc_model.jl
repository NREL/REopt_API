using JuMP
using Cbc

function reopt_model(seconds::Float64, ratioGap::Float64)
   
    REopt = Model(with_optimizer(Cbc.Optimizer, logLevel=0, seconds=seconds, ratioGap=ratioGap))
	REopt[:solver_name] = "Cbc"
	REopt[:timeout_seconds] = seconds
	REopt[:optimality_tolerance] = ratioGap
	return REopt

end
