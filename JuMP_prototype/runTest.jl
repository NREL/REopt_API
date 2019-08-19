import JSON
using DelimitedFiles
using JuMP

function readDataTable(v::String, t::String)
    f = open("data/data_table.md")
    lines = readlines(f)
    tableArray = Array{String}(undef, 0, 7)
    header = true
    headLine = false

    for line in lines
        global colName

        if header
            line = replace(line, " " => "")
            line = split(line, '|')
            tableArray = line
            colName = line[2:4]
            header = false
            headLine = true
        elseif headLine
            headLine = false
        else
            line = replace(line, " " => "")
            line = split(line, '|')
            tableArray = hcat(tableArray, line)
        end 
    end

    tableArray = tableArray[2:4, 2:end]

    input_value = v
    input_type = t

    if input_type != "uuid"
        rowidx = findall(x->x==input_type, colName)[1]
        colidx = findall(x->x==input_value, tableArray[rowidx, :])[1]
        uuid = tableArray[3, colidx]
    end

    println("using $uuid")
    return uuid
end

"""
    runTest(v::String, t::String)

Compare JuMP results with Mosel results.
Argument options are in JuMP_prototype/data/data_table

# Examples
```julia-repl
julia> runTest("1", "no")
using 76168a37-a78b-4ef3-bdb8-a2f8b213430b
    .
    . test continues
    .
```
```julia-repl
julia> runTest("PV+storage", "name")
using 8ff29780-4e1b-4aca-b079-1342ea21bde2
    .
    . test continues
    .
```
```julia-repl
julia> runTest("PV + storage", "name")
ERROR: remove spaces from <v> input_value
```
```julia-repl
julia> runTest("eda919d6-1481-4bf9-a531-a1b3397c8c67", "uuid")
using eda919d6-1481-4bf9-a531-a1b3397c8c67
    .
    . test continues
    .
```
"""
function runTest(v::String, t::String)
    uuid = readDataTable(v::String, t::String)
    global uuid

    @time include("reopt.jl")
    
    # Parse REopt results
    resultPath = dataPath * "/Outputs/REopt_results.json"
    resultDict = JSON.parsefile(resultPath)

    # Compare JuMP and Mosel
    tolerance = 0.01
    bigtol = 0.05

    try
        @assert (resultDict["lcc"] - ojv) / max(ojv, 1) < tolerance
        @assert (resultDict["year_one_energy_cost"] - Year1EnergyCost) / max(Year1EnergyCost, 1) < bigtol
        @assert (resultDict["year_one_demand_cost"] - Year1DemandCost) / max(Year1DemandCost, 1) < bigtol
        @assert (resultDict["year_one_demand_tou_cost"] - Year1DemandTOUCost) / max(Year1DemandTOUCost, 1) < bigtol
        @assert (resultDict["year_one_demand_flat_cost"] - Year1DemandFlatCost) / max(Year1DemandFlatCost, 1) < bigtol
        @assert (resultDict["year_one_fixed_cost"] - Year1FixedCharges) / max(Year1FixedCharges, 1) < bigtol
        @assert (resultDict["year_one_bill"] - Year1Bill) / max(Year1Bill, 1) < bigtol
        
        println("\nOK")
        uuid = nothing
        return true
    catch e
        @warn (e)
        uuid = nothing
        return false
    end
end

