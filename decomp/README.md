# REopt Decompostion Prototype

We will use this directory to prototype the decomposition of REopt. I have
effectivly neutered the api to only generate JLD files with the data we need to
run the model outside of the api using `reopt.jl` and`reopt_slow.jl` found in
this script.

## Usage

We are using Julia 1.2.0 for all of the opensource code right now. It is ideal
for you to be using that same version.

> NOTE: All of these command assume that you are in this directory

## Notes on Julia

When launching a Julia REPL you should use the command:

``` bash
julia --project
```

This will activate the julia environment in the `Project.toml` and
`Manifest.toml` files in this directory.

The first time you run things you will need to install all of the necesary
packages. To install all of the packages described in the environment files run:

``` julia
using Pkg; Pkg.instantiate()
```

### reopt\_slow.jl

The reason this is called `reopt_slow.jl` is because it does not follow best
practices of writing julia code, but allows us full access to the model
information. Basically, it is much easier to query data and results for trouble
shooting. Ideally, we will make most of the changes here then modify things
slightly to be put into `reopt.jl` to run more extensive testing. To run this
script you will just need to run:

``` julia
include("reopt_slow.jl")
```

You can then use the `value()` function to query decision variables and
`p.<parameter>` to query parameter and set data.

### reopt.jl

When you start a new julia session you will need to load the `reopt.jl` script
with, while in this directory:

``` julia
include("reopt.jl")
```

This script allows you to run individual scenarios from the `data` directroy
using:

``` julia
reopt("data/<scenario>")
```

replacing `<scenario>` with one of the data files in the `data/` directory. You
can also run all of the scenarios in the data directory with:

``` julia
run_all_scenarios()
```
