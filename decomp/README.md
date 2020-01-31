REopt Decompostion Prototype
============================

We will use this directory to prototype the decomposition of REopt. I have
effectivly neutered the api to only generate JLD files with the data we need to
run the model outside of the api using `reopt.jl` found in this script. This is
a work in progess and here are the things we need to do:

-   [ ] Address problems generating data with hybrid wind systems
-   [ ] Generate data sets that have incentive structure logic in them
-   [ ] Implement decompostion in standard REopt
    -   [ ] Benchmark tiered scenarios to show the speedups achieved
-   [ ] Add CHP to decompostion
    -   [ ] Benchmark with hard CHP cases
