using AxisArrays

T = 3
TimeSteps = range(1, stop=T)
techs=[:util, :pv]
n_techs = length(techs)

function mock_reopt(dvRatedProd::AxisArray{Float64, n_techs, Array{Float64, n_techs},
                                           Tuple{Axis{:row, UnitRange{Int64}}, Axis{:Tech, Array{Symbol,1}}}
                                           }
                   )
    println("success")
    println(typeof(dvRatedProd))
end


# d=Dict(:util=>[1,2.1], :pv=>[1.2,1])
#
# a=AxisArray([[1; 2.1] [2; 1.1]], 1:2, Axis{:Tech}([:pv,:util]))
