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

function fast_reopt(model_inputs)

    println("Tech", ": ", typeof(model_inputs["Tech"]))
    println("Load", ": ", typeof(model_inputs["Load"]))
    println("TechClass", ": ", typeof(model_inputs["TechClass"]))
    println("TechIsGrid", ": ", typeof(model_inputs["TechIsGrid"]))
    println("TechToLoadMatrix", ": ", typeof(model_inputs["TechToLoadMatrix"]))
    println("TurbineDerate", ": ", typeof(model_inputs["TurbineDerate"]))
    println("TechToTechClassMatrix", ": ", typeof(model_inputs["TechToTechClassMatrix"]))
    println("NMILRegime", ": ", typeof(model_inputs["NMILRegime"]))
    println("r_tax_owner", ": ", typeof(model_inputs["r_tax_owner"]))
    println("r_tax_offtaker", ": ", typeof(model_inputs["r_tax_offtaker"]))
    println("pwf_om", ": ", typeof(model_inputs["pwf_om"]))
    println("pwf_e", ": ", typeof(model_inputs["pwf_e"]))
    println("pwf_prod_incent", ": ", typeof(model_inputs["pwf_prod_incent"]))
    println("LevelizationFactor", ": ", typeof(model_inputs["LevelizationFactor"]))
    println("LevelizationFactorProdIncent", ": ", typeof(model_inputs["LevelizationFactorProdIncent"]))
    println("StorageCostPerKW", ": ", typeof(model_inputs["StorageCostPerKW"]))
    println("StorageCostPerKWH", ": ", typeof(model_inputs["StorageCostPerKWH"]))
    println("OMperUnitSize", ": ", typeof(model_inputs["OMperUnitSize"]))
    println("CapCostSlope", ": ", typeof(model_inputs["CapCostSlope"]))
    println("CapCostYInt", ": ", typeof(model_inputs["CapCostYInt"]))
    println("CapCostX", ": ", typeof(model_inputs["CapCostX"]))
    println("ProdIncentRate", ": ", typeof(model_inputs["ProdIncentRate"]))
    println("MaxProdIncent", ": ", typeof(model_inputs["MaxProdIncent"]))
    println("MaxSizeForProdIncent", ": ", typeof(model_inputs["MaxSizeForProdIncent"]))
    println("two_party_factor", ": ", typeof(model_inputs["two_party_factor"]))
    println("analysis_years", ": ", typeof(model_inputs["analysis_years"]))
    println("AnnualElecLoad", ": ", typeof(model_inputs["AnnualElecLoad"]))
    println("LoadProfile", ": ", typeof(model_inputs["LoadProfile"]))
    println("ProdFactor", ": ", typeof(model_inputs["ProdFactor"]))
    println("StorageMinChargePcent", ": ", typeof(model_inputs["StorageMinChargePcent"]))
    println("EtaStorIn", ": ", typeof(model_inputs["EtaStorIn"]))
    println("EtaStorOut", ": ", typeof(model_inputs["EtaStorOut"]))
    println("InitSOC", ": ", typeof(model_inputs["InitSOC"]))
    println("MaxSize", ": ", typeof(model_inputs["MaxSize"]))
    println("MinStorageSizeKW", ": ", typeof(model_inputs["MinStorageSizeKW"]))
    println("MaxStorageSizeKW", ": ", typeof(model_inputs["MaxStorageSizeKW"]))
    println("MinStorageSizeKWH", ": ", typeof(model_inputs["MinStorageSizeKWH"]))
    println("MaxStorageSizeKWH", ": ", typeof(model_inputs["MaxStorageSizeKWH"]))
    println("TechClassMinSize", ": ", typeof(model_inputs["TechClassMinSize"]))
    println("MinTurndown", ": ", typeof(model_inputs["MinTurndown"]))
    println("FuelRate", ": ", typeof(model_inputs["FuelRate"]))
    println("FuelAvail", ": ", typeof(model_inputs["FuelAvail"]))
    println("FixedMonthlyCharge", ": ", typeof(model_inputs["FixedMonthlyCharge"]))
    println("AnnualMinCharge", ": ", typeof(model_inputs["AnnualMinCharge"]))
    println("MonthlyMinCharge", ": ", typeof(model_inputs["MonthlyMinCharge"]))
    println("ExportRates", ": ", typeof(model_inputs["ExportRates"]))
    println("TimeStepRatchetsMonth", ": ", typeof(model_inputs["TimeStepRatchetsMonth"]))
    println("DemandRatesMonth", ": ", typeof(model_inputs["DemandRatesMonth"]))
    println("DemandLookbackPercent", ": ", typeof(model_inputs["DemandLookbackPercent"]))
    println("MaxDemandInTier", ": ", typeof(model_inputs["MaxDemandInTier"]))
    println("MaxDemandMonthsInTier", ": ", typeof(model_inputs["MaxDemandMonthsInTier"]))
    println("MaxUsageInTier", ": ", typeof(model_inputs["MaxUsageInTier"]))
    println("FuelBurnRateM", ": ", typeof(model_inputs["FuelBurnRateM"]))
    println("FuelBurnRateB", ": ", typeof(model_inputs["FuelBurnRateB"]))
    println("NMILLimits", ": ", typeof(model_inputs["NMILLimits"]))
    println("TechToNMILMapping", ": ", typeof(model_inputs["TechToNMILMapping"]))
    println("DemandRates", ": ", typeof(model_inputs["DemandRates"]))
    println("TimeStepRatchets", ": ", typeof(model_inputs["TimeStepRatchets"]))
    println("DemandLookbackMonths", ": ", typeof(model_inputs["DemandLookbackMonths"]))
    println("CapCostSegCount", ": ", typeof(model_inputs["CapCostSegCount"]))
    println("FuelBinCount", ": ", typeof(model_inputs["FuelBinCount"]))
    println("DemandBinCount",  ": ", typeof(model_inputs["DemandBinCount"]))
    println("DemandMonthsBinCount", ": ", typeof(model_inputs["DemandMonthsBinCount"]))
    println("TimeStepCount", ": ", typeof(model_inputs["TimeStepCount"]))
    println("TimeStepScaling", ": ", typeof(model_inputs["TimeStepScaling"]))


    p = build_param(Tech = model_inputs["Tech"],
          Load = model_inputs["Load"],
          TechClass = model_inputs["TechClass"],
          TechIsGrid = model_inputs["TechIsGrid"],
          TechToLoadMatrix = model_inputs["TechToLoadMatrix"],
          TurbineDerate = model_inputs["TurbineDerate"],
          TechToTechClassMatrix = model_inputs["TechToTechClassMatrix"],
          NMILRegime = model_inputs["NMILRegime"],
          r_tax_owner = model_inputs["r_tax_owner"],
          r_tax_offtaker = model_inputs["r_tax_offtaker"],
          pwf_om = model_inputs["pwf_om"],
          pwf_e = model_inputs["pwf_e"],
          pwf_prod_incent = model_inputs["pwf_prod_incent"],
          LevelizationFactor = model_inputs["LevelizationFactor"],
          LevelizationFactorProdIncent = model_inputs["LevelizationFactorProdIncent"],
          StorageCostPerKW = model_inputs["StorageCostPerKW"],
          StorageCostPerKWH = model_inputs["StorageCostPerKWH"],
          OMperUnitSize = model_inputs["OMperUnitSize"],
          CapCostSlope = model_inputs["CapCostSlope"],
          CapCostYInt = model_inputs["CapCostYInt"],
          CapCostX = model_inputs["CapCostX"],
          ProdIncentRate = model_inputs["ProdIncentRate"],
          MaxProdIncent = model_inputs["MaxProdIncent"],
          MaxSizeForProdIncent = model_inputs["MaxSizeForProdIncent"],
          two_party_factor = model_inputs["two_party_factor"],
          analysis_years = model_inputs["analysis_years"],
          AnnualElecLoad = model_inputs["AnnualElecLoad"],
          LoadProfile = model_inputs["LoadProfile"],
          ProdFactor = model_inputs["ProdFactor"],
          StorageMinChargePcent = model_inputs["StorageMinChargePcent"],
          EtaStorIn = model_inputs["EtaStorIn"],
          EtaStorOut = model_inputs["EtaStorOut"],
          InitSOC = model_inputs["InitSOC"],
          MaxSize = model_inputs["MaxSize"],
          MinStorageSizeKW = model_inputs["MinStorageSizeKW"],
          MaxStorageSizeKW = model_inputs["MaxStorageSizeKW"],
          MinStorageSizeKWH = model_inputs["MinStorageSizeKWH"],
          MaxStorageSizeKWH = model_inputs["MaxStorageSizeKWH"],
          TechClassMinSize = model_inputs["TechClassMinSize"],
          MinTurndown = model_inputs["MinTurndown"],
          FuelRate = model_inputs["FuelRate"],
          FuelAvail = model_inputs["FuelAvail"],
          FixedMonthlyCharge = model_inputs["FixedMonthlyCharge"],
          AnnualMinCharge = model_inputs["AnnualMinCharge"],
          MonthlyMinCharge = model_inputs["MonthlyMinCharge"],
          ExportRates = model_inputs["ExportRates"],
          TimeStepRatchetsMonth = model_inputs["TimeStepRatchetsMonth"],
          DemandRatesMonth = model_inputs["DemandRatesMonth"],
          DemandLookbackPercent = model_inputs["DemandLookbackPercent"],
          MaxDemandInTier = model_inputs["MaxDemandInTier"],
          MaxDemandMonthsInTier = model_inputs["MaxDemandMonthsInTier"],
          MaxUsageInTier = model_inputs["MaxUsageInTier"],
          FuelBurnRateM = model_inputs["FuelBurnRateM"],
          FuelBurnRateB = model_inputs["FuelBurnRateB"],
          NMILLimits = model_inputs["NMILLimits"],
          TechToNMILMapping = model_inputs["TechToNMILMapping"],
          DemandRates = model_inputs["DemandRates"],
          TimeStepRatchets = model_inputs["TimeStepRatchets"],
          DemandLookbackMonths = model_inputs["DemandLookbackMonths"],
          CapCostSegCount = model_inputs["CapCostSegCount"],
          FuelBinCount = model_inputs["FuelBinCount"],
          DemandBinCount  = model_inputs["DemandBinCount"],
          DemandMonthsBinCount = model_inputs["DemandMonthsBinCount"],
          TimeStepCount = model_inputs["TimeStepCount"],
          NumRatchets = model_inputs["NumRatchets"],
          TimeStepScaling = model_inputs["TimeStepScaling"])

    return reopt_run(p)
end


#function fast_reopt(args...;
#          Tech,
#          Load,
#          TechClass,
#          TechIsGrid,
#          TechToLoadMatrix,
#          TurbineDerate,
#          TechToTechClassMatrix,
#          NMILRegime,
#          r_tax_owner,
#          r_tax_offtaker,
#          pwf_om,
#          pwf_e,
#          pwf_prod_incent,
#          LevelizationFactor,
#          LevelizationFactorProdIncent,
#          StorageCostPerKW,
#          StorageCostPerKWH,
#          OMperUnitSize,
#          CapCostSlope,
#          CapCostYInt,
#          CapCostX,
#          ProdIncentRate,
#          MaxProdIncent,
#          MaxSizeForProdIncent,
#          two_party_factor,
#          analysis_years,
#          AnnualElecLoad,
#          LoadProfile,
#          ProdFactor,
#          StorageMinChargePcent,
#          EtaStorIn,
#          EtaStorOut,
#          InitSOC,
#          MaxSize,
#          MinStorageSizeKW,
#          MaxStorageSizeKW,
#          MinStorageSizeKWH,
#          MaxStorageSizeKWH,
#          TechClassMinSize,
#          MinTurndown,
#          FuelRate,
#          FuelAvail,
#          FixedMonthlyCharge,
#          AnnualMinCharge,
#          MonthlyMinCharge,
#          ExportRates,
#          TimeStepRatchetsMonth,
#          DemandRatesMonth,
#          DemandLookbackPercent,
#          MaxDemandInTier,
#          MaxDemandMonthsInTier,
#          MaxUsageInTier,
#          FuelBurnRateM,
#          FuelBurnRateB,
#          NMILLimits,
#          TechToNMILMapping,
#          DemandRates,
#          TimeStepRatchets,
#          DemandLookbackMonths,
#          CapCostSegCount,
#          FuelBinCount,
#          DemandBinCount ,
#          DemandMonthsBinCount,
#          TimeStepCount,
#          NumRatchets,
#          TimeStepScaling,
#          kwargs...
#    )
#
#    pBattLevelCount = 1
#    pSeg = 1:CapCostSegCount
#    pPoints = 0:CapCostSegCount
#    pMonth = 1:12
#    pRatchets = 1:NumRatchets
#    pFuelBin = 1:FuelBinCount
#    pDemandBin = 1:DemandBinCount
#    pDemandMonthsBin = 1:DemandMonthsBinCount
#    pBattLevel=1:pBattLevelCount
#    pTimeStep=1:TimeStepCount
#    pTimeStepBat=0:TimeStepCount
#    pTechIsGrid = parameter(Tech, TechIsGrid)
#    pTechToLoadMatrix = parameter((Tech, Load), TechToLoadMatrix)
#    pTurbineDerate = parameter(Tech, TurbineDerate)
#    pTechToTechClassMatrix = parameter((Tech, TechClass), TechToTechClassMatrix)
#    ppwf_prod_incent = parameter(Tech, pwf_prod_incent)
#    pLevelizationFactor = parameter(Tech, LevelizationFactor)
#    pLevelizationFactorProdIncent = parameter(Tech, LevelizationFactorProdIncent)
#    pStorageCostPerKW = parameter(pBattLevel, StorageCostPerKW)
#    pStorageCostPerKWH = parameter(pBattLevel, StorageCostPerKWH)
#    pOMperUnitSize = parameter(Tech, OMperUnitSize)
#    pCapCostSlope = parameter((Tech, pSeg), CapCostSlope)
#    pCapCostYInt = parameter((Tech, pSeg), CapCostYInt)
#    pCapCostX = parameter((Tech, pPoints), CapCostX)
#    pProdIncentRate = parameter((Tech, Load), ProdIncentRate)
#    pMaxProdIncent = parameter(Tech, MaxProdIncent)
#    pMaxSizeForProdIncent = parameter(Tech, MaxSizeForProdIncent)
#    pLoadProfile = parameter((Load, pTimeStep), LoadProfile)
#    pProdFactor = parameter((Tech, Load, pTimeStep), ProdFactor)
#    pEtaStorIn = parameter((Tech, Load), EtaStorIn)
#    pEtaStorOut = parameter(Load, EtaStorOut)
#    pMaxSize = parameter(Tech, MaxSize)
#    pTechClassMinSize = parameter(TechClass, TechClassMinSize)
#    pMinTurndown = parameter(Tech, MinTurndown)
#    pTimeStepRatchets = emptySetException(pRatchets, TimeStepRatchets)
#    pDemandRates = emptySetException((pRatchets, pDemandBin), DemandRates, true)
#    pFuelRate = parameter((Tech, pFuelBin, pTimeStep), FuelRate)
#    pFuelAvail = parameter((Tech, pFuelBin), FuelAvail)
#    pExportRates = parameter((Tech, Load, pTimeStep), ExportRates)
#    pTimeStepRatchetsMonth = parameter(pMonth, TimeStepRatchetsMonth)
#    pDemandRatesMonth = parameter((pMonth, pDemandMonthsBin), DemandRatesMonth)
#    pMaxDemandInTier = parameter(pDemandBin, MaxDemandInTier)
#    pMaxDemandMonthsInTier = parameter(pDemandMonthsBin, MaxDemandMonthsInTier)
#    pMaxUsageInTier = parameter(pFuelBin, MaxUsageInTier)
#    pFuelBurnRateM = parameter((Tech, Load, pFuelBin), FuelBurnRateM)
#    pFuelBurnRateB = parameter((Tech, Load, pFuelBin), FuelBurnRateB)
#    pNMILLimits = parameter(NMILRegime, NMILLimits)
#    pTechToNMILMapping = parameter((Tech, NMILRegime), TechToNMILMapping)
#
#    param = Parameter(Tech, 
#                      Load, 
#                      TechClass,
#                      pTechIsGrid,
#                      pTechToLoadMatrix,
#                      pTurbineDerate,
#                      pTechToTechClassMatrix,
#                      NMILRegime,
#                      r_tax_owner,
#                      r_tax_offtaker,
#                      pwf_om,
#                      pwf_e,
#                      pwf_prod_incent,
#                      pLevelizationFactor,
#                      pLevelizationFactorProdIncent,
#                      pStorageCostPerKW,
#                      pStorageCostPerKWH,
#                      pOMperUnitSize,
#                      pCapCostSlope,
#                      pCapCostYInt,
#                      pCapCostX,
#                      pProdIncentRate,
#                      pMaxProdIncent,
#                      pMaxSizeForProdIncent,
#                      two_party_factor,
#                      analysis_years,
#                      AnnualElecLoad,
#                      pLoadProfile,
#                      pProdFactor,
#                      StorageMinChargePcent,
#                      pEtaStorIn,
#                      pEtaStorOut,
#                      InitSOC,
#                      pMaxSize,
#                      MinStorageSizeKW,
#                      MaxStorageSizeKW,
#                      MinStorageSizeKWH,
#                      MaxStorageSizeKWH,
#                      pTechClassMinSize,
#                      MinTurndown,
#                      pFuelRate,
#                      pFuelAvail,
#                      FixedMonthlyCharge,
#                      AnnualMinCharge,
#                      MonthlyMinCharge,
#                      pExportRates,
#                      pTimeStepRatchetsMonth,
#                      pDemandRatesMonth,
#                      DemandLookbackPercent,
#                      pMaxDemandInTier,
#                      pMaxDemandMonthsInTier,
#                      pMaxUsageInTier,
#                      pFuelBurnRateM,
#                      pFuelBurnRateB,
#                      pNMILLimits,
#                      pTechToNMILMapping,
#                      pDemandRates,
#                      pTimeStepRatchets,
#                      DemandLookbackMonths,
#                      CapCostSegCount,
#                      FuelBinCount,
#                      DemandBinCount ,
#                      DemandMonthsBinCount,
#                      pBattLevelCount,
#                      TimeStepCount,
#                      pSeg,
#                      pPoints,
#                      pMonth,
#                      pRatchets,
#                      pFuelBin,
#                      pDemandBin,
#                      pDemandMonthsBin,
#                      pBattLevel,
#                      pTimeStep,
#                      pTimeStepBat,
#                      TimeStepScaling)
#
#    return reopt_run(param)    
#
#end



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
    REopt = direct_model(Xpress.Optimizer(MAXTIME=MAXTIME))

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
        results["year_one_soc_series_pct"] = value.(dvStoredEnergy)/results["batt_kwh"]
    else
        results["year_one_soc_series_pct"] = []
    end
    
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
        
    GeneratorTechs = filter(t->TechToTechClassMatrix[t, "GENERATOR"] == 1, Tech)
    if !isempty(GeneratorTechs)
		results["Generator"] = Dict()
        results["gen_net_fixed_om_costs"] = value(GenPerUnitSizeOMCosts) * r_tax_fraction_owner
        results["gen_net_variable_om_costs"] = value(GenPerUnitProdOMCosts) * r_tax_fraction_owner
		# TODO: calculate rest of Generator costs
    else
    	results["gen_net_fixed_om_costs"] = 0
        results["gen_net_variable_om_costs"] = 0
        results["gen_total_fuel_cost"] = 0
        results["gen_year_one_fuel_cost"] = 0
		results["gen_year_one_variable_om_costs"] = 0
    end
    
    
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
    
    #DemandPeaks = value.(dvPeakDemandE)
    #MonthlyDemandPeaks = value.(dvPeakDemandEMonth)
    
    if termination_status(REopt) == MOI.OPTIMAL
        status = "optimal"
#     elseif termination_status(REopt) == MOI.TIME_LIMIT && has_values(REopt)
#         error(TimeoutExpired)
    else
        status = "not optimal"
    end
    results["status"] = status
    return results
end
