#=
reopt:
- Julia version: 1.2
- Author: nlaws
- Date: 2019-11-01
=#
using JuMP
using Xpress


function reopt(data;
    Tech,
    TechIsGrid,
    Load,
    TechToLoadMatrix,
    TechClass,
    NMILRegime,
    TurbineDerate,
    TechToTechClassMatrix,
    ProdFactor,
    EtaStorIn,
    EtaStorOut,
    MaxSize,
    MinStorageSizeKW,
    MaxStorageSizeKW,
    MinStorageSizeKWH,
    MaxStorageSizeKWH,
    TechClassMinSize,
    MinTurndown,
    LevelizationFactor,
    LevelizationFactorProdIncent,
    pwf_e,
    pwf_om,
    two_party_factor,
    pwf_prod_incent,
    ProdIncentRate,
    MaxProdIncent,
    MaxSizeForProdIncent,
    CapCostSlope,
    CapCostX,
    CapCostYInt,
    r_tax_owner,
    r_tax_offtaker,
    StorageCostPerKW,
    StorageCostPerKWH,
    OMperUnitSize,
    OMcostPerUnitProd,
    analysis_years,
    NumRatchets,
    FuelBinCount,
    DemandBinCount,
    DemandMonthsBinCount,
    DemandRatesMonth,
    DemandRates,
    # MinDemand,  # not used in REopt
    TimeStepRatchets,
    MaxDemandInTier,
    MaxUsageInTier,
    MaxDemandMonthsInTier,
    FuelRate,
    FuelAvail,
    FixedMonthlyCharge,
    AnnualMinCharge,
    MonthlyMinCharge,
    ExportRates,
    DemandLookbackMonths,
    DemandLookbackPercent,
    TimeStepRatchetsMonth,
    FuelBurnRateM,
    FuelBurnRateB,
    TimeStepCount,
    TimeStepScaling,
    CapCostSegCount,
    LoadProfile,
    AnnualElecLoad,
    NMILLimits,
    TechToNMILMapping,
    StorageMinChargePcent,
    InitSOC,
)
    MAXTIME = data["inputs"]["Scenario"]["timeout_seconds"]
    REopt = direct_model(Xpress.Optimizer(MAXTIME=MAXTIME))
    @objective(REopt, Min, 1)
    optimize!(REopt)
    if termination_status(REopt) == MOI.OPTIMAL
        status = "optimal"
    else
        status = "not optimal"
    end
    data["outputs"]["Scenario"]["status"] = status
    return data
end