module GHPGHX
# -------
export ghp_model
export get_ghpghx_results_for_reopt

include("ghpghx_inputs.jl")

include("ghpghx_results.jl")

function ghp_model(d)
    # Load parameters and process from input Dict, to create instance of type InputsStruct
    p = InputsProcess(d)

    # Run size_borefield for each attempt to SOLVE
    results = size_borefield(p)

    return results, p
end

function size_borefield(p)
    # Declare and initialize arrays which get passed and mutated by GHX model (different length arrays used for different models)
    INFO = zeros(Int32, 15)  # Used for initialization and incrementing the number of times the GHX model is called by timestep
    if p.ghx_model == "DST"
        PAR = zeros(Float64, 112)  # Only changed by assign_PAR! each sizing iteration for ResultsStruct variables
        XIN = zeros(Float64, 5)  # Key inputs passed from GHP calcs to the GHX model (T_in, Mdot_in, T_amb)
        OUT = zeros(Float64, 29)  # Outputs from the GHX model to go into the GHP calcs - most notably OUT[1] = Tout_GHX
    end
    if p.ghx_model == "TESS"
        PAR = zeros(Float64, 32)  # Only changed by assign_PAR! each sizing iteration for ResultsStruct variables
        XIN = zeros(Float64, 4)  # Key inputs passed from GHP calcs to the GHX model (T_in, Mdot_in, T_amb)
        OUT = zeros(Float64, 12)  # Outputs from the GHX model to go into the GHP calcs - most notably OUT[1] = Tout_GHX
    end

    # Define TimeArray; TimeArray[1] varies with time, and TimeArray[4] varies for TESS GHX model with variable time step per hour
    Time0 = 0.0
    Time = Time0
    Tfinal = 8760 * p.simulation_years
    Delt = 1.0 / p.dst_ghx_timesteps_per_hour  # This gets overwritten for TESS GHX model for each hour
    TimeArray = [Time, Time0, Tfinal, Delt]
    
    # Initial sizing guess and initialize ResultsStruct
    X_Now::Array{Float64, 1} = zeros(p.max_sizing_iterations + 1)
    FX_Now::Array{Float64, 1} = zeros(p.max_sizing_iterations + 1)
    N_Bores::Array{Float64, 1} = zeros(p.max_sizing_iterations + 1)

    # Initial size guess for first sizing iteration
    size_iter = 1
    X_Now[size_iter] = p.X_init

    r = ResultsStruct(X_Now = X_Now, FX_Now = FX_Now, N_Bores = N_Bores, 
                        total_hours = p.simulation_years * 8760)
    init_sizing!(r, p, size_iter)  # Only modifies r, not p
    
    #Set the parameters for the ground model
    assign_PAR!(p, r, PAR, size_iter)

    # Instantiate TESS GHX storage/save variables
    #tess_save = TESSStruct()

    # Initialize GHX model with 2 calls
    #init_ghx_calls_2x!(p, TimeArray, XIN, OUT, PAR, INFO, tess_save)
    init_ghx_calls_2x!(p, TimeArray, XIN, OUT, PAR, INFO)

    ###   LOOP THROUGH FOR EACH SIZING ITERATION UNTIL "break" or reaching max iterations   ###
    while size_iter <= p.max_sizing_iterations
        println("size_iter = ", size_iter)
        # Initialize/reset and update variables (already done for first iteration above)
        if size_iter > 1
            r = ResultsStruct(X_Now = r.X_Now, FX_Now = r.FX_Now, N_Bores = r.N_Bores, 
                                total_hours = p.simulation_years * 8760)
            init_sizing!(r, p, size_iter)  # Only modifies r, not p
            assign_PAR!(p, r, PAR, size_iter)
            init_ghx_calls_2x!(p, TimeArray, XIN, OUT, PAR, INFO)
        end
        println("X_Now = ", r.X_Now[size_iter])
        println("N_bores = ", r.N_Bores[size_iter])
        for year in 1:p.simulation_years
            println("  ",OUT[1],"  ")
            #println("Time = ", TimeArray[1])  # This has some interesting small decimal place behavior (from Fortran?)
            for hr in 1:8760  # TESS model has hourly-based timesteps per hour
                Q_Heat = p.HeatingThermalLoadKW[hr] * 3600.0  # Convert kW to kJ/hr
                Q_Cool = p.CoolingThermalLoadKW[hr] * 3600.0  # Convert kW to kJ/hr
                # Find time step per hour based on flow rate
                Tons_HeatPump_H = Q_Heat / 1.055 / 12000.0
                Tons_HeatPump_C = Q_Cool / 1.055 / 12000.0
                GPM_GHX = max(p.fMin_VSP_GHXPump * p.GPM_GHXPump, (Tons_HeatPump_H + Tons_HeatPump_C) * p.GPMperTon_WSHP)
                Mdot_GHX = GPM_GHX * 60.0 / 264.172 * p.Rho_GHXFluid
                Mdot_Circuit = Mdot_GHX / r.N_Bores[size_iter] * p.N_Series
                Circuit_Time = r.Mass_Circuit / max(0.001, Mdot_Circuit)
             
                # TESS GHX model, Model = 3, uses variable time step per hour; DST uses fixed p.dst_ghx_timesteps_per_hour
                if p.ghx_model == "TESS"
                   N_Steps_ThisHour = max(p.tess_ghx_minimum_timesteps_per_hour, convert(Int64, floor(1.0 / Circuit_Time)) + 1)
                else
                   N_Steps_ThisHour = p.dst_ghx_timesteps_per_hour
                end

                for step in 1:N_Steps_ThisHour
                    Delt = 1 / N_Steps_ThisHour
                    if year == 1 && hr == 1 && step == 1
                        TimeArray[1] = 0.0  # Reset time to 0; especially important for initialization in GHX model
                    else
                        TimeArray[1] += Delt
                    end
                    TimeArray[4] = Delt
                    INFO[7] = 0
                    INFO[8] += 1
                    Tout_GHX = OUT[1]  # [C] This is always OUT[1] for ANY GHX model, but if that changes need to update                  
                    EWT_F = Tout_GHX * 1.8 + 32.0  # [F] 
                    # Find COP_Heat (Col 2) and COP_Cool (Col 3) based on temperature (Col 1) map; use interpolation between data points
                    if EWT_F <= p.HeatPumpCOPMap[1, 1]
                        COP_Heat = p.HeatPumpCOPMap[1, 2]
                        COP_Cool = p.HeatPumpCOPMap[1, 3]
                    elseif EWT_F > p.HeatPumpCOPMap[end, 1]
                        COP_Heat = p.HeatPumpCOPMap[end, 2]
                        COP_Cool = p.HeatPumpCOPMap[end, 3]            
                    else
                        # Loop over all temperature points in p.HeatPumpCOPMap, but break out of loop if it is found
                        for (index, tmp) in enumerate(p.HeatPumpCOPMap[2:end, 1])  # Omit first and last temp checks, done above
                            if EWT_F > p.HeatPumpCOPMap[index, 1] && EWT_F <= tmp  # "index" starts at 1, not 2, which is i-1 of tmp index in HeatPumpCOPMap
                                slope_heat = (p.HeatPumpCOPMap[index+1, 2] - p.HeatPumpCOPMap[index, 2]) / (tmp - p.HeatPumpCOPMap[index, 1])
                                COP_Heat = p.HeatPumpCOPMap[index, 2] + (tmp - EWT_F) * slope_heat
                                slope_cool = (p.HeatPumpCOPMap[index+1, 3] - p.HeatPumpCOPMap[index, 3]) / (tmp - p.HeatPumpCOPMap[index, 1])
                                COP_Cool = p.HeatPumpCOPMap[index, 3] + (tmp - EWT_F) * slope_cool
                                break
                            end
                        end
                    end
                    
                    # Override COP_Heat/COP_Cool calculation if Q_Heat/Q_Cool is negative
                    if Q_Heat <= 0.0
                        COP_Heat = 3.0
                    end
                    if Q_Cool <= 0.0
                        COP_Cool = 3.0
                    end

                    # Calculate the heat pump outputs
                    P_WSHP_H = Q_Heat / COP_Heat
                    P_WSHP_C = Q_Cool / COP_Cool

                    Q_Absorbed = Q_Heat - P_WSHP_H
                    Q_Rejected = Q_Cool + P_WSHP_C
                    
                    Tons_HeatPump_H = Q_Heat / 1.055 / 12000.0
                    Tons_HeatPump_C = Q_Cool / 1.055 / 12000.0
                    
                    if (Tons_HeatPump_H + Tons_HeatPump_C) > 0.0
                        GPM_GHX = max(p.fMin_VSP_GHXPump * p.GPM_GHXPump, 
                                        (Tons_HeatPump_H + Tons_HeatPump_C) * p.GPMperTon_WSHP)
                    else
                        GPM_GHX = 0.0
                    end
                    
                    Mdot_GHX = GPM_GHX * 60.0 / 264.172 * p.Rho_GHXFluid
                    
                    if Mdot_GHX > 0.0
                        Tout_HeatPumps_GHX = Tout_GHX + (Q_Rejected - Q_Absorbed) / Mdot_GHX / p.Cp_GHXFluid
                    else
                        Tout_HeatPumps_GHX = Tout_GHX
                    end

                    # Calculate the pump outputs
                    if GPM_GHX > 0.0
                        f_GHXPump = GPM_GHX / p.GPM_GHXPump
                    else
                        f_GHXPump = 0.0
                    end
                    
                    P_GHXPump = p.Prated_GHXPump * (f_GHXPump^p.Exponent_GHXPump)
                    Qf_GHXPump = P_GHXPump * 0.3
                    if Mdot_GHX > 0.0
                        Tout_Pump = Tout_HeatPumps_GHX + Qf_GHXPump / Mdot_GHX / p.Cp_GHXFluid
                    else
                        Tout_Pump = Tout_HeatPumps_GHX
                    end

                    # Call the GHX model each iteration
                    ErrorFound = [false]
                    if p.ghx_model == "DST"
                        XIN[1] = Tout_Pump
                        XIN[2] = Mdot_GHX
                        XIN[3] = p.AmbientTemperature[hr]
                        XIN[4] = p.AmbientTemperature[hr]
                        XIN[5] = 1.0
                        # Call the ground model
                        ccall((:type557_, "/opt/julia_src/dst.so"), Cvoid, 
                        (Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Int64}, Ptr{Int64}), 
                        TimeArray, XIN, OUT, PAR, INFO, ErrorFound)
                    elseif p.ghx_model == "TESS"
                        XIN[1] = Tout_Pump
                        XIN[2] = Mdot_GHX
                        XIN[3] = p.AmbientTemperature[hr]
                        XIN[4] = p.AmbientTemperature[hr]
                        ccall((:type1373_, "/opt/julia_src/tess.so"), Cvoid, 
                        (Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Int64}, Ptr{Int64}), 
                        TimeArray, XIN, OUT, PAR, INFO, ErrorFound)
                    end

                    # Calculate the outputs
                    # This might be an inefficient calc to do every timestep (could just do at the end if not using before)
                    r.Tmax_GHX = max(r.Tmax_GHX, OUT[1])
                    r.Tmin_GHX = min(r.Tmin_GHX, OUT[1])

                    r.Power_GHXPump += P_GHXPump * Delt
                    r.Qfluid_GHXPump += Qf_GHXPump * Delt
                    r.Power_WSHP_C += P_WSHP_C * Delt
                    r.Power_WSHP_H += P_WSHP_H * Delt
                    r.LoadMet_WSHP_C += Q_Cool * Delt
                    r.LoadMet_WSHP_H += Q_Heat * Delt
                    r.Q_Rejected_Total += Q_Rejected * Delt
                    r.Q_Absorbed_Total += Q_Absorbed * Delt
                    r.Q_GHX_Net += (Q_Rejected - Q_Absorbed) * Delt
                    
                    if p.ghx_model == "DST"
                        r.Q_GHX_In += OUT[4] * Delt
                        r.Q_GHX_Top += OUT[5] * Delt
                        r.Q_GHX_Sides += OUT[6] * Delt
                        r.Q_GHX_Bottom += OUT[7] * Delt
                        r.Q_GHX_Stored += OUT[8] * Delt
                    elseif p.ghx_model == "TESS"
                        r.Q_GHX_In += OUT[3] * Delt
                        r.Q_GHX_Top += OUT[5] * Delt
                        r.Q_GHX_Sides += OUT[8] * Delt
                        r.Q_GHX_Bottom += OUT[10] * Delt
                        r.Q_GHX_Stored += OUT[3] * Delt
                        r.Qf_GHX_Stored += OUT[12] * Delt
                    end

                    # EWT is an AVERAGE temperature over the hour
                    r.EWT[8760*(year-1)+hr] += OUT[1]*Delt

                    r.P_GHXPump_Hourly[8760*(year-1)+hr] += P_GHXPump * Delt / 3600.0
                    r.P_WSHPc_Hourly[8760*(year-1)+hr] += P_WSHP_C * Delt / 3600.0
                    r.P_WSHPh_Hourly[8760*(year-1)+hr] += P_WSHP_H * Delt / 3600.0
                    r.Qc_Hourly[8760*(year-1)+hr] += Q_Cool * Delt / 3600.0
                    r.Qh_Hourly[8760*(year-1)+hr] += Q_Heat * Delt / 3600.0

                    # Call the ground heat exchanger model to clean up as the timestep is complete (assign Ti=Tf)
                    INFO[13] = 1
                    if p.ghx_model == "DST"
                        ccall((:type557_, "/opt/julia_src/dst.so"), Cvoid, 
                        (Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Int64}, Ptr{Int64}), 
                        TimeArray, XIN, OUT, PAR, INFO, ErrorFound)
                    elseif p.ghx_model == "TESS"
                        ccall((:type1373_, "/opt/julia_src/tess.so"), Cvoid, 
                        (Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Int64}, Ptr{Int64}), 
                        TimeArray, XIN, OUT, PAR, INFO, ErrorFound)
                    end 
                    INFO[13] = 0
                end
            end
        end
        # Use a Newton's method to calculate the bore size to meet the design goals
        # FX => error of temperature limits
        r.N_Bores_Final = r.N_Bores[size_iter]
        FX_Cooling = p.Tmax_Sizing - r.Tmax_GHX
        FX_Heating = r.Tmin_GHX - p.Tmin_Sizing
        # If tolerance is met for either heating or cooling, break the while loop and accept size solution
        if (abs(FX_Cooling) < p.solver_ewt_tolerance) && (abs(FX_Heating) < p.solver_ewt_tolerance)
            r.FX_Now[size_iter] = min(FX_Cooling, FX_Heating)
            break
        elseif (abs(FX_Cooling) < p.solver_ewt_tolerance) && (FX_Heating > 0.0)
            r.FX_Now[size_iter] = FX_Cooling
            break
        elseif (abs(FX_Heating) < p.solver_ewt_tolerance) && (FX_Cooling > 0.0)
            r.FX_Now[size_iter] = FX_Heating
            break
        end
        # Check the first iteration if it solved and if not, give it a next best guess
        if size_iter == 1
            # X_Now[size_iter=1] is already defined by X_init
            # FX_Now[size_iter=1] is NOT already defined (removed "X/FX_Previous" from TESS)
            if (FX_Cooling > 0.0) && (FX_Heating > 0.0)
                r.X_Now[size_iter+1] = r.X_Now[size_iter] / 2.0
                r.FX_Now[size_iter] = max(FX_Cooling, FX_Heating)
            elseif FX_Cooling > 0.0
                r.X_Now[size_iter+1] = 2.0 * r.X_Now[size_iter]
                r.FX_Now[size_iter] = FX_Heating
            elseif FX_Heating > 0.0
                r.X_Now[size_iter+1] = 2.0 * r.X_Now[size_iter]
                r.FX_Now[size_iter] = FX_Cooling
            else
                r.X_Now[size_iter+1] = 2.0 * r.X_Now[size_iter]
                r.FX_Now[size_iter] = min(FX_Cooling, FX_Heating)
            end
            size_iter += 1
            continue
        elseif size_iter > 1
            if (FX_Cooling > p.solver_ewt_tolerance) || (FX_Heating > p.solver_ewt_tolerance)
                if FX_Heating < p.solver_ewt_tolerance
                    r.FX_Now[size_iter] = FX_Heating
                elseif FX_Cooling < p.solver_ewt_tolerance
                    r.FX_Now[size_iter] = FX_Cooling
                else  # Both are greater than tolerance
                    r.FX_Now[size_iter] = min(FX_Cooling, FX_Heating)
                end
            else
                r.FX_Now[size_iter] = max(FX_Cooling, FX_Heating)
            end
            X_New = r.X_Now[size_iter] - r.FX_Now[size_iter] * 
                    (r.X_Now[size_iter] - r.X_Now[size_iter-1]) / 
                    (r.FX_Now[size_iter] - r.FX_Now[size_iter-1])
            if X_New <= 0.0
                X_New = min(r.X_Now[size_iter], r.X_Now[size_iter-1]) / 2.0
            end
            X_New = min(r.X_Now[size_iter] * 2.0, X_New)
            X_New = max(r.X_Now[size_iter] / 2.0, X_New)
            r.X_Now[size_iter+1] = X_New
        
            #!Check to see if the program is stuck in a tolerance situation hunting a solution between two adjacent # bore sizes 
            if abs(r.N_Bores[size_iter] - r.N_Bores[size_iter-1]) == 1
                if (r.FX_Now[size_iter] < 0) && (r.FX_Now[size_iter-1] > 0)
                    break    
                elseif (r.FX_Now[size_iter] > 0) && (r.FX_Now[size_iter-1] < 0)
                    break
                end
            end
            
            size_iter += 1
            continue
        end
    end
    # Record actual final EWT error; if the loop exits by hitting max_sizing_iterations, record previous error
    if r.FX_Now[size_iter] == 0
        r.FX_Final = r.FX_Now[size_iter-1]
    else
        r.FX_Final = r.FX_Now[size_iter]
    end
    return r
end

function assign_PAR!(p, r, PAR, size_iter)
    if p.ghx_model == "DST"
        PAR[1] = r.StorageVolume
        PAR[2] = r.Length_Boreholes + p.Depth_Header
        PAR[3] = p.Depth_Header
        PAR[4] = r.N_Bores[size_iter]
        PAR[5] = p.Radius_Bores
        PAR[6] = p.N_Series
        PAR[7] = p.N_Radial
        PAR[8] = p.N_Vertical
        PAR[9] = p.K_Soil
        PAR[10] = p.RhoCp_Soil
        PAR[11] = -1.0
        PAR[12] = p.Ro_Pipe
        PAR[13] = p.Ri_Pipe
        PAR[14] = p.Center_Center_Distance / 2.0  # Was Center_Center_HalfDistance
        PAR[15] = p.K_Grout
        PAR[16] = p.K_Pipe
        PAR[17] = p.K_Grout
        PAR[18] = 0.0
        PAR[19] = r.Mdot_Borehole
        PAR[20] = p.T_Ground
        PAR[21] = -1.0
        PAR[22] = p.Cp_GHXFluid
        PAR[23] = p.Rho_GHXFluid
        PAR[24] = 0.0
        PAR[25] = 0.0
        PAR[26] = 0.0
        PAR[27] = 0.04 * 3.6
        PAR[28] = 25.0
        PAR[29] = 100.0
        PAR[30] = p.T_Ground
        PAR[31] = 0.0
        PAR[32] = 0.0
        PAR[33] = p.T_Ground 
        PAR[34] = p.T_Ground
        PAR[35] = 0.
        PAR[36] = p.T_Ground
        PAR[37] = p.Tamp_Ground
        PAR[38] = p.DayMin_DST
        PAR[39] = 1.0
        PAR[40] = p.K_Soil
        PAR[41] = p.RhoCp_Soil
        PAR[42] = r.Depth_DST
        PAR[43] = 0.0
        PAR[44] = 0.0
    elseif p.ghx_model == "TESS"
        PAR[1] = r.N_Bores[size_iter]
        PAR[2] = 1.0
        PAR[3] = r.Length_Boreholes
        PAR[4] = p.BoreSpacing
        PAR[5] = p.SpacingType
        PAR[6] = p.Radius_Bores * 2.0
        PAR[7] = p.K_Grout
        PAR[8] = p.Center_Center_Distance
        PAR[9] = p.Ri_Pipe * 2.0
        PAR[10] = p.Ro_Pipe * 2.0
        PAR[11] = p.K_Pipe
        PAR[12] = p.Depth_Header
        PAR[13] = p.Cp_GHXFluid
        PAR[14] = p.Rho_GHXFluid
        PAR[15] = p.K_GHXFluid
        PAR[16] = p.Mu_GHXFluid
        PAR[17] = 0.0
        PAR[18] = 0.0
        PAR[19] = 0.0
        PAR[20] = p.K_Soil
        PAR[21] = p.Rho_Soil
        PAR[22] = p.Cp_Soil
        PAR[23] = p.T_Ground
        PAR[24] = p.Tamp_Ground
        PAR[25] = p.DayMin_Surface
        PAR[26] = 0.0
        PAR[27] = r.Radius_Field  #!Far-field distance
        PAR[28] = p.Depth_Bores / 2.0  #!Deep earth distance
        PAR[29] = 0.1
        PAR[30] = 2.0
        PAR[31] = 0.02
        PAR[32] = 2.0       
    end
end

function init_ghx_calls_2x!(p, TimeArray, XIN, OUT, PAR, INFO)
    # Call the GHX model two times for initialization
    INFO[1] = 1
    INFO[7] = -1
    INFO[8] = 2
    ErrorFound = [false]
    if p.ghx_model == "DST"
        INFO[2] = 557
        XIN[1] = p.T_Ground
        XIN[2] = 0.0
        XIN[3] = 20.0
        XIN[4] = 20.0
        XIN[5] = 1.0
        
        # First time
        ccall((:type557_, "/opt/julia_src/dst.so"), Cvoid, 
        (Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Int64}, Ptr{Int64}), 
        TimeArray, XIN, OUT, PAR, INFO, ErrorFound)
        
        INFO[7] = 0
        INFO[8] = 3

        # Second time
        ccall((:type557_, "/opt/julia_src/dst.so"), Cvoid,
        (Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Int64}, Ptr{Int64}), 
        TimeArray, XIN, OUT, PAR, INFO, ErrorFound)
    elseif p.ghx_model == "TESS"
        INFO[2] = 1373
        XIN[1] = p.T_Ground
        XIN[2] = 0.0
        XIN[3] = 20.0
        XIN[4] = 20.0

        # First time
        ccall((:type1373_, "/opt/julia_src/tess.so"), Cvoid,
        (Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Int64}, Ptr{Int64}), 
        TimeArray, XIN, OUT, PAR, INFO, ErrorFound)        

        INFO[7] = 0
        INFO[8] = 3

        # Second time
        ccall((:type1373_, "/opt/julia_src/tess.so"), Cvoid,
        (Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Ptr{Int64}, Ptr{Int64}), 
        TimeArray, XIN, OUT, PAR, INFO, ErrorFound)         
    end
end    


# -------
end # module GHPGHX
