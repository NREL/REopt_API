using Pkg
using PackageCompiler


function build_julia_image(project_path::String)

    Pkg.activate(joinpath(project_path, "julia_envs", "Xpress"))
    Pkg.instantiate(verbose=true)

    # must point pycall to the python path we want it to use
    ENV["PYTHON"] = joinpath(project_path, "env", "bin", "python")
    ENV["PROJECT_PATH"] = project_path

    # TODO create REopt module to attach to Base for system image
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
        sysimage_path=joinpath(project_path, "julia_envs", "Xpress", "JuliaXpressSysimage" * ext),
        precompile_execution_file=joinpath(project_path, "julia_envs", "Xpress", "precompile.jl")
    )
end