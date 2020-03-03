using JuMP
using Debugger
using Xpress
import MathOptInterface
const MOI = MathOptInterface
include("utils.jl")


function reopt(reo_pyobject, data;
                     Tech,
                     Load,
                     TechClass,
                     TechIsGrid,
                     TechToLoadMatrix,
                     TurbineDerate,
                     TechToTechClassMatrix,
                     NMILRegime,
                     ProdFactor,
                     EtaStorIn,
                     EtaStorOut,
                     MaxSize,
                     MinStorageSizeKW,
                     MaxStorageSizeKW,
                     MinStorageSizeKWH,
                     MaxStorageSizeKWH,
                     TechClassMinSize,
                     MinTurndown,
                     LevelizationFactor,
                     LevelizationFactorProdIncent,
                     pwf_e,
                     pwf_om,
                     two_party_factor,
                     pwf_prod_incent,
                     ProdIncentRate,
                     MaxProdIncent,
                     MaxSizeForProdIncent,
                     CapCostSlope,
                     CapCostX,
                     CapCostYInt,
                     r_tax_owner,
                     r_tax_offtaker,
                     StorageCostPerKW,
                     StorageCostPerKWH,
                     OMperUnitSize,
                     OMcostPerUnitProd,
                     analysis_years,
                     NumRatchets,
                     FuelBinCount,
                     DemandBinCount,
                     DemandMonthsBinCount,
                     DemandRatesMonth,
                     DemandRates,
                     TimeStepRatchets,
                     MaxDemandInTier,
                     MaxUsageInTier,
                     MaxDemandMonthsInTier,
                     FuelRate,
                     FuelAvail,
                     FixedMonthlyCharge,
                     AnnualMinCharge,
                     MonthlyMinCharge,
                     ExportRates,
                     DemandLookbackMonths,
                     DemandLookbackPercent,
                     TimeStepRatchetsMonth,
                     FuelBurnRateM,
                     FuelBurnRateB,
                     TimeStepCount,
                     TimeStepScaling,
                     AnnualElecLoad,
                     LoadProfile,
                     StorageMinChargePcent,
                     InitSOC,
                     NMILLimits,
                     TechToNMILMapping,
                     CapCostSegCount)

    open("types_covered.txt", "w") do io
        write(io, "Tech: " * string(typeof(Tech)) * "\n")
        write(io, "Load: " * string(typeof(Load)) * "\n")
        write(io, "TechClass: " * string(typeof(TechClass)) * "\n")
        write(io, "TechIsGrid: " * string(typeof(TechIsGrid)) * "\n")
        write(io, "TechToLoadMatrix: " * string(typeof(TechToLoadMatrix)) * "\n")
        write(io, "TurbineDerate: " * string(typeof(TurbineDerate)) * "\n")
        write(io, "TechToTechClassMatrix: " * string(typeof(TechToTechClassMatrix)) * "\n")
        write(io, "NMILRegime: " * string(typeof(NMILRegime)) * "\n")
        write(io, "ProdFactor: " * string(typeof(ProdFactor)) * "\n")
        write(io, "EtaStorIn: " * string(typeof(EtaStorIn)) * "\n")
        write(io, "EtaStorOut: " * string(typeof(EtaStorOut)) * "\n")
        write(io, "MaxSize: " * string(typeof(MaxSize)) * "\n")
        write(io, "MinStorageSizeKW: " * string(typeof(MinStorageSizeKW)) * "\n")
        write(io, "MaxStorageSizeKW: " * string(typeof(MaxStorageSizeKW)) * "\n")
        write(io, "MinStorageSizeKWH: " * string(typeof(MinStorageSizeKWH)) * "\n")
        write(io, "MaxStorageSizeKWH: " * string(typeof(MaxStorageSizeKWH)) * "\n")
        write(io, "TechClassMinSize: " * string(typeof(TechClassMinSize)) * "\n")
        write(io, "MinTurndown: " * string(typeof(MinTurndown)) * "\n")
        write(io, "LevelizationFactor: " * string(typeof(LevelizationFactor)) * "\n")
        write(io, "LevelizationFactorProdIncent: " * string(typeof(LevelizationFactorProdIncent)) * "\n")
        write(io, "pwf_e: " * string(typeof(pwf_e)) * "\n")
        write(io, "pwf_om: " * string(typeof(pwf_om)) * "\n")
        write(io, "two_party_factor: " * string(typeof(two_party_factor)) * "\n")
        write(io, "pwf_prod_incent: " * string(typeof(pwf_prod_incent)) * "\n")
        write(io, "ProdIncentRate: " * string(typeof(ProdIncentRate)) * "\n")
        write(io, "MaxProdIncent: " * string(typeof(MaxProdIncent)) * "\n")
        write(io, "MaxSizeForProdIncent: " * string(typeof(MaxSizeForProdIncent)) * "\n")
        write(io, "CapCostSlope: " * string(typeof(CapCostSlope)) * "\n")
        write(io, "CapCostX: " * string(typeof(CapCostX)) * "\n")
        write(io, "CapCostYInt: " * string(typeof(CapCostYInt)) * "\n")
        write(io, "r_tax_owner: " * string(typeof(r_tax_owner)) * "\n")
        write(io, "r_tax_offtaker: " * string(typeof(r_tax_offtaker)) * "\n")
        write(io, "StorageCostPerKW: " * string(typeof(StorageCostPerKW)) * "\n")
        write(io, "StorageCostPerKWH: " * string(typeof(StorageCostPerKWH)) * "\n")
        write(io, "OMperUnitSize: " * string(typeof(OMperUnitSize)) * "\n")
        write(io, "OMcostPerUnitProd: " * string(typeof(OMcostPerUnitProd)) * "\n")
        write(io, "analysis_years: " * string(typeof(analysis_years)) * "\n")
        write(io, "NumRatchets: " * string(typeof(NumRatchets)) * "\n")
        write(io, "FuelBinCount: " * string(typeof(FuelBinCount)) * "\n")
        write(io, "DemandBinCount: " * string(typeof(DemandBinCount)) * "\n")
        write(io, "DemandMonthsBinCount: " * string(typeof(DemandMonthsBinCount)) * "\n")
        write(io, "DemandRatesMonth: " * string(typeof(DemandRatesMonth)) * "\n")
        write(io, "DemandRates: " * string(typeof(DemandRates)) * "\n")
        write(io, "TimeStepRatchets: " * string(typeof(TimeStepRatchets)) * "\n")
        write(io, "MaxDemandInTier: " * string(typeof(MaxDemandInTier)) * "\n")
        write(io, "MaxUsageInTier: " * string(typeof(MaxUsageInTier)) * "\n")
        write(io, "MaxDemandMonthsInTier: " * string(typeof(MaxDemandMonthsInTier)) * "\n")
        write(io, "FuelRate: " * string(typeof(FuelRate)) * "\n")
        write(io, "FuelAvail: " * string(typeof(FuelAvail)) * "\n")
        write(io, "FixedMonthlyCharge: " * string(typeof(FixedMonthlyCharge)) * "\n")
        write(io, "AnnualMinCharge: " * string(typeof(AnnualMinCharge)) * "\n")
        write(io, "MonthlyMinCharge: " * string(typeof(MonthlyMinCharge)) * "\n")
        write(io, "ExportRates: " * string(typeof(ExportRates)) * "\n")
        write(io, "DemandLookbackMonths: " * string(typeof(DemandLookbackMonths)) * "\n")
        write(io, "DemandLookbackPercent: " * string(typeof(DemandLookbackPercent)) * "\n")
        write(io, "TimeStepRatchetsMonth: " * string(typeof(TimeStepRatchetsMonth)) * "\n")
        write(io, "FuelBurnRateM: " * string(typeof(FuelBurnRateM)) * "\n")
        write(io, "FuelBurnRateB: " * string(typeof(FuelBurnRateB)) * "\n")
        write(io, "TimeStepCount: " * string(typeof(TimeStepCount)) * "\n")
        write(io, "TimeStepScaling: " * string(typeof(TimeStepScaling)) * "\n")
        write(io, "AnnualElecLoad: " * string(typeof(AnnualElecLoad)) * "\n")
        write(io, "LoadProfile: " * string(typeof(LoadProfile)) * "\n")
        write(io, "StorageMinChargePcent: " * string(typeof(StorageMinChargePcent)) * "\n")
        write(io, "InitSOC: " * string(typeof(InitSOC)) * "\n")
        write(io, "NMILLimits: " * string(typeof(NMILLimits)) * "\n")
        write(io, "TechToNMILMapping: " * string(typeof(TechToNMILMapping)) * "\n")
        write(io, "CapCostSegCount: " * string(typeof(CapCostSegCount)) * "\n")
    end


    reo_model = direct_model(Xpress.Optimizer())

    p = build_param(Tech = Tech,
                    Load = Load,
                    TechClass = TechClass,
                    TechIsGrid = TechIsGrid,
                    TechToLoadMatrix = TechToLoadMatrix,
                    TurbineDerate = TurbineDerate,
                    TechToTechClassMatrix = TechToTechClassMatrix,
                    NMILRegime = NMILRegime,
                    r_tax_owner = r_tax_owner,
                    r_tax_offtaker = r_tax_offtaker,
                    pwf_om = pwf_om,
                    pwf_e = pwf_e,
                    pwf_prod_incent = pwf_prod_incent,
                    LevelizationFactor = LevelizationFactor,
                    LevelizationFactorProdIncent = LevelizationFactorProdIncent,
                    StorageCostPerKW = StorageCostPerKW,
                    StorageCostPerKWH = StorageCostPerKWH,
                    OMperUnitSize = OMperUnitSize,
                    CapCostSlope = CapCostSlope,
                    CapCostYInt = CapCostYInt,
                    CapCostX = CapCostX,
                    ProdIncentRate = ProdIncentRate,
                    MaxProdIncent = MaxProdIncent,
                    MaxSizeForProdIncent = MaxSizeForProdIncent,
                    two_party_factor = two_party_factor,
                    analysis_years = analysis_years,
                    AnnualElecLoad = AnnualElecLoad,
                    LoadProfile = LoadProfile,
                    ProdFactor = ProdFactor,
                    StorageMinChargePcent = StorageMinChargePcent,
                    EtaStorIn = EtaStorIn,
                    EtaStorOut = EtaStorOut,
                    InitSOC = InitSOC,
                    MaxSize = MaxSize,
                    MinStorageSizeKW = MinStorageSizeKW,
                    MaxStorageSizeKW = MaxStorageSizeKW,
                    MinStorageSizeKWH = MinStorageSizeKWH,
                    MaxStorageSizeKWH = MaxStorageSizeKWH,
                    TechClassMinSize = TechClassMinSize,
                    MinTurndown = MinTurndown,
                    FuelRate = FuelRate,
                    FuelAvail = FuelAvail,
                    FixedMonthlyCharge = FixedMonthlyCharge,
                    AnnualMinCharge = AnnualMinCharge,
                    MonthlyMinCharge = MonthlyMinCharge,
                    ExportRates = ExportRates,
                    TimeStepRatchetsMonth = TimeStepRatchetsMonth,
                    DemandRatesMonth = DemandRatesMonth,
                    DemandLookbackPercent = DemandLookbackPercent,
                    MaxDemandInTier = MaxDemandInTier,
                    MaxDemandMonthsInTier = MaxDemandMonthsInTier,
                    MaxUsageInTier = MaxUsageInTier,
                    FuelBurnRateM = FuelBurnRateM,
                    FuelBurnRateB = FuelBurnRateB,
                    NMILLimits = NMILLimits,
                    TechToNMILMapping = TechToNMILMapping,
                    DemandRates = DemandRates,
                    TimeStepRatchets = TimeStepRatchets,
                    DemandLookbackMonths = DemandLookbackMonths,
                    CapCostSegCount = CapCostSegCount,
                    FuelBinCount = FuelBinCount,
                    DemandBinCount = DemandBinCount  ,
                    DemandMonthsBinCount = DemandMonthsBinCount,
                    TimeStepCount = TimeStepCount,
                    NumRatchets = NumRatchets,
                    TimeStepScaling = TimeStepScaling,
                    OMcostPerUnitProd = OMcostPerUnitProd)

    #MAXTIME = data["inputs"]["Scenario"]["timeout_seconds"]
    MAXTIME = 60000

    return reopt_run(reo_model, MAXTIME, p)
end

function reopt_run(reo_model, MAXTIME::Int64, p::Parameter)

	REopt = reo_model
    Obj = 2  # 1 for minimize LCC, 2 for min LCC AND high mean SOC

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
        dvElecToStor[p.Tech, p.TimeStep] >= 0
        dvElecFromStor[p.TimeStep] >= 0
        dvStoredEnergy[p.TimeStepBat] >= 0
        dvStorageSizeKWH >= 0
        dvStorageSizeKW >= 0
        dvMeanSOC >= 0
        dvFuelCost[p.Tech, p.FuelBin]
        dvFuelUsed[p.Tech, p.FuelBin]
        binTechIsOnInTS[p.Tech, p.TimeStep], Bin
        MinChargeAdder >= 0
        binDemandTier[p.Ratchets, p.DemandBin], Bin
        binDemandMonthsTier[p.Month, p.DemandMonthsBin], Bin
        binUsageTier[p.Month, p.FuelBin], Bin
        dvPeakDemandELookback >= 0

    # ADDED due to implied types
        ElecToBatt[p.Tech] >= 0
        UsageInTier[p.Month, p.FuelBin] >= 0
        #TotalTechCapCosts >= 0
        #TotalStorageCapCosts >= 0
        #TotalEnergyCharges >= 0
        #DemandTOUCharges >= 0
        #DemandFlatCharges >= 0
        #TotalDemandCharges >= 0
        #TotalFixedCharges >= 0
        #TotalEnergyExports <= 0
        #TotalProductionIncentive >= 0
        #TotalMinCharge >= 0

    # ADDED due to calculations
        #Year1ElecProd
        #AverageElecProd
        #Year1WindProd
        #AverageWindProd

    # ADDED for modeling
        binMinTurndown[p.Tech, p.TimeStep], Bin
    end

    ##############################################################################
	#############  		Constraints									 #############
	##############################################################################
    #TODO: account for exist formatting
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
    @constraint(REopt, dvStoredEnergy[0] == p.InitSOC * dvStorageSizeKWH / p.TimeStepScaling)
    @constraint(REopt, p.MinStorageSizeKWH <= dvStorageSizeKWH)
    @constraint(REopt, dvStorageSizeKWH <=  p.MaxStorageSizeKWH)
    @constraint(REopt, p.MinStorageSizeKW <= dvStorageSizeKW)
    @constraint(REopt, dvStorageSizeKW <=  p.MaxStorageSizeKW)


    ### Battery Operations
    # AC electricity to be stored, generated by each Tech, applied to the storage load, for each timestep
    @constraint(REopt, [t in p.Tech, ts in p.TimeStep],
    	        dvElecToStor[t,ts] == sum(p.ProdFactor[t,"1S",ts] * p.LevelizationFactor[t] * dvRatedProd[t,"1S",ts,s,fb]
                                        for s in p.Seg, fb in p.FuelBin))
    @constraint(REopt, [ts in p.TimeStep],
    	        dvStoredEnergy[ts] == dvStoredEnergy[ts-1] + sum(dvElecToStor[t,ts] * p.EtaStorIn[t,"1S"] for t in p.Tech) - dvElecFromStor[ts] / p.EtaStorOut["1S"])
    @constraint(REopt, [ts in p.TimeStep],
    	        dvElecFromStor[ts] / p.EtaStorOut["1S"] <=  dvStoredEnergy[ts-1])
    @constraint(REopt, [ts in p.TimeStep],
    	        dvStoredEnergy[ts] >=  p.StorageMinChargePcent * dvStorageSizeKWH / p.TimeStepScaling)

    ### Operational
    # Storage inverter is AC rated. Following constrains the energy / timestep throughput of the inverter
    #     to the sum of the energy in and energy out of the battery.
    @constraint(REopt, [ts in p.TimeStep],
    	        dvStorageSizeKW * p.TimeStepScaling >=  dvElecFromStor[ts] + sum(dvElecToStor[t,ts] for t in p.Tech))
    @constraint(REopt, dvMeanSOC == sum(dvStoredEnergy[ts] for ts in p.TimeStep) / p.TimeStepCount)
    @constraint(REopt, [ts in p.TimeStep],
    	        dvStorageSizeKWH >=  dvStoredEnergy[ts] * p.TimeStepScaling)
    @constraint(REopt, [t in p.Tech],
    	        ElecToBatt[t] == sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t,LD,ts] * p.LevelizationFactor[t]
                                     for ts in p.TimeStep, LD in ["1S"], s in p.Seg, fb in p.FuelBin))

    ### Binary Bookkeeping
    @constraint(REopt, [t in p.Tech],
                sum(binSegChosen[t,s] for s in p.Seg) == 1)
    @constraint(REopt, [b in p.TechClass],
                sum(binSingleBasicTech[t,b] for t in p.Tech) <= 1)


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
        if LD != "1R" && LD != "1S"
            @constraint(REopt, [ts in p.TimeStep],
                        sum(p.ProdFactor[t,LD,ts] * p.LevelizationFactor[t] * dvRatedProd[t,LD,ts,s,fb]
                            for t in p.Tech, s in p.Seg, fb in p.FuelBin) <= p.LoadProfile[LD,ts])
        end
    end

    @constraint(REopt, [LD in ["1R"], ts in p.TimeStep],
                sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t,LD,ts] * p.LevelizationFactor[t]
                    for t in p.Tech, s in p.Seg, fb in p.FuelBin) + dvElecFromStor[ts] >= p.LoadProfile[LD,ts])

    ###  Net Meter Module
    @constraint(REopt, sum(binNMLorIL[n] for n in p.NMILRegime) == 1)

    @constraint(REopt, [n in p.NMILRegime],
                sum(p.TechToNMILMapping[t,n] * p.TurbineDerate[t] * dvSystemSize[t,s]
                    for t in p.Tech, s in p.Seg) <= p.NMILLimits[n] * binNMLorIL[n])

    ###  Rate Variable Definitions
    @constraint(REopt, [t in ["UTIL1"], LD in p.Load, fb in p.FuelBin, ts in p.TimeStep],
    	        sum(dvRatedProd[t,LD,ts,s,fb] for s in p.Seg) == sum(dvGrid[LD,ts,db,fb,dbm] for db in p.DemandBin, dbm in p.DemandMonthsBin))
    @constraint(REopt, [t in ["UTIL1"], fb in p.FuelBin, m in p.Month],
    	        UsageInTier[m, fb] ==  sum(dvRatedProd[t,LD,ts,s,fb] * p.TimeStepScaling for LD in p.Load, ts in p.TimeStepRatchetsMonth[m], s in p.Seg))

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
    #@constraint(REopt, [LD in p.Load, lbm in p.DemandLookbackMonths], dvPeakDemandELookback >= sum(dvPeakDemandEMonth[lbm, dbm] for dbm in p.DemandMonthsBin))
    @expression(REopt, fake, dvPeakDemandEMonth[1])

    #= Annual energy produced by Tech's' (except UTIL) used to meet the 1R, 1W, and 1S loads must
    be less than the annual site load (in kWh) =#
    TechIsNotGridSet = filter(t->p.TechIsGrid[t] == 0, p.Tech)
    @constraint(REopt, sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.LevelizationFactor[t] *  p.TimeStepScaling
                           for t in TechIsNotGridSet, LD in ["1R", "1W", "1S"],
                           ts in p.TimeStep, s in p.Seg, fb in p.FuelBin) <=  p.AnnualElecLoad)

    ###
    #Added, but has awful bounds
    @constraint(REopt, [t in p.Tech, b in p.TechClass],
                sum(dvSystemSize[t, s] * p.TechToTechClassMatrix[t, b] for s in p.Seg) <= p.MaxSize[t] * binSingleBasicTech[t, b])

    for t in p.Tech
        if p.TechToTechClassMatrix[t, "PV"] == 1 || p.TechToTechClassMatrix[t, "WIND"] == 1
            @constraint(REopt, [ts in p.TimeStep, s in p.Seg],
            	        sum(dvRatedProd[t,LD,ts,s,fb] for fb in p.FuelBin,
                            LD in ["1R", "1W", "1X", "1S"]) ==  dvSystemSize[t, s])
        end
    end


    ### Parts of Objective

    ProdLoad = ["1R", "1W", "1X", "1S"]

    PVTechs = filter(t->p.TechToTechClassMatrix[t, "PV"] == 1, p.Tech)
    @expression(REopt, Year1PvProd, sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.TimeStepScaling
                                            for t in PVTechs, s in p.Seg, fb in p.FuelBin, ts in p.TimeStep, LD in ProdLoad))
    @expression(REopt, AveragePvProd, sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.TimeStepScaling * p.LevelizationFactor[t]
                                              for t in PVTechs, s in p.Seg, fb in p.FuelBin, ts in p.TimeStep, LD in ProdLoad))

    WindTechs = filter(t->p.TechToTechClassMatrix[t, "WIND"] == 1, p.Tech)
    @expression(REopt, Year1WindProd, sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.TimeStepScaling
                                            for t in WindTechs, s in p.Seg, fb in p.FuelBin, ts in p.TimeStep, LD in ProdLoad))
    @expression(REopt, AverageWindProd, sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.TimeStepScaling * p.LevelizationFactor[t]
                                              for t in WindTechs, s in p.Seg, fb in p.FuelBin, ts in p.TimeStep, LD in ProdLoad))

    GeneratorTechs = filter(t->p.TechToTechClassMatrix[t, "GENERATOR"] == 1, p.Tech)
    @expression(REopt, Year1GenProd, sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.TimeStepScaling
                       for t in GeneratorTechs, s in p.Seg, fb in p.FuelBin, ts in p.TimeStep, LD in ProdLoad))
    @expression(REopt, AverageGenProd, sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.TimeStepScaling * p.LevelizationFactor[t]
                       for t in GeneratorTechs, s in p.Seg, fb in p.FuelBin, ts in p.TimeStep, LD in ProdLoad))

    @expression(REopt, TotalTechCapCosts, sum(p.CapCostSlope[t, s] * dvSystemSize[t, s] + p.CapCostYInt[t,s] * binSegChosen[t,s]
                                                for t in p.Tech, s in p.Seg))
    @expression(REopt, TotalStorageCapCosts, dvStorageSizeKWH * p.StorageCostPerKWH + dvStorageSizeKW * p.StorageCostPerKW)
    @expression(REopt, TotalPerUnitSizeOMCosts, sum(p.OMperUnitSize[t] * p.pwf_om * dvSystemSize[t, s] for t in p.Tech, s in p.Seg))

    if !isempty(GeneratorTechs)
        @expression(REopt, TotalPerUnitProdOMCosts, sum(dvRatedProd[t,LD,ts,s,fb] * p.TimeStepScaling * p.ProdFactor[t,LD,ts] * p.OMcostPerUnitProd[t] * p.pwf_om
                                                    for t in GeneratorTechs, LD in p.Load, ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))
    else
        @expression(REopt, TotalPerUnitProdOMCosts, 0.0)
    end

    @expression(REopt, GenPerUnitSizeOMCosts, sum(p.OMperUnitSize[t] * p.pwf_om * dvSystemSize[t, s] for t in GeneratorTechs, s in p.Seg))
    @expression(REopt, GenPerUnitProdOMCosts, sum(dvRatedProd[t,LD,ts,s,fb] * p.TimeStepScaling * p.ProdFactor[t,LD,ts] * p.OMcostPerUnitProd[t] * p.pwf_om
                                              for t in GeneratorTechs, LD in p.Load, ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))


    ### Aggregates of definitions
    @expression(REopt, TotalEnergyCharges, sum(dvFuelCost[t,fb]
                                                 for t in p.Tech, fb in p.FuelBin))
    @expression(REopt, TotalEnergyChargesUtil, sum(dvFuelCost["UTIL1",fb] for fb in p.FuelBin))
    @expression(REopt, TotalGenFuelCharges, sum(dvFuelCost[t,fb] for t in GeneratorTechs, fb in p.FuelBin))
    @expression(REopt, DemandTOUCharges, sum(dvPeakDemandE[r, db] * p.DemandRates[r,db] * p.pwf_e
                                               for r in p.Ratchets, db in p.DemandBin))
    @expression(REopt, DemandFlatCharges, sum(dvPeakDemandEMonth[m, dbm] * p.DemandRatesMonth[m, dbm] * p.pwf_e
                                                for m in p.Month, dbm in p.DemandMonthsBin))
    @expression(REopt, TotalDemandCharges, DemandTOUCharges + DemandFlatCharges)
    @expression(REopt, TotalFixedCharges, p.FixedMonthlyCharge * 12 * p.pwf_e)

    ### Utility and Taxable Costs
    @expression(REopt, TotalEnergyExports, sum(dvRatedProd[t,LD,ts,s,fb] * p.TimeStepScaling * p.ProdFactor[t, LD, ts] * p.LevelizationFactor[t] *
                                                 p.ExportRates[t,LD,ts] * p.pwf_e for t in p.Tech, LD in p.Load, ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))
    @expression(REopt, TotalProductionIncentive, sum(dvProdIncent[t] for t in p.Tech))


    ### MinChargeAdder
    if p.AnnualMinCharge > 12 * p.MonthlyMinCharge
        TotalMinCharge = p.AnnualMinCharge * p.pwf_e
    else
        TotalMinCharge = 12 * p.MonthlyMinCharge * p.pwf_e
    end

    if TotalMinCharge > 0
        @constraint(REopt, MinChargeAdder >= TotalMinCharge - (TotalEnergyCharges + TotalDemandCharges + TotalEnergyExports + TotalFixedCharges))
	else
		@constraint(REopt, MinChargeAdder == 0)
    end
    #= Note: 0.999*MinChargeAdder in Obj b/c when TotalMinCharge > (TotalEnergyCharges + TotalDemandCharges + TotalEnergyExports + TotalFixedCharges)
		it is arbitrary where the min charge ends up (eg. could be in TotalDemandCharges or MinChargeAdder).
		0.001*MinChargeAdder is added back into LCC when writing to results.  =#

    # Define Rates
    r_tax_fraction_owner = (1 - p.r_tax_owner)
    r_tax_fraction_offtaker = (1 - p.r_tax_offtaker)

    ### Objective Function
    @expression(REopt, REcosts,
		# Capital Costs
		TotalTechCapCosts + TotalStorageCapCosts +

		# Fixed O&M, tax deductible for owner
		TotalPerUnitSizeOMCosts * r_tax_fraction_owner +

		# Variable O&M, tax deductible for owner
		TotalPerUnitProdOMCosts * r_tax_fraction_owner +

		# Utility Bill, tax deductible for offtaker
		(TotalEnergyCharges + TotalDemandCharges + TotalEnergyExports + TotalFixedCharges + 0.999*MinChargeAdder) * r_tax_fraction_offtaker -

		# Subtract Incentives, which are taxable
		TotalProductionIncentive * r_tax_fraction_owner
	)

    if Obj == 1
		@objective(REopt, Min, REcosts)
	elseif Obj == 2  # Keep SOC high
		@objective(REopt, Min, REcosts - dvMeanSOC)
	end
	optimize!(REopt)

    ##############################################################################
    #############  		Outputs    									 #############
    ##############################################################################
    @expression(REopt, ExportedElecPV,
                sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.LevelizationFactor[t] * p.TimeStepScaling
                    for t in PVTechs, LD in ["1W", "1X"], ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))
    @expression(REopt, ExportedElecWIND,
                sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.LevelizationFactor[t] * p.TimeStepScaling
                    for t in WindTechs, LD in ["1W", "1X"], ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))
    @expression(REopt, ExportedElecGEN,
                sum(dvRatedProd[t,LD,ts,s,fb] * p.ProdFactor[t, LD, ts] * p.LevelizationFactor[t] * p.TimeStepScaling
                    for t in GeneratorTechs, LD in ["1W", "1X"], ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))

    # Needs levelization factor?
    @expression(REopt, ExportBenefitYr1,
                sum(dvRatedProd[t,LD,ts,s,fb] * p.TimeStepScaling * p.ProdFactor[t, LD, ts] * p.ExportRates[t,LD,ts] * p.LevelizationFactor[t]
                    for t in p.Tech, LD in p.Load, ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))
    @expression(REopt, Year1UtilityEnergy,
                sum(dvRatedProd["UTIL1",LD,ts,s,fb] * p.TimeStepScaling * p.ProdFactor["UTIL1", LD, ts]
                    for LD in p.Load, ts in p.TimeStep, s in p.Seg, fb in p.FuelBin))


    ojv = round(JuMP.objective_value(REopt)+ 0.001*value(MinChargeAdder))
    Year1EnergyCost = TotalEnergyChargesUtil / p.pwf_e
    Year1DemandCost = TotalDemandCharges / p.pwf_e
    Year1DemandTOUCost = DemandTOUCharges / p.pwf_e
    Year1DemandFlatCost = DemandFlatCharges / p.pwf_e
    Year1FixedCharges = TotalFixedCharges / p.pwf_e
    Year1MinCharges = MinChargeAdder / p.pwf_e
    Year1Bill = Year1EnergyCost + Year1DemandCost + Year1FixedCharges + Year1MinCharges

    results = Dict{String, Any}("lcc" => ojv)

    results["batt_kwh"] = value(dvStorageSizeKWH)
    results["batt_kw"] = value(dvStorageSizeKW)

    if results["batt_kwh"] != 0
    	@expression(REopt, soc[ts in p.TimeStep], dvStoredEnergy[ts] / results["batt_kwh"])
        results["year_one_soc_series_pct"] = value.(soc)
    else
        results["year_one_soc_series_pct"] = []
    #MAXTIME = data["inputs"]["Scenario"]["timeout_seconds"]
   end

    if !isempty(PVTechs)
        results["PV"] = Dict()
        results["pv_kw"] = round(value(sum(dvSystemSize[t,s] for s in p.Seg, t in PVTechs)), digits=4)
        @expression(REopt, PVtoBatt[t in PVTechs, ts in p.TimeStep],
                    sum(dvRatedProd[t, "1S", ts, s, fb] * p.ProdFactor[t, "1S", ts] * p.LevelizationFactor[t] for s in p.Seg, fb in p.FuelBin))
    end

    WindTechs = filter(t->p.TechToTechClassMatrix[t, "WIND"] == 1, p.Tech)
    if !isempty(WindTechs)
        results["Wind"] = Dict()
        results["wind_kw"] = round(value(sum(dvSystemSize[t,s] for s in p.Seg, t in WindTechs)), digits=4)
        @expression(REopt, WINDtoBatt[t in WindTechs, ts in p.TimeStep],
                    sum(dvRatedProd[t, "1S", ts, s, fb] * p.ProdFactor[t, "1S", ts] * p.LevelizationFactor[t] for s in p.Seg, fb in p.FuelBin))
    end

	results["gen_net_fixed_om_costs"] = 0
	results["gen_net_variable_om_costs"] = 0
	results["gen_total_fuel_cost"] = 0
	results["gen_year_one_fuel_cost"] = 0
	results["gen_year_one_variable_om_costs"] = 0

    GeneratorTechs = filter(t->p.TechToTechClassMatrix[t, "GENERATOR"] == 1, p.Tech)
    if !isempty(GeneratorTechs)
    	if value(sum(dvSystemSize[t,s] for s in p.Seg, t in GeneratorTechs)) > 0
			results["Generator"] = Dict()
            results["generator_kw"] = value(sum(dvSystemSize[t,s] for s in p.Seg, t in GeneratorTechs))
			results["gen_net_fixed_om_costs"] = round(value(GenPerUnitSizeOMCosts) * r_tax_fraction_owner, digits=0)
			results["gen_net_variable_om_costs"] = round(value(GenPerUnitProdOMCosts) * r_tax_fraction_owner, digits=0)
	        results["gen_total_fuel_cost"] = round(value(TotalGenFuelCharges) * r_tax_fraction_offtaker, digits=2)
	        results["gen_year_one_fuel_cost"] = round(value(TotalGenFuelCharges) * r_tax_fraction_offtaker / p.pwf_e, digits=2)
	        results["gen_year_one_variable_om_costs"] = round(value(GenPerUnitProdOMCosts) * r_tax_fraction_owner / p.pwf_om, digits=0)
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
						 "total_energy_cost" => round(value(TotalEnergyCharges) * r_tax_fraction_offtaker, digits=2),
						 "total_demand_cost" => round(value(TotalDemandCharges) * r_tax_fraction_offtaker, digits=2),
						 "total_fixed_cost" => round(value(TotalFixedCharges) * r_tax_fraction_offtaker, digits=2),
						 "total_export_benefit" => round(value(TotalEnergyExports) * r_tax_fraction_offtaker, digits=2),
						 "total_min_charge_adder" => round(value(MinChargeAdder) * r_tax_fraction_offtaker, digits=2),
						 "total_payments_to_third_party_owner" => 0,
						 "net_capital_costs_plus_om" => round(net_capital_costs_plus_om, digits=0),
						 "year_one_energy_produced" => round(value(Year1PvProd), digits=0),
                         "average_yearly_pv_energy_produced" => round(value(AveragePvProd), digits=0),
						 "average_annual_energy_exported_pv" => round(value(ExportedElecPV), digits=0),
						 "year_one_wind_energy_produced" => round(value(Year1WindProd), digits=0),
						 "average_wind_energy_produced" => round(value(AverageWindProd), digits=0),
						 "average_annual_energy_exported_wind" => round(value(ExportedElecWIND), digits=0),
                         "year_one_gen_energy_produced" => round(value(Year1GenProd), digits=0),
                         "average_yearly_gen_energy_produced" => round(value(AverageGenProd), digits=0),
                         "average_annual_energy_exported_gen" => round(value(ExportedElecGEN), digits=0),
						 "net_capital_costs" => round(value(TotalTechCapCosts + TotalStorageCapCosts), digits=2))...)

    @expression(REopt, GeneratorFuelUsed, sum(dvFuelUsed[t, fb] for t in GeneratorTechs, fb in p.FuelBin))
    results["fuel_used_gal"] = round(value(GeneratorFuelUsed), digits=2)

    @expression(REopt, GridToBatt[ts in p.TimeStep],
                sum(dvRatedProd["UTIL1", "1S", ts, s, fb] * p.ProdFactor["UTIL1", "1S", ts] * p.LevelizationFactor["UTIL1"]
					for s in p.Seg, fb in p.FuelBin))
    results["GridToBatt"] = round.(value.(GridToBatt), digits=3)

    @expression(REopt, GridToLoad[ts in p.TimeStep],
                sum(dvRatedProd["UTIL1", "1R", ts, s, fb] * p.ProdFactor["UTIL1", "1R", ts] * p.LevelizationFactor["UTIL1"]
					for s in p.Seg, fb in p.FuelBin))
    results["GridToLoad"] = round.(value.(GridToLoad), digits=3)

	if !isempty(GeneratorTechs)
		@expression(REopt, GENERATORtoBatt[ts in p.TimeStep],
					sum(dvRatedProd[t, "1S", ts, s, fb] * p.ProdFactor[t, "1S", ts] * p.LevelizationFactor[t]
						for t in GeneratorTechs, s in p.Seg, fb in p.FuelBin))
    	results["GENERATORtoBatt"] = round.(value.(GENERATORtoBatt), digits=3)

		@expression(REopt, GENERATORtoGrid[ts in p.TimeStep],
					sum(dvRatedProd[t, LD, ts, s, fb] * p.ProdFactor[t, LD, ts] * p.LevelizationFactor[t]
						for t in GeneratorTechs, LD in ["1W", "1X"], s in p.Seg, fb in p.FuelBin))
		results["GENERATORtoGrid"] = round.(value.(GENERATORtoGrid), digits=3)

		@expression(REopt, GENERATORtoLoad[ts in p.TimeStep],
					sum(dvRatedProd[t, "1R", ts, s, fb] * p.ProdFactor[t, "1R", ts] * p.LevelizationFactor[t]
						for t in GeneratorTechs, s in p.Seg, fb in p.FuelBin))
		results["GENERATORtoLoad"] = round.(value.(GENERATORtoLoad), digits=3)
    else
    	results["GENERATORtoBatt"] = []
		results["GENERATORtoGrid"] = []
		results["GENERATORtoLoad"] = []
	end

	if !isempty(PVTechs)
		@expression(REopt, PVtoLoad[ts in p.TimeStep],
					sum(dvRatedProd[t, "1R", ts, s, fb] * p.ProdFactor[t, "1R", ts] * p.LevelizationFactor[t]
						for t in PVTechs, s in p.Seg, fb in p.FuelBin))
    	results["PVtoLoad"] = round.(value.(PVtoLoad), digits=3)

		@expression(REopt, PVtoGrid[ts in p.TimeStep],
					sum(dvRatedProd[t, LD, ts, s, fb] * p.ProdFactor[t, LD, ts] * p.LevelizationFactor[t]
						for t in PVTechs, LD in ["1W", "1X"], s in p.Seg, fb in p.FuelBin))
    	results["PVtoGrid"] = round.(value.(PVtoGrid), digits=3)

		@expression(REopt, PVPerUnitSizeOMCosts,
					sum(p.OMperUnitSize[t] * p.pwf_om * dvSystemSize[t, s] for t in PVTechs, s in p.Seg))
		results["pv_net_fixed_om_costs"] = round(value(PVPerUnitSizeOMCosts) * r_tax_fraction_owner, digits=0)
	else
		results["PVtoLoad"] = []
		results["PVtoGrid"] = []
		results["pv_net_fixed_om_costs"] = 0
	end

	if !isempty(WindTechs)
		@expression(REopt, WINDtoLoad[ts in p.TimeStep],
					sum(dvRatedProd[t, "1R", ts, s, fb] * p.ProdFactor[t, "1R", ts] * p.LevelizationFactor[t]
						for t in WindTechs, s in p.Seg, fb in p.FuelBin))
		results["WINDtoLoad"] = round.(value.(WINDtoLoad), digits=3)

		@expression(REopt, WINDtoGrid[ts in p.TimeStep],
					sum(dvRatedProd[t, LD, ts, s, fb] * p.ProdFactor[t, LD, ts] * p.LevelizationFactor[t]
						for t in WindTechs, s in p.Seg, fb in p.FuelBin, LD in ["1W", "1X"]))
		results["WINDtoGrid"] = round.(value.(WINDtoGrid), digits=3)
	else
		results["WINDtoLoad"] = []
    	results["WINDtoGrid"] = []
	end

    results["Load"] = p.LoadProfile["1R", :]

	if termination_status(REopt) == MOI.TIME_LIMIT
		status = "timed-out"
    elseif termination_status(REopt) == MOI.OPTIMAL
        status = "optimal"
    else
        status = "not optimal"
    end

    results["status"] = status
    return results
end


function test(reo_model, data; Tech, kwargs...)

    println("Tech =", Tech)
    #for (k,v) in kwargs
    #    println(k, ": ", typeof(v))
    #end
end

py_reopt = pyfunctionret(reopt, Dict, PyObject, Dict{Any,Any};
                     Tech=Array{String,1},
                     Load=Array{String,1},
                     TechClass=Array{String,1},
                     TechIsGrid=Array{Int64,1},
                     TechToLoadMatrix=Array{Int64,1},
                     TurbineDerate=Array{Float64,1},
                     TechToTechClassMatrix=Array{Int64,1},
                     NMILRegime=Array{String,1},
                     ProdFactor=Array{Float64,1},
                     EtaStorIn=Array{Float64,1},
                     EtaStorOut=Array{Float64,1},
                     MaxSize=Array{Float64,1},
                     MinStorageSizeKW=Float64,
                     MaxStorageSizeKW=Float64,
                     MinStorageSizeKWH=Float64,
                     MaxStorageSizeKWH=Float64,
                     TechClassMinSize=Array{Float64,1},
                     MinTurndown=Array{Float64,1},
                     LevelizationFactor=Array{Float64,1},
                     LevelizationFactorProdIncent=Array{Float64,1},
                     pwf_e=Float64,
                     pwf_om=Float64,
                     two_party_factor=Float64,
                     pwf_prod_incent=Array{Float64,1},
                     ProdIncentRate=Array{Float64,1},
                     MaxProdIncent=Array{Float64,1},
                     MaxSizeForProdIncent=Array{Float64,1},
                     CapCostSlope=Array{Float64,1},
                     CapCostX=Array{Float64,1},
                     CapCostYInt=Array{Float64,1},
                     r_tax_owner=Float64,
                     r_tax_offtaker=Float64,
                     StorageCostPerKW=Float64,
                     StorageCostPerKWH=Float64,
                     OMperUnitSize=Array{Float64,1},
                     OMcostPerUnitProd=Array{Float64,1},
                     analysis_years=Int64,
                     NumRatchets=Int64,
                     FuelBinCount=Int64,
                     DemandBinCount=Int64,
                     DemandMonthsBinCount=Int64,
                     DemandRatesMonth=Array{Float64,1},
                     DemandRates=Array{Float64,1},
                     TimeStepRatchets=Array{Array{Int64,1}},
                     MaxDemandInTier=Array{Float64,1},
                     MaxUsageInTier=Array{Float64,1},
                     MaxDemandMonthsInTier=Array{Float64,1},
                     FuelRate=Array{Float64,1},
                     FuelAvail=Array{Float64,1},
                     FixedMonthlyCharge=Int64,
                     AnnualMinCharge=Int64,
                     MonthlyMinCharge=Int64,
                     ExportRates=Array{Float64,1},
                     DemandLookbackMonths=Array{Int64,1},
                     DemandLookbackPercent=Float64,
                     TimeStepRatchetsMonth=Array{Array{Int64,1},1},
                     FuelBurnRateM=Array{Float64,1},
                     FuelBurnRateB=Array{Float64,1},
                     TimeStepCount=Int64,
                     TimeStepScaling=Float64,
                     AnnualElecLoad=Float64,
                     LoadProfile=Array{Float64,1},
                     StorageMinChargePcent=Float64,
                     InitSOC=Float64,
                     NMILLimits=Array{Float64,1},
                     TechToNMILMapping=Array{Int64,1},
                     CapCostSegCount=Int64)
