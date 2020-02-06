using JuMP
using Xpress

function reopt_model(MAXTIME)
   
    REopt = direct_model(Xpress.Optimizer(MAXTIME=-MAXTIME))
	return REopt

end
