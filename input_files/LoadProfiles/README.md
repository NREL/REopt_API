This folder contains load data generated from EnergyPlus building models of the DOE commercial reference buildings for cities which represent different ASHRAE climate zones (256 files per folder). Each of the four folders (Electric, Cooling, SpaceHeating, and DHW) contains normalized hourly profiles (8760 hours) representing the fraction of the annual energy that is the load for each hour. 

The SpaceHeating and DHW (domestic hot water) normalized profiles are slightly different, as described below. The other files in the folder contain annual energy values for DHW, SpaceHeating, combined DHW+SpaceHeating, and cooling (electric consumption from an electric chiller, described more below). The annual_heating_stats.csv contains additional data for heating load for future use.

Folders:
- Electric
    - This is the total facility electric load
    - The normalized profiles are the fraction of `LoadProfile.annual_kwh` for each hour
- Cooling
    - This is a subset of the total facility electric load that is consumed for cooling by the electric chiller plant
    - The normalized profiles are the fraction of `LoadProfileChillerThermal.annual_tonhour`
- SpaceHeating
    - This is a subset of the total facility heating gas load that is consumed for space heating
    - The normalized profiles are the fraction of the annual **total** facility gas load `LoadProfileBoilerFuel.annual_mmbtu`
- DHW
    - This is a subset of the total facility heating gas load  that is consumed for domestic hot water
    - The normalized profiles are the fraction of the annual **total** facility gas load `LoadProfileBoilerFuel.annual_mmbtu`

Files:
- reference_cooling_kwh.json
    - The annual electric energy (in units of kWh) consumption by the electric chiller cooling plant
- space_heating_annual_mmbtu.json, dhw_annual_mmbtu.json, total_heating_annual_loads.json
    - The annual fuel energy (in units of MMBtu) for space heating, DHW, and total space heating plus DHW, respectively
- space_heating_fraction_flat_load.json
    - Flat loads (and altnerative schedule-based flat loads) annual energy values are not actually based on EnergyPlus models, so the average annual energy values across all building types for each climate zones are used to estimate the flat load annual energy values
    - This is the average space heating annual fuel energy divided by the average total heating annual fuel energy
- annual_heating_stats.csv
    - This file is not currently used, but it contains data to derive the fraction of total heating fuel consumption divided by the total fuel consumption (including non-heating fuel consumption) at the facility.
    - This data will be used in the future to allow the user to enter their **total fuel** consumption (the normal data they have) and leverage this data to derive the addressable heating load portion of their total fuel data.