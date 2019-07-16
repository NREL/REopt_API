include("readDataTable.jl")
@time include("reopt.jl")
import JSON

# Parse REopt results
resultPath = dataPath * "/Outputs/REopt_results.json"

function testResult(resultPath::String)
    resultDict = JSON.parsefile(resultPath)
    return resultDict
end

resultDict = testResult(resultPath)

# Compare JuMP and Mosel
tolerance = 1.0e-3

@assert (resultDict["year_one_energy_cost"] - Year1EnergyCost) / max(Year1EnergyCost, 1) < tolerance
@assert (resultDict["year_one_demand_cost"] - Year1DemandCost) / max(Year1DemandCost, 1) < tolerance
@assert (resultDict["year_one_demand_tou_cost"] - Year1DemandTOUCost) / max(Year1DemandTOUCost, 1) < tolerance
@assert (resultDict["year_one_demand_flat_cost"] - Year1DemandFlatCost) / max(Year1DemandFlatCost, 1) < tolerance
@assert (resultDict["year_one_fixed_cost"] - Year1FixedCharges) / max(Year1FixedCharges, 1) < tolerance
@assert (resultDict["year_one_bill"] - Year1Bill) / max(Year1Bill, 1) < tolerance

println("\nOK")
