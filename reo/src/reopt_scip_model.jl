using JuMP
using SCIP

function reopt_model(time_limit_seconds::Real)

    REopt = Model(with_optimizer(SCIP.Optimizer, display_verblevel=0, limits_time=time_limit_seconds))
	return REopt

end
