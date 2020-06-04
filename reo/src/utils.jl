import Base.length
import Base.reshape
import AxisArrays.AxisArray
import JuMP.value
import LinearAlgebra: transpose
using AxisArrays
using JuMP
using Printf


function string_dictkeys_tosymbols(d::Dict)
    d2 = Dict()
    for (k, v) in d
        d2[Symbol(k)] = v
    end
    return d2
end

function filter_dict_to_match_struct_field_names(d::Dict, s::DataType)
    f = fieldnames(s)
    d2 = Dict()
    for k in f
        if haskey(d, k)
            d2[k] = d[k]
        else
            @sprintf "\nWARNING: dict is missing struct field %s !\n" k
        end
    end
    return d2
end


##TODO Get rid of union types
Base.@kwdef struct Parameter
    # TODO: change AxisArray types back to heavily specified types like:
    #       AxisArray{Float64,1,Array{Float64,1},Tuple{Axis{:row,Array{String,1}}}} ?
    #       Problem is that many Array{Float64, 1} can be empty so PyCall makes them Array{Any, 1}
	 ###  Sets  ###
	 #Storage::Array{String,1}      # Set B in math; new; B = "Elec","HotThermal","ColdThermal"
     TechClass::Array{String,1}    # Set C
	 DemandBin::UnitRange{Int64}   # Set E
	 #FuelType::Array{String,1}     # Set F; new; F = {"NaturalGas"} for CHP and whatever fuel source is used for Boiler
     TimeStep::UnitRange{Int64}    # Set H
     TimeStepBat::UnitRange{Int64} # Set H union {0}
	 #Subdivision::Array{String,1}	# Set K; new; elements = { "CapCost", "FuelBurn" }
	 Month::UnitRange{Int64} 	    # Set M
	 DemandMonthsBin::UnitRange{Int64}	# Set N
	 Ratchets::UnitRange{Int64}	   # Set R
     Seg::UnitRange{Int64}	       # Set S
	 Tech::Array{String,1}         # Set T in math
	 FuelBin::UnitRange{Int64}	   # To be removed
	 PricingTier::UnitRange{Int64}  # Set U: Pricing Tiers (proposed revision) #new
	 NMILRegime::Array{String,1}	# Set V: Net-metering Regimes
	 
	 ###  Subsets and Indexed Sets  ####
	 #ElecStorage::Array{String,1}  # B^{e} \subset B: Electrical energy storage systems
	 #HotTES::Array{String,1}  # B^{h} \subset B: Hot thermal energy storage systems (IGNORE)
	 #ColdTES::Array{String,1}  # B^{c} \subset B: Cold thermal energy storage systems (IGNORE)
	 #ThermalStorage::Array{String,1}  # B^{th} \subset B: Thermal energy storage systems (IGNORE)
	 #FuelTypeByTech::AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}  # F_t: Fuel types accessible by technology t
	 TimeStepRatchetsMonth::Array{Array{Int64,1},1}   #  H_m: Time steps in month m
	 TimeStepRatchets::Array{Array{Int64,1},1}   #  H_r: Time steps in ratchet r
     TimeStepsWithGrid::Array{Int64,1}  # H_g: Time steps with grid connection
     TimeStepsWithoutGrid::Array{Int64,1}	 # H \setminus H_g: Time steps without grid connection 
	 #SubdivsionByTech K_t \subset K: Subdivisions applied to technology t
	 #CapCostSeg::UnitRange{Int64}  # K^c \subset K: Capital Cost Subdivisions
	 #FuelBurnSlopeSeg::UnitRange{Int64} # K^f \subset K: Fuel Burn Subdivisions   (IGNORE)
	 DemandLookbackMonths::Array{Any,1}   # M^{lb}: Look back months considered for peak pricing 
	 #SegByTechSubdivision::AxisArray{Int64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}},Axis{:page,UnitRange{Int64}}}} # S_{kt}: System size segments from segmentation k applied to technology t
	 #TechsChargingStorage::AxisArray{Array{Int64,1},1,Array{Array{Int64,1},1},Tuple{Axis{:row,UnitRange{Int64}}}} # T_b \subset T: Technologies that can charge storage system b
	 #TechsInClass::AxisArray{Array{Int64,1},1,Array{Array{String,1},1},Tuple{Axis{:row,UnitRange{Int64}}}} # T_c \subset T: Technologies that are in class c
	 #TechsByFuelType::AxisArray{Array{Int64,1},1,Array{Array{String,1},1},Tuple{Axis{:row,UnitRange{Int64}}}}   # T_f \subset T: Technologies that burn fuel type f
	 #TechsByPricingTier::AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}  # T_u  \subset T: Technologies that access pricing tier u
	 #TechsByNMILRegime::AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}} # T_v \subset T: Technologies that may acess net-meterng regime v 
	 #AbsorptionChillers::Array{String,1}  # T^{ac} \subset T: Absorption Chillers (IGNORE)
	 #CHPTechs::Array{String,1}  # T^{CHP} \subset T: CHP technologies (IGNORE)
	 #CoolingTechs::Array{String,1}  # T^{cl} \subset T: Cooling technologies (IGNORE)
	 #ElectricTechs::Array{String,1}  # T^{e} \subset T: Electricity-producing technologies
	 #ElectricChillers::Array{String,1}  # T^{ec} \subset T: Electric chillers  (IGNORE) 
	 #FuelBurningTechs::Array{String,1}  # T^{f} \subset T: Fuel-burning technologies
	 #HeatingTechs::Array{String,1}  # T^{ht} \subset T: Heating technologies (IGNORE)
	 #TechsNoTurndown::Array{String,1}  # T^{ac} \subset T: Technologies that cannot turn down, i.e., PV and wind
	 #TechsTurndown::Array{String,1}  # This is just T \setminus T^{ac}; not in the math
	 #PricingTiersByTech::AxisArray{Array{Int64,1},1,Array{Array{String,1},1},Tuple{Axis{:row,UnitRange{Int64}}}}   # U_t \subset U:  Pricing tiers accessible by technology td
	 #PricingTiersNM::Array{Int64}  # U^{nm} \subset U: Pricing Tiers Used in net-metering
	 
	 ###  Parameters and Tables supporting Indexed Sets ###
	 TechToNMILMapping#::AxisArray{Int64,2,Array{Int64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}  # Defines set T_v: Technologies that may be access net-metering regime v 
	 
	 ###  Scaling Parameters ###
	 TimeStepScaling::Float64  # \Delta: Time step scaling [h]
	 
	 ###  Parameters for Costs and their Functional Forms ###
     AnnualMinCharge::Float64    # c^{amc}: Utility annual minimum charge
     MonthlyMinCharge::Float64    # c^{mmc}: Utility monthly minimum charge  (not in math; will use this in min charge calculation)
	 FixedMonthlyCharge::Float64  # c^{fmc}: Utility monthly fixed charge
	 #FuelCost::AxisArray{Float64} # c^{u}_{f}: Unit cost of fuel type f [$/MMBTU]  in math  (NEW)
	 #ElecRate::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}  #   c^{g}_{uh}: Grid energy cost in energy demand tier u during time step h  (NEW)
	 OMperUnitSize # c^{om}_{t}: Operation and maintenance cost of technology t per unit of system size [$/kW]
     OMcostPerUnitProd
     
	 ExportRates    # to be replaced by GridExportRates
	 #GridExportRates::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{Int64,1}}, Axis{:col,UnitRange{Int64}}}}    # c^{e}_{uh}: Export rate for energy in energy pricing tier u in time step h   (NEW)
	 CapCostSlope   # c^{cm}_{ts}: Slope of capital cost curve for technology t in segment s 
     CapCostYInt  # c^{cb}_{ts}: Y-Intercept of capital cost curve for technology t in segment s 
     CapCostX    # X-value of inflection point (will be changed)
	 #For the replacement of CapCostX, see new parameters SegmentLB and SegmentUB in section "System size and fuel limit parameters"
	 DemandRates  # c^{r}_{re}: Cost per unit peak demand in tier e during ratchet r
	 DemandRatesMonth   # c^{rm}_{mn}: Cost per unit peak demand in tier n during month m
	 
	 ###  Demand Parameters ###
	 ElecLoad::Array{Float64,1}  # \delta^{d}_{h}: Electrical load in time step h   [kW]
	 # HeatingLoad::Array{Float64,1}  # \delta^{bo}_{h}: Heating load in time step h   [MMBTU/hr]
	 # CoolingLoad::Array{Float64,1}  # \delta^{c}_{h}: Cooling load in time step h   [kW]
     DemandLookbackPercent::Float64    # \delta^{lp}: Demand Lookback proportion [fraction]
     MaxDemandInTier::Array{Float64,1}  # \delta^{t}_{e}: Maximum power demand in ratchet e
     MaxDemandMonthsInTier::Array{Float64,1}   # \delta^{mt}_{n}: Maximum monthly power demand in tier n
	 #MaxGridSales::Array{Float64,1}   # \delta^{gs}_{u}: Maximum allowable energy sales in tier u in math; equal to sum of LoadProfile["1R",ts] on set TimeStep for tier 1 (analogous "1W") and unlimited for "1X"
     MaxUsageInTier::Array{Float64,1}   # \delta^{tu}_{u}: Maximum monthly energy demand in tier u
	 
	 
	 ###  Incentive Parameters ###
	 NMILLimits   # i^{n}_{v}: Net metering and interconnect limits in net metering regime v [kW]
     
     MaxProdIncent           # \bar{i}_t: Upper incentive limit for technology t [$]
	 #ProductionIncentiveRate::AxisArray  # i^{r}_{t}: Incentive rate for technology t [$/kWh] (NEW)
	 MaxSizeForProdIncent    # \bar{i}^{\sigma}_t: Maximum system size to obtain production incentive for technology t [kW]	 
	 
	 ###  Technology-specific Time-series Factor Parameters ###
	 #ProductionFactor::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,UnitRange{Int64}}}}     #f^{p}_{th}  Production factor of technology t and time step h  [unitless]  (NEW)
     # f^{fa}_{th}: Fuel burn ambient correction factor of technology t at time step h [unitless] 
	 # f^{ha}_{th}: Hot water ambient correction factor of technology t at time step h [unitless] 
	 # f^{ht}_{th}: Hot water thermal grade correction factor t correction factor of technology t at time step h [unitless] 
	 # f^{ed}_{th}: Fuel burn ambient correction factor of technology t at time step h [unitless] 
	 
	 ###  Technology-specific Factor Parameters ###
	 TurbineDerate  # f^{d}_{t}: Derate factor for turbine technologyt [unitless]
     MinTurndown     # f^{td}_{t}:  Minimum turn down for technology t [unitless]
     pwf_prod_incent   # f^{pi}_t: Present worth factor for incentives for technology t [unitless] 
	 LevelizationFactor    # f^{l}_{t}: Levelization factor of technology t [unitless]
	 
	 ###  Generic Factor Parameters ###
	 pwf_om::Float64  # f^{om}: Operations and maintenance present worth factor [unitless] 
     pwf_e::Float64   # f^{e}: Energy present worth factor [unitless] 
	 r_tax_owner::Float64      # f^{tow}: Tax rate factor for owner [fraction]
     r_tax_offtaker::Float64   # f^{tot}: Tax rate factor for offtaker [fraction]
	 
	 ###  System Size and Fuel Limit Parameters ###
	 TechClassMinSize   #  \ubar{b}^{\sigma}_{c}: Minimum system size for technology class c [kW]
	 MaxSize    #  \bar{b}^{\sigma}_{t}: Maximum system size for technology t [kW]
	 #SegmentMinSize::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}},Axis{:page,UnitRange{Int64}}}}  # \ubar{b}^{\sigma s}_{tks}: Minimum system size for technology t, subdivision k, segments
	 #SegmentMaxSize::AxisArray{Float64,3,Array{Float64,3},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}},Axis{:page,UnitRange{Int64}}}}  # \bar{b}^{\sigma s}_{tks}: Maximum system size for technology t, subdivision k, segments
	 #FuelLimit::AxisArray # b^{fa}_{f}: Amount of available fuel for type f [MMBTU]   (NEW)
	 
	 ###  Efficiency Parameters ###
	 #ChargeEfficiency::AxisArray{Float64,2,Array{Float64,2},Tuple{Axis{:row,Array{String,1}},Axis{:col,Array{String,1}}}}  # \eta^{esi}_{bt}: Efficiency of charging storage system b using technology t  [fraction] (NEW)
	 #GridChargeEfficiency::Float64   # \eta^{esig}: Efficiency of charging electrical storage using grid power [fraction] (NEW)
     #DischargeEfficiency::AxisArray  # \eta^{eso}_{b}: Efficiency of discharging storage system b [fraction] (NEW)
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
     #StorageMinSizeEnergy::AxisArray     # \bar{w}^{bkWh}_{b}: Maximum energy capacity of storage system b [kWh]
     #StorageMaxSizeEnergy::AxisArray     # \ubar{w}^{bkWh}_{b}: Minimum energy capacity of storage system b [kWh]
     #StorageMinSizePower::AxisArray     # \bar{w}^{bkW}_{b}: Maximum power capacity of storage system b [kW]
     #StorageMaxSizePower::AxisArray     # \ubar{w}^{bkW}_{b}: Minimum power capacity of storage system b [kW]
     #StorageMinSOC::AxisArray     #  \ubar{w}^{mcp}_{b}: Minimum state of charge of storage system b [fraction]
     #StorageInitSOC::AxisArray  #Initial state of charge of storage system b [fraction]
	 
	 ###  Fuel Burn Parameters ###
	 #FuelBurnSlope::AxisArray # m^\text{fm}_{t}: Fuel burn rate slope parameter for technology t
	 #FuelBurnYInt::AxisArray # m^\text{fb}_{t}: Fuel burn rate slope parameter for technology t	 

	 ### To be replaced  ###
	 Load::Array{String,1}
	 
	 ### Not used or used for calculation of other parameters ###
	 two_party_factor::Float64
     analysis_years::Int64     # Used to calculate present worth factors maybe?
     AnnualElecLoad::Float64   # Not used anymore (can just sum LoadProfile["1R",h] for all h in TimeStep
     CapCostSegCount::Int64    # Size of set S 
     FuelBinCount::Int64       # Size of set F  
     DemandBinCount ::Int64    # Size of set E
     DemandMonthsBinCount::Int64   # Size of set N
     TimeStepCount::Int64          # Size of set H
     Points::UnitRange{Int64}      # CapCostSegCount+1; this is going to be the size of set S^{c} now
     PricingTierCount::Int64    # Size of set U
	 
     # new parameters for reformulation
     StorageCostPerKW::AxisArray
     StorageCostPerKWH::AxisArray
     FuelCost
     ElecRate
     GridExportRates
     FuelBurnSlope
     FuelBurnYInt
     MaxGridSales::Array{<:Real, 1}
     ProductionIncentiveRate
     ProductionFactor
     FuelLimit
     ChargeEfficiency
     GridChargeEfficiency::Float64
     DischargeEfficiency
     StorageMinSizeEnergy
     StorageMaxSizeEnergy
     StorageMinSizePower
     StorageMaxSizePower
     StorageMinSOC
     StorageInitSOC
     SegmentMinSize::AxisArray
     SegmentMaxSize::AxisArray
	 ElectricDerate

     # New Sets
     Storage
     FuelType
     Subdivision
     ElecStorage
     FuelTypeByTech
     SubdivisionByTech
     SegByTechSubdivision
     TechsChargingStorage
     TechsInClass
     TechsByFuelType
     ElectricTechs
     FuelBurningTechs
     TechsNoTurndown
     SalesTiers
     StorageSalesTiers
     NonStorageSalesTiers
	 SalesTiersByTech
	 TechsBySalesTier
	 CurtailmentTiers
	 TechsByNMILRegime

    # Feature Additions
     TechToLocation::AxisArray
     MaxSizesLocation::Array{Float64, 1}
     Location::UnitRange
end


function Parameter(d::Dict)
    can_be_empty = (
        "MaxSize",
        "OMperUnitSize",
        "OMcostPerUnitProd",
        "MaxProdIncent",
        "MaxSizeForProdIncent",
        "TurbineDerate",
        "MinTurndown",
        "pwf_prod_incent",
        "LevelizationFactor",
        "NMILLimits",
        "TurbineDerate",
        "TechClassMinSize",
		"TechsBySalesTier",
		"SalesTiersByTech",
		"NMILRegime",
		"NMILLimits",
		"TechsByNMILRegime"
     )
    if typeof(d["Tech"]) === Array{Any, 1}  # came from Python as empty array
        d["Tech"] = convert(Array{String, 1}, d["Tech"])
    end
    for x in can_be_empty
        if typeof(x) === Array{Any, 1}  # came from Python as empty array
            d[x] = convert(Array{Float64, 1}, d[x])
        end
    end

    d[:Seg] = 1:d["CapCostSegCount"]
    d[:Points] = 0:d["CapCostSegCount"]
    d[:Month] = 1:12
    d[:Ratchets] = 1:d["NumRatchets"]
    d[:FuelBin] = 1:d["FuelBinCount"]
	d[:PricingTier] = 1:d["PricingTierCount"]
    d[:DemandBin] = 1:d["DemandBinCount"]
    d[:DemandMonthsBin] = 1:d["DemandMonthsBinCount"]
    d[:TimeStep] = 1:d["TimeStepCount"]
    d[:TimeStepBat] = 0:d["TimeStepCount"]
	d[:SalesTiers] = 1:d["SalesTierCount"]
	#Subdivision=1:1
	#FuelType = 1:d["FuelBinCount"]
    #Storage = 1:1
    n_location = length(d["MaxSizesLocation"])
    d[:Location] = 1:n_location
    d["TechToLocation"] = transpose(reshape(d["TechToLocation"], n_location, length(d["Tech"])))

    # the following array manipulation may have to adapt once length(d["Subdivision"]) > 1
    seg_min_size_array = reshape(transpose(reshape(d["SegmentMinSize"], length(d[:Seg]), length(d["Tech"]))), 
                                 length(d["Tech"]), length(d["Subdivision"]), length(d[:Seg]))
    seg_max_size_array = reshape(transpose(reshape(d["SegmentMaxSize"], length(d[:Seg]), length(d["Tech"]))), 
                                length(d["Tech"]), length(d["Subdivision"]), length(d[:Seg]))

    # convert vectors to AxisArray's with axes for REopt JuMP model
    d["TurbineDerate"] = AxisArray(d["TurbineDerate"], d["Tech"])
    d["TechToLocation"] = AxisArray(d["TechToLocation"], d["Tech"], d[:Location])
    d["pwf_prod_incent"] = AxisArray(d["pwf_prod_incent"], d["Tech"])
    d["LevelizationFactor"] = AxisArray(d["LevelizationFactor"], d["Tech"])
    d["OMperUnitSize"] = AxisArray(d["OMperUnitSize"], d["Tech"])
    d["CapCostSlope"] = parameter((d["Tech"], d[:Seg]), d["CapCostSlope"])
    d["CapCostYInt"] = parameter((d["Tech"], d[:Seg]), d["CapCostYInt"])
    d["CapCostX"] = parameter((d["Tech"],d[:Points]), d["CapCostX"])
    d["MaxProdIncent"] = AxisArray(d["MaxProdIncent"], d["Tech"])
    d["MaxSizeForProdIncent"] = AxisArray(d["MaxSizeForProdIncent"], d["Tech"])
    d["MaxSize"] = AxisArray(d["MaxSize"], d["Tech"])
    d["TechClassMinSize"] = AxisArray(d["TechClassMinSize"], d["TechClass"])
    d["MinTurndown"] = AxisArray(d["MinTurndown"], d["Tech"])
    d["DemandRates"] = transpose(reshape(d["DemandRates"], d["DemandBinCount"], d["NumRatchets"]))
    d["ExportRates"] = parameter((d["Tech"], d["Load"], d[:TimeStep]), d["ExportRates"])
    d["DemandRatesMonth"] = parameter((d[:Month], d[:DemandMonthsBin]), d["DemandRatesMonth"])
    d["NMILLimits"] = AxisArray(d["NMILLimits"], d["NMILRegime"])
    d["TechToNMILMapping"] = parameter((d["Tech"], d["NMILRegime"]), d["TechToNMILMapping"])
    d["OMcostPerUnitProd"] = AxisArray(d["OMcostPerUnitProd"], d["Tech"])

    # Reformulation additions
    d["StorageCostPerKW"] = AxisArray(d["StorageCostPerKW"], d["Storage"])
    d["StorageCostPerKWH"] = AxisArray(d["StorageCostPerKWH"], d["Storage"])
    d["FuelCost"] = AxisArray(d["FuelCost"], d["FuelType"])
    d["ElecRate"] = parameter((d[:PricingTier], d[:TimeStep]), d["ElecRate"])
    d["GridExportRates"] = parameter((d[:SalesTiers], d[:TimeStep]), d["GridExportRates"])
    d["FuelBurnSlope"] = AxisArray(d["FuelBurnSlope"], d["Tech"])
    d["FuelBurnYInt"] = AxisArray(d["FuelBurnYInt"], d["Tech"])
    d["ProductionFactor"] = parameter((d["Tech"], d[:TimeStep]), d["ProductionFactor"])
    d["ProductionIncentiveRate"] = AxisArray(d["ProductionIncentiveRate"], d["Tech"])
    d["FuelLimit"] = AxisArray(d["FuelLimit"], d["FuelType"])
    d["ChargeEfficiency"] = parameter((d["Tech"], d["Storage"]), d["ChargeEfficiency"]) # does this need to be indexed on techs?
    #d["GridChargeEfficiency"] = AxisArray(d["GridChargeEfficiency"], d["Storage"])
    d["DischargeEfficiency"] = AxisArray(d["DischargeEfficiency"], d["Storage"])
    d["StorageMinSizeEnergy"] = AxisArray(d["StorageMinSizeEnergy"], d["Storage"])
    d["StorageMaxSizeEnergy"] = AxisArray(d["StorageMaxSizeEnergy"], d["Storage"])
    d["StorageMinSizePower"] = AxisArray(d["StorageMinSizePower"], d["Storage"])
    d["StorageMaxSizePower"] = AxisArray(d["StorageMaxSizePower"], d["Storage"])
    d["StorageMinSOC"] = AxisArray(d["StorageMinSOC"], d["Storage"])
    d["StorageInitSOC"] = AxisArray(d["StorageInitSOC"], d["Storage"])
    d["SegmentMinSize"] = AxisArray(seg_min_size_array, d["Tech"], d["Subdivision"], d[:Seg])
    d["SegmentMaxSize"] = AxisArray(seg_max_size_array, d["Tech"], d["Subdivision"], d[:Seg])
	d["ElectricDerate"] = parameter((d["Tech"], d[:TimeStep]), d["ElectricDerate"])
    d["MaxGridSales"] = [d["MaxGridSales"]]

    # Indexed Sets
    d["SegByTechSubdivision"] = parameter((d["Subdivision"], d["Tech"]), d["SegByTechSubdivision"])
    d["TechsByFuelType"] = len_zero_param(d["FuelType"], d["TechsByFuelType"])
    d["FuelTypeByTech"] = len_zero_param(d["Tech"], d["FuelTypeByTech"])
    d["SubdivisionByTech"] = len_zero_param(d["Tech"], d["SubdivisionByTech"])
    d["TechsInClass"] = len_zero_param(d["TechClass"], d["TechsInClass"])
	d["SalesTiersByTech"] = len_zero_param(d["Tech"], d["SalesTiersByTech"])
	d["TechsBySalesTier"] = len_zero_param(d[:SalesTiers], d["TechsBySalesTier"])
	d["TechsByNMILRegime"] = len_zero_param(d["NMILRegime"], d["TechsByNMILRegime"])

    d = string_dictkeys_tosymbols(d)
    d = filter_dict_to_match_struct_field_names(d, Parameter)
    param = Parameter(;d...)
end

# Code for parameter() function
function paramDataFormatter(setTup::Tuple, data::AbstractArray)
    if typeof(data) === Array{Any, 1}
        data = convert(Array{Float64, 1}, data)
    end
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


function parameter(setTup::Tuple{Array{Symbol,1}, UnitRange{Int64}}, data::Number)
    newTup = ([setTup[1][1], :FAKE], 1:2)
    return AxisArray(fill(data, 2, 2), newTup)
end

# Additional dispatches to make things easier
function length(::Symbol)
    return 1
end

function AxisArray(data::Number, index::Array{T, 1}) where T <: Union{Symbol, String}
    return AxisArray([float(data)], index)
end

function JuMP.value(::Val{false})
    return 0.0
end

function JuMP.value(x::Float64)
    return x
end

function len_zero_param(sets, arr::Array)
    try
        if length(arr) == 0
            dims = setdiff(size(arr), 0)
            zero_array = Array{Array}(undef, dims...)
            return AxisArray(zero_array, sets)
        else
            return AxisArray(arr, sets)
        end
    catch
        return []
    end
end
