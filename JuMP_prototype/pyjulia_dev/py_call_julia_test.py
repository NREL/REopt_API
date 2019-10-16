import julia
# julia.install()
import time
import sys
# from py_call_julia_test import call_julia_func

def array_of_techs(array, techs):
    tech_symbols = str([":"+t for t in techs])
    str_array = "[" + " ".join([str(l) for l in array]) + "]"
    a = "AxisArray({:s}, 1:{:d}, Axis{{:Tech}}({:s}))".format(
        str_array, len(techs), tech_symbols
    )
    return a

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
    j.eval("mock_reopt(AxisArray([[1, 2.1] [2, 1.1]], 1:2, Axis{:Tech}([:pv,:util])))")
    """
    The above 'eval' runs successfully, but will require creating a gigantic
    string for all of the values to be passed to Julia.
    """
    elapsed = time.time() - t0
    print("... took {0:.3f} seconds.".format(elapsed))


if __name__ == "__main__":
    techs = ["util", "pv"]
    array = [[1]*35040]*10 # using list of lists as array since that is what dfm uses
    a = array_of_techs(array, techs)
    print("Size of array = {}".format((len(array[0]), len(array))))
    print("Memory of array = {} MB.".format(sys.getsizeof(array) / 1e6))
    print("Memory of string = {} MB.".format(sys.getsizeof(a) / 1e6))

"""
Compare speed of methods:
1. Create strings from python list of lists with Julia type info, pass to julia via j.eval
2. Write out python values and read in with type info in julia
3. Pass as dicts or other? to Julia, convert in Julia
"""
