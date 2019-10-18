using AxisArrays
import InteractiveUtils.@code_warntype

techs=[:util, :pv]
n_techs = length(techs)

function mock_reopt(dvRatedProd::AxisArray{Float64, n_techs, Array{Float64, n_techs},
                                           Tuple{Axis{:row, UnitRange{Int64}}, Axis{:Tech, Array{Symbol,1}}}
                                           }
                   )
    println("success")
    println(typeof(dvRatedProd))
end

function mock_reopt(dvRatedProd::AxisArray{Float64, n_techs, Array{Float64, n_techs},
                                           Tuple{Axis{:Tech, Array{Symbol,1}}, Axis{:col, UnitRange{Int64}}}
                                           }
                   )
    println("success")
    println(typeof(dvRatedProd))
end

function mock_reopt(dvRatedProd::Array{Float64, 1}, n::Int64)
    TimeSteps=1:n
    setTup = (techs, TimeSteps)
    data =  dvRatedProd
    reverseTupleAxis = Tuple([length(set) for set in setTup][end:-1:1])
    shapedData = reshape(data, reverseTupleAxis)
    reverseDataAxis = [length(setTup)+1 - n for n in 1:length(setTup)]
    shapedDataT = permutedims(shapedData, reverseDataAxis)
    x = AxisArray(shapedDataT, setTup)
    println("success")
    println(typeof(x))
end

# d=Dict(:util=>[1,2.1], :pv=>[1.2,1])
#
# a=AxisArray([[1; 2.1] [2; 1.1]], 1:2, Axis{:Tech}([:pv,:util]))
