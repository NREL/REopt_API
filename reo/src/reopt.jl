using JuMP
import MathOptInterface
const MOI = MathOptInterface
include("utils.jl")


function reopt(reo_model, data, model_inputs)

    p = Parameter(model_inputs)
    MAXTIME = data["inputs"]["Scenario"]["timeout_seconds"]

    return reopt_run(reo_model, MAXTIME, p)
end

function reopt_run(reo_model, MAXTIME::Int64, p::Parameter)
	
	REopt = reo_model
    Obj = 1  # 1 for minimize LCC, 2 for min LCC AND high mean SOC
	
	## Big-M adjustments; these need not be replaced in the parameter object.
	
	NewMaxUsageInTier = Array{Float64,2}(undef,12, p.PricingTierCount+1)
	NewMaxDemandInTier = Array{Float64,2}(undef, length(p.Ratchets), p.DemandBinCount)
	NewMaxDemandMonthsInTier = Array{Float64,2}(undef,12, p.DemandMonthsBinCount)
	NewMaxSize = Dict()
	NewMaxSizeByHour = Array{Float64,2}(undef,length(p.Tech),p.TimeStepCount)
	# NewMaxDemandMonthsInTier sets a new minimum if the new peak demand for the month, minus the size of all previous bins, is less than the existing bin size.
	if !isempty(p.ElecStorage)
		added_power = p.StorageMaxSizePower["Elec"]
		added_energy = p.StorageMaxSizeEnergy["Elec"]
	else
		added_power = 1.0e-3
		added_energy = 1.0e-3
	end
	
	for n in p.DemandMonthsBin
		for m in p.Month 
			if n > 1
				NewMaxDemandMonthsInTier[m,n] = minimum([p.MaxDemandMonthsInTier[n], 
					added_power + maximum([p.ElecLoad[ts] #+ LoadProfileChillerElectric[ts]
					for ts in p.TimeStepRatchetsMonth[m]])  - 
					sum(NewMaxDemandMonthsInTier[m,np] for np in 1:(n-1)) ]
				)
			else 
				NewMaxDemandMonthsInTier[m,n] = minimum([p.MaxDemandMonthsInTier[n], 
					added_power + maximum([p.ElecLoad[ts] #+ LoadProfileChillerElectric[ts]
					for ts in p.TimeStepRatchetsMonth[m]])   ])
			end
		end
	end
	
	# NewMaxDemandInTier sets a new minimum if the new peak demand for the ratchet, minus the size of all previous bins for the ratchet, is less than the existing bin size.
	for e in p.DemandBin
		for r in p.Ratchets 
			if e > 1
				NewMaxDemandInTier[r,e] = minimum([p.MaxDemandInTier[e], 
				added_power + maximum([p.ElecLoad[ts] #+ p.LoadProfileChillerElectric[ts]
					for ts in p.TimeStep])  - 
				sum(NewMaxDemandInTier[r,ep] for ep in 1:(e-1))
				])
			else
				NewMaxDemandInTier[r,e] = minimum([p.MaxDemandInTier[e], 
				added_power + maximum([p.ElecLoad[ts] #+ p.LoadProfileChillerElectric[ts]
					for ts in p.TimeStep])  
				])
			end
		end
	end
	
	# NewMaxUsageInTier sets a new minumum if the total demand for the month, minus the size of all previous bins, is less than the existing bin size.
	for u in p.PricingTier
		for m in p.Month 
			if u > 1
				NewMaxUsageInTier[m,u] = minimum([p.MaxUsageInTier[u], 
					added_energy + sum(p.ElecLoad[ts] #+ p.LoadProfileChillerElectric[ts]
					for ts in p.TimeStepRatchetsMonth[m]) - sum(NewMaxUsageInTier[m,up] for up in 1:(u-1))
				])
			else
				NewMaxUsageInTier[m,u] = minimum([p.MaxUsageInTier[u], 
					added_energy + sum(p.ElecLoad[ts] #+ p.LoadProfileChillerElectric[ts]
					for ts in p.TimeStepRatchetsMonth[m])  
				])
			end
		end
	end
	
	# NewMaxSize generates a new maximum size that is equal to the largest monthly load of the year.  This is intended to be a reasonable upper bound on size that would never be exceeeded, but is sufficienctly small to replace much larger big-M values placed as a default.
	TempHeatingTechs = [] #temporarily replace p.HeatingTechs which is undefined
	TempCoolingTechs = [] #temporarily replace p.CoolingTechs which is undefined
	
	for t in TempHeatingTechs
		NewMaxSize[t] = maximum([sum(p.HeatingLoad[ts] for ts in p.TimeStepRatchetsMonth[m]) for m in p.Month])
		if (NewMaxSize[t] > p.MaxSize[t])
			NewMaxSize[t] = p.MaxSize[t]
		end
	end
	for t in TempCoolingTechs
		NewMaxSize[t] = maximum([sum(p.CoolingLoad[ts] for ts in p.TimeStepRatchetsMonth[m]) for m in p.Month])
		if (NewMaxSize[t] > p.MaxSize[t])
			NewMaxSize[t] = p.MaxSize[t]
		end
	end
	for t in p.ElectricTechs
		NewMaxSize[t] = maximum([sum(p.ElecLoad[ts] for ts in p.TimeStepRatchetsMonth[m]) for m in p.Month])
		if (NewMaxSize[t] > p.MaxSize[t])
			NewMaxSize[t] = p.MaxSize[t]
		end
	end
	
	# NewMaxSizeByHour is designed to scale the right-hand side of the constraint limiting rated production in each hour to the production factor; in most cases this is unaffected unless the production factor is zero, in which case the right-hand side is set to zero.
	#for t in p.ElectricTechs 
	#	for ts in p.TimeStep
	#		NewMaxSizeByHour[t,ts] = minimum([NewMaxSize[t],
	#			sum(p.ProdFactor[t,d,ts] for d in p.Load if p.LoadProfile[d,ts] > 0)  * NewMaxSize[t],
	#			sum(p.LoadProfile[d,ts] for d in ["1R"], ts in p.TimeStep)  
	#		])
	#	end
	#end	
	
    @variables REopt begin
		# Continuous Variables
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
		dvFuelUsage[p.Tech, p.TimeStep]  # Fuel burned by technology t in time step h
		#dvFuelBurnYIntercept[p.Tech, p.TimeStep]  #X^{fb}_{th}: Y-intercept of fuel burned by technology t in time step h
		#dvThermalProduction[p.Tech, p.TimeStep]  #X^{tp}_{th}: Thermal production by technology t in time step h
		#dvAbsorptionChillerDemand[p.TimeStep]  #X^{ac}_h: Thermal power consumption by absorption chiller in time step h
		#dvElectricChillerDemand[p.TimeStep]  #X^{ec}_h: Electrical power consumption by electric chiller in time step h
		
		# Binary Variables
        binNMLorIL[p.NMILRegime], Bin    # Z^{nmil}_{v}: 1 If generation is in net metering interconnect limit regime v; 0 otherwise
        binProdIncent[p.Tech], Bin # Z^{pi}_{t}:  1 If production incentive is available for technology t; 0 otherwise 
		binSegmentSelect[p.Tech, p.Subdivision, p.Seg], Bin # Z^{\sigma s}_{tks} 1 if technology t, segmentation k is in segment s; 0 ow. (NEW)
        binSingleBasicTech[p.Tech,p.TechClass], Bin   #  Z^\text{sbt}_{tc}: 1 If technology t is used for technology class c; 0 otherwise
        binTechIsOnInTS[p.Tech, p.TimeStep], Bin  # 1 Z^{to}_{th}: If technology t is operating in time step h; 0 otherwise
		binDemandTier[p.Ratchets, p.DemandBin], Bin  # 1 If tier e has allocated demand during ratchet r; 0 otherwise
        binDemandMonthsTier[p.Month, p.DemandMonthsBin], Bin # 1 If tier n has allocated demand during month m; 0 otherwise
		binEnergyTier[p.Month, p.PricingTier], Bin    #  Z^{ut}_{mu} 1 If demand tier $u$ is active in month m; 0 otherwise (NEW)
    end
		
    ##############################################################################
	#############  		Constraints									 #############
	##############################################################################
	
	## Temporary workaround for outages TimeStepsWithoutGrid
	for ts in p.TimeStepsWithoutGrid
		fix(dvGridToStorage[ts], 0.0, force=true)
		for u in p.PricingTier
			fix(dvGridPurchase[u,ts], 0.0, force=true)
		end
		#for u in p.StorageSalesTiers  #don't allow curtailment of storage either
		#	fix(dvStorageToGrid[u,ts], 0.0, force=true)
		#end
	end
	
	#don't allow curtailment or sales of stroage 
	for ts in p.TimeStep
		for u in p.StorageSalesTiers
			fix(dvStorageToGrid[u,ts], 0.0, force=true)
		end
	end

					
	##Constraint (1a): Sum of fuel used must not exceed prespecified limits
	@constraint(REopt, TotalFuelConsumptionCon[f in p.FuelType],
				sum( dvFuelUsage[t,ts] for t in p.TechsByFuelType[f], ts in p.TimeStep ) <= 
				p.FuelLimit[f]
				)
	
	# Constraint (1b): Fuel burn for non-CHP Constraints
	@constraint(REopt, FuelBurnCon[t in p.FuelBurningTechs, ts in p.TimeStep],
				dvFuelUsage[t,ts]  == (p.FuelBurnSlope[t] * p.ProductionFactor[t,ts] * dvRatedProduction[t,ts]) + 
					(p.FuelBurnYInt[t] * binTechIsOnInTS[t,ts])
				)
	
	#if !isempty(CHPTechs)
		#Constraint (1c): Total Fuel burn for CHP
		#@constraint(REopt, CHPFuelBurnCon[t in CHPTechs, ts in p.TimeStep],
		#			dvFuelUsage[t,ts]  == p.FuelBurnAmbientFactor[t,ts] * (dvFuelBurnYIntercept[t,th] +  
		#				p.ProductionFactor[t,ts] * p.FuelBurnRateM[t] * dvRatedProduction[t,ts]) 					
		#			)
					
		#Constraint (1d): Y-intercept fuel burn for CHP
		#@constraint(REopt, CHPFuelBurnYIntCon[t in CHPTechs, ts in p.TimeStep],
		#			p.FuelBurnYIntRate[t] * dvSize[t] - NewMaxSize[t] * (1-binTechIsOnInTS[t,ts])  <= dvFuelBurnYIntercept[t,th]   					
		#			)
	#end
	
	#if !isempty(NonCHPHeatingTechs)
		#Constraint (1e): Total Fuel burn for Boiler
		#@constraint(REopt, BoilerFuelBurnCon[t in NonCHPHeatingTechs, ts in p.TimeStep],
		#			dvFuelUsage[t,ts]  ==  dvThermalProduction[t,ts] / p.BoilerEfficiency 					
		#			)
	#end
	
	
	### Constraint set (2): CHP Thermal Production Constraints
	#if !isempty(CHPTechs)
		#Constraint (2a-1): Upper Bounds on Thermal Production Y-Intercept 
		#@constraint(REopt, CHPYInt2a1Con[t in CHPTechs, ts in p.TimeStep],
		#			dvThermalProductionYIntercept[t,ts] <= CHPThermalProdIntercept[t] * dvSize[t]
		#			)
		# Constraint (2a-2): Upper Bounds on Thermal Production Y-Intercept 
		#@constraint(REopt, CHPYInt2a1Con[t in CHPTechs, ts in p.TimeStep],
		#			dvThermalProductionYIntercept[t,ts] <= CHPThermalProdIntercept[t] * NewMaxSize[t] * binTechIsOnInTS[t,ts]
		#			)
		# Constraint (2b): Thermal Production of CHP 
		#@constraint(REopt, CHPThermalProductionCpn[t in CHPTechs, ts in p.TimeStep],
		#			dvThermalProduction[t,ts] <=  HotWaterAmbientFactor[t,ts] * HotWaterThermalFactor[t,ts] * (
		#			CHPThermalProdSlope[t] * ProductionFactor[t,ts] * dvRatedProduction[t,ts] + dvThermalProductionYIntercept[t,ts]
		#				)
		#			)
	#end
	
	
	### Section 3: Switch Constraints
	#Constraint (3a): Technology must be on for nonnegative output (fuel-burning only)
	@constraint(REopt, ProduceIfOnCon[t in p.FuelBurningTechs, ts in p.TimeStep],
				dvRatedProduction[t,ts] <= NewMaxSize[t] * binTechIsOnInTS[t,ts])
	#Constraint (3b): Technologies that are turned on must not be turned down
	@constraint(REopt, MinTurndownCon[t in p.FuelBurningTechs, ts in p.TimeStep],
			  p.MinTurndown[t] * dvSize[t] - dvRatedProduction[t,ts] <= NewMaxSize[t] * (1-binTechIsOnInTS[t,ts]) )
	
    ### Section 4: Storage System Constraints
	### 
	### Boundary Conditions and Size Limits
	# Constraint (4a): Reconcile initial state of charge for storage systems
	@constraint(REopt, InitStorageCon[b in p.Storage], dvStorageSOC[b,0] == p.StorageInitSOC[b] * dvStorageCapEnergy[b])
	# Constraint (4b)-1: Lower bound on Storage Energy Capacity
	@constraint(REopt, StorageEnergyLBCon[b in p.Storage], dvStorageCapEnergy[b] >= p.StorageMinSizeEnergy[b])
	# Constraint (4b)-2: Upper bound on Storage Energy Capacity
	@constraint(REopt, StorageEnergyUBCon[b in p.Storage], dvStorageCapEnergy[b] <= p.StorageMaxSizeEnergy[b])
	# Constraint (4c)-1: Lower bound on Storage Power Capacity
	@constraint(REopt, StoragePowerLBCon[b in p.Storage], dvStorageCapPower[b] >= p.StorageMinSizePower[b])
	# Constraint (4c)-2: Upper bound on Storage Power Capacity
	@constraint(REopt, StoragePowerUBCon[b in p.Storage], dvStorageCapPower[b] <= p.StorageMaxSizePower[b])
	
	### Battery Operations
	# Constraint (4d): Electrical production sent to storage or grid must be less than technology's rated production
	@constraint(REopt, ElecTechProductionFlowCon[b in p.ElecStorage, t in p.ElectricTechs, ts in p.TimeStepsWithGrid],
    	        dvProductionToStorage[b,t,ts] + sum(dvProductionToGrid[t,u,ts] for u in p.SalesTiersByTech[t]) <= 
				p.ProductionFactor[t,ts] * p.LevelizationFactor[t] * dvRatedProduction[t,ts]
				)
	# Constraint (4e): Electrical production sent to storage or grid must be less than technology's rated production - no grid
	@constraint(REopt, ElecTechProductionFlowNoGridCon[b in p.ElecStorage, t in p.ElectricTechs, ts in p.TimeStepsWithoutGrid],
    	        dvProductionToStorage[b,t,ts]  <= 
				p.ProductionFactor[t,ts] * p.LevelizationFactor[t] * dvRatedProduction[t,ts]
				)
	# Constraint (4f)-1: (Hot) Thermal production sent to storage or grid must be less than technology's rated production
	#@constraint(REopt, HeatingTechProductionFlowCon[b in p.HotTES, t in p.HeatingTechs, ts in p.TimeStep],
    #	        dvProductionToStorage[b,t,ts]  <= 
	#			p.ProductionFactor[t,ts] * dvThermalProduction[t,ts]
	#			)
	# Constraint (4f)-2: (Cold) Thermal production sent to storage or grid must be less than technology's rated production
	#@constraint(REopt, CoolingTechProductionFlowCon[b in p.ColdTES, t in p.CoolingTechs, ts in p.TimeStep],
    #	        dvProductionToStorage[b,t,ts]  <= 
	#			p.ProductionFactor[t,ts] * dvThermalProduction[t,ts]
	#			)
	# Constraint (4g): Reconcile state-of-charge for electrical storage - with grid
	@constraint(REopt, ElecStorageInventoryCon[b in p.ElecStorage, ts in p.TimeStepsWithGrid],
    	        dvStorageSOC[b,ts] == dvStorageSOC[b,ts-1] + p.TimeStepScaling * (  
					sum(p.ChargeEfficiency[t,b] * dvProductionToStorage[b,t,ts] for t in p.ElectricTechs) + 
					p.GridChargeEfficiency*dvGridToStorage[ts] - dvDischargeFromStorage[b,ts]/p.DischargeEfficiency[b]
					)
				)
				
	# Constraint (4h): Reconcile state-of-charge for electrical storage - no grid
	@constraint(REopt, ElecStorageInventoryConNoGrid[b in p.ElecStorage, ts in p.TimeStepsWithoutGrid],
    	        dvStorageSOC[b,ts] == dvStorageSOC[b,ts-1] + p.TimeStepScaling * (  
					sum(p.ChargeEfficiency[t,b] * dvProductionToStorage[b,t,ts] for t in p.ElectricTechs) - dvDischargeFromStorage[b,ts]/p.DischargeEfficiency[b]
					)
				)
	
	# Constraint (4i)-1: Reconcile state-of-charge for (hot) thermal storage
	#@constraint(REopt, HotTESInventoryCon[b in p.HotTES, ts in p.TimeStep],
    #	        dvStorageSOC[b,ts] == dvStorageSOC[b,ts-1] + p.TimeStepScaling * (  
	#				sum(p.ChargeEfficiency[t,b] * dvProductionToStorage[b,t,ts] for t in p.HeatingTechs) - 
	#				dvDischargeFromStorage[b,ts]/p.DischargeEfficiency[b]
	#				)
	#			)
				
	# Constraint (4i)-2: Reconcile state-of-charge for (cold) thermal storage
	#@constraint(REopt, ColdTESInventoryCon[b in p.ColdTES, ts in p.TimeStep],
    #	        dvStorageSOC[b,ts] == dvStorageSOC[b,ts-1] + p.TimeStepScaling * (  
	#				sum(p.ChargeEfficiency[t,b] * dvProductionToStorage[b,t,ts] for t in p.CoolingTechs) - 
	#				dvDischargeFromStorage[b,ts]/p.DischargeEfficiency[b]
	#				)
	#			)
	
	# Constraint (4j): Minimum state of charge
	@constraint(REopt, MinStorageLevelCon[b in p.Storage, ts in p.TimeStep],
    	        dvStorageSOC[b,ts] >= p.StorageMinSOC[b] * dvStorageCapEnergy[b]
					)
	
	#Constraint (4i)-1: Dispatch to electrical storage is no greater than power capacity
	@constraint(REopt, ElecChargeLEQCapCon[b in p.ElecStorage, ts in p.TimeStep],
    	        dvStorageCapPower[b] >= (  
					sum(dvProductionToStorage[b,t,ts] for t in p.ElectricTechs) + dvGridToStorage[ts]
					)
				)
	
	#Constraint (4i)-2: Dispatch to hot storage is no greater than power capacity
	#@constraint(REopt, HotTESChargeLEQCapCon[b in p.HotTES, ts in p.TimeStep],
    #	        dvStorageCapPower[b] >= (  
	#				sum(dvProductionToStorage[b,t,ts] for t in p.HeatingTechs)
	#				)
	#			)
	
	#Constraint (4i)-3: Dispatch to cold storage is no greater than power capacity
	#@constraint(REopt, ColdTESChargeLEQCapCon[b in p.ColdTES, ts in p.TimeStep],
    #	        dvStorageCapPower[b] >= (  
	#				sum(dvProductionToStorage[b,t,ts] for t in p.CoolingTechs)
	#				)
	#			)
	
	#Constraint (4j): Dispatch from storage is no greater than power capacity
	@constraint(REopt, DischargeLEQCapCon[b in p.Storage, ts in p.TimeStep],
    	        dvStorageCapPower[b] >= dvDischargeFromStorage[b,ts]
				)
	
	#Constraint (4k)-alt: Dispatch to and from electrical storage is no greater than power capacity
	@constraint(REopt, ElecChargeLEQCapConAlt[b in p.ElecStorage, ts in p.TimeStepsWithGrid],
    	        dvStorageCapPower[b] >=   dvDischargeFromStorage[b,ts] + 
					sum(dvProductionToStorage[b,t,ts] for t in p.ElectricTechs) + dvGridToStorage[ts]
				)	
	#Constraint (4l)-alt: Dispatch from electrical storage is no greater than power capacity
	@constraint(REopt, DischargeLEQCapConNoGridAlt[b in p.ElecStorage, ts in p.TimeStepsWithoutGrid],
    	        dvStorageCapPower[b] >= dvDischargeFromStorage[b,ts] + 
					sum(dvProductionToStorage[b,t,ts] for t in p.ElectricTechs)
				)
				
	#Constraint (4m)-1: Dispatch from thermal storage is no greater than power capacity
	#@constraint(REopt, DischargeLEQCapCon[b in p.HotTES, ts in p.TimeStep],
    #	        dvStorageCapPower[b] >= sum(dvProductionToStorage[b,t,ts] for t in p.HeatingTechs)
	#			)
	#Constraint (4m)-2: Dispatch from thermal storage is no greater than power capacity
	#@constraint(REopt, DischargeLEQCapCon[b in p.ColdTES, ts in p.TimeStep],
    #	        dvStorageCapPower[b] >= sum(dvProductionToStorage[b,t,ts] for t in p.CoolingTechs)
	#			)
	

	#Constraint (4n): Discharge no greater than power capacity
	@constraint(REopt, StoragePowerCapCon[b in p.Storage, ts in p.TimeStep],
    	        dvDischargeFromStorage[b,ts] <= dvStorageCapPower[b]
					)
					
	#Constraint (4n): State of charge upper bound is storage system size
	@constraint(REopt, StorageEnergyMaxCapCon[b in p.Storage, ts in p.TimeStep],
				dvStorageSOC[b,ts] <= dvStorageCapEnergy[b]
					)
	
	### Constraint set (5) - hot and cold thermal loads - reserved for later
	
	### Constraint set (6): Production Incentive Cap
	##Constraint (6a)-1: Production Incentive Upper Bound (unchanged)
	@constraint(REopt, ProdIncentUBCon[t in p.Tech],
                dvProdIncent[t] <= binProdIncent[t] * p.MaxProdIncent[t] * p.pwf_prod_incent[t] * p.two_party_factor)
	##Constraint (6a)-2: Production Incentive According to Production (updated)
	@constraint(REopt, IncentByProductionCon[t in p.Tech],
                dvProdIncent[t] <= p.TimeStepScaling * p.ProductionIncentiveRate[t] * p.pwf_prod_incent[t] * p.two_party_factor * 
                                   sum(p.ProductionFactor[t, ts] * dvRatedProduction[t,ts] for ts in p.TimeStep)
                )
	##Constraint (6b): System size max to achieve production incentive
	@constraint(REopt, IncentBySystemSizeCon[t in p.Tech],
                dvSize[t]  <= p.MaxSizeForProdIncent[t] + NewMaxSize[t] * (1 - binProdIncent[t]))

    ### System Size and Production Constraints
	### Constraint set (7): System Size is zero unless single basic tech is selected for class
	if !isempty(p.Tech)

		# PV techs can be constrained by space available based on location at site (roof, ground, both)
		@constraint(REopt, TechMaxSizeByLocCon[loc in p.Location],
			sum( dvSize[t] * p.TechToLocation[t, loc] for t in p.Tech) <= p.MaxSizesLocation[loc]
		)

		#Constraint (7a): Single Basic Technology Constraints
		@constraint(REopt, TechMaxSizeByClassCon[c in p.TechClass, t in p.TechsInClass[c]],
			dvSize[t] <= NewMaxSize[t] * binSingleBasicTech[t,c]
			)
		##Constraint (7b): At most one Single Basic Technology per Class
		@constraint(REopt, TechClassMinSelectCon[c in p.TechClass],
			sum( binSingleBasicTech[t,c] for t in p.TechsInClass[c] ) <= 1
			)
		##Constraint (7c): Minimum size for each tech class
		@constraint(REopt, TechClassMinSizeCon[c in p.TechClass],
					sum( dvSize[t] for t in p.TechsInClass[c] ) >= p.TechClassMinSize[c]
				)
		
		## Constraint (7d): Non-turndown technologies are always at rated production
		@constraint(REopt, RenewableRatedProductionCon[t in p.TechsNoTurndown, ts in p.TimeStep],
			dvRatedProduction[t,ts] == dvSize[t]  
		)
			
		##Constraint (7e): Derate factor limits production variable (separate from ProdFactor)
		@constraint(REopt, TurbineRatedProductionCon[t in p.Tech, ts in p.TimeStep; !(t in p.TechsNoTurndown)],
			dvRatedProduction[t,ts]  <= p.ElectricDerate[t,ts] * dvSize[t]
		)
			
		##Constraint (7f)-1: Minimum segment size
		@constraint(REopt, SegmentSizeMinCon[t in p.Tech, k in p.Subdivision, s in 1:p.SegByTechSubdivision[k,t]],
			dvSystemSizeSegment[t,k,s]  >= p.SegmentMinSize[t,k,s] * binSegmentSelect[t,k,s]
		)
		
		##Constraint (7f)-2: Maximum segment size
		@constraint(REopt, SegmentSizeMaxCon[t in p.Tech, k in p.Subdivision, s in 1:p.SegByTechSubdivision[k,t]],
			dvSystemSizeSegment[t,k,s]  <= p.SegmentMaxSize[t,k,s] * binSegmentSelect[t,k,s]
		)
		
		##Constraint (7g):  Segments add up to system size 
		@constraint(REopt, SegmentSizeAddCon[t in p.Tech, k in p.Subdivision],
			sum(dvSystemSizeSegment[t,k,s] for s in 1:p.SegByTechSubdivision[k,t]) == dvSize[t]
		)
			
		##Constraint (7h): At most one segment allowed
		@constraint(REopt, SegmentSelectCon[c in p.TechClass, t in p.TechsInClass[c], k in p.Subdivision],
			sum(binSegmentSelect[t,k,s] for s in 1:p.SegByTechSubdivision[k,t]) <= binSingleBasicTech[t,c]
		)
	end

	### Constraint set (8): Electrical Load Balancing and Grid Sales
	##Constraint (8a): Electrical Load Balancing with Grid
	
	@constraint(REopt, ElecLoadBalanceCon[ts in p.TimeStepsWithGrid],
		sum(p.ProductionFactor[t,ts] * p.LevelizationFactor[t] * dvRatedProduction[t,ts] for t in p.ElectricTechs) +  
		sum( dvDischargeFromStorage[b,ts] for b in p.ElecStorage ) + 
		sum( dvGridPurchase[u,ts] for u in p.PricingTier ) ==
		sum( sum(dvProductionToStorage[b,t,ts] for b in p.ElecStorage) + 
			sum(dvProductionToGrid[t,u,ts] for u in p.SalesTiersByTech[t]) for t in p.ElectricTechs) +
		sum(dvStorageToGrid[u,ts] for u in p.StorageSalesTiers) + dvGridToStorage[ts] + 
		## sum(dvThermalProduction[t,ts] for t in p.CoolingTechs )/ p.ElectricChillerEfficiency +
		p.ElecLoad[ts]
	)
	
	##Constraint (8b): Electrical Load Balancing without Grid
	@constraint(REopt, ElecLoadBalanceNoGridCon[ts in p.TimeStepsWithoutGrid],
		sum(p.ProductionFactor[t,ts] * p.LevelizationFactor[t] * dvRatedProduction[t,ts] for t in p.ElectricTechs) +  
		sum( dvDischargeFromStorage[b,ts] for b in p.ElecStorage )  ==
		sum( sum(dvProductionToStorage[b,t,ts] for b in p.ElecStorage) + 
			sum(dvProductionToGrid[t,u,ts] for u in p.CurtailmentTiers) for t in p.ElectricTechs) +
		## sum(dvThermalProduction[t,ts] for t in p.CoolingTechs )/ p.ElectricChillerEfficiency +
		p.ElecLoad[ts]
	)
	
	##Constraint (8c): Grid-to-storage no greater than grid purchases 
	@constraint(REopt, GridToStorageCon[ts in p.TimeStepsWithGrid],
		sum( dvGridPurchase[u,ts] for u in p.PricingTier)  >= dvGridToStorage[ts]
	)
		
	##Constraint (8d): Storage-to-grid no greater than discharge from Storage
	@constraint(REopt, StorageToGridCon[ts in p.TimeStepsWithGrid],
		sum( dvDischargeFromStorage[b,ts] for b in p.ElecStorage)  >= sum(dvStorageToGrid[u,ts] for u in p.StorageSalesTiers)
	)
		
	if !isempty(p.SalesTiers)
		##Constraint (8e): Production-to-grid no greater than production
		@constraint(REopt, ProductionToGridCon[t in p.Tech, ts in p.TimeStepsWithGrid],
		 p.ProductionFactor[t,ts] * p.LevelizationFactor[t] * dvRatedProduction[t,ts] >= sum(dvProductionToGrid[t,u,ts] for u in p.SalesTiersByTech[t])
		)
		
		##Constraint (8f): Total sales to grid no greater than annual allocation - storage tiers
		@constraint(REopt,  AnnualGridSalesLimitCon,
		 p.TimeStepScaling * ( 
			sum( dvStorageToGrid[u,ts] for u in p.StorageSalesTiers, ts in p.TimeStepsWithGrid if !(u in p.CurtailmentTiers)) +  sum(dvProductionToGrid[t,u,ts] for u in p.SalesTiers, t in p.TechsBySalesTier[u], ts in p.TimeStepsWithGrid if !(u in p.CurtailmentTiers))) <= p.MaxGridSales[1]
		)
	end
	## End constraint (8)

    ### Constraint set (9): Net Meter Module (copied directly from legacy model)
	if !isempty(p.Tech)
		#Constraint (9a): exactly one net-metering regime must be selected
		@constraint(REopt, sum(binNMLorIL[n] for n in p.NMILRegime) == 1)
		
		##Constraint (9b): Maximum system sizes for each net-metering regime
		@constraint(REopt, NetMeterSizeLimit[n in p.NMILRegime],
					sum(p.TurbineDerate[t] * dvSize[t]
                    for t in p.TechsByNMILRegime[n]) <= p.NMILLimits[n] * binNMLorIL[n])
	end
	##Constraint (9c): Net metering only -- can't sell more than you purchase
	if !isempty(p.SalesTiers)
		@constraint(REopt, GridSalesLimit, 
				p.TimeStepScaling * sum(dvProductionToGrid[t,1,ts] for t in p.TechsBySalesTier[1], ts in p.TimeStep)  + 
				sum(dvStorageToGrid[u,ts] for u in p.StorageSalesTiers, ts in p.TimeStep) <= p.TimeStepScaling * 
				sum(dvGridPurchase[u,ts] for u in p.PricingTier, ts in p.TimeStep)
			)
	end
	###End constraint set (9)
	
	### Constraint set (10): Electrical Energy Demand Pricing Tiers
	##Constraint (10a): Usage limits by pricing tier, by month
	@constraint(REopt, [u in p.PricingTier, m in p.Month],
                p.TimeStepScaling * sum( dvGridPurchase[u, ts] for ts in p.TimeStepRatchetsMonth[m] ) <= binEnergyTier[m, u] * NewMaxUsageInTier[m,u])
	##Constraint (10b): Ordering of pricing tiers
	@constraint(REopt, [u in 2:p.FuelBinCount, m in p.Month],   #Need to fix, update purchase vs. sales pricing tiers
    	        binEnergyTier[m, u] - binEnergyTier[m, u-1] <= 0)
	## Constraint (10c): One tier must be full before any usage in next tier 
	@constraint(REopt, [u in 2:p.FuelBinCount, m in p.Month],
    	        binEnergyTier[m, u] * NewMaxUsageInTier[m,u-1] - sum( dvGridPurchase[u-1, ts] for ts in p.TimeStepRatchetsMonth[m] ) <= 0)
	
	#End constraint set (10)

	### Constraint set (11): Peak Electrical Power Demand Charges: Months
	## Constraint (11a): Upper bound on peak electrical power demand by tier, by month, if tier is selected (0 o.w.)
	@constraint(REopt, [n in p.DemandMonthsBin, m in p.Month],
                dvPeakDemandEMonth[m,n] <= NewMaxDemandMonthsInTier[m,n] * binDemandMonthsTier[m,n])
	
	## Constraint (11b): Monthly peak electrical power demand tier ordering
	@constraint(REopt, [m in p.Month, n in 2:p.DemandMonthsBinCount],
        	        binDemandMonthsTier[m, n] <= binDemandMonthsTier[m, n-1])
	
	## Constraint (11c): One monthly peak electrical power demand tier must be full before next one is active
	@constraint(REopt, [m in p.Month, n in 2:p.DemandMonthsBinCount],
        	 binDemandMonthsTier[m, n] * NewMaxDemandMonthsInTier[m,n-1] <= dvPeakDemandEMonth[m, n-1])
	
	## Constraint (11d): Monthly peak demand is >= demand at each hour in the month` 
	@constraint(REopt, [m in p.Month, ts in p.TimeStepRatchetsMonth[m]],
        	 sum( dvPeakDemandEMonth[m, n] for n in p.DemandMonthsBin ) >= 
			 sum( dvGridPurchase[u, ts] for u in p.PricingTier )
	)
	### End Constraint Set (11)
	
	### Constraint set (12): Peak Electrical Power Demand Charges: Ratchets
	if !isempty(p.TimeStepRatchets)
		## Constraint (12a): Upper bound on peak electrical power demand by tier, by ratchet, if tier is selected (0 o.w.)
		@constraint(REopt, [r in p.Ratchets, e in p.DemandBin],
		            dvPeakDemandE[r, e] <= NewMaxDemandInTier[r,e] * binDemandTier[r, e])
		
		## Constraint (12b): Ratchet peak electrical power ratchet tier ordering
		@constraint(REopt, [r in p.Ratchets, e in 2:p.DemandBinCount],
		    	        binDemandTier[r, e] <= binDemandTier[r, e-1])
		
		## Constraint (12c): One ratchet peak electrical power demand tier must be full before next one is active
		@constraint(REopt, [r in p.Ratchets, e in 2:p.DemandBinCount],
		    	 binDemandTier[r, e] * NewMaxDemandInTier[r,e-1] <= dvPeakDemandE[r, e-1])
		
		## Constraint (12d): Ratchet peak demand is >= demand at each hour in the ratchet` 
		@constraint(REopt, [r in p.Ratchets, ts in p.TimeStepRatchets[r]],
		    	 sum( dvPeakDemandE[r, e] for e in p.DemandBin ) >= 
				 sum( dvGridPurchase[u, ts] for u in p.PricingTier )
		)
		
		##Constraint (12e): Peak demand used in percent lookback calculation 
		@constraint(REopt, [m in p.DemandLookbackMonths],
			        dvPeakDemandELookback >= sum(dvPeakDemandEMonth[m, n] for n in p.DemandMonthsBin)
					)
		
		##Constraint (12f): Ratchet peak demand charge is bounded below by lookback
		@constraint(REopt, [r in p.DemandLookbackMonths],
					sum( dvPeakDemandEMonth[r,e] for e in p.DemandBin ) >= 
					p.DemandLookbackPercent * dvPeakDemandELookback )
	end
	### End Constraint Set (12)
		
	### Constraint (13): Annual minimum charge adder 
	if p.AnnualMinCharge > 12 * p.MonthlyMinCharge
        TotalMinCharge = p.AnnualMinCharge 
    else
        TotalMinCharge = 12 * p.MonthlyMinCharge
    end
	
	if TotalMinCharge >= 1e-2
        @constraint(REopt, MinChargeAddCon, MinChargeAdder >= TotalMinCharge - (
			#Demand Charges
			p.TimeStepScaling * sum( p.ElecRate[u,ts] * dvGridPurchase[u,ts] for ts in p.TimeStep, u in p.PricingTier ) +
			#Peak Ratchet Charges
			sum( p.DemandRates[r,e] * dvPeakDemandE[r,e] for r in p.Ratchets, e in p.DemandBin) + 
			#Preak Monthly Demand Charges
			sum( p.DemandRatesMonth[m,n] * dvPeakDemandEMonth[m,n] for m in p.Month, n in p.DemandMonthsBin) -
			# Energy Exports
			p.TimeStepScaling * sum( sum(p.GridExportRates[u,ts] * dvStorageToGrid[u,ts] for u in p.StorageSalesTiers) + sum(p.GridExportRates[u,ts] * dvProductionToGrid[t,u,ts] for u in p.SalesTiers, t in p.TechsBySalesTier[u]) for ts in p.TimeStep ) - 
			p.FixedMonthlyCharge * 12 )
		)
	else
		@constraint(REopt, MinChargeAddCon, MinChargeAdder == 0)
    end
	
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

	@expression(REopt, TotalTechCapCosts, p.two_party_factor * (
		sum( p.CapCostSlope[t,s] * dvSystemSizeSegment[t,"CapCost",s] for t in p.Tech, s in 1:p.SegByTechSubdivision["CapCost",t] ) + 
		sum( p.CapCostYInt[t,s] * binSegmentSelect[t,"CapCost",s] for t in p.Tech, s in 1:p.SegByTechSubdivision["CapCost",t] ) 
	))
	@expression(REopt, TotalStorageCapCosts, p.two_party_factor * 
		sum( p.StorageCostPerKW[b]*dvStorageCapPower[b] + p.StorageCostPerKWH[b]*dvStorageCapEnergy[b] for b in p.Storage )
	)
	@expression(REopt, TotalPerUnitSizeOMCosts, p.two_party_factor * p.pwf_om * 
		sum( p.OMperUnitSize[t] * dvSize[t] for t in p.Tech ) 
	)
    if !isempty(GeneratorTechs)
		@expression(REopt, TotalPerUnitProdOMCosts, p.two_party_factor * p.pwf_om * 
			sum( p.OMcostPerUnitProd[t] * dvRatedProduction[t,ts] for t in p.FuelBurningTechs, ts in p.TimeStep ) 
		)
    else
        @expression(REopt, TotalPerUnitProdOMCosts, 0.0)
	end

	### Utility and Taxable Costs
	if !isempty(p.Tech)
		@expression(REopt, TotalExportBenefit, -1 *p.pwf_e * p.TimeStepScaling * sum( 
			sum(p.GridExportRates[u,ts] * dvStorageToGrid[u,ts] for u in p.StorageSalesTiers) 
			+ sum(p.GridExportRates[u,ts] * dvProductionToGrid[t,u,ts] for u in p.SalesTiers, t in p.TechsBySalesTier[u]) 
			for ts in p.TimeStep ) 
		)
		@expression(REopt, TotalProductionIncentive, sum(dvProdIncent[t] for t in p.Tech))

		@expression(REopt, ExportedElecWIND,
					p.TimeStepScaling * sum(dvProductionToGrid[t,u,ts] 
						for t in WindTechs, u in p.SalesTiersByTech[t], ts in p.TimeStep))
		@expression(REopt, ExportedElecGEN,
					p.TimeStepScaling * sum(dvProductionToGrid[t,u,ts] 
						for t in GeneratorTechs, u in p.SalesTiersByTech[t], ts in p.TimeStep))        
		# Needs levelization factor?
		@expression(REopt, ExportBenefitYr1,
				p.TimeStepScaling * sum( sum( p.GridExportRates[u,ts] * dvStorageToGrid[u,ts] for u in p.StorageSalesTiers) + sum(dvProductionToGrid[t,u,ts] for u in p.SalesTiers, t in p.TechsBySalesTier[u]) for ts in p.TimeStep ) )
	else
		@expression(REopt, TotalExportBenefit, 0.0)
		@expression(REopt, TotalProductionIncentive, 0.0)
		@expression(REopt, ExportedElecWIND, 0.0)
		@expression(REopt, ExportedElecGEN, 0.0)
		@expression(REopt, ExportBenefitYr1,0.0)
	end
	
	@expression(REopt, TotalEnergyChargesUtil, p.pwf_e * p.TimeStepScaling * 
		sum( p.ElecRate[u,ts] * dvGridPurchase[u,ts] for ts in p.TimeStep, u in p.PricingTier ) 
	)
	@expression(REopt, TotalGenFuelCharges, p.pwf_e * p.TimeStepScaling * sum( p.FuelCost[f] *
		sum(dvFuelUsage[t,ts] for t in p.TechsByFuelType[f], ts in p.TimeStep)
		for f in p.FuelType)
	)
	@expression(REopt, DemandTOUCharges, p.pwf_e * sum( p.DemandRates[r,e] * dvPeakDemandE[r,e] for r in p.Ratchets, e in p.DemandBin) )
    @expression(REopt, DemandFlatCharges, p.pwf_e * sum( p.DemandRatesMonth[m,n] * dvPeakDemandEMonth[m,n] for m in p.Month, n in p.DemandMonthsBin) )
    @expression(REopt, TotalDemandCharges, DemandTOUCharges + DemandFlatCharges)
    @expression(REopt, TotalFixedCharges, p.pwf_e * p.FixedMonthlyCharge * 12 )
	
	###  New Objective Function
	@expression(REopt, REcosts,
		# Capital Costs
		TotalTechCapCosts + TotalStorageCapCosts +  
		
		## Fixed O&M, tax deductible for owner
		TotalPerUnitSizeOMCosts * r_tax_fraction_owner +

        ## Variable O&M, tax deductible for owner
		TotalPerUnitProdOMCosts * r_tax_fraction_owner +

		# Utility Bill, tax deductible for offtaker
		(TotalEnergyChargesUtil + TotalDemandCharges + TotalExportBenefit + TotalFixedCharges + 0.999*MinChargeAdder) * r_tax_fraction_offtaker +
        
        ## Total Generator Fuel Costs, tax deductible for offtaker
        TotalGenFuelCharges * r_tax_fraction_offtaker -
                
        # Subtract Incentives, which are taxable
		TotalProductionIncentive * r_tax_fraction_owner
	)
    #= Note: 0.9999*MinChargeAdder in Obj b/c when TotalMinCharge > (TotalEnergyCharges + TotalDemandCharges + TotalExportBenefit + TotalFixedCharges)
		it is arbitrary where the min charge ends up (eg. could be in TotalDemandCharges or MinChargeAdder).
		0.0001*MinChargeAdder is added back into LCC when writing to results.  =#
	
    if Obj == 1
		@objective(REopt, Min, REcosts)
	elseif Obj == 2  # Keep SOC high
		@objective(REopt, Min, REcosts - sum(dvStorageSOC["Elec",ts] for ts in p.TimeStep)/8760.)
	end
	
	optimize!(REopt)
	if termination_status(REopt) == MOI.TIME_LIMIT
		status = "timed-out"
    elseif termination_status(REopt) == MOI.OPTIMAL
        status = "optimal"
    else
        status = "not optimal"
    end
    
	##############################################################################
    #############  		Outputs    									 #############
    ##############################################################################
    #ProdLoad = ["1R", "1W", "1X", "1S"]
    @expression(REopt, Year1WindProd, p.TimeStepScaling * sum(dvRatedProduction[t,ts] * p.ProductionFactor[t, ts] 
                                            for t in WindTechs, ts in p.TimeStep))
    @expression(REopt, AverageWindProd, p.TimeStepScaling * sum(dvRatedProduction[t,ts] * p.ProductionFactor[t, ts] * p.LevelizationFactor[t]
                                              for t in WindTechs, ts in p.TimeStep))

    @expression(REopt, Year1GenProd, p.TimeStepScaling * sum(dvRatedProduction[t,ts] * p.ProductionFactor[t, ts] 
                       for t in GeneratorTechs, ts in p.TimeStep))
    @expression(REopt, AverageGenProd, p.TimeStepScaling * sum(dvRatedProduction[t,ts] * p.ProductionFactor[t, ts] * p.LevelizationFactor[t]
					   for t in GeneratorTechs, ts in p.TimeStep))
						

	@expression(REopt, GenPerUnitSizeOMCosts, p.two_party_factor * 
		sum(p.OMperUnitSize[t] * p.pwf_om * dvSize[t] for t in GeneratorTechs)
	)
	@expression(REopt, GenPerUnitProdOMCosts, p.two_party_factor * 
		sum(dvRatedProduction[t,ts] * p.TimeStepScaling * p.ProductionFactor[t,ts] * p.OMcostPerUnitProd[t] * p.pwf_om
			for t in GeneratorTechs, ts in p.TimeStep)
	)

    @expression(REopt, Year1UtilityEnergy,  p.TimeStepScaling * sum(
		dvGridPurchase[u,ts] for ts in p.TimeStep, u in p.PricingTier)
		)	

    ojv = round(JuMP.objective_value(REopt)+ 0.0001*value(MinChargeAdder))
    Year1EnergyCost = TotalEnergyChargesUtil / p.pwf_e
    Year1DemandCost = TotalDemandCharges / p.pwf_e
    Year1DemandTOUCost = DemandTOUCharges / p.pwf_e
    Year1DemandFlatCost = DemandFlatCharges / p.pwf_e
    Year1FixedCharges = TotalFixedCharges / p.pwf_e
    Year1MinCharges = MinChargeAdder / p.pwf_e
    Year1Bill = Year1EnergyCost + Year1DemandCost + Year1FixedCharges + Year1MinCharges

    results = Dict{String, Any}("lcc" => ojv)

    results["batt_kwh"] = value(dvStorageCapEnergy["Elec"])
    results["batt_kw"] = value(dvStorageCapPower["Elec"])

    if results["batt_kwh"] != 0
    	@expression(REopt, soc[ts in p.TimeStep], dvStorageSOC["Elec",ts] / results["batt_kwh"])
        results["year_one_soc_series_pct"] = value.(soc)
    else
        results["year_one_soc_series_pct"] = []
    end
	
    if !isempty(WindTechs)
        results["Wind"] = Dict()
        results["wind_kw"] = round(value(sum(dvSize[t] for t in WindTechs)), digits=4)
        #@expression(REopt, WINDtoBatt[ts in p.TimeStep],
        #            sum(dvProductionToStorage[b, t, ts] for t in WindTechs, b in p.ElecStorage))
		WINDtoBatt = 0.0*Array{Float64,1}(undef,p.TimeStepCount)
		for ts in p.TimeStep
			for t in WindTechs
				for b in p.ElecStorage
					WINDtoBatt[ts] += value(dvProductionToStorage[b, t, ts]) 
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
    	if value(sum(dvSize[t] for t in GeneratorTechs)) > 0
			results["Generator"] = Dict()
            results["generator_kw"] = value(sum(dvSize[t] for t in GeneratorTechs))
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
						 "year_one_fixed_cost" => round(value(Year1FixedCharges), digits=0),
						 "year_one_min_charge_adder" => round(value(Year1MinCharges), digits=2),
						 "year_one_bill" => round(value(Year1Bill), digits=2),
						 "year_one_payments_to_third_party_owner" => round(value(TotalDemandCharges) / p.pwf_e, digits=0),
						 "total_energy_cost" => round(value(TotalEnergyChargesUtil) * r_tax_fraction_offtaker, digits=2),
						 "total_demand_cost" => round(value(TotalDemandCharges) * r_tax_fraction_offtaker, digits=2),
						 "total_fixed_cost" => round(value(TotalFixedCharges) * r_tax_fraction_offtaker, digits=2),
						 "total_export_benefit" => round(value(TotalExportBenefit) * r_tax_fraction_offtaker, digits=2),
						 "total_min_charge_adder" => round(value(MinChargeAdder) * r_tax_fraction_offtaker, digits=2),
						 "total_payments_to_third_party_owner" => 0,
						 "net_capital_costs_plus_om" => round(net_capital_costs_plus_om, digits=0),
						 "year_one_wind_energy_produced" => round(value(Year1WindProd), digits=0),
						 "average_wind_energy_produced" => round(value(AverageWindProd), digits=0),
						 "average_annual_energy_exported_wind" => round(value(ExportedElecWIND), digits=0),
                         "year_one_gen_energy_produced" => round(value(Year1GenProd), digits=0),
                         "average_yearly_gen_energy_produced" => round(value(AverageGenProd), digits=0),
                         "average_annual_energy_exported_gen" => round(value(ExportedElecGEN), digits=0),
						 "net_capital_costs" => round(value(TotalTechCapCosts + TotalStorageCapCosts), digits=2))...)

    @expression(REopt, GeneratorFuelUsed, sum(dvFuelUsage[t, ts] for t in GeneratorTechs, ts in p.TimeStep))
    results["fuel_used_gal"] = round(value(GeneratorFuelUsed), digits=2)

    @expression(REopt, GridToBatt[ts in p.TimeStep], dvGridToStorage[ts])
    results["GridToBatt"] = round.(value.(GridToBatt), digits=3)

    @expression(REopt, GridToLoad[ts in p.TimeStep],
                sum(dvGridPurchase[u,ts] for u in p.PricingTier) - dvGridToStorage[ts] )
    results["GridToLoad"] = round.(value.(GridToLoad), digits=3)

	if !isempty(GeneratorTechs)
		@expression(REopt, GENERATORtoBatt[ts in p.TimeStep],
					sum(dvProductionToStorage["Elec",t,ts] for t in GeneratorTechs))
    	results["GENERATORtoBatt"] = round.(value.(GENERATORtoBatt), digits=3)

		@expression(REopt, GENERATORtoGrid[ts in p.TimeStep],
					sum(dvProductionToGrid[t,u,ts] for t in GeneratorTechs, u in p.SalesTiersByTech[t]))
		results["GENERATORtoGrid"] = round.(value.(GENERATORtoGrid), digits=3)

		@expression(REopt, GENERATORtoLoad[ts in p.TimeStep],
					sum(dvRatedProduction[t, ts] * p.ProductionFactor[t, ts] * p.LevelizationFactor[t]
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
			
			results[string(PVclass, "_kw")] = round(value(sum(dvSize[t] for t in PVtechs_in_class)), digits=4)
			
			# NOTE: must use anonymous expressions in this loop to overwrite values for cases with multiple PV
            if !isempty(p.ElecStorage)			
				PVtoBatt = @expression(REopt, [ts in p.TimeStep],
					sum(dvProductionToStorage[b, t, ts] for t in PVtechs_in_class, b in p.ElecStorage))
			else
				PVtoBatt = @expression(REopt, [ts in p.TimeStep], 0.0)
            end
			results[string(PVclass, "toBatt")] = round.(value.(PVtoBatt), digits=3)
			
			PVtoGrid = @expression(REopt, [ts in p.TimeStep],
					sum(dvProductionToGrid[t,u,ts] for t in PVtechs_in_class, u in p.SalesTiersByTech[t]))
    	    results[string(PVclass, "toGrid")] = round.(value.(PVtoGrid), digits=3)
			
			PVtoLoad = @expression(REopt, [ts in p.TimeStep],
				sum(dvRatedProduction[t, ts] * p.ProductionFactor[t, ts] * p.LevelizationFactor[t] for t in PVtechs_in_class) 
				- PVtoGrid[ts] - PVtoBatt[ts]
				)
			
            results[string(PVclass, "toLoad")] = round.(value.(PVtoLoad), digits=3)
			
			Year1PvProd = @expression(REopt, sum(dvRatedProduction[t,ts] * p.ProductionFactor[t, ts] 
				for t in PVtechs_in_class, ts in p.TimeStep) * p.TimeStepScaling)
			results[string("year_one_energy_produced_", PVclass)] = round(value(Year1PvProd), digits=0)

			AveragePvProd = @expression(REopt, sum(dvRatedProduction[t,ts] * p.ProductionFactor[t, ts] * p.LevelizationFactor[t] 
			    for t in PVtechs_in_class, ts in p.TimeStep) * p.TimeStepScaling)
            results[string("average_yearly_energy_produced_", PVclass)] = round(value(AveragePvProd), digits=0)

			ExportedElecPV = @expression(REopt, sum(dvProductionToGrid[t,u,ts] 
				for t in PVtechs_in_class, u in p.SalesTiersByTech[t], ts in p.TimeStep) * p.TimeStepScaling)
            results[string("average_annual_energy_exported_", PVclass)] = round(value(ExportedElecPV), digits=0)

            PVPerUnitSizeOMCosts = @expression(REopt, sum(p.OMperUnitSize[t] * p.pwf_om * dvSize[t] for t in PVtechs_in_class))
            results[string(PVclass, "_net_fixed_om_costs")] = round(value(PVPerUnitSizeOMCosts) * r_tax_fraction_owner, digits=0)
        end
    end
	
	if !isempty(WindTechs)
		@expression(REopt, WINDtoGrid[ts in p.TimeStep],
					sum(dvProductionToGrid[t,u,ts] for t in WindTechs, u in p.SalesTiers))
		results["WINDtoGrid"] = round.(value.(WINDtoGrid), digits=3)
		@expression(REopt, WINDtoLoad[ts in p.TimeStep],
					sum(dvRatedProduction[t, ts] * p.ProductionFactor[t, ts] * p.LevelizationFactor[t]
						for t in WindTechs) - WINDtoGrid[ts] - WINDtoBatt[ts] )
		results["WINDtoLoad"] = round.(value.(WINDtoLoad), digits=3)

		
	else
		results["WINDtoLoad"] = []
    	results["WINDtoGrid"] = []
	end

	if termination_status(REopt) == MOI.TIME_LIMIT
		status = "timed-out"
    elseif termination_status(REopt) == MOI.OPTIMAL
        status = "optimal"
    else
        status = "not optimal"
    end

    results["status"] = status
	
	#=
	print("TotalTechCapCosts:")
	println(value(TotalTechCapCosts))
	print("TotalStorageCapCosts:")
	println(value(TotalStorageCapCosts))
	print("TotalPerUnitSizeOMCosts:")
	println(value(TotalPerUnitSizeOMCosts))
	print("TotalPerUnitProdOMCosts:")
	println(value(TotalPerUnitProdOMCosts))
	println(value( r_tax_fraction_owner * TotalPerUnitProdOMCosts ))
	print("TotalEnergyCharges:")
	println(value(TotalEnergyCharges))
	println(value(r_tax_fraction_offtaker * TotalEnergyCharges))
	print("TotalExportBenefit:")
	println(value(TotalExportBenefit))
	println(value( r_tax_fraction_offtaker * TotalExportBenefit ))
	print("TotalFixedCharges:")
	println(value(TotalFixedCharges))
	println(value(r_tax_fraction_offtaker * p.pwf_e * ( p.FixedMonthlyCharge * 12 ) ) )
	print("MinChargeAdder:")
	println(value(MinChargeAdder))
	println(value(r_tax_fraction_offtaker * p.pwf_e * ( MinChargeAdder ) ) )
	print("TotalProductionIncentive:")
	println(value(TotalProductionIncentive))
	=#
	return results
end
