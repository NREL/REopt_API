#=
reo_structs:
- Julia version: 1.0.3
- Author: Sakshi Mishra
- Date: 2019-04-12
=#

import PowerSystems
using TimeSeries
# fieldnames(PowerSystem)


#### GENERATION MODELING
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


#### STORAGE MODELING
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

### LOAD MODELING
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


### Following concrete types are NOT subtyped from PowerSystems.jl
### Reo specific abstract types is defined here:
abstract type Reo end

struct TechClassReo <: Reo
    techclassminsize::Array{Float64, 1}
    techtotechclassmatrix::Array{Int8, 1}

    function TechClassReo(techclassminsize=[0],
        techtotechclassmatrix=Int8.([0,1]))
        new(techclassminsize, techtotechclassmatrix)
    end
end


struct GeneralEconReo <: Reo
    analysisyears::Float64
    maxprodincentive::Array{Float64, 1}
    levelizationfactor::Array{Float64, 1}
    levelizationfactor_prodincent::Array{Float64, 1}
    prodincentrate::Array{Float64,1}
    pwf_e::Float64
    pwf_om::Float64
    twopartyfactor::Float64
    pwf_prod_incent::Array{Float64,1}
    r_tax_offtaker::Float64
    r_tax_owner::Float64
    nmil_regime::Array{String, 1}

    function GeneralEconReo(analysis_years=20, maxprodincentive=[0.0,0.2],
        levelizationfactor=[0.0,0.1],levelizationfactor_prodincent=[0.1,0.3],
        prodincentrate=[1.0,20.6], pwf_e=0.9, pwf_om=12.3, twopartyfactor=1.2,
        pwf_prod_incent=[1,10.2], r_tax_offtaker=0.3, r_tax_owner=2.3,
        nmil_regime=["a","b","c"])

        new(analysis_years, maxprodincentive, levelizationfactor,
        levelizationfactor_prodincent, prodincentrate, pwf_e, pwf_om,
        twopartyfactor, pwf_prod_incent, r_tax_offtaker, r_tax_owner,
        nmil_regime)
    end
end

struct UtilTariffReo <: Reo
    fixedmonthlycharge::Float64
    annualmincharge::Float64
    monthlymincharge::Float64
    demandlookbackpercent::Float32
    demandlookbackmonths::Array{Int32, 1}
    nmil_limits::Array{Float64, 1}
    exportrates::TimeSeries.TimeArray
    timestep_ratchets::Array{Float64, 1}
    timestep_ratchetsmonths::Array{Array{Int64,1}}

    function UtilTariffReo(fixedmonthlycharge=0.0, annualmincharge=0.0,
        monthlymincharge=0.0, demandlookbackpercent=0.5,
        demandlookbackmonths=[1,2,3,4,5,6,7,8,9,10,11,12],
        nmil_limits=[1000,1500,100000],
        exportrates=TimeSeries.TimeArray(Dates.today(), ones(1)),
        timestep_ratchets=[1,2,3],
        timestep_ratchetsmonths=[[2,8,112],[596,12,36],[74,86,12],[38,45,1296]])

        new(fixedmonthlycharge, annualmincharge, monthlymincharge,
        demandlookbackpercent, demandlookbackmonths, nmil_limits, exportrates,
        timestep_ratchets, timestep_ratchetsmonths)
    end
end
