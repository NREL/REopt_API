using JuMP
using Cbc

function reopt_model(seconds::Float64, ratioGap::Float64)
   
    REopt = Model(with_optimizer(Cbc.Optimizer, logLevel=0, seconds=seconds, ratioGap=ratioGap))
	REopt[:solver_name] = "Cbc"
	REopt[:timeout_sections] = seconds
	REopt[:optimality_tolerance] = MIPRELSTOP
	return REopt

end
