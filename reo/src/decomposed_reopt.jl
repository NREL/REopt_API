##############################################################################
#############  Additional functions for REopt decomopsition		 #############
##############################################################################

function add_decomp_model(m, p::Parameter, model_type::String, mth::Int64)
	if m[:solver_name] == "Xpress"
		sub_model = direct_model(Xpress.Optimizer(MAXTIME=-p.DecompTimeOut, MIPRELSTOP=p.DecompOptTol, OUTPUTLOG = 0))
	elseif m[:solver_name] == "Cbc"
		sub_model = Model(with_optimizer(Cbc.Optimizer, logLevel=0, seconds=p.DecompTimeOut, ratioGap=p.DecompOptTol))
	elseif m[:solver_name] == "SCIP"
		sub_model = Model(with_optimizer(SCIP.Optimizer, display_verblevel=0, limits_time=p.DecompTimeOut, limits_gap=p.DecompOptTol))
	else
		error("solver_name undefined or doesn't match existing base of REopt solvers.")
	end
	sub_model[:model_type] = model_type
	sub_model[:month_idx] = mth
	return sub_model
end

function add_subproblem_time_sets(m, p)
	m[:TimeStep] = p.TimeStepRatchetsMonth[m[:month_idx]]
	m[:start_period] = m[:TimeStep][1] - 1
	m[:end_period] = last(m[:TimeStep])
	m[:TimeStepBat] = append!([m[:start_period]],m[:TimeStep])
	m[:Month] = [m[:month_idx]]
	m[:TimeStepsWithGrid] = Int64[]
	m[:TimeStepsWithoutGrid] = Int64[]
	m[:TimeStepRatchets] = Dict()
	for r in p.Ratchets
		m[:TimeStepRatchets][r] = Int64[]
	end
	for ts in m[:TimeStep]
		if (ts in p.TimeStepsWithoutGrid)
			append!(m[:TimeStepsWithoutGrid], ts)
		else
			append!(m[:TimeStepsWithGrid], ts)
		end
		for r in p.Ratchets
			if (ts in p.TimeStepRatchets[r])
				append!(m[:TimeStepRatchets][r], ts)
			end
		end
	end
	m[:weight] = 1/12
end

function get_initial_decomp_penalties(m,p)
	m[:tech_size_penalty] = Dict()
	m[:storage_power_size_penalty] = Dict()
	m[:storage_energy_size_penalty] = Dict()
	m[:storage_inventory_penalty] = Dict()
	for t in p.Tech
		m[:tech_size_penalty][t] = 0.0
	end
	for b in p.Storage
		m[:storage_power_size_penalty][b] = 0.0
		m[:storage_energy_size_penalty][b] = 0.0
		m[:storage_inventory_penalty][b] = 0.0
	end
end

function update_decomp_penalties(m,p,mean_sizes::Dict)
	rho = 1e-4 #penalty factor; this is a parameter that can be tuned
	for t in p.Tech
		mean_size = mean_sizes["dvSize",t]
		m[:tech_size_penalty][t] = rho * (p.CapCostSlope[t,1] + p.pwf_om * p.OMperUnitSize[t]) * (value(m[:dvSize][t]) - mean_size)
	end
	for b in p.Storage
		mean_power = mean_sizes["dvStorageCapPower",b]
		mean_energy = mean_sizes["dvStorageCapPower",b]
		mean_inv = mean_sizes["dvStorageResetSOC",b]
		m[:storage_power_size_penalty][b] = rho * p.StorageCostPerKW[b] *(value(m[:dvStorageCapPower][b]) - mean_power)
		m[:storage_energy_size_penalty][b] = rho * p.StorageCostPerKWH[b] *(value(m[:dvStorageCapEnergy][b]) - mean_energy)
		m[:storage_inventory_penalty][b] = rho * p.StorageCostPerKWH[b] *(value(m[:dvStorageResetSOC][b]) - mean_inv)
	end
	add_to_expression!(m[:LagrangianPenalties], 
		sum(m[:tech_size_penalty][t] * m[:dvSize][t] for t in p.Tech)
			+ sum(m[:storage_power_size_penalty][b] * m[:dvStorageCapPower][b]
				+ m[:storage_energy_size_penalty][b] * m[:dvStorageCapEnergy][b]
				+ m[:storage_inventory_penalty][b] * m[:dvStorageResetSOC][b]
				for b in p.Storage)
	)
	set_objective_function(m, m[:REcosts] + m[:LagrangianPenalties])
	nothing
end

function get_sizing_decisions(m,p)
	sizes = Dict()
	for t in p.Tech
		sizes["dvSize",t] = value(m[:dvSize][t])
	end
	for b in p.Storage
		sizes["dvStorageCapPower",b] = value(m[:dvStorageCapPower][b])
		sizes["dvStorageCapEnergy",b] = value(m[:dvStorageCapEnergy][b])
		sizes["dvStorageResetSOC",b] = value(m[:dvStorageResetSOC][b])
	end
	return sizes
end

function fix_sizing_decisions(m,p,sizes::Dict)
	for midx in 1:12
		for t in p.Tech
			if t != "BOILER" && t != "ELECCHL"
				fix(m[:dvSize][t], sizes["dvSize",t], force=true)
			end
		end
		for b in p.Storage
			fix(m[:dvStorageCapPower][b], sizes["dvStorageCapPower",b], force=true)
			fix(m[:dvStorageCapEnergy][b], sizes["dvStorageCapEnergy",b], force=true)
			fix(m[:dvStorageResetSOC][b], sizes["dvStorageResetSOC",b], force=true)
		end
	end
	nothing
end

function add_sub_obj_value_results(m, p, r::Dict)
	### Obtain subproblem lcc's, minus the min charge adders and production incentives
	r["obj_no_annuals"] = value(m[:REcosts]) - value(m[:MinChargeAdder]) + value(m[:TotalProductionIncentive]) 
	### recalculate min charge adder and add to the results
	r["min_charge_adder_comp"] = value(m[:TotalEnergyChargesUtil]) + value(m[:TotalDemandCharges]) + value(m[:TotalExportBenefit]) + value(m[:TotalFixedCharges])
	r["sub_incentive"] = Array{Float64,1}([value(m[:dvProdIncent][t]) for t in p.Tech])
	if !isempty(p.DemandRatesMonth)
		r["peak_demand_for_month"] = sum(value(m[:dvPeakDemandEMonth][m[:month_idx],n]) for n in p.DemandMonthsBin)
	else
		r["peak_demand_for_month"] = 0.0
	end
	r["peak_ratchets"] = Array{Float64,1}([sum(value(m[:dvPeakDemandE][r,e]) for e in p.DemandBin) for r in p.Ratchets])
	r["total_min_charge"] = value(m[:TotalMinCharge])
	nothing
end

function convert_to_arrays(m, results::Dict)
	for key in keys(results)
		if !(typeof(results[key]) in [Array{Float64,1}, String, Float64, Dict{Any, Any}, Int64]) && length(results[key]) == length(m[:TimeStep])
			results[key] = Array{Float64,1}([results[key][idx] for idx in m[:TimeStep]])
		end
	end
	return results
end

function convert_to_axis_arrays(p, r::Dict)
	new_r = Dict()
	for key in keys(r)
		#if the value has been converted to an array for manipulation within python, then convert back to a DenseAxisArray
		if typeof(r[key])== Array{Float64,1} && length(r[key]) == p.TimeStepCount
			new_r[key] = JuMP.Containers.DenseAxisArray(r[key], p.TimeStep)
		#remove subproblem outputs
		elseif !(key in ["obj_no_annuals","min_charge_adder_comp","sub_incentive","peak_demand_for_month","peak_ratchets","total_min_charge"])
			new_r[key] = r[key]
		end
	end
	return new_r
end

function add_to_results(r1,r2)
	for key in keys(r1)
		if typeof(r1[key]) in [Float64, Int64]
			if !(key in ["chp_kw","batt_kwh","batt_kw","hot_tes_size_mmbtu","cold_tes_size_kwht",
					"wind_kw","generator_kw","absorpchl_kw"]) && !((occursin("pv",key) || occursin("PV",key)) && occursin("kw", key))
				r1[key] += r2[key]
			end
		elseif typeof(r1[key]) == Array{Float64,1}
			if length(r2[key]) >= 28*24
				r1[key] = append!(r1[key],r2[key])   #append time series outputs
			else
				r1[key] += r2[key]   #add tech-specific arrays (e.g., production incentive) 
			end
		end
	end
	return r1
end