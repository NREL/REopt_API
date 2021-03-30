import json
import numpy as np
import matplotlib.pyplot as plt
import os

def plot_results(dir, file, results, include_rtm=True):
    load = np.array(results['inputs']['Scenario']['Site']['LoadProfile']['loads_kw'])
    grid_to_load = np.array(results['outputs']['Scenario']['Site']['ElectricTariff']['year_one_to_load_series_kw'])
    grid_to_stor = np.array(results['outputs']['Scenario']['Site']['ElectricTariff']['year_one_to_battery_series_kw'])
    stor_to_load = np.array(results['outputs']['Scenario']['Site']['Storage']['year_one_to_load_series_kw'])
    pv_to_load = np.array(results['outputs']['Scenario']['Site']['PV']['year_one_to_load_series_kw'])
    pv_to_stor = np.array(results['outputs']['Scenario']['Site']['PV']['year_one_to_battery_series_kw'])
    pv_curtailed = np.array(results['outputs']['Scenario']['Site']['PV']['year_one_curtailed_production_series_kw'])
    wind_to_load = None#np.array(results['outputs']['Scenario']['Site']['Wind']['year_one_to_load_series_kw'])
    wind_to_stor = None#np.array(results['outputs']['Scenario']['Site']['Wind']['year_one_to_battery_series_kw'])
    gen_to_load = None#np.array(results['outputs']['Scenario']['Site']['Generator']['year_one_power_production_series_kw'])

    fig, ax1 = plt.subplots(figsize=(13,6))
    # stacked area plot
    ax1.set_xlabel('Timestep [hours]', fontsize=12)
    ax1.set_ylabel('Power [kW]', fontsize=12)
    n_wks = 1
    #start = 24*181 # july 1st
    start = 24*17# a week in feb 24*230 # a week in august
    end = start + n_wks*7*24 # n_wks weeks later
    timesteps=np.arange(start,end)
    if results['outputs']['Scenario']['Site']['PV']['size_kw'] == 0.0:
        stor_charge = np.maximum(0,grid_to_stor - stor_to_load)
        stor_discharge = np.maximum(0,stor_to_load - grid_to_stor)
        # stor_charge = grid_to_stor
        # stor_discharge = stor_to_load
        labels = ['Grid to Load','Battery Discharging','Battery Charging']
        areas = ax1.stackplot(timesteps,grid_to_load[start:end], stor_discharge[start:end], stor_charge[start:end], labels=slabels, colors=('tab:gray','tab:blue','tab:green'))
    else:
        stor_charge = np.maximum(0,(grid_to_stor+pv_to_stor) - stor_to_load)
        stor_discharge = np.maximum(0,stor_to_load - (grid_to_stor+pv_to_stor))
        # stor_charge = grid_to_stor+pv_to_stor
        # stor_discharge = stor_to_load
        labels = ['PV to Load','Grid to Load','Battery Discharging','Battery Charging','PV Curtailed']
        areas = ax1.stackplot(timesteps,pv_to_load[start:end], grid_to_load[start:end], stor_discharge[start:end], stor_charge[start:end], pv_curtailed[start:end], labels=labels, colors=('tab:orange','tab:gray','tab:blue','tab:green','tab:red'))
    ax1.tick_params(axis='y')
    # add line for load
    line_load = ax1.plot(timesteps,load[start:end], label='Load', color='k')
    labels = labels + ['Load']
    lines = areas+line_load
    if include_rtm:
        # add line for energy price
        RTM_prices = np.array(results['inputs']['Scenario']['Site']['ElectricTariff']['real_time_market_rates_series_us_dollars_per_kwh'][start:end])
        ax2 = ax1.twinx()
        #ax2.set_ylim(ax1.get_ylim())
        line_rtm = ax2.plot(np.arange(start,end), RTM_prices, label=labels[2])
        #ax2.axes.yaxis.set_visible(False)
        ax2.set_ylabel('Price [$ / kWh]', fontsize=12)
        labels = labels + ['RTM Prices']
        lines = lines+line_rtm
    ax1.legend(lines, labels)
    # save plot
    plt.savefig(os.path.join(dir,file[16:-5]+"_dispatch_{}to{}{}".format(start,end,"_withRTMprice" if include_rtm else "")))

def plot_energy_prices(dir,file,results):
    n_wks = 1
    #start = 24*181 # july 1st
    start = 24*230 # a week in august
    end = start + n_wks*7*24 # n_wks weeks later
    RTM_prices = np.array(results['inputs']['Scenario']['Site']['ElectricTariff']['real_time_market_rates_series_us_dollars_per_kwh'][start:end])
    index_prices = np.array(results['inputs']['Scenario']['Site']['ElectricTariff']['contract_rates_series_us_dollars_per_kwh'][start:end])
    TOU_price_options = np.array([rate[0]['rate'] for rate in results['inputs']['Scenario']['Site']['ElectricTariff']['urdb_response']['energyratestructure']])
    weekday_TOU_prices = TOU_price_options[np.array(results['inputs']['Scenario']['Site']['ElectricTariff']['urdb_response']['energyweekdayschedule'][6])]
    weekend_TOU_prices = TOU_price_options[np.array(results['inputs']['Scenario']['Site']['ElectricTariff']['urdb_response']['energyweekendschedule'][6])]
    #TOU_prices = [weekday_TOU_prices,weekday_TOU_prices,weekday_TOU_prices,weekday_TOU_prices,weekday_TOU_prices,weekend_TOU_prices,weekend_TOU_prices]
    TOU_prices = np.repeat([weekday_TOU_prices,weekend_TOU_prices], [5, 2], axis=0)
    TOU_prices = np.tile(TOU_prices.flatten(),n_wks)
    labels=['TOU Prices','Index Prices','RTM Prices']
    fig, ax = plt.subplots(figsize=(13,6))
    line_TOU = ax.plot(np.arange(start,end), TOU_prices, label=labels[0])
    line_index = ax.plot(np.arange(start,end), index_prices, label=labels[1])
    line_rtm = ax.plot(np.arange(start,end), RTM_prices, label=labels[2])
    ax.legend()
    ax.set_xlabel('Timestep [hours]', fontsize=12)
    ax.set_ylabel('Price [$ / kWh]', fontsize=12)
    plt.savefig(os.path.join(dir,file[16:-5]+"_energy_prices_{}to{}".format(start,end)))
    

def print_PV_stats(results):
    pv_prod = np.array(results['outputs']['Scenario']['Site']['PV']['year_one_power_production_series_kw'])
    pv_to_load = np.array(results['outputs']['Scenario']['Site']['PV']['year_one_to_load_series_kw'])
    pv_to_stor = np.array(results['outputs']['Scenario']['Site']['PV']['year_one_to_battery_series_kw'])
    pv_curtailed = np.array(results['outputs']['Scenario']['Site']['PV']['year_one_curtailed_production_series_kw'])
    print("Year 1 PV to Load (kWh): {}".format(sum(pv_to_load)))
    print("Year 1 PV to Battery (kWh): {}".format(sum(pv_to_stor)))
    print("Year 1 PV Curtailed (kWh): {}".format(sum(pv_curtailed)))
    print("Year 1 PV Exported (kWh): {}".format(sum(pv_prod-pv_to_load-pv_to_stor)))

def plot_emissions_vs_PV(dir, file, results):
    n_wks = 1
    #start = 24*181 # july 1st
    start = 24*230 # a week in august
    end = start + n_wks*7*24 # n_wks weeks later
    emissions_factors = np.array(results['inputs']['Scenario']['Site']['ElectricTariff']["emissions_factor_series_lb_CO2_per_kwh"])
    PV_production = np.array(results['outputs']['Scenario']['Site']['PV']["year_one_power_production_series_kw"])
    labels=['AVERT Emissions Factor','PV Production']
    fig, ax1 = plt.subplots(figsize=(13,6))
    line_em = ax1.plot(np.arange(start,end), emissions_factors[start:end], label=labels[0], color='tab:grey')
    ax1.yaxis.label.set_color('tab:grey')
    ax2 = ax1.twinx()
    line_pv = ax2.plot(np.arange(start,end), PV_production[start:end], label=labels[1], color='tab:orange')
    ax2.yaxis.label.set_color('tab:orange')
    ax2.legend(line_em+line_pv, labels)
    ax1.set_xlabel('Timestep [hours]', fontsize=12)
    ax1.set_ylabel('Emissions [lb CO2 / kWh]', fontsize=12)
    ax2.set_ylabel('Power [kW]', fontsize=12)
    plt.savefig(os.path.join(dir,file[16:-5]+"_emissions_vs_PV"))

def print_summary_stats(results):
    tariff_out = results['outputs']['Scenario']['Site']['ElectricTariff']
    print("PV size_kw = {}".format(results['outputs']['Scenario']['Site']['PV']['size_kw']))
    print("Storage size_kw = {}".format(results['outputs']['Scenario']['Site']['Storage']['size_kw']))
    print("Storage size_kwh = {}".format(results['outputs']['Scenario']['Site']['Storage']['size_kwh']))
    print("contract cost = {}".format(tariff_out['total_contract_energy_cost_us_dollars']))
    print("excess deficit cost = {}".format(tariff_out['total_contract_excess_deficit_energy_cost_us_dollars']))
    print("total energy cost = {}".format(tariff_out['total_energy_cost_us_dollars']))
    print("energy export benfit = {}".format(tariff_out['total_export_benefit_us_dollars']))
    print("demand cost = {}".format(tariff_out['total_demand_cost_us_dollars']))
    print("PPA cost = {}".format(results['outputs']['Scenario']['Site']['PV']['pv_ppa_cost_us_dollars']))
    print("CapX = {}".format(results['outputs']['Scenario']['Site']['Financial']['net_capital_costs']))
    print("LCC = {}".format(results['outputs']['Scenario']['Site']['Financial']['lcc_us_dollars']))
    print("NPV = {}".format(results['outputs']['Scenario']['Site']['Financial']['npv_us_dollars']))
    print("CO2 = {}".format(results['outputs']['Scenario']['Site']['year_one_emissions_lb_C02']))


if __name__ == '__main__':
    dir = 'fixed_optE_demand'
    for file in os.listdir(dir):
        if file.endswith(".json") and file in ["lineage_results_2019_existstor_optE.json"]:
            path = os.path.join(dir,file)
            print("Analyzing results in file: {}".format(path))

            results = json.load(open(path))

            #print_summary_stats(results)

            #plot_results(dir, file, results, include_rtm=False)
            #plot_results(dir, file, results, include_rtm=True)

            # if "BAU" not in file and "bau" not in file:
            #     print_PV_stats(results)

            plot_emissions_vs_PV(dir, file, results)

            #plot_energy_prices(dir,file,results)

            #print("eGRID year one emissions = {}".format(0.4965*np.array(results['outputs']['Scenario']['Site']['ElectricTariff']['year_one_energy_supplied_kwh'])))

            # start = 24*181 # july 1st
            # end = 4344 + 7*24 # 1 week later
            # print(np.any((grid_to_stor[start:end]+pv_to_stor[start:end]) * stor_to_load[start:end]))
            # print(np.count_nonzero((grid_to_stor[start:end]+pv_to_stor[start:end]) * stor_to_load[start:end]))
            # print(grid_to_stor[start:end]+pv_to_stor[start:end])
            # print(stor_to_load[start:end])