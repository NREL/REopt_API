#=
reo_structs:
- Julia version: 1.0.3
- Author: Sakshi Mishra
- Date: 2019-04-21
=#

using Revise
include("utils.jl")
include("reo_structs.jl")

jsonToVariable("./all_data_new.json")


pv = RenewableGenReo("PV", "PV", Int8(0), Int8(1), PowerSystems.Bus(),
TimeSeries.TimeArray(Dates.today(), ones(1)),
TechReo((min=25.0, max=200.0),nothing,nothing,nothing),
250.0, Int8.([1,1,1,1]), Int8.([0,1,0]))


util =ThermalGenReo("UTIL", "UTIL", false, true, PowerSystems.Bus(),
TimeSeries.TimeArray(Dates.today(), ones(1)), 999,55,[1,1,1,1], [0,1,0],
0.96,[1,0.6,1.1,0.98],[1,0.6,1.1,0.98], [100000],[1,2,3],0)

println(pv)
