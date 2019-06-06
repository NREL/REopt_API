import JSON
import Base.length
import Base.reshape
import AxisArrays.AxisArray
using AxisArrays

# Helper Functions
function importDict(path)
    open(path) do file
        JSON.parse(read(file, String))
    end
end

function strToSym(list)
    symList = []
    for str in list
        push!(symList, Symbol(str))
    end
    return symList
end

function globalInit(variable, value)
    eval(
            :(
              $variable = $value
             )
        )
end

function initWrapper(var, v)
    if v[1] isa Number || v[1] isa Array
        #println(var)
        globalInit(var, v)
    elseif v[1] isa String
        v = strToSym(v)
        globalInit(var, v)
    end
end

# Build Scenario from JSON
function jsonToVariable(path)
    JSON = importDict(path)
    for (dat, dic) in JSON
        for (k,v) in dic
            var = Symbol(k)
            try
                initWrapper(var, v)
            catch y
                #println(y)
                #println(var, " ", v)
            end
        end
    end
end

# Build Scenario from Dat Files
function buildPairs(datfile)
    let pairs = []
        let var = "nothing"
        let data = []
            for line in readlines(datfile)
                if occursin(":", line)
                    splitLine = split(line, ":")
                    var = splitLine[1]
                elseif !occursin("]", line)
                    try
                        intLine = parse(Int64, line)
                        push!(data, intLine)
                    catch
                        try
                            floatLine = parse(Float64, line)
                            push!(data, floatLine)
                        catch
                            #println("can't parse ", line, " into Float")
                            push!(data, line)
                        end
                    end
                end
                if occursin("]", line)
                    pair = [var, data]
                    push!(pairs, pair)
                    var = "nothing"
                    data = []
                end
            end
        end
        end
    return pairs
    end
end

function buildPairsArray(datfile)
    let pairs = []
        let var = "nothing"
        let data = []
            for line in readlines(datfile)
                if occursin(":", line)
                    splitLine = split(line, ":")
                    var = splitLine[1]
                elseif occursin("]", line) && occursin("[", line)
                    arrayCons = [parse(Int64, s) for s in
                                 split(replace(replace(line, "[" => ""), "]" => ""))]
                    push!(data, arrayCons)
                    continue
                end
                if occursin("]", line)
                    pair = [var, data]
                    push!(pairs, pair)
                    var = "nothing"
                    data = []
                end
            end
        end
        end
    return pairs
    end
end


function loadPairs(pairs)
    for (strvar, data) in pairs
        var = Symbol(strvar)
        try
            if length(data) == 1
                initWrapper(var, data[1])
            else
                initWrapper(var, data)
            end
        catch y
            println("\n", y, ": for variable name '", var, "'",
                    "\n Initializing as empty array\n")
                globalInit(var, [])
        end
    end
end


function datToVariable(scenarioPath)
    for (root, dirs, files) in walkdir(scenarioPath)
        for f in files
            if !occursin("bau", f) && occursin(".dat", f)
                filePath = joinpath(root, f)
                contents = readlines(filePath)
                if occursin("=", contents[1])
                    eval(Meta.parse(readline(filePath)))
                elseif occursin("[", contents[2])
                    pairArrayArray = buildPairsArray(filePath)
                    loadPairs(pairArrayArray)
                elseif occursin(":", contents[1])
                    pairArray = buildPairs(filePath)
                    loadPairs(pairArray)
                else
                    println("Case not accounted for in dat to var")
                end
                println("Loaded Dat File: ", filePath)
            end
        end
    end
end

# Parse variables in mosel command
function readCmd(path)
    println("\nParameters read from mosel command:\n")
    for char in split(readline(path))
        if occursin("=", char) && !occursin("'", char) && !occursin("-", char)
            parseLine = Meta.parse(char)
            eval(parseLine)
            println(parseLine)
        end
    end
end



# Format Parameters to be called like variables
function paramDataFormatter(setTup::Tuple, data)
    reverseTupleAxis = Tuple([length(set) for set in setTup][end:-1:1])
    shapedData = reshape(data, reverseTupleAxis)
    reverseDataAxis = [length(setTup)+1 - n for n in 1:length(setTup)]
    shapedDataT = permutedims(shapedData, reverseDataAxis)
    return AxisArray(shapedDataT, setTup)
end

function parameter(setTup::Tuple, data)
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

function parameter(setTup::Tuple{Array{Symbol,1},UnitRange{Int64}}, data::Number)
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
    return Dict(index[1] => data)
end

# Output Benchmarking

function testOutput()
    ExportedElecPV = AffExpr(0)
    
    for t in Tech, LD in Load, ts in TimeStep, s in Seg, fb in FuelBin 
        if TechToTechClassMatrix[t, :PV] == 1 && (LD == Symbol("1W") || LD == Symbol("1X"))
            y = AffExpr(0, dvRatedProd[t,LD,ts,s,fb] => ProdFactor[t,LD,ts] * LevelizationFactor[t] *  TimeStepScaling)
            add_to_expression!(ExportedElecPV, y)
        end
    end
    return value(ExportedElecPV)
end


function testOutput2()
    ExportedElecPV = 0
    
    for t in Tech, LD in Load, ts in TimeStep, s in Seg, fb in FuelBin 
        if TechToTechClassMatrix[t, :PV] == 1 && (LD == Symbol("1W") || LD == Symbol("1X"))
            ExportedElecPV += value(dvRatedProd[t,LD,ts,s,fb] * ProdFactor[t,LD,ts] * LevelizationFactor[t] *  TimeStepScaling)
        end
    end
    return ExportedElecPV
end
