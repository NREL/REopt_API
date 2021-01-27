using JuMP
using CPLEX

function reopt_model(MAXTIME, MIPRELSTOP)
   
	REopt = Model(optimizer_with_attributes(
					CPLEX.Optimizer, 
					"CPXPARAM_MIP_Tolerances_MIPGap" => MIPRELSTOP,
					"CPXPARAM_TimeLimit" => MAXTIME  
					)
				  )
	REopt[:solver_name] = "CPLEX"
	REopt[:timeout_seconds] = MAXTIME
	REopt[:optimality_tolerance] = MIPRELSTOP
	return REopt

end