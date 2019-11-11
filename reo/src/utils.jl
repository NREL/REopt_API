import Base.length
import Base.reshape
import AxisArrays.AxisArray
using JLD2
using JuMP
using AxisArrays

jumpex(m::JuMP.AbstractModel) = JuMP.GenericAffExpr{Float64, JuMP.variable_type(m)}()

# Helper Functions
function strToSym(list)
    symList = Array{Symbol}(undef, 0)
    for str in list
        push!(symList, Symbol(str))
    end
    return symList
end

macro globalInit(variable, value)
    e=Expr(:(=), variable, Meta.parse(value))
    return esc(e)
end

function globalInit(variable, value)
    eval(
            :(
              $variable = $value
             )
        )
end

function initWrapper(var, v)
    if v isa String
        v = strToSym([v])
        globalInit(var, v)
    elseif v[1] isa Number || v[1] isa Array
        #println(var)
        globalInit(var, v)
    elseif v[1] isa String
        v = strToSym(v)
        globalInit(var, v)
    end
end

# Format Parameters to be called like variables

function retype(dataAr::AbstractArray, floatbool::Bool=false)
    if length(dataAr) == 0 
        if floatbool
            return Float64[]
        else
            return Int64[]
        end
    end
    
    x = typeof(dataAr[1])
    if x == Int64
        typed = Array{Float64}(undef,0)
        for elem in dataAr
            push!(typed, elem)
        end
        return typed  # could this return convert(Array{Float64}, dataAr) instead?
    else
        typed = Array{x}(undef,0)
        for elem in dataAr  # do we need the for loops?
            push!(typed, elem)
        end
        return typed
    end
end

function retype(val::Union{Float64,Int})
    return val
end


function paramDataFormatter(setTup::Tuple, data::AbstractArray)
    reverseTupleAxis = Tuple([length(set) for set in setTup][end:-1:1])
    shapedData = reshape(data, reverseTupleAxis)
    reverseDataAxis = [length(setTup)+1 - n for n in 1:length(setTup)]
    shapedDataT = permutedims(shapedData, reverseDataAxis)
    return AxisArray(shapedDataT, setTup)
end

function parameter(setTup::Tuple, nondata::AbstractArray)
    data = retype(nondata)
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
