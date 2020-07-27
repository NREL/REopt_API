using JuMP
using Xpress

function reopt_model(MAXTIME, MIPRELSTOP)
   
    REopt = direct_model(Xpress.Optimizer(MAXTIME=-MAXTIME, MIPRELSTOP=MIPRELSTOP, OUTPUTLOG = 0))
	return REopt

end