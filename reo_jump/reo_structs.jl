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

# outer constructor
function TechReo(activepowerlimits=(min=25.0, max=200.0),
    installedcapacity=nothing, reactivepowerlimits=nothing,
    powerfactor=nothing)
    TechReo(activepowerlimits, installedcapacity, reactivepowerlimits,
    powerfactor)
end

#struct EconGenReo <: PowerSystems.TechnicalParams
struct EconGenReo
    capcostslope::Array{Float64,1}
    capcostx::Array{Float64, 1}
    capcostyint::Array{Float64,1}
    variablecost::Union{Function,Array{Tuple{Float64,Float64}}} #[$/kWh]
    fixedcost::Union{Float64, Nothing} #[$/h]
end

#outer constructor
function EconGenReo(capcostslope=[0.0], capcostx=[0.0], capcostyint=[0.0],
    variablecost= [(0.0,0.1)], fixedcost=0.0)
    EconGenReo(capcostslope, capcostx, capcostyint,variablecost, fixedcost)
end

struct RenewableGenReo <: PowerSystems.RenewableGen
   name::String
   techclass::String
   techisgrid::Int8
   available::Int8
   bus::PowerSystems.Bus
   productionfactor::TimeSeries.TimeArray #can be named scalingfactor
   maxsizeforprodincent::Float64
   techtoloadarray::Array{Int8,1}
   techtonmilmapping::Array{Int8,1}
   tech::Union{TechReo, Nothing}
   econ::Union{EconGenReo, Nothing}


   function RenewableGenReo(name= "init", techclass= "init",
        techisgrid= Int8(0), available=Int8(0),
        bus=PowerSystems.Bus(),
        productionfactor=TimeSeries.TimeArray(Dates.today(), ones(1)),
        maxsizeforprodincent=0.0, techtoloadarray=Int8.([0]),
        techtonmilmapping=Int8.([0]), tech=TechReo(), econ=EconGenReo())

        tech = TechReo()
        econ = EconGenReo()
        new(name, techclass, techisgrid, available, bus, productionfactor,
        maxsizeforprodincent, techtoloadarray, techtonmilmapping, tech, econ)
   end
end


struct ThermalGenReo <: PowerSystems.ThermalGen
    name::String
    techclass::String
    techisgrid::Int8
    available::Int8
    bus::PowerSystems.Bus
    productionfactor::TimeSeries.TimeArray #can be named scalingfactor
    techtoloadarray::Array{Int8,1}
    techtonmilmapping::Array{Int8,1}
    turbinederate::Float32
    fuelburnratem::Array{Float32,1}
    fuelburnrateb::Array{Float32,1}
    fuelavail::Array{Float32,1}
    fuelrate::Array{Float32,1}
    minturndown::Float32
    tech::Union{TechReo, Nothing}
    econ::Union{EconGenReo, Nothing}


    function ThermalGenReo(name="init", techclass="init", techisgrid=Int8(0),
        available=Int8(0), bus=PowerSystems.Bus(),
         productionfactor=TimeSeries.TimeArray(Dates.today(), ones(1)),
         techtoloadarray=Int8.([0,0]), techtonmilmapping=Int8.([0,0]),
         turbinederate=Float32(0), fuelburnratem=Float32.([0,0]),
         fuelburnrateb=Float32.([0,0]), fuelavail=Float32.([0,0]),
         fuelrate=Float32.([0,0]), minturndown=Float32(0.0),tech=TechReo(),
         econ=EconGenReo())

        tech=TechReo()
        econ=EconGenReo()
        new(name, techclass, techisgrid, available, bus, productionfactor,
        techtoloadarray, techtonmilmapping, turbinederate, fuelburnratem,
        fuelburnrateb, fuelavail, fuelrate, minturndown, tech, econ)
    end
end


struct EconBattReo
    storagecostperkw::Float64
    storagecostperkwh::Float64
end

function EconBattReo(storagecostperkw=0.0, storagecostperkwh=0.0)
    EconBattReo(storagecostperkw, storagecostperkwh)
end


struct GenericBatteryReo <: PowerSystems.Storage
    name::String
    available::Int8
    bus::PowerSystems.Bus
    #MinStorageSizeKWh and MaxStorageSizekWh in original Reo is energycapacity here
    energycapacity::NamedTuple{(:min, :max), Tuple{Float64, Float64}}
    #MinStorageSizeKW and MaxStorageSizekW in original Reo is powercapacity here
    powercapacity::NamedTuple{(:min, :max), Tuple{Float64, Float64}}
    initsoc::Float16
    storageminchargepcent::Float32
    battlevelcoef::Float32
    etastorout::Array{Float16,1}
    etastorin::Array{Float16,1}
    econ::Union{EconBattReo, Nothing}

    function GenericBatteryReo(name="init", available=Int8(0),
        bus=PowerSystems.Bus(), energycapacity=(min=0.0, max=0.9),
        powercapacity=(min=0.0, max=0.9), initsoc=0.1,
        storageminchargepcent=0.2, battlevelcoef=0.2,
        etastorout=Float16.([0.1,0.2]), etastorin=Float16.([0.0,0.1]),
        econ=EconBattReo())

        econ = EconBattReo()
        new(name, available, bus,energycapacity, powercapacity, initsoc,
        storageminchargepcent, battlevelcoef, etastorout, etastorin, econ)
    end
end


struct StaticLoadReo <: PowerSystems.ElectricLoad
    name::Union{String, Nothing}
    available::Union{Int8, Nothing}
    bus::PowerSystems.Bus
    activepowerloadseries::TimeSeries.TimeArray #originally named as LoadProfile
    annualelecload::Float64
    reactivepowerloadseries::Union{TimeSeries.TimeArray, Nothing}
end


#multiple dispatch
function StaticLoadReoPF(name::Union{String, Nothing},
    available::Union{Int8, Nothing}, bus::PowerSystems.Bus,
    activepowerloadseries::TimeSeries.TimeArray, annualelecload::Float64,
    power_factor::Float64)
    reactivepowerloadseries = activepowerloadseries.*sin(acos(power_factor))
    return PowerLoad(name, available, bus, activepowerloadseries,
    annualelecload, reactivepowerloadseries)
end

#outer constructor
function StaticLoadReo(name="init",
    available=Int8(0), bus=PowerSystems.Bus(),
    activepowerloadseries=TimeSeries.TimeArray(Dates.today(), ones(1)),
    annualelecload=0.0,
    reactivepowerloadseries=nothing)
    return StaticLoadReo(name, available, bus, activepowerloadseries,
    annualelecload, reactivepowerloadseries)
end

#outer constructor of the multiple dispatched struct
function StaticLoadReoPF(name="init",
    available=Int8(0), bus=PowerSystems.Bus(),
    activepowerloadseries=TimeSeries.TimeArray(Dates.today(), ones(1)),
    annualelecload=0.0,
    power_factor=1.0)
    return StaticLoadReo(name, available, bus, activepowerloadseries,
    annualelecload, reactivepowerloadseries)
end
