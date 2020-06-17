using Pkg
using PackageCompiler


function build_julia_image(project_path::String)
    
    # cwd = home/deploy ! PyCall not in Project?
    Pkg.activate(joinpath(project_path, "julia_envs", "Xpress"))
    Pkg.instantiate(verbose=true)
    Pkg.add("PackageCompiler")

    # must point pycall to the python path we want it to use
    ENV["PYTHON"] = joinpath(project_path, "env", "bin", "python")
    println("Python path for PyCall: ", ENV["PYTHON"])
    Pkg.build("PyCall")
    Pkg.build("Xpress")

    include(joinpath(project_path, "reo", "src", "reopt_xpress_model.jl"))
    include(joinpath(project_path, "reo", "src", "reopt.jl"))

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
        sysimage_path=joinpath(project_path, "julia_envs", "Xpress", "JuliaXpressSysimage" * ext)
    )
end