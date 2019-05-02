#=
reopt:
- Julia version: 1.0.3
- Author: Sakshi Mishra
- Date: 2019-04-21
=#

using Revise
include("utils.jl")
include("reo_structs.jl")

init_data = importData("./wtch_data.json")
init_data["TechClass"] = Symbol.(init_data["TechClass"])
init_data["Tech"] = Symbol.(init_data["Tech"])
init_data["load"] = Symbol.(init_data["load"])
init_data["NMILRegime"] = Symbol.(init_data["NMILRegime"])
