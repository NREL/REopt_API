using JuMP
using AxisArrays
using MathOptInterface
using AxisArrays
using LinearAlgebra
using MutableArithmetics
using Printf
using Pkg
using JSON
using Logging

@info pwd()
mi = JSON.parsefile(joinpath(ENV["PROJECT_PATH"], "julia_envs", "Xpress", "modelinputs.json"))

Pkg.build("PyCall")
Pkg.build("Xpress")

# somehow changing working dir during the image build?
include(joinpath(ENV["PROJECT_PATH"], "reo", "src", "reopt_xpress_model.jl"))
include(joinpath(ENV["PROJECT_PATH"], "reo", "src", "reopt.jl"))

model = reopt_model(300, 0.001, 3)
results = reopt(model, mi)
