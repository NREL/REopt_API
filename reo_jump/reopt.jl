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
init_data["TechClass"] = Symbol.(init_data["TechClass"])
init_data["Tech"] = Symbol.(init_data["Tech"])
init_data["load"] = Symbol.(init_data["load"])
init_data["NMILRegime"] = Symbol.(init_data["NMILRegime"])


TimeStepCount = init_data["TimeStepCount"]
TechCount = length(init_data["Tech"])
LoadCount = length(init_data["load"])
FuelBinCount = init_data["FuelBinCount"]

# reshaping all the matrices
# Juila being column-first language reshapes the 1-D into matrices
# in transposed way, thus rearranging the dimensions along with reshaping
ProdFactor = NamedArray(permutedims(reshape(init_data["ProdFactor"],
                            (timestepcount, loadcount, techcount)), [3,2,1]),
                            (init_data["Tech"], init_data["load"],
                            collect(1:timestepcount)))
# indexing: prodfactor[:PV, Symbol("1X"), 569:571]

TechToLoadMatrix = NamedArray(permutedims(reshape(
                                init_data["TechToLoadMatrix"],
                                (loadcount,techcount)), [2,1]), (init_data["Tech"],
                                init_data["load"]))
#indexing techtoloadmatrix[:PV, Symbol("1R")]

FuelRate = NamedArray(permutedims(reshape(init_data["FuelRate"],
          (timestepcount, FuelBinCount, techcount)), [3,2,1]),
          (init_data["Tech"], collect(1:FuelBinCount),
          collect(1:timestepcount)))

FuelAvail = NamedArray(permutedims(reshape(init_data["FuelAvail"],
        (collect(1:FuelBinCount), init_data["Tech"])), [2,1]),
        (init_data["Tech"], collect(1:FuelBinCount)))


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
