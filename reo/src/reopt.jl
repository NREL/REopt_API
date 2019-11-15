#=
reopt:
- Julia version: 1.2
- Author: nlaws
- Date: 2019-11-01
=#
using JuMP
using Xpress
import MathOptInterface
const MOI = MathOptInterface

include("utils.jl")

function emptySetException(sets, values)
    try
        return parameter(sets, values)
    catch
        return []
    end
end

function JuMP.value(::Val{false})
    return 0.0
end

function reopt(data;
    Tech,
    Load,
    TechClass,
    TechIsGrid,
    TechToLoadMatrix,
    TurbineDerate,
    TechToTechClassMatrix,
    NMILRegime,
    r_tax_owner,
    r_tax_offtaker,
    pwf_om,
    pwf_e,
    pwf_prod_incent,
    LevelizationFactor,
    LevelizationFactorProdIncent,
    StorageCostPerKW,
    StorageCostPerKWH,
    OMperUnitSize,
    CapCostSlope,
    CapCostYInt,
    CapCostX,
    ProdIncentRate,
    MaxProdIncent,
    MaxSizeForProdIncent,
    two_party_factor,
    analysis_years,
    AnnualElecLoad,
    LoadProfile,
    ProdFactor,
    StorageMinChargePcent,
    EtaStorIn,
    EtaStorOut,
    InitSOC,
    MaxSize,
    MinStorageSizeKW,
    MaxStorageSizeKW,
    MinStorageSizeKWH,
    MaxStorageSizeKWH,
    TechClassMinSize,
    MinTurndown,
    FuelRate,
    FuelAvail,
    FixedMonthlyCharge,
    AnnualMinCharge,
    MonthlyMinCharge,
    ExportRates,
    TimeStepRatchetsMonth,
    DemandRatesMonth,
    DemandLookbackPercent,
    MaxDemandInTier,
    MaxDemandMonthsInTier,
    MaxUsageInTier,
    FuelBurnRateM,
    FuelBurnRateB,
    NMILLimits,
    TechToNMILMapping,
    DemandRates,
    TimeStepRatchets,
    DemandLookbackMonths,
    CapCostSegCount,
    FuelBinCount,
    DemandBinCount,
    DemandMonthsBinCount,
    TimeStepCount,
    #Points,
    #Month,
    #Ratchets,
    #FuelBin,
    #DemandBin,
    #DemandMonthsBin,
    #TimeStep,
    #TimeStepBat,
    NumRatchets,
    TimeStepScaling, 
    args...)

    MAXTIME = data["inputs"]["Scenario"]["timeout_seconds"]
    REopt = direct_model(Xpress.Optimizer(MAXTIME=-MAXTIME))
	# TODO: handle different solvers and their respective timeout variable names

    # CMD Paramters
    #CapCostSegCount = 5
    #FuelBinCount = 1
    #DemandBinCount = 1
    #demandMonthsBinCount = 1
    #TimeStepScaling = 1.0
    #TimeStepCount = 35040
    #Obj = 5
    #REoptTol = 5e-5
    #NumRatchets = 20
   
    # Counting Sets 
    Seg = 1:CapCostSegCount
    Points = 0:CapCostSegCount
    Month = 1:12
    Ratchets = 1:NumRatchets
    FuelBin = 1:FuelBinCount
    DemandBin = 1:DemandBinCount
    DemandMonthsBin = 1:DemandMonthsBinCount
    TimeStep=1:TimeStepCount
    TimeStepBat=0:TimeStepCount
    
    TechIsGrid = parameter(Tech, TechIsGrid)
    TechToLoadMatrix = parameter((Tech, Load), TechToLoadMatrix)
    TurbineDerate = parameter(Tech, TurbineDerate)
    TechToTechClassMatrix = parameter((Tech, TechClass), TechToTechClassMatrix)
    pwf_prod_incent = parameter(Tech, pwf_prod_incent)
    LevelizationFactor = parameter(Tech, LevelizationFactor)
    LevelizationFactorProdIncent = parameter(Tech, LevelizationFactorProdIncent)
    OMperUnitSize = parameter(Tech, OMperUnitSize)
    CapCostSlope = parameter((Tech, Seg), CapCostSlope)
    CapCostYInt = parameter((Tech, Seg), CapCostYInt)
    CapCostX = parameter((Tech, Points), CapCostX)
    ProdIncentRate = parameter((Tech, Load), ProdIncentRate)
    MaxProdIncent = parameter(Tech, MaxProdIncent)
    MaxSizeForProdIncent = parameter(Tech, MaxSizeForProdIncent)
    LoadProfile = parameter((Load, TimeStep), LoadProfile)
    ProdFactor = parameter((Tech, Load, TimeStep), ProdFactor)
    EtaStorIn = parameter((Tech, Load), EtaStorIn)
    EtaStorOut = parameter(Load, EtaStorOut)
    MaxSize = parameter(Tech, MaxSize)
    TechClassMinSize = parameter(TechClass, TechClassMinSize)
    MinTurndown = parameter(Tech, MinTurndown)

    TimeStepRatchets = emptySetException(Ratchets, TimeStepRatchets)
    DemandRates = emptySetException((Ratchets, DemandBin), DemandRates)
    FuelRate = parameter((Tech, FuelBin, TimeStep), FuelRate)
    FuelAvail = parameter((Tech, FuelBin), FuelAvail)
    ExportRates = parameter((Tech, Load, TimeStep), ExportRates)
    TimeStepRatchetsMonth = parameter(Month, TimeStepRatchetsMonth)
    DemandRatesMonth = parameter((Month, DemandMonthsBin), DemandRatesMonth)
    MaxDemandInTier = parameter(DemandBin, MaxDemandInTier)
    MaxDemandMonthsInTier = parameter(DemandMonthsBin, MaxDemandMonthsInTier)
    MaxUsageInTier = parameter(FuelBin, MaxUsageInTier)
    FuelBurnRateM = parameter((Tech, Load, FuelBin), FuelBurnRateM)
    FuelBurnRateB = parameter((Tech, Load, FuelBin), FuelBurnRateB)
    NMILLimits = parameter(NMILRegime, NMILLimits)
    TechToNMILMapping = parameter((Tech, NMILRegime), TechToNMILMapping)
    
    ### Begin Variable Initialization ###
    ######################################
    
    @variables REopt begin
        binNMLorIL[NMILRegime], Bin
        binSegChosen[Tech, Seg], Bin
        dvSystemSize[Tech, Seg] >= 0
        dvGrid[Load, TimeStep, DemandBin, FuelBin, DemandMonthsBin] >= 0
        dvRatedProd[Tech, Load, TimeStep, Seg, FuelBin] >= 0
        dvProdIncent[Tech] >= 0
        binProdIncent[Tech], Bin
        binSingleBasicTech[Tech,TechClass], Bin
        dvPeakDemandE[Ratchets, DemandBin] >= 0
        dvPeakDemandEMonth[Month, DemandMonthsBin] >= 0
        dvElecToStor[TimeStep] >= 0
        dvElecFromStor[TimeStep] >= 0
        dvStoredEnergy[TimeStepBat] >= 0
        dvStorageSizeKWH >= 0
        dvStorageSizeKW >= 0
        dvMeanSOC >= 0
        binBattCharge[TimeStep], Bin
        binBattDischarge[TimeStep], Bin
        dvFuelCost[Tech, FuelBin]
        dvFuelUsed[Tech, FuelBin]
        binTechIsOnInTS[Tech, TimeStep], Bin
        MinChargeAdder >= 0
        binDemandTier[Ratchets, DemandBin], Bin
        binDemandMonthsTier[Month, DemandMonthsBin], Bin
        binUsageTier[Month, FuelBin], Bin
        dvPeakDemandELookback >= 0
    
    # ADDED due to implied types
        ElecToBatt[Tech] >= 0
        UsageInTier[Month, FuelBin] >= 0
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
    
    # ADDED for modeling
        binMinTurndown[Tech, TimeStep], Bin
    end
    
    
    
    ### Begin Constraints###
    ########################
    
    #NEED To account for exist formatting
    @constraint(REopt, [t in Tech, LD in Load, ts in TimeStep, s in Seg, fb in FuelBin; MaxSize[t] * LoadProfile[LD, ts] * TechToLoadMatrix[t, LD] == 0],
                dvRatedProd[t, LD, ts, s, fb] == 0)
   
 

    ### Fuel Tracking Constraints
    @constraint(REopt, [t in Tech, fb in FuelBin],
                sum(ProdFactor[t,LD,ts] * LevelizationFactor[t] * dvRatedProd[t,LD,ts,s,fb] * FuelBurnRateM[t,LD,fb] * TimeStepScaling
                    for ts in TimeStep, LD in Load, s in Seg) +
                sum(binTechIsOnInTS[t,ts] * FuelBurnRateB[t,LD,fb] * TimeStepScaling
                    for ts in TimeStep, LD in Load) == dvFuelUsed[t,fb])
    @constraint(REopt, FuelCont[t in Tech, fb in FuelBin],
                dvFuelUsed[t,fb] <= FuelAvail[t,fb])
    @constraint(REopt, [t in Tech, fb in FuelBin],
                sum(ProdFactor[t, LD, ts] * LevelizationFactor[t] * dvRatedProd[t,LD,ts,s,fb] * FuelBurnRateM[t,LD,fb] * TimeStepScaling * FuelRate[t,fb,ts] * pwf_e
                    for ts in TimeStep, LD in Load, s in Seg) +
               sum(binTechIsOnInTS[t,ts] * FuelBurnRateB[t,LD,fb] * TimeStepScaling * FuelRate[t,fb,ts] * pwf_e
                    for ts in TimeStep, LD in Load) == dvFuelCost[t,fb])
    
    ### Switch Constraints
    @constraint(REopt, [t in Tech, ts in TimeStep],
                sum(ProdFactor[t,LD,ts] * dvRatedProd[t,LD,ts,s,fb] for LD in Load, s in Seg, fb in FuelBin) <=
                MaxSize[t] * 100 * binTechIsOnInTS[t,ts])
    @constraint(REopt, [t in Tech, ts in TimeStep],
                sum(MinTurndown[t] * dvSystemSize[t,s] for s in Seg) -
      		    sum(dvRatedProd[t,LD,ts,s,fb] for LD in Load, s in Seg, fb in FuelBin) <= 
                MaxSize[t] * (1 - binTechIsOnInTS[t, ts]))
    
    ### Boundary Conditions and Size Limits
    @constraint(REopt, dvStoredEnergy[0] == InitSOC * dvStorageSizeKWH / TimeStepScaling)
    @constraint(REopt, MinStorageSizeKWH <= dvStorageSizeKWH)
    @constraint(REopt, dvStorageSizeKWH <=  MaxStorageSizeKWH)
    @constraint(REopt, MinStorageSizeKW <= dvStorageSizeKW)
    @constraint(REopt, dvStorageSizeKW <=  MaxStorageSizeKW)
    
    
    ### Battery Operations
    @constraint(REopt, [ts in TimeStep],
    	        dvElecToStor[ts] == sum(ProdFactor[t,LD,ts] * LevelizationFactor[t] * dvRatedProd[t,LD,ts,s,fb] * EtaStorIn[t,LD]
                                        for t in Tech, LD in ["1S"], s in Seg, fb in FuelBin))
    @constraint(REopt, [ts in TimeStep],
    	        dvStoredEnergy[ts] == dvStoredEnergy[ts-1] + dvElecToStor[ts] - dvElecFromStor[ts] / EtaStorOut["1S"])
    @constraint(REopt, [ts in TimeStep],
    	        dvElecFromStor[ts] / EtaStorOut["1S"] <=  dvStoredEnergy[ts-1])
    @constraint(REopt, [ts in TimeStep],
    	        dvStoredEnergy[ts] >=  StorageMinChargePcent * dvStorageSizeKWH / TimeStepScaling)
    
    ### Operational Nuance
    @constraint(REopt, [ts in TimeStep],
    	        dvStorageSizeKW >=  dvElecToStor[ts])
    @constraint(REopt, [ts in TimeStep],
    	        dvStorageSizeKW >=  dvElecFromStor[ts])
    @constraint(REopt, dvMeanSOC == sum(dvStoredEnergy[ts] for ts in TimeStep) / TimeStepCount)
    @constraint(REopt, [ts in TimeStep],
    	        dvStorageSizeKWH >=  dvStoredEnergy[ts] * TimeStepScaling)
    @constraint(REopt, [ts in TimeStep],
                dvElecToStor[ts] <= MaxStorageSizeKW * binBattCharge[ts])
    @constraint(REopt, [ts in TimeStep],
                dvElecFromStor[ts] <= MaxStorageSizeKW * binBattDischarge[ts])
    @constraint(REopt, [ts in TimeStep],
                binBattDischarge[ts] + binBattCharge[ts] <= 1)
    @constraint(REopt, [t in Tech],
    	        ElecToBatt[t] == sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t,LD,ts] * LevelizationFactor[t]
                                     for ts in TimeStep, LD in ["1S"], s in Seg, fb in FuelBin))
    
    ### Binary Bookkeeping
    @constraint(REopt, [t in Tech],
                sum(binSegChosen[t,s] for s in Seg) == 1)
    @constraint(REopt, [b in TechClass],
                sum(binSingleBasicTech[t,b] for t in Tech) <= 1)
    
    ### Battery Level
    @constraint(REopt, dvStorageSizeKWH <= MaxStorageSizeKWH)
    @constraint(REopt, dvStorageSizeKW <= MaxStorageSizeKW)

    ### Capital Cost Constraints (NEED Had to modify b/c AxisArrays doesn't do well with range 0:20
    @constraint(REopt, [t in Tech, s in Seg],
                dvSystemSize[t,s] <= CapCostX[t,s+1] * binSegChosen[t,s])
    @constraint(REopt, [t in Tech, s in Seg],
                dvSystemSize[t,s] >= CapCostX[t,s] * binSegChosen[t,s])
    
    ### Production Incentive Cap Module
    @constraint(REopt, [t in Tech],
                dvProdIncent[t] <= binProdIncent[t] * MaxProdIncent[t] * pwf_prod_incent[t])
    @constraint(REopt, [t in Tech],
                dvProdIncent[t] <= sum(ProdFactor[t, LD, ts] * LevelizationFactorProdIncent[t] * dvRatedProd[t,LD,ts,s,fb] *
                                       TimeStepScaling * ProdIncentRate[t, LD] * pwf_prod_incent[t]
                                       for LD in Load, ts in TimeStep, s in Seg, fb in FuelBin))
    @constraint(REopt, [t in Tech, LD in Load,ts in TimeStep],
                sum(dvSystemSize[t,s] for s in Seg) <= MaxSizeForProdIncent[t] + MaxSize[t] * (1 - binProdIncent[t]))
    
    ### System Size and Production Constraints
    @constraint(REopt, [t in Tech, s in Seg],
                dvSystemSize[t,s] <=  MaxSize[t])
    @constraint(REopt, [b in TechClass],
                sum(dvSystemSize[t, s] * TechToTechClassMatrix[t,b] for t in Tech, s in Seg) >= TechClassMinSize[b])
    #NEED to tighten bound and check logic
    @constraint(REopt, [t in Tech, LD in Load, ts in TimeStep, s in Seg, fb in FuelBin; MinTurndown[t] > 0],
                binMinTurndown[t,ts] * MinTurndown[t] <= dvRatedProd[t,LD,ts,s,fb] <= binMinTurndown[t,ts] * AnnualElecLoad)
    @constraint(REopt, [t in Tech, s in Seg, ts in TimeStep],
                sum(dvRatedProd[t,LD,ts,s,fb] for LD in Load, fb in FuelBin) <= dvSystemSize[t, s])
    @constraint(REopt, [LD in Load, ts in TimeStep; LD != "1R" && LD != "1S"],
                sum(ProdFactor[t,LD,ts] * LevelizationFactor[t] * dvRatedProd[t,LD,ts,s,fb]
                    for t in Tech, s in Seg, fb in FuelBin) <= LoadProfile[LD,ts])
    @constraint(REopt, [LD in Load, ts in TimeStep; LD == "1R"],
                sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t,LD,ts] * LevelizationFactor[t]
                    for t in Tech, s in Seg, fb in FuelBin) + dvElecFromStor[ts] >= LoadProfile[LD,ts])
    
    ###  Net Meter Module
    @constraint(REopt, sum(binNMLorIL[n] for n in NMILRegime) == 1)
    @constraint(REopt, [n in NMILRegime; n != "AboveIL"],
                sum(TechToNMILMapping[t,n] * TurbineDerate[t] * dvSystemSize[t,s]
                    for t in Tech, s in Seg) <= NMILLimits[n] * binNMLorIL[n])
    @constraint(REopt, sum(TechToNMILMapping[t, "AboveIL"] * TurbineDerate[t] * dvSystemSize[t, s] for t in Tech, s in Seg)  <= NMILLimits["AboveIL"] * binNMLorIL["AboveIL"])
    
    ###  Rate Variable Definitions
    @constraint(REopt, [t in ["UTIL1"], LD in Load, fb in FuelBin, ts in TimeStep],
    	        sum(dvRatedProd[t,LD,ts,s,fb] for s in Seg) == sum(dvGrid[LD,ts,db,fb,dbm] for db in DemandBin, dbm in DemandMonthsBin))
    @constraint(REopt, [t in ["UTIL1"], fb in FuelBin, m in Month],
    	        UsageInTier[m, fb] ==  sum(dvRatedProd[t,LD,ts,s,fb] for LD in Load, ts in TimeStepRatchetsMonth[m], s in Seg))
    
    ### Fuel Bins
    @constraint(REopt, [m in Month, fb in FuelBin],
                UsageInTier[m, fb] <= binUsageTier[m, fb] * MaxUsageInTier[fb])
    @constraint(REopt, [fb in FuelBin, m in Month; fb >= 2],
    	        binUsageTier[m, fb] - binUsageTier[m, fb-1] <= 0)
    @constraint(REopt, [fb in FuelBin, m in Month; fb >= 2],
    	        binUsageTier[m, fb] * MaxUsageInTier[fb-1] - UsageInTier[m, fb-1] <= 0)
    
    ### Peak Demand Energy Rates
    @constraint(REopt, [db in DemandBin, r in Ratchets; db < DemandBinCount],
                dvPeakDemandE[r, db] <= binDemandTier[r,db] * MaxDemandInTier[db])
    @constraint(REopt, [db in DemandBin, r in Ratchets; db >= 2],
                binDemandTier[r, db] - binDemandTier[r, db-1] <= 0)
    @constraint(REopt, [db in DemandBin, r in Ratchets; db >= 2],
                binDemandTier[r, db]*MaxDemandInTier[db-1] - dvPeakDemandE[r, db-1] <= 0)
    
    if !isempty(TimeStepRatchets)
        @constraint(REopt, [db in DemandBin, r in Ratchets, ts in TimeStepRatchets[r]],
                    dvPeakDemandE[r,db] >= sum(dvGrid[LD,ts,db,fb,dbm] for LD in Load, fb in FuelBin, dbm in DemandMonthsBin))
        @constraint(REopt, [db in DemandBin, r in Ratchets, ts in TimeStepRatchets[r]],
                    dvPeakDemandE[r,db] >= DemandLookbackPercent * dvPeakDemandELookback)
    end
    
    ### Peak Demand Energy Rachets
    @constraint(REopt, [dbm in DemandMonthsBin, m in Month; dbm < DemandMonthsBinCount],
    	        dvPeakDemandEMonth[m, dbm] <= binDemandMonthsTier[m,dbm] * MaxDemandMonthsInTier[dbm])
    @constraint(REopt, [dbm in DemandMonthsBin, m in Month; dbm >= 2],
    	        binDemandMonthsTier[m, dbm] - binDemandMonthsTier[m, dbm-1] <= 0)
    @constraint(REopt, [dbm in DemandMonthsBin, m in Month; dbm >= 2],
    	        binDemandMonthsTier[m, dbm] * MaxDemandMonthsInTier[dbm-1] <= dvPeakDemandEMonth[m, dbm-1])
    @constraint(REopt, [dbm in DemandMonthsBin, m in Month, ts in TimeStepRatchetsMonth[m]],
    	        dvPeakDemandEMonth[m, dbm] >=  sum(dvGrid[LD,ts,db,fb,dbm] for LD in Load, db in DemandBin, fb in FuelBin))
    @constraint(REopt, [LD in Load, lbm in DemandLookbackMonths],
                dvPeakDemandELookback >= sum(dvPeakDemandEMonth[lbm, dbm] for dbm in DemandMonthsBin))
    
    ### Site Load
    @constraint(REopt, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * LevelizationFactor[t] *  TimeStepScaling
                           for t in Tech, LD in ["1R", "1W", "1S"],
                           ts in TimeStep, s in Seg, fb in FuelBin if TechIsGrid[t] == 0) <=  AnnualElecLoad)
    
    ###
    #Added, but has awful bounds
    @constraint(REopt, [t in Tech, b in TechClass],
                sum(dvSystemSize[t, s] * TechToTechClassMatrix[t, b] for s in Seg) <= MaxSize[t] * binSingleBasicTech[t, b])
    @constraint(REopt, [t in Tech, ts in TimeStep, s in Seg; TechToTechClassMatrix[t, "PV"] == 1 || TechToTechClassMatrix[t, "WIND"] == 1],
    	        sum(dvRatedProd[t,LD,ts,s,fb] for fb in FuelBin,
                    LD in ["1R", "1W", "1X", "1S"]) ==  dvSystemSize[t, s])
    
    
    @expression(REopt, Year1ElecProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling
                                            for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                            (TechToTechClassMatrix[t, "PV"] == 1 && (LD == "1R" || LD == "1W" || LD == "1X" || LD == "1S"))))
    @expression(REopt, AverageElecProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling * LevelizationFactor[t]
                                              for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                              (TechToTechClassMatrix[t, "PV"] == 1 && (LD == "1R" || LD == "1W" || LD == "1X" || LD == "1S"))))
    @expression(REopt, Year1PVProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling
                                            for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                            (TechToTechClassMatrix[t, "PV"] == 1 && (LD == "1R" || LD == "1W" || LD == "1X" || LD == "1S"))))
    @expression(REopt, AveragePVProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling * LevelizationFactor[t]
                                              for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                              (TechToTechClassMatrix[t, "PV"] == 1 && (LD == "1R" || LD == "1W" || LD == "1X" || LD == "1S"))))
    @expression(REopt, Year1WindProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling
                                            for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                            (TechToTechClassMatrix[t, "WIND"] == 1 && (LD == "1R" || LD == "1W" || LD == "1X" || LD == "1S"))))
    @expression(REopt, AverageWindProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling * LevelizationFactor[t]
                                              for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                              (TechToTechClassMatrix[t, "WIND"] == 1 && (LD == "1R" || LD == "1W" || LD == "1X" || LD == "1S"))))
    @expression(REopt, Year1GenProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling
                                            for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                            (TechToTechClassMatrix[t, "GENERATOR"] == 1 && (LD == "1R" || LD == "1W" || LD == "1X" || LD == "1S"))))
    @expression(REopt, AverageGenProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling * LevelizationFactor[t]
                                              for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                              (TechToTechClassMatrix[t, "GENERATOR"] == 1 && (LD == "1R" || LD == "1W" || LD == "1X" || LD == "1S"))))
    
    
    ### Parts of Objective
    @constraint(REopt, TotalTechCapCosts == sum(CapCostSlope[t, s] * dvSystemSize[t, s] + CapCostYInt[t,s] * binSegChosen[t,s]
                                                for t in Tech, s in Seg))
    @constraint(REopt, TotalStorageCapCosts == dvStorageSizeKWH * StorageCostPerKWH + dvStorageSizeKW *  StorageCostPerKW)
    @constraint(REopt, TotalOMCosts == sum(OMperUnitSize[t] * pwf_om * dvSystemSize[t, s]
                                           for t in Tech, s in Seg))
    
    ### Aggregates of definitions
    @constraint(REopt, TotalEnergyCharges == sum(dvFuelCost[t,fb]
                                                 for t in Tech, fb in FuelBin))
    
    if isempty(DemandRates)
        @constraint(REopt, DemandTOUCharges == 0)
    else
        @constraint(REopt, DemandTOUCharges == sum(dvPeakDemandE[r, db] * DemandRates[r,db] * pwf_e
                                                   for r in Ratchets, db in DemandBin))
    end
    
    @constraint(REopt, DemandFlatCharges == sum(dvPeakDemandEMonth[m, dbm] * DemandRatesMonth[m, dbm] * pwf_e
                                                for m in Month, dbm in DemandMonthsBin))
    @constraint(REopt, TotalDemandCharges ==  DemandTOUCharges + DemandFlatCharges)
    @constraint(REopt, TotalFixedCharges == FixedMonthlyCharge * 12 * pwf_e)
    
    ### Utility and Taxable Costs
    @constraint(REopt, TotalEnergyExports == sum(dvRatedProd[t,LD,ts,s,fb] * TimeStepScaling * ProdFactor[t, LD, ts] * LevelizationFactor[t] * ExportRates[t,LD,ts] * pwf_e for t in Tech, LD in Load, ts in TimeStep, s in Seg, fb in FuelBin))
    @constraint(REopt, TotalProductionIncentive == sum(dvProdIncent[t] for t in Tech))
    
    
    ### MinChargeAdder
    if AnnualMinCharge > 12 * MonthlyMinCharge
        @constraint(REopt, TotalMinCharge == AnnualMinCharge * pwf_e)
    else
        @constraint(REopt, TotalMinCharge == 12 * MonthlyMinCharge * pwf_e)
    end
    @constraint(REopt, MinChargeAdder >= TotalMinCharge - (TotalEnergyCharges + TotalDemandCharges + TotalEnergyExports + TotalFixedCharges))
    
    
    # Define Rates
    r_tax_fraction_owner = (1 - r_tax_owner)
    r_tax_fraction_offtaker = (1 - r_tax_offtaker)
    

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
                sum(ProdFactor[t, "1R", ts]*dvRatedProd[t, "1R", ts, 1, 1] 
                    for t in Tech, ts in TimeStep));
    @expression(REopt, powerfromUTIL1, 
                sum(ProdFactor["UTIL1", "1R", ts]*dvRatedProd["UTIL1", "1R", ts, 1, 1] 
                    for ts in TimeStep));
    
    
    #println("Model built. Moving on to optimization...")
    
    optimize!(REopt)
    
    
    ### Output Module
    #println("\n\nPreparing outputs...\n\n")
    
    @expression(REopt, ExportedElecPV, 
                sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * LevelizationFactor[t] * TimeStepScaling
                    for t in Tech, LD in ["1W", "1X"], ts in TimeStep, s in Seg, fb in FuelBin 
                    if TechToTechClassMatrix[t, "PV"] == 1))
    @expression(REopt, ExportedElecWIND,
                sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * LevelizationFactor[t] * TimeStepScaling
                    for t in Tech, LD in ["1W", "1X"], ts in TimeStep, s in Seg, fb in FuelBin 
                    if TechToTechClassMatrix[t, "WIND"] == 1))
    @expression(REopt, ExportBenefitYr1,
                sum(dvRatedProd[t,LD,ts,s,fb] * TimeStepScaling * ProdFactor[t, LD, ts] * ExportRates[t,LD,ts] 
                    for t in Tech, LD in Load, ts in TimeStep, s in Seg, fb in FuelBin ))
    @expression(REopt, Year1UtilityEnergy, 
                sum(dvRatedProd["UTIL1",LD,ts,s,fb] * TimeStepScaling * ProdFactor["UTIL1", LD, ts] 
                    for LD in Load, ts in TimeStep, s in Seg, fb in FuelBin))

    
    ojv = JuMP.objective_value(REopt)+ 0.001*value(MinChargeAdder)
    Year1EnergyCost = TotalEnergyCharges / pwf_e
    Year1DemandCost = TotalDemandCharges / pwf_e
    Year1DemandTOUCost = DemandTOUCharges / pwf_e
    Year1DemandFlatCost = DemandFlatCharges / pwf_e
    Year1FixedCharges = TotalFixedCharges / pwf_e
    Year1MinCharges = MinChargeAdder / pwf_e
    Year1Bill = Year1EnergyCost + Year1DemandCost + Year1FixedCharges + Year1MinCharges
    
    results = Dict{String, Any}("lcc" => ojv)
    
    results["batt_kwh"] = value(dvStorageSizeKWH)
    results["batt_kw"] = value(dvStorageSizeKW)
    
    if results["batt_kwh"] != 0
    	@expression(REopt, soc[ts in TimeStep], dvStoredEnergy[ts] / results["batt_kwh"])
        results["year_one_soc_series_pct"] = value.(soc)
    else
        results["year_one_soc_series_pct"] = []
    end
    
    #println("1")   
 
    PVTechs = filter(t->TechToTechClassMatrix[t, "PV"] == 1, Tech)
    if !isempty(PVTechs)
        results["PV"] = Dict()
        results["pv_kw"] = value(sum(dvSystemSize[t,s] for s in Seg, t in PVTechs))
        @expression(REopt, PVtoBatt[t in PVTechs, ts in TimeStep],
                    sum(dvRatedProd[t, "1S", ts, s, fb] * ProdFactor[t, "1S", ts] * LevelizationFactor[t] for s in Seg, fb in FuelBin))
    end
    
    WindTechs = filter(t->TechToTechClassMatrix[t, "WIND"] == 1, Tech)
    if !isempty(WindTechs)
        results["Wind"] = Dict()
        results["wind_kw"] = value(sum(dvSystemSize[t,s] for s in Seg, t in WindTechs))
        @expression(REopt, WINDtoBatt[t in WindTechs, ts in TimeStep],
                    sum(dvRatedProd[t, "1S", ts, s, fb] * ProdFactor[t, "1S", ts] * LevelizationFactor[t] for s in Seg, fb in FuelBin))
    end

	results["gen_net_fixed_om_costs"] = 0
	results["gen_net_variable_om_costs"] = 0
	results["gen_total_fuel_cost"] = 0
	results["gen_year_one_fuel_cost"] = 0
	results["gen_year_one_variable_om_costs"] = 0

    GeneratorTechs = filter(t->TechToTechClassMatrix[t, "GENERATOR"] == 1, Tech)
    if !isempty(GeneratorTechs)
    	if value(sum(dvSystemSize[t,s] for s in Seg, t in GeneratorTechs)) > 0
			results["Generator"] = Dict()
			results["gen_net_fixed_om_costs"] = value(GenPerUnitSizeOMCosts) * r_tax_fraction_owner
			results["gen_net_variable_om_costs"] = value(GenPerUnitProdOMCosts) * r_tax_fraction_owner
			# TODO: calculate rest of Generator costs
		end
    end
    
    #println("2")   
    
    push!(results, Dict("year_one_utility_kwh" => value(Year1UtilityEnergy),
						 "year_one_energy_cost" => value(Year1EnergyCost),
						 "year_one_demand_cost" => value(Year1DemandCost),
						 "year_one_demand_tou_cost" => value(Year1DemandTOUCost),
						 "year_one_demand_flat_cost" => value(Year1DemandFlatCost),
						 "year_one_export_benefit" => value(ExportBenefitYr1),
						 "year_one_fixed_cost" => value(Year1FixedCharges),
						 "year_one_min_charge_adder" => value(Year1MinCharges),
						 "year_one_bill" => value(Year1Bill),
						 "year_one_payments_to_third_party_owner" => value(TotalDemandCharges / pwf_e),
						 "total_energy_cost" => value(TotalEnergyCharges * r_tax_fraction_offtaker),
						 "total_demand_cost" => value(TotalDemandCharges * r_tax_fraction_offtaker),
						 "total_fixed_cost" => value(TotalFixedCharges * r_tax_fraction_offtaker),
						 "total_export_benefit" => value(TotalEnergyExports * r_tax_fraction_offtaker),
						 "total_min_charge_adder" => value(MinChargeAdder * r_tax_fraction_offtaker),
						 "total_payments_to_third_party_owner" => 0,
						 "net_capital_costs_plus_om" => value(TotalTechCapCosts + TotalStorageCapCosts + TotalOMCosts * r_tax_fraction_owner),
						 "average_wind_energy_produced" => value(AverageWindProd),
						 "year_one_energy_produced" => value(Year1ElecProd),
						 "year_one_wind_energy_produced" => value(Year1WindProd),
						 "average_annual_energy_exported_wind" => value(ExportedElecWIND),
						 "fuel_used_gal" => 0,  # TODO: calculate fuel_used_gal
						 "net_capital_costs" => value(TotalTechCapCosts + TotalStorageCapCosts))...)
    
    #try @show results["batt_kwh"] catch end
    #try @show results["batt_kw"] catch end
    #try @show results["pv_kw"] catch end
    #try @show results["wind_kw"] catch end
    #@show results["year_one_utility_kwh"]
    #@show results["year_one_energy_cost"]
    #@show results["year_one_demand_cost"]
    #@show results["year_one_demand_tou_cost"]
    #@show results["year_one_demand_flat_cost"]
    #@show results["year_one_export_benefit"]
    #@show results["year_one_fixed_cost"]
    #@show results["year_one_min_charge_adder"]
    #@show results["year_one_bill"]
    #@show results["year_one_payments_to_third_party_owner"]
    #@show results["total_energy_cost"]
    #@show results["total_demand_cost"]
    #@show results["total_fixed_cost"]
    #@show results["total_min_charge_adder"]
    #@show results["net_capital_costs_plus_om"]
    #@show results["net_capital_costs"]
    ##@show results["average_yearly_pv_energy_produced"]
    #@show results["average_wind_energy_produced"]
    #@show results["year_one_energy_produced"]
    #@show results["year_one_wind_energy_produced"]
    ##@show results["average_annual_energy_exported"]
    #@show results["average_annual_energy_exported_wind"]
    
    
    #println("3")   
    
    @expression(REopt, GridToBatt[ts in TimeStep],
                sum(dvRatedProd["UTIL1", "1S", ts, s, fb] * ProdFactor["UTIL1", "1S", ts] * LevelizationFactor["UTIL1"]
					for s in Seg, fb in FuelBin))
    results["GridToBatt"] = value.(GridToBatt)

    @expression(REopt, GridToLoad[ts in TimeStep],
                sum(dvRatedProd["UTIL1", "1R", ts, s, fb] * ProdFactor["UTIL1", "1R", ts] * LevelizationFactor["UTIL1"]
					for s in Seg, fb in FuelBin))
    results["GridToLoad"] = value.(GridToLoad)

	if !isempty(GeneratorTechs)
		@expression(REopt, GENERATORtoBatt[ts in TimeStep],
					sum(dvRatedProd[t, "1S", ts, s, fb] * ProdFactor[t, "1S", ts] * LevelizationFactor[t]
						for t in GeneratorTechs, s in Seg, fb in FuelBin))
    	results["GENERATORtoBatt"] = value.(GENERATORtoBatt)

		@expression(REopt, GENERATORtoGrid[ts in TimeStep],
					sum(dvRatedProd[t, LD, ts, s, fb] * ProdFactor[t, LD, ts] * LevelizationFactor[t]
						for t in GeneratorTechs, LD in ["1W", "1X"], s in Seg, fb in FuelBin))
		results["GENERATORtoGrid"] = value.(GENERATORtoGrid)

		@expression(REopt, GENERATORtoLoad[ts in TimeStep],
					sum(dvRatedProd[t, "1R", ts, s, fb] * ProdFactor[t, "1R", ts] * LevelizationFactor[t]
						for t in GeneratorTechs, s in Seg, fb in FuelBin))
		results["GENERATORtoLoad"] = value.(GENERATORtoLoad)
    else
    	results["GENERATORtoBatt"] = []
		results["GENERATORtoGrid"] = []
		results["GENERATORtoLoad"] = []
	end

	if !isempty(PVTechs)
		@expression(REopt, PVtoLoad[ts in TimeStep],
					sum(dvRatedProd[t, "1R", ts, s, fb] * ProdFactor[t, "1R", ts] * LevelizationFactor[t]
						for t in PVTechs, s in Seg, fb in FuelBin))
    	results["PVtoLoad"] = value.(PVtoLoad)

		@expression(REopt, PVtoGrid[ts in TimeStep],
					sum(dvRatedProd[t, LD, ts, s, fb] * ProdFactor[t, LD, ts] * LevelizationFactor[t]
						for t in PVTechs, LD in ["1W", "1X"], s in Seg, fb in FuelBin))
    	results["PVtoGrid"] = value.(PVtoGrid)

		@expression(REopt, PVPerUnitSizeOMCosts,
					sum(OMperUnitSize[t] * pwf_om * dvSystemSize[t, s] for t in PVTechs, s in Seg))
		results["pv_net_fixed_om_costs"] = value.(PVPerUnitSizeOMCosts) * r_tax_fraction_owner
	else
		results["PVtoLoad"] = []
		results["PVtoGrid"] = []
		results["pv_net_fixed_om_costs"] = 0
	end

	if !isempty(WindTechs)
		@expression(REopt, WINDtoLoad[ts in TimeStep],
					sum(dvRatedProd[t, "1R", ts, s, fb] * ProdFactor[t, "1R", ts] * LevelizationFactor[t]
						for t in WindTechs, s in Seg, fb in FuelBin))
		results["WINDtoLoad"] = value.(WINDtoLoad)

		@expression(REopt, WINDtoGrid[ts in TimeStep],
					sum(dvRatedProd[t, LD, ts, s, fb] * ProdFactor[t, LD, ts] * LevelizationFactor[t]
						for t in WindTechs, s in Seg, fb in FuelBin, LD in ["1W", "1X"]))
		results["WINDtoGrid"] = value.(WINDtoGrid)
	else
		results["WINDtoLoad"] = []
    	results["WINDtoGrid"] = []
	end
    Site_load = LoadProfile["1R", :]
    #println("4")   
    
    #DemandPeaks = value.(dvPeakDemandE)
    #MonthlyDemandPeaks = value.(dvPeakDemandEMonth)
    #println("5")

	if termination_status(REopt) == MOI.TIME_LIMIT
		status = "timed-out"
    elseif termination_status(REopt) == MOI.OPTIMAL
        status = "optimal"
    else
        status = "not optimal"
    end
    #println("6")   
    results["status"] = status
    #println("7")   
    return results
end
