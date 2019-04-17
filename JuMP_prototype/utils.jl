import JSON
import IndexedTables
using AxisArrays
const I = IndexedTables

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
    end
end

function parameter(set, data)
    shapedData = reshape(data, length(set))
    return AxisArray(shapedData, set)
end
