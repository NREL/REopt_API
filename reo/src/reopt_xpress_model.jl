using JuMP
using Xpress

function reopt_model(MAXTIME, LOGFILE)
   
    REopt = direct_model(Xpress.Optimizer(MAXTIME=-MAXTIME, logfile=LOGFILE))
	return REopt

end
