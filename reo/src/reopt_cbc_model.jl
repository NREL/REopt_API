using JuMP
using Cbc

function reopt_model(seconds::Float64)
   
    REopt = Model(with_optimizer(Cbc.Optimizer, logLevel=0, seconds=seconds))
	return REopt

end
