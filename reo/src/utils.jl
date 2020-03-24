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
	 ###  Sets  ###
	 Storage::Array{String,1}      # Set B in math; new; B = "Elec","HotThermal","ColdThermal"
     TechClass::Array{String,1}    # Set C
	 DemandBin::UnitRange{Int64}   # Set E
	 FuelType::Array{String,1}     # Set F; new; F = {"NaturalGas"} for CHP and whatever fuel source is used for Boiler
     TimeStep::UnitRange{Int64}    # Set H
     TimeStepBat::UnitRange{Int64} # Set H union {0}
	 Segmentation::Array{String,1}	# Set K; new; elements = { "CapCost", "FuelBurn" }
	 Month::UnitRange{Int64} 	    # Set M
	 DemandMonthsBin::UnitRange{Int64}	# Set N
	 Ratchets::UnitRange{Int64}	   # Set R
     Seg::UnitRange{Int64}	       # Set S
	 Tech::Array{String,1}         # Set T in math
	 FuelBin::UnitRange{Int64}	   # To be removed
	 PricingTier::UnitRange{Int64}  # Set U: Pricing Tiers (proposed revision)
	 NMILRegime::Array{String,1}	# Set V: Net-metering Regimes
	 
	 ###  Subsets and Indexed Sets  ####
	 #ElecStorage::Array{String,1}  # B^{e} \subset B: Electrical energy storage systems
	 #HotTES::Array{String,1}  # B^{h} \subset B: Hot thermal energy storage systems
	 #ColdTES::Array{String,1}  # B^{c} \subset B: Cold thermal energy storage systems
	 #TES::Array{String,1}  # B^{th} \subset B: Thermal energy storage systems
	 #FuelTypeByTech::AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}  # F_t: Fuel types accessible by technology t
	 TimeStepRatchetsMonth::AxisArray{Array{Int64,1},1,Array{Array{Int64,1},1},Tuple{Axis{:row,UnitRange{Int64}}}}   #  H_m: Time steps in month m
	 TimeStepRatchets::Union{Array{Int64,1},AxisArray{Array{Any,1},1,Array{Array{Any,1},1},Tuple{Axis{:row,UnitRange{Int64}}}},AxisArray{Array{Int64,1},1,Array{Array{Int64,1},1},Tuple{Axis{:row,UnitRange{Int64}}}}}    #  H_r: Time steps in ratchet r
	 #K_t \subset K: Segmentations applied to technology t
	 #CapCostSeg::UnitRange{Int64}  # K^c \subset K: Capital Cost Segmentations
	 #FuelBurnSlopeSeg::UnitRange{Int64} # K^f \subset K: Fuel Burn Segmentations
	 DemandLookbackMonths::Array{Any,1}   # M^{lb}: Look back months considered for peak pricing 
	 #SegByTechSegmentation::AxisArray{Int64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}},Axis{:page,UnitRange{Int64}}}} # S_{kt}: System size segments from segmentation k applied to technology t
	 #TechsChargingStorage::AxisArray{Array{Int64,1},1,Array{Array{Int64,1},1},Tuple{Axis{:row,UnitRange{Int64}}}} # T_b \subset T: Technologies that can charge storage system b
	 #TechsInClass::AxisArray{Array{Int64,1},1,Array{Array{String,1},1},Tuple{Axis{:row,UnitRange{Int64}}}} # T_c \subset T: Technologies that are in class c
	 #TechsByFuelType::AxisArray{Array{Int64,1},1,Array{Array{String,1},1},Tuple{Axis{:row,UnitRange{Int64}}}}   # T_f \subset T: Technologies that burn fuel type f
	 #TechsByPricingTier::AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}  # T_u  \subset T: Technologies that access pricing tier u
	 #TechsByNMILRegime::AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}} # T_v \subset T: Technologies that may acess net-meterng regime v 
	 #AbsorptionChillers::Array{String,1}  # T^{ac} \subset T: Absorption Chillers
	 #CHPTechs::Array{String,1}  # T^{CHP} \subset T: CHP technologies
	 #CoolingTechs::Array{String,1}  # T^{cl} \subset T: Cooling technologies
	 #ElectricTechs::Array{String,1}  # T^{e} \subset T: Electricity-producing technologies
	 #ElectricChillers::Array{String,1}  # T^{ec} \subset T: Electric chillers 
	 #FuelBurningTechs::Array{String,1}  # T^{f} \subset T: Fuel-burning technologies
	 #HeatingTechs::Array{String,1}  # T^{ht} \subset T: Heating technologies
	 #TechsNoTurndown::Array{String,1}  # T^{ac} \subset T: Technologies that cannot turn down, i.e., PV and wind
	 #PricingTiersByTech::AxisArray{Array{Int64,1},1,Array{Array{String,1},1},Tuple{Axis{:row,UnitRange{Int64}}}}   # U_t \subset U:  Pricing tiers accessible by technology td
	 #PricingTiersNM::Array{Int64}  # U^{nm} \subset U: Pricing Tiers Used in net-metering
	 
	 ###  Parameters and Tables supporting Indexed Sets ###
	 TechToTechClassMatrix::AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}} # Defines T_c: technologies in class c
	 TechToLoadMatrix::AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}    # Defines electrical, hot and cold thermal technology subsets
	 TechToNMILMapping::AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}  # Defines set T_v: Technologies that may be access net-metering regime v 
	 
	 ###  Scaling Parameters ###
	 TimeStepScaling::Float64  # \Delta: Time step scaling [h]
	 
	 ###  Parameters for Costs and their Functional Forms ###
     AnnualMinCharge::Float64    # c^{amc}: Utility annual minimum charge
     MonthlyMinCharge::Float64    # c^{mmc}: Utility monthly minimum charge  (not in math; will use this in min charge calculation)
	 FixedMonthlyCharge::Float64  # c^{fmc}: Utility monthly fixed charge
	 StorageCostPerKW::Float64    # c^{kW}_{b}:  Capital cost per unit power capacity of storage system b [$/kW]    NOTE: Needs to be updated for set B
     StorageCostPerKWH::Float64   # c^{kWh}_{b}:  Capital cost per unit energy capacity of storage system b [$/kWh]  NOTE: Needs to be updated for set B 
	 #StoragePowerCost::AxisArray{Float64,1,Array{Float64,1},Axis{:row,Array{String,1}}}  # c^{kW}_{b}:  Capital cost per unit power capacity of storage system b [$/kW]  (NEW)
	 #StorageEnergyCost::AxisArray{Float64,1,Array{Float64,1},Axis{:row,Array{String,1}}}  # c^{kWh}_{b}:  Capital cost per unit energy capacity of storage system b [$/kWh]  (NEW)
	 FuelRate::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}},Axis{:page,UnitRange{Int64}}}}   	 # to be replaced by FuelCost and ElecRate
	 #FuelCost::AxisArray{Float64} # c^{u}_{f}: Unit cost of fuel type f [$/MMBTU]  in math  (NEW)
	 #ElecRate::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}  #   c^{g}_{uh}: Grid energy cost in energy demand tier u during time step h  (NEW)
	 OMperUnitSize::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}} # c^{om}_{t}: Operation and maintenance cost of technology t per unit of system size [$/kW]
     
	 ExportRates::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}},Axis{:page,UnitRange{Int64}}}}    # to be replaced by GridExportRates
	 #GridExportRates::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{Int64,1}}, Axis{:col,UnitRange{Int64}}}}    # c^{e}_{uh}: Export rate for energy in energy pricing tier u in time step h   (NEW)
	 CapCostSlope::Union{AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}},AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}}   # c^{cm}_{ts}: Slope of capital cost curve for technology t in segment s 
     CapCostYInt::Union{AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}},AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}}   # c^{cb}_{ts}: Y-Intercept of capital cost curve for technology t in segment s 
     CapCostX::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}    # X-value of inflection point (will be changed)
	 #For the replacement of CapCostX, see new parameters SegmentLB and SegmentUB in section "System size and fuel limit parameters"
	 DemandRates::Union{Array{Float64,1},AxisArray{Any,2,Array{Any,2},Tuple{Axis{:row,UnitRange{Int64}},Axis{:col,UnitRange{Int64}}}},AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,UnitRange{Int64}},Axis{:col,UnitRange{Int64}}}}}    # c^{r}_{re}: Cost per unit peak demand in tier e during ratchet r
	 DemandRatesMonth::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,UnitRange{Int64}},Axis{:col,UnitRange{Int64}}}}   # c^{rm}_{mn}: c^{r}_{re}: Cost per unit peak demand in tier n during month m
	 
	 ###  Demand Parameters ###
	 LoadProfile::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}   # Covers Electrical Load and Thermal Load Profiles; this is to be split into three parameters in the math
	 # ElecLoad::Array{Float64,1}  # \delta^{d}_{h}: Electrical load in time step h   [kW]
	 # HeatingLoad::Array{Float64,1}  # \delta^{bo}_{h}: Heating load in time step h   [MMBTU/hr]
	 # CoolingLoad::Array{Float64,1}  # \delta^{c}_{h}: Cooling load in time step h   [kW]
     DemandLookbackPercent::Float64    # \delta^{lp}: Demand Lookback proportion [fraction]
     MaxDemandInTier::Array{Float64,1}  # \delta^{t}_{e}: Maximum power demand in ratchet e
     MaxDemandMonthsInTier::Array{Float64,1}   # \delta^{mt}_{n}: Maximum monthly power demand in tier n
	 #MaxGridSales::Array{Float64,1}   # \delta^{gs}_{u}: Maximum allowable energy sales in tier u in math; equal to sum of LoadProfile["1R",ts] on set TimeStep for tier 1 (analogous "1W") and unlimited for "1X"
     MaxUsageInTier::Array{Float64,1}   # \delta^{tu}_{u}: Maximum monthly energy demand in tier u
	 
	 
	 ###  Incentive Parameters ###
	 NMILLimits::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}   # i^{n}_{v}: Net metering and interconnect limits in net metering regime v [kW]
     
     MaxProdIncent::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}           # \bar{i}_t: Upper incentive limit for technology t [$]
	 ProdIncentRate::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}   # to be replaced by ProductionIncentiveRate 
	 #ProductionIncentiveRate::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}  # i^{r}_{t}: Incentive rate for technology t [$/kWh] (NEW)
	 MaxSizeForProdIncent::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}    # \bar{i}^{\sigma}_t: Maximum system size to obtain production incentive for technology t [kW]	 
	 
	 ###  Technology-specific Time-series Factor Parameters ###
	 ProdFactor::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}},Axis{:page,UnitRange{Int64}}}}   # to eb replaced by production factor 
	 #ProductionFactor::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}     #f^{p}_{th}  Production factor of technology t and time step h  [unitless]  (NEW)
     # f^{fa}_{th}: Fuel burn ambient correction factor of technology t at time step h [unitless] 
	 # f^{ha}_{th}: Hot water ambient correction factor of technology t at time step h [unitless] 
	 # f^{ht}_{th}: Hot water thermal grade correction factor t correction factor of technology t at time step h [unitless] 
	 # f^{ed}_{th}: Fuel burn ambient correction factor of technology t at time step h [unitless] 
	 
	 ###  Technology-specific Factor Parameters ###
	 TurbineDerate::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}  # f^{d}_{t}: Derate factor for turbine technologyt [unitless]
     MinTurndown::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}     # f^{td}_{t}:  Minimum turn down for technology t [unitless]
     pwf_prod_incent::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}   # f^{pi}_t: Present worth factor for incentives for technology t [unitless] 
	 LevelizationFactor::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}    # f^{l}_{t}: Levelization factor of technology t [unitless]
     LevelizationFactorProdIncent::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}   # f^{pi}_{t}: Levelization factor of production incentive for technology t [unitless]
	 
	 ###  Generic Factor Parameters ###
	 pwf_om::Float64  # f^{om}: Operations and maintenance present worth factor [unitless] 
     pwf_e::Float64   # f^{e}: Energy present worth factor [unitless] 
	 r_tax_owner::Float64      # f^{tow}: Tax rate factor for owner [fraction]
     r_tax_offtaker::Float64   # f^{tot}: Tax rate factor for offtaker [fraction]
	 
	 ###  System Size and Fuel Limit Parameters ###
	 TechClassMinSize::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}   #  \ubar{b}^{\sigma}_{c}: Minimum system size for technology class c [kW]
	 MaxSize::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}    #  \bar{b}^{\sigma}_{t}: Maximum system size for technology t [kW]
	 FuelAvail::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}  # to be replaced
	 #FuelLimit::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}} # b^{fa}_{f}: Amount of available fuel for type f [MMBTU]   (NEW)
	 
	 ###  Efficiency Parameters ###
	 EtaStorIn::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}  # to be replaced by ChargeEfficiency (index change)
	 #ChargeEfficiency::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}  # \eta^{esi}_{bt}: Efficiency of charging storage system b using technology t  [fraction] (NEW)
	 #GridChargeEfficiency::Float64   # \eta^{esig}: Efficiency of charging electrical storage using grid power [fraction] (NEW)
     EtaStorOut::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}  # To be replaced by DischargeEfficiency (Index Change)
     #DischargeEfficiency::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}  # \eta^{eso}_{b}: Efficiency of discharging storage system b [fraction] (NEW)
	 # \eta^{bo}: Boiler efficiency [fraction]
	 # \eta^{ecop}: Electric chiller efficiency [fraction]
	 # \eta^{acop}: Absorption chiller efficiency [fraction]
	 
	 
	 ###  Storage Parameters ###
     MinStorageSizeKWH::Float64     # \bar{w}^{bkWh}_{b}: Maximum energy capacity of storage system b (needs to be indexed on b)
     MaxStorageSizeKWH::Float64     # \ubar{w}^{bkWh}_{b}: Minimum energy capacity of storage system b (needs to be indexed on b )
	 MinStorageSizeKW::Float64     # \bar{w}^{bkW}_{b}: Maximum power capacity of storage system b (needs to be indexed on b )
     MaxStorageSizeKW::Float64     # \ubar{w}^{bkW}_{b}: Minimum power capacity of storage system b (needs to be indexed on b )
     StorageMinChargePcent::Float64     #  \ubar{w}^{mcp}_{b}: Minimum state of charge of storage system b
     InitSOC::Float64    # w^{i}_{b} Initial percent state of charge for storage system b
	 StorageMinSizeEnergy::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}     # \bar{w}^{bkWh}_{b}: Maximum energy capacity of storage system b [kWh]
     StorageMaxSizeEnergy::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}     # \ubar{w}^{bkWh}_{b}: Minimum energy capacity of storage system b [kWh]
	 StorageMinSizePower::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}     # \bar{w}^{bkW}_{b}: Maximum power capacity of storage system b [kW]
     StorageMaxSizePower::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}     # \ubar{w}^{bkW}_{b}: Minimum power capacity of storage system b [kW]
     StorageMinSOC::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}     #  \ubar{w}^{mcp}_{b}: Minimum state of charge of storage system b [fraction]
     StorageInitSOC::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}  #Initial state of charge of storage system b [fraction]
	 
	 ###  Fuel Burn Parameters ###
     FuelBurnRateM::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}},Axis{:page,UnitRange{Int64}}}}
     FuelBurnRateB::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}},Axis{:page,UnitRange{Int64}}}}
	 #FuelBurnSlope::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}} # m^\text{fm}_{t}: Fuel burn rate slope parameter for technology t
	 #FuelBurnYInt::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}} # m^\text{fb}_{t}: Fuel burn rate slope parameter for technology t
	 
	 ###  CHP Thermal Performance Parameters ###
	 
	 
	 ### New parameters (commented copies above ###
	 StoragePowerCost::AxisArray{Float64,1,Array{Float64,1},Axis{:row,Array{String,1}}}  # c^{kW}_{b}:  Capital cost per unit power capacity of storage system b [$/kW]  (NEW)
	 StorageEnergyCost::AxisArray{Float64,1,Array{Float64,1},Axis{:row,Array{String,1}}}  # c^{kWh}_{b}:  Capital cost per unit energy capacity of storage system b [$/kWh]  (NEW)
	 FuelCost::AxisArray{Float64} # c^{u}_{f}: Unit cost of fuel type f [$/MMBTU]  in math  (NEW)
	 ElecRate::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}  #   c^{g}_{uh}: Grid energy cost in energy demand tier u during time step h  (NEW)
	 GridExportRates::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{Int64,1}}, Axis{:col,UnitRange{Int64}}}}    # c^{e}_{uh}: Export rate for energy in energy pricing tier u in time step h   (NEW)
	 FuelBurnSlope::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}} # m^\text{fm}_{t}: Fuel burn rate slope parameter for technology t
	 FuelBurnYInt::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}} # m^\text{fb}_{t}: Fuel burn rate slope parameter for technology t
	 MaxGridSales::Array{Float64,1}   # \delta^{gs}_{u}: Maximum allowable energy sales in tier u in math; equal to sum of LoadProfile["1R",ts] on set TimeStep for tier 1 (analogous "1W") and unlimited for "1X"
	 ProductionIncentiveRate::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}  # i^{r}_{t}: Incentive rate for technology t [$/kWh] (NEW)
	 ProductionFactor::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}     #f^{p}_{th}  Production factor of technology t and time step h  [unitless]  (NEW)
	 ElecLoad::Array{Float64,1}  # \delta^{d}_{h}: Electrical load in time step h   [kW]
	 FuelLimit::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}} # b^{fa}_{f}: Amount of available fuel for type f [MMBTU]   (NEW)
	 ChargeEfficiency::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}  # \eta^{esi}_{bt}: Efficiency of charging storage system b using technology t  [fraction] (NEW)
	 GridChargeEfficiency::Float64   # \eta^{esig}: Efficiency of charging electrical storage using grid power [fraction] (NEW)
	 DischargeEfficiency::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}  # \eta^{eso}_{b}: Efficiency of discharging storage system b [fraction] (NEW)
	 StorageMinSizeEnergy::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}     # \bar{w}^{bkWh}_{b}: Maximum energy capacity of storage system b [kWh] (NEW)
     StorageMaxSizeEnergy::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}     # \ubar{w}^{bkWh}_{b}: Minimum energy capacity of storage system b [kWh] (NEW)
	 StorageMinSizePower::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}     # \bar{w}^{bkW}_{b}: Maximum power capacity of storage system b [kW] (NEW)
     StorageMaxSizePower::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}     # \ubar{w}^{bkW}_{b}: Minimum power capacity of storage system b [kW] (NEW)
     StorageMinSOC::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}     #  \ubar{w}^{mcp}_{b}: Minimum state of charge of storage system b [fraction] (NEW)
     StorageInitSOC::AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}}  #Initial state of charge of storage system b [fraction] (NEW)
	 
	 
	 ### To be replaced  ###
	 Load::Array{String,1}
	 TechIsGrid::AxisArray{Int64,1,Array{Int64,1},Tuple{Axis{:row,Array{String,1}}}}
	 
	 ### Not used or used for calculation of other parameters ###
	 two_party_factor::Float64 # Not used (?)
     analysis_years::Int64     # Used to calculate present worth factors maybe?
     AnnualElecLoad::Float64   # Not used anymore (can just sum LoadProfile["1R",h] for all h in TimeStep
     CapCostSegCount::Int64    # Size of set S 
     FuelBinCount::Int64       # Size of set U  (but should be F now)
     DemandBinCount ::Int64    # Size of set E
     DemandMonthsBinCount::Int64   # Size of set N
     TimeStepCount::Int64          # Size of set H
     Points::UnitRange{Int64}      # CapCostSegCount+1; this is going to be the size of set S^{c} now
		
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
		  StoragePowerCost,
		  StorageEnergyCost,
		  FuelCost,
		  ElecRate,
		  GridExportRates,
		  FuelBurnSlope,
		  FueBurnYInt,
		  MaxGridSales,
		  ProductionIncentiveRate,
		  ProductionFactor,
		  ElecLoad,
		  FuelLimit,
		  ChargeEfficiency,
		  GridChargeEfficiency,
		  DischargeEfficiency,
		  StorageMinSizeEnergy,
		  StorageMaxSizeEnergy,
		  StorageMinSizePower,
		  StorageMaxSizePower,
		  StorageMinSOC,
		  StorageInitSOC,
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
	Segmentation=1:1
	FuelType = 1:FuelBinCount
	PricingTier = 1:FuelBinCount
	Storage = 1:1

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
	StoragePowerCost = parameter(Storage, StoragePowerCost)
	StorageEnergyCost = parameter(Storage, StorageEnergyCost)
	FuelCost = parameter(FuelType, FuelCost)
	ElecRate = parameter((PricingTier,TimeStep), ElecRate)
	GridExportRates = parameter((PricingTier, TimeStep), GridExportRates)
	FuelBurnSlope = parameter(Tech, FuelBurnSlope)
	FuelBurnYInt = parameter(Tech, FuelBurnYInt)
	MaxGridSales = parameter(PricingTier, MaxGridSales)
	ProductionFactor = parameter((Tech, TimeStep), ProductionFactor)
	ProductionIncentiveRate = parameter(Tech, ProductionIncentiveRate)
	ElecLoad = parameter(TimeStep, ElecLoad)
	FuelLimit = parameter(FuelType, FuelLimit)
	ChargeEfficiency = parameter(Storage, ChargeEfficiency)
	GridChargeEfficiency = parameter(Storage, GridChargeEfficiency)
	DischargeEfficiency = parameter(Storage, DischargeEfficiency)
    StorageMinSizeEnergy = parameter(Storage, StorageMinSizeEnergy)
    StorageMaxSizeEnergy = parameter(Storage, StorageMaxSizeEnergy)
    StorageMinSizePower = parameter(Storage, StorageMinSizePower)
    StorageMaxSizePower = parameter(Storage, StorageMaxSizePower)
    StorageMinSOC = parameter(Storage, StorageMinSOC)
    StorageInitSOC = parameter(Storage, StorageInitSOC)

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
                      OMcostPerUnitProd,
					  Segmentation,
					  FuelType,
					  PricingTier,
					  Storage,
					  StoragePowerCost,
					  StorageEnergyCost,
					  FuelCost,
					  ElecRate,
					  GridExportRates,
					  FuelBurnSlope,
					  FueBurnYInt,
					  MaxGridSales,
					  ProductionIncentiveRate,
					  ProductionFactor,
					  ElecLoad,
					  FuelLimit,
					  ChargeEfficiency,
					  GridChargeEfficiency,
					  DischargeEfficiency,
					  StorageMinSizeEnergy,
					  StorageMaxSizeEnergy,
					  StorageMinSizePower,
					  StorageMaxSizePower,
					  StorageMinSOC,
					  StorageInitSOC
					  )

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
