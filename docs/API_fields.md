# Site Information
- Site location: ```latitude, longitude```  
- Land Area Available (acres): ```land_area```  
- Roofspace Available (square feet): ```roof_area```  
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

# Electricity
If user selects building type, then require input of "Annual Electric Load (kWh).  Otherwise, user can upload their own load profile (a file with 8760 lines of kW values).  If they upload their own file, they must also specify the year of the load (to properly align days-of-the week).  

For the electricity rate, the user shall select a rate from URDB, which is queried based on their entered location.  The web app will pass along the urdb json to the API.  
 
# Financial Inputs
The "third-party" inputs should be grayed out or unavailable unless the "Third-party owner" box is checked.  

- Analysis period (years) - ```analysis_period```  
- Third-party owner (check_box or something) - ```third_party_owned```  
- Host real Discount rate (%) - ```offtaker_discount_rate```  
- Host tax rate (%) - ```offtaker_tax_rate```  
- Third-party owner real discount rate (%) - ```owner_discount_rate```  
- Third-party owner tax rate (%) - ```owner_tax_rate```  
- Electricity escalation rate (%) - ```rate_escalation```  
- Inflation rate (%) - ```rate_inflation```   

# Grid Connection Inputs
- Net metering limit (kW): ```net_metering_limit```  
- Sellback rate avove net metering ($/kWh) ```wholesale_rate```  
- Interconnection limit (kW) ```interconnection_limit```  

# Photovoltaic

## PV Cost 
- System installed cost ($/kW) - ```pv_cost```
- Operating and maintenance ($/kW-year) - ```pv_om```

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



## PV Capital Cost Based Incentives
- PV Federal percentage based incentive (%) - ```pv_itc_federal```  
- PV State percentage based incentive (%) - ```pv_itc_state```  
- PV Utility percentage based incentive (%) - ```pv_itc_utility```  
- PV Federal maximum incentive ($) - ```pv_itc_federal_max```  
- PV State maximum incentive (%) - ```pv_itc_state_max```  
- PV Utility maximum incentive (%) - ```pv_itc_utility_max```  
- PV Federal rebate ($/kW) - ```pv_rebate_federal```  
- PV State rebate ($/kW) - ```pv_rebate_state```  
- PV Utility rebate ($/kW) - ```pv_rebate_utility```  
- PV Federal maximum rebate ($) - ```pv_rebate_federal_max```  
- PV State maximum rebate ($) - ```pv_rebate_state_max```  
- PV Utility maximum rebate ($) - ```pv_rebate_utility_max```

## PV Production Based Incentives

- PV production based incentive ($/kWh) - ```pv_pbi```  
- PV production based incentive max ($) - ```pv_pbi_max```  
- PV production based incentive year duration (years) - ```pv_pbi_years```  
- PV production based incentive max system size (kW) - ```pv_pbi_system_max```  

## PV MACRS
- MACRs Schedule (years), dropdown - ```pv_macrs_schedule```  
 _Options for dropdown_ (pass integer 0, 3, 5, 7 to API):  
  * 0  
  * 3  
  * 5  
  * 7  

# Battery

## Battery Costs
- Energy capacity ($/kWh) - ```batt_cost_kwh```  
- Power electronics ($/kW) - ```batt_cost_kw```  
- Energy capacity replacement cost ($/kWh) - ```batt_replacement_cost_kwh```  
- Energy capacity replacement year (year) - ```batt_replacement_year_kwh```  
- Power electronics replacement cost ($/kW) - ```batt_replacement_cost_kw```  
- Power electronics replacement year (year) - ```batt_replacement_year_kw```  

## Technology
- Minimum power desired (kW) - ```batt_kw_min```  
- Maximum power desired (kW) - ```batt_kw_max```  
- Minimum capacity at full power (kWh) ` ```batt_kwh_min```  
- Maximum capacity at full power (kWh) - ```batt_kwh_max```  
- Battery internal efficiency (%) - ``batt_efficiency```  
- Inverter efficiency (%) - ```batt_inverter_efficiency```  
- Rectifier efficiency (%) - ```batt_rectifier_efficiency```  
- Minimum state of charge (%) - ```batt_soc_min```  
- Initial state of charge (%) - ```batt_soc_init```
- Grid can charge battery? (checkbox) - ```batt_can_gridcharge```  



## Battery Capital Cost Incentives  
- Battery Federal percentage based incentive (%) - ```batt_itc_federal```  
- Battery State percentage based incentive (%) - ```batt_itc_state```  
- Battery Utility percentage based incentive (%) - ```batt_itc_utility```  
- Battery Federal maximum incentive ($) - ```batt_itc_federal_max```  
- Battery State maximum incentive (%) - ```batt_itc_state_max```  
- Battery Utility maximum incentive (%) - ```batt_itc_utility_max```  
- Battery Federal rebate ($/kW) - ```batt_rebate_federal```  
- Battery State rebate ($/kW) - ```batt_rebate_state```  
- Battery Utility rebate ($/kW) - ```batt_rebate_utility```  
- Battery Federal maximum rebate ($) - ```batt_rebate_federal_max```  
- Battery State maximum rebate ($) - ```batt_rebate_state_max```  
- Battery Utility maximum rebate ($) - ```batt_rebate_utility_max```

## Battery MACRS
- MACRs Schedule (years), dropdown - ```batt_macrs_schedule```  
- -- _Options for dropdown_ (pass integer 0, 3, 5, 7 to API):  
  * 0  
  * 3  
  * 5  
  * 7  

# Scalar Outputs
- Solution status - ```status```  
- Lifecycle cost ($) - ```lcc```  
- Net present value ($) - ```npv```
- Interal rate of return (%) - ```irr```
- Year 1 energy supplied from grid (kWh) - ```year_one_utility_kwh```  
- Recommended PV size (kW) - ```pv_kw```
- Recommended battery power (kW) - ```batt_kw```  
- Recommended battery capacity (kW) - ```batt_kwh```  
- Average PV energy produced per year (kWh) - ```average_yearly_pv_energy_produced```  
- Net capital costs plus operations and maintenence cost ($) - ```net_capital_costs_plus_om```  
- Total demand cost ($) - ```total_demand_cost```  
- Total energy cost ($) - ```total_energy_cost```  
- Total payments to third party developer ($) - ```total_payments_to_third_party_owner```  
- Year 1 energy cost ($) - ```year_one_energy_cost```  
- Year 1 demand cost ($) - ```year_one_demand_cost```  
- Year 1 payement to third party owner ($) - ```year_one_payments_to_third_party_owner```  
- Year 1 energy cost business as usual ($) - ```year_one_energy_cost_bau```
- Year 1 demand cost business as usual ($) - ```year_one_demand_cost_bau```
- Year 1 datetime start (datetime) - ```year_one_datetime_start```  
- Time steps per hour: ```time_steps_per_hour```  

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

