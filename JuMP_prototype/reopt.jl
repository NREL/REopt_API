using JLD2
using JuMP
using Xpress
using MathOptInterface
const MOI = MathOptInterface

include("utils.jl")

function JuMP.value(::Val{false})
    return 0.0
end

function reopt_run(p::Parameter)
   
    REopt = direct_model(Xpress.Optimizer(OUTPUTLOG=1))
    @time begin
    @variables REopt begin
        binNMLorIL[p.NMILRegime], Bin
        binSegChosen[p.Tech, p.Seg], Bin
        dvSystemSize[p.Tech, p.Seg] >= 0
        dvGrid[p.Load, p.TimeStep, p.DemandBin, p.FuelBin, p.DemandMonthsBin] >= 0
        dvRatedProd[p.Tech, p.Load, p.TimeStep, p.Seg, p.FuelBin] >= 0
        dvProdIncent[p.Tech] >= 0
        binProdIncent[p.Tech], Bin
        binSingleBasicTech[p.Tech,p.TechClass], Bin
        dvPeakDemandE[p.Ratchets, p.DemandBin] >= 0
        dvPeakDemandEMonth[p.Month, p.DemandMonthsBin] >= 0
        dvElecToStor[p.TimeStep] >= 0
        dvElecFromStor[p.TimeStep] >= 0
        dvStoredEnergy[p.TimeStepBat] >= 0
        dvStorageSizeKWH[p.BattLevel] >= 0
        dvStorageSizeKW[p.BattLevel] >= 0
        dvMeanSOC >= 0
        binBattCharge[p.TimeStep], Bin
        binBattDischarge[p.TimeStep], Bin
        dvFuelCost[p.Tech, p.FuelBin]
        dvFuelUsed[p.Tech, p.FuelBin]
        binTechIsOnInTS[p.Tech, p.TimeStep], Bin
        MinChargeAdder >= 0
        binDemandTier[p.Ratchets, p.DemandBin], Bin
        binDemandMonthsTier[p.Month, p.DemandMonthsBin], Bin
        binUsageTier[p.Month, p.FuelBin], Bin
        dvPeakDemandELookback >= 0
        binBattLevel[p.BattLevel], Bin
    
    # ADDED due to implied types
        ElecToBatt[p.Tech] >= 0
        UsageInTier[p.Month, p.FuelBin] >= 0
        TotalTechCapCosts >= 0
        TotalStorageCapCosts >= 0
        TotalOMCosts >= 0
        TotalEnergyCharges >= 0
        DemandTOUCharges >= 0
        DemandFlatCharges >= 0
        TotalDemandCharges >= 0
        TotalFixedCharges >= 0
        TotalEnergyExports <= 0
        TotalProductionIncentive >= 0
        TotalMinCharge >= 0
    
    # ADDED due to calculations
        Year1ElecProd
        AverageElecProd
        Year1WindProd
        AverageWindProd
    
    # ADDED for modeling
        binMinTurndown[p.Tech, p.TimeStep], Bin
    end
    
    
    
    ### Begin Constraints###
    ########################
    
    
    #NEED To account for exist formatting
    for t in p.Tech
        if p.MaxSize == 0
            for LD in p.Load
                if p.TechToLoadMatrix[t,LD] == 0
                    for ts in p.TimeStep
                        if p.LoadProfile[LD,ts] == 0
                            for s in p.Seg, fb in p.FuelBin
                            @constraint(REopt, dvRatedProd[t, LD, ts, s, fb] == 0)
                            end
                        end
                    end
                end
            end
        end
    end
    
    ## Fuel Tracking Constraints
    @constraint(REopt, [t in p.Tech, fb in p.FuelBin],
                sum(p.ProdFactor[t,LD,ts] * p.LevelizationFactor[t] * dvRatedProd[t,LD,ts,s,fb] * p.FuelBurnRateM[t,LD,fb] * p.TimeStepScaling
                    for ts in p.TimeStep, LD in p.Load, s in p.Seg) +
                sum(binTechIsOnInTS[t,ts] * p.FuelBurnRateB[t,LD,fb] * p.TimeStepScaling
                    for ts in p.TimeStep, LD in p.Load) == dvFuelUsed[t,fb])
    @constraint(REopt, FuelCont[t in p.Tech, fb in p.FuelBin],
                dvFuelUsed[t,fb] <= p.FuelAvail[t,fb])
    @constraint(REopt, [t in p.Tech, fb in p.FuelBin],
                sum(p.ProdFactor[t, LD, ts] * p.LevelizationFactor[t] * dvRatedProd[t,LD,ts,s,fb] * p.FuelBurnRateM[t,LD,fb] * p.TimeStepScaling * p.FuelRate[t,fb,ts] * p.pwf_e
                    for ts in p.TimeStep, LD in p.Load, s in p.Seg) +
                sum(binTechIsOnInTS[t,ts] * p.FuelBurnRateB[t,LD,fb] * p.TimeStepScaling * p.FuelRate[t,fb,ts] * p.pwf_e
                    for ts in p.TimeStep, LD in p.Load) == dvFuelCost[t,fb])
    
    ### Switch Constraints
    @constraint(REopt, [t in p.Tech, ts in p.TimeStep],
                sum(p.ProdFactor[t,LD,ts] * dvRatedProd[t,LD,ts,s,fb] for LD in p.Load, s in p.Seg, fb in p.FuelBin) <=
                p.MaxSize[t] * 100 * binTechIsOnInTS[t,ts])
    @constraint(REopt, [t in p.Tech, ts in p.TimeStep],
                sum(p.MinTurndown[t] * dvSystemSize[t,s] for s in p.Seg) -
      		    sum(dvRatedProd[t,LD,ts,s,fb] for LD in p.Load, s in p.Seg, fb in p.FuelBin) <= 
                p.MaxSize[t] * (1 - binTechIsOnInTS[t, ts]))
    
    ### Boundary Conditions and Size Limits
    @constraint(REopt, dvStoredEnergy[0] == p.InitSOC * sum(dvStorageSizeKWH[b] for b in p.BattLevel) / p.TimeStepScaling)
    @constraint(REopt, p.MinStorageSizeKWH <= sum(dvStorageSizeKWH[b] for b in p.BattLevel))
    @constraint(REopt, sum(dvStorageSizeKWH[b] for b in p.BattLevel) <=  p.MaxStorageSizeKWH)
    @constraint(REopt, p.MinStorageSizeKW <= sum(dvStorageSizeKW[b] for b in p.BattLevel))
    @constraint(REopt, sum(dvStorageSizeKW[b] for b in p.BattLevel) <=  p.MaxStorageSizeKW)
    
    
    ### Battery Operations
    @constraint(REopt, [ts in p.TimeStep],
    	        dvElecToStor[ts] == sum(p.ProdFactor[t,LD,ts] * p.LevelizationFactor[t] * dvRatedProd[t,LD,ts,s,fb] * p.EtaStorIn[t,LD]
                                        for t in p.Tech, LD in [Symbol("1S")], s in p.Seg, fb in p.FuelBin))
    @constraint(REopt, [ts in p.TimeStep],
    	        dvStoredEnergy[ts] == dvStoredEnergy[ts-1] + dvElecToStor[ts] - dvElecFromStor[ts] / p.EtaStorOut[Symbol("1S")])
    @constraint(REopt, [ts in p.TimeStep],
    	        dvElecFromStor[ts] / p.EtaStorOut[Symbol("1S")] <=  dvStoredEnergy[ts-1])
    @constraint(REopt, [ts in p.TimeStep],
    	        dvStoredEnergy[ts] >=  p.StorageMinChargePcent * sum(dvStorageSizeKWH[b] / p.TimeStepScaling for b in p.BattLevel))
    
    ### Operational Nuance
    @constraint(REopt, [ts in p.TimeStep],
    	        sum(dvStorageSizeKW[b] for b in p.BattLevel) >=  dvElecToStor[ts])
    @constraint(REopt, [ts in p.TimeStep],
    	        sum(dvStorageSizeKW[b] for b in p.BattLevel) >=  dvElecFromStor[ts])
    @constraint(REopt, dvMeanSOC == sum(dvStoredEnergy[ts] for ts in p.TimeStep) / p.TimeStepCount)
    @constraint(REopt, [ts in p.TimeStep],
    	        sum(dvStorageSizeKWH[b] for b in p.BattLevel) >=  dvStoredEnergy[ts] * p.TimeStepScaling)
    @constraint(REopt, [ts in p.TimeStep],
                dvElecToStor[ts] <= p.MaxStorageSizeKW * binBattCharge[ts])
    @constraint(REopt, [ts in p.TimeStep],
                dvElecFromStor[ts] <= p.MaxStorageSizeKW * binBattDischarge[ts])
    @constraint(REopt, [ts in p.TimeStep],
                binBattDischarge[ts] + binBattCharge[ts] <= 1)
    @constraint(REopt, [t in p.Tech],
    	        ElecToBatt[t] == sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t,LD,ts] * p.LevelizationFactor[t]
                                     for ts in p.TimeStep, LD in [Symbol("1S")], s in p.Seg, fb in p.FuelBin))

    ### Binary Bookkeeping
    @constraint(REopt, [t in p.Tech],
                sum(binSegChosen[t,s] for s in p.Seg) == 1)
    @constraint(REopt, [b in p.TechClass],
                sum(binSingleBasicTech[t,b] for t in p.Tech) <= 1)
    
    ### Battery Level
    @constraint(REopt, [b in p.BattLevel],
                dvStorageSizeKWH[b] <= p.MaxStorageSizeKWH * binBattLevel[b])
    @constraint(REopt, [b in p.BattLevel],
                dvStorageSizeKW[b] <= p.MaxStorageSizeKW * binBattLevel[b])
    
    ###### Not Sure ######
    @constraint(REopt, sum(binBattLevel[b] for b in p.BattLevel) == 1)
    ###### Not Sure ######
    
    ### Capital Cost Constraints (NEED Had to modify b/c AxisArrays doesn't do well with range 0:20
    @constraint(REopt, [t in p.Tech, s in p.Seg],
                dvSystemSize[t,s] <= p.CapCostX[t,s+1] * binSegChosen[t,s])
    @constraint(REopt, [t in p.Tech, s in p.Seg],
                dvSystemSize[t,s] >= p.CapCostX[t,s] * binSegChosen[t,s])
    
    ### Production Incentive Cap Module
    @constraint(REopt, [t in p.Tech],
                dvProdIncent[t] <= binProdIncent[t] * p.MaxProdIncent[t] * p.pwf_prod_incent[t])
    @constraint(REopt, [t in p.Tech],
                dvProdIncent[t] <= sum(p.ProdFactor[t, LD, ts] * p.LevelizationFactorProdIncent[t] * dvRatedProd[t,LD,ts,s,fb] *
                                       p.TimeStepScaling * p.ProdIncentRate[t, LD] * p.pwf_prod_incent[t]
                                       for LD in p.Load, ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))
    @constraint(REopt, [t in p.Tech, LD in p.Load,ts in p.TimeStep],
                sum(dvSystemSize[t,s] for s in p.Seg) <= p.MaxSizeForProdIncent[t] + p.MaxSize[t] * (1 - binProdIncent[t]))
    
    ### System Size and Production Constraints
    @constraint(REopt, [t in p.Tech, s in p.Seg],
                dvSystemSize[t,s] <=  p.MaxSize[t])
    @constraint(REopt, [b in p.TechClass],
                sum(dvSystemSize[t, s] * p.TechToTechClassMatrix[t,b] for t in p.Tech, s in p.Seg) >= p.TechClassMinSize[b])
    #NEED to tighten bound and check logic

    for t in p.Tech
        if p.MinTurndown[t] > 0
            @constraint(REopt, [LD in p.Load, ts in p.TimeStep, s in p.Seg, fb in p.FuelBin],
                        binMinTurndown[t,ts] * p.MinTurndown[t] <= dvRatedProd[t,LD,ts,s,fb])
            @constraint(REopt, [LD in p.Load, ts in p.TimeStep, s in p.Seg, fb in p.FuelBin],
                        dvRatedProd[t,LD,ts,s,fb] <= binMinTurndown[t,ts] * p.AnnualElecLoad)
        end
    end

    @constraint(REopt, [t in p.Tech, s in p.Seg, ts in p.TimeStep],
                sum(dvRatedProd[t,LD,ts,s,fb] for LD in p.Load, fb in p.FuelBin) <= dvSystemSize[t, s])

   
    for LD in p.Load
        if LD != Symbol("1R") && LD != Symbol("1S")
            @constraint(REopt, [ts in p.TimeStep],
                        sum(p.ProdFactor[t,LD,ts] * p.LevelizationFactor[t] * dvRatedProd[t,LD,ts,s,fb]
                            for t in p.Tech, s in p.Seg, fb in p.FuelBin) <= p.LoadProfile[LD,ts])
        end
    end

    @constraint(REopt, [LD in [Symbol("1R")], ts in p.TimeStep],
                sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t,LD,ts] * p.LevelizationFactor[t]
                    for t in p.Tech, s in p.Seg, fb in p.FuelBin) + dvElecFromStor[ts] >= p.LoadProfile[LD,ts])
    
    ###  Net Meter Module
    @constraint(REopt, sum(binNMLorIL[n] for n in p.NMILRegime) == 1)
    
    BelowNMset = filter(x->x!=:AboveIL, p.NMILRegime)
    @constraint(REopt, [n in BelowNMset],
                sum(p.TechToNMILMapping[t,n] * p.TurbineDerate[t] * dvSystemSize[t,s]
                    for t in p.Tech, s in p.Seg) <= p.NMILLimits[n] * binNMLorIL[n])
    @constraint(REopt, sum(p.TechToNMILMapping[t, :AboveIL] * p.TurbineDerate[t] * dvSystemSize[t, s] for t in p.Tech, s in p.Seg) 
                           <= p.NMILLimits[:AboveIL] * binNMLorIL[:AboveIL])
    
    ###  Rate Variable Definitions
    @constraint(REopt, [t in [Symbol("UTIL1")], LD in p.Load, fb in p.FuelBin, ts in p.TimeStep],
    	        sum(dvRatedProd[t,LD,ts,s,fb] for s in p.Seg) == sum(dvGrid[LD,ts,db,fb,dbm] for db in p.DemandBin, dbm in p.DemandMonthsBin))
    @constraint(REopt, [t in [Symbol("UTIL1")], fb in p.FuelBin, m in p.Month],
    	        UsageInTier[m, fb] ==  sum(dvRatedProd[t,LD,ts,s,fb] for LD in p.Load, ts in p.TimeStepRatchetsMonth[m], s in p.Seg))
    
    ### Fuel Bins
    @constraint(REopt, [fb in p.FuelBin, m in p.Month],
                UsageInTier[m, fb] <= binUsageTier[m, fb] * p.MaxUsageInTier[fb])
    @constraint(REopt, [fb in 2:p.FuelBinCount, m in p.Month],
    	        binUsageTier[m, fb] - binUsageTier[m, fb-1] <= 0)
    @constraint(REopt, [fb in 2:p.FuelBinCount, m in p.Month],
    	        binUsageTier[m, fb] * p.MaxUsageInTier[fb-1] - UsageInTier[m, fb-1] <= 0)
    
    ### Peak Demand Energy Rates
    for db in p.DemandBin
        @constraint(REopt, [r in p.Ratchets],
                    dvPeakDemandE[r, db] <= binDemandTier[r,db] * p.MaxDemandInTier[db])
        if db >= 2
            @constraint(REopt, [r in p.Ratchets],
                        binDemandTier[r, db] - binDemandTier[r, db-1] <= 0)
            @constraint(REopt, [r in p.Ratchets],
                        binDemandTier[r, db] * p.MaxDemandInTier[db-1] - dvPeakDemandE[r, db-1] <= 0)
        end
    end

    
    if !isempty(p.TimeStepRatchets)
        @constraint(REopt, [db in p.DemandBin, r in p.Ratchets, ts in p.TimeStepRatchets[r]],
                    dvPeakDemandE[r,db] >= sum(dvGrid[LD,ts,db,fb,dbm] for LD in p.Load, fb in p.FuelBin, dbm in p.DemandMonthsBin))
        @constraint(REopt, [db in p.DemandBin, r in p.Ratchets, ts in p.TimeStepRatchets[r]],
                    dvPeakDemandE[r,db] >= p.DemandLookbackPercent * dvPeakDemandELookback)
    end
    
    ### Peak Demand Energy Rachets
    for dbm in p.DemandMonthsBin
        @constraint(REopt, [m in p.Month],
        	        dvPeakDemandEMonth[m, dbm] <= binDemandMonthsTier[m,dbm] * p.MaxDemandMonthsInTier[dbm])
        if dbm >= 2
        @constraint(REopt, [m in p.Month],
        	        binDemandMonthsTier[m, dbm] - binDemandMonthsTier[m, dbm-1] <= 0)
        @constraint(REopt, [m in p.Month],
        	        binDemandMonthsTier[m, dbm] * p.MaxDemandMonthsInTier[dbm-1] <= dvPeakDemandEMonth[m, dbm-1])
        end
    end
    @constraint(REopt, [dbm in p.DemandMonthsBin, m in p.Month, ts in p.TimeStepRatchetsMonth[m]],
    	        dvPeakDemandEMonth[m, dbm] >=  sum(dvGrid[LD,ts,db,fb,dbm] for LD in p.Load, db in p.DemandBin, fb in p.FuelBin))
    @constraint(REopt, [LD in p.Load, lbm in p.DemandLookbackMonths],
                dvPeakDemandELookback >= sum(dvPeakDemandEMonth[lbm, dbm] for dbm in p.DemandMonthsBin))
    
    ### Site Load
    TechIsGridSet = filter(t->p.TechIsGrid[t] == 1, p.Tech)
    @constraint(REopt, sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.LevelizationFactor[t] *  p.TimeStepScaling
                           for t in TechIsGridSet, LD in [Symbol("1R"), Symbol("1W"), Symbol("1S")],
                           ts in p.TimeStep, s in p.Seg, fb in p.FuelBin) <=  p.AnnualElecLoad)
    
    ###
    #Added, but has awful bounds
    @constraint(REopt, [t in p.Tech, b in p.TechClass],
                sum(dvSystemSize[t, s] * p.TechToTechClassMatrix[t, b] for s in p.Seg) <= p.MaxSize[t] * binSingleBasicTech[t, b])

    for t in p.Tech
        if p.TechToTechClassMatrix[t, :PV] == 1 || p.TechToTechClassMatrix[t, :WIND] == 1
            @constraint(REopt, [ts in p.TimeStep, s in p.Seg],
            	        sum(dvRatedProd[t,LD,ts,s,fb] for fb in p.FuelBin,
                            LD in [Symbol("1R"), Symbol("1W"), Symbol("1X"), Symbol("1S")]) ==  dvSystemSize[t, s])
        end
    end
    
    
    ### Parts of Objective

    ProdLoad = [Symbol("1R"), Symbol("1W"), Symbol("1X"), Symbol("1S")]
    
    PVClass = filter(t->p.TechToTechClassMatrix[t, :PV] == 1, p.Tech)
    @constraint(REopt, Year1ElecProd == sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.TimeStepScaling
                                            for t in PVClass, s in p.Seg, fb in p.FuelBin, ts in p.TimeStep, LD in ProdLoad))
    @constraint(REopt, AverageElecProd == sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.TimeStepScaling * p.LevelizationFactor[t]
                                              for t in PVClass, s in p.Seg, fb in p.FuelBin, ts in p.TimeStep, LD in ProdLoad))

    WINDClass = filter(t->p.TechToTechClassMatrix[t, :WIND] == 1, p.Tech)
    @constraint(REopt, Year1WindProd == sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.TimeStepScaling
                                            for t in WINDClass, s in p.Seg, fb in p.FuelBin, ts in p.TimeStep, LD in ProdLoad))
    @constraint(REopt, AverageWindProd == sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.TimeStepScaling * p.LevelizationFactor[t]
                                              for t in WINDClass, s in p.Seg, fb in p.FuelBin, ts in p.TimeStep, LD in ProdLoad))

    @constraint(REopt, TotalTechCapCosts == sum(p.CapCostSlope[t, s] * dvSystemSize[t, s] + p.CapCostYInt[t,s] * binSegChosen[t,s]
                                                for t in p.Tech, s in p.Seg))
    @constraint(REopt, TotalStorageCapCosts == sum(dvStorageSizeKWH[b] * p.StorageCostPerKWH[b] + dvStorageSizeKW[b] *  p.StorageCostPerKW[b]
                                                   for b in p.BattLevel))
    @constraint(REopt, TotalOMCosts == sum(p.OMperUnitSize[t] * p.pwf_om * dvSystemSize[t, s]
                                           for t in p.Tech, s in p.Seg))
    
    ### Aggregates of definitions
    @constraint(REopt, TotalEnergyCharges == sum(dvFuelCost[t,fb]
                                                 for t in p.Tech, fb in p.FuelBin))
    @constraint(REopt, DemandTOUCharges == sum(dvPeakDemandE[r, db] * p.DemandRates[r,db] * p.pwf_e
                                               for r in p.Ratchets, db in p.DemandBin))
    @constraint(REopt, DemandFlatCharges == sum(dvPeakDemandEMonth[m, dbm] * p.DemandRatesMonth[m, dbm] * p.pwf_e
                                                for m in p.Month, dbm in p.DemandMonthsBin))
    @constraint(REopt, TotalDemandCharges ==  DemandTOUCharges + DemandFlatCharges)
    @constraint(REopt, TotalFixedCharges == p.FixedMonthlyCharge * 12 * p.pwf_e)
    
    ### Utility and Taxable Costs
    @constraint(REopt, TotalEnergyExports == sum(dvRatedProd[t,LD,ts,s,fb] * p.TimeStepScaling * p.ProdFactor[t, LD, ts] * p.LevelizationFactor[t] * 
                                                 p.ExportRates[t,LD,ts] * p.pwf_e for t in p.Tech, LD in p.Load, ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))
    @constraint(REopt, TotalProductionIncentive == sum(dvProdIncent[t] for t in p.Tech))
    
    
    ### MinChargeAdder
    if p.AnnualMinCharge > 12 * p.MonthlyMinCharge
        @constraint(REopt, TotalMinCharge == p.AnnualMinCharge * p.pwf_e)
    else
        @constraint(REopt, TotalMinCharge == 12 * p.MonthlyMinCharge * p.pwf_e)
    end
    @constraint(REopt, MinChargeAdder >= TotalMinCharge - (TotalEnergyCharges + TotalDemandCharges + TotalEnergyExports + TotalFixedCharges))
    
    
    # Define Rates
    r_tax_fraction_owner = (1 - p.r_tax_owner)
    r_tax_fraction_offtaker = (1 - p.r_tax_offtaker)
    
    ### Objective Function
    @objective(REopt, Min,
               # Capital Costs
               TotalTechCapCosts + TotalStorageCapCosts +
    
               # Fixed O&M, tax deductible for owner
               TotalOMCosts * r_tax_fraction_owner +
    
               # Utility Bill, tax deductible for offtaker
               (TotalEnergyCharges + TotalDemandCharges + TotalEnergyExports + TotalFixedCharges + 0.999*MinChargeAdder) * r_tax_fraction_offtaker -
    
               # Subtract Incentives, which are taxable
               TotalProductionIncentive * r_tax_fraction_owner
               )
    
    ### Troubleshooting Expressions
    @expression(REopt, powerto1R, 
                sum(p.ProdFactor[t, Symbol("1R"), ts]*dvRatedProd[t, Symbol("1R"), ts, 1, 1] 
                    for t in p.Tech, ts in p.TimeStep))
    @expression(REopt, powerfromUTIL1, 
                sum(p.ProdFactor[:UTIL1, Symbol("1R"), ts]*dvRatedProd[:UTIL1, Symbol("1R"), ts, 1, 1] 
                    for ts in p.TimeStep))
    
    end
    println("Model built. Moving on to optimization...")
    
    optimize!(REopt)

    println("Generating outputs...")
    
    @expression(REopt, ExportedElecPV, 
                sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.LevelizationFactor[t] * p.TimeStepScaling
                    for t in PVClass, LD in [Symbol("1W"), Symbol("1X")], ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))
    @expression(REopt, ExportedElecWIND,
                sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.LevelizationFactor[t] * p.TimeStepScaling
                    for t in WINDClass, LD in [Symbol("1W"), Symbol("1X")], ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))
    @expression(REopt, ExportBenefitYr1,
                sum(dvRatedProd[t,LD,ts,s,fb] * p.TimeStepScaling * p.ProdFactor[t, LD, ts] * p.ExportRates[t,LD,ts] 
                    for t in p.Tech, LD in p.Load, ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))
    @expression(REopt, Year1UtilityEnergy, 
                sum(dvRatedProd[:UTIL1,LD,ts,s,fb] * p.TimeStepScaling * p.ProdFactor[:UTIL1, LD, ts] 
                    for LD in p.Load, ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))
    
    
    ojv = JuMP.objective_value(REopt)+ 0.001*value(MinChargeAdder)
    Year1EnergyCost = TotalEnergyCharges / p.pwf_e
    Year1DemandCost = TotalDemandCharges / p.pwf_e
    Year1DemandTOUCost = DemandTOUCharges / p.pwf_e
    Year1DemandFlatCost = DemandFlatCharges / p.pwf_e
    Year1FixedCharges = TotalFixedCharges / p.pwf_e
    Year1MinCharges = MinChargeAdder / p.pwf_e
    Year1Bill = Year1EnergyCost + Year1DemandCost + Year1FixedCharges + Year1MinCharges
    
    results_JSON = Dict("lcc" => ojv)
    
    for b in p.BattLevel
        results_JSON["batt_kwh"] = value(dvStorageSizeKWH[b])
        results_JSON["batt_kw"] = value(dvStorageSizeKW[b])
    end
    
    for t in p.Tech
        if p.TechToTechClassMatrix[t, :PV] == 1
            results_JSON["pv_kw"] = value(sum(dvSystemSize[t,s] for s in p.Seg))
        end
    end
    
    for t in p.Tech
        if p.TechToTechClassMatrix[t, :WIND] == 1
            results_JSON["wind_kw"] = value(sum(dvSystemSize[t,s] for s in p.Seg))
        end
    end
    
    
    push!(results_JSON, Dict("year_one_utility_kwh" => value(Year1UtilityEnergy),
                             "year_one_energy_cost" => value(Year1EnergyCost),
                             "year_one_demand_cost" => value(Year1DemandCost),
                             "year_one_demand_tou_cost" => value(Year1DemandTOUCost),
                             "year_one_demand_flat_cost" => value(Year1DemandFlatCost),
                             "year_one_export_benefit" => value(ExportBenefitYr1),
                             "year_one_fixed_cost" => value(Year1FixedCharges),
                             "year_one_min_charge_adder" => value(Year1MinCharges),
                             "year_one_bill" => value(Year1Bill),
                             "year_one_payments_to_third_party_owner" => value(TotalDemandCharges / p.pwf_e),
                             "total_energy_cost" => value(TotalEnergyCharges * r_tax_fraction_offtaker),
                             "total_demand_cost" => value(TotalDemandCharges * r_tax_fraction_offtaker),
                             "total_fixed_cost" => value(TotalFixedCharges * r_tax_fraction_offtaker),
                             "total_min_charge_adder" => value(MinChargeAdder * r_tax_fraction_offtaker),
                             "net_capital_costs_plus_om" => value(TotalTechCapCosts + TotalStorageCapCosts + TotalOMCosts * r_tax_fraction_owner),
                             "net_capital_costs" => value(TotalTechCapCosts + TotalStorageCapCosts),
                             "average_yearly_pv_energy_produced" => value(AverageElecProd),
                             "average_wind_energy_produced" => value(AverageWindProd),
                             "year_one_energy_produced" => value(Year1ElecProd),
                             "year_one_wind_energy_produced" => value(Year1WindProd),
                             "average_annual_energy_exported" => value(ExportedElecPV),
                             "average_annual_energy_exported_wind" => value(ExportedElecWIND))...)
    
    try @show results_JSON["batt_kwh"] catch end
    try @show results_JSON["batt_kw"] catch end
    try @show results_JSON["pv_kw"] catch end
    try @show results_JSON["wind_kw"] catch end
    @show results_JSON["year_one_utility_kwh"]
    @show results_JSON["year_one_energy_cost"]
    @show results_JSON["year_one_demand_cost"]
    @show results_JSON["year_one_demand_tou_cost"]
    @show results_JSON["year_one_demand_flat_cost"]
    @show results_JSON["year_one_export_benefit"]
    @show results_JSON["year_one_fixed_cost"]
    @show results_JSON["year_one_min_charge_adder"]
    @show results_JSON["year_one_bill"]
    @show results_JSON["year_one_payments_to_third_party_owner"]
    @show results_JSON["total_energy_cost"]
    @show results_JSON["total_demand_cost"]
    @show results_JSON["total_fixed_cost"]
    @show results_JSON["total_min_charge_adder"]
    @show results_JSON["net_capital_costs_plus_om"]
    @show results_JSON["net_capital_costs"]
    @show results_JSON["average_yearly_pv_energy_produced"]
    @show results_JSON["average_wind_energy_produced"]
    @show results_JSON["year_one_energy_produced"]
    @show results_JSON["year_one_wind_energy_produced"]
    @show results_JSON["average_annual_energy_exported"]
    @show results_JSON["average_annual_energy_exported_wind"]

    return results_JSON

end
