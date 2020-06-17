using Pkg

Pkg.activate("julia_envs/Xpress")
Pkg.instantiate()

using PackageCompiler

# must point pycall to the python path we want it to use
ENV["PYTHON"] = joinpath(pwd(), "env", "bin", "python")
println("Python path for PyCall: ", ENV["PYTHON"])
Pkg.build("PyCall")

include(joinpath("..", "..", "reo", "src", "reopt_xpress_model.jl"))
include(joinpath("..", "..", "reo", "src", "reopt.jl"))


if Sys.islinux()
    ext = ".so"
elseif Sys.isapple()
    ext = ".dylib"
elseif Sys.iswindows()
    ext = ".dll"
else
    error("Unsupported operating system")
end

PackageCompiler.create_sysimage(
    [:AxisArrays, :JuMP, :MathOptInterface, :PyCall, :Xpress, :MutableArithmetics],
    sysimage_path=joinpath("julia_envs", "Xpress", "JuliaXpressSysimage" * ext)
)
