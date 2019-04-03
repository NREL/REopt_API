import JSON
import IndexedTables
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
                if v[1] isa Number
                    globalInit(var, v)
                elseif v[1] isa String
                    v = strToSym(v)
                    globalInit(var, v)
                end
            catch
            end
        end
    end
end


function set1param(set1, data)
    tmp1 = []

    for elem1 in set1
        push!(tmp1, elem1)
    end

    return I.ndsparse((tmp1), data)
end

function set2param(set1, set2, data)
    tmp1 = []
    tmp2 = []

    for elem1 in set1
        for elem2 in set2
            push!(tmp1, elem1)
            push!(tmp2, elem2)
        end
    end

    return I.ndsparse((tmp1, tmp2), data)
end

function set3param(set1, set2, set3, data)
    tmp1 = []
    tmp2 = []
    tmp3 = []

    for elem1 in set1
        for elem2 in set2
            for elem3 in set3
                push!(tmp1, elem1)
                push!(tmp2, elem2)
                push!(tmp3, elem3)
            end
        end
    end

    return I.ndsparse((tmp1, tmp2, tmp3), data)
end

function set4param(set1, set2, set3, set4, data)
    tmp1 = []
    tmp2 = []
    tmp3 = []
    tmp4 = []

    for elem1 in set1
        for elem2 in set2
            for elem3 in set3
                for elem4 in set4
                    push!(tmp1, elem1)
                    push!(tmp2, elem2)
                    push!(tmp3, elem3)
                    push!(tmp4, elem4)
                end
            end
        end
    end

    return I.ndsparse((tmp1, tmp2, tmp3, tmp4), data)
end

function set5param(set1, set2, set3, set4, set5, data)
    tmp1 = []
    tmp2 = []
    tmp3 = []
    tmp4 = []
    tmp5 = []

    for elem1 in set1
        for elem2 in set2
            for elem3 in set3
                for elem4 in set4
                    for elem5 in set5
                        push!(tmp1, elem1)
                        push!(tmp2, elem2)
                        push!(tmp3, elem3)
                        push!(tmp4, elem4)
                        push!(tmp5, elem5)
                    end
                end
            end
        end
    end

    return I.ndsparse((tmp1, tmp2, tmp3, tmp4, tmp5), data)
end
