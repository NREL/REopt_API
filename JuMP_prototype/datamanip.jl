using AxisArrays
using FileIO
using JLD2


function UseAxisArrays(uuid = "eda919d6-1481-4bf9-a531-a1b3397c8c67")
    include("utils.jl")

    dataPath = "data/Run$uuid"
    jldPath = "data/julia_data_files/" * uuid * ".jld"

    @load(jldPath,
          Tech,
          Load,
          TechClass,
          TechIsGrid,
          TechToLoadMatrix,
          TechClass,
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
          BattLevelCoef,
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
          TimeStepRatchets,
          DemandRates,
          DemandLookbackMonths)

    #TimeStepRatchets = fix_TimeStepRatchets(jldPath)
    #DemandRates = fix_DemandRates(jldPath)
    #DemandLookbackMonths = fix_DemandLookbackMonths(jldPath)

    BattLevelCount = 1
    readCmd(dataPath * "/Inputs/cmd.log")


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

    TechIsGrid = parameter(Tech, TechIsGrid)
    TechToLoadMatrix = parameter((Tech, Load), TechToLoadMatrix)
    TurbineDerate = parameter(Tech, TurbineDerate)
    TechToTechClassMatrix = parameter((Tech, TechClass), TechToTechClassMatrix)
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
    LoadProfile = parameter((Load, TimeStep), LoadProfile)
    ProdFactor = parameter((Tech, Load, TimeStep), ProdFactor)
    EtaStorIn = parameter((Tech, Load), EtaStorIn)
    EtaStorOut = parameter(Load, EtaStorOut)
    BattLevelCoef = parameter((BattLevel, 1:2), BattLevelCoef)
    MaxSize = parameter(Tech, MaxSize)
    TechClassMinSize = parameter(TechClass, TechClassMinSize)
    MinTurndown = parameter(Tech, MinTurndown)

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


    @save("data/julia_data_files/AA_" * uuid * ".jld",
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
          BattLevelCoef,
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
          BattLevelCount,
          TimeStepCount,
          Seg,
          Points,
          Month,
          Ratchets,
          FuelBin,
          DemandBin,
          DemandMonthsBin,
          BattLevel,
          TimeStep,
          TimeStepBat,
          TimeStepScaling)

end


struct Parameter
    Tech ::Array{Symbol,1}
    Load ::Array{Symbol,1}
    TechClass::Array{Symbol,1}
    TechIsGrid::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{Symbol,1}}}}
    TechToLoadMatrix::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,Array{Symbol,1}}}}
    TurbineDerate::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{Symbol,1}}}}
    TechToTechClassMatrix::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,Array{Symbol,1}}}}
    NMILRegime::Array{Symbol,1}
    r_tax_owner::Float64
    r_tax_offtaker::Float64
    pwf_om::Float64
    pwf_e::Float64
    pwf_prod_incent::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{Symbol,1}}}}
    LevelizationFactor::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{Symbol,1}}}}
    LevelizationFactorProdIncent::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{Symbol,1}}}}
    StorageCostPerKW::Array{Float64,1}
    StorageCostPerKWH::Array{Float64,1}
    OMperUnitSize::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{Symbol,1}}}}
    CapCostSlope::Union{AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,UnitRange{Int64}}}},AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,UnitRange{Int64}}}}}
    CapCostYInt::Union{AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,UnitRange{Int64}}}},AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,UnitRange{Int64}}}}}
    CapCostX::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,UnitRange{Int64}}}}
    ProdIncentRate::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,Array{Symbol,1}}}}
    MaxProdIncent::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{Symbol,1}}}}
    MaxSizeForProdIncent::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{Symbol,1}}}}
    two_party_factor::Int64
    analysis_years::Int64
    AnnualElecLoad::Float64
    LoadProfile::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,UnitRange{Int64}}}}
    ProdFactor::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,Array{Symbol,1}},Axis{:page,UnitRange{Int64}}}}
    StorageMinChargePcent::Float64
    EtaStorIn::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,Array{Symbol,1}}}}
    EtaStorOut::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{Symbol,1}}}}
    BattLevelCoef::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,UnitRange{Int64}},Axis{:col,UnitRange{Int64}}}}
    InitSOC::Float64
    MaxSize::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{Symbol,1}}}}
    MinStorageSizeKW::Union{Int64,Float64}
    MaxStorageSizeKW::Union{Int64,Float64}
    MinStorageSizeKWH::Union{Int64,Float64}
    MaxStorageSizeKWH::Union{Int64,Float64}
    TechClassMinSize::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{Symbol,1}}}}
    MinTurndown::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{Symbol,1}}}}
    FuelRate::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,UnitRange{Int64}},Axis{:page,UnitRange{Int64}}}}
    FuelAvail::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,UnitRange{Int64}}}}
    FixedMonthlyCharge::Union{Int64,Float64}
    AnnualMinCharge::Union{Int64,Float64}
    MonthlyMinCharge::Union{Int64,Float64}
    ExportRates::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,Array{Symbol,1}},Axis{:page,UnitRange{Int64}}}}
    TimeStepRatchetsMonth::AxisArray{Array{Int64,1},1,Array{Array{Int64,1},1},Tuple{Axis{:row,UnitRange{Int64}}}}
    DemandRatesMonth::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,UnitRange{Int64}},Axis{:col,UnitRange{Int64}}}}
    DemandLookbackPercent::Union{Int64,Float64}
    MaxDemandInTier::Array{Float64,1}
    MaxDemandMonthsInTier::Array{Float64,1}
    MaxUsageInTier::Array{Float64,1}
    FuelBurnRateM::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,Array{Symbol,1}},Axis{:page,UnitRange{Int64}}}}
    FuelBurnRateB::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,Array{Symbol,1}},Axis{:page,UnitRange{Int64}}}}
    NMILLimits::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{Symbol,1}}}}
    TechToNMILMapping::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{Symbol,1}},Axis{:col,Array{Symbol,1}}}}
    DemandRates::Union{AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,UnitRange{Int64}},Axis{:col,UnitRange{Int64}}}}, AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,UnitRange{Int64}},Axis{:col,UnitRange{Int64}}}}}
    TimeStepRatchets::Union{Array{Int64,1},AxisArray{Array{Int64,1},1,Array{Array{Int64,1},1},Tuple{Axis{:row,UnitRange{Int64}}}}}
    DemandLookbackMonths::Array{Int64,1}
    CapCostSegCount::Int64
    FuelBinCount::Int64
    DemandBinCount ::Int64
    DemandMonthsBinCount::Int64
    BattLevelCount::Int64
    TimeStepCount::Int64
    Seg::UnitRange{Int64}
    Points::UnitRange{Int64}
    Month::UnitRange{Int64}
    Ratchets::UnitRange{Int64}
    FuelBin::UnitRange{Int64}
    DemandBin::UnitRange{Int64}
    DemandMonthsBin::UnitRange{Int64}
    BattLevel::UnitRange{Int64}
    TimeStep::UnitRange{Int64}
    TimeStepBat::UnitRange{Int64}
    TimeStepScaling::Float64
end


function build_params(uuid="eda919d6-1481-4bf9-a531-a1b3397c8c67")
    
    jldPath = "data/julia_data_files/AA_" * uuid * ".jld"

    @load(jldPath,
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
          BattLevelCoef,
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
          BattLevelCount,
          TimeStepCount,
          Seg,
          Points,
          Month,
          Ratchets,
          FuelBin,
          DemandBin,
          DemandMonthsBin,
          BattLevel,
          TimeStep,
          TimeStepBat,
          TimeStepScaling)

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
                      BattLevelCoef,
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
                      BattLevelCount,
                      TimeStepCount,
                      Seg,
                      Points,
                      Month,
                      Ratchets,
                      FuelBin,
                      DemandBin,
                      DemandMonthsBin,
                      BattLevel,
                      TimeStep,
                      TimeStepBat,
                      TimeStepScaling)

    return param

end
