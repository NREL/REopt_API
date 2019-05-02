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
