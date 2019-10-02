import julia
julia.install()
import time
# from py_call_julia_test import call_julia_func

def call_julia_func():
    dvRatedProd = dict(
        util=[1,2,3,4.3],
        pv=[1,2,3,4.3],
    )

    print("starting julia ...")
    t0 = time.time()
    j = julia.Julia()
    elapsed = time.time() - t0
    print("... took {0:.3f} seconds.".format(elapsed))

    print("calling julia_func.jl ...")
    t0 = time.time()
    j.include("julia_func.jl")
    # j.mock_reopt(dvRatedProd)
    j.eval("mock_reopt(AxisArray([[1; 2.1] [2; 1.1]], 1:2, Axis{:Tech}([:pv,:util])))")
    """
    The above 'eval' runs successfully, but will require creating a gigantic
    string for all of the values to be passed to Julia.
    """
    elapsed = time.time() - t0
    print("... took {0:.3f} seconds.".format(elapsed))
