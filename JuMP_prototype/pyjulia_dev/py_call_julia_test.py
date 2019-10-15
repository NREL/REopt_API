import julia
julia.install()
import time
# from py_call_julia_test import call_julia_func

default = 10000

def call_julia_func(n=default):
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

    datastr = '{}'.format(n * [0.0]).replace(',', '')
    #print("mock_reopt(AxisArray([{} {}], 1:{}, Axis{{:Tech}}([:pv,:util])))".format(datastr,datastr,n))
    j.eval("mock_reopt(AxisArray([{}; {}], Axis{{:Tech}}([:pv,:util]), 1:{}))".format(datastr,datastr,n))
    """
    The above 'eval' runs successfully, but will require creating a gigantic
    string for all of the values to be passed to Julia.
    """
    elapsed = time.time() - t0
    print("... took {0:.3f} seconds.".format(elapsed))

def pass_array_julia(n=default):

    data = [0.0] * 2 * n

    print("starting julia ...")
    t0 = time.time()
    j = julia.Julia()
    elapsed = time.time() - t0
    print("... took {0:.3f} seconds.".format(elapsed))

    print("calling julia_func.jl ...")
    t0 = time.time()
    j.include("julia_func.jl")

    j.mock_reopt(data, n)
    """
    The above 'eval' runs successfully, but will require creating a gigantic
    string for all of the values to be passed to Julia.
    """
    elapsed = time.time() - t0
    print("... took {0:.3f} seconds.".format(elapsed))
