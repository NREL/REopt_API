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