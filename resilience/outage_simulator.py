#!usr/bin/python


def simulate_outage(pv_kw, batt_kwh, batt_kw, load, prod_factor, init_soc, crit_load_factor,
                    batt_roundtrip_efficiency=0.829):
    """
    
    :param pv_kw: float, pv capacity
    :param batt_kwh: float, battery storage capacity
    :param batt_kw: float, battery inverter capacity
    :param load: list of floats, units=kW, len(load) must equal len(prod_factor)
    :param prod_factor: list of floats, production of 1kW PV system
    :param init_soc: list of floats between 0 and 1 inclusive, initial state-of-charge
    :param crit_load_factor: list of floats between 0 and 1 inclusive (can be all 1's if load is critical load)
    :param batt_roundtrip_efficiency: roundtrip battery efficiency
    :return: list of hours survived for outages starting at every time step, plus min,max,avg of list
    """
    
    n_timesteps = len(load)
    r = [0] * n_timesteps  # initialize resiliency vector

    # pv minus load is the burden on battery
    pvMld = [pf * pv_kw - clf * ld for (pf, clf, ld) in
             zip(prod_factor, crit_load_factor, load)]  # negative values are unmet load (by PV)

    for n in range(n_timesteps):  # outer loop for finding r for outage starting each timestep of year

        charge = batt_kwh * init_soc[n]  # reset battery for each simulation

        for bal in pvMld:  # bal == balance after PV serves load

            if bal >= 0:  # load met by PV
                r[n] += 1  # survived one more timestep

                if charge < batt_kwh:  # if there's room in the battery
                    charge += min(batt_kwh - charge, bal * batt_roundtrip_efficiency, batt_kw)

            else:  # balance < 0 --> load not met by PV
                b = abs(bal)
                
                if min(charge, batt_kw) >= b:  # battery can carry balance
                    charge = max(0, charge - b)  # prevent battery charge from going negative
                    r[n] += 1  # survived one more timestep
                    
                else:  # battery cannot carry balance
                    r[n] += min(charge / b, batt_kw / b)  # fraction of timestep carried by battery
                    pvMld = pvMld[1:] + pvMld[:1]  # shift pvMld one timestep
                    break

    pvMld = pvMld[1:] + pvMld[:1]  # shift back to original state

    r_min = min(r)
    r_max = max(r)
    r_avg = float(sum(r)) / float(len(r))
    r_list = r
    
    return r_list, r_min, r_max, r_avg