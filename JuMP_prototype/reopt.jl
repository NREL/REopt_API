## REopt port to Julia

using JuMP
using Xpress
using MathOptInterface
using JSON
const MOI = MathOptInterface

# Data
include("utils.jl")
dataPath = "data/Run5b75684a-232d-4e95-8bf1-3fcb47b07a46"

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

optimizer = Xpress.Optimizer(OUTPUTLOG=1, LPLOG=1, MIPLOG=-10)
REopt = direct_model(optimizer)

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
#FuelAvail = [1.0e10 for x in 1:length(Tech)]

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
function emptySetException(sets, values)
    try
        return parameter(sets, values)
    catch
        return []
    end
end

TimeStepRatchets = emptySetException(Ratchets, TimeStepRatchets)

#initializations from DAT9
#DemandRates = parameter((Ratchets, DemandBin), DemandRates)
DemandRates = emptySetException((Ratchets, DemandBin), DemandRates)

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
    #Year1ElecProd
    #AverageElecProd
    #Year1WindProd
    #AverageWindProd

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
@constraint(REopt, dvStoredEnergy[0] == InitSOC * sum(dvStorageSizeKWH[b] for b in BattLevel) / TimeStepScaling)
@constraint(REopt, MinStorageSizeKWH <= sum(dvStorageSizeKWH[b] for b in BattLevel))
@constraint(REopt, sum(dvStorageSizeKWH[b] for b in BattLevel) <=  MaxStorageSizeKWH)
@constraint(REopt, MinStorageSizeKW <= sum(dvStorageSizeKW[b] for b in BattLevel))
@constraint(REopt, sum(dvStorageSizeKW[b] for b in BattLevel) <=  MaxStorageSizeKW)


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
                       for t in Tech, LD in [Symbol("1R"), Symbol("1W"), Symbol("1S")],
                       ts in TimeStep, s in Seg, fb in FuelBin if TechIsGrid[t] == 0) <=  AnnualElecLoad)

###
#Added, but has awful bounds
@constraint(REopt, [t in Tech, b in TechClass],
            sum(dvSystemSize[t, s] * TechToTechClassMatrix[t, b] for s in Seg) <= MaxSize[t] * binSingleBasicTech[t, b])
@constraint(REopt, [t in Tech, ts in TimeStep, s in Seg; TechToTechClassMatrix[t, :PV] == 1 || TechToTechClassMatrix[t, :WIND] == 1],
	        sum(dvRatedProd[t,LD,ts,s,fb] for fb in FuelBin,
                LD in [Symbol("1R"), Symbol("1W"), Symbol("1X"), Symbol("1S")]) ==  dvSystemSize[t, s])


@expression(REopt, Year1ElecProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling
                                        for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                        (TechToTechClassMatrix[t, :PV] == 1 && (LD == Symbol("1R") || LD == Symbol("1W") || LD == Symbol("1X") || LD == Symbol("1S")))))
@expression(REopt, AverageElecProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling * LevelizationFactor[t]
                                          for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                          (TechToTechClassMatrix[t, :PV] == 1 && (LD == Symbol("1R") || LD == Symbol("1W") || LD == Symbol("1X") || LD == Symbol("1S")))))
@expression(REopt, Year1PVProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling
                                        for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                        (TechToTechClassMatrix[t, :PV] == 1 && (LD == Symbol("1R") || LD == Symbol("1W") || LD == Symbol("1X") || LD == Symbol("1S")))))
@expression(REopt, AveragePVProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling * LevelizationFactor[t]
                                          for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                          (TechToTechClassMatrix[t, :PV] == 1 && (LD == Symbol("1R") || LD == Symbol("1W") || LD == Symbol("1X") || LD == Symbol("1S")))))
@expression(REopt, Year1WindProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling
                                        for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                        (TechToTechClassMatrix[t, :WIND] == 1 && (LD == Symbol("1R") || LD == Symbol("1W") || LD == Symbol("1X") || LD == Symbol("1S")))))
@expression(REopt, AverageWindProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling * LevelizationFactor[t]
                                          for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                          (TechToTechClassMatrix[t, :WIND] == 1 && (LD == Symbol("1R") || LD == Symbol("1W") || LD == Symbol("1X") || LD == Symbol("1S")))))
@expression(REopt, Year1GenProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling
                                        for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                        (TechToTechClassMatrix[t, :GENERATOR] == 1 && (LD == Symbol("1R") || LD == Symbol("1W") || LD == Symbol("1X") || LD == Symbol("1S")))))
@expression(REopt, AverageGenProd, sum(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t, LD, ts] * TimeStepScaling * LevelizationFactor[t]
                                          for t in Tech, s in Seg, fb in FuelBin, ts in TimeStep, LD in Load if 
                                          (TechToTechClassMatrix[t, :GENERATOR] == 1 && (LD == Symbol("1R") || LD == Symbol("1W") || LD == Symbol("1X") || LD == Symbol("1S")))))


### Parts of Objective
@constraint(REopt, TotalTechCapCosts == sum(CapCostSlope[t, s] * dvSystemSize[t, s] + CapCostYInt[t,s] * binSegChosen[t,s]
                                            for t in Tech, s in Seg))
@constraint(REopt, TotalStorageCapCosts == sum(dvStorageSizeKWH[b] * StorageCostPerKWH[b] + dvStorageSizeKW[b] *  StorageCostPerKW[b]
                                               for b in BattLevel))
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
            sum(ProdFactor[t, Symbol("1R"), ts]*dvRatedProd[t, Symbol("1R"), ts, 1, 1] 
                for t in Tech, ts in TimeStep));
@expression(REopt, powerfromUTIL1, 
            sum(ProdFactor[:UTIL1, Symbol("1R"), ts]*dvRatedProd[:UTIL1, Symbol("1R"), ts, 1, 1] 
                for ts in TimeStep));


println("Model built. Moving on to optimization...")

optimize!(REopt)


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
@expression(REopt, ExportBenefitYr1,
            sum(dvRatedProd[t,LD,ts,s,fb] * TimeStepScaling * ProdFactor[t, LD, ts] * ExportRates[t,LD,ts] 
                for t in Tech, LD in Load, ts in TimeStep, s in Seg, fb in FuelBin ))
@expression(REopt, Year1UtilityEnergy, 
            sum(dvRatedProd[:UTIL1,LD,ts,s,fb] * TimeStepScaling * ProdFactor[:UTIL1, LD, ts] 
                for LD in Load, ts in TimeStep, s in Seg, fb in FuelBin))


ojv = JuMP.objective_value(REopt)+ 0.001*value(MinChargeAdder)
Year1EnergyCost = TotalEnergyCharges / pwf_e
Year1DemandCost = TotalDemandCharges / pwf_e
Year1DemandTOUCost = DemandTOUCharges / pwf_e
Year1DemandFlatCost = DemandFlatCharges / pwf_e
Year1FixedCharges = TotalFixedCharges / pwf_e
Year1MinCharges = MinChargeAdder / pwf_e
Year1Bill = Year1EnergyCost + Year1DemandCost + Year1FixedCharges + Year1MinCharges

results_JSON = Dict{String, Any}("lcc" => ojv)

results_JSON["batt_kwh"] = value(sum(dvStorageSizeKWH[b] for b in BattLevel))
results_JSON["batt_kw"] = value(sum(dvStorageSizeKW[b] for b in BattLevel))

if results_JSON["batt_kwh"] != 0
    results_JSON["year_one_soc_series_pct"] = value.(dvStoredEnergy)/results_JSON["batt_kwh"]
else
    results_JSON["year_one_soc_series_pct"] = value.(dvStoredEnergy)
end


PVClass = filter(t->TechToTechClassMatrix[t, :PV] == 1, Tech)
if !isempty(PVClass)
    results_JSON["PV"] = Dict()
    results_JSON["pv_kw"] = value(sum(dvSystemSize[t,s] for s in Seg, t in PVClass))
    @expression(REopt, PVtoBatt[t in PVClass, ts in TimeStep],
                sum(dvRatedProd[t, Symbol("1S"), ts, s, fb] * ProdFactor[t, Symbol("1S"), ts] * LevelizationFactor[t] for s in Seg, fb in FuelBin))
end

WINDClass = filter(t->TechToTechClassMatrix[t, :WIND] == 1, Tech)
if !isempty(WINDClass)
    results_JSON["Wind"] = Dict()
    results_JSON["wind_kw"] = value(sum(dvSystemSize[t,s] for s in Seg, t in WINDClass))
    @expression(REopt, WINDtoBatt[t in WINDClass, ts in TimeStep],
                sum(dvRatedProd[t, Symbol("1S"), ts, s, fb] * ProdFactor[t, Symbol("1S"), ts] * LevelizationFactor[t] for s in Seg, fb in FuelBin))
end
    
GENERATORClass = filter(t->TechToTechClassMatrix[t, :GENERATOR] == 1, Tech)
#if !isempty(GENERATORClass)
#    results_JSON["Generator"] = Dict()
#    results_JSON["gen_net_fixed_om_costs"] = value(GenPerUnitSizeOMCosts * r_tax_fraction_owner)
#    results_JSON["gen_net_variable_om_costs"] = value(GenPerUnitProdOMCosts * r_tax_fraction_owner)
#end

function JuMP.value(::Val{false})
    return 0.0
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
                         "year_one_payments_to_third_party_owner" => value(TotalDemandCharges / pwf_e),
                         "total_energy_cost" => value(TotalEnergyCharges * r_tax_fraction_offtaker),
                         "total_demand_cost" => value(TotalDemandCharges * r_tax_fraction_offtaker),
                         "total_fixed_cost" => value(TotalFixedCharges * r_tax_fraction_offtaker),
                         "total_export_benefit" => value(TotalEnergyExports * r_tax_fraction_offtaker),
                         "total_min_charge_adder" => value(MinChargeAdder * r_tax_fraction_offtaker),
                         "total_payments_to_third_party_owner" => 0, 
                         "net_capital_costs_plus_om" => value(TotalTechCapCosts + TotalStorageCapCosts + TotalOMCosts * r_tax_fraction_owner),
#                         "pv_net_fixed_om_costs" => value(PVPerUnitSizeOMCosts * r_tax_fraction_owner),
                         "average_wind_energy_produced" => value(AverageWindProd),
                         "year_one_energy_produced" => value(Year1ElecProd),
                         "year_one_wind_energy_produced" => value(Year1WindProd),
                         "average_annual_energy_exported_wind" => value(ExportedElecWIND),
                         "net_capital_costs" => value(TotalTechCapCosts + TotalStorageCapCosts))...)

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
#@show results_JSON["average_yearly_pv_energy_produced"]
@show results_JSON["average_wind_energy_produced"]
@show results_JSON["year_one_energy_produced"]
@show results_JSON["year_one_wind_energy_produced"]
#@show results_JSON["average_annual_energy_exported"]
@show results_JSON["average_annual_energy_exported_wind"]



@expression(REopt, GridToBatt[ts in TimeStep],
            sum(dvRatedProd[:UTIL1, Symbol("1S"), ts, s, fb] * ProdFactor[:UTIL1, Symbol("1S"), ts] * LevelizationFactor[:UTIL1] for s in Seg, fb in FuelBin))

@expression(REopt, GENERATORtoBatt[t in GENERATORClass, ts in TimeStep],
            sum(dvRatedProd[t, Symbol("1S"), ts, s, fb] * ProdFactor[t, Symbol("1S"), ts] * LevelizationFactor[t] for s in Seg, fb in FuelBin))

@expression(REopt, PVtoLoad[t in PVClass, ts in TimeStep],
            sum(dvRatedProd[t, Symbol("1R"), ts, s, fb] * ProdFactor[t, Symbol("1R"), ts] * LevelizationFactor[t] for s in Seg, fb in FuelBin))

@expression(REopt, PVtoGrid[t in PVClass, ts in TimeStep, LD in [Symbol("1W"), Symbol("1X")]],
            sum(dvRatedProd[t, LD, ts, s, fb] * ProdFactor[t, LD, ts] * LevelizationFactor[t] for s in Seg, fb in FuelBin))

@expression(REopt, WINDtoLoad[t in WINDClass, ts in TimeStep],
            sum(dvRatedProd[t, Symbol("1R"), ts, s, fb] * ProdFactor[t, Symbol("1R"), ts] * LevelizationFactor[t] for s in Seg, fb in FuelBin))

@expression(REopt, WINDtoGrid[t in WINDClass, ts in TimeStep, LD in [Symbol("1W"), Symbol("1X")]],
            sum(dvRatedProd[t, LD, ts, s, fb] * ProdFactor[t, LD, ts] * LevelizationFactor[t] for s in Seg, fb in FuelBin))

@expression(REopt, GENERATORtoLoad[t in GENERATORClass, ts in TimeStep],
            sum(dvRatedProd[t, Symbol("1R"), ts, s, fb] * ProdFactor[t, Symbol("1R"), ts] * LevelizationFactor[t] for s in Seg, fb in FuelBin))

@expression(REopt, GENERATORtoGrid[t in GENERATORClass, ts in TimeStep, LD in [Symbol("1W"), Symbol("1X")]],
            sum(dvRatedProd[t, LD, ts, s, fb] * ProdFactor[t, LD, ts] * LevelizationFactor[t] for s in Seg, fb in FuelBin))

@expression(REopt, GridtoLoad[ts in TimeStep],
            sum(dvRatedProd[:UTIL1, Symbol("1R"), ts, s, fb] * ProdFactor[:UTIL1, Symbol("1R"), ts] * LevelizationFactor[:UTIL1] for s in Seg, fb in FuelBin))

Site_load = LoadProfile[Symbol("1R"), :]

DemandPeaks = value.(dvPeakDemandE)
MonthlyDemandPeaks = value.(dvPeakDemandEMonth)

results_JSON["GridToBatt"] = value.(GridToBatt)
results_JSON["GENERATORtoBatt"] = value.(GENERATORtoBatt)
results_JSON["PVtoLoad"] = value.(PVtoLoad)
results_JSON["PVtoGrid"] = value.(PVtoGrid)
results_JSON["WINDtoLoad"] = value.(WINDtoLoad)
results_JSON["WINDtoGrid"] = value.(WINDtoGrid)
results_JSON["GENERATORtoLoad"] = value.(GENERATORtoLoad)
results_JSON["GENERATORtoGrid"] = value.(GENERATORtoGrid)
results_JSON["GridtoLoad"] = value.(GridtoLoad)

#results_JSON["year_one_to_grid_series_kw"] = value.(GridToBatt)
#results_JSON["year_one_to_load_series_kw"] = value.(dvElecFromStor)
#results_JSON["year_one_to_load_series_kw"] = value.(dvElecFromStor)
#
#results_JSON["LoadProfile"] = Dict()
#results_JSON["Financial"] = Dict()
#results_JSON["Storage"] = Dict()
#results_JSON["ElectricTariff"] = Dict()
#
#
#for (name, value) in results_JSON:
#    if name == "LoadProfile":
#        #load_model = LoadProfileModel.objects.get(run_uuid=meta['run_uuid'])
#        results_JSON[name]["year_one_electric_load_series_kw"] = LoadProfile[Symbol("1R"), :]
#        #results_JSON[name]["critical_load_series_kw"] = self.po.get_crit_load_profile()
#        results_JSON[name]["annual_calculated_kwh"] = AnnualElecLoad
#        #results_JSON[name]["resilience_check_flag"] = load_model.resilience_check_flag
#        #results_JSON[name]["sustain_hours"] = load_model.sustain_hours
#    elseif name == "Financial":
#        results_JSON[name]["lcc_us_dollars"] = ojv
#        #results_JSON[name]["lcc_bau_us_dollars"] = self.results_dict.get("lcc_bau")
#        #results_JSON[name]["npv_us_dollars"] = self.results_dict.get("npv")
#        results_JSON[name]["net_capital_costs_plus_om_us_dollars"] = value(TotalTechCapCosts + TotalStorageCapCosts + TotalOMCosts * r_tax_fraction_owner)
#        results_JSON[name]["net_capital_costs"] = value(TotalTechCapCosts + TotalStorageCapCosts)
#        #results_JSON[name]["microgrid_upgrade_cost_us_dollars"] = self.results_dict.get("net_capital_costs") * data['inputs']['Scenario']['Site']['Financial']['microgrid_upgrade_cost_pct']
#    elseif name == "PV":
#        #pv_model = PVModel.objects.get(run_uuid=meta['run_uuid'])
#        results_JSON[name]["size_kw"] = value(sum(dvSystemSize[t,s] for s in Seg, t in PVClass))
#        results_JSON[name]["average_yearly_energy_produced_kwh"] = self.results_dict.get("average_yearly_pv_energy_produced")
#        results_JSON[name]["average_yearly_energy_exported_kwh"] = self.results_dict.get("average_annual_energy_exported")
#        results_JSON[name]["year_one_energy_produced_kwh"] = self.results_dict.get("year_one_energy_produced")
#        results_JSON[name]["year_one_to_battery_series_kw"] = self.po.get_pv_to_batt()
#        results_JSON[name]["year_one_to_load_series_kw"] = self.po.get_pv_to_load()
#        results_JSON[name]["year_one_to_grid_series_kw"] = self.po.get_pv_to_grid()
#        results_JSON[name]["year_one_power_production_series_kw"] = self.compute_total_power(name)
#        #results_JSON[name]["existing_pv_om_cost_us_dollars"] = self.results_dict.get("pv_net_fixed_om_costs_bau")
#        results_JSON[name]["station_latitude"] = pv_model.station_latitude
#        results_JSON[name]["station_longitude"] = pv_model.station_longitude
#        results_JSON[name]["station_distance_km"] = pv_model.station_distance_km
#    elseif name == "Wind":
#        results_JSON[name]["size_kw"] = self.results_dict.get("wind_kw",0)
#        results_JSON[name]["average_yearly_energy_produced_kwh"] = value(AveragePVProd)
#        results_JSON[name]["average_yearly_energy_exported_kwh"] = self.results_dict.get("average_annual_energy_exported_wind")
#        results_JSON[name]["year_one_energy_produced_kwh"] = self.results_dict.get("year_one_wind_energy_produced")
#        results_JSON[name]["year_one_to_battery_series_kw"] = self.po.get_wind_to_batt()
#        results_JSON[name]["year_one_to_load_series_kw"] = self.po.get_wind_to_load()
#        results_JSON[name]["year_one_to_grid_series_kw"] = self.po.get_wind_to_grid()
#        results_JSON[name]["year_one_power_production_series_kw"] = self.compute_total_power(name)
#    elseif name == "Storage":
#        results_JSON[name]["size_kw"] = self.results_dict.get("batt_kw",0)
#        results_JSON[name]["size_kwh"] = self.results_dict.get("batt_kwh",0)
#        results_JSON[name]["year_one_to_load_series_kw"] = self.po.get_batt_to_load()
#        results_JSON[name]["year_one_to_grid_series_kw"] = self.po.get_batt_to_grid()
#        results_JSON[name]["year_one_soc_series_pct"] = self.po.get_soc(self.results_dict.get('batt_kwh'))
#    elseif name == "ElectricTariff":
#        results_JSON[name]["year_one_energy_cost_us_dollars"] = self.results_dict.get("year_one_energy_cost")
#        results_JSON[name]["year_one_demand_cost_us_dollars"] = self.results_dict.get("year_one_demand_cost")
#        results_JSON[name]["year_one_fixed_cost_us_dollars"] = self.results_dict.get("year_one_fixed_cost")
#        results_JSON[name]["year_one_min_charge_adder_us_dollars"] = self.results_dict.get("year_one_min_charge_adder")
#        #results_JSON[name]["year_one_energy_cost_bau_us_dollars"] = self.results_dict.get("year_one_energy_cost_bau")
#        results_JSON[name]["year_one_energy_cost_us_dollars"] = self.results_dict.get("year_one_energy_cost")
#        #results_JSON[name]["year_one_demand_cost_bau_us_dollars"] = self.results_dict.get("year_one_demand_cost_bau")
#        #results_JSON[name]["year_one_fixed_cost_bau_us_dollars"] = self.results_dict.get("year_one_fixed_cost_bau")
#        #results_JSON[name]["year_one_min_charge_adder_bau_us_dollars"] = self.results_dict.get("year_one_min_charge_adder_bau")
#        results_JSON[name]["total_energy_cost_us_dollars"] = self.results_dict.get("total_energy_cost")
#        results_JSON[name]["total_demand_cost_us_dollars"] = self.results_dict.get("total_demand_cost")
#        results_JSON[name]["total_fixed_cost_us_dollars"] = self.results_dict.get("total_fixed_cost")
#        results_JSON[name]["total_min_charge_adder_us_dollars"] = self.results_dict.get("total_min_charge_adder")
#        #results_JSON[name]["total_energy_cost_bau_us_dollars"] = self.results_dict.get("total_energy_cost_bau")
#        #results_JSON[name]["total_demand_cost_bau_us_dollars"] = self.results_dict.get("total_demand_cost_bau")
#        #results_JSON[name]["total_fixed_cost_bau_us_dollars"] = self.results_dict.get("total_fixed_cost_bau")
#        #results_JSON[name]["total_min_charge_adder_bau_us_dollars"] = self.results_dict.get("total_min_charge_adder_bau")
#        results_JSON[name]["year_one_bill_us_dollars"] = self.results_dict.get("year_one_bill")
#        #results_JSON[name]["year_one_bill_bau_us_dollars"] = self.results_dict.get("year_one_bill_bau")
#        results_JSON[name]["year_one_export_benefit_us_dollars"] = self.results_dict.get("year_one_export_benefit")
#        results_JSON[name]["total_export_benefit_us_dollars"] = self.results_dict.get("total_export_benefit")
#        results_JSON[name]["year_one_energy_cost_series_us_dollars_per_kwh"] = self.po.get_energy_cost()
#        results_JSON[name]["year_one_demand_cost_series_us_dollars_per_kw"] = self.po.get_demand_cost()
#        results_JSON[name]["year_one_to_load_series_kw"] = self.po.get_grid_to_load()
#        results_JSON[name]["year_one_to_battery_series_kw"] = self.po.get_grid_to_batt()
#        results_JSON[name]["year_one_energy_supplied_kwh"] = self.results_dict.get("year_one_utility_kwh")
#        #results_JSON[name]["year_one_energy_supplied_kwh_bau"] = self.results_dict.get("year_one_utility_kwh_bau")
#    elseif name == "Generator":
#        results_JSON[name]["size_kw"] = self.results_dict.get("generator_kw",0)
#        results_JSON[name]["fuel_used_gal"] = self.results_dict.get("fuel_used_gal")
#        #results_JSON[name]["fuel_used_gal_bau"] = self.results_dict.get("fuel_used_gal_bau")
#        results_JSON[name]["year_one_to_load_series_kw"] = self.po.get_gen_to_load()
#        results_JSON[name]["average_yearly_energy_produced_kwh"] = self.results_dict.get("average_yearly_gen_energy_produced")
#        results_JSON[name]["average_yearly_energy_exported_kwh"] = self.results_dict.get("average_annual_energy_exported_gen")
#        results_JSON[name]["year_one_energy_produced_kwh"] = self.results_dict.get("year_one_gen_energy_produced")
#        results_JSON[name]["year_one_to_battery_series_kw"] = self.po.get_gen_to_batt()
#        results_JSON[name]["year_one_to_load_series_kw"] = self.po.get_gen_to_load()
#        results_JSON[name]["year_one_to_grid_series_kw"] = self.po.get_gen_to_grid()
#        results_JSON[name]["year_one_power_production_series_kw"] = self.compute_total_power(name)
#        #results_JSON[name]["existing_gen_fixed_om_cost_us_dollars_bau"] = self.results_dict.get("gen_net_fixed_om_costs_bau")
#        #results_JSON[name]["existing_gen_variable_om_cost_us_dollars_bau"] = self.results_dict.get("gen_net_variable_om_costs_bau")
#        results_JSON[name]["gen_variable_om_cost_us_dollars"] = self.results_dict.get("gen_net_variable_om_costs")
