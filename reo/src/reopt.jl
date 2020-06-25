using JuMP
import MathOptInterface
const MOI = MathOptInterface
include("utils.jl")


function add_continuous_variables(m, p)
    @variables m begin
	    dvSize[p.Tech] >= 0     #X^{\sigma}_{t}: System Size of Technology t [kW]   (NEW)
    	dvSystemSizeSegment[p.Tech, p.Subdivision, p.Seg] >= 0   #X^{\sigma s}_{tks}: System size of technology t allocated to segmentation k, segment s [kW]  (NEW)
		dvGridPurchase[p.PricingTier, p.TimeStep] >= 0   # X^{g}_{uh}: Power from grid dispatched to meet electrical load in demand tier u during time step h [kW]  (NEW)
	    dvRatedProduction[p.Tech, p.TimeStep] >= 0   #X^{rp}_{th}: Rated production of technology t during time step h [kW]  (NEW)
	    dvProductionToGrid[p.Tech, p.SalesTiers, p.TimeStep] >= 0  # X^{ptg}_{tuh}: Exports from electrical production to the grid by technology t in demand tier u during time step h [kW]   (NEW)
	    dvStorageToGrid[p.StorageSalesTiers, p.TimeStep] >= 0  # X^{stg}_{uh}: Exports from electrical storage to the grid in demand tier u during time step h [kW]  (NEW)
		dvProductionToStorage[p.Storage, p.Tech, p.TimeStep] >= 0  # X^{ptg}_{bth}: Power from technology t used to charge storage system b during time step h [kW]  (NEW)
	    dvDischargeFromStorage[p.Storage, p.TimeStep] >= 0 # X^{pts}_{bh}: Power discharged from storage system b during time step h [kW]  (NEW)
	    dvGridToStorage[p.TimeStep] >= 0 # X^{gts}_{h}: Electrical power delivered to storage by the grid in time step h [kW]  (NEW)
	    dvStorageSOC[p.Storage, p.TimeStepBat] >= 0  # X^{se}_{bh}: State of charge of storage system b in time step h   (NEW)
	    dvStorageCapPower[p.Storage] >= 0   # X^{bkW}_b: Power capacity of storage system b [kW]  (NEW)
	    dvStorageCapEnergy[p.Storage] >= 0   # X^{bkWh}_b: Energy capacity of storage system b [kWh]  (NEW)
	    dvProdIncent[p.Tech] >= 0   # X^{pi}_{t}: Production incentive collected for technology [$]
		dvPeakDemandE[p.Ratchets, p.DemandBin] >= 0  # X^{de}_{re}:  Peak electrical power demand allocated to tier e during ratchet r [kW]
		dvPeakDemandEMonth[p.Month, p.DemandMonthsBin] >= 0  #  X^{dn}_{mn}: Peak electrical power demand allocated to tier n during month m [kW]
		dvPeakDemandELookback >= 0  # X^{lp}: Peak electric demand look back [kW]
        MinChargeAdder >= 0   #to be removed
		#UtilityMinChargeAdder[p.Month] >= 0   #X^{mc}_m: Annual utility minimum charge adder in month m [\$]
		#CHP and Fuel-burning variables
		dvFuelUsage[p.Tech, p.TimeStep] >= 0  # Fuel burned by technology t in time step h
		#dvFuelBurnYIntercept[p.Tech, p.TimeStep]  #X^{fb}_{th}: Y-intercept of fuel burned by technology t in time step h
		#dvThermalProduction[p.Tech, p.TimeStep]  #X^{tp}_{th}: Thermal production by technology t in time step h
		#dvAbsorptionChillerDemand[p.TimeStep]  #X^{ac}_h: Thermal power consumption by absorption chiller in time step h
		#dvElectricChillerDemand[p.TimeStep]  #X^{ec}_h: Electrical power consumption by electric chiller in time step h
    end
end


function add_integer_variables(m, p)
    @variables m begin
        binNMLorIL[p.NMILRegime], Bin    # Z^{nmil}_{v}: 1 If generation is in net metering interconnect limit regime v; 0 otherwise
        binProdIncent[p.Tech], Bin # Z^{pi}_{t}:  1 If production incentive is available for technology t; 0 otherwise 
		binSegmentSelect[p.Tech, p.Subdivision, p.Seg], Bin # Z^{\sigma s}_{tks} 1 if technology t, segmentation k is in segment s; 0 ow. (NEW)
        binSingleBasicTech[p.Tech,p.TechClass], Bin   #  Z^\text{sbt}_{tc}: 1 If technology t is used for technology class c; 0 otherwise
        binTechIsOnInTS[p.Tech, p.TimeStep], Bin  # 1 Z^{to}_{th}: If technology t is operating in time step h; 0 otherwise
		binDemandTier[p.Ratchets, p.DemandBin], Bin  # 1 If tier e has allocated demand during ratchet r; 0 otherwise
        binDemandMonthsTier[p.Month, p.DemandMonthsBin], Bin # 1 If tier n has allocated demand during month m; 0 otherwise
		binEnergyTier[p.Month, p.PricingTier], Bin    #  Z^{ut}_{mu} 1 If demand tier $u$ is active in month m; 0 otherwise (NEW)
    end
end


function add_no_grid_constraints(m, p)
	for ts in p.TimeStepsWithoutGrid
		fix(m[:dvGridToStorage][ts], 0.0, force=true)
		for u in p.PricingTier
			fix(m[:dvGridPurchase][u,ts], 0.0, force=true)
		end
		#for u in p.StorageSalesTiers  #don't allow curtailment of storage either
		#	fix(m[:dvStorageToGrid][u,ts], 0.0, force=true)
		#end
	end
end


function add_storage_size_constraints(m, p)
	# Constraint (4a): Reconcile initial state of charge for storage systems
	@constraint(m, InitStorageCon[b in p.Storage], m[:dvStorageSOC][b,0] == p.StorageInitSOC[b] * m[:dvStorageCapEnergy][b])
	# Constraint (4b)-1: Lower bound on Storage Energy Capacity
	@constraint(m, StorageEnergyLBCon[b in p.Storage], m[:dvStorageCapEnergy][b] >= p.StorageMinSizeEnergy[b])
	# Constraint (4b)-2: Upper bound on Storage Energy Capacity
	@constraint(m, StorageEnergyUBCon[b in p.Storage], m[:dvStorageCapEnergy][b] <= p.StorageMaxSizeEnergy[b])
	# Constraint (4c)-1: Lower bound on Storage Power Capacity
	@constraint(m, StoragePowerLBCon[b in p.Storage], m[:dvStorageCapPower][b] >= p.StorageMinSizePower[b])
	# Constraint (4c)-2: Upper bound on Storage Power Capacity
	@constraint(m, StoragePowerUBCon[b in p.Storage], m[:dvStorageCapPower][b] <= p.StorageMaxSizePower[b])
end


function add_storage_op_constraints(m, p)
	### Battery Operations
	# Constraint (4d): Electrical production sent to storage or grid must be less than technology's rated production
	@constraint(m, ElecTechProductionFlowCon[b in p.ElecStorage, t in p.ElectricTechs, ts in p.TimeStepsWithGrid],
		m[:dvProductionToStorage][b,t,ts] + sum(m[:dvProductionToGrid][t,u,ts] for u in p.SalesTiersByTech[t]) <= 
		p.ProductionFactor[t,ts] * p.LevelizationFactor[t] * m[:dvRatedProduction][t,ts]
	)
	# Constraint (4e): Electrical production sent to storage or grid must be less than technology's rated production - no grid
	@constraint(m, ElecTechProductionFlowNoGridCon[b in p.ElecStorage, t in p.ElectricTechs, ts in p.TimeStepsWithoutGrid],
		m[:dvProductionToStorage][b,t,ts]  <= 
		p.ProductionFactor[t,ts] * p.LevelizationFactor[t] * m[:dvRatedProduction][t,ts]
	)
	# Constraint (4f)-1: (Hot) Thermal production sent to storage or grid must be less than technology's rated production
	#@constraint(m, HeatingTechProductionFlowCon[b in p.HotTES, t in p.HeatingTechs, ts in p.TimeStep],
    #	        m[:dvProductionToStorage][b,t,ts]  <= 
	#			p.ProductionFactor[t,ts] * dvThermalProduction[t,ts]
	#			)
	# Constraint (4f)-2: (Cold) Thermal production sent to storage or grid must be less than technology's rated production
	#@constraint(m, CoolingTechProductionFlowCon[b in p.ColdTES, t in p.CoolingTechs, ts in p.TimeStep],
    #	        m[:dvProductionToStorage][b,t,ts]  <= 
	#			p.ProductionFactor[t,ts] * dvThermalProduction[t,ts]
	#			)
	# Constraint (4g): Reconcile state-of-charge for electrical storage - with grid
	@constraint(m, ElecStorageInventoryCon[b in p.ElecStorage, ts in p.TimeStepsWithGrid],
		m[:dvStorageSOC][b,ts] == m[:dvStorageSOC][b,ts-1] + p.TimeStepScaling * (  
			sum(p.ChargeEfficiency[t,b] * m[:dvProductionToStorage][b,t,ts] for t in p.ElectricTechs) + 
			p.GridChargeEfficiency*m[:dvGridToStorage][ts] - m[:dvDischargeFromStorage][b,ts]/p.DischargeEfficiency[b]
		)
	)
				
	# Constraint (4h): Reconcile state-of-charge for electrical storage - no grid
	@constraint(m, ElecStorageInventoryConNoGrid[b in p.ElecStorage, ts in p.TimeStepsWithoutGrid],
		m[:dvStorageSOC][b,ts] == m[:dvStorageSOC][b,ts-1] + p.TimeStepScaling * (  
			sum(p.ChargeEfficiency[t,b] * m[:dvProductionToStorage][b,t,ts] for t in p.ElectricTechs) - m[:dvDischargeFromStorage][b,ts]/p.DischargeEfficiency[b]
		)
	)
	
	# Constraint (4i)-1: Reconcile state-of-charge for (hot) thermal storage
	#@constraint(m, HotTESInventoryCon[b in p.HotTES, ts in p.TimeStep],
    #	        m[:dvStorageSOC][b,ts] == m[:dvStorageSOC][b,ts-1] + p.TimeStepScaling * (  
	#				sum(p.ChargeEfficiency[t,b] * m[:dvProductionToStorage][b,t,ts] for t in p.HeatingTechs) - 
	#				m[:dvDischargeFromStorage][b,ts]/p.DischargeEfficiency[b]
	#				)
	#			)
				
	# Constraint (4i)-2: Reconcile state-of-charge for (cold) thermal storage
	#@constraint(m, ColdTESInventoryCon[b in p.ColdTES, ts in p.TimeStep],
    #	        m[:dvStorageSOC][b,ts] == m[:dvStorageSOC][b,ts-1] + p.TimeStepScaling * (  
	#				sum(p.ChargeEfficiency[t,b] * m[:dvProductionToStorage][b,t,ts] for t in p.CoolingTechs) - 
	#				m[:dvDischargeFromStorage][b,ts]/p.DischargeEfficiency[b]
	#				)
	#			)
	
	# Constraint (4j): Minimum state of charge
	@constraint(m, MinStorageLevelCon[b in p.Storage, ts in p.TimeStep],
		m[:dvStorageSOC][b,ts] >= p.StorageMinSOC[b] * m[:dvStorageCapEnergy][b]
	)
	
	#Constraint (4i)-1: Dispatch to electrical storage is no greater than power capacity
	@constraint(m, ElecChargeLEQCapCon[b in p.ElecStorage, ts in p.TimeStep],
		m[:dvStorageCapPower][b] >= (  
			sum(m[:dvProductionToStorage][b,t,ts] for t in p.ElectricTechs) + m[:dvGridToStorage][ts]
		)
	)
	
	#Constraint (4i)-2: Dispatch to hot storage is no greater than power capacity
	#@constraint(m, HotTESChargeLEQCapCon[b in p.HotTES, ts in p.TimeStep],
    #	        m[:dvStorageCapPower][b] >= (  
	#				sum(m[:dvProductionToStorage][b,t,ts] for t in p.HeatingTechs)
	#				)
	#			)
	
	#Constraint (4i)-3: Dispatch to cold storage is no greater than power capacity
	#@constraint(m, ColdTESChargeLEQCapCon[b in p.ColdTES, ts in p.TimeStep],
    #	        m[:dvStorageCapPower][b] >= (  
	#				sum(m[:dvProductionToStorage][b,t,ts] for t in p.CoolingTechs)
	#				)
	#			)
	
	#Constraint (4j): Dispatch from storage is no greater than power capacity
	@constraint(m, DischargeLEQCapCon[b in p.Storage, ts in p.TimeStep],
		m[:dvStorageCapPower][b] >= m[:dvDischargeFromStorage][b,ts]
	)
	
	#Constraint (4k)-alt: Dispatch to and from electrical storage is no greater than power capacity
	@constraint(m, ElecChargeLEQCapConAlt[b in p.ElecStorage, ts in p.TimeStepsWithGrid],
		m[:dvStorageCapPower][b] >=   m[:dvDischargeFromStorage][b,ts] + 
			sum(m[:dvProductionToStorage][b,t,ts] for t in p.ElectricTechs) + m[:dvGridToStorage][ts]
	)	
	#Constraint (4l)-alt: Dispatch from electrical storage is no greater than power capacity
	@constraint(m, DischargeLEQCapConNoGridAlt[b in p.ElecStorage, ts in p.TimeStepsWithoutGrid],
		m[:dvStorageCapPower][b] >= m[:dvDischargeFromStorage][b,ts] + 
			sum(m[:dvProductionToStorage][b,t,ts] for t in p.ElectricTechs)
	)
				
	#Constraint (4m)-1: Dispatch from thermal storage is no greater than power capacity
	#@constraint(m, DischargeLEQCapCon[b in p.HotTES, ts in p.TimeStep],
    #	        m[:dvStorageCapPower][b] >= sum(m[:dvProductionToStorage][b,t,ts] for t in p.HeatingTechs)
	#			)
	#Constraint (4m)-2: Dispatch from thermal storage is no greater than power capacity
	#@constraint(m, DischargeLEQCapCon[b in p.ColdTES, ts in p.TimeStep],
    #	        m[:dvStorageCapPower][b] >= sum(m[:dvProductionToStorage][b,t,ts] for t in p.CoolingTechs)
	#			)
					
	#Constraint (4n): State of charge upper bound is storage system size
	@constraint(m, StorageEnergyMaxCapCon[b in p.Storage, ts in p.TimeStep],
		m[:dvStorageSOC][b,ts] <= m[:dvStorageCapEnergy][b]
	)
	
end


function add_prod_incent_constraints(m, p)
	##Constraint (6a)-1: Production Incentive Upper Bound (unchanged)
	@constraint(m, ProdIncentUBCon[t in p.Tech],
		m[:dvProdIncent][t] <= m[:binProdIncent][t] * p.MaxProdIncent[t] * p.pwf_prod_incent[t] * p.two_party_factor)
	##Constraint (6a)-2: Production Incentive According to Production (updated)
	@constraint(m, IncentByProductionCon[t in p.Tech],
		m[:dvProdIncent][t] <= p.TimeStepScaling * p.ProductionIncentiveRate[t] * p.pwf_prod_incent[t] * p.two_party_factor * 
			sum(p.ProductionFactor[t, ts] * m[:dvRatedProduction][t,ts] for ts in p.TimeStep)
	)
	##Constraint (6b): System size max to achieve production incentive
	@constraint(m, IncentBySystemSizeCon[t in p.Tech],
		m[:dvSize][t]  <= p.MaxSizeForProdIncent[t] + m[:NewMaxSize][t] * (1 - m[:binProdIncent][t]))
end


function reopt(reo_model, model_inputs::Dict)

	t_start = time()
    p = Parameter(model_inputs)
	t = time() - t_start

	results = reopt_run(reo_model, p)
	results["julia_input_construction_seconds"] = t
	return results
end


function reopt_run(m, p::Parameter)

	t_start = time()
	results = Dict{String, Any}()
    Obj = 2  # 1 for minimize LCC, 2 for min LCC AND high mean SOC
	
	## Big-M adjustments; these need not be replaced in the parameter object.
	
	m[:NewMaxUsageInTier] = Array{Float64,2}(undef,12, p.PricingTierCount+1)
	m[:NewMaxDemandInTier] = Array{Float64,2}(undef, length(p.Ratchets), p.DemandBinCount)
	m[:NewMaxDemandMonthsInTier] = Array{Float64,2}(undef,12, p.DemandMonthsBinCount)
	m[:NewMaxSize] = Dict()
	NewMaxSizeByHour = Array{Float64,2}(undef,length(p.Tech),p.TimeStepCount)
	# m[:NewMaxDemandMonthsInTier] sets a new minimum if the new peak demand for the month, minus the size of all previous bins, is less than the existing bin size.
	if !isempty(p.ElecStorage)
		added_power = p.StorageMaxSizePower["Elec"]
		added_energy = p.StorageMaxSizeEnergy["Elec"]
	else
		added_power = 1.0e-3
		added_energy = 1.0e-3
	end
	
	for n in p.DemandMonthsBin
		for mth in p.Month 
			if n > 1
				m[:NewMaxDemandMonthsInTier][mth,n] = minimum([p.MaxDemandMonthsInTier[n], 
					added_power + maximum([p.ElecLoad[ts] #+ LoadProfileChillerElectric[ts]
					for ts in p.TimeStepRatchetsMonth[mth]])  - 
					sum(m[:NewMaxDemandMonthsInTier][mth,np] for np in 1:(n-1)) ]
				)
			else 
				m[:NewMaxDemandMonthsInTier][mth,n] = minimum([p.MaxDemandMonthsInTier[n], 
					added_power + maximum([p.ElecLoad[ts] #+ LoadProfileChillerElectric[ts]
					for ts in p.TimeStepRatchetsMonth[mth]])   ])
			end
		end
	end
	
	# m[:NewMaxDemandInTier] sets a new minimum if the new peak demand for the ratchet, minus the size of all previous bins for the ratchet, is less than the existing bin size.
	for e in p.DemandBin
		for r in p.Ratchets 
			if e > 1
				m[:NewMaxDemandInTier][r,e] = minimum([p.MaxDemandInTier[e], 
				added_power + maximum([p.ElecLoad[ts] #+ p.LoadProfileChillerElectric[ts]
					for ts in p.TimeStep])  - 
				sum(m[:NewMaxDemandInTier][r,ep] for ep in 1:(e-1))
				])
			else
				m[:NewMaxDemandInTier][r,e] = minimum([p.MaxDemandInTier[e], 
				added_power + maximum([p.ElecLoad[ts] #+ p.LoadProfileChillerElectric[ts]
					for ts in p.TimeStep])  
				])
			end
		end
	end
	
	# m[:NewMaxUsageInTier] sets a new minumum if the total demand for the month, minus the size of all previous bins, is less than the existing bin size.
	for u in p.PricingTier
		for mth in p.Month 
			if u > 1
				m[:NewMaxUsageInTier][mth,u] = minimum([p.MaxUsageInTier[u], 
					added_energy + sum(p.ElecLoad[ts] #+ p.LoadProfileChillerElectric[ts]
					for ts in p.TimeStepRatchetsMonth[mth]) - sum(m[:NewMaxUsageInTier][mth,up] for up in 1:(u-1))
				])
			else
				m[:NewMaxUsageInTier][mth,u] = minimum([p.MaxUsageInTier[u], 
					added_energy + sum(p.ElecLoad[ts] #+ p.LoadProfileChillerElectric[ts]
					for ts in p.TimeStepRatchetsMonth[mth])  
				])
			end
		end
	end
	
	# NewMaxSize generates a new maximum size that is equal to the largest monthly load of the year.  This is intended to be a reasonable upper bound on size that would never be exceeeded, but is sufficienctly small to replace much larger big-M values placed as a default.
	TempHeatingTechs = [] #temporarily replace p.HeatingTechs which is undefined
	TempCoolingTechs = [] #temporarily replace p.CoolingTechs which is undefined
	
	for t in TempHeatingTechs
		m[:NewMaxSize][t] = maximum([sum(p.HeatingLoad[ts] for ts in p.TimeStepRatchetsMonth[mth]) for mth in p.Month])
		if (m[:NewMaxSize][t] > p.MaxSize[t])
			m[:NewMaxSize][t] = p.MaxSize[t]
		end
	end
	for t in TempCoolingTechs
		m[:NewMaxSize][t] = maximum([sum(p.CoolingLoad[ts] for ts in p.TimeStepRatchetsMonth[mth]) for mth in p.Month])
		if (m[:NewMaxSize][t] > p.MaxSize[t])
			m[:NewMaxSize][t] = p.MaxSize[t]
		end
	end
	for t in p.ElectricTechs
		m[:NewMaxSize][t] = maximum([sum(p.ElecLoad[ts] for ts in p.TimeStepRatchetsMonth[mth]) for mth in p.Month])
		if (m[:NewMaxSize][t] > p.MaxSize[t])
			m[:NewMaxSize][t] = p.MaxSize[t]
		end
	end
	
	# NewMaxSizeByHour is designed to scale the right-hand side of the constraint limiting rated production in each hour to the production factor; in most cases this is unaffected unless the production factor is zero, in which case the right-hand side is set to zero.
	#for t in p.ElectricTechs 
	#	for ts in p.TimeStep
	#		NewMaxSizeByHour[t,ts] = minimum([m[:NewMaxSize][t],
	#			sum(p.ProdFactor[t,d,ts] for d in p.Load if p.LoadProfile[d,ts] > 0)  * m[:NewMaxSize][t],
	#			sum(p.LoadProfile[d,ts] for d in ["1R"], ts in p.TimeStep)  
	#		])
	#	end
	#end	
	results["julia_reopt_preamble_seconds"] = time() - t_start
	t_start = time()

	add_continuous_variables(m, p)
	add_integer_variables(m, p)

	results["julia_reopt_variables_seconds"] = time() - t_start
	t_start = time()
    ##############################################################################
	#############  		Constraints									 #############
	##############################################################################
	
	## Temporary workaround for outages TimeStepsWithoutGrid
	if !isempty(p.TimeStepsWithoutGrid)
		add_no_grid_constraints(m, p)
	end

	#don't allow curtailment or sales of stroage 
	for ts in p.TimeStep
		for u in p.StorageSalesTiers
			fix(m[:dvStorageToGrid][u,ts], 0.0, force=true)
		end
	end

					
	##Constraint (1a): Sum of fuel used must not exceed prespecified limits
	@constraint(m, TotalFuelConsumptionCon[f in p.FuelType],
				sum( m[:dvFuelUsage][t,ts] for t in p.TechsByFuelType[f], ts in p.TimeStep ) <= 
				p.FuelLimit[f]
				)
	
	# Constraint (1b): Fuel burn for non-CHP Constraints
	@constraint(m, FuelBurnCon[t in p.FuelBurningTechs, ts in p.TimeStep],
				m[:dvFuelUsage][t,ts]  == (p.FuelBurnSlope[t] * p.ProductionFactor[t,ts] * m[:dvRatedProduction][t,ts]) + 
					(p.FuelBurnYInt[t] * m[:binTechIsOnInTS][t,ts])
				)
	
	#if !isempty(CHPTechs)
		#Constraint (1c): Total Fuel burn for CHP
		#@constraint(m, CHPFuelBurnCon[t in CHPTechs, ts in p.TimeStep],
		#			m[:dvFuelUsage][t,ts]  == p.FuelBurnAmbientFactor[t,ts] * (dvFuelBurnYIntercept[t,th] +  
		#				p.ProductionFactor[t,ts] * p.FuelBurnRateM[t] * m[:dvRatedProduction][t,ts]) 					
		#			)
					
		#Constraint (1d): Y-intercept fuel burn for CHP
		#@constraint(m, CHPFuelBurnYIntCon[t in CHPTechs, ts in p.TimeStep],
		#			p.FuelBurnYIntRate[t] * m[:dvSize][t] - m[:NewMaxSize][t] * (1-m[:binTechIsOnInTS][t,ts])  <= dvFuelBurnYIntercept[t,th]   					
		#			)
	#end
	
	#if !isempty(NonCHPHeatingTechs)
		#Constraint (1e): Total Fuel burn for Boiler
		#@constraint(m, BoilerFuelBurnCon[t in NonCHPHeatingTechs, ts in p.TimeStep],
		#			m[:dvFuelUsage][t,ts]  ==  dvThermalProduction[t,ts] / p.BoilerEfficiency 					
		#			)
	#end
	
	
	### Constraint set (2): CHP Thermal Production Constraints
	#if !isempty(CHPTechs)
		#Constraint (2a-1): Upper Bounds on Thermal Production Y-Intercept 
		#@constraint(m, CHPYInt2a1Con[t in CHPTechs, ts in p.TimeStep],
		#			dvThermalProductionYIntercept[t,ts] <= CHPThermalProdIntercept[t] * m[:dvSize][t]
		#			)
		# Constraint (2a-2): Upper Bounds on Thermal Production Y-Intercept 
		#@constraint(m, CHPYInt2a1Con[t in CHPTechs, ts in p.TimeStep],
		#			dvThermalProductionYIntercept[t,ts] <= CHPThermalProdIntercept[t] * m[:NewMaxSize][t] * m[:binTechIsOnInTS][t,ts]
		#			)
		# Constraint (2b): Thermal Production of CHP 
		#@constraint(m, CHPThermalProductionCpn[t in CHPTechs, ts in p.TimeStep],
		#			dvThermalProduction[t,ts] <=  HotWaterAmbientFactor[t,ts] * HotWaterThermalFactor[t,ts] * (
		#			CHPThermalProdSlope[t] * ProductionFactor[t,ts] * m[:dvRatedProduction][t,ts] + dvThermalProductionYIntercept[t,ts]
		#				)
		#			)
	#end
	
	
	### Section 3: Switch Constraints
	#Constraint (3a): Technology must be on for nonnegative output (fuel-burning only)
	@constraint(m, ProduceIfOnCon[t in p.FuelBurningTechs, ts in p.TimeStep],
				m[:dvRatedProduction][t,ts] <= m[:NewMaxSize][t] * m[:binTechIsOnInTS][t,ts])
	#Constraint (3b): Technologies that are turned on must not be turned down
	@constraint(m, MinTurndownCon[t in p.FuelBurningTechs, ts in p.TimeStep],
			  p.MinTurndown[t] * m[:dvSize][t] - m[:dvRatedProduction][t,ts] <= m[:NewMaxSize][t] * (1-m[:binTechIsOnInTS][t,ts]) )
	
    ### Section 4: Storage System Constraints
	add_storage_size_constraints(m, p)
	add_storage_op_constraints(m, p)
	### Constraint set (5) - hot and cold thermal loads - reserved for later
	
	### Constraint set (6): Production Incentive Cap
	add_prod_incent_constraints(m, p)
    ### System Size and Production Constraints
	### Constraint set (7): System Size is zero unless single basic tech is selected for class
	if !isempty(p.Tech)

		# PV techs can be constrained by space available based on location at site (roof, ground, both)
		@constraint(m, TechMaxSizeByLocCon[loc in p.Location],
			sum( m[:dvSize][t] * p.TechToLocation[t, loc] for t in p.Tech) <= p.MaxSizesLocation[loc]
		)

		#Constraint (7a): Single Basic Technology Constraints
		@constraint(m, TechMaxSizeByClassCon[c in p.TechClass, t in p.TechsInClass[c]],
			m[:dvSize][t] <= m[:NewMaxSize][t] * m[:binSingleBasicTech][t,c]
			)
		##Constraint (7b): At most one Single Basic Technology per Class
		@constraint(m, TechClassMinSelectCon[c in p.TechClass],
			sum( m[:binSingleBasicTech][t,c] for t in p.TechsInClass[c] ) <= 1
			)
		##Constraint (7c): Minimum size for each tech class
		@constraint(m, TechClassMinSizeCon[c in p.TechClass],
					sum( m[:dvSize][t] for t in p.TechsInClass[c] ) >= p.TechClassMinSize[c]
				)
		
		## Constraint (7d): Non-turndown technologies are always at rated production
		@constraint(m, RenewableRatedProductionCon[t in p.TechsNoTurndown, ts in p.TimeStep],
			m[:dvRatedProduction][t,ts] == m[:dvSize][t]  
		)
			
		##Constraint (7e): Derate factor limits production variable (separate from ProductionFactor)
		@constraint(m, TurbineRatedProductionCon[t in p.Tech, ts in p.TimeStep; !(t in p.TechsNoTurndown)],
			m[:dvRatedProduction][t,ts]  <= p.ElectricDerate[t,ts] * m[:dvSize][t]
		)
			
		##Constraint (7f)-1: Minimum segment size
		@constraint(m, SegmentSizeMinCon[t in p.Tech, k in p.Subdivision, s in 1:p.SegByTechSubdivision[k,t]],
			m[:dvSystemSizeSegment][t,k,s]  >= p.SegmentMinSize[t,k,s] * m[:binSegmentSelect][t,k,s]
		)
		
		##Constraint (7f)-2: Maximum segment size
		@constraint(m, SegmentSizeMaxCon[t in p.Tech, k in p.Subdivision, s in 1:p.SegByTechSubdivision[k,t]],
			m[:dvSystemSizeSegment][t,k,s]  <= p.SegmentMaxSize[t,k,s] * m[:binSegmentSelect][t,k,s]
		)
		
		##Constraint (7g):  Segments add up to system size 
		@constraint(m, SegmentSizeAddCon[t in p.Tech, k in p.Subdivision],
			sum(m[:dvSystemSizeSegment][t,k,s] for s in 1:p.SegByTechSubdivision[k,t]) == m[:dvSize][t]
		)
			
		##Constraint (7h): At most one segment allowed
		@constraint(m, SegmentSelectCon[c in p.TechClass, t in p.TechsInClass[c], k in p.Subdivision],
			sum(m[:binSegmentSelect][t,k,s] for s in 1:p.SegByTechSubdivision[k,t]) <= m[:binSingleBasicTech][t,c]
		)
	end

	### Constraint set (8): Electrical Load Balancing and Grid Sales
	##Constraint (8a): Electrical Load Balancing with Grid
	
	@constraint(m, ElecLoadBalanceCon[ts in p.TimeStepsWithGrid],
		sum(p.ProductionFactor[t,ts] * p.LevelizationFactor[t] * m[:dvRatedProduction][t,ts] for t in p.ElectricTechs) +  
		sum( m[:dvDischargeFromStorage][b,ts] for b in p.ElecStorage ) + 
		sum( m[:dvGridPurchase][u,ts] for u in p.PricingTier ) ==
		sum( sum(m[:dvProductionToStorage][b,t,ts] for b in p.ElecStorage) + 
			sum(m[:dvProductionToGrid][t,u,ts] for u in p.SalesTiersByTech[t]) for t in p.ElectricTechs) +
		sum(m[:dvStorageToGrid][u,ts] for u in p.StorageSalesTiers) + m[:dvGridToStorage][ts] + 
		## sum(dvThermalProduction[t,ts] for t in p.CoolingTechs )/ p.ElectricChillerEfficiency +
		p.ElecLoad[ts]
	)
	
	##Constraint (8b): Electrical Load Balancing without Grid
	@constraint(m, ElecLoadBalanceNoGridCon[ts in p.TimeStepsWithoutGrid],
		sum(p.ProductionFactor[t,ts] * p.LevelizationFactor[t] * m[:dvRatedProduction][t,ts] for t in p.ElectricTechs) +  
		sum( m[:dvDischargeFromStorage][b,ts] for b in p.ElecStorage )  ==
		sum( sum(m[:dvProductionToStorage][b,t,ts] for b in p.ElecStorage) + 
			sum(m[:dvProductionToGrid][t,u,ts] for u in p.CurtailmentTiers) for t in p.ElectricTechs) +
		## sum(dvThermalProduction[t,ts] for t in p.CoolingTechs )/ p.ElectricChillerEfficiency +
		p.ElecLoad[ts]
	)
	
	##Constraint (8c): Grid-to-storage no greater than grid purchases 
	@constraint(m, GridToStorageCon[ts in p.TimeStepsWithGrid],
		sum( m[:dvGridPurchase][u,ts] for u in p.PricingTier)  >= m[:dvGridToStorage][ts]
	)
		
	##Constraint (8d): Storage-to-grid no greater than discharge from Storage
	@constraint(m, StorageToGridCon[ts in p.TimeStepsWithGrid],
		sum( m[:dvDischargeFromStorage][b,ts] for b in p.ElecStorage)  >= sum(m[:dvStorageToGrid][u,ts] for u in p.StorageSalesTiers)
	)
		
	if !isempty(p.SalesTiers)
		##Constraint (8e): Production-to-grid no greater than production
		@constraint(m, ProductionToGridCon[t in p.Tech, ts in p.TimeStepsWithGrid],
		 p.ProductionFactor[t,ts] * p.LevelizationFactor[t] * m[:dvRatedProduction][t,ts] >= sum(m[:dvProductionToGrid][t,u,ts] for u in p.SalesTiersByTech[t])
		)
		
		##Constraint (8f): Total sales to grid no greater than annual allocation - storage tiers
		@constraint(m,  AnnualGridSalesLimitCon,
		 p.TimeStepScaling * ( 
			sum( m[:dvStorageToGrid][u,ts] for u in p.StorageSalesTiers, ts in p.TimeStepsWithGrid if !(u in p.CurtailmentTiers)) +  sum(m[:dvProductionToGrid][t,u,ts] for u in p.SalesTiers, t in p.TechsBySalesTier[u], ts in p.TimeStepsWithGrid if !(u in p.CurtailmentTiers))) <= p.MaxGridSales[1]
		)
	end
	## End constraint (8)

    ### Constraint set (9): Net Meter Module (copied directly from legacy model)
	if !isempty(p.Tech)
		#Constraint (9a): exactly one net-metering regime must be selected
		@constraint(m, sum(m[:binNMLorIL][n] for n in p.NMILRegime) == 1)
		
		##Constraint (9b): Maximum system sizes for each net-metering regime
		@constraint(m, NetMeterSizeLimit[n in p.NMILRegime],
					sum(p.TurbineDerate[t] * m[:dvSize][t]
                    for t in p.TechsByNMILRegime[n]) <= p.NMILLimits[n] * m[:binNMLorIL][n])
	end
	##Constraint (9c): Net metering only -- can't sell more than you purchase
	if !isempty(p.SalesTiers)
		@constraint(m, GridSalesLimit, 
				p.TimeStepScaling * sum(m[:dvProductionToGrid][t,1,ts] for t in p.TechsBySalesTier[1], ts in p.TimeStep)  + 
				sum(m[:dvStorageToGrid][u,ts] for u in p.StorageSalesTiers, ts in p.TimeStep) <= p.TimeStepScaling * 
				sum(m[:dvGridPurchase][u,ts] for u in p.PricingTier, ts in p.TimeStep)
			)
	end
	###End constraint set (9)
	
	### Constraint set (10): Electrical Energy Demand Pricing Tiers
	##Constraint (10a): Usage limits by pricing tier, by month
	@constraint(m, [u in p.PricingTier, mth in p.Month],
                p.TimeStepScaling * sum( m[:dvGridPurchase][u, ts] for ts in p.TimeStepRatchetsMonth[mth] ) <= m[:binEnergyTier][mth, u] * m[:NewMaxUsageInTier][mth,u])
	##Constraint (10b): Ordering of pricing tiers
	@constraint(m, [u in 2:p.FuelBinCount, mth in p.Month],   #Need to fix, update purchase vs. sales pricing tiers
    	        m[:binEnergyTier][mth, u] - m[:binEnergyTier][mth, u-1] <= 0)
	## Constraint (10c): One tier must be full before any usage in next tier 
	@constraint(m, [u in 2:p.FuelBinCount, mth in p.Month],
    	        m[:binEnergyTier][mth, u] * m[:NewMaxUsageInTier][mth,u-1] - sum( m[:dvGridPurchase][u-1, ts] for ts in p.TimeStepRatchetsMonth[mth] ) <= 0)
	
	#End constraint set (10)

	### Constraint set (11): Peak Electrical Power Demand Charges: Months
	## Constraint (11a): Upper bound on peak electrical power demand by tier, by month, if tier is selected (0 o.w.)
	@constraint(m, [n in p.DemandMonthsBin, mth in p.Month],
                m[:dvPeakDemandEMonth][mth,n] <= m[:NewMaxDemandMonthsInTier][mth,n] * m[:binDemandMonthsTier][mth,n])
	
	## Constraint (11b): Monthly peak electrical power demand tier ordering
	@constraint(m, [mth in p.Month, n in 2:p.DemandMonthsBinCount],
        	        m[:binDemandMonthsTier][mth, n] <= m[:binDemandMonthsTier][mth, n-1])
	
	## Constraint (11c): One monthly peak electrical power demand tier must be full before next one is active
	@constraint(m, [mth in p.Month, n in 2:p.DemandMonthsBinCount],
        	 m[:binDemandMonthsTier][mth, n] * m[:NewMaxDemandMonthsInTier][mth,n-1] <= m[:dvPeakDemandEMonth][mth, n-1])
	
	## Constraint (11d): Monthly peak demand is >= demand at each hour in the month` 
	@constraint(m, [mth in p.Month, ts in p.TimeStepRatchetsMonth[mth]],
        	 sum( m[:dvPeakDemandEMonth][mth, n] for n in p.DemandMonthsBin ) >= 
			 sum( m[:dvGridPurchase][u, ts] for u in p.PricingTier )
	)
	### End Constraint Set (11)
	
	### Constraint set (12): Peak Electrical Power Demand Charges: Ratchets
	if !isempty(p.TimeStepRatchets)
		## Constraint (12a): Upper bound on peak electrical power demand by tier, by ratchet, if tier is selected (0 o.w.)
		@constraint(m, [r in p.Ratchets, e in p.DemandBin],
		            m[:dvPeakDemandE][r, e] <= m[:NewMaxDemandInTier][r,e] * m[:binDemandTier][r, e])
		
		## Constraint (12b): Ratchet peak electrical power ratchet tier ordering
		@constraint(m, [r in p.Ratchets, e in 2:p.DemandBinCount],
		    	        m[:binDemandTier][r, e] <= m[:binDemandTier][r, e-1])
		
		## Constraint (12c): One ratchet peak electrical power demand tier must be full before next one is active
		@constraint(m, [r in p.Ratchets, e in 2:p.DemandBinCount],
		    	 m[:binDemandTier][r, e] * m[:NewMaxDemandInTier][r,e-1] <= m[:dvPeakDemandE][r, e-1])
		
		## Constraint (12d): Ratchet peak demand is >= demand at each hour in the ratchet` 
		@constraint(m, [r in p.Ratchets, ts in p.TimeStepRatchets[r]],
		    	 sum( m[:dvPeakDemandE][r, e] for e in p.DemandBin ) >= 
				 sum( m[:dvGridPurchase][u, ts] for u in p.PricingTier )
		)
		
		##Constraint (12e): Peak demand used in percent lookback calculation 
		@constraint(m, [m in p.DemandLookbackMonths],
			        m[:dvPeakDemandELookback] >= sum(m[:dvPeakDemandEMonth][m, n] for n in p.DemandMonthsBin)
					)
		
		##Constraint (12f): Ratchet peak demand charge is bounded below by lookback
		@constraint(m, [r in p.DemandLookbackMonths],
					sum( m[:dvPeakDemandEMonth][r,e] for e in p.DemandBin ) >= 
					p.DemandLookbackPercent * m[:dvPeakDemandELookback] )
	end
	### End Constraint Set (12)
	
	### Alternate constraint (13): Monthly minimum charge adder
	
    r_tax_fraction_owner = (1 - p.r_tax_owner)
    r_tax_fraction_offtaker = (1 - p.r_tax_offtaker)

    PVTechs = filter(t->startswith(t, "PV"), p.Tech)
	if !isempty(p.Tech)
		WindTechs = p.TechsInClass["WIND"]
		GeneratorTechs = p.TechsInClass["GENERATOR"]
	else
		WindTechs = []
		GeneratorTechs = []
	end

	@expression(m, TotalTechCapCosts, p.two_party_factor * (
		sum( p.CapCostSlope[t,s] * m[:dvSystemSizeSegment][t,"CapCost",s] for t in p.Tech, s in 1:p.SegByTechSubdivision["CapCost",t] ) + 
		sum( p.CapCostYInt[t,s] * m[:binSegmentSelect][t,"CapCost",s] for t in p.Tech, s in 1:p.SegByTechSubdivision["CapCost",t] ) 
	))
	@expression(m, TotalStorageCapCosts, p.two_party_factor * 
		sum( p.StorageCostPerKW[b]*m[:dvStorageCapPower][b] + p.StorageCostPerKWH[b]*m[:dvStorageCapEnergy][b] for b in p.Storage )
	)
	@expression(m, TotalPerUnitSizeOMCosts, p.two_party_factor * p.pwf_om * 
		sum( p.OMperUnitSize[t] * m[:dvSize][t] for t in p.Tech ) 
	)
    if !isempty(GeneratorTechs)
		@expression(m, TotalPerUnitProdOMCosts, p.two_party_factor * p.pwf_om * 
			sum( p.OMcostPerUnitProd[t] * m[:dvRatedProduction][t,ts] for t in p.FuelBurningTechs, ts in p.TimeStep ) 
		)
    else
        @expression(m, TotalPerUnitProdOMCosts, 0.0)
	end

	### Utility and Taxable Costs
	if !isempty(p.Tech)
		# NOTE: LevelizationFactor is baked into m[:dvProductionToGrid]
		@expression(m, TotalExportBenefit, p.pwf_e * p.TimeStepScaling * sum( 
			sum(p.GridExportRates[u,ts] * m[:dvStorageToGrid][u,ts] for u in p.StorageSalesTiers) 
			+ sum(p.GridExportRates[u,ts] * m[:dvProductionToGrid][t,u,ts] 
				  for u in p.SalesTiers, t in p.TechsBySalesTier[u]
			) for ts in p.TimeStep )
		)
		@expression(m, TotalProductionIncentive, sum(m[:dvProdIncent][t] for t in p.Tech))

		@expression(m, ExportedElecWIND,
					p.TimeStepScaling * sum(m[:dvProductionToGrid][t,u,ts] 
						for t in WindTechs, u in p.SalesTiersByTech[t], ts in p.TimeStep)
		)
		@expression(m, ExportedElecGEN,
					p.TimeStepScaling * sum(m[:dvProductionToGrid][t,u,ts] 
						for t in GeneratorTechs, u in p.SalesTiersByTech[t], ts in p.TimeStep)
		)        
		@expression(m, ExportBenefitYr1,
				p.TimeStepScaling * sum( 
				sum( p.GridExportRates[u,ts] * m[:dvStorageToGrid][u,ts] for u in p.StorageSalesTiers) 
				+ sum( p.GridExportRates[u,ts] * m[:dvProductionToGrid][t,u,ts] 
					  for u in p.SalesTiers, t in p.TechsBySalesTier[u]) 
				for ts in p.TimeStep ) 
		)
	else
		@expression(m, TotalExportBenefit, 0.0)
		@expression(m, TotalProductionIncentive, 0.0)
		@expression(m, ExportedElecWIND, 0.0)
		@expression(m, ExportedElecGEN, 0.0)
		@expression(m, ExportBenefitYr1, 0.0)
	end
	
	@expression(m, TotalEnergyChargesUtil, p.pwf_e * p.TimeStepScaling * 
		sum( p.ElecRate[u,ts] * m[:dvGridPurchase][u,ts] for ts in p.TimeStep, u in p.PricingTier ) 
	)
	@expression(m, TotalGenFuelCharges, p.pwf_e * p.TimeStepScaling * sum( p.FuelCost[f] *
		sum(m[:dvFuelUsage][t,ts] for t in p.TechsByFuelType[f], ts in p.TimeStep)
		for f in p.FuelType)
	)

	if !isempty(p.DemandRates)
		@expression(m, DemandTOUCharges, p.pwf_e * sum( p.DemandRates[r,e] * m[:dvPeakDemandE][r,e] for r in p.Ratchets, e in p.DemandBin) )
	else
		@expression(m, DemandTOUCharges, 0)
	end

	if !isempty(p.DemandRatesMonth)
		@expression(m, DemandFlatCharges, p.pwf_e * sum( p.DemandRatesMonth[mth,n] * m[:dvPeakDemandEMonth][mth,n] for mth in p.Month, n in p.DemandMonthsBin) )
	else
		@expression(m, DemandFlatCharges, 0)
	end

    @expression(m, TotalDemandCharges, DemandTOUCharges + DemandFlatCharges)
    TotalFixedCharges = p.pwf_e * p.FixedMonthlyCharge * 12
		
	### Constraint (13): Annual minimum charge adder 
	if p.AnnualMinCharge > 12 * p.MonthlyMinCharge
        TotalMinCharge = p.AnnualMinCharge 
    else
        TotalMinCharge = 12 * p.MonthlyMinCharge
    end
	
	if TotalMinCharge >= 1e-2
        @constraint(m, MinChargeAddCon, m[:MinChargeAdder] >= TotalMinCharge - ( 
			TotalEnergyChargesUtil + TotalDemandCharges + TotalExportBenefit + TotalFixedCharges)
		)
	else
		@constraint(m, MinChargeAddCon, m[:MinChargeAdder] == 0)
    end
	
	###  New Objective Function
	@expression(m, REcosts,
		# Capital Costs
		TotalTechCapCosts + TotalStorageCapCosts +  
		
		## Fixed O&M, tax deductible for owner
		TotalPerUnitSizeOMCosts * r_tax_fraction_owner +

        ## Variable O&M, tax deductible for owner
		TotalPerUnitProdOMCosts * r_tax_fraction_owner +

		# Utility Bill, tax deductible for offtaker
		(TotalEnergyChargesUtil + TotalDemandCharges + TotalExportBenefit + TotalFixedCharges + 0.999*m[:MinChargeAdder]) * r_tax_fraction_offtaker +
        
        ## Total Generator Fuel Costs, tax deductible for offtaker
        TotalGenFuelCharges * r_tax_fraction_offtaker -
                
        # Subtract Incentives, which are taxable
		TotalProductionIncentive * r_tax_fraction_owner
	)
    #= Note: 0.9999*m[:MinChargeAdder] in Obj b/c when TotalMinCharge > (TotalEnergyCharges + TotalDemandCharges + TotalExportBenefit + TotalFixedCharges)
		it is arbitrary where the min charge ends up (eg. could be in TotalDemandCharges or m[:MinChargeAdder]).
		0.0001*m[:MinChargeAdder] is added back into LCC when writing to results.  =#
	
    if Obj == 1
		@objective(m, Min, REcosts)
	elseif Obj == 2  # Keep SOC high
		@objective(m, Min, REcosts - sum(m[:dvStorageSOC]["Elec",ts] for ts in p.TimeStep)/8760.)
	end
	
	results["julia_reopt_constriants_seconds"] = time() - t_start
	t_start = time()

	optimize!(m)

	results["julia_reopt_optimize_seconds"] = time() - t_start
	t_start = time()

	if termination_status(m) == MOI.TIME_LIMIT
		status = "timed-out"
    elseif termination_status(m) == MOI.OPTIMAL
        status = "optimal"
    else
        status = "not optimal"
    end
    
	##############################################################################
    #############  		Outputs    									 #############
    ##############################################################################
    #ProdLoad = ["1R", "1W", "1X", "1S"]
    @expression(m, Year1WindProd, p.TimeStepScaling * sum(m[:dvRatedProduction][t,ts] * p.ProductionFactor[t, ts] 
                                            for t in WindTechs, ts in p.TimeStep))
    @expression(m, AverageWindProd, p.TimeStepScaling * sum(m[:dvRatedProduction][t,ts] * p.ProductionFactor[t, ts] * p.LevelizationFactor[t]
                                              for t in WindTechs, ts in p.TimeStep))

    @expression(m, Year1GenProd, p.TimeStepScaling * sum(m[:dvRatedProduction][t,ts] * p.ProductionFactor[t, ts] 
                       for t in GeneratorTechs, ts in p.TimeStep))
    @expression(m, AverageGenProd, p.TimeStepScaling * sum(m[:dvRatedProduction][t,ts] * p.ProductionFactor[t, ts] * p.LevelizationFactor[t]
					   for t in GeneratorTechs, ts in p.TimeStep))
						

	@expression(m, GenPerUnitSizeOMCosts, p.two_party_factor * 
		sum(p.OMperUnitSize[t] * p.pwf_om * m[:dvSize][t] for t in GeneratorTechs)
	)
	@expression(m, GenPerUnitProdOMCosts, p.two_party_factor * 
		sum(m[:dvRatedProduction][t,ts] * p.TimeStepScaling * p.ProductionFactor[t,ts] * p.OMcostPerUnitProd[t] * p.pwf_om
			for t in GeneratorTechs, ts in p.TimeStep)
	)

    @expression(m, Year1UtilityEnergy,  p.TimeStepScaling * sum(
		m[:dvGridPurchase][u,ts] for ts in p.TimeStep, u in p.PricingTier)
		)	
	
	try
		results["lcc"] = round(JuMP.objective_value(m)+ 0.0001*value(m[:MinChargeAdder]))
	catch
		results["status"] = "not optimal"
		return results
	end

    Year1EnergyCost = TotalEnergyChargesUtil / p.pwf_e
    Year1DemandCost = TotalDemandCharges / p.pwf_e
    Year1DemandTOUCost = DemandTOUCharges / p.pwf_e
    Year1DemandFlatCost = DemandFlatCharges / p.pwf_e
    Year1FixedCharges = TotalFixedCharges / p.pwf_e
    Year1MinCharges = m[:MinChargeAdder] / p.pwf_e
    Year1Bill = Year1EnergyCost + Year1DemandCost + Year1FixedCharges + Year1MinCharges

    results["batt_kwh"] = value(m[:dvStorageCapEnergy]["Elec"])
    results["batt_kw"] = value(m[:dvStorageCapPower]["Elec"])

    if results["batt_kwh"] != 0
    	@expression(m, soc[ts in p.TimeStep], m[:dvStorageSOC]["Elec",ts] / results["batt_kwh"])
        results["year_one_soc_series_pct"] = value.(soc)
    else
        results["year_one_soc_series_pct"] = []
    end
	
    if !isempty(WindTechs)
        results["Wind"] = Dict()
        results["wind_kw"] = round(value(sum(m[:dvSize][t] for t in WindTechs)), digits=4)
        #@expression(m, WINDtoBatt[ts in p.TimeStep],
        #            sum(m[:dvProductionToStorage][b, t, ts] for t in WindTechs, b in p.ElecStorage))
		WINDtoBatt = 0.0*Array{Float64,1}(undef,p.TimeStepCount)
		for ts in p.TimeStep
			for t in WindTechs
				for b in p.ElecStorage
					WINDtoBatt[ts] += value(m[:dvProductionToStorage][b, t, ts]) 
				end
			end
		end
	end

	results["gen_net_fixed_om_costs"] = 0
	results["gen_net_variable_om_costs"] = 0
	results["gen_total_fuel_cost"] = 0
	results["gen_year_one_fuel_cost"] = 0
	results["gen_year_one_variable_om_costs"] = 0

    if !isempty(GeneratorTechs)
    	if value(sum(m[:dvSize][t] for t in GeneratorTechs)) > 0
			results["Generator"] = Dict()
            results["generator_kw"] = value(sum(m[:dvSize][t] for t in GeneratorTechs))
			results["gen_net_fixed_om_costs"] = round(value(GenPerUnitSizeOMCosts) * r_tax_fraction_owner, digits=0)
			results["gen_net_variable_om_costs"] = round(value(GenPerUnitProdOMCosts) * r_tax_fraction_owner, digits=0)
	        results["gen_total_fuel_cost"] = round(value(TotalGenFuelCharges) * r_tax_fraction_offtaker, digits=2)
	        results["gen_year_one_fuel_cost"] = round(value(TotalGenFuelCharges) / p.pwf_e, digits=2)
	        results["gen_year_one_variable_om_costs"] = round(value(GenPerUnitProdOMCosts) / (p.pwf_om * p.two_party_factor), digits=0)
	        results["gen_year_one_fixed_om_costs"] = round(value(GenPerUnitSizeOMCosts) / (p.pwf_om * p.two_party_factor), digits=0)
		end
    end
	
    net_capital_costs_plus_om = value(TotalTechCapCosts + TotalStorageCapCosts) +
                                value(TotalPerUnitSizeOMCosts + TotalPerUnitProdOMCosts) * r_tax_fraction_owner +
                                value(TotalGenFuelCharges) * r_tax_fraction_offtaker

    push!(results, Dict("year_one_utility_kwh" => round(value(Year1UtilityEnergy), digits=2),
						 "year_one_energy_cost" => round(value(Year1EnergyCost), digits=2),
						 "year_one_demand_cost" => round(value(Year1DemandCost), digits=2),
						 "year_one_demand_tou_cost" => round(value(Year1DemandTOUCost), digits=2),
						 "year_one_demand_flat_cost" => round(value(Year1DemandFlatCost), digits=2),
						 "year_one_export_benefit" => round(value(ExportBenefitYr1), digits=0),
						 "year_one_fixed_cost" => round(Year1FixedCharges, digits=0),
						 "year_one_min_charge_adder" => round(value(Year1MinCharges), digits=2),
						 "year_one_bill" => round(value(Year1Bill), digits=2),
						 "year_one_payments_to_third_party_owner" => round(value(TotalDemandCharges) / p.pwf_e, digits=0),
						 "total_energy_cost" => round(value(TotalEnergyChargesUtil) * r_tax_fraction_offtaker, digits=2),
						 "total_demand_cost" => round(value(TotalDemandCharges) * r_tax_fraction_offtaker, digits=2),
						 "total_fixed_cost" => round(TotalFixedCharges * r_tax_fraction_offtaker, digits=2),
						 "total_export_benefit" => round(value(TotalExportBenefit) * r_tax_fraction_offtaker, digits=2),
						 "total_min_charge_adder" => round(value(m[:MinChargeAdder]) * r_tax_fraction_offtaker, digits=2),
						 "total_payments_to_third_party_owner" => 0,
						 "net_capital_costs_plus_om" => round(net_capital_costs_plus_om, digits=0),
						 "year_one_wind_energy_produced" => round(value(Year1WindProd), digits=0),
						 "average_wind_energy_produced" => round(value(AverageWindProd), digits=0),
						 "average_annual_energy_exported_wind" => round(value(ExportedElecWIND), digits=0),
                         "year_one_gen_energy_produced" => round(value(Year1GenProd), digits=0),
                         "average_yearly_gen_energy_produced" => round(value(AverageGenProd), digits=0),
                         "average_annual_energy_exported_gen" => round(value(ExportedElecGEN), digits=0),
						 "net_capital_costs" => round(value(TotalTechCapCosts + TotalStorageCapCosts), digits=2))...)

    @expression(m, GeneratorFuelUsed, sum(m[:dvFuelUsage][t, ts] for t in GeneratorTechs, ts in p.TimeStep))
    results["fuel_used_gal"] = round(value(GeneratorFuelUsed), digits=2)

    @expression(m, GridToBatt[ts in p.TimeStep], m[:dvGridToStorage][ts])
    results["GridToBatt"] = round.(value.(GridToBatt), digits=3)

    @expression(m, GridToLoad[ts in p.TimeStep],
                sum(m[:dvGridPurchase][u,ts] for u in p.PricingTier) - m[:dvGridToStorage][ts] )
    results["GridToLoad"] = round.(value.(GridToLoad), digits=3)

	if !isempty(GeneratorTechs)
		@expression(m, GENERATORtoBatt[ts in p.TimeStep],
					sum(m[:dvProductionToStorage]["Elec",t,ts] for t in GeneratorTechs))
    	results["GENERATORtoBatt"] = round.(value.(GENERATORtoBatt), digits=3)

		@expression(m, GENERATORtoGrid[ts in p.TimeStep],
					sum(m[:dvProductionToGrid][t,u,ts] for t in GeneratorTechs, u in p.SalesTiersByTech[t]))
		results["GENERATORtoGrid"] = round.(value.(GENERATORtoGrid), digits=3)

		@expression(m, GENERATORtoLoad[ts in p.TimeStep],
					sum(m[:dvRatedProduction][t, ts] * p.ProductionFactor[t, ts] * p.LevelizationFactor[t]
						for t in GeneratorTechs) - 
						GENERATORtoBatt[ts] - GENERATORtoGrid[ts]
						)
		results["GENERATORtoLoad"] = round.(value.(GENERATORtoLoad), digits=3)
    else
    	results["GENERATORtoBatt"] = []
		results["GENERATORtoGrid"] = []
		results["GENERATORtoLoad"] = []
	end
	
	PVclasses = filter(tc->startswith(tc, "PV"), p.TechClass)
    for PVclass in PVclasses
		PVtechs_in_class = filter(t->startswith(t, PVclass), PVTechs)
		
		if !isempty(PVtechs_in_class)
			
			results[string(PVclass, "_kw")] = round(value(sum(m[:dvSize][t] for t in PVtechs_in_class)), digits=4)
			
			# NOTE: must use anonymous expressions in this loop to overwrite values for cases with multiple PV
            if !isempty(p.ElecStorage)			
				PVtoBatt = @expression(m, [ts in p.TimeStep],
					sum(m[:dvProductionToStorage][b, t, ts] for t in PVtechs_in_class, b in p.ElecStorage))
			else
				PVtoBatt = @expression(m, [ts in p.TimeStep], 0.0)
            end
			results[string(PVclass, "toBatt")] = round.(value.(PVtoBatt), digits=3)
			
			PVtoGrid = @expression(m, [ts in p.TimeStep],
					sum(m[:dvProductionToGrid][t,u,ts] for t in PVtechs_in_class, u in p.SalesTiersByTech[t]))
    	    results[string(PVclass, "toGrid")] = round.(value.(PVtoGrid), digits=3)
			
			PVtoLoad = @expression(m, [ts in p.TimeStep],
				sum(m[:dvRatedProduction][t, ts] * p.ProductionFactor[t, ts] * p.LevelizationFactor[t] for t in PVtechs_in_class) 
				- PVtoGrid[ts] - PVtoBatt[ts]
				)
			
            results[string(PVclass, "toLoad")] = round.(value.(PVtoLoad), digits=3)
			
			Year1PvProd = @expression(m, sum(m[:dvRatedProduction][t,ts] * p.ProductionFactor[t, ts] 
				for t in PVtechs_in_class, ts in p.TimeStep) * p.TimeStepScaling)
			results[string("year_one_energy_produced_", PVclass)] = round(value(Year1PvProd), digits=0)

			AveragePvProd = @expression(m, sum(m[:dvRatedProduction][t,ts] * p.ProductionFactor[t, ts] * p.LevelizationFactor[t] 
			    for t in PVtechs_in_class, ts in p.TimeStep) * p.TimeStepScaling)
            results[string("average_yearly_energy_produced_", PVclass)] = round(value(AveragePvProd), digits=0)

			ExportedElecPV = @expression(m, sum(m[:dvProductionToGrid][t,u,ts] 
				for t in PVtechs_in_class, u in p.SalesTiersByTech[t], ts in p.TimeStep) * p.TimeStepScaling)
            results[string("average_annual_energy_exported_", PVclass)] = round(value(ExportedElecPV), digits=0)

            PVPerUnitSizeOMCosts = @expression(m, sum(p.OMperUnitSize[t] * p.pwf_om * m[:dvSize][t] for t in PVtechs_in_class))
            results[string(PVclass, "_net_fixed_om_costs")] = round(value(PVPerUnitSizeOMCosts) * r_tax_fraction_owner, digits=0)
        end
    end
	
	if !isempty(WindTechs)
		@expression(m, WINDtoGrid[ts in p.TimeStep],
					sum(m[:dvProductionToGrid][t,u,ts] for t in WindTechs, u in p.SalesTiers))
		results["WINDtoGrid"] = round.(value.(WINDtoGrid), digits=3)
		@expression(m, WINDtoLoad[ts in p.TimeStep],
					sum(m[:dvRatedProduction][t, ts] * p.ProductionFactor[t, ts] * p.LevelizationFactor[t]
						for t in WindTechs) - WINDtoGrid[ts] - WINDtoBatt[ts] )
		results["WINDtoLoad"] = round.(value.(WINDtoLoad), digits=3)

	else
		results["WINDtoLoad"] = []
    	results["WINDtoGrid"] = []
	end

	if termination_status(m) == MOI.TIME_LIMIT
		status = "timed-out"
    elseif termination_status(m) == MOI.OPTIMAL
        status = "optimal"
    else
        status = "not optimal"
    end

    results["status"] = status
	results["julia_reopt_postprocess_seconds"] = time() - t_start
	return results
end