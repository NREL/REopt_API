using JuMP
using SCIP

function reopt_model()

    REopt = Model(with_optimizer(SCIP.Optimizer, display_verblevel=0))
	return REopt

end
