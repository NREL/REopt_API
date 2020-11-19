using JuMP
using Xpress

function reopt_model(MAXTIME, MIPRELSTOP)
   
    REopt = direct_model(Xpress.Optimizer(MAXTIME=-MAXTIME, MIPRELSTOP=MIPRELSTOP, CUTSTRATEGY = 3, OUTPUTLOG = 0))
	REopt[:solver_name] = "Xpress"
	REopt[:timeout_seconds] = MAXTIME
	REopt[:optimality_tolerance] = MIPRELSTOP
	return REopt

end