using JuMP
using SCIP

function reopt_model(time_limit_seconds::Real, limits_gap::Real)

    m = Model(with_optimizer(SCIP.Optimizer, display_verblevel=0, limits_time=time_limit_seconds, limits_gap=limits_gap))
	m[:solver_name] = "SCIP"
	m[:timeout_seconds] = time_limit_seconds
	m[:optimality_tolerance] = limits_gap
	return m

end
