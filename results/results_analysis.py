import json
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

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

def print_max_system_sizes():
    site = "SIAD"
    for scen_abrv in ["no_PV","with_PV"]:
        pv_kw = []
        batt_kw = []
        batt_kwh = []
        gen_kw = []
        for day in range(365-14):
            json_filename = "{}_results_{}_outage_{}.json".format(site,scen_abrv,day)
            try:
                results = json.load(open(json_filename))['outputs']["Scenario"]["Site"]
                pv_kw.append(results["PV"]["size_kw"])
                batt_kw.append(results["Storage"]["size_kw"])
                batt_kwh.append(results["Storage"]["size_kwh"])
                gen_kw.append(results["Generator"]["size_kw"])
            except:
                break
        pv_max_kw = max(pv_kw)
        pv_75p_kw = np.percentile(pv_kw,75)
        pv_med_kw = np.median(pv_kw)
        batt_max_kw = max(batt_kw)
        batt_75p_kw = np.percentile(batt_kw,75)
        batt_med_kw = np.median(batt_kw)
        batt_max_kwh = max(batt_kwh)
        batt_75p_kwh = np.percentile(batt_kwh,75)
        batt_med_kwh = np.median(batt_kwh)
        gen_max_kw = max(gen_kw)
        gen_75p_kw = np.percentile(gen_kw,75)
        gen_med_kw = np.median(gen_kw)
        print(scen_abrv)
        print("PV max kW: {}, PV 75 pctl kW: {}, PV median kW: {}".format(pv_max_kw,pv_75p_kw,pv_med_kw))
        print("Storage max kW: {}, Storage 75 pctl kW: {}, Storage median kW: {}".format(batt_max_kw,batt_75p_kw,batt_med_kw))
        print("Storage max kWh: {}, Storage 75 pctl kWh: {}, Storage median kWh: {}".format(batt_max_kwh,batt_75p_kwh,batt_med_kwh))
        print("Generator max kW: {}, Generator 75 pctl kW: {}, Generator median kW: {}".format(gen_max_kw,gen_75p_kw,gen_med_kw))

# def print_max_system_sizes():
#     site = "SIAD"
#     for scen_abrv in ["no_PV","with_PV"]:
#         pv_max_kw = 0
#         batt_max_kw = 0
#         batt_max_kwh = 0
#         pv_max_kw_day = None
#         batt_max_kw_day = None
#         batt_max_kwh_day = None
#         gen_max_kw = 0
#         gen_max_kw_day = None
#         for day in range(365-14):
#             json_filename = "{}_results_{}_outage_{}.json".format(site,scen_abrv,day)
#             try:
#                 results = json.load(open(json_filename))['outputs']["Scenario"]["Site"]
#                 if results["PV"]["size_kw"] > pv_max_kw:
#                     pv_max_kw = results["PV"]["size_kw"]
#                     pv_max_kw_day = day
#                 if results["Storage"]["size_kw"] > batt_max_kw:
#                     batt_max_kw = results["Storage"]["size_kw"]
#                     batt_max_kw_day = day
#                 if results["Storage"]["size_kwh"] > batt_max_kwh:
#                     batt_max_kwh = results["Storage"]["size_kwh"]
#                     batt_max_kwh_day = day
#                 if results["Generator"]["size_kw"] > gen_max_kw:
#                     gen_max_kw = results["Generator"]["size_kw"]
#                     gen_max_kw_day = day
#             except:
#                 break
#         print(scen_abrv)
#         print("PV max kW: {}, for outage starting on day {}".format(pv_max_kw,pv_max_kw_day))
#         print("Storage max kW: {}, for outage starting on day {}".format(batt_max_kw,batt_max_kw_day))
#         print("Storage max kWh: {}, for outage starting on day {}".format(batt_max_kwh,batt_max_kwh_day))
#         print("Generator max kW: {}, for outage starting on day {}".format(gen_max_kw,gen_max_kw_day))


def multi_site_summary_xlsx():
    summary_filename = "siad_results.xlsx"
    sites = ["SIAD"]
    # df_all_sites = None
    print(site_summary_df(sites[0]))
    with pd.ExcelWriter(summary_filename) as writer:
        for site in sites:
            df_site = site_summary_df(site)
            df_site.to_excel(writer, sheet_name=site)
            # if df_all_sites is None:
            #     df_all_sites = df_site
            # else:
            #     df_all_sites = df_all_sites.append(df_site)

def site_summary_df(site):
    rows = ["PV size (kW)",
            "Storage size (kW)",
            "Storage size (kWh)",
            "Generator size (kW)",
            "Energy charge savings ($000)",
            "Demand charge savings ($000)",
            # "PV PPA charges ($000)",
            "Annualized payment to third party ($000)",
            "Capital costs ($000)",
            "LCC ($000)",
            "NPV ($000)",
            "",
            "Net PV penetration (%)",
            # "Year 1 grid energy consumed (MW)",
            "Year 1 emissions (1000 lb CO2)"
            # "Year 1 emissions – eGRID marginal (1000 lb CO2)",
            # "Year 1 emissions – eGRID overall (1000 lb CO2)"
            ]
    scenarios = {#"BAU": "Business as Usual",
                "no_PV_100pctl_resilience": "No Added PV, 100th pctl Resilience",
                "with_PV_100pctl_resilience": "With Added PV, 100th pctl Resilience",
                "no_PV_75pctl_resilience": "No Added PV, 75th pctl Resilience",
                "with_PV_75pctl_resilience": "With Added PV, 75th pctl Resilience",
                "no_PV_50pctl_resilience": "No Added PV, 50th pctl Resilience",
                "with_PV_50pctl_resilience": "With Added PV, 50th pctl Resilience",
                "no_PV_no_resilience": "No Added PV, No Extra Resilience",
                "with_PV_no_resilience": "With Added PV, No Extra Resilience",
                "with_PV_neutral_NPV": "With Added PV, Neutral NPV Resilience"
                }
    add_BAU_col = False
    df = pd.DataFrame(index=rows)
    for scen_abrv,col_title in scenarios.items():
        json_filename = "{}_results_{}.json".format(site,scen_abrv)
        results = json.load(open(json_filename))['outputs']["Scenario"]["Site"]

        # if site == "Allentown":
        #     eGRID_factor_avg = 0.695 * 1.051
        #     eGRID_factor_marg = 1.2379 * 1.051
        # else:
        #     eGRID_factor_avg = 1.0677 * 1.051
        #     eGRID_factor_marg = 1.8316 * 1.051

        if "Business as Usual" not in df.columns and add_BAU_col:
            df["Business as Usual"] = [ "-",
                                        "-",
                                        "-",
                                        "-",#TODO: these might not be - if there are existing techs
                                        results["ElectricTariff"]["total_energy_cost_bau_us_dollars"]/1000,
                                        results["ElectricTariff"]["total_demand_cost_bau_us_dollars"]/1000,
                                        # "-",
                                        "-",
                                        "-",
                                        results["Financial"]["lcc_bau_us_dollars"]/1000,
                                        "-",
                                        "",
                                        100*results["PV"]["average_yearly_energy_produced_bau_kwh"]/sum(json.load(open(json_filename))['inputs']["Scenario"]["Site"]["LoadProfile"]["loads_kw"]),
                                        # results["ElectricTariff"]["year_one_energy_supplied_kwh_bau"]/1000,
                                        results["ElectricTariff"]["year_one_emissions_bau_lb_C02"]/1000
                                        # (results["ElectricTariff"]["year_one_energy_supplied_kwh_bau"]/eGRID_factor_marg)/1000,
                                        # (results["ElectricTariff"]["year_one_energy_supplied_kwh_bau"]/eGRID_factor_avg)/1000
                                        ]
                            
        df[col_title] = [results["PV"]["size_kw"] if results["PV"]["size_kw"] != 0 else "-",
                        results["Storage"]["size_kw"] if results["Storage"]["size_kw"] != 0 else "-",
                        results["Storage"]["size_kwh"] if results["Storage"]["size_kwh"] != 0 else "-",
                        results["Generator"]["size_kw"] if results["Generator"]["size_kw"] != 0 else "-",
                        (results["ElectricTariff"]["total_energy_cost_bau_us_dollars"]-results["ElectricTariff"]["total_energy_cost_us_dollars"])/1000,
                        (results["ElectricTariff"]["total_demand_cost_bau_us_dollars"]-results["ElectricTariff"]["total_demand_cost_us_dollars"])/1000,
                        # results["PV"]["pv_ppa_cost_us_dollars"]/1000,
                        results["Financial"]["annualized_payment_to_third_party_us_dollars"]/1000 if results["Financial"]["annualized_payment_to_third_party_us_dollars"] !=0 else "-",
                        results["Financial"]["net_capital_costs"]/1000 if results["Financial"]["net_capital_costs"] != 0 else "-",
                        results["Financial"]["lcc_us_dollars"]/1000,
                        results["Financial"]["npv_us_dollars"]/1000 if results["Financial"]["npv_us_dollars"] != 0 else "-",
                        "",
                        100*results["PV"]["average_yearly_energy_produced_kwh"]/sum(json.load(open(json_filename))['inputs']["Scenario"]["Site"]["LoadProfile"]["loads_kw"]),
                        # results["ElectricTariff"]["year_one_energy_supplied_kwh"]/1000,
                        results["ElectricTariff"]["year_one_emissions_lb_C02"]/1000
                        # (results["ElectricTariff"]["year_one_energy_supplied_kwh"]/eGRID_factor_marg)/1000,
                        # (results["ElectricTariff"]["year_one_energy_supplied_kwh"]/eGRID_factor_avg)/1000
                        ]
    #df.to_csv(summary_filename)
    return df

def load_profiles_plot():
    fig, ax = plt.subplots(figsize=(13,6))
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Power [kW]', fontsize=12)
    timesteps = pd.date_range("2020-01-01", "2021-01-01", periods=(365*24+1))
    timesteps = timesteps[:-1]

    sites = ["Allentown","Bedford","Rochelle","Cranberry","Solon"]
    for site in sites:
        json_filename = "results_{}_battery_max-pv.json".format(site)
        loads = json.load(open(json_filename))['inputs']["Scenario"]["Site"]["LoadProfile"]["loads_kw"]
        ax.plot(timesteps,loads, label=site, linewidth=.5)
    
    ax.legend()
    plt.savefig("5_sites_load_profiles")


###### Resilience Analysis #######

import csv
from math import floor
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import copy
import sys
import re
from datetime import datetime
import xlwt 
from xlwt import Workbook 
import matplotlib.dates as mdates

# Utilities
def csv2list(file):
    with open(file) as f:
        floatlist = [list(map(float,l))[0] for l in csv.reader(f, delimiter=',')]
    return floatlist

def readInputs(file):
    with open(file) as f:
        inputs = json.load(f)
    battCap = float(inputs["batt_kwh"])
    battPower = float(inputs["batt_kw"])
    genPower = float(inputs["generator_kw"])
    fuelavail = float(inputs["fuelavail"])
    pvsize = float(inputs["pv_kw"])
    windsize = float(inputs["wind_kw"])

    return battCap, battPower, genPower, fuelavail, pvsize

def readInputsFromREoptResultsFile(file):
    with open(file) as f:
        inputs = json.load(f)
    battCap = float(inputs["outputs"]["Scenario"]["Site"]["Storage"]["size_kwh"])
    battPower = float(inputs["outputs"]["Scenario"]["Site"]["Storage"]["size_kw"])
    genPower = float(inputs["outputs"]["Scenario"]["Site"]["Generator"]["size_kw"])
    fuelAvail = float(inputs["inputs"]["Scenario"]["Site"]["Generator"]["fuel_avail_gal"])
    pvProd = inputs["outputs"]["Scenario"]["Site"]["PV"]["year_one_power_production_series_kw"]
    windProd = inputs["outputs"]["Scenario"]["Site"]["Wind"]["year_one_power_production_series_kw"]
    load = inputs["outputs"]["Scenario"]["Site"]["LoadProfile"]["critical_load_series_kw"]
    soc = inputs["outputs"]["Scenario"]["Site"]["Storage"]["year_one_soc_series_pct"]

    return battCap, battPower, genPower, fuelAvail, pvProd, windProd, load, soc

# Generator
class generator():
    def __init__(self, diesel_kw, fuel_available, diesel_min_turndown=0.3):
        self.kw = diesel_kw
        self.fuel_available = fuel_available if self.kw > 0 else 0
        m, b = self.default_fuel_burn_rate(diesel_kw)
        self.m = m
        self.b = b * self.kw
        self.min_turndown = diesel_min_turndown
        self.genmin = self.min_turndown * self.kw
        
    def default_fuel_burn_rate(self, diesel_kw):
        if self.kw <= 40:
            m = 0.068
            b = 0.0125
        elif self.kw <= 80:
            m = 0.066
            b = 0.0142
        elif self.kw <= 150:
            m = 0.0644
            b = 0.0095
        elif self.kw <= 250:
            m = 0.0648
            b = 0.0067
        elif self.kw <= 750:
            m = 0.0656
            b = 0.0048
        elif self.kw <= 1500:
            m = 0.0657
            b = 0.0043
        else:
            m = 0.0657
            b = 0.004
        return m, b

    def gen_avail(self, n_steps_per_hour):  # kW
        if self.fuel_available - self.b > 0:
            return min((self.fuel_available * n_steps_per_hour - self.b) / self.m, self.kw)
        else:
            return 0

    def fuel_consume(self, gen_output, n_steps_per_hour):  # kW
        if self.gen_avail(n_steps_per_hour) >= self.genmin and gen_output > 0:
            gen_output = max(self.genmin, min(gen_output, self.gen_avail(n_steps_per_hour)))
            fuel_consume = (self.b + self.m * gen_output) / n_steps_per_hour 
            self.fuel_available -= min(self.fuel_available, fuel_consume)
        else:
            gen_output = 0
        return gen_output

# Battery
class battery():
    def __init__(self, batt_kwh, batt_kw, batt_roundtrip_efficiency=0.89, soc=1.0):
        self.kw = batt_kw
        self.size = batt_kwh if self.kw > 0 else 0
        self.soc = soc
        self.roundtrip_efficiency = batt_roundtrip_efficiency

    def batt_avail(self, n_steps_per_hour):  # kW
        return min(self.size * self.soc * n_steps_per_hour, self.kw)

    def batt_discharge(self, discharge, n_steps_per_hour):  # kW
        discharge = min(self.batt_avail(n_steps_per_hour), discharge)
        self.soc -= 0 if self.size == 0 else min(discharge / self.size / n_steps_per_hour, self.soc)
        return discharge

    def batt_charge(self, charge, n_steps_per_hour):  # kw
        room = (1 - self.soc)   # if there's room in the battery
        charge = min(room * n_steps_per_hour * self.size / self.roundtrip_efficiency, charge, self.kw / self.roundtrip_efficiency)
        chargesoc = 0 if self.size == 0 else charge * self.roundtrip_efficiency / self.size / n_steps_per_hour
        self.soc += chargesoc
        return charge

# Dispatch
def loadFollowing(critical_load, pv, wind, generator, battery, n_steps_per_hour):
    """
    Dispatch strategy for one time step
    """

    # distributed generation minus load is the burden on battery
    unmatch = (critical_load - pv - wind)  # kw
    discharge = 0
    gen_output = 0
    charge = 0
    
    if unmatch < 0:    # pv + wind> critical_load
        # excess PV power to charge battery
        charge = battery.batt_charge(-unmatch, n_steps_per_hour)
        unmatch = 0

    elif generator.genmin <= generator.gen_avail(n_steps_per_hour) and 0 < generator.kw:
        gen_output = generator.fuel_consume(unmatch, n_steps_per_hour)
        # charge battery with excess energy if unmatch < genmin
        charge = battery.batt_charge(max(gen_output - unmatch, 0), n_steps_per_hour)  # prevent negative charge
        discharge = battery.batt_discharge(max(unmatch - gen_output, 0), n_steps_per_hour)  # prevent negative discharge
        unmatch -= (gen_output + discharge - charge)

    elif unmatch <= battery.batt_avail(n_steps_per_hour):   # battery can carry balance
        discharge = battery.batt_discharge(unmatch, n_steps_per_hour)
        unmatch = 0
    
    stat = (gen_output, discharge, charge)
    
    return unmatch, stat, generator, battery

# Simulator
def simulator(strategy, generator, battery, critical_loads_kw, pv_kw_ac_hourly, wind_kw_ac_hourly, init_soc):
    n_timesteps = len(critical_loads_kw)
    n_steps_per_hour = n_timesteps / 8760  # type: int

    r = [0] * n_timesteps

    for time_step in range(n_timesteps):
        gen = copy.deepcopy(generator)
        batt = copy.deepcopy(battery)
        # outer loop: do simulation starting at each time step
        batt.soc = init_soc[time_step]   # reset battery for each simulation
                
        for i in range(n_timesteps):    # the i-th time step of simulation
            # inner loop: step through all possible surviving time steps
            # break inner loop if can not survive
            t = (time_step + i) % n_timesteps

            unmatch, stat, gen, batt = strategy(
                        critical_loads_kw[t], pv_kw_ac_hourly[t], wind_kw_ac_hourly[t], gen, batt, n_steps_per_hour)

            if unmatch > 0:  # cannot survive
                r[time_step] = i
                break
            elif (i == (n_timesteps-1)) and (unmatch <=0): # can survive a full year
                r[time_step] = i
                break


    r_min = min(r)
    r_max = max(r)
    r_avg = round((float(sum(r)) / float(len(r))), 2)

    x_vals = range(1, int(floor(r_max)+1))
    y_vals = list()

    for hrs in x_vals:
        y_vals.append(round(float(sum([1 if h >= hrs else 0 for h in r])) / float(n_timesteps), 4))

    return {"resilience_by_timestep": r,
            "resilience_min_timestep": r_min,
            "resilience_max_timestep": r_max,
            "resilience_avg_timestep": r_avg,
            "outage_durations": x_vals,
            "probs_of_surviving": y_vals,
            }

# Resilience main
def resilience_main():
    # Resilience User Inputs
    project = "Sierra Army Depot"
    # output_path = None#"//nrel.gov/shared/7A40/Renewable Energy Optimization/REO 3.0/Projects/AUC/Outage simulator/outputs/"
    rRE = []
    rmaxRE = []
    y_valsRE = []

    for scen in ["with_PV"]:#,"no_PV"]:
        # for pctl in [100,75,50]:
            json_input_path = "SIAD_results_{}_neutral_NPV.json".format(scen)
            output_path = "./{}".format(json_input_path[:-5])
            # Run Resilience
            tag = ""

            if project not in [None, "", " "]:
                project = project + "-"
                
            if tag not in [None, "", " "]:
                tag = "_" + tag
            
            if output_path in [None, "", " "]:
                output_path = "./"
                
            battCap, battPower, genPower, fuelAvail, pvProd, windProd, load, soc = readInputsFromREoptResultsFile(json_input_path)
            
            # load = csv2list(load_path)
            n_timesteps = len(load)
            n_steps_per_hour = n_timesteps / 8760
            empty_array = [0] * n_timesteps

            if pvProd == []:
                pvProd = empty_array
            if windProd == []:
                windProd = empty_array
            if soc == []:
                soc = empty_array
                
            # soc = csv2list(soc_path) if soc_path else empty_array
            # pv_factor = csv2list(pv_pf_path) if pv_pf_path else empty_array
            # wind_factor = csv2list(wind_pf_path) if wind_pf_path else empty_array
                
            pv_kw_ac_hourly = pvProd#[f*pvSize for f in pv_factor]
            wind_kw_ac_hourly = windProd#[f*windSize for f in wind_factor]
            
            inputsRE = {
                'batt_kwh': battCap,
                'batt_kw': battPower,
                'pv_kw_ac_hourly': pv_kw_ac_hourly,
                'wind_kw_ac_hourly': wind_kw_ac_hourly,
                'critical_loads_kw': load,
                'init_soc': soc,
                'diesel_kw': genPower,
                'fuel_available': fuelAvail
            }
            print(inputsRE['batt_kw'])
            print(inputsRE['batt_kwh'])
            print(max(inputsRE['pv_kw_ac_hourly']))
            print(inputsRE['diesel_kw'])
            print(inputsRE['fuel_available'])

            # inputs = copy.deepcopy(inputsRE)
            # inputs['pv_kw_ac_hourly'] = empty_array
            # inputs['wind_kw_ac_hourly'] = empty_array
            # inputs['init_soc'] = empty_array
            

            REfactor = sum(pv_kw_ac_hourly)/sum(load)
            print("Renewable Energy Factor:{}".format(round(REfactor,3)))

            GEN = generator(**{k: inputsRE[k] for k in generator.__init__.__code__.co_varnames if k in inputsRE})
            BATT = battery(**{k: inputsRE[k] for k in battery.__init__.__code__.co_varnames if k in inputsRE})

            # resp = simulator(loadFollowing, GEN, BATT, **{k: inputs[k] for k in simulator.__code__.co_varnames if k in inputs})
            respRE = simulator(loadFollowing, GEN, BATT, **{k: inputsRE[k] for k in simulator.__code__.co_varnames if k in inputsRE})

            # r = resp["resilience_by_timestep"]
            # rmax = resp["resilience_max_timestep"]
            # y_vals = resp["probs_of_surviving"]
            
            rRE.append(respRE["resilience_by_timestep"])
            rmaxRE.append(respRE["resilience_max_timestep"])
            y_valsRE.append(respRE["probs_of_surviving"])

            def writeResult(resp, file_name, path):
                wb = Workbook() 
                
                sheet1 = wb.add_sheet('Result') 
                sheet1.write(0, 1, 'Timesteps') 
                sheet1.write(1, 0, 'max resilience')
                sheet1.write(1, 1, resp["resilience_max_timestep"])
                sheet1.write(2, 0, 'min resilience')
                sheet1.write(2, 1, resp["resilience_min_timestep"]) 
                sheet1.write(3, 0, 'avg resilience')
                sheet1.write(3, 1, resp["resilience_avg_timestep"])

                sheet2 = wb.add_sheet('resilience_by_timestep') 
                for i, v in enumerate(resp["resilience_by_timestep"]):
                    sheet2.write(i, 0, v) 

                sheet3 = wb.add_sheet('probs_of_surviving') 
                for i, v in enumerate(resp["probs_of_surviving"]):
                    sheet3.write(i, 0, v)

                wb.save(path + '{}.xls'.format(file_name))
            
            # writeResult(resp, "Diesel Only{}".format(tag), output_path)
            # writeResult(respRE, "Diesel + RE{}".format(tag), output_path)
            writeResult(respRE, tag, output_path)

    m = int(max(rmaxRE))
    for i in range(len(y_valsRE)):
        y_valsRE[i] = y_valsRE[i] + [0] * int(m - rmaxRE[i] + 1)
    # y_vals = y_vals + [0] * int(m - rmax + 1)
    # y_valsRE = y_valsRE + [0] * int(m - rmaxRE + 1)

    hr = [i*3600/n_steps_per_hour for i in range(n_timesteps)]
    x1 = [datetime.utcfromtimestamp(h).strftime("%Y-%m-%dT%H") for h in hr]
    x1 = np.array(x1, dtype='datetime64')
    x2 = [float(i)/float(n_steps_per_hour) for i in range(m+1)]
    
    months = mdates.MonthLocator()  # every month
    monthFmt = mdates.DateFormatter('%b')
    
    for r in rRE:
        r = [float(q)/float(n_steps_per_hour) for q in r] if n_steps_per_hour != 1 else r
    # r = [float(q)/float(n_steps_per_hour) for q in r] if n_steps_per_hour != 1 else r
    # rRE = [float(q)/float(n_steps_per_hour) for q in rRE] if n_steps_per_hour != 1 else rRE
    
    dpi = 200
    # fig, ax1 = plt.subplots(figsize=(2200/dpi, 900/dpi), dpi=dpi)
    # ax1.fill_between(x1, 0, r, alpha=0.3)
    # ax1.fill_between(x1, r, rRE, alpha=0.5)
    # ax1.plot(x1, r, linewidth=1.5)
    # ax1.plot(x1, rRE, linewidth=1.5)
    # ax1.xaxis.set_major_locator(months)
    # ax1.xaxis.set_major_formatter(monthFmt)
    # ax1.set_ylabel('Survived hours')
    # ax1.set_xlabel('Outage start timestep')
    # ax1.legend(['Diesel Only', 'Diesel + RE'])
    # ax1.set_title(project + "Resilience by timestep")

    # plt.ylim((0,float(m+1)/float(n_steps_per_hour)))
    # datemin = np.datetime64(x1[0], 'm')
    # datemax = np.datetime64(x1[-1], 'm') + np.timedelta64(1, 'm')
    # ax1.set_xlim(datemin, datemax)

    # plt.savefig(project + "Resiliency{}.png".format(tag))

    fig, ax2 = plt.subplots(figsize=(2200/dpi, 900/dpi), dpi=dpi)
    for Y in y_valsRE:
        ax2.plot(x2[:672], Y[:672], linewidth=1.5)
    ax2.set_ylabel("Probability of Surviving Outage")
    ax2.set_xlabel("Duration of Outage (hours)")
    ax2.legend(["Optimal, No Added PV","Optimal, With Added PV"])#[name[13:-5] for name in scenario_result_input_files])
    ax2.set_title(project + "Survivability")
    plt.ylim((0,1.1))
    plt.xlim((0,float(672)/float(n_steps_per_hour)))
    # plt.xlim((0,float(m+1)/float(n_steps_per_hour)))
    plt.savefig(project + "Probability of Survival{}.png".format(tag))


if __name__ == '__main__':

    # print_max_system_sizes()
    resilience_main()
    multi_site_summary_xlsx()
    # load_profiles_plot()

    # dir = '.'
    # for file in os.listdir(dir):
    #     if file.endswith(".json"):
    #         path = os.path.join(dir,file)
    #         print("Analyzing results in file: {}".format(path))

    #         results = json.load(open(path))

            #print_summary_stats(results)

            #plot_results(dir, file, results, include_rtm=False)
            #plot_results(dir, file, results, include_rtm=True)

            # if "BAU" not in file and "bau" not in file:
            #     print_PV_stats(results)

            # plot_emissions_vs_PV(dir, file, results)

            #plot_energy_prices(dir,file,results)

            #print("eGRID year one emissions = {}".format(0.4965*np.array(results['outputs']['Scenario']['Site']['ElectricTariff']['year_one_energy_supplied_kwh'])))

            # start = 24*181 # july 1st
            # end = 4344 + 7*24 # 1 week later
            # print(np.any((grid_to_stor[start:end]+pv_to_stor[start:end]) * stor_to_load[start:end]))
            # print(np.count_nonzero((grid_to_stor[start:end]+pv_to_stor[start:end]) * stor_to_load[start:end]))
            # print(grid_to_stor[start:end]+pv_to_stor[start:end])
            # print(stor_to_load[start:end])