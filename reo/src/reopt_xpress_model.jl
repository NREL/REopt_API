using JuMP
using Xpress

function reopt_model(MAXTIME, MIPRELSTOP)
   
    REopt = direct_model(Xpress.Optimizer(MAXTIME=-MAXTIME, MIPRELSTOP=MIPRELSTOP, OUTPUTLOG = 0))
	REopt[:solver_name] = "Xpress"
	REopt[:timeout_seconds] = MAXTIME
	REopt[:optimality_tolerance] = MIPRELSTOP
	
	set_optimizer_attribute(REopt, "FEASTOL", 1.0e-6)
	set_optimizer_attribute(REopt, "BACKTRACK", 5)
	set_optimizer_attribute(REopt, "LPTHREADS", 3)
	
	return REopt

end