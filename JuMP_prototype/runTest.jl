import JSON
using DelimitedFiles

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

    if length(ARGS) == 2
        input_value = ARGS[1]
        input_type = ARGS[2]
    else
        input_value = v
        input_type = t
    end

    if input_type != "uuid"
        rowidx = findall(x->x==input_type, colName)[1]
        colidx = findall(x->x==input_value, tableArray[rowidx, :])[1]
        uuid = tableArray[3, colidx]
    end

    println("using $uuid")
    return uuid
end

function runTest(v::String, t::String)
    uuid = readDataTable(v::String, t::String)
    global uuid

    @time include("reopt.jl")
    
    # Parse REopt results
    resultPath = dataPath * "/Outputs/REopt_results.json"
    resultDict = JSON.parsefile(resultPath)

    # Compare JuMP and Mosel
    tolerance = 1.0e-3

    try
        @assert (resultDict["year_one_energy_cost"] - Year1EnergyCost) / max(Year1EnergyCost, 1) < tolerance
        @assert (resultDict["year_one_demand_cost"] - Year1DemandCost) / max(Year1DemandCost, 1) < tolerance
        @assert (resultDict["year_one_demand_tou_cost"] - Year1DemandTOUCost) / max(Year1DemandTOUCost, 1) < tolerance
        @assert (resultDict["year_one_demand_flat_cost"] - Year1DemandFlatCost) / max(Year1DemandFlatCost, 1) < tolerance
        @assert (resultDict["year_one_fixed_cost"] - Year1FixedCharges) / max(Year1FixedCharges, 1) < tolerance
        @assert (resultDict["year_one_bill"] - Year1Bill) / max(Year1Bill, 1) < tolerance
        
        println("\nOK")
        uuid = nothing
        return true
    catch e
        @warn (e)
        uuid = nothing
        return false
    end
end

