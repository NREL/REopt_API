#=
reopt:
- Julia version: 1.0.3
- Author: Sakshi Mishra
- Date: 2019-04-21
=#

using Revise
using NamedArrays
include("utils.jl")
include("reo_structs.jl")

init_data = importData("./wtch_data.json")
TechClassNames = Symbol.(init_data["TechClass"])
TechNames = Symbol.(init_data["Tech"])
LoadNames = Symbol.(init_data["load"])
NMILRegimeNames = Symbol.(init_data["NMILRegime"])


BattLevelCount = 1 #resolve this
CapCostSegCount = init_data["CapCostSegCount"]
DemandBinCount = init_data["DemandBinCount"]
DemandMonthsBinCount = init_data["DemandMonthsBinCount"]
FuelBinCount = init_data["FuelBinCount"]
LoadCount = length(LoadNames)
NumRatchets = init_data["NumRatchets"]
TechCount = length(TechNames)
TimeStepCount = init_data["TimeStepCount"]
TimeStepScaling = init_data["TimeStepScaling"]


Seg = collect(1:CapCostSegCount)
Points = collect(0:CapCostSegCount)
Month = collect(1:12)
Ratchets = collect(1:NumRatchets)
TimeSteps = collect(1:TimeStepCount)
FuelBin = collect(1:FuelBinCount)
DemandBin =  collect(1:DemandBinCount)
DemandMonthsBin = collect(1:DemandMonthsBinCount)
BattLevel = collect(1:BattLevelCount)



# reshaping parameters (vectors) into multi-D arrays
# Juila being column-first language reshapes the 1-D vector into multi-D
# arrays in a transposed way, thus rearranging the dimensions as well
ProdFactor = NamedArray(permutedims(reshape(init_data["ProdFactor"],
                            (TimeStepCount, LoadCount, TechCount)), [3,2,1]),
                            (TechNames, LoadNames, TimeSteps))
# How to index: ProdFactor[:PV, Symbol("1X"), 569:571]

TechToLoadMatrix = NamedArray(permutedims(reshape(
                                init_data["TechToLoadMatrix"],
                                (LoadCount,TechCount)), [2,1]), (TechNames,
                                LoadNames))
# How to index: TechToLoadMatrix[:PV, Symbol("1R")]

FuelRate = NamedArray(permutedims(reshape(init_data["FuelRate"],
          (TimeStepCount, FuelBinCount, TechCount)), [3,2,1]),
          (TechNames, FuelBin, TimeSteps))
# How to index: FuelRate[:UTIL1, 1, 456:459]

FuelAvail = NamedArray(permutedims(reshape(init_data["FuelAvail"],
        (FuelBinCount, TechCount)), [2,1]),
        (TechNames, FuelBin))
# How to index: FuelAvail[:WINDNM, 1]


FuelBurnRateB = NamedArray(permutedims(reshape(init_data["FuelBurnRateB"],
(FuelBinCount, LoadCount, TechCount)), [3,2,1]),
(TechNames, LoadNames, FuelBin))
# How to index: FuelBurnRateB[:WIND, Symbol("1W"), 1]

FuelBurnRateM = NamedArray(permutedims(reshape(init_data["FuelBurnRateM"],
(FuelBinCount, LoadCount, TechCount)), [3,2,1]),
(TechNames, LoadNames, FuelBin))
# How to index: FuelBurnRateM[:WINDNM, Symbol("1X"), 1]

# the commaa after TechNames is necessary
LevelizationFactor = NamedArray(init_data["LevelizationFactor"], (TechNames,))
# How to index: LevelizationFactor[:WIND]

LevelizationFactorProdIncent = NamedArray(init_data["LevelizationFactorProdIncent"],
                                        (TechNames,))

LoadProfile = NamedArray(permutedims(reshape(init_data["LoadProfile"],
              (TimeStepCount, LoadCount)), [2,1]),
              (LoadNames, TimeSteps))
# How to index: LoadProfile[Symbol("1R"), 5683:5690]

MaxDemandInTier = NamedArray(init_data["MaxDemandInTier"],
                 (DemandBin,))

MaxProdIncent = NamedArray(init_data["MaxProdIncent"], (TechNames,))

MaxSize = NamedArray(init_data["MaxSize"], (TechNames,))

MaxSizeForProdIncent = NamedArray(init_data["MaxSizeForProdIncent"],
                        (TechNames,))

MaxUsageInTier = NamedArray(init_data["MaxUsageInTier"], (FuelBin,))

MinTurnDown = NamedArray(init_data["MinTurndown"], (TechNames,))










"""
for tch in init_data["Tech"]
    if String(tch) in("PV","PVNM","WIND","WINDNM")
        # call the function for creating RenewableGenReo Object
    elseif String(tch) == "GENERATOR"
        # call the function which uses ThermalGenReo
    else
        # call the function

# function to create RenewableGen objection
function createRenewableGenReo()
"""
