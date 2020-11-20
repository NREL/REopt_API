using JuMP
using Xpress

function reopt_model(MAXTIME, MIPRELSTOP, CUTSTRATEGY)
   
    REopt = direct_model(Xpress.Optimizer(MAXTIME=-MAXTIME, MIPRELSTOP=MIPRELSTOP, CUTSTRATEGY=CUTSTRATEGY, OUTPUTLOG = 0))
	REopt[:solver_name] = "Xpress"
	REopt[:timeout_seconds] = MAXTIME
	REopt[:optimality_tolerance] = MIPRELSTOP
	REopt[:cutstrategy] = CUTSTRATEGY
	return REopt

end