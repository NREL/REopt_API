using JuMP
using SCIP

function reopt_model(time_limit_seconds::Real, limits_gap::Real)

    REopt = Model(with_optimizer(SCIP.Optimizer, display_verblevel=0, limits_time=time_limit_seconds, limits_gap=limits_gap))
	REopt[:solver_name] = "SCIP"
	REopt[:timeout_sections] = time_limit_seconds
	REopt[:optimality_tolerance] = limits_gap
	return REopt

end
