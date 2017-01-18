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
-- _Options for dropdown_ (pass integer 0,1,2,3,4 to API):
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
