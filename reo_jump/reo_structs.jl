#=
reo_structs:
- Julia version: 1.0.3
- Author: Sakshi Mishra
- Date: 2019-04-12
=#

import PowerSystems
using TimeSeries
# fieldnames(PowerSystem)

#struct TechReo <: PowerSystems.TechnicalParams
struct TechReo
   activepowerlimits::NamedTuple{(:min, :max),Tuple{Float64,Float64}}
   installedcapacity::Union{Float64,Nothing} # [kW]
   reactivepowerlimits::Union{NamedTuple{(:min, :max),Tuple{Float64,Float64}},Nothing} # [kVar]
   powerfactor::Union{Float64,Nothing} # [-1. -1]
end

#outer constructor for TechReo
function TechReo(activepowerlimits=(min=25.0, max=200.0),
    installedcapacity=nothing, reactivepowerlimits=nothing,
    powerfactor=nothing)
    TechReo(activepowerlimits, installedcapacity, reactivepowerlimits,
    powerfactor)
end

struct RenewableGenReo <: PowerSystems.RenewableGen
   name::String
   techclass::String
   techisgrid::Int8
   available::Int8
   bus::PowerSystems.Bus
   productionfactor::TimeSeries.TimeArray #can be named scalingfactor
   tech::Union{TechReo, Nothing}
   maxsizeforprodincent::Float64
   techtoloadarray::Array{Int8,1}
   techtonmilmapping::Array{Int8,1}


    function RenewableGenReo(name= "init", techclass= "init",
        techisgrid= Int8(0), available=Int8(0),
        bus=PowerSystems.Bus(),
        productionfactor=TimeSeries.TimeArray(Dates.today(), ones(1)),
        #activepowerlimits::NamedTuple{(:min,:max),Tuple{Float64,Float64}},
        tech=TechReo(),
        maxsizeforprodincent=0.0, techtoloadarray=[0], techtonmilmapping=[0])

        tech = TechReo()
        new(name, techclass, techisgrid, available, bus, productionfactor,
        tech, maxsizeforprodincent, techtoloadarray, techtonmilmapping)
   end
end


struct ThermalGenReo <: PowerSystems.ThermalGen
    name::String
    techclass::String
    techisgrid::Int8
    available::Int8
    bus::PowerSystems.Bus
    productionfactor::TimeSeries.TimeArray #can be named scalingfactor
    maxsize::Float64
    minsize::Float64
    techtoloadarray::Array{Int8,1}
    techtonmilmapping::Array{Int8,1}
    turbinederate::Float32
    fuelburnratem::Array{Float32,1}
    fuelburnrateb::Array{Float32,1}
    fuelavail::Array{Float32,1}
    fuelrate::Array{Float32,1}
    minturndown::Float32

    function ThermalGenReo(name, techclass, techisgrid, available, bus,
         productionfactor, maxsize, minsize,techtoloadarray, techtonmilmapping,
         turbinederate, fuelburnratem,fuelburnrateb, fuelavail,fuelrate,
         minturndown)
        new(name, techclass, techisgrid, available, bus, productionfactor,
        maxsize, minsize, techtoloadarray, techtonmilmapping, turbinederate,
        fuelburnratem, fuelburnrateb, fuelavail, fuelrate, minturndown)
    end
end
