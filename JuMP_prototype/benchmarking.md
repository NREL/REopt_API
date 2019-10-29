Benchmarking for speed-ups
==========================


We are trying to beat:

```
Before Anything (data/Runeda919d6-1481-4bf9-a531-a1b3397c8c67)
Load Data:             8.748646 seconds (13.73 M allocations: 646.356 MiB, 2.47% gc time)
Initialize variables:  3.556285 seconds (9.14 M allocations: 402.624 MiB, 12.46% gc time)
const1 Block:          9.216795 seconds (19.03 M allocations: 837.160 MiB, 7.25% gc time)
const2 Block:          1.347799 seconds (2.08 M allocations: 103.366 MiB, 29.24% gc time)
const3 Block:          4.101646 seconds (10.25 M allocations: 418.073 MiB, 18.16% gc time)
const4 Block:          2.679856 seconds (5.19 M allocations: 230.929 MiB, 8.63% gc time)
const5 Block:          3.588232 seconds (6.82 M allocations: 244.122 MiB, 7.63% gc time)
outputs Block:         1.276189 seconds (3.55 M allocations: 106.331 MiB, 7.75% gc time)
Model built. Moving on to optimization...
 61.169886 seconds (84.52 M allocations: 3.685 GiB, 6.77% gc time)
```

The first thing we are going to try is changing the parameter datatypes from
AxisArrays to dictionaries. I am not sure how well this will go given the
follwing benchmark outputs


```julia
julia> @benchmark ProdFactorDic[(:UTIL1, Symbol("1R"), 8760)]
BenchmarkTools.Trial:
  memory estimate:  64 bytes
  allocs estimate:  2
  --------------
  minimum time:     266.525 ns (0.00% GC)
  median time:      272.601 ns (0.00% GC)
  mean time:        356.814 ns (16.17% GC)
  maximum time:     104.442 μs (99.70% GC)
  --------------
  samples:          10000
  evals/sample:     326

julia> @benchmark ProdFactorAA[:UTIL1, Symbol("1R"), 8760]
BenchmarkTools.Trial:
  memory estimate:  0 bytes
  allocs estimate:  0
  --------------
  minimum time:     123.587 ns (0.00% GC)
  median time:      125.170 ns (0.00% GC)
  mean time:        130.469 ns (0.00% GC)
  maximum time:     480.183 ns (0.00% GC)
  --------------
  samples:          10000
  evals/sample:     900
```

These results lead me to believe that the AxisArrays are faster, but if we try
on a smaller sample we get different results for the dictionaries.

```julia
julia> testdict[(1,7,6)] = "asdfag"
"asdfag"

julia> @benchmark testdict[(1,7,6)]
BenchmarkTools.Trial:
  memory estimate:  0 bytes
  allocs estimate:  0
  --------------
  minimum time:     71.659 ns (0.00% GC)
  median time:      72.869 ns (0.00% GC)
  mean time:        76.666 ns (0.00% GC)
  maximum time:     402.646 ns (0.00% GC)
  --------------
  samples:          10000
  evals/sample:     973
```

so lets see how it goes...

After switching over to dictionaries as our datatype for parameters we get:

```
Load Data:  18.583608 seconds (14.17 M allocations: 651.323 MiB, 3.22% gc time)
Initialize variables:   3.625026 seconds (9.14 M allocations: 401.223 MiB, 14.66% gc time)
const1 Block:   8.945508 seconds (18.98 M allocations: 817.324 MiB, 8.86% gc time)
const2 Block:   1.018558 seconds (2.16 M allocations: 106.050 MiB, 10.77% gc time)
const3 Block:   4.340205 seconds (11.10 M allocations: 447.966 MiB, 16.59% gc time)
const4 Block:   2.723323 seconds (5.22 M allocations: 231.771 MiB, 10.27% gc time)
const5 Block:   4.145396 seconds (7.71 M allocations: 263.711 MiB, 12.94% gc time)
 59.197179 seconds (83.21 M allocations: 3.617 GiB, 7.44% gc time)
```

Which is remarkably similar. Good to know though.
