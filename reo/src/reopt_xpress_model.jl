using JuMP
using Xpress

function reopt_model(MAXTIME)
   
    REopt = direct_model(Xpress.Optimizer(MAXTIME=-MAXTIME, OUTPUTLOG = 0, 
		RESOURCESTRATEGY = 1, MAXMEMORYSOFT = 4000, TREEMEMORYLIMIT = 4000))
    # assuming that MAXMEMORYSOFT units are megabytes (b/c TREEMEMORYLIMIT units are megabytes)
    return REopt

end
