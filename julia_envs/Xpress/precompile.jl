using JuMP
using AxisArrays
using MathOptInterface
using AxisArrays
using LinearAlgebra
using MutableArithmetics
using Printf
using Pkg

Pkg.build("PyCall")
Pkg.build("Xpress")

include(joinpath("..", "..", "reo", "src", "reopt_xpress_model.jl"))
include(joinpath("..", "..", "reo", "src", "reopt.jl"))

# TODO run_reopt