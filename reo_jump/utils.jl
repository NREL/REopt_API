#=
reo_struct:
- Julia version: 1.0.3
- Author: Josiah
- Date: 2019-04-16
=#

using JSON
using Revise

function importData(path)
    open(path) do file
        JSON.parse(read(file, String))
    end
end
