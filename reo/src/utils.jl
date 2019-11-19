import Base.length
import Base.reshape
import AxisArrays.AxisArray
import JuMP.value
using AxisArrays
using JuMP

function emptySetException(sets, values, floatbool=false)
    try
        return parameter(sets, values)
    catch
        if floatbool
            return Float64[]
        else
            return Int64[]
        end
    end
end

#TODO Get rid of union types
struct Parameter
     Tech::Array{String,1}
     Load::Array{String,1}
     TechClass::Array{String,1}
     TechIsGrid::AxisArray{Int64,1,Array{Int64,1},Tuple{Axis{:row,Array{String,1}}}}
     TechToLoadMatrix::AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}
     TurbineDerate::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}
     TechToTechClassMatrix::AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}
     NMILRegime::Array{String,1}
     r_tax_owner::Float64
     r_tax_offtaker::Float64
     pwf_om::Float64
     pwf_e::Float64
     pwf_prod_incent::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}
     LevelizationFactor::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}
     LevelizationFactorProdIncent::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}
     StorageCostPerKW::Float64
     StorageCostPerKWH::Float64
     OMperUnitSize::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}
     CapCostSlope::Union{AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}},AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}}
     CapCostYInt::Union{AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}},AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}}
     CapCostX::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}
     ProdIncentRate::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}
     MaxProdIncent::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}
     MaxSizeForProdIncent::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}
     two_party_factor::Float64
     analysis_years::Int64
     AnnualElecLoad::Float64
     LoadProfile::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}
     ProdFactor::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}},Axis{:page,UnitRange{Int64}}}}
     StorageMinChargePcent::Float64
     EtaStorIn::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}
     EtaStorOut::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}
     InitSOC::Float64
     MaxSize::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}
     MinStorageSizeKW::Float64
     MaxStorageSizeKW::Float64
     MinStorageSizeKWH::Float64
     MaxStorageSizeKWH::Float64
     TechClassMinSize::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}
     MinTurndown::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}
     FuelRate::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}},Axis{:page,UnitRange{Int64}}}}
     FuelAvail::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}
     FixedMonthlyCharge::Float64
     AnnualMinCharge::Float64
     MonthlyMinCharge::Float64
     ExportRates::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}},Axis{:page,UnitRange{Int64}}}}
     TimeStepRatchetsMonth::AxisArray{Array{Int64,1},1,Array{Array{Int64,1},1},Tuple{Axis{:row,UnitRange{Int64}}}}
     DemandRatesMonth::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,UnitRange{Int64}},Axis{:col,UnitRange{Int64}}}}
     DemandLookbackPercent::Float64
     MaxDemandInTier::Array{Float64,1}
     MaxDemandMonthsInTier::Array{Float64,1}
     MaxUsageInTier::Array{Float64,1}
     FuelBurnRateM::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}},Axis{:page,UnitRange{Int64}}}}
     FuelBurnRateB::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}},Axis{:page,UnitRange{Int64}}}}
     NMILLimits::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}
     TechToNMILMapping::AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}
     DemandRates::Union{Array{Float64,1},AxisArray{Any,2,Array{Any,2},Tuple{Axis{:row,UnitRange{Int64}},Axis{:col,UnitRange{Int64}}}},AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,UnitRange{Int64}},Axis{:col,UnitRange{Int64}}}}}
     TimeStepRatchets::Union{Array{Int64,1},AxisArray{Array{Any,1},1,Array{Array{Any,1},1},Tuple{Axis{:row,UnitRange{Int64}}}},AxisArray{Array{Int64,1},1,Array{Array{Int64,1},1},Tuple{Axis{:row,UnitRange{Int64}}}}}
     DemandLookbackMonths::Array{Any,1}
     CapCostSegCount::Int64
     FuelBinCount::Int64
     DemandBinCount ::Int64
     DemandMonthsBinCount::Int64
     TimeStepCount::Int64
     Seg::UnitRange{Int64}
     Points::UnitRange{Int64}
     Month::UnitRange{Int64}
     Ratchets::UnitRange{Int64}
     FuelBin::UnitRange{Int64}
     DemandBin::UnitRange{Int64}
     DemandMonthsBin::UnitRange{Int64}
     TimeStep::UnitRange{Int64}
     TimeStepBat::UnitRange{Int64}
     TimeStepScaling::Float64
     OMcostPerUnitProd::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}
end


function build_param(args...;
          Tech,
          Load,
          TechClass,
          TechIsGrid,
          TechToLoadMatrix,
          TurbineDerate,
          TechToTechClassMatrix,
          NMILRegime,
          r_tax_owner,
          r_tax_offtaker,
          pwf_om,
          pwf_e,
          pwf_prod_incent,
          LevelizationFactor,
          LevelizationFactorProdIncent,
          StorageCostPerKW,
          StorageCostPerKWH,
          OMperUnitSize,
          CapCostSlope,
          CapCostYInt,
          CapCostX,
          ProdIncentRate,
          MaxProdIncent,
          MaxSizeForProdIncent,
          two_party_factor,
          analysis_years,
          AnnualElecLoad,
          LoadProfile,
          ProdFactor,
          StorageMinChargePcent,
          EtaStorIn,
          EtaStorOut,
          InitSOC,
          MaxSize,
          MinStorageSizeKW,
          MaxStorageSizeKW,
          MinStorageSizeKWH,
          MaxStorageSizeKWH,
          TechClassMinSize,
          MinTurndown,
          FuelRate,
          FuelAvail,
          FixedMonthlyCharge,
          AnnualMinCharge,
          MonthlyMinCharge,
          ExportRates,
          TimeStepRatchetsMonth,
          DemandRatesMonth,
          DemandLookbackPercent,
          MaxDemandInTier,
          MaxDemandMonthsInTier,
          MaxUsageInTier,
          FuelBurnRateM,
          FuelBurnRateB,
          NMILLimits,
          TechToNMILMapping,
          DemandRates,
          TimeStepRatchets,
          DemandLookbackMonths,
          CapCostSegCount,
          FuelBinCount,
          DemandBinCount ,
          DemandMonthsBinCount,
          TimeStepCount,
          NumRatchets,
          TimeStepScaling,
          OMcostPerUnitProd,
          kwargs...
    )


    Seg = 1:CapCostSegCount
    Points = 0:CapCostSegCount
    Month = 1:12
    Ratchets = 1:NumRatchets
    FuelBin = 1:FuelBinCount
    DemandBin = 1:DemandBinCount
    DemandMonthsBin = 1:DemandMonthsBinCount
    TimeStep=1:TimeStepCount
    TimeStepBat=0:TimeStepCount

    TechIsGrid = parameter(Tech, TechIsGrid)
    TechToLoadMatrix = parameter((Tech, Load), TechToLoadMatrix)
    TurbineDerate = parameter(Tech, TurbineDerate)
    TechToTechClassMatrix = parameter((Tech, TechClass), TechToTechClassMatrix)
    pwf_prod_incent = parameter(Tech, pwf_prod_incent)
    LevelizationFactor = parameter(Tech, LevelizationFactor)
    LevelizationFactorProdIncent = parameter(Tech, LevelizationFactorProdIncent)
    OMperUnitSize = parameter(Tech, OMperUnitSize)
    CapCostSlope = parameter((Tech, Seg), CapCostSlope)
    CapCostYInt = parameter((Tech, Seg), CapCostYInt)
    CapCostX = parameter((Tech, Points), CapCostX)
    ProdIncentRate = parameter((Tech, Load), ProdIncentRate)
    MaxProdIncent = parameter(Tech, MaxProdIncent)
    MaxSizeForProdIncent = parameter(Tech, MaxSizeForProdIncent)
    LoadProfile = parameter((Load, TimeStep), LoadProfile)
    ProdFactor = parameter((Tech, Load, TimeStep), ProdFactor)
    EtaStorIn = parameter((Tech, Load), EtaStorIn)
    EtaStorOut = parameter(Load, EtaStorOut)
    MaxSize = parameter(Tech, MaxSize)
    TechClassMinSize = parameter(TechClass, TechClassMinSize)
    MinTurndown = parameter(Tech, MinTurndown)
    TimeStepRatchets = emptySetException(Ratchets, TimeStepRatchets)
    DemandRates = emptySetException((Ratchets, DemandBin), DemandRates, true)
    FuelRate = parameter((Tech, FuelBin, TimeStep), FuelRate)
    FuelAvail = parameter((Tech, FuelBin), FuelAvail)
    ExportRates = parameter((Tech, Load, TimeStep), ExportRates)
    TimeStepRatchetsMonth = parameter(Month, TimeStepRatchetsMonth)
    DemandRatesMonth = parameter((Month, DemandMonthsBin), DemandRatesMonth)
    MaxDemandInTier = parameter(DemandBin, MaxDemandInTier)
    MaxDemandMonthsInTier = parameter(DemandMonthsBin, MaxDemandMonthsInTier)
    MaxUsageInTier = parameter(FuelBin, MaxUsageInTier)
    FuelBurnRateM = parameter((Tech, Load, FuelBin), FuelBurnRateM)
    FuelBurnRateB = parameter((Tech, Load, FuelBin), FuelBurnRateB)
    NMILLimits = parameter(NMILRegime, NMILLimits)
    TechToNMILMapping = parameter((Tech, NMILRegime), TechToNMILMapping)
    OMcostPerUnitProd = parameter(Tech, OMcostPerUnitProd)


    param = Parameter(Tech, 
                      Load, 
                      TechClass,
                      TechIsGrid,
                      TechToLoadMatrix,
                      TurbineDerate,
                      TechToTechClassMatrix,
                      NMILRegime,
                      r_tax_owner,
                      r_tax_offtaker,
                      pwf_om,
                      pwf_e,
                      pwf_prod_incent,
                      LevelizationFactor,
                      LevelizationFactorProdIncent,
                      StorageCostPerKW,
                      StorageCostPerKWH,
                      OMperUnitSize,
                      CapCostSlope,
                      CapCostYInt,
                      CapCostX,
                      ProdIncentRate,
                      MaxProdIncent,
                      MaxSizeForProdIncent,
                      two_party_factor,
                      analysis_years,
                      AnnualElecLoad,
                      LoadProfile,
                      ProdFactor,
                      StorageMinChargePcent,
                      EtaStorIn,
                      EtaStorOut,
                      InitSOC,
                      MaxSize,
                      MinStorageSizeKW,
                      MaxStorageSizeKW,
                      MinStorageSizeKWH,
                      MaxStorageSizeKWH,
                      TechClassMinSize,
                      MinTurndown,
                      FuelRate,
                      FuelAvail,
                      FixedMonthlyCharge,
                      AnnualMinCharge,
                      MonthlyMinCharge,
                      ExportRates,
                      TimeStepRatchetsMonth,
                      DemandRatesMonth,
                      DemandLookbackPercent,
                      MaxDemandInTier,
                      MaxDemandMonthsInTier,
                      MaxUsageInTier,
                      FuelBurnRateM,
                      FuelBurnRateB,
                      NMILLimits,
                      TechToNMILMapping,
                      DemandRates,
                      TimeStepRatchets,
                      DemandLookbackMonths,
                      CapCostSegCount,
                      FuelBinCount,
                      DemandBinCount ,
                      DemandMonthsBinCount,
                      TimeStepCount,
                      Seg,
                      Points,
                      Month,
                      Ratchets,
                      FuelBin,
                      DemandBin,
                      DemandMonthsBin,
                      TimeStep,
                      TimeStepBat,
                      TimeStepScaling,
                      OMcostPerUnitProd)

    return param

end

# Code for paramter() function
function paramDataFormatter(setTup::Tuple, data::AbstractArray)
    reverseTupleAxis = Tuple([length(set) for set in setTup][end:-1:1])
    shapedData = reshape(data, reverseTupleAxis)
    reverseDataAxis = [length(setTup)+1 - n for n in 1:length(setTup)]
    shapedDataT = permutedims(shapedData, reverseDataAxis)
    return AxisArray(shapedDataT, setTup)
end

function parameter(setTup::Tuple, data::AbstractArray)
    #data = retype(nondata)
    try
        formattedParam = paramDataFormatter(setTup, data)
        return formattedParam
    catch
        correctLength = prod([length(x) for x in setTup])
        if length(data) < correctLength
            let x = 1
                for set in setTup
                    x = x * length(set)
                end
                numZeros = x - length(data)
                for zero in 1:numZeros
                    append!(data, 0)
                end
                formattedParam = paramDataFormatter(setTup, data)
                return formattedParam
            end
        else
            data = data[1:correctLength]
            formattedParam = paramDataFormatter(setTup, data)
            return formattedParam
        end
    end
end

function parameter(set::UnitRange{Int64}, data::Float64)
    return [data]
end

function parameter(setTup::Tuple{Array{Symbol,1}, UnitRange{Int64}}, data::Number)
    newTup = ([setTup[1][1], :FAKE], 1:2)
    return AxisArray(fill(data, 2, 2), newTup)
end

function parameter(set::Symbol, data::Int64)
    return AxisArray([data], set)
end

function parameter(set, data)
    shapedData = reshape(data, length(set))
    return AxisArray(shapedData, set)
end


# Additional dispatches to make things easier
function length(::Symbol)
    return 1
end

function reshape(data::Number, axes::Int64)
    return data
end

function AxisArray(data::Number, index::Array{Symbol, 1})
    return AxisArray([float(data)], index)
end

function JuMP.value(::Val{false})
    return 0.0
end

function JuMP.value(x::Float64)
    return x
end
