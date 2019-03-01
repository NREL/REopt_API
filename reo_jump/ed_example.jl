#=
ed_example:
- Julia version: 1.0.3
- Author: reopt
- Date: 2019-01-12
=#

using JuMP
using Cbc
using GLPK
using MathOptInterface
using Interact

const MOI = MathOptInterface

# defining constants
const g_max = [1000,1000];
# Minimum power output of generators
const g_min = [0,300];
# Incremental cost of generators
const c_g = [50,100];
# Fixed cost of generators
const c_g0 = [1000,0]
# Incremental cost of wind generators
const c_w = 50;
# Total demand
const d = 1500;
# Wind forecast
const w_f = 200;

# In this cell we create  function solve_ed, which solves the economic dispatch problem for a given set of input parameters.
function solve_ed(g_max, g_min, c_g, c_g0, c_w, d, w_f)

    #Define the economic dispatch (ED) model
    ed=Model(solver = CbcSolver())

    # Define decision variables
    @variable(ed, 0 <= g[i=1:2] <= g_max[i]) # power output of generators
    @variable(ed, 0 <= w  <= w_f ) # wind power injection

    # Define the objective function
    @objective(ed,Min,sum(c_g[i] * g[i] for i in 1:2)+ c_w * w)

    # Define the constraint on the maximum and minimum power output of each generator
    for i in 1:2
        @constraint(ed,  g[i] <= g_max[i]) #maximum
        @constraint(ed,  g[i] >= g_min[i]) #minimum
    end

    # Define the constraint on the wind power injection
    @constraint(ed, w <= w_f)

    # Define the power balance constraint
    @constraint(ed, sum(g[i] for i in 1:2) + w == d)

    # Solve statement
    solve(ed)

    # return the optimal value of the objective function and its minimizers
    return JuMP.getvalue(g), JuMP.getvalue(w), w_f-JuMP.getvalue(w), JuMP.getobjectivevalue(ed)
end

# Solve the economic dispatch problem
(g_opt,w_opt,ws_opt,obj)=solve_ed(g_max, g_min, c_g, c_g0, c_w, d, w_f);

println("\n")
println("Dispatch of Generators: ", g_opt[1:2], " MW")
println("Dispatch of Wind: ", w_opt, " MW")
println("Wind spillage: ", w_f-w_opt, " MW")
println("\n")
println("Total cost: ", obj, "\$")
