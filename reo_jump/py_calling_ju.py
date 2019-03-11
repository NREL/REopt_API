import julia
import julia.Base
from julia.Base import Enums    # import a submodule
from julia.Base import sin      # import a function from a module
from julia import Main

j = julia.Julia()

j.include("ed_example.jl")

Main.g_max = [1000,1000];
# Minimum power output of generators
Main.g_min = [0,300];
# Incremental cost of generators
Main.c_g = [50,100];
# Fixed cost of generators
Main.c_g0 = [1000,0]
# Incremental cost of wind generators
Main.c_w = 50;
# Total demand
Main.d = 1500;
# Wind forecast
Main.w_f = 200;

#(g_opt,w_opt,ws_opt,obj)= j.eval("solve_ed(g_max, g_min, c_g, c_g0, c_w, d, w_f)")
(w_opt,ws_opt,obj)= j.eval("solve_ed(g_max, g_min, c_g, c_g0, c_w, d, w_f)")

print("\n")
#print("Dispatch of Generators: ", g_opt[1:2], " MW")
print("Dispatch of Wind: ", w_opt, " MW")
print("Wind spillage: ", Main.w_f-w_opt, " MW")
print("\n")
print("Total cost: ", obj, "$")
print("\n")