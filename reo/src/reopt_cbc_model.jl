using JuMP
using Cbc

function reopt_model()
   
    REopt = Model(with_optimizer(Cbc.Optimizer, logLevel=1))
	return REopt

end
