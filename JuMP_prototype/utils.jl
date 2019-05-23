import JSON
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

# Build Scenario from JSON
function jsonToVariable(path)
    JSON = importDict(path)
    for (dat, dic) in JSON
        for (k,v) in dic
            var = Symbol(k)
            try
                if v[1] isa Number || v[1] isa Array
                    #println(var)
                    globalInit(var, v)
                elseif v[1] isa String
                    v = strToSym(v)
                    globalInit(var, v)
                end
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
                        floatLine = parse(Float64, line)
                        push!(data, floatLine)
                    catch
                        #println("can't parse ", line, " into Float")
                        push!(data, line)
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
            if data[1] isa Number || data[1] isa Array
                #println(var)
                globalInit(var, data)
            elseif data[1] isa String
                data = strToSym(data)
                globalInit(var, data)
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

function parameter(set, data)
    shapedData = reshape(data, length(set))
    return AxisArray(shapedData, set)
end
