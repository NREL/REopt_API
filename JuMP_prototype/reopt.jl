## REopt port to Julia

using JuMP
using Xpress
using MathOptInterface
const MOI = MathOptInterface

# Data
include("utils.jl")
#dataPath = "data/Runeda919d6-1481-4bf9-a531-a1b3397c8c67"

try 
    global dataPath
    dataPath = "data/Run$uuid"
catch e
    if isa(e, UndefVarError) || isa(e, ArgumentError)
        println("\nusing default uuid\n")
    else
        @warn e
    end
end

datToVariable(dataPath * "/Inputs/")
# NEED this when there is only one tech
#Tech = [:UTIL1]

REopt = Model()

# Counting Sets
CapCostSegCount = 5
FuelBinCount = 1
DemandBinCount = 1
demandMonthsBinCount = 1
BattLevelCount = 1
TimeStepScaling = 1.0
TimeStepCount = 35040
Obj = 5
REoptTol = 5e-5
NumRatchets = 20

readCmd(dataPath * "/Inputs/cmd.log")

#NEED to figure out new way of doing FuelAvail
FuelAvail = [1.0e10 for x in 1:length(Tech)]

Seg = 1:CapCostSegCount
Points = 0:CapCostSegCount
Month = 1:12
Ratchets = 1:NumRatchets
FuelBin = 1:FuelBinCount
DemandBin = 1:DemandBinCount
DemandMonthsBin = 1:DemandMonthsBinCount
BattLevel=1:BattLevelCount
TimeStep=1:TimeStepCount
TimeStepBat=0:TimeStepCount

## TAILORED BIG M
#MaxDemandMonthsInTier = [AnnualElecLoad]
#MaxDemandInTier = [AnnualElecLoad]
##MaxSize[CapCostSegCount] = [AnnualElecLoad]
#MaxUsageInTier = [AnnualElecLoad]


##### Sets and Parameter #####
##############################

#initializations from DAT1 ! constants
#Tech
#Load ##Had to change JSON from "load" to "Load"
TechIsGrid = parameter(Tech, TechIsGrid)
TechToLoadMatrix = parameter((Tech, Load), TechToLoadMatrix)
#TechClass
TurbineDerate = parameter(Tech, TurbineDerate)
TechToTechClassMatrix = parameter((Tech, TechClass), TechToTechClassMatrix)
#NMILRegime

#initializations from DAT2 ! economics
#r_tax_owner
#r_tax_offtaker
#pwf_om
#pwf_e
pwf_prod_incent = parameter(Tech, pwf_prod_incent)
LevelizationFactor = parameter(Tech, LevelizationFactor)
LevelizationFactorProdIncent = parameter(Tech, LevelizationFactorProdIncent)
StorageCostPerKW = parameter(BattLevel, StorageCostPerKW)
StorageCostPerKWH = parameter(BattLevel, StorageCostPerKWH)
OMperUnitSize = parameter(Tech, OMperUnitSize)
CapCostSlope = parameter((Tech, Seg), CapCostSlope)
CapCostYInt = parameter((Tech, Seg), CapCostYInt)
CapCostX = parameter((Tech, Points), CapCostX)
ProdIncentRate = parameter((Tech, Load), ProdIncentRate)
MaxProdIncent = parameter(Tech, MaxProdIncent)
MaxSizeForProdIncent = parameter(Tech, MaxSizeForProdIncent)
#two_party_factor
#analysis_years

#initializations from DAT3
#AnnualElecLoad

#initializations from DAT4
LoadProfile = parameter((Load, TimeStep), LoadProfile)

#initializations from DAT5 ! GIS
ProdFactor = parameter((Tech, Load, TimeStep), ProdFactor)

#initializations from DAT6 ! storage <--NEED A BAU VERSION WITH EMPTY PARAMS?
#StorageMinChargePcent
EtaStorIn = parameter((Tech, Load), EtaStorIn)
EtaStorOut = parameter(Load, EtaStorOut)
BattLevelCoef = parameter((BattLevel, 1:2), BattLevelCoef)
#InitSOC

#initializations from DAT7 ! maxsizes
MaxSize = parameter(Tech, MaxSize)
#MinStorageSizeKW
#MaxStorageSizeKW
#MinStorageSizeKWH
#MaxStorageSizeKWH
TechClassMinSize = parameter(TechClass, TechClassMinSize)
MinTurndown = parameter(Tech, MinTurndown)

#initializations from DAT8
function tsr(Ratchets, TimeStepRatchets)
    try
        return parameter(Ratchets, TimeStepRatchets)
    catch
        return []
    end
end

TimeStepRatchets = tsr(Ratchets, TimeStepRatchets)

#initializations from DAT9
DemandRates = parameter((Ratchets, DemandBin), DemandRates)

#initializations from DAT10 ! FuelCost
FuelRate = parameter((Tech, FuelBin, TimeStep), FuelRate)

# MAY NEED TO CHANGE to (Tech, FuelBin)
FuelAvail = parameter((Tech, FuelBin), FuelAvail)
#FixedMonthlyCharge
#AnnualMinCharge
#MonthlyMinCharge

#initializations from DAT11
ExportRates = parameter((Tech, Load, TimeStep), ExportRates)

#initializations from DAT12
TimeStepRatchetsMonth = parameter(Month, TimeStepRatchetsMonth)

#initializations from DAT13
DemandRatesMonth = parameter((Month, DemandMonthsBin), DemandRatesMonth)

#initializations from DAT14 ! LookbackMonthsAndPercent
#DemandLookbackMonths
#DemandLookbackPercent

#initializations from DAT15 ! UtilityTiers
MaxDemandInTier = parameter(DemandBin, MaxDemandInTier)
MaxDemandMonthsInTier = parameter(DemandMonthsBin, MaxDemandMonthsInTier)
MaxUsageInTier = parameter(FuelBin, MaxUsageInTier)

#initializations from DAT16
FuelBurnRateM = parameter((Tech, Load, FuelBin), FuelBurnRateM)
FuelBurnRateB = parameter((Tech, Load, FuelBin), FuelBurnRateB)

#initializations from DAT17  ! net metering
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
    dvStorageSizeKWH[BattLevel] >= 0
    dvStorageSizeKW[BattLevel] >= 0
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
    binBattLevel[BattLevel], Bin

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
    #r_tax_fraction_owner >= 0
    #r_tax_fraction_offtaker >= 0
    TotalMinCharge >= 0

# ADDED due to calculations
    Year1ElecProd
    AverageElecProd
    Year1WindProd
    AverageWindProd

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
            dvFuelUsed[t,fb] <= FuelAvail[fb])
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
@constraint(REopt, dvStoredEnergy[0] == InitSOC * sum(dvStorageSizeKWH[b] for b in BattLevel) / TimeStepScaling)
@constraint(REopt, MinStorageSizeKWH <= sum(dvStorageSizeKWH[b] for b in BattLevel) <=  MaxStorageSizeKWH)
@constraint(REopt, MinStorageSizeKW <= sum(dvStorageSizeKW[b] for b in BattLevel) <=  MaxStorageSizeKW)


### Battery Operations
@constraint(REopt, [ts in TimeStep],
	        dvElecToStor[ts] == sum(ProdFactor[t,LD,ts] * LevelizationFactor[t] * dvRatedProd[t,LD,ts,s,fb] * EtaStorIn[t,LD]
                                    for t in Tech, LD in [Symbol("1S")], s in Seg, fb in FuelBin))
@constraint(REopt, [ts in TimeStep],
	        dvStoredEnergy[ts] == dvStoredEnergy[ts-1] + dvElecToStor[ts] - dvElecFromStor[ts] / EtaStorOut[Symbol("1S")])
@constraint(REopt, [ts in TimeStep],
	        dvElecFromStor[ts] / EtaStorOut[Symbol("1S")] <=  dvStoredEnergy[ts-1])
@constraint(REopt, [ts in TimeStep],
	        dvStoredEnergy[ts] >=  StorageMinChargePcent * sum(dvStorageSizeKWH[b] / TimeStepScaling for b in BattLevel))

### Operational Nuance
@constraint(REopt, [ts in TimeStep],
	        sum(dvStorageSizeKW[b] for b in BattLevel) >=  dvElecToStor[ts])
@constraint(REopt, [ts in TimeStep],
	        sum(dvStorageSizeKW[b] for b in BattLevel) >=  dvElecFromStor[ts])
@constraint(REopt, dvMeanSOC == sum(dvStoredEnergy[ts] for ts in TimeStep) / TimeStepCount)
@constraint(REopt, [ts in TimeStep],
	        sum(dvStorageSizeKWH[b] for b in BattLevel) >=  dvStoredEnergy[ts] * TimeStepScaling)
@constraint(REopt, [ts in TimeStep],
            dvElecToStor[ts] <= MaxStorageSizeKW * binBattCharge[ts])
@constraint(REopt, [ts in TimeStep],
            dvElecFromStor[ts] <= MaxStorageSizeKW * binBattDischarge[ts])
@constraint(REopt, [ts in TimeStep],
            binBattDischarge[ts] + binBattCharge[ts] <= 1)
@constraint(REopt, [t in Tech],
	        ElecToBatt[t] == sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t,LD,ts] * LevelizationFactor[t]
                                 for ts in TimeStep, LD in [Symbol("1S")], s in Seg, fb in FuelBin))
@constraint(REopt, [b in BattLevel],
            BattLevelCoef[b,1] * sum(ElecToBatt[t] for t in Tech if TechIsGrid[t]==1) -
            BattLevelCoef[b,2] * sum(ElecToBatt[t] for t in Tech if TechIsGrid[t]!=1) <=
            (1 - binBattLevel[b]) * MaxStorageSizeKWH / TimeStepScaling * 365* 2)

### Binary Bookkeeping
@constraint(REopt, [t in Tech],
            sum(binSegChosen[t,s] for s in Seg) == 1)
@constraint(REopt, [b in TechClass],
            sum(binSingleBasicTech[t,b] for t in Tech) <= 1)

### Battery Level
@constraint(REopt, [b in BattLevel],
            dvStorageSizeKWH[b] <= MaxStorageSizeKWH * binBattLevel[b])
@constraint(REopt, [b in BattLevel],
            dvStorageSizeKW[b] <= MaxStorageSizeKW * binBattLevel[b])

###### Not Sure ######
@constraint(REopt, sum(binBattLevel[b] for b in BattLevel) == 1)
###### Not Sure ######

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
@constraint(REopt, [LD in Load, ts in TimeStep; LD == Symbol("1R")],
            sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t,LD,ts] * LevelizationFactor[t]
                for t in Tech, s in Seg, fb in FuelBin) + dvElecFromStor[ts] >= LoadProfile[LD,ts])

###  Net Meter Module
@constraint(REopt, sum(binNMLorIL[n] for n in NMILRegime) == 1)
@constraint(REopt, [n in NMILRegime; n != :AboveIL],
            sum(TechToNMILMapping[t,n] * TurbineDerate[t] * dvSystemSize[t,s]
                for t in Tech, s in Seg) <= NMILLimits[n] * binNMLorIL[n])
@constraint(REopt, sum(TechToNMILMapping[t, :AboveIL] * TurbineDerate[t] * dvSystemSize[t, s] for t in Tech, s in Seg)  <= NMILLimits[:AboveIL] * binNMLorIL[:AboveIL])

###  Rate Variable Definitions
@constraint(REopt, [t in [Symbol("UTIL1")], LD in Load, fb in FuelBin, ts in TimeStep],
	        sum(dvRatedProd[t,LD,ts,s,fb] for s in Seg) == sum(dvGrid[LD,ts,db,fb,dbm] for db in DemandBin, dbm in DemandMonthsBin))
@constraint(REopt, [t in [Symbol("UTIL1")], fb in FuelBin, m in Month],
	        UsageInTier[m, fb] ==  sum(dvRatedProd[t,LD,ts,s,fb] for LD in Load, ts in TimeStepRatchetsMonth[m], s in Seg))

### Fuel Bins
@constraint(REopt, [m in Month, fb in FuelBin; fb < FuelBinCount],
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
                       for t in Tech, LD in [Symbol("1R"), Symbol("1W"), Symbol("1S")],
                       ts in TimeStep, s in Seg, fb in FuelBin if TechIsGrid[t] == 0) <=  AnnualElecLoad)

###
#Added, but has awful bounds
@constraint(REopt, [t in Tech, b in TechClass],
            sum(dvSystemSize[t, s] * TechToTechClassMatrix[t, b] for s in Seg) <= MaxSize[t] * binSingleBasicTech[t, b])
@constraint(REopt, NONDISPATCH[t in Tech, ts in TimeStep, s in Seg; TechToTechClassMatrix[t, :PV] == 1 || TechToTechClassMatrix[t, :WIND] == 1],
	        sum(dvRatedProd[t,LD,ts,s,fb] for fb in FuelBin,
                LD in [Symbol("1R"), Symbol("1W"), Symbol("1X"), Symbol("1S")]) ==  dvSystemSize[t, s])


### Parts of Objective
@constraint(REopt, Year1ElecProd == sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling
                                        for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                        (TechToTechClassMatrix[t, :PV] == 1 && (LD == Symbol("1R") || LD == Symbol("1W") || LD == Symbol("1X") || LD == Symbol("1S")))))
@constraint(REopt, AverageElecProd == sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling * LevelizationFactor[t]
                                          for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                          (TechToTechClassMatrix[t, :PV] == 1 && (LD == Symbol("1R") || LD == Symbol("1W") || LD == Symbol("1X") || LD == Symbol("1S")))))
@constraint(REopt, Year1WindProd == sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling
                                        for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                        (TechToTechClassMatrix[t, :WIND] == 1 && (LD == Symbol("1R") || LD == Symbol("1W") || LD == Symbol("1X") || LD == Symbol("1S")))))
@constraint(REopt, AverageWindProd == sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling * LevelizationFactor[t]
                                          for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                          (TechToTechClassMatrix[t, :WIND] == 1 && (LD == Symbol("1R") || LD == Symbol("1W") || LD == Symbol("1X") || LD == Symbol("1S")))))
@constraint(REopt, TotalTechCapCosts == sum(CapCostSlope[t, s] * dvSystemSize[t, s] + CapCostYInt[t,s] * binSegChosen[t,s]
                                            for t in Tech, s in Seg))
@constraint(REopt, TotalStorageCapCosts == sum(dvStorageSizeKWH[b] * StorageCostPerKWH[b] + dvStorageSizeKW[b] *  StorageCostPerKW[b]
                                               for b in BattLevel))
@constraint(REopt, TotalOMCosts == sum(OMperUnitSize[t] * pwf_om * dvSystemSize[t, s]
                                       for t in Tech, s in Seg))

### Aggregates of definitions
@constraint(REopt, TotalEnergyCharges == sum(dvFuelCost[t,fb]
                                             for t in Tech, fb in FuelBin))
@constraint(REopt, DemandTOUCharges == sum(dvPeakDemandE[r, db] * DemandRates[r,db] * pwf_e
                                           for r in Ratchets, db in DemandBin))
@constraint(REopt, DemandTOUCharges == 0)
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
            sum(ProdFactor[t, Symbol("1R"), ts]*dvRatedProd[t, Symbol("1R"), ts, 1, 1] 
                for t in Tech, ts in TimeStep));
@expression(REopt, powerfromUTIL1, 
            sum(ProdFactor[:UTIL1, Symbol("1R"), ts]*dvRatedProd[:UTIL1, Symbol("1R"), ts, 1, 1] 
                for ts in TimeStep));


println("Model built. Moving on to optimization...")

optimize!(REopt, with_optimizer(Xpress.Optimizer, OUTPUTLOG=1, LPLOG=1, MIPLOG=-10))


### Output Module
println("\n\nPreparing outputs...\n\n")

@expression(REopt, ExportedElecPV, 
            sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * LevelizationFactor[t] * TimeStepScaling
                for t in Tech, LD in [Symbol("1W"), Symbol("1X")], ts in TimeStep, s in Seg, fb in FuelBin 
                if TechToTechClassMatrix[t, :PV] == 1))
@expression(REopt, ExportedElecWIND,
            sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * LevelizationFactor[t] * TimeStepScaling
                for t in Tech, LD in [Symbol("1W"), Symbol("1X")], ts in TimeStep, s in Seg, fb in FuelBin 
                if TechToTechClassMatrix[t, :WIND] == 1))
@expression(REopt, ExportedBenefitYr1,
            sum(dvRatedProd[t,LD,ts,s,fb] * TimeStepScaling * ProdFactor[t, LD, ts] * ExportRates[t,LD,ts] 
                for t in Tech, LD in Load, ts in TimeStep, s in Seg, fb in FuelBin ))
@expression(REopt, Year1UtilityEnergy, 
            sum(dvRatedProd[:UTIL1,LD,ts,s,fb] * TimeStepScaling * ProdFactor[:UTIL1, LD, ts] 
                for LD in Load, ts in TimeStep, s in Seg, fb in FuelBin))


ojv = JuMP.objective_value(REopt)
Year1EnergyCost = value(TotalEnergyCharges / pwf_e)
Year1DemandCost = value(TotalDemandCharges / pwf_e)
Year1DemandTOUCost = value(DemandTOUCharges / pwf_e)
Year1DemandFlatCost = value(DemandFlatCharges / pwf_e)
Year1FixedCharges = value(TotalFixedCharges / pwf_e)
Year1MinCharges = value(MinChargeAdder / pwf_e)
Year1Bill = Year1EnergyCost + Year1DemandCost + Year1FixedCharges + Year1MinCharges

println("Objective Value: ", ojv)
println("Year1EnergyCost: ", Year1EnergyCost)
println("Year1DemandCost: ", Year1DemandCost)
println("Year1DemandTOUCost: ", Year1DemandTOUCost)
println("Year1DemandFlatCost: ", Year1DemandFlatCost)
println("Year1FixedCharges: ", Year1FixedCharges)
println("Year1MinCharges: ", Year1MinCharges)
println("Year1Bill: ", Year1Bill)




### Stuff to add
#
#@expression(REopt, Year1Utilityto1R, 
#            sum(dvRatedProd[:UTIL1,LD,ts,s,fb] *TimeStepScaling 
#                for LD in Load, ts in TimeStep, s in Seg, fb in FuelBin))
#
#@expression(REopt, Year1Load, 
#            sum(dvRatedProd[t,LD,ts,s,fb] *TimeStepScaling * ProdFactor[t, LD, ts] 
#                for t in Tech, LD in [Symbol("1R")], ts in TimeStep, s in Seg, fb in FuelBin))
#
#@expression(REopt, Year1PVNMto1R, 
#            sum(dvRatedProd[:PVNM,LD,ts,s,fb] *TimeStepScaling * ProdFactor[:PVNM, LD, ts] 
#                for LD in [Symbol("1R")], ts in TimeStep, s in Seg, fb in FuelBin))
#
#@expression(REopt, Year1Loadwbat, 
#            sum(dvRatedProd[t,LD,ts,s,fb] * LevelizationFactor[t] * ProdFactor[t, LD, ts] + dvElecFromStor[ts] 
#                for t in Tech, LD in [Symbol("1R")], ts in TimeStep, s in Seg, fb in FuelBin))
#
#@expression(REopt, R1[t in Tech], 
#            sum(ProdFactor[t, LD, ts] * dvRatedProd[t,LD,ts,s,fb] for LD in [Symbol("1R")], ts in TimeStep, s in Seg, fb in FuelBin))
#@expression(REopt, S1[t in Tech], 
#            sum(ProdFactor[t, LD, ts] * dvRatedProd[t,LD,ts,s,fb] for LD in [Symbol("1S")], ts in TimeStep, s in Seg, fb in FuelBin))
#
#@expression(REopt, PV[LD in Load], 
#            sum(ProdFactor[t, LD, ts] * dvRatedProd[t,LD,ts,s,fb] for t in [:PV], LD in Load, ts in TimeStep, s in Seg, fb in FuelBin))
#@expression(REopt, PVNM[LD in Load], 
#            sum(ProdFactor[t, LD, ts] * dvRatedProd[t,LD,ts,s,fb] for t in [:PVNM], ts in TimeStep, s in Seg, fb in FuelBin))
#@expression(REopt, UTIL1[LD in Load], 
#            sum(ProdFactor[t, LD, ts] * dvRatedProd[t,LD,ts,s,fb] for t in [:UTIL1], ts in TimeStep, s in Seg, fb in FuelBin))
#
#@expression(REopt, loadsattech[ts in TimeStep, t in Tech], 
#            sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t,LD,ts] * LevelizationFactor[t] + dvElecFromStor[ts] 
#                for LD in [Symbol("1R")], s in Seg, fb in FuelBin))
#
#
#GeneratorFuelUsed := sum(t in Tech, fb in FuelBin | TechToTechClassMatrix (t, "GENERATOR") = 1) dvFuelUsed(t, fb)
#

#GeneratorFuelUsed = AffExpr(0)
#
#for t in Tech, fb in FuelBin 
#    if TechToTechClassMatrix[t, "GENERATOR"] == 1
#        y = AffExpr(0, dvFuelUsed[t, fb] => 1)
#        add_to_expression!(GeneratorFuelUsed, y)
#    end
#end

#!************************** Writing to files ************************************
#
#
#!Time series dispatch output
#
#if sum(b in BattLevel) getsol(dvStorageSizeKWH(b)) > REoptTol then
#
#    fopen(OutputDir + "\\GridToBatt.csv", F_OUTPUT)
#        forall (ts in TimeStep) do
#           writeln (sum (s in Seg, fb in FuelBin)   getsol (dvRatedProd ("UTIL1", "1S", ts, s, fb)) * ProdFactor("UTIL1", "1S", ts) * LevelizationFactor("UTIL1"))
#        end-do
#    fclose(F_OUTPUT)
#
#    fopen(OutputDir + "\\ElecToStore.csv",F_OUTPUT)
#        forall (ts in TimeStep )     do
#           writeln (     getsol (dvElecToStor (ts)))
#        end-do
#    fclose(F_OUTPUT)
#
#    !Time series dispatch output
#    fopen(OutputDir + "\\ElecFromStore.csv",F_OUTPUT)
#        forall (ts in TimeStep )     do
#           writeln (    getsol (dvElecFromStor (ts)))
#        end-do
#    fclose(F_OUTPUT)
#
#    fopen(OutputDir + "\\StoredEnergy.csv",F_OUTPUT)
#        forall (ts in TimeStep )     do
#           writeln (   getsol (dvStoredEnergy (ts)))
#        end-do
#    fclose(F_OUTPUT)
#
#    forall (t in Tech | (TechToTechClassMatrix (t, "PV") = 1 and sum(s in Seg) getsol (dvSystemSize(t,s)) > REoptTol)) do
#
#        fopen(OutputDir + "\\PVtoBatt.csv", F_OUTPUT)
#            forall (ts in TimeStep) do
#               writeln (sum (s in Seg, fb in FuelBin)  getsol (dvRatedProd (t, "1S", ts, s, fb)) * ProdFactor(t, "1S", ts) * LevelizationFactor(t))
#            end-do
#        fclose(F_OUTPUT)
#
#    end-do
#
#    forall (t in Tech | (TechToTechClassMatrix (t, "WIND") = 1 and sum(s in Seg) getsol (dvSystemSize(t,s)) > 0)) do
#
#        fopen(OutputDir + "\\WINDtoBatt.csv", F_OUTPUT)
#            forall (ts in TimeStep) do
#               writeln (sum (s in Seg, fb in FuelBin)  getsol (dvRatedProd (t, "1S", ts, s, fb)) * ProdFactor(t, "1S", ts) * LevelizationFactor(t))
#            end-do
#        fclose(F_OUTPUT)
#
#    end-do
#
#end-if
#
#forall (t in Tech | (TechToTechClassMatrix (t, "PV") = 1 and sum(s in Seg) getsol (dvSystemSize(t,s)) > REoptTol)) do
#
#    fopen(OutputDir + "\\PVtoLoad.csv", F_OUTPUT)
#        forall (ts in TimeStep) do
#           writeln (sum (s in Seg, fb in FuelBin)   getsol (dvRatedProd (t, "1R", ts, s, fb)) * ProdFactor(t, "1R", ts) * LevelizationFactor(t))
#        end-do
#    fclose(F_OUTPUT)
#
#    fopen(OutputDir + "\\PVtoGrid.csv", F_OUTPUT)
#        forall (ts in TimeStep) do
#           writeln (sum (s in Seg, fb in FuelBin)   getsol (dvRatedProd (t, "1W", ts, s, fb)) * ProdFactor(t, "1W", ts) * LevelizationFactor(t) +
#                    sum (s in Seg, fb in FuelBin)   getsol (dvRatedProd (t, "1X", ts, s, fb)) * ProdFactor(t, "1X", ts) * LevelizationFactor(t))
#        end-do
#    fclose(F_OUTPUT)
#
#end-do
#
#forall (t in Tech | (TechToTechClassMatrix (t, "WIND") = 1 and sum(s in Seg) getsol (dvSystemSize(t,s)) > 0)) do
#
#    fopen(OutputDir + "\\WINDtoLoad.csv", F_OUTPUT)
#        forall (ts in TimeStep) do
#           writeln (sum (s in Seg, fb in FuelBin)   getsol (dvRatedProd (t, "1R", ts, s, fb)) * ProdFactor(t, "1R", ts) * LevelizationFactor(t))
#        end-do
#    fclose(F_OUTPUT)
#
#    fopen(OutputDir + "\\WINDtoGrid.csv", F_OUTPUT)
#        forall (ts in TimeStep) do
#           writeln (sum (s in Seg, fb in FuelBin)   getsol (dvRatedProd (t, "1W", ts, s, fb)) * ProdFactor(t, "1W", ts) * LevelizationFactor(t) +
#                    sum (s in Seg, fb in FuelBin)   getsol (dvRatedProd (t, "1X", ts, s, fb)) * ProdFactor(t, "1X", ts) * LevelizationFactor(t))
#        end-do
#    fclose(F_OUTPUT)
#
#end-do
#
#forall (t in Tech | (TechToTechClassMatrix (t, "GENERATOR") = 1 and sum(s in Seg) getsol (dvSystemSize(t,s)) > 0)) do
#
#    fopen(OutputDir + "\\GENERATORtoLoad.csv", F_OUTPUT)
#        forall (ts in TimeStep) do
#           writeln (sum (s in Seg, fb in FuelBin)   getsol (dvRatedProd (t, "1R", ts, s, fb)) * ProdFactor(t, "1R", ts) * LevelizationFactor(t))
#        end-do
#    fclose(F_OUTPUT)
#
#end-do
#
#fopen(OutputDir + "\\GridToLoad.csv", F_OUTPUT)
#    forall (ts in TimeStep) do
#       writeln (sum (s in Seg, fb in FuelBin)   getsol (dvRatedProd ("UTIL1", "1R", ts, s, fb)) * ProdFactor("UTIL1", "1R", ts) * LevelizationFactor("UTIL1"))
#    end-do
#fclose(F_OUTPUT)
#
#fopen(OutputDir + "\\Load.csv",F_OUTPUT)
#    forall (ts in TimeStep )     do
#       writeln (   getsol (LoadProfile("1R",ts)))
#    end-do
#fclose(F_OUTPUT)
#
#
#fopen(OutputDir + "\\DemandPeaks.csv",F_OUTPUT)
#    writeln ("Ratchet,DemandTier,PeakDemand")
#    forall  ( r in Ratchets, db in DemandBin)  do
#       writeln (r, ",", db, ",", getsol(dvPeakDemandE(r,db)),",")
#    end-do
#    writeln(",")
#    writeln("Month,Peak_Demand")
#    forall  ( m in Month, dbm in DemandMonthsBin)  do
#       writeln (m, ",", getsol(dvPeakDemandEMonth(m, dbm)),",")
#    end-do
#fclose(F_OUTPUT)
#
#
#! write outputs in JSON for post processing
#
#    Root:=addnode(out_json, 0, XML_ELT, "jsv")
#
#    Node:=addnode(out_json, Root, "status", status)
#    Node:=addnode(out_json, Root, "lcc", strfmt(getsol(RECosts) + 0.001*getsol(MinChargeAdder), 10, 0))
#
#    forall  (b in BattLevel)  do
#        Node:=addnode(out_json, Root, "batt_kwh", getsol (dvStorageSizeKWH(b)))
#    end-do
#
#    forall  (b in BattLevel)  do
#        Node:=addnode(out_json, Root, "batt_kw", getsol (dvStorageSizeKW(b)))
#    end-do
#
#    forall (t in Tech  | TechToTechClassMatrix(t, "PV") = 1 and sum(s in Seg) getsol (dvSystemSize(t,s)) > REoptTol)  do
#        Node:=addnode(out_json, Root, "pv_kw", sum(s in Seg) getsol (dvSystemSize(t,s)))
#    end-do
#
#    forall (t in Tech  | TechToTechClassMatrix(t, "WIND") = 1 and sum(s in Seg) getsol (dvSystemSize(t,s)) > 0)  do
#        Node:=addnode(out_json, Root, "wind_kw", sum(s in Seg) getsol (dvSystemSize(t,s)))
#    end-do
#
#    Node:=addnode(out_json, Root, "year_one_utility_kwh", strfmt(getsol (Year1UtilityEnergy) , 10, 4))
#    Node:=addnode(out_json, Root, "year_one_energy_cost", strfmt(getsol(Year1EnergyCost), 10, 2))
#    Node:=addnode(out_json, Root, "year_one_demand_cost", strfmt(getsol(Year1DemandCost), 10, 2))
#    Node:=addnode(out_json, Root, "year_one_demand_tou_cost", strfmt(getsol(Year1DemandTOUCost), 10, 2))
#    Node:=addnode(out_json, Root, "year_one_demand_flat_cost", strfmt(getsol(Year1DemandFlatCost), 10, 2))
#    Node:=addnode(out_json, Root, "year_one_export_benefit", strfmt(getsol(ExportBenefitYr1), 10, 0))
#    Node:=addnode(out_json, Root, "year_one_fixed_cost", strfmt(getsol(Year1FixedCharges), 10, 0))
#    Node:=addnode(out_json, Root, "year_one_min_charge_adder", strfmt(getsol(Year1MinCharges), 10, 2))
#    Node:=addnode(out_json, Root, "year_one_bill", strfmt(getsol(Year1Bill), 10, 2))
#    !Node:=addnode(out_json, Root, "year_one_payments_to_third_party_owner", strfmt(getsol(TotalDemandCharges) / pwf_e, 10, 0))
#    Node:=addnode(out_json, Root, "total_energy_cost", strfmt(getsol(TotalEnergyCharges) * r_tax_fraction_offtaker, 10, 2))
#    Node:=addnode(out_json, Root, "total_demand_cost", strfmt(getsol(TotalDemandCharges) * r_tax_fraction_offtaker, 10, 2))
#    Node:=addnode(out_json, Root, "total_fixed_cost", strfmt(getsol(TotalFixedCharges) * r_tax_fraction_offtaker, 10, 2))
#    Node:=addnode(out_json, Root, "total_min_charge_adder", strfmt(getsol(MinChargeAdder) * r_tax_fraction_offtaker, 10, 2))
#    Node:=addnode(out_json, Root, "total_payments_to_third_party_owner", 0)
#    Node:=addnode(out_json, Root, "net_capital_costs_plus_om", strfmt(getsol(TotalTechCapCosts) + getsol(TotalStorageCapCosts) + getsol(TotalOMCosts) * r_tax_fraction_owner, 10, 0))
#    Node:=addnode(out_json, Root, "net_capital_costs", strfmt(getsol(TotalTechCapCosts) + getsol(TotalStorageCapCosts), 10, 0))
#    Node:=addnode(out_json, Root, "average_yearly_pv_energy_produced", strfmt(getsol(AverageElecProd), 10, 0))
#    Node:=addnode(out_json, Root, "average_wind_energy_produced", strfmt(getsol(AverageWindProd), 10, 0))
#    Node:=addnode(out_json, Root, "year_one_energy_produced", strfmt(getsol(Year1ElecProd), 10, 0))
#    Node:=addnode(out_json, Root, "year_one_wind_energy_produced", strfmt(getsol(Year1WindProd), 10, 0))
#    Node:=addnode(out_json, Root, "average_annual_energy_exported", strfmt(getsol(ExportedElecPV), 10, 0))
#    Node:=addnode(out_json, Root, "average_annual_energy_exported_wind", strfmt(getsol(ExportedElecWIND), 10, 0))
#    Node:=addnode(out_json, Root, "fuel_used_gal", strfmt(getsol(GeneratorFuelUsed), 10, 2))
#
#jsonsave(out_json, OutputDir + "\\REopt_results.json")
