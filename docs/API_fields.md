# Site Information

- Site location: ```latitude, longitude```  
- Land Area Available (acres): ```land_area```  
- Roofspace Available (square feet): ```roof_area```  

# Electricity
If user selects building type, then require input of "Annual Electric Load (kWh).  Otherwise, user can upload their own load profile (a file with 8760 lines of kW values).  If they upload their own file, they must also specify the year of the load (to properly align days-of-the week).  

For the electricity rate, the user shall select a rate from URDB, which is queried based on their entered location.  The web app will pass along the urdb json to the API.  

- Electricity rate (user selects from URDB): ```urdb_rate```  
- Type of building (dropdown): ```load_profile_name```  
-- _Options for dropdown_:  
  * Small Office  
  * Medium Office  
  * Large Office  
  * Warehouse  
  * Midrise Apartment  
  * Small Hotel  
  * Large Hotel  
  * Hospital  
  * Strip Mall  
  * Supermarket  
  * Retail Store  
  * Primary School  
  * Secondary School  
  * Outpatient  
  * Fast Food Restaurant  
  * Full Service Restaurant  
  * Flat Load  
- Annual Electric Load (kWh): ```load_size```  
- Upload hourly load (kW): ```load_8760_kw```  
- Year of uploaded load (kW): ```load_year```  
- Net metering limit (kW): ```net_metering_limit```  
- Sellback rate avove net metering ($/kWh) ```wholesale_rate```  
- Interconnection limit (kW) ```interconnection_limit```  

# Photovoltaic

## Technology
- Minimum size desired (kW) - ```pv_kw_min```  
- Maximum size desired (kW) - ```pv_kw_max```  
- Module type (dropdown) - ```module_type```  
-- _Options for dropdown_ (pass integer 0,1,2 to API):  
  * Standard (0)    
  * Premium (1)  
  * Thin film (2)  
- Array Azimuth (degrees) - ```azimuth```
- Array Tilt (degrees) - ```tilt```
- Array Type (dropdown) - ```array_type```  
 _Options for dropdown_ (pass integer 0,1,2,3,4 to API):
  * Fixed - Open Rack (0)  
  * Fixed - Roof Mounted (1)
  * 1-Axis (2)  
  * 1-Axis Backtracking (3)  
  * 2-Axis (4)  
- Losses (%) - ```losses```
- DC-AC ratio - ```dc_ac_ratio```
- Ground coverage ratio - ```gcr```

## Cost and Incentives
- System installed cost ($/kW) - ```pv_cost```
- Operating and maintenance ($/kW-year) - ```pv_om```
- Federal percentage based incentive (%) - ```pv_pbi_federal```  
- Federal maximum incentive ($) - ```pv_pbi_federal_max```  
- State percentage based incentive (%) - ```pv_pbi_state```  
- State maximum incentive (%) - ```pv_pbi_state_max```  
- State rebate ($/kW) - ```pv_rebate_state```  
- State maximum rebate ($) - ```pv_rebate_state_max```  
- Utility rebate ($) - ```pv_rebate_utility```  
- Utility maximum rebate ($) - ```pv_rebate_utility_max```
- Production incentive ($/kWh) - ```pv_production_incentive```
- Production incentive duration (years) - ```pv_production_incentive_years```
- Production incentive size limit (kW) - ```pv_production_incentive_max_kw```
- MACRs Schedule (years), dropdown - ```pv_macrs_schedule```  
 _Options for dropdown_ (pass integer 0, 3, 5, 7 to API):  
  * 0  
  * 3  
  * 5  
  * 7  

# Battery

## Technology

- Minimum power desired (kW) - ```batt_kw_min```  
- Maximum power desired (kW) - ```batt_kw_max```  
- Minimum capacity at full power (kWh) ` ```batt_kwh_min```  
- Maximum capacity at full power (kWh) - ```batt_kwh_max```  
- Battery internal efficiency (%) - ``batt_efficiency```  
- Inverter efficiency (%) - ```batt_inverter_efficiency```  
- Rectifier efficiency (%) - ```batt_rectifier_efficiency```  
- Minimum state of charge (%) - ```batt_soc_min```  
- Grid can charge battery? (checkbox) - ```batt_can_gridcharge```  

## Cost and Incentives
- Capacity ($/kW) - ```batt_cost_kwh```  
- Power electronics ($/kW) - ```batt_cost_kw```  
- Replacement cost escalation (%) - ```batt_replacement_cost_escalation```  
- Federal percentage based incentive (%) - ```batt_pbi_federal```  
- Federal maximum incentive ($) - ```batt_pbi_federal_max```  
- State percentage based incentive (%) - ```batt_pbi_state```  
- State maximum incentive (%) - ```batt_pbi_state_max```  
- MACRs Schedule (years), dropdown - ```pv_macrs_schedule```  
- -- _Options for dropdown_ (pass integer 0, 3, 5, 7 to API):  
  * 0  
  * 3  
  * 5  
  * 7  


# Financial Inputs
The "developer" inputs should be grayed out or unavailable unless the "Third-party owner" box is checked.  

- Analysis period (years) - ```analysis_period```  
- Electricity escalation rate (%) - ```rate_escalation```  
- Inflation rate (%) - ```rate_inflation```  
- Real Discount rate (%) - ```offtaker_discount_rate```  
- Owner tax rate (%) - ```offtaker_tax_rate```  
- Third-party owner (check_box or something) - ```third_party_owned```  
-- Developer real discount rate (%) - ```owner_discount_rate```  
-- Developer tax rate (%) - ```owner_tax_rate```  

# Scalar Outputs
- Solution status - ```status```  
- Lifecycle cost ($) - ```lcc```  
- Net present value ($) - ```npv```
- Interal rate of return (%) - ```irr```
- Year 1 energy supplied from grid (kWh) - ```utility_kwh```  
- Recommended PV size (kW) - ```pv_kw```
- Recommended battery power (kW) - ```batt_kw```  
- Recommended battery capacity (kW) - ```batt_kwh```  
- Year 1 energy cost ($) - ```year_one_energy_cost```  
- Year 1 demand cost ($) - ```year_one_demand_cost```

# Time series outputs
- Year 1 electric load time series (kW) - ```year_one_electric_load_series```  
- Year 1 PV power to battery time series (kW) - ```year_one_pv_to_battery_series```  
- Year 1 PV power to electric load time series (kW) - ```year_one_pv_to_load_series```
- Year 1 PV power to grid time series (kW) - ```year_one_pv_to_grid_series```
- Year 1 grid power to electric load time series (kW) - ```year_one_grid_to_load_series```  
- Year 1 grid power to battery (kW) - ```year_one_grid_to_battery_series```  
- Year 1 battery state-of-charge time series (%) - ```year_one_battery_soc_series```  
- Year 1 battery power to electric electric load time series (kW) - ```year_one_battery_to_load_series```  
- Year 1 battery power to grid time series (kW) - ```year_one_battery_to_grid_series```  

