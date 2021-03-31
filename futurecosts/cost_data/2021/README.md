## PV Costs from NREL Annual Technology Baseline
Steps to create future costs for solar PV systems from the 2020 ATB Data Excel spreadsheet:
1. Go to the `Solar - PV Dist. Comm` tab
2. Select `CustomCRP` in the `Choose a Capital Recovery Period (CRP)` box and enter `25` years.
3. Click `Apply CRP to all Technologies`
4. Select `Market Factor Financials` in the `Financial Assumption` box
5. Click `Apply Finances to all Technologies`
6. Take `CAPEX` and `Fixed Operations and Maintenance Expenses` from the `Moderate` rows in `Future Projections` tables (any region since all regions show the same price)
The values from this process are saved in ATB_2021_PV_costs.csv.