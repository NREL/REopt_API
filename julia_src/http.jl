using HTTP, JSON
include("REopt.jl")

using .REopt

function job(req::HTTP.Request)
    d = JSON.parse(String(req.body))
    timeout = pop!(d, "timeout_seconds")
    tol = pop!(d, "tolerance")
    m = xpress_model(timeout, tol)
    @info "Starting REopt with timeout of $(timeout) seconds..."
    results = reopt(m, d)
    @info "REopt model solved with status $(results["status"])."
    return HTTP.Response(200, JSON.json(results))
end

function health(req::HTTP.Request)
    try
        # xpress_model will fail with stacktrace below once a node has run out of memory
        m = xpress_model(100, 0.01)
        return HTTP.Response(200, JSON.json(Dict("Julia-api"=>"healthy!")))
    catch
        return HTTP.Response(500, JSON.json(Dict("Julia-api"=>"sick!")))
    end
end

# define REST endpoints to dispatch to "service" functions
const ROUTER = HTTP.Router()

HTTP.@register(ROUTER, "POST", "/job", job)
HTTP.@register(ROUTER, "GET", "/health", health)
HTTP.serve(ROUTER, "0.0.0.0", 8081, reuseaddr=true)

"""
┌ Error: error handling request
│   exception =
│    UndefVarError: prob not defined
│    Stacktrace:
│     [1] macro expansion at /root/.julia/packages/Xpress/ab5Cg/src/utils.jl:99 [inlined]
│     [2] createprob(::Base.RefValue{Ptr{Nothing}}) at /root/.julia/packages/Xpress/ab5Cg/src/api.jl:56
│     [3] Xpress.XpressProblem(; logfile::String) at /root/.julia/packages/Xpress/ab5Cg/src/helper.jl:67
│     [4] XpressProblem at /root/.julia/packages/Xpress/ab5Cg/src/helper.jl:66 [inlined]
│     [5] empty!(::Xpress.Optimizer) at /root/.julia/packages/Xpress/ab5Cg/src/MOI/MOI_wrapper.jl:281
│     [6] Xpress.Optimizer(; kwargs::Base.Iterators.Pairs{Symbol,Real,Tuple{Symbol,Symbol,Symbol},NamedTuple{(:MAXTIME, :MIPRELSTOP, :OUTPUTLOG),Tuple{Int64,Float64,Int64}}}) at /root/.julia/packages/Xpress/ab5Cg/src/MOI/MOI_wrapper.jl:271
│     [7] xpress_model(::Int64, ::Float64) at /opt/julia_src/xpress_model.jl:31
│     [8] job(::HTTP.Messages.Request) at /opt/julia_src/http.jl:10
│     [9] handle at /root/.julia/packages/HTTP/cxgat/src/Handlers.jl:254 [inlined]
│     [10] handle(::HTTP.Handlers.RequestHandlerFunction{typeof(job)}, ::HTTP.Streams.Stream{HTTP.Messages.Request,HTTP.ConnectionPool.Transaction{Sockets.TCPSocket}}) at /root/.julia/packages/HTTP/cxgat/src/Handlers.jl:277
│     [11] handle(::HTTP.Handlers.Router{Symbol("##1483")}, ::HTTP.Streams.Stream{HTTP.Messages.Request,HTTP.ConnectionPool.Transaction{Sockets.TCPSocket}}) at /root/.julia/packages/HTTP/cxgat/src/Handlers.jl:467
│     [12] #4 at /root/.julia/packages/HTTP/cxgat/src/Handlers.jl:346 [inlined]
│     [13] macro expansion at /root/.julia/packages/HTTP/cxgat/src/Servers.jl:406 [inlined]
│     [14] (::HTTP.Servers.var"#13#14"{HTTP.Handlers.var"#4#5"{HTTP.Handlers.Router{Symbol("##1483")}},HTTP.ConnectionPool.Transaction{Sockets.TCPSocket},HTTP.Streams.Stream{HTTP.Messages.Request,HTTP.ConnectionPool.Transaction{Sockets.TCPSocket}}})() at ./task.jl:356
└ @ HTTP.Servers ~/.julia/packages/HTTP/cxgat/src/Servers.jl:417


This error is related to the following?

signal (11): Segmentation fault
in expression starting at /opt/julia_src/http.jl:26
unknown function (ip: 0x7f8710dfcf7c)
XPRSdestroyprob at /opt/xpressmp/lib/libxprs.so (unknown line)
XPRSdestroyprob at /root/.julia/packages/Xpress/ab5Cg/src/lib.jl:22 [inlined]
macro expansion at /root/.julia/packages/Xpress/ab5Cg/src/utils.jl:97 [inlined]
destroyprob at /root/.julia/packages/Xpress/ab5Cg/src/api.jl:66
_jl_invoke at /buildworker/worker/package_linux64/build/src/gf.c:2214 [inlined]
jl_apply_generic at /buildworker/worker/package_linux64/build/src/gf.c:2398
jl_apply at /buildworker/worker/package_linux64/build/src/julia.h:1690 [inlined]
run_finalizer at /buildworker/worker/package_linux64/build/src/gc.c:277
jl_gc_run_finalizers_in_list at /buildworker/worker/package_linux64/build/src/gc.c:363
run_finalizers at /buildworker/worker/package_linux64/build/src/gc.c:391 [inlined]
jl_gc_run_all_finalizers at /buildworker/worker/package_linux64/build/src/gc.c:428
jl_atexit_hook at /buildworker/worker/package_linux64/build/src/init.c:245
jl_exit at /buildworker/worker/package_linux64/build/src/jl_uv.c:624
jl_exit_thread0_cb at /buildworker/worker/package_linux64/build/src/signals-unix.c:343
unknown function (ip: (nil))
Allocations: 39536788914 (Pool: 39536002060; Big: 786854); GC: 13742

Root of issue might be multi threading Xpress problems?

Or maybe multithreading HTTP.jl:
[ Info: Xpress: Found license file /opt/xpressmp/bin/xpauth.xpr
[ Info: Xpress: Development license detected.
[ Info: Starting REopt with timeout of 420 seconds...

signal (15): Terminated
in expression starting at /opt/julia_src/http.jl:32
pthread_cond_wait at /lib/x86_64-linux-gnu/libpthread.so.0 (unknown line)
uv_cond_wait at /workspace/srcdir/libuv/src/unix/thread.c:827
jl_task_get_next at /buildworker/worker/package_linux64/build/src/partr.c:509
poptask at ./task.jl:704
wait at ./task.jl:712 [inlined]
task_done_hook at ./task.jl:442
_jl_invoke at /buildworker/worker/package_linux64/build/src/gf.c:2214 [inlined]
jl_apply_generic at /buildworker/worker/package_linux64/build/src/gf.c:2398
jl_apply at /buildworker/worker/package_linux64/build/src/julia.h:1690 [inlined]
jl_finish_task at /buildworker/worker/package_linux64/build/src/task.c:196
jl_threadfun at /buildworker/worker/package_linux64/build/src/partr.c:265
start_thread at /lib/x86_64-linux-gnu/libpthread.so.0 (unknown line)
clone at /lib/x86_64-linux-gnu/libc.so.6 (unknown line)
unknown function (ip: (nil))
_ZN4llvm17ScheduleDAGInstrs14addPhysRegDepsEPNS_5SUnitEj at /usr/local/julia/bin/../lib/julia/libLLVM-9jl.so (unknown line)
_ZN4llvm17ScheduleDAGInstrs15buildSchedGraphEPNS_9AAResultsEPNS_18RegPressureTrackerEPNS_13PressureDiffsEPNS_13LiveIntervalsEb at /usr/local/julia/bin/../lib/julia/libLLVM-9jl.so (unknown line)
_ZN4llvm17ScheduleDAGMILive8scheduleEv at /usr/local/julia/bin/../lib/julia/libLLVM-9jl.so (unknown line)
_ZN12_GLOBAL__N_120MachineSchedulerBase15scheduleRegionsERN4llvm17ScheduleDAGInstrsEb at /usr/local/julia/bin/../lib/julia/libLLVM-9jl.so (unknown line)
_ZN12_GLOBAL__N_116MachineScheduler20runOnMachineFunctionERN4llvm15MachineFunctionE at /usr/local/julia/bin/../lib/julia/libLLVM-9jl.so (unknown line)
_ZN4llvm19MachineFunctionPass13runOnFunctionERNS_8FunctionE at /usr/local/julia/bin/../lib/julia/libLLVM-9jl.so (unknown line)
_ZN4llvm13FPPassManager13runOnFunctionERNS_8FunctionE at /usr/local/julia/bin/../lib/julia/libLLVM-9jl.so (unknown line)
_ZN4llvm13FPPassManager11runOnModuleERNS_6ModuleE at /usr/local/julia/bin/../lib/julia/libLLVM-9jl.so (unknown line)
_ZN4llvm6legacy15PassManagerImpl3runERNS_6ModuleE at /usr/local/julia/bin/../lib/julia/libLLVM-9jl.so (unknown line)
operator() at /buildworker/worker/package_linux64/build/src/jitlayers.cpp:520
addModule at /buildworker/worker/package_linux64/build/usr/include/llvm/ExecutionEngine/Orc/IRCompileLayer.h:93 [inlined]
addModule at /buildworker/worker/package_linux64/build/src/jitlayers.cpp:648
jl_add_to_ee at /buildworker/worker/package_linux64/build/src/jitlayers.cpp:893 [inlined]
jl_add_to_ee at /buildworker/worker/package_linux64/build/src/jitlayers.cpp:955
jl_add_to_ee at /buildworker/worker/package_linux64/build/src/jitlayers.cpp:940
jl_add_to_ee at /buildworker/worker/package_linux64/build/src/jitlayers.cpp:940
jl_add_to_ee at /buildworker/worker/package_linux64/build/src/jitlayers.cpp:940
jl_add_to_ee at /buildworker/worker/package_linux64/build/src/jitlayers.cpp:977 [inlined]
_jl_compile_codeinst at /buildworker/worker/package_linux64/build/src/jitlayers.cpp:126
jl_generate_fptr at /buildworker/worker/package_linux64/build/src/jitlayers.cpp:302
jl_compile_method_internal at /buildworker/worker/package_linux64/build/src/gf.c:1964
jl_compile_method_internal at /buildworker/worker/package_linux64/build/src/gf.c:1919 [inlined]
_jl_invoke at /buildworker/worker/package_linux64/build/src/gf.c:2224 [inlined]
jl_apply_generic at /buildworker/worker/package_linux64/build/src/gf.c:2398
job at /opt/julia_src/http.jl:12
handle at /root/.julia/packages/HTTP/cxgat/src/Handlers.jl:254 [inlined]
handle at /root/.julia/packages/HTTP/cxgat/src/Handlers.jl:277
_jl_invoke at /buildworker/worker/package_linux64/build/src/gf.c:2231 [inlined]
jl_apply_generic at /buildworker/worker/package_linux64/build/src/gf.c:2398
handle at /root/.julia/packages/HTTP/cxgat/src/Handlers.jl:467
#4 at /root/.julia/packages/HTTP/cxgat/src/Handlers.jl:346 [inlined]
macro expansion at /root/.julia/packages/HTTP/cxgat/src/Servers.jl:406 [inlined]
#13 at ./task.jl:356
unknown function (ip: 0x7f1f15cc4a04)
_jl_invoke at /buildworker/worker/package_linux64/build/src/gf.c:2214 [inlined]
jl_apply_generic at /buildworker/worker/package_linux64/build/src/gf.c:2398
jl_apply at /buildworker/worker/package_linux64/build/src/julia.h:1690 [inlined]
start_task at /buildworker/worker/package_linux64/build/src/task.c:705
unknown function (ip: (nil))
unknown function (ip: (nil))
Allocations: 67501077 (Pool: 67478456; Big: 22621); GC: 66
<unknown>:0: error: starting new .cfi frame before finishing the previous one
<unknown>:0: error: starting new .cfi frame before finishing the previous one
<unknown>:0: error: this directive must appear between .cfi_startproc and .cfi_endproc directives
<unknown>:0: error: starting new .cfi frame before finishing the previous one
<unknown>:0: error: this directive must appear between .cfi_startproc and .cfi_endproc directives

signal (11): Segmentation fault
in expression starting at /opt/julia_src/http.jl:32
unknown function (ip: (nil))
_atexit at ./initdefs.jl:316
jfptr__atexit_48210.clone_1 at /usr/local/julia/lib/julia/sys.so (unknown line)
_jl_invoke at /buildworker/worker/package_linux64/build/src/gf.c:2214 [inlined]
jl_apply_generic at /buildworker/worker/package_linux64/build/src/gf.c:2398
jl_apply at /buildworker/worker/package_linux64/build/src/julia.h:1690 [inlined]
jl_atexit_hook at /buildworker/worker/package_linux64/build/src/init.c:230
jl_exit at /buildworker/worker/package_linux64/build/src/jl_uv.c:624
jl_exit_thread0_cb at /buildworker/worker/package_linux64/build/src/signals-unix.c:343
unknown function (ip: (nil))
Allocations: 67501077 (Pool: 67478456; Big: 22621); GC: 66

"""