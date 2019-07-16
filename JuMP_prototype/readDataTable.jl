using DelimitedFiles

f = open("data/data_table.md")
lines = readlines(f)

tableArray = Array{String}(undef, 0, 7)

header = true
headLine = false

for line in lines
    global header
    global headLine
    global tableArray
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

if length(ARGS) < 2
    println("\nnot enough input arguments")
    println("julia runTest.jl <vlaue> <type>")
    value = "1"
    type = "no"
else
    value = ARGS[1]
    type = ARGS[2]
end

if type != "uuid"
    rowidx = findall(x->x==type, colName)[1]
    colidx = findall(x->x==value, tableArray[rowidx, :])[1]
    uuid = tableArray[3, colidx]
end

println("using $uuid")

