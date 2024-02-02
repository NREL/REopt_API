# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
function cbc_model(MAXTIME, MIPRELSTOP)
    m = Model(Cbc.Optimizer)
    set_optimizer_attribute(m, "seconds", MAXTIME)
    set_optimizer_attribute(m, "ratioGap", MIPRELSTOP)
	m[:solver_name] = "Cbc"
	m[:timeout_seconds] = MAXTIME
	m[:optimality_tolerance] = MIPRELSTOP
	return m
end

function xpress_solver(MAXTIME, MIPRELSTOP)
    m = direct_model(Xpress.Optimizer(MAXTIME=-MAXTIME, MIPRELSTOP=MIPRELSTOP, OUTPUTLOG = 0)) #logfile="output.log"))
	m[:solver_name] = "Xpress"
	m[:timeout_seconds] = MAXTIME
	m[:optimality_tolerance] = MIPRELSTOP
	return m
end

m1 = Model(optimizer_with_attributes(HiGHS.Optimizer, 
"time_limit" => timeout_seconds, 
"mip_rel_gap" => optimality_tolerance,
"output_flag" => false, "log_to_console" => false)
)