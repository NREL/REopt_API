#=
reo_struct:
- Julia version: 1.0.3
- Author: Josiah
- Date: 2019-04-16
=#

using JSON
using Revise

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

function jsonToVariable(path::String="./all_data_new.json")
    JSON = importDict(path)
    for (dat, dic) in JSON
        for (k,v) in dic
            var = Symbol(k)
            try
                if v[1] isa Number || v[1] isa Array
                    #println("this is a number or array: $var")
                    globalInit(var, v)
                elseif v[1] isa String
                    v = strToSym(v)
                    #println("this is string: $var")
                    globalInit(var, v)
                end
            catch y
                println("seems like a catch $y with $var of type $v")
                #println(var, " ", v)
            end
        end
    end
end



#jsonToVariable("reo_jump/all_data_new.json")

#function jsonToVariable()
