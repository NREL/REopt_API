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

@info "pwd: " pwd()
mi = JSON.parsefile(joinpath("julia_envs", "Xpress", "modelinputs.json"))

Pkg.build("PyCall")
Pkg.build("Xpress")

# somehow changing working dir during the image build?
include(joinpath("..", "..", "reo", "src", "reopt_xpress_model.jl"))
include(joinpath("..", "..", "reo", "src", "reopt.jl"))

model = reopt_model(300)
results = reopt(model, mi)
