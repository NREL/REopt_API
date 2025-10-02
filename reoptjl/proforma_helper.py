import xlsxwriter
import json
import numpy as np
from copy import copy

# print(xlsxwriter.__version__)

# #### LOAD FILE FOR TESTING
# with open('samples/26_evaluation_results.json') as f:
#     results = json.load(f)

def proforma_helper(results, output):

    #### HELPER FUNCTIONS
    # Generic function to pull values from results dict or get 0 instead of Null
    def get_value(one:str, two:str, three:str):
        try:
            if two in results[one].keys():
                if results[one][two][three] == None:
                    return 0.0
                if type(results[one][two][three]) is list:
                    if two == 'CHP':
                        return results[one][two][three]
                    else:
                        return sum(results[one][two][three]) # sum any lists
                if type(results[one][two][three]) == str: # API bugs?
                    return float(results[one][two][three])
                return results[one][two][three]
            else:
                return 0.0
        except:
            # print('error on ', one,two,three)
            return 0.0

    ## CHP installed cost determination
    def get_chp_installed_cost_us_dollars():
        if (get_value('outputs','CHP','size_kw') or 0) > 0:
            #replicated logic from reo/process_results.py
        
            # Calculate capital cost from cost curve list
            
            cost_list = get_value('inputs','CHP','installed_cost_per_kw') or []
            size_list = get_value('inputs','CHP','tech_sizes_for_cost_curve') or []
            
            # CHP size object defined below, but use the chp_size_kw_cell to preserve spreadsheet referencing
            chp_size = get_value('outputs','CHP','size_kw')
            if len(cost_list) > 1: # More than 1 cost values
                if (chp_size or 0) <= size_list[0]: # smaller than the lower tech size for cost curve
                    chp_installed_cost_us_dollars = cost_list[0]*chp_size
                elif (chp_size or 0) > size_list[-1]: # larger than the larger tech size for cost curve
                    chp_installed_cost_us_dollars = cost_list[-1]*chp_size
                else:
                    for s in range(1, len(size_list)):
                        if (chp_size > size_list[s-1]) and (chp_size <= size_list[s]):
                            slope = (cost_list[s] * size_list[s] - cost_list[s-1] * size_list[s-1]) / \
                                        (size_list[s] - size_list[s-1])
                            chp_installed_cost_us_dollars = cost_list[s-1]*size_list[s-1] + (chp_size - size_list[s-1])*slope
            else:
                chp_installed_cost_us_dollars = cost_list[0]*chp_size
        else:
            chp_installed_cost_us_dollars = 0.0
        
        return chp_installed_cost_us_dollars

    # Add row with 2 elements in Col A and B.
    # Return shifted row indexer
    def add_inputs_outputs_defined_cell(start_row, shift, rowlabel, value, format, define_name):
        
        inandout_sheet.write_row('A'+str(shift+start_row), [rowlabel, value], d[format])
        if define_name is not None:
            proforma.define_name(define_name, '=\'Inputs and Outputs\'!$B$'+str(start_row+shift)+'')
        shift += 1
        return shift

    # proforma.define_name(define_name, '=\'Inputs and Outputs\'!$B$'+str(start_row+shift)+'')
    ## Add multiple values in one go, define cells of interest outside this function.
    def add_multiple_inputs_outputs_defined_cell(start_row, shift, values, format):
        inandout_sheet.write_row('A'+str(shift+start_row), values, d[format])
        shift += 1
        return shift

    ## OPERATING EXPENSES
    def add_operating_expenses(row, row_label, formula_str):
        optcashf_sheet.write_row('A'+str(row), [row_label]+[None]+[formula_str + base_upper_case_letters[i]+str(2) for i in range(2,27)], o['text_format'])
        return row + 1

    #### STYLES SECTION
    def create_styles(proforma):
        d = {}
        d['header_format'] = proforma.add_format(
            {
                'font_name': 'Segoe UI',
                'font_size': 14,
                'bold': True,
                'font_color': 'white',
                'bg_color': 'black'
            }
        )
        d['header_format_right'] = proforma.add_format(
            {
                'font_name': 'Segoe UI',
                'font_size': 14,
                'bold': True,
                'font_color': 'white',
                'bg_color': 'black'
            }
        )
        d['header_format'].set_top(1)
        d['header_format'].set_bottom(1)
        d['header_format'].set_left(1)
        d['header_format_right'].set_top(1)
        d['header_format_right'].set_bottom(1)
        d['header_format_right'].set_right(1)
        d['subheader_format'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'bold': True,
            'font_color': 'black',
            'bg_color': 'C2C5CC'
        })
        d['subheader_format_mid'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'bold': True,
            'font_color': 'black',
            'bg_color': 'C2C5CC',
            'align': 'center'
        })
        d['subheader_format_right'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'bold': True,
            'font_color': 'black',
            'bg_color': 'C2C5CC',
            'align': 'center'
        })
        d['subheader_format'].set_top(1)
        d['subheader_format'].set_bottom(1)
        d['subheader_format'].set_left(1)
        d['subheader_format_mid'].set_top(1)
        d['subheader_format_mid'].set_bottom(1)
        d['subheader_format_right'].set_top(1)
        d['subheader_format_right'].set_bottom(1)
        d['subheader_format_right'].set_right(1)
        d['text_format'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black'
        })
        d['text_format_center'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'align': 'center'
        })
        d['text_format_indent'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'indent': 1
        })
        d['text_format_indent_2'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'indent': 2
        })
        d['text_format_mid'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black'
        })
        d['text_format_right'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black'
        })
        d['text_format_right_center_align'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'align': 'center'
        })
        d['text_format_right_decimal'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'num_format' : '0.000'
        })
        d['text_format_right_percentage'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'num_format' : '0%'
        })
        d['scientific_text'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'border':1,
            'num_format':11
        })
        d['text_format'].set_top(1)
        d['text_format'].set_bottom(1)
        d['text_format'].set_left(1)
        d['text_format_center'].set_top(1)
        d['text_format_center'].set_bottom(1)
        d['text_format_center'].set_left(1)
        d['text_format_indent'].set_top(1)
        d['text_format_indent'].set_bottom(1)
        d['text_format_indent'].set_left(1)
        d['text_format_indent_2'].set_top(1)
        d['text_format_indent_2'].set_bottom(1)
        d['text_format_indent_2'].set_left(1)
        d['text_format_mid'].set_top(1)
        d['text_format_mid'].set_bottom(1)
        d['text_format_right'].set_top(1)
        d['text_format_right'].set_bottom(1)
        d['text_format_right'].set_right(1)
        d['text_format_right'].set_num_format('#,##0')
        d['text_format_right_decimal'].set_top(1)
        d['text_format_right_decimal'].set_bottom(1)
        d['text_format_right_decimal'].set_right(1)
        d['text_format_right_center_align'].set_top(1)
        d['text_format_right_center_align'].set_bottom(1)
        d['text_format_right_center_align'].set_right(1)
        d['text_format_right_percentage'].set_top(1)
        d['text_format_right_percentage'].set_bottom(1)
        d['text_format_right_percentage'].set_right(1)
        d['proj_fin_format'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'bg_color': 'AEC9EB',
            'border':1,
            'align': 'center',
            'num_format' : '#,##0'
        })
        d['proj_fin_format_spp'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'bg_color': 'AEC9EB',
            'border':1,
            'align': 'center',
            'num_format' : '#,##0.00'
        })
        d['proj_fin_format_decimal'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'bg_color': 'AEC9EB',
            'border':1,
            'align': 'center',
            'num_format' : '0.00%'
        })
        d['year_0_format'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'bg_color': 'C2C5CC',
            'border':1,
            'align': 'center',
            'num_format' : '#,##0'
        })
        d['bold_text_format'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'bold': True
        })
        d['standalone_bold_text_format'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'bold': True
        })
        d['standalone_bold_text_format'].set_border(1)

        # Formats specifically for optimal worksheet.
        o = {}
        o['header_format'] = proforma.add_format(
            {
                'font_name': 'Segoe UI',
                'font_size': 14,
                'bold': False,
                'font_color': 'white',
                'bg_color': 'black'
            }
        )
        o['year_format'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'bold': True,
            'font_color': 'black',
            'bg_color': 'C2C5CC'
        })
        o['year_format'].set_top(1)

        o['subheader_format'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'bold': True,
            'font_color': 'black',
            'bg_color': 'C2C5CC'
        })
        o['subheader_format'].set_top(1)
        o['subheader_format'].set_bottom(1)

        o['text_format'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'num_format': '#,##0'
        })

        o['text_format_decimal'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'num_format': '0.0'
        })

        o['text_format_indent'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'indent': 1
        })

        o['text_format_2'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'num_format': '#,##0'
        })
        o['text_format_2'].set_top(1)
        o['text_format_2'].set_bottom(1)


        o['standalone_bold_text_format'] = proforma.add_format({
            'font_name': 'Calibri',
            'font_size': 10,
            'font_color': 'black',
            'bold': True,
            'num_format': '#,##0'
        })

        return d, o

    base_upper_case_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                            'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA']

    ## OPTIMAL SYSTEM DESIGN
    def optimal_system_design(start_row, shift, discount_rate_fieldname):
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'PV Nameplate capacity (kW), purchased', get_value('outputs','PV','size_kw')-get_value('inputs','PV','existing_kw'), 'text_format', 'PV_purchased_kw')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'PV Nameplate capacity (kW), existing', get_value('inputs','PV','existing_kw'), 'text_format', 'PV_existing_kw')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'PV degradation rate (%/year)', 100*get_value('inputs','PV','degradation_fraction'), 'text_format', 'PV_degradation_per_year')
        
        if 'PV' in results['outputs'].keys():
            lcoe_formula = '=ROUND(((PV_purchased_installed_costs + -1*(NPV('+discount_rate_fieldname+'/100, Purchased_PV_OM_series_cost)) - SUM(PV_total_CBI, PV_total_IBI, NPV('+discount_rate_fieldname+'/100,Purchased_PV_PBI_combined), NPV('+discount_rate_fieldname+'/100,PV_itc_amount), NPV('+discount_rate_fieldname+'/100,Purchased_PV_income_tax_savings))) ) / ((NPV('+discount_rate_fieldname+'/100, Total_PV_annual_gen_kwh_range) - NPV('+discount_rate_fieldname+'/100,Existing_PV_annual_gen_kwh_range))), 4)'
        else:
            lcoe_formula = '=0.0'
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'PV LCOE of New Capacity ($/kWh), nominal', lcoe_formula, 'text_format_right_decimal', 'PV_calculated_LCOE')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Wind Nameplate capacity (kW), purchased', get_value('outputs','Wind','size_kw'), 'text_format', 'Wind_purchased_kw')

        if 'Wind' in results['outputs'].keys():
            lcoe_formula = '=ROUND((Wind_installed_costs + (-1 * NPV('+discount_rate_fieldname+'/100,Wind_OM_series_cost)) - SUM(Wind_total_CBI, Wind_total_IBI, NPV('+discount_rate_fieldname+'/100,Wind_PBI_combined), NPV('+discount_rate_fieldname+'/100,Wind_itc_amount), NPV('+discount_rate_fieldname+'/100, Wind_income_tax_savings))) / NPV('+discount_rate_fieldname+'/100, Wind_annual_gen_kwh_range),4)'
        else:
            lcoe_formula = '=0.0'
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Wind LCOE ($/kWh), nominal', lcoe_formula, 'text_format_right_decimal', 'Wind_calculated_LCOE')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Backup Generator Nameplate capacity (kW), purchased', get_value('outputs','Generator','size_kw')-get_value('inputs','Generator','existing_kw'), 'text_format', 'Generator_purchased_kw')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Backup Generator Nameplate capacity (kW), existing', get_value('inputs','Generator','existing_kw'), 'text_format', 'Generator_existing_kw')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Battery power (kW)', get_value('outputs','ElectricStorage','size_kw'), 'text_format', 'Battery_purchased_kw')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Battery capacity (kWh)', get_value('outputs','ElectricStorage','size_kwh'), 'text_format', 'Battery_purchased_kwh')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'CHP capacity (kW)', get_value('outputs','CHP','size_kw'), 'text_format', 'CHP_purchased_kw')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Absorption chiller capacity (tons)', get_value('outputs','AbsorptionChiller','size_ton'), 'text_format', 'AbsChl_purhcased_tons')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'ASHP space heater capacity (tons)', get_value('outputs','ASHPSpaceHeater','size_ton'), 'text_format', 'ASHP_spaceheater_tons')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'ASHP water heater capacity (tons)', get_value('outputs','ASHPWaterHeater','size_ton'), 'text_format', 'ASHP_waterheater_tons')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Chilled water TES capacity (gallons)', get_value('outputs','ColdThermalStorage','size_gal'), 'text_format', 'ColdTES_size_gal')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Hot water TES capacity (gallons)', get_value('outputs','HotThermalStorage','size_gal'), 'text_format', 'HotTES_size_gal')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Steam turbine capacity (kW)', get_value('outputs', 'SteamTurbine', 'size_kw'), 'text_format', 'SteamTurbine_size_kw')

        ghp_size = 0.0
        heat_exchanger_size = 0.0
        if get_value('outputs','GHP','ghp_option_chosen') == 1:
            try:
                heat_exchanger_size = results['outputs']['GHP']['ghpghx_chosen_outputs']['number_of_boreholes']*results['outputs']['GHP']['ghpghx_chosen_outputs']['length_boreholes_ft']
            except:
                heat_exchanger_size = 0
            
            if results['outputs']['GHP']['size_heat_pump_ton'] == None:
                ghp_size = 0.0
            else:
                ghp_size = get_value('outputs','GHP','size_heat_pump_ton')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'GHP heat pump capacity (ton)', ghp_size, 'text_format', 'GHP_capacity_tons')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'GHP ground heat exchanger size (ft)', heat_exchanger_size, 'text_format', 'GHX_size_ft')

        return shift+start_row

    ## ANNUAL RESULTS
    def annual_results(start_row, shift):
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Present value of annual Business as Usual electric utility bill ($/year)', get_value('outputs','ElectricTariff','year_one_bill_before_tax_bau'), 'text_format', 'BAU_annual_electricity_bill')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Present value of annual Business as Usual export credits ($/year)', get_value('outputs','ElectricTariff','year_one_export_benefit_before_tax_bau'), 'text_format', 'BAU_annual_export_to_grid_benefits')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Present value of annual Optimal electric utility bill($/year)', get_value('outputs','ElectricTariff','year_one_bill_before_tax'), 'text_format', 'OPT_annual_electricity_bill')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Present value of annual Optimal export credits ($/year)', get_value('outputs','ElectricTariff','year_one_export_benefit_before_tax'), 'text_format', 'OPT_annual_export_to_grid_benefits')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Existing PV electricity produced (kWh), Year 1', get_value('outputs','PV','year_one_energy_produced_kwh_bau'), 'text_format', 'Existing_PV_gen_year1_kwh')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Total PV optimal electricity produced (kWh), Year 1', get_value('outputs','PV','year_one_energy_produced_kwh'), 'text_format', 'Total_PV_gen_year1_kwh')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'PV optimal electricity produced (kWh), Annual Average', get_value('outputs','PV','annual_energy_produced_kwh'), 'text_format', 'Total_PV_annual_gen_kwh')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Nominal annual optimal wind electricity produced (kWh/year)', get_value('outputs','Wind','annual_energy_produced_kwh'), 'text_format', 'Wind_annual_electricity_gen_kwh')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Nominal annual optimal backup generator electricity produced (kWh/year)', get_value('outputs','Generator','annual_energy_produced_kwh'), 'text_format', 'Generator_annual_electricity_gen_kwh')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Nominal annual BAU backup generator electricity produced (kWh/year)', get_value('outputs','Generator','annual_energy_produced_kwh_bau'), 'text_format', 'Generator_annual_electricity_gen_kwh_bau')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'CHP annual optimal electricity produced (kWh/year)', get_value('outputs','CHP','annual_electric_production_kwh'), 'text_format', 'CHP_annual_electricity_gen_kwh')

        runtime_vec = 0.0
        try:
            runtime_vec = [1 for i in (results['outputs']['CHP']['electric_production_series_kw'] or []) if i > 0]
        except:
            runtime_vec = [0.0]
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'CHP annual runtime (hours/year)', sum(runtime_vec)/(results['inputs']['Settings']['time_steps_per_hour'] or 1), 'text_format', 'CHP_annual_runtime_hrs_per_year')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Steam turbine annual optimal electricity produced (kWh/year)', get_value('outputs','SteamTurbine','annual_electric_production_kwh'), 'text_format', 'STM_annual_elec_gen_kwh')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Total optimal electricity produced (kWh/year)', '=Total_PV_gen_year1_kwh+Wind_annual_electricity_gen_kwh+CHP_annual_electricity_gen_kwh+STM_annual_elec_gen_kwh-Existing_PV_gen_year1_kwh', 'text_format', 'Total_opt_electricity_gen_kwh')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Present value of annual Business as Usual boiler fuels utility bill ($/year)', get_value('outputs','ExistingBoiler','year_one_fuel_cost_before_tax_bau'), 'text_format', 'BAU_boiler_fuel_bill_annual_sum')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Present value of annual Optimal boiler fuels utility bill ($/year)', get_value('outputs','ExistingBoiler','year_one_fuel_cost_before_tax'), 'text_format', 'OPT_boiler_fuel_bill_annual_sum')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Present value of annual CHP fuels utility bill ($/year)', get_value('outputs','CHP','year_one_fuel_cost_before_tax'), 'text_format', 'CHP_fuels_annual_fuel_bill_sum')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'CHP annual optimal thermal energy produced (MMBtu/year)', get_value('outputs','CHP','annual_thermal_production_mmbtu'), 'text_format', 'CHP_annual_thermal_energy_gen_mmbtu')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Steam turbine annual optimal thermal energy produced (MMBtu/year)', get_value('outputs','SteamTurbine','annual_thermal_production_mmbtu'), 'text_format', 'STM_annual_thermal_energy_gen_mmbtu')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'ASHP SpaceHeater annual optimal thermal energy produced (MMBtu/year)', get_value('outputs','ASHPSpaceHeater','annual_thermal_production_mmbtu'), 'text_format', 'ASHP_spaceheater_annual_thermal_energy_gen_mmbtu')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'ASHP WaterHeater annual optimal thermal energy produced (MMBtu/year)', get_value('outputs','ASHPWaterHeater','annual_thermal_production_mmbtu'), 'text_format', 'ASHP_waterheater_annual_thermal_energy_gen_mmbtu')
        ## Percent renewable electricity calculation
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'PV to site annual optimal electricity delivered (kWh/year)', get_value('outputs','PV','electric_to_load_series_kw'), 'text_format', 'PV_to_site_annual_gen_kwh')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'PV to battery annual optimal electricity delivered (kWh/year)', 0.89*get_value('outputs','PV','electric_to_load_series_kw'), 'text_format', 'PV_to_battery_optimal_gen_kwh')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Annual electric load at site (kWh)', get_value('outputs','ElectricLoad','annual_calculated_kwh'), 'text_format', 'Calculated_annual_site_kwh')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Percent electricity from on-site renewable resources', '=(PV_to_site_annual_gen_kwh + PV_to_battery_optimal_gen_kwh)/Calculated_annual_site_kwh', 'text_format', 'PCT_electricity_from_onsite_renewable_gen')
        # Percent electricity bill savings calculations
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Percent reduction in annual electricity bill', '=IF(BAU_annual_electricity_bill=0,"N/A",ROUND((BAU_annual_electricity_bill - OPT_annual_electricity_bill)/BAU_annual_electricity_bill,2))', 'text_format', 'PCT_reduction_annual_elec_bill')
        # Percent reduction in annual fuel bill
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Percent reduction in annual fuels bill', '=IF(BAU_boiler_fuel_bill_annual_sum=0,"N/A",ROUND((BAU_boiler_fuel_bill_annual_sum - OPT_boiler_fuel_bill_annual_sum)/BAU_boiler_fuel_bill_annual_sum,2))', 'text_format', 'PCT_reduction_annual_fuel_bill')
        ## Emissions
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Year one total site carbon dioxide emissions (ton CO2)', get_value('outputs','Site','annual_emissions_tonnes_CO2'), 'text_format', 'Year_1_total_site_CO2_emissions_tonnes')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Year one total site carbon dioxide emissions BAU (ton CO2)', get_value('outputs','Site','annual_emissions_tonnes_CO2_bau'), 'text_format', 'BAU_year_1_total_site_CO2_emissions_tonnes')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Year one total carbon dioxide emissions from electric utility purchases (ton CO2)', get_value('outputs','ElectricUtility','annual_emissions_tonnes_CO2'), 'text_format', 'Year_1_grid_purchase_CO2_emissions_tonnes')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Year one total carbon dioxide emissions from electric utility purchases BAU (ton CO2)', get_value('outputs','ElectricUtility','annual_emissions_tonnes_CO2_bau'), 'text_format', 'BAU_year_1_grid_purchase_CO2_emissions_tonnes')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Year one total carbon dioxide emissions from on-site fuel burn (ton CO2)', get_value('outputs','Site','annual_emissions_from_fuelburn_tonnes_CO2'), 'text_format', 'Year_1_onsite_fueldburn_CO2_emissions_tonnes')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Year one total carbon dioxide emissions from on-site fuel burn BAU (ton CO2)', get_value('outputs','Site','annual_emissions_from_fuelburn_tonnes_CO2_bau'), 'text_format', 'BAU_year_1_onsite_fueldburn_CO2_emissions_tonnes')
        return shift+start_row

    ## SYSTEM COSTS
    def system_costs(start_row, shift):
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Total Installed Cost ($)', get_value('outputs','Financial','initial_capital_costs'), 'text_format', 'Total_installed_costs_no_incentives')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'PV Installed Cost ($)', get_value('inputs','PV','installed_cost_per_kw')*(
            get_value('outputs','PV','size_kw')-get_value('inputs','PV','existing_kw')
        ), 'text_format', 'PV_purchased_installed_costs')

        average_elec_load=sum(np.array(results['outputs']['ElectricLoad']['load_series_kw']).astype(float))/len(results['outputs']['ElectricLoad']['load_series_kw'])
        install_cost = get_value('inputs','Wind','installed_cost_per_kw') # get any user provided costs, overwrite if size class and cost are not given.

        if 'Wind' in results['inputs'].keys():
            if results['inputs']['Wind']['size_class'] == '' and results['inputs']['Wind']['installed_cost_per_kw'] == None:
                if average_elec_load <= 12.5:
                    install_cost = 6339.0
                elif average_elec_load <= 100:
                    install_cost = 4760.0
                elif average_elec_load <= 1000:
                    install_cost = 3137.0
                else:
                    install_cost = 2386.0
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Wind Installed Cost ($)', install_cost*get_value('outputs','Wind','size_kw'), 'text_format', 'Wind_installed_costs')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Backup generator Installed Cost ($)', get_value('inputs','Generator','installed_cost_per_kw')*(
            get_value('outputs','Generator','size_kw')-get_value('inputs','Generator','existing_kw')
        ), 'text_format', 'Backup_generator_purchased_installed_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Battery Installed Cost ($)', get_value('inputs','ElectricStorage','installed_cost_per_kwh')*get_value('outputs','ElectricStorage','size_kwh')+get_value('inputs','ElectricStorage','installed_cost_per_kw')*get_value('outputs','ElectricStorage','size_kw'), 'text_format', 'Battery_installed_costs')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'CHP Installed Cost ($)', get_chp_installed_cost_us_dollars(), 'text_format', 'CHP_installed_costs')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Absorption Chiller Installed Cost ($)', get_value('inputs','AbsorptionChiller','installed_cost_per_ton')*get_value('outputs','AbsorptionChiller','size_ton'), 'text_format', 'AbsorptionChiller_installed_costs')

        space_ashp_capex = 0.0
        if get_value('outputs','ASHPSpaceHeater','size_ton') > 0:
            if results['inputs']['ASHPSpaceHeater']['installed_cost_per_ton'] == None:
                space_ashp_capex = 2250
            else:
                space_ashp_capex = results['inputs']['ASHPSpaceHeater']['installed_cost_per_ton']
        
        water_ashp_capex = 0.0
        if get_value('outputs','ASHPWaterHeater','size_ton') > 0:
            if results['inputs']['ASHPWaterHeater']['installed_cost_per_ton'] == None:
                water_ashp_capex = 2250
            else:
                water_ashp_capex = results['inputs']['ASHPWaterHeater']['installed_cost_per_ton']
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'ASHP Space Heater Installed Cost ($)', space_ashp_capex*get_value('outputs','ASHPSpaceHeater','size_ton'), 'text_format', 'ASHPSpaceheater_installed_costs')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'ASHP Water Heater Installed Cost ($)', water_ashp_capex*get_value('outputs','ASHPWaterHeater','size_ton'), 'text_format', 'ASHPWaterheater_installed_costs')

        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Hot water TES Installed Cost ($)', get_value('inputs','HotThermalStorage','installed_cost_per_gal')*get_value('outputs','HotThermalStorage','size_gal'), 'text_format', 'HotTES_installed_costs')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Chilled water TES Installed Cost ($)', get_value('inputs','ColdThermalStorage','installed_cost_per_gal')*get_value('outputs','ColdThermalStorage','size_gal'), 'text_format', 'ColdTES_installed_costs')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Steam turbine Installed Cost ($)', get_value('inputs','SteamTurbine','installed_cost_per_kw'), 'text_format', 'SteamTurbine_installed_costs')
        
        heat_exchanger_size = 0.0
        if get_value('outputs','GHP','ghp_option_chosen') == 1:
            try:
                heat_exchanger_size = results['outputs']['GHP']['ghpghx_chosen_outputs']['number_of_boreholes']*results['outputs']['GHP']['ghpghx_chosen_outputs']['length_boreholes_ft']
            except:
                heat_exchanger_size = 0
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'GHP Installed Cost ($)', get_value('outputs','GHP','size_heat_pump_ton')*get_value('inputs','GHP','installed_cost_heatpump_per_ton') + heat_exchanger_size*get_value('inputs','GHP','installed_cost_ghx_per_ft') + get_value('inputs','GHP','building_sqft')*get_value('inputs','GHP','installed_cost_building_hydronic_loop_per_sqft'), 'text_format', 'GHP_installed_costs')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'GHX Residual Value ($)', get_value('outputs','GHP','ghx_residual_value_present_value'), 'text_format', 'GHX_residual_value')

        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Operation and Maintenance (O&M)', None, 'bold_text_format', 'OM_cost_header_row')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Fixed PV O&M ($/kW-yr)', get_value('inputs','PV','om_cost_per_kw'), 'text_format', 'PV_OM_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Fixed Wind O&M ($/kW-yr)', get_value('inputs','Wind','om_cost_per_kw'), 'text_format', 'Wind_OM_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Fixed Backup Generator O&M ($/kW-yr)', get_value('inputs','Generator','om_cost_per_kw'), 'text_format', 'Generator_fixed_backup_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Variable Backup Generator O&M ($/kWh)', get_value('inputs','Generator','om_cost_per_kwh'), 'text_format', 'Generator_variable_backup_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Diesel fuel used cost ($)', get_value('inputs','Generator','fuel_cost_per_gallon')*get_value('outputs','Generator','annual_fuel_consumption_gal'), 'text_format', 'Diesel_fuel_used_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Diesel BAU fuel used cost ($)', get_value('inputs','Generator','fuel_cost_per_gallon')*get_value('outputs','Generator','annual_fuel_consumption_gal_bau'), 'text_format', 'Diesel_BAU_fuel_used_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Battery replacement cost ($/kW)', get_value('inputs','ElectricStorage','replace_cost_per_kw'), 'text_format', 'Battery_kw_replacement_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Battery kW replacement year', get_value('inputs','ElectricStorage','inverter_replacement_year'), 'text_format', 'Battery_kw_replacement_year')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Battery replacement cost ($/kWh)', get_value('inputs','ElectricStorage','replace_cost_per_kwh'), 'text_format', 'Battery_kwh_replacement_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Battery kWh replacement year', get_value('inputs','ElectricStorage','battery_replacement_year'), 'text_format', 'Battery_kwh_replacement_year')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Fixed CHP O&M cost ($/kW-yr)', get_value('inputs','CHP','om_cost_per_kw'), 'text_format', 'CHP_fixed_OM_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Variable CHP O&M cost ($/kWh)', get_value('inputs','CHP','om_cost_per_kwh'), 'text_format', 'CHP_variable_OM_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Runtime CHP O&M cost ($/kW-rated/run-hour)', get_value('inputs','CHP','om_cost_per_hr_per_kw_rated'), 'text_format', 'CHP_runtime_OM_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Fixed Absorption Chiller O&M cost ($/ton-yr)', get_value('inputs','AbsorptionChiller','om_cost_per_ton'), 'text_format', 'AbsChl_OM_cost')

        ashp_om_per_ton = 0.0
        if get_value('outputs','ASHPSpaceHeater','size_ton') > 0:
            if results['inputs']['ASHPSpaceHeater']['om_cost_per_ton'] == None:
                ashp_om_per_ton = 40
            else:
                ashp_om_per_ton = results['inputs']['ASHPSpaceHeater']['om_cost_per_ton']        

        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Fixed ASHP SpaceHeater O&M cost ($/ton-yr)', ashp_om_per_ton, 'text_format', 'ASHP_spaceheater_OM_cost')

        ashp_om_per_ton = 0.0
        if get_value('outputs','ASHPWaterHeater','size_ton') > 0:
            if results['inputs']['ASHPWaterHeater']['om_cost_per_ton'] == None:
                ashp_om_per_ton = 40
            else:
                ashp_om_per_ton = results['inputs']['ASHPWaterHeater']['om_cost_per_ton']
        
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Fixed ASHP WaterHeater O&M cost ($/ton-yr)', ashp_om_per_ton, 'text_format', 'ASHP_waterheader_OM_cost')

        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Fixed Chilled water TES O&M cost ($/gallon-year)', get_value('inputs','ColdThermalStorage','om_cost_per_gal'), 'text_format', 'ColdTES_OM_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Fixed Hot water TES O&M cost ($/gallon-year)', get_value('inputs','HotThermalStorage','om_cost_per_gal'), 'text_format', 'HotTES_OM_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Fixed Steam Turbine O&M ($/kW-yr)', get_value('inputs','SteamTurbine','om_cost_per_kw'), 'text_format', 'SteamTurbine_fixed_OM_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Variable Steam Turbine O&M ($/kWh)', get_value('inputs','SteamTurbine','om_cost_per_kwh'), 'text_format', 'SteamTurbine_variable_OM_cost')
        shift = add_inputs_outputs_defined_cell(start_row, shift, '  Fixed GHP O&M ($/yr)', get_value('inputs','GHP','building_sqft')*get_value('inputs','GHP','om_cost_per_sqft_year'), 'text_format', 'GHP_fixed_OM_cost')
        return shift + start_row

    ## ANALYSIS PARAMETERS
    def analysis_parameters(start_row, shift, third_party_own):
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Analysis period (years)', get_value('inputs','Financial','analysis_years'), 'text_format', 'Analysis_period_years')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Nominal O&M cost escalation rate (%/year)', 100*get_value('inputs','Financial','om_cost_escalation_rate_fraction'), 'text_format', 'OM_cost_escal_pct')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Nominal electric utility cost escalation rate (%/year)', 100*get_value('inputs','Financial','elec_cost_escalation_rate_fraction'), 'text_format', 'Elec_cost_escal_pct')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Nominal generator fuel cost escalation rate (%/year)', 100*get_value('inputs','Financial','generator_fuel_cost_escalation_rate_fraction'), 'text_format', 'Generator_fuel_cost_escal_pct')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Nominal boiler fuel cost escalation rate (%/year)', 100*get_value('inputs','Financial','boiler_fuel_cost_escalation_rate_fraction'), 'text_format', 'Boiler_fuel_cost_escal_pct')
        shift = add_inputs_outputs_defined_cell(start_row, shift, 'Nominal CHP fuel cost escalation rate (%/year)', 100*get_value('inputs','Financial','chp_fuel_cost_escalation_rate_fraction'), 'text_format', 'CHP_fuel_cost_escal_rate')
        
        if not third_party_own:
            shift = add_inputs_outputs_defined_cell(start_row, shift, 'Nominal discount rate (%/year)', 100*get_value('inputs','Financial','offtaker_discount_rate_fraction'), 'text_format', 'Offtaker_discount_rate')
        else:
            shift = add_inputs_outputs_defined_cell(start_row, shift, 'Nominal third-party discount rate (%/year)', 100*get_value('inputs','Financial','owner_discount_rate_fraction'), 'text_format', 'Developer_discount_rate')
            shift = add_inputs_outputs_defined_cell(start_row, shift, 'Nominal Host discount rate (%/year)', 100*get_value('inputs','Financial','offtaker_discount_rate_fraction'), 'text_format', 'Offtaker_discount_rate')
        
        return start_row+shift

    ## TAX AND INSURANCE PARAMETERS
    def tax_insurance_params(start_row, shift, third_party_own):

        if not third_party_own:
            shift = add_inputs_outputs_defined_cell(start_row, shift, 'Federal income tax rate (%)', 100*get_value('inputs','Financial','offtaker_tax_rate_fraction'), 'text_format', 'Offtaker_tax_rate')
        else:
            shift = add_inputs_outputs_defined_cell(start_row, shift, 'Third-party owner Federal income tax rate (%)', 100*get_value('inputs','Financial','owner_tax_rate_fraction'), 'text_format', 'Developer_tax_rate')
            shift = add_inputs_outputs_defined_cell(start_row, shift, 'Host Federal income tax rate (%)', 100*get_value('inputs','Financial','offtaker_tax_rate_fraction'), 'text_format', 'Offtaker_tax_rate')
        
        return start_row+shift

    ## PV TAX CREDITS AND DIRECT CASH INCENTIVES
    def pv_tax_credits(start_row, shift):
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Investment tax credit (ITC)', None, None, 'Reduces depreciation'
            ], 'bold_text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            ' As percentage', '%', 'Maximum', 'Federal'
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Federal', 100*get_value('inputs','PV','federal_itc_fraction'), 1.0E10, 'Yes'
            ], 'text_format')
        proforma.define_name('PV_federal_itc_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_max_itc_benefit', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_reduces_depreciation', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        return shift + start_row

    ## PV DIRECT CASH INCENTIVES
    def pv_direct_cash_incentives(start_row, shift):
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Investment based incentive (IBI)', None, None, 'Incentive is taxable', 'Reduces depreciation and ITC basis'
            ], 'bold_text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            ' As percentage', '%', 'Maximum ($)', 'Federal', 'Federal'
            ], 'text_format')
        
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  State (percent of total installed cost)', get_value('inputs','PV','state_ibi_fraction'), 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('PV_state_ibi_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_state_ibi_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_state_ibi_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_state_ibi_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Utility (percent of total installed cost)', get_value('inputs','PV','utility_ibi_fraction'), 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('PV_utility_ibi_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_utility_ibi_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_utility_ibi_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_utility_ibi_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Capacity based incentive (CBI)', 'Amount ($/kW)', 'Maximum ($)', None, None
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '   Federal ($/kW)', 0, 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('PV_federal_rebate_per_kw', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_federal_rebate_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_federal_rabete_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_federal_rebate_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  State ($/kW)', 0, 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('PV_state_rebate_per_kw', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_state_rebate_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_state_rebate_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_state_rebate_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Utility ($/kW)', 0, 1.0E10, 'No', 'No'
            ], 'text_format')
        proforma.define_name('PV_utility_rebate_per_kw', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_utility_rebate_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_utility_rebate_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_utility_rebate_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Production based incentive (PBI)', 'Amount ($/kWh)', 'Maximum ($/year)', 'Federal taxable', 'Term (years)', 'System size limit (kW)'
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Combined ($/kWh)', 0, 1.0E9, 'Yes', 1, 1.0E9
            ], 'text_format')
        proforma.define_name('PV_PBI_years', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_PBI_per_kwh', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_PBI_max_benefit', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('PV_PBI_federally_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        return shift + start_row

    ## WIND TAX CREDITS AND DIRECT CASH INCENTIVES
    def wind_tax_credits(start_row, shift):
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Investment tax credit (ITC)', None, None, 'Reduces depreciation'
            ], 'bold_text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            ' As percentage', '%', 'Maximum', 'Federal'
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Federal', 100*get_value('inputs','Wind','federal_itc_fraction'), 1.0E10, 'Yes'
            ], 'text_format')
        proforma.define_name('Wind_federal_itc_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_max_itc_benefit', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_reduces_depreciation', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        return shift + start_row

    ## WIND DIRECT CASH INCENTIVES
    def wind_direct_cash_incentives(start_row, shift):
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Investment based incentive (IBI)', None, None, 'Incentive is taxable', 'Reduces depreciation and ITC basis'
            ], 'bold_text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            ' As percentage', '%', 'Maximum ($)', 'Federal', 'Federal'
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  State (percent of total installed cost)', get_value('inputs','Wind','state_ibi_fraction'), 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('Wind_state_ibi_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_state_ibi_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_state_ibi_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_state_ibi_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Utility (percent of total installed cost)', get_value('inputs','Wind','utility_ibi_fraction'), 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('Wind_utility_ibi_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_utility_ibi_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_utility_ibi_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_utility_ibi_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Capacity based incentive (CBI)', 'Amount ($/kW)', 'Maximum ($)', None, None
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '   Federal ($/kW)', 0, 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('Wind_federal_rebate_per_kw', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_federal_rebate_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_federal_rebate_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_federal_rebate_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  State ($/kW)', 0, '=1.0E10', 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('Wind_state_rebate_per_kw', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_state_rebate_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_state_rebate_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_state_rebate_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Utility ($/kW)', 0, 1.0E10, 'No', 'No'
            ], 'text_format')
        proforma.define_name('Wind_utility_rebate_per_kw', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_utility_rebate_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_utility_rebate_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_utility_rebate_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Production based incentive (PBI)', 'Amount ($/kWh)', 'Maximum ($/year)', 'Federal taxable', 'Term (years)', 'System size limit (kW)'
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Combined ($/kWh)', 0, 1.0E9, 'Yes', 1, 1.0E9
            ], 'text_format')
        proforma.define_name('Wind_PBI_years', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_PBI_per_kwh', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_PBI_max_benefit', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Wind_PBI_federally_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        return shift + start_row

    ## BATTERY TAX CREDITS AND DIRECT CASH INCENTIVES
    def battery_tax_credits(start_row, shift):
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Investment tax credit (ITC)', None, None, 'Reduces depreciation'
            ], 'bold_text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            ' As percentage', '%', 'Maximum', 'Federal'
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Federal', 100*get_value('inputs','ElectricStorage','total_itc_fraction'), 1.0E10, 'Yes'
            ], 'text_format')
        proforma.define_name('Battery_federal_itc_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_max_itc_benefit', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_reduces_depreciation', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        return shift + start_row

    ## BATTERY DIRECT CASH INCENTIVES
    def battery_direct_cash_incentives(start_row, shift):
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Investment based incentive (IBI)', None, None, 'Incentive is taxable', 'Reduces depreciation and ITC basis'
            ], 'bold_text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            ' As percentage', '%', 'Maximum ($)', 'Federal', 'Federal'
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  State (percent of total installed cost)', get_value('inputs','ElectricStorage','state_ibi_fraction'), 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('Battery_state_ibi_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_state_ibi_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_state_ibi_is_taxable', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_state_ibi_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Utility (percent of total installed cost)', get_value('inputs','ElectricStorage','utility_ibi_fraction'), 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('Battery_utility_ibi_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_utility_ibi_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_utility_ibi_is_taxable', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_utility_ibi_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Capacity based incentive (CBI)', 'Amount ($/kW)', 'Maximum ($)', None, None
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '   Total ($/kW)', 0, 1.0E10, 'No', 'No'
            ], 'text_format')
        proforma.define_name('Battery_total_kw_cbi_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_total_kw_cbi_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_kw_cbi_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_kw_cbi_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Total ($/kWh)', 0, '=1.0E10', 'No', 'No'
            ], 'text_format')
        proforma.define_name('Battery_total_kwh_cbi_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_total_kwh_cbi_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_kwh_cbi_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('Battery_kwh_cbi_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        return shift + start_row

    ## CHP TAX CREDITS AND DIRECT CASH INCENTIVES
    def chp_tax_credits(start_row, shift):
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Investment tax credit (ITC)', None, None, 'Reduces depreciation'
            ], 'bold_text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            ' As percentage', '%', 'Maximum', 'Federal'
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Federal', 100*get_value('inputs','CHP','federal_itc_fraction'), 1.0E10, 'Yes'
            ], 'text_format')
        proforma.define_name('CHP_federal_itc_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_max_itc_benefit', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_reduces_depreciation', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        return shift + start_row

    ## CHP DIRECT CASH INCENTIVES
    def chp_direct_cash_incentives(start_row, shift):
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Investment based incentive (IBI)', None, None, 'Incentive is taxable', 'Reduces depreciation and ITC basis'
            ], 'bold_text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            ' As percentage', '%', 'Maximum ($)', 'Federal', 'Federal'
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  State (percent of total installed cost)', get_value('inputs', 'CHP','state_ibi_fraction'), 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('CHP_state_ibi_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_state_ibi_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_state_ibi_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_state_ibi_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Utility (percent of total installed cost)', get_value('inputs','CHP','utility_ibi_fraction'), 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('CHP_utility_ibi_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_utility_ibi_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_utility_ibi_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_utility_ibi_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Capacity based incentive (CBI)', 'Amount ($/kW)', 'Maximum ($)', None, None
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '   Federal ($/kW)', 0, 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('CHP_federal_rebate_per_kw', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_federal_rebate_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_federal_rebate_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_federal_rebate_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  State ($/kW)', 0, '=1.0E10', 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('CHP_state_rebate_per_kw', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_state_rebate_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_state_rebate_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_state_rebate_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Utility ($/kW)', 0, 1.0E10, 'No', 'No'
            ], 'text_format')
        proforma.define_name('CHP_utility_rebate_per_kw', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_utility_rebate_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_utility_rebate_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_utility_rebate_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Production based incentive (PBI)', 'Amount ($/kWh)', 'Maximum ($/year)', 'Federal taxable', 'Term (years)', 'System size limit (kW)'
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Combined ($/kWh)', 0, 1.0E9, 'Yes', 1, 1.0E9
            ], 'text_format')
        proforma.define_name('CHP_PBI_years', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_PBI_per_kwh', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_PBI_max_benefit', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('CHP_PBI_federally_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        return shift + start_row

    ## GHP TAX CREDITS AND DIRECT CASH INCENTIVES
    def ghp_tax_credits(start_row, shift):
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Investment tax credit (ITC)', None, None, 'Reduces depreciation'
            ], 'bold_text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            ' As percentage', '%', 'Maximum', 'Federal'
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Federal', 100*get_value('inputs','GHP','federal_itc_fraction'), 1.0E10, 'Yes'
            ], 'text_format')
        proforma.define_name('GHP_federal_itc_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_max_itc_benefit', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_reduces_depreciation', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        return shift + start_row

    ## GHP DIRECT CASH INCENTIVES
    def ghp_direct_cash_incentives(start_row, shift):
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Investment based incentive (IBI)', None, None, 'Incentive is taxable', 'Reduces depreciation and ITC basis'
            ], 'bold_text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            ' As percentage', '%', 'Maximum ($)', 'Federal', 'Federal'
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  State (percent of total installed cost)', get_value('inputs','GHP','state_ibi_fraction'), 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('GHP_state_ibi_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_state_ibi_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_state_ibi_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_state_ibi_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Utility (percent of total installed cost)', get_value('inputs','GHP','utility_ibi_fraction'), 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('GHP_utility_ibi_fraction', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_utility_ibi_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_utility_ibi_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_utility_ibi_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Capacity based incentive (CBI)', 'Amount ($/kW)', 'Maximum ($)', None, None
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '   Federal ($/kW)', 0, 1.0E10, 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('GHP_federal_rebate_per_kw', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_federal_rebate_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_federal_rebate_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_federal_rebate_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  State ($/kW)', 0, '=1.0E10', 'No', 'Yes'
            ], 'text_format')
        proforma.define_name('GHP_state_rebate_per_kw', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_state_rebate_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_state_rebate_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_state_rebate_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Utility ($/kW)', 0, 1.0E10, 'No', 'No'
            ], 'text_format')
        proforma.define_name('GHP_utility_rebate_per_kw', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_utility_rebate_max', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_utility_rebate_is_taxable', '=\'Inputs and Outputs\'!$D$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_utility_rebate_reduces_basis', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            'Production based incentive (PBI)', 'Amount ($/kWh)', 'Maximum ($/year)', 'Federal taxable', 'Term (years)', 'System size limit (kW)'
            ], 'text_format')
        shift = add_multiple_inputs_outputs_defined_cell(start_row, shift, [
            '  Combined ($/kWh)', 0, 1.0E9, 'Yes', 1, 1.0E9
            ], 'text_format')
        proforma.define_name('GHP_PBI_years', '=\'Inputs and Outputs\'!$E$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_PBI_per_kwh', '=\'Inputs and Outputs\'!$B$'+str(start_row+shift-1)+'')
        proforma.define_name('GHP_PBI_max_benefit', '=\'Inputs and Outputs\'!$C$'+str(start_row+shift-1)+'')
        return shift + start_row

    ## DEPRECIATION SECTION
    def add_tech_depreciation_info(section_end):
        depr_row = ['DEPRECIATION', 'PV', 'WIND', 'BATTERY', 'CHP', 'Absorption Chiller', 'ASHP Space Heater', 'ASHP Water Heater', 'Hot TES', 'Cold TES', 'SteamTurbine', 'GHP']
        section_end += 1
        inandout_sheet.write_row('A'+str(section_end+1), depr_row, d['subheader_format'])
        inandout_sheet.write_row('N'+str(section_end+1), ['MACRS SCHEDULES (INFORMATIONAL ONLY)', None, None, None, None, None, None, None, None], d['subheader_format'])

        section_end += 1
        macrs_option_year_row = copy(section_end+1)
        inandout_sheet.write_row('A'+str(section_end+1), [
            'Federal (years)',
            get_value('inputs', 'PV', 'macrs_option_years'),
            get_value('inputs', 'Wind', 'macrs_option_years'),
            get_value('inputs', 'ElectricStorage', 'macrs_option_years'),
            get_value('inputs', 'CHP', 'macrs_option_years'),
            get_value('inputs', 'AbsorptionChiller', 'macrs_option_years'),
            get_value('inputs', 'ASHPSpaceHeater', 'macrs_option_years'),
            get_value('inputs', 'ASHPWaterHeater', 'macrs_option_years'),
            get_value('inputs', 'HotThermalStorage', 'macrs_option_years'),
            get_value('inputs', 'ColdThermalStorage', 'macrs_option_years'),
            get_value('inputs', 'SteamTurbine', 'macrs_option_years'),
            get_value('inputs', 'GHP', 'macrs_option_years')], d['text_format'])

        macrs_bonus_fraction_row = section_end+1

        inandout_sheet.write_row('N'+str(section_end+1), ['Year', 1,2,3,4,5,6,7,8], d['text_format'])

        section_end += 1
        inandout_sheet.write_row('A'+str(section_end+1), [
            'Federal bonus fraction',
            get_value('inputs', 'PV', 'macrs_bonus_fraction'),
            get_value('inputs', 'Wind', 'macrs_bonus_fraction'),
            get_value('inputs', 'ElectricStorage', 'macrs_bonus_fraction'),
            get_value('inputs', 'CHP', 'macrs_bonus_fraction'),
            get_value('inputs', 'AbsorptionChiller', 'macrs_bonus_fraction'),
            get_value('inputs', 'ASHPSpaceHeater', 'macrs_bonus_fraction'),
            get_value('inputs', 'ASHPWaterHeater', 'macrs_bonus_fraction'),
            get_value('inputs', 'HotThermalStorage', 'macrs_bonus_fraction'),
            get_value('inputs', 'ColdThermalStorage', 'macrs_bonus_fraction'),
            get_value('inputs', 'SteamTurbine', 'macrs_bonus_fraction'),
            get_value('inputs', 'GHP', 'macrs_bonus_fraction')], d['text_format'])
        inandout_sheet.write_row('N'+str(section_end+1), ['5-Year', 0.2, 0.32, 0.192, 0.1152, 0.1152, 0.0576, None, None], d['text_format'])

        section_end += 1
        inandout_sheet.write_row('N'+str(section_end+1), ['7-Year', 0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446], d['text_format'])
        return section_end, macrs_option_year_row, macrs_bonus_fraction_row

    ## ANNUAL VALUES
    def add_annual_generation_values(annual_value_rows):
        # Raise a value by year
        year_exponent_str = 'B' +str(annual_value_rows)+ ':Z' +str(annual_value_rows)

        inandout_sheet.write_array_formula('C'+str(annual_value_rows+1)+':AA'+str(annual_value_rows+1), '{ = Total_PV_gen_year1_kwh * ( 1 - (PV_degradation_per_year/100) )^'+year_exponent_str+'}', d['proj_fin_format'])
        proforma.define_name('Total_PV_annual_gen_kwh_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+1)+':$AA$'+str(annual_value_rows+1))
        annual_value_rows+=1

        inandout_sheet.write_array_formula('C'+str(annual_value_rows+1)+':AA'+str(annual_value_rows+1), '{ = Existing_PV_gen_year1_kwh * ( 1 - (PV_degradation_per_year/100) )^'+year_exponent_str+'}', d['proj_fin_format'])
        proforma.define_name('Existing_PV_annual_gen_kwh_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+1)+':$AA$'+str(annual_value_rows+1))
        annual_value_rows+=1

        inandout_sheet.write_array_formula('C'+str(annual_value_rows+1)+':AA'+str(annual_value_rows+1), '{ =Wind_annual_electricity_gen_kwh}', d['proj_fin_format'])
        proforma.define_name('Wind_annual_gen_kwh_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+1)+':$AA$'+str(annual_value_rows+1))
        annual_value_rows+=1

        inandout_sheet.write_array_formula('C'+str(annual_value_rows+1)+':AA'+str(annual_value_rows+1), '{ =Generator_annual_electricity_gen_kwh}', d['proj_fin_format'])
        annual_value_rows+=1

        inandout_sheet.write_array_formula('C'+str(annual_value_rows+1)+':AA'+str(annual_value_rows+1), '{ =CHP_annual_electricity_gen_kwh}', d['proj_fin_format'])
        proforma.define_name('CHP_annual_gen_kwh_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+1)+':$AA$'+str(annual_value_rows+1))
        annual_value_rows+=1

        inandout_sheet.write_array_formula('C'+str(annual_value_rows+1)+':AA'+str(annual_value_rows+1), '{ =CHP_annual_thermal_energy_gen_mmbtu}', d['proj_fin_format'])
        annual_value_rows+=1

        inandout_sheet.write_array_formula('C'+str(annual_value_rows+1)+':AA'+str(annual_value_rows+1), '{ =STM_annual_elec_gen_kwh}', d['proj_fin_format'])
        annual_value_rows+=1

        inandout_sheet.write_array_formula('C'+str(annual_value_rows+1)+':AA'+str(annual_value_rows+1), '{ =STM_annual_thermal_energy_gen_mmbtu}', d['proj_fin_format'])
        annual_value_rows+=1

        inandout_sheet.write_array_formula('C'+str(annual_value_rows+1)+':AA'+str(annual_value_rows+1), '{ =ASHP_spaceheater_annual_thermal_energy_gen_mmbtu}', d['proj_fin_format'])
        annual_value_rows+=1

        inandout_sheet.write_array_formula('C'+str(annual_value_rows+1)+':AA'+str(annual_value_rows+1), '{ =ASHP_waterheater_annual_thermal_energy_gen_mmbtu}', d['proj_fin_format'])
        annual_value_rows+=1

        return annual_value_rows

    ## MACRS YEARS ANNUAL FRACTIONS FOR ELIGIBLE TECHS
    def add_macrs_years_for_techs(annual_value_rows, macrs_option_year_row):
        ## MACRS depreciation fraction over the years
        proforma.define_name('PV_MACRS_years', '=\'Inputs and Outputs\'!$B$'+str(macrs_option_year_row))
        proforma.define_name('Wind_MACRS_years', '=\'Inputs and Outputs\'!$C$'+str(macrs_option_year_row))
        proforma.define_name('Battery_MACRS_years', '=\'Inputs and Outputs\'!$D$'+str(macrs_option_year_row))
        proforma.define_name('CHP_MACRS_years', '=\'Inputs and Outputs\'!$E$'+str(macrs_option_year_row))
        proforma.define_name('AbsorptionChiller_MACRS_years', '=\'Inputs and Outputs\'!$F$'+str(macrs_option_year_row))
        proforma.define_name('ASHPSpaceHeater_MACRS_years', '=\'Inputs and Outputs\'!$G$'+str(macrs_option_year_row))
        proforma.define_name('ASHPWaterHeater_MACRS_years', '=\'Inputs and Outputs\'!$H$'+str(macrs_option_year_row))
        proforma.define_name('HotTES_MACRS_years', '=\'Inputs and Outputs\'!$I$'+str(macrs_option_year_row))
        proforma.define_name('ColdTES_MACRS_years', '=\'Inputs and Outputs\'!$J$'+str(macrs_option_year_row))
        proforma.define_name('SteamTurbine_MACRS_years', '=\'Inputs and Outputs\'!$K$'+str(macrs_option_year_row))
        proforma.define_name('GHP_MACRS_years', '=\'Inputs and Outputs\'!$L$'+str(macrs_option_year_row))

        techs_eligible_for_macrs = [
            'PV_MACRS_years','Wind_MACRS_years', 'Battery_MACRS_years', 'CHP_MACRS_years',
            'AbsorptionChiller_MACRS_years','ASHPSpaceHeater_MACRS_years','ASHPWaterHeater_MACRS_years', 
            'HotTES_MACRS_years','ColdTES_MACRS_years','SteamTurbine_MACRS_years','GHP_MACRS_years']

        for col_idx in range(2,27): # C to AA
            for row_idx in range(annual_value_rows+1, annual_value_rows+1+len(techs_eligible_for_macrs)):
                inandout_sheet.write(base_upper_case_letters[col_idx]+str(row_idx), 0.0, d['proj_fin_format_decimal'])

        for macrs_years in techs_eligible_for_macrs:
            inandout_sheet.write_formula('C'+str(annual_value_rows+1), '=IF(OR('+macrs_years+'=5,'+macrs_years+'=7),IF('+macrs_years+'=5,O'+str(macrs_option_year_row+1)+',O'+str(macrs_option_year_row+2)+'),0)', d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('D'+str(annual_value_rows+1), '=IF(OR('+macrs_years+'=5,'+macrs_years+'=7),IF('+macrs_years+'=5,P'+str(macrs_option_year_row+1)+',P'+str(macrs_option_year_row+2)+'),0)', d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('E'+str(annual_value_rows+1), '=IF(OR('+macrs_years+'=5,'+macrs_years+'=7),IF('+macrs_years+'=5,Q'+str(macrs_option_year_row+1)+',Q'+str(macrs_option_year_row+2)+'),0)', d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('F'+str(annual_value_rows+1), '=IF(OR('+macrs_years+'=5,'+macrs_years+'=7),IF('+macrs_years+'=5,R'+str(macrs_option_year_row+1)+',R'+str(macrs_option_year_row+2)+'),0)', d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('G'+str(annual_value_rows+1), '=IF(OR('+macrs_years+'=5,'+macrs_years+'=7),IF('+macrs_years+'=5,S'+str(macrs_option_year_row+1)+',S'+str(macrs_option_year_row+2)+'),0)', d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('H'+str(annual_value_rows+1), '=IF(OR('+macrs_years+'=5,'+macrs_years+'=7),IF('+macrs_years+'=5,T'+str(macrs_option_year_row+1)+',T'+str(macrs_option_year_row+2)+'),0)', d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('I'+str(annual_value_rows+1), '=IF(OR('+macrs_years+'=5,'+macrs_years+'=7),IF('+macrs_years+'=5,0,U'+str(macrs_option_year_row+2)+'),0)', d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('J'+str(annual_value_rows+1), '=IF(OR('+macrs_years+'=5,'+macrs_years+'=7),IF('+macrs_years+'=5,0,V'+str(macrs_option_year_row+2)+'),0)', d['proj_fin_format_decimal'])
            annual_value_rows += 1
        
        return annual_value_rows

    ###### OPT CASHFLOW SHEET FUNCTIONS
    ## OPERATING EXPENSES
    def add_operating_expense_rows(row, sheet, third_party_own):

        if not third_party_own:
            row = add_operating_expenses(row, 'Electricity bill with system before export credits', '=-OPT_annual_electricity_bill * (1 + Elec_cost_escal_pct/100)^')
            row = add_operating_expenses(row, 'Export credits with system', '=OPT_annual_export_to_grid_benefits * (1 + Elec_cost_escal_pct/100)^')
            row = add_operating_expenses(row, 'Boiler fuel bill with system', '=-OPT_boiler_fuel_bill_annual_sum * (1 + Boiler_fuel_cost_escal_pct/100)^')
            row = add_operating_expenses(row, 'CHP fuel bill', '=-CHP_fuels_annual_fuel_bill_sum * (1 + CHP_fuel_cost_escal_rate/100)^')
        optcashf_sheet.write('A'+str(row), 'Operation and Maintenance (O&M)', o['text_format'])
        row += 1
        row = add_operating_expenses(row, 'New PV fixed O&M cost', '=-PV_OM_cost * PV_purchased_kw * (1 + OM_cost_escal_pct/100)^')
        proforma.define_name('Purchased_PV_OM_series_cost', '=\''+sheet+'\'!$C$'+str(row-1)+':\''+sheet+'\'!$AA$'+str(row-1))
        if not third_party_own:
            row = add_operating_expenses(row, 'Existing PV fixed O&M cost', '=-PV_OM_cost * PV_existing_kw * (1 + OM_cost_escal_pct/100)^')
        row = add_operating_expenses(row, 'Wind fixed O&M cost', '=-Wind_OM_cost * Wind_purchased_kw * (1 + OM_cost_escal_pct/100)^')
        proforma.define_name('Wind_OM_series_cost', '=\''+sheet+'\'!$C$'+str(row-1)+':\''+sheet+'\'!$AA$'+str(row-1))
        if not third_party_own:
            row = add_operating_expenses(row, 'Generator fixed O&M cost', '=-Generator_fixed_backup_cost * (Generator_purchased_kw + Generator_existing_kw) * (1 + OM_cost_escal_pct/100)^')
            row = add_operating_expenses(row, 'Generator variable O&M cost', '=-Generator_variable_backup_cost * Generator_annual_electricity_gen_kwh * (1 + OM_cost_escal_pct/100)^')
        else:
            row = add_operating_expenses(row, 'Generator fixed O&M cost', '=-Generator_fixed_backup_cost * Generator_purchased_kw * (1 + OM_cost_escal_pct/100)^')
            row = add_operating_expenses(row, 'Generator variable O&M cost', '=-Generator_variable_backup_cost * Generator_annual_electricity_gen_kwh * (1 + OM_cost_escal_pct/100)^')
        
        if not third_party_own:
            row = add_operating_expenses(row, 'Generator diesel fuel cost ($)', '=-Diesel_fuel_used_cost * (1+Generator_fuel_cost_escal_pct/100)^')
        
        Battery_kw_replacement_row = row
        row += 1
        Battery_kwh_replacement_row = row
        row += 1
        row = add_operating_expenses(row, 'CHP fixed O&M cost', '=-CHP_fixed_OM_cost * CHP_purchased_kw* (1+OM_cost_escal_pct/100)^')
        row = add_operating_expenses(row, 'CHP variable generation O&M cost', '=-CHP_variable_OM_cost * CHP_annual_electricity_gen_kwh * (1+OM_cost_escal_pct/100)^')
        row = add_operating_expenses(row, 'CHP runtime O&M cost', '=-CHP_runtime_OM_cost * CHP_purchased_kw* CHP_annual_runtime_hrs_per_year * (1+OM_cost_escal_pct/100)^')
        row = add_operating_expenses(row, 'Absorption Chiller fixed O&M cost', '=-AbsChl_OM_cost * AbsChl_purhcased_tons * (1+OM_cost_escal_pct/100)^')
        row = add_operating_expenses(row, 'ASHP SpaceHeater fixed O&M cost', '=-AbsChl_OM_cost * AbsChl_purhcased_tons * (1+OM_cost_escal_pct/100)^')
        row = add_operating_expenses(row, 'ASHP WaterHeater fixed O&M cost', '=-AbsChl_OM_cost * AbsChl_purhcased_tons * (1+OM_cost_escal_pct/100)^')
        row = add_operating_expenses(row, 'Chilled water TES fixed O&M cost', '=-ColdTES_OM_cost * ColdTES_size_gal * (1+OM_cost_escal_pct/100)^')
        row = add_operating_expenses(row, 'Hot water TES fixed O&M cost', '=-HotTES_OM_cost * HotTES_size_gal * (1+OM_cost_escal_pct/100)^')
        row = add_operating_expenses(row, 'Steam turbine fixed O&M cost', '=-SteamTurbine_fixed_OM_cost * SteamTurbine_size_kw * (1+OM_cost_escal_pct/100)^')
        row = add_operating_expenses(row, 'Steam turbine variable generation O&M cost', '=-SteamTurbine_variable_OM_cost * STM_annual_elec_gen_kwh * (1+OM_cost_escal_pct/100)^')
        row = add_operating_expenses(row, 'GHP fixed O&M cost', '=-GHP_fixed_OM_cost * (1+OM_cost_escal_pct/100)^')
        return row, Battery_kw_replacement_row, Battery_kwh_replacement_row

    ## COMPLETE OPERATING EXPENSE ROWS
    def complete_operating_expense_rows(
            Battery_kw_replacement_row,
            Battery_kwh_replacement_row,
            row,
            tax_rate_fieldname
            ):
        optcashf_sheet.write('A'+str(Battery_kw_replacement_row), 'Battery kW Replacement Cost', o['text_format'])
        optcashf_sheet.write_array_formula('C'+str(Battery_kw_replacement_row)+':AA'+str(Battery_kw_replacement_row), '{=-IF(C2:AA2 = Battery_kw_replacement_year, Battery_purchased_kw * Battery_kw_replacement_cost, 0)}', o['text_format'])

        optcashf_sheet.write('A'+str(Battery_kwh_replacement_row), 'Battery kWh Replacement Cost', o['text_format'])
        optcashf_sheet.write_array_formula('C'+str(Battery_kwh_replacement_row)+':AA'+str(Battery_kwh_replacement_row), '{=-IF(C2:AA2 = Battery_kwh_replacement_year, Battery_purchased_kwh * Battery_kwh_replacement_cost, 0)}', o['text_format'])

        optcashf_sheet.write('A'+str(row), 'Total operating expenses', o['text_format_2'])
        optcashf_sheet.write('A'+str(row+1), 'Tax deductible operating expenses', o['text_format_2'])

        for idx in range(2, 27):
            col = base_upper_case_letters[idx] # C through AA
            optcashf_sheet.write_formula(col+str(row), '=SUM('+col+'5:'+col+str(row-1)+')', o['text_format_2'])
            optcashf_sheet.write_formula(col+str(row+1), '=IF('+tax_rate_fieldname+' > 0, '+col+str(row)+', 0)', o['text_format_2'])
        
        proforma.define_name('Total_operating_expenses',  '= \'' + sheet + '\'!$C$' + str(row) + ':$AA$' +str(row))
        proforma.define_name('Txded_operating_expenses', '=\'' +sheet+ '\'!$C$' +str(row+1)+ ':$AA$' +str(row+1))

        return row

    ## DIRECT CASH INCENTIVES
    def add_direct_cash_incentives(row, sheet):
        optcashf_sheet.write_row('A'+str(row), ['Direct Cash Incentives']+[None]*26, o['subheader_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), ['PV Investment-based incentives (IBI)', None], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' State IBI', '=MIN((PV_state_ibi_fraction/100)*(PV_purchased_installed_costs-B'+str(row+1)+'-B'+str(row+6)+'), PV_state_ibi_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Utility IBI', '=MIN((PV_utility_ibi_fraction/100) * PV_purchased_installed_costs, PV_utility_ibi_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Total', '=SUM(B'+str(row-2)+', B'+str(row-1)+')'], o['text_format'])

        proforma.define_name('PV_total_IBI', '=\''+sheet+'\'!$B$'+str(row))
        row += 1
        optcashf_sheet.write_row('A'+str(row), ['PV Capacity-based incentives (CBI)', None], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Federal CBI', '=MIN(PV_federal_rebate_per_kw * PV_purchased_kw * 1000, PV_federal_rebate_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' State CBI', '=MIN(PV_state_rebate_per_kw * PV_purchased_kw * 1000, PV_state_rebate_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Utility CBI', '=MIN(PV_utility_rebate_per_kw * PV_purchased_kw * 1000, PV_utility_rebate_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Total', '=SUM(B'+str(row-3)+':B'+str(row-1)+')'], o['text_format'])

        proforma.define_name('PV_total_CBI', '=\''+sheet+'\'!$B$'+str(row))

        # WIND
        row += 1
        optcashf_sheet.write_row('A'+str(row), ['Wind Investment-based incentives (IBI)', None], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' State IBI', '=MIN((PV_state_ibi_fraction/100)*(PV_purchased_installed_costs-B'+str(row+1)+'-B'+str(row+6)+'), PV_state_ibi_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Utility IBI', '=MIN((PV_utility_ibi_fraction/100) * PV_purchased_installed_costs, PV_utility_ibi_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Total', '=SUM(B'+str(row-2)+', B'+str(row-1)+')'], o['text_format'])
        proforma.define_name('Wind_total_IBI', '=\''+sheet+'\'!$B$'+str(row))
        row += 1
        optcashf_sheet.write_row('A'+str(row), ['Wind Capacity-based incentives (CBI)', None], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Federal CBI', '=MIN(PV_federal_rebate_per_kw * PV_purchased_kw * 1000, PV_federal_rebate_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' State CBI', '=MIN(PV_state_rebate_per_kw * PV_purchased_kw * 1000, PV_state_rebate_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Utility CBI', '=MIN(PV_utility_rebate_per_kw * PV_purchased_kw * 1000, PV_utility_rebate_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Total', '=SUM(B'+str(row-3)+':B'+str(row-1)+')'], o['text_format'])
        proforma.define_name('Wind_total_CBI', '=\''+sheet+'\'!$B$'+str(row))

        # BATTERY
        row += 1
        optcashf_sheet.write_row('A'+str(row), ['Battery Investment-based incentives (IBI)', None], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' State IBI', '=MIN((PV_state_ibi_fraction/100)*(PV_purchased_installed_costs-B'+str(row+1)+'-B'+str(row+6)+'), PV_state_ibi_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Utility IBI', '=MIN((PV_utility_ibi_fraction/100) * PV_purchased_installed_costs, PV_utility_ibi_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Total', '=SUM(B'+str(row-2)+', B'+str(row-1)+')'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), ['Battery Capacity-based incentives (CBI)', None], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Total Power (per kW) CBI', '=MIN(Battery_total_kw_cbi_fraction * Battery_purchased_kw, Battery_total_kw_cbi_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Total Storage Capacity (per kWh) CBI', '=MIN(Battery_total_kwh_cbi_fraction * Battery_purchased_kwh, Battery_total_kwh_cbi_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Total', '=SUM(B'+str(row-2)+':B'+str(row-1)+')'], o['text_format'])

        # CHP
        row += 1
        optcashf_sheet.write_row('A'+str(row), ['CHP Investment-based incentives (IBI)', None], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' State IBI', '=MIN((PV_state_ibi_fraction/100)*(PV_purchased_installed_costs-B'+str(row+1)+'-B'+str(row+6)+'), PV_state_ibi_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Utility IBI', '=MIN((PV_utility_ibi_fraction/100) * PV_purchased_installed_costs, PV_utility_ibi_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Total', '=SUM(B'+str(row-2)+', B'+str(row-1)+')'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), ['CHP Capacity-based incentives (CBI)', None], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Federal CBI', '=MIN(PV_federal_rebate_per_kw * PV_purchased_kw * 1000, PV_federal_rebate_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' State CBI', '=MIN(PV_state_rebate_per_kw * PV_purchased_kw * 1000, PV_state_rebate_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Utility CBI', '=MIN(PV_utility_rebate_per_kw * PV_purchased_kw * 1000, PV_utility_rebate_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Total', '=SUM(B'+str(row-3)+':B'+str(row-1)+')'], o['text_format'])

        row += 2
        optcashf_sheet.write_row('A'+str(row), ['Total CBI and IBI', '=SUM(B'+str(row-33)+',B'+str(row-28)+',B'+str(row-24)+',B'+str(row-19)+',B'+str(row-15)+',B'+str(row-11)+',B'+str(row-7)+',B'+str(row-2)+')'], o['text_format'])

        # GHP
        row += 2
        optcashf_sheet.write_row('A'+str(row), ['GHP Investment-based incentives (IBI)', None], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' State IBI', '=MIN((PV_state_ibi_fraction/100)*(PV_purchased_installed_costs-B'+str(row+1)+'-B'+str(row+6)+'), PV_state_ibi_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Utility IBI', '=MIN((PV_utility_ibi_fraction/100) * PV_purchased_installed_costs, PV_utility_ibi_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Total', '=SUM(B'+str(row-2)+', B'+str(row-1)+')'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), ['GHP Capacity-based incentives (CBI)', None], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Federal CBI', '=MIN(PV_federal_rebate_per_kw * PV_purchased_kw * 1000, PV_federal_rebate_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' State CBI', '=MIN(PV_state_rebate_per_kw * PV_purchased_kw * 1000, PV_state_rebate_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Utility CBI', '=MIN(PV_utility_rebate_per_kw * PV_purchased_kw * 1000, PV_utility_rebate_max)'], o['text_format'])
        row += 1
        optcashf_sheet.write_row('A'+str(row), [' Total', '=SUM(B'+str(row-3)+':B'+str(row-1)+')'], o['text_format'])

        row += 2
        optcashf_sheet.write_row('A'+str(row), ['Total CBI and IBI', '=SUM(B'+str(row-12)+',B'+str(row-7)+',B'+str(row-2)+')'], o['text_format'])

        row += 2
        optcashf_sheet.write('A'+str(row), 'Production-based incentives (PBI)', o['text_format'])
        optcashf_sheet.write('A'+str(row), ' New PV Combined PBI', o['text_format_indent'])
        optcashf_sheet.write_dynamic_array_formula(
            'C'+str(row)+':AA'+str(row),
            '=IF(B2:Z2 < PV_PBI_years, MIN(PV_PBI_per_kwh * (Total_PV_annual_gen_kwh_range - Existing_PV_annual_gen_kwh_range), PV_PBI_max_benefit * (1 - PV_degradation_per_year/100)^B2:Z2), 0)',
            o['text_format']
        )
        proforma.define_name('Purchased_PV_PBI_combined', '=\'' +sheet+ '\'!$C$' +str(row)+ ':\'' +sheet+ '\'!$AA$'+str(row))
        row += 1

        optcashf_sheet.write('A'+str(row), ' Existing PV Combined PBI', o['text_format_indent'])
        optcashf_sheet.write_dynamic_array_formula(
            'C'+str(row)+':AA'+str(row),
            '=IF(B2:Z2 < PV_PBI_years, MIN(PV_PBI_per_kwh * Existing_PV_annual_gen_kwh_range, PV_PBI_max_benefit * (1 - PV_degradation_per_year/100)^B2:Z2), 0)',
            o['text_format']
        )
        row += 1

        optcashf_sheet.write('A'+str(row), ' Wind Combined PBI', o['text_format_indent'])
        optcashf_sheet.write_dynamic_array_formula(
            'C'+str(row)+':AA'+str(row),
            '=IF(B2:Z2 < Wind_PBI_years, MIN(Wind_PBI_per_kwh * Wind_annual_gen_kwh_range, Wind_PBI_max_benefit), 0)',
            o['text_format']
        )

        proforma.define_name('Wind_PBI_combined', '=\''+sheet+'\'!$C$'+str(row)+':\''+sheet+'\'!$AA$'+str(row))
        row += 1

        optcashf_sheet.write('A'+str(row), ' CHP Combined PBI', o['text_format_indent'])
        optcashf_sheet.write_dynamic_array_formula(
            'C'+str(row)+':AA'+str(row),
            '=IF(B2:Z2 < CHP_PBI_years, MIN(CHP_PBI_per_kwh * CHP_annual_gen_kwh_range, CHP_PBI_max_benefit), 0)',
            o['text_format']
        )
        row += 1

        optcashf_sheet.write('A'+str(row), 'Total taxable cash incentives', o['text_format_2'])
        optcashf_sheet.write_dynamic_array_formula(
            'C'+str(row)+':AA'+str(row),
            '=IF(PV_PBI_federally_taxable="Yes", C'+str(row-4)+':AA'+str(row-4)+', 0) + IF(PV_PBI_federally_taxable="Yes", C'+str(row-3)+':AA'+str(row-3)+', 0) + IF(Wind_PBI_federally_taxable="Yes", C'+str(row-2)+':AA'+str(row-2)+', 0)+IF(CHP_PBI_federally_taxable="Yes", C'+str(row-1)+':AA'+str(row-1)+', 0)',
            o['text_format_2']
        )
        optcashf_sheet.write_formula(
            'B'+str(row),
            '=IF(PV_state_ibi_is_taxable="Yes", B34, 0) + IF(PV_utility_ibi_is_taxable="Yes", B35, 0) + IF(PV_federal_rabete_is_taxable="Yes", B38,0) + IF(PV_state_rebate_is_taxable="Yes", B39, 0) + IF(PV_utility_rebate_is_taxable="Yes", B40, 0)+IF(Battery_state_ibi_is_taxable="Yes", B52, 0)+IF(Battery_utility_ibi_is_taxable="Yes", B53, 0)+IF(Battery_kw_cbi_is_taxable="Yes", B56, 0)+IF(Battery_kwh_cbi_is_taxable="Yes", B75, 0)+IF(Wind_state_ibi_is_taxable="Yes", B43, 0)+IF(Wind_utility_ibi_is_taxable="Yes", B44, 0)+IF(Wind_federal_rebate_is_taxable="Yes", B47, 0)+IF(Wind_state_rebate_is_taxable="Yes", B48, 0)+IF(Wind_utility_rebate_is_taxable="Yes", B49, 0)+'+
            'IF(CHP_state_ibi_is_taxable="Yes", B60, 0)+IF(CHP_utility_ibi_is_taxable="Yes", B61, 0)+IF(CHP_federal_rebate_is_taxable="Yes", B64, 0)+IF(CHP_state_rebate_is_taxable="Yes", B65, 0)+IF(CHP_utility_rebate_is_taxable="Yes", B66, 0)+IF(GHP_state_ibi_is_taxable="Yes", B72, 0)+IF(GHP_utility_ibi_is_taxable="Yes", B73, 0)+IF(GHP_federal_rebate_is_taxable="Yes", B76, 0)+IF(GHP_state_rebate_is_taxable="Yes", B77, 0)+IF(GHP_utility_rebate_is_taxable="Yes", B78, 0)',
            o['text_format_2']
        )
        row += 1

        optcashf_sheet.write('A'+str(row), 'Total non-taxable cash incentives', o['text_format_2'])
        optcashf_sheet.write_array_formula(
            'C'+str(row)+':AA'+str(row),
            '{=IF(PV_PBI_federally_taxable="No", C'+str(row-5)+':AA'+str(row-5)+', 0) + IF(PV_PBI_federally_taxable="No", C'+str(row-4)+':AA'+str(row-4)+', 0) + IF(Wind_PBI_federally_taxable="No", C'+str(row-3)+':AA'+str(row-3)+', 0)+IF(CHP_PBI_federally_taxable="No", C'+str(row-2)+':AA'+str(row-2)+', 0)}',
            o['text_format_2']
        )
        optcashf_sheet.write_formula(
            'B'+str(row),
            '=IF(PV_state_ibi_is_taxable="No", B34, 0) + IF(PV_utility_ibi_is_taxable="No", B35, 0) + IF(PV_federal_rabete_is_taxable="No", B38,0) + IF(PV_state_rebate_is_taxable="No", B39, 0) + IF(PV_utility_rebate_is_taxable="No", B40, 0)+IF(Battery_state_ibi_is_taxable="No", B52, 0)+IF(Battery_utility_ibi_is_taxable="No", B53, 0)+IF(Battery_kw_cbi_is_taxable="No", B56, 0)+IF(Battery_kwh_cbi_is_taxable="No", B75, 0)+IF(Wind_state_ibi_is_taxable="No", B43, 0)+IF(Wind_utility_ibi_is_taxable="No", B44, 0)+IF(Wind_federal_rebate_is_taxable="No", B47, 0)+IF(Wind_state_rebate_is_taxable="No", B48, 0)+IF(Wind_utility_rebate_is_taxable="No", B49, 0)+'+
            'IF(CHP_state_ibi_is_taxable="No", B60, 0)+IF(CHP_utility_ibi_is_taxable="No", B61, 0)+IF(CHP_federal_rebate_is_taxable="No", B64, 0)+IF(CHP_state_rebate_is_taxable="No", B65, 0)+IF(CHP_utility_rebate_is_taxable="No", B66, 0)+IF(GHP_state_ibi_is_taxable="No", B72, 0)+IF(GHP_utility_ibi_is_taxable="No", B73, 0)+IF(GHP_federal_rebate_is_taxable="No", B76, 0)+IF(GHP_state_rebate_is_taxable="No", B77, 0)+IF(GHP_utility_rebate_is_taxable="No", B78, 0)',
            o['text_format_2']
        )
        proforma.define_name('Sum_taxable_cash_incentives', '=\''+sheet+'\'!$B$'+str(row-1)+':$AA$'+str(row-1))
        proforma.define_name('Sum_nontaxable_cash_incentives', '=\''+sheet+'\'!$B$'+str(row)+':$AA$'+str(row))

        return row

    ## CAPITAL DEPRECIATION
    def add_capital_depreciation_LCOE_calculations(row, sheet, tax_rate_fieldname):
        row += 2
        optcashf_sheet.write_row('A'+str(row), ['Capital Depreciation']+[None]*26, o['subheader_format'])
        row += 1

        techs = ['PV', 'Wind', 'Battery', 'CHP', 'AbsorptionChiller', 'ASHPSpaceHeater', 'ASHPWaterHeater', 'HotTES', 'ColdTES', 'SteamTurbine', 'GHP']
        itc_basis_array = ['PV_itc_basis','Wind_itc_basis','Battery_itc_basis','CHP_itc_basis',None, None, None, None, None, None, 'GHP_itc_basis']
        cols = ['B','C','D','E','F','G','H','I','J','K','L']
        for (t,c,itc_basis) in zip(techs,cols,itc_basis_array):
            optcashf_sheet.write('A'+str(row), t+' Depreciation, Commercial only', o['text_format'])
            row += 1
            optcashf_sheet.write('A'+str(row), '  Percentage', o['text_format_indent'])
            optcashf_sheet.write_dynamic_array_formula('C'+str(row)+':AA'+str(row), '='+t+'_depreciation_range', o['text_format_decimal'])
            row += 1
            optcashf_sheet.write('A'+str(row), '    Bonus Basis', o['text_format_indent'])

            # these techs do not have ITC.
            if t in ['AbsorptionChiller', 'ASHPSpaceHeater', 'ASHPWaterHeater', 'HotTES', 'ColdTES', 'SteamTurbine']:
                optcashf_sheet.write_formula(
                    'B'+str(row),
                    '=IF(OR('+t+'_MACRS_years=5,'+t+'_MACRS_years=7), '+t+'_installed_costs, 0)',
                    o['text_format']
                )
            else:
                optcashf_sheet.write_formula(
                    'B'+str(row),
                    '=IF(OR('+t+'_MACRS_years=5,'+t+'_MACRS_years=7),('+itc_basis+'-IF('+t+'_reduces_depreciation="Yes",0.5*MIN('+t+'_federal_itc_fraction/100*'+itc_basis+','+t+'_max_itc_benefit),0)),0)',
                    o['text_format']
                )
            row += 1
            optcashf_sheet.write('A'+str(row), '    Basis', o['text_format_indent'])
            optcashf_sheet.write_formula(
                'B'+str(row),
                '=B'+str(row-1)+'*(1-\'Inputs and Outputs\'!'+c+''+str(macrs_bonus_fraction_row+1)+')',
                o['text_format']
            )
            row += 1
            optcashf_sheet.write('A'+str(row), '    Amount', o['text_format_indent'])
            optcashf_sheet.write_dynamic_array_formula('D'+str(row)+':AA'+str(row), '=B'+str(row-1)+'*D'+str(row-3)+':AA'+str(row-3), o['text_format'])
            optcashf_sheet.write_formula(
                'C'+str(row),
                '=B'+str(row-1)+'*C'+str(row-3) + ' + (B'+str(row-2)+'*\'Inputs and Outputs\'!'+c+''+str(macrs_bonus_fraction_row+1)+')',
                o['text_format']
            )
            if t == 'PV':
                first_amount_row = row
            proforma.define_name(t+'_capital_depreciation_series', '=\'' +sheet+ '\'!$C$' +str(row)+ ':\''+sheet+'\'!$AA$'+str(row))
            row += 1

        optcashf_sheet.write('A'+str(row), 'Total depreciation', o['text_format_2'])
        for idx in range(2, 27):
            col = base_upper_case_letters[idx] # C through AA
            optcashf_sheet.write_formula(
                col+str(row),
                '=SUM('+col+str(first_amount_row+5*0)+', '+col+str(first_amount_row+5*1)+', '+col+str(first_amount_row+5*2)+', '+col+str(first_amount_row+5*3)+', '+col+str(first_amount_row+5*4)+', '+col+str(first_amount_row+5*5)+', '+col+str(first_amount_row+5*6)+', '+col+str(first_amount_row+5*7)+', '+col+str(first_amount_row+5*8)+', '+col+str(first_amount_row+5*9)+', '+col+str(first_amount_row+5*10)+')',
                o['text_format_2']
            )
        proforma.define_name('Total_depreciation_shield', '=\''+sheet+'\'!$C$'+str(row)+':$AA$'+str(row))
        row += 2

        # Tax benefits for LCOE calculations
        optcashf_sheet.write_row('A'+str(row), ['Tax benefits for LCOE Calculations']+[None]*26, o['subheader_format'])
        row += 1
        optcashf_sheet.write('A'+str(row), 'PV income tax savings, $', o['text_format_2'])
        optcashf_sheet.write_array_formula('C'+str(row)+':AA'+str(row)+'', '{=(-Purchased_PV_OM_series_cost + PV_capital_depreciation_series) * '+tax_rate_fieldname+'/100}', o['text_format_2'])
        proforma.define_name('Purchased_PV_income_tax_savings', '=\''+sheet+'\'!$C$'+str(row)+':\''+sheet+'\'!$AA$'+str(row))
        
        row += 1
        optcashf_sheet.write('A'+str(row), 'Wind income tax savings, $', o['text_format_2'])
        optcashf_sheet.write_array_formula('C'+str(row)+':AA'+str(row)+'', '{=(-Wind_OM_series_cost + Wind_capital_depreciation_series) * '+tax_rate_fieldname+'/100}', o['text_format_2'])
        proforma.define_name('Wind_income_tax_savings', '=\''+sheet+'\'!$C$'+str(row)+':\''+sheet+'\'!$AA$'+str(row))
        return row + 2

    ## FEDERAL ITC CALCULATIONS
    def add_federal_itc_calculations(row, sheet):
        optcashf_sheet.write_row('A'+str(row), ['Federal Investment Tax Credit']+[None]*26, o['subheader_format'])
        row += 1
        # PV
        optcashf_sheet.write('A'+str(row), 'Federal ITC basis: PV', o['text_format'])
        optcashf_sheet.write_formula('B'+str(row), '=PV_purchased_installed_costs -IF(PV_state_ibi_reduces_basis="Yes",B34,0)-IF(PV_utility_ibi_reduces_basis="Yes",B35,0)-IF(PV_federal_rebate_reduces_basis="Yes",B38,0)-IF(PV_state_rebate_reduces_basis="Yes",B39,0)-IF(PV_utility_rebate_reduces_basis="Yes",B40,0)', o['text_format'])
        proforma.define_name('PV_itc_basis', '=\''+sheet+'\'!$B$'+str(row))
        row += 1
        optcashf_sheet.write('A'+str(row), 'Federal ITC amount: PV', o['text_format'])
        optcashf_sheet.write_formula('C'+str(row), '=MIN(PV_federal_itc_fraction/100*B'+str(row-1)+', PV_max_itc_benefit)')
        
        proforma.define_name('PV_itc_amount', '=\''+sheet+'\'!$C$'+str(row))
        row += 1

        # Wind
        optcashf_sheet.write('A'+str(row), 'Federal ITC basis: Wind', o['text_format'])
        optcashf_sheet.write_formula('B'+str(row), '=Wind_installed_costs -IF(Wind_state_ibi_reduces_basis="Yes",B43,0)-IF(Wind_utility_ibi_reduces_basis="Yes",B44,0)-IF(Wind_federal_rebate_reduces_basis="Yes",B47,0)-IF(Wind_state_rebate_reduces_basis="Yes",B48,0)-IF(Wind_utility_rebate_reduces_basis="Yes",B49,0)', o['text_format'])
        proforma.define_name('Wind_itc_basis', '=\''+sheet+'\'!$B$'+str(row))
        row += 1
        optcashf_sheet.write('A'+str(row), 'Federal ITC amount: Wind', o['text_format'])
        optcashf_sheet.write_formula('C'+str(row), '=MIN(Wind_federal_itc_fraction/100*B'+str(row-1)+', Wind_max_itc_benefit)')
        
        proforma.define_name('Wind_itc_amount', '=\''+sheet+'\'!$C$'+str(row))
        row += 1

        # Battery
        optcashf_sheet.write('A'+str(row), 'Federal ITC basis: Battery', o['text_format'])
        optcashf_sheet.write_formula('B'+str(row), '=Battery_installed_costs -IF(Battery_state_ibi_reduces_basis="Yes",B52,0)-IF(Battery_utility_ibi_reduces_basis="Yes",B53,0)-IF(Battery_kw_cbi_reduces_basis="Yes",B56,0)-IF(Battery_kwh_cbi_reduces_basis="Yes",B57,0)', o['text_format'])
        proforma.define_name('Battery_itc_basis', '=\''+sheet+'\'!$B$'+str(row))
        row += 1
        optcashf_sheet.write('A'+str(row), 'Federal ITC amount: Battery', o['text_format'])
        optcashf_sheet.write_formula('C'+str(row), '=MIN(Battery_federal_itc_fraction/100*B'+str(row-1)+', Battery_max_itc_benefit)')
        row += 1

        # CHP
        optcashf_sheet.write('A'+str(row), 'Federal ITC basis: CHP', o['text_format'])
        optcashf_sheet.write_formula('B'+str(row), '=CHP_installed_costs -IF(CHP_state_ibi_reduces_basis="Yes",B60,0)-IF(CHP_utility_ibi_reduces_basis="Yes",B61,0)-IF(CHP_federal_rebate_reduces_basis="Yes",B64,0)-IF(CHP_state_rebate_reduces_basis="Yes",B65,0)-IF(CHP_utility_rebate_reduces_basis="Yes",B66,0)', o['text_format'])
        proforma.define_name('CHP_itc_basis', '=\''+sheet+'\'!$B$'+str(row))
        row += 1
        optcashf_sheet.write('A'+str(row), 'Federal ITC amount: CHP', o['text_format'])
        optcashf_sheet.write_formula('C'+str(row), '=MIN(CHP_federal_itc_fraction/100*B'+str(row-1)+', CHP_max_itc_benefit)')
        row += 1

        # GHP
        optcashf_sheet.write('A'+str(row), 'Federal ITC basis: GHP', o['text_format'])
        optcashf_sheet.write_formula('B'+str(row), '=GHP_installed_costs -IF(GHP_state_ibi_reduces_basis="Yes",B72,0)-IF(GHP_utility_ibi_reduces_basis="Yes",B73,0)-IF(GHP_federal_rebate_reduces_basis="Yes",B76,0)-IF(GHP_state_rebate_reduces_basis="Yes",B77,0)-IF(GHP_utility_rebate_reduces_basis="Yes",B78,0)', o['text_format'])
        proforma.define_name('GHP_itc_basis', '=\''+sheet+'\'!$B$'+str(row))
        row += 1
        optcashf_sheet.write('A'+str(row), 'Federal ITC amount: GHP', o['text_format'])
        optcashf_sheet.write_formula('C'+str(row), '=MIN(GHP_federal_itc_fraction/100*B'+str(row-1)+', GHP_max_itc_benefit)')
        row += 1
        optcashf_sheet.write_row('A'+str(row), ['Total Federal ITC']+[None]+['=SUM(C'+str(row-9)+', C'+str(row-7)+', C'+str(row-5)+', C'+str(row-3)+', C'+str(row-1)+')']+[None]*24, o['text_format_2'])

        proforma.define_name('Total_federal_itc', '=\''+sheet+'\'!$C$'+str(row)+':$AA$'+str(row))

        return row + 2

    ## TOTAL CASH FLOW CALCULATIONS
    def add_total_cash_flow_calculations(row, sheet, discount_rate_fieldname, tax_rate_fieldname):
        optcashf_sheet.write_row('A'+str(row), ['Total Cash Flows']+[None]*26, o['subheader_format'])
        row+=1
        optcashf_sheet.write('A'+str(row), 'Upfront Capital Cost', o['text_format'])
        optcashf_sheet.write_formula('B'+str(row), '=-Total_installed_costs_no_incentives', o['text_format'])
        row+=1
        optcashf_sheet.write('A'+str(row), 'Upfront Asset Residual Value', o['text_format'])
        optcashf_sheet.write_formula('B'+str(row), '=GHX_residual_value', o['text_format']) # present value of GHX residual value in year 25.
        row+=1
        optcashf_sheet.write('A'+str(row), 'Operating expenses, after-tax', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C'+str(row)+':AA'+str(row), '=(Total_operating_expenses - Txded_operating_expenses) + Txded_operating_expenses * (1 - '+tax_rate_fieldname+'/100)', o['text_format'])
        row+=1
        optcashf_sheet.write('A'+str(row), 'Total Cash incentives, after-tax', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('B'+str(row)+':AA'+str(row), '=(Sum_taxable_cash_incentives * (1 - '+tax_rate_fieldname+'/100)) + Sum_nontaxable_cash_incentives', o['text_format'])
        row+=1
        optcashf_sheet.write('A'+str(row), 'Depreciation Tax Shield', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C'+str(row)+':AA'+str(row), '=Total_depreciation_shield * '+tax_rate_fieldname+'/100', o['text_format'])
        row+=1
        optcashf_sheet.write('A'+str(row), 'Investment Tax Credit', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C'+str(row)+':AA'+str(row), '=Total_federal_itc', o['text_format'])
        row+=1
        optcashf_sheet.write('A'+str(row), 'Free Cash Flow before income', o['text_format_2'])
        optcashf_sheet.write_formula('B'+str(row), '=B'+str(row-6)+'+B'+str(row-5)+'+B'+str(row-3), o['text_format_2'])
        optcashf_sheet.write_dynamic_array_formula('C'+str(row)+':AA'+str(row), '=C'+str(row-4)+':AA'+str(row-4)+' + C'+str(row-3)+':AA'+str(row-3)+' + C'+str(row-2)+':AA'+str(row-2)+' + C'+str(row-1)+':AA'+str(row-1), o['text_format_2'])
        proforma.define_name('OPT_free_cash_flow_range', '=\''+sheet+'\'!$B$'+str(row)+':$AA$'+str(row))
        row+=1
        optcashf_sheet.write('A'+str(row), 'Discounted Cash Flow', o['text_format_2'])
        optcashf_sheet.write_formula('B'+str(row), '=B'+str(row-7)+'+B'+str(row-6)+'+B'+str(row-4), o['text_format_2'])
        optcashf_sheet.write_dynamic_array_formula('C'+str(row)+':AA'+str(row), '=C'+str(row-1)+':AA'+str(row-1) +' / (1 + '+discount_rate_fieldname+'/100)^C2:AA2', o['text_format_2'])
        row+=1
        optcashf_sheet.write('A'+str(row), 'Optimal Life Cycle Cost', o['standalone_bold_text_format'])
        optcashf_sheet.write_formula('B'+str(row), '=SUM(B'+str(row-1)+':AA'+str(row-1)+')', o['standalone_bold_text_format'])
        return row

    ## PROJECT ECONOMICS
    def add_direct_own_project_economics_summary():
        inandout_sheet.write('D5', 'RESULTS', d['subheader_format'])
        inandout_sheet.write_blank('E5', None, d['subheader_format_right'])
        inandout_sheet.write('D6', 'Business as usual LCC, $', d['text_format'])
        inandout_sheet.write('D7', 'Optimal LCC, $', d['text_format'])
        inandout_sheet.write('D8', 'NPV, $', d['text_format'])
        inandout_sheet.write('D9', 'IRR, %', d['text_format'])
        inandout_sheet.write('D10', 'Simple Payback Period, years', d['text_format'])
        inandout_sheet.write('F7', 'NOTE: A negative LCC indicates a profit (for example when production based incentives are greater than costs.', d['text_format'])
        inandout_sheet.write('F8', 'NOTE: This NPV can differ slightly (<1%) from the Webtool/API results due to rounding and the tolerance in the optimizer.', d['text_format'])

        inandout_sheet.write_formula('E6', '=-\'BAU Cash Flow\'!B24', d['proj_fin_format'])
        inandout_sheet.write_formula('E7', '=-\'Optimal Cash Flow\'!B174', d['proj_fin_format'])
        inandout_sheet.write_formula('E8', '=E6 - E7', d['proj_fin_format'])
        # If NPV is 0 or less, then sets IRR to 0%.
        inandout_sheet.write_formula('E9', '=IF(E8<=0,"",IRR(Net_free_cash_flow_range, Offtaker_discount_rate/100))', d['proj_fin_format_decimal'])

        spp_formula_string = '=IF(\'Inputs and Outputs\'!B'+str(ccf_row)+'=0,"", IF(\'Inputs and Outputs\'!AA'+str(ccf_row)+' < 0, "Over 25", SUM(IF(\'Inputs and Outputs\'!C'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!B'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!B'+str(ccf_row)+'/\'Inputs and Outputs\'!C'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!D'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!C'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!C'+str(ccf_row)+'/\'Inputs and Outputs\'!D'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!E'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!D'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!D'+str(ccf_row)+'/\'Inputs and Outputs\'!E'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!F'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!E'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!E'+str(ccf_row)+'/\'Inputs and Outputs\'!F'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!G'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!F'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!F'+str(ccf_row)+'/\'Inputs and Outputs\'!G'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!H'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!G'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!G'+str(ccf_row)+'/\'Inputs and Outputs\'!H'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!I'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!H'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!H'+str(ccf_row)+'/\'Inputs and Outputs\'!I'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!J'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!I'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!I'+str(ccf_row)+'/\'Inputs and Outputs\'!J'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!K'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!J'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!J'+str(ccf_row)+'/\'Inputs and Outputs\'!K'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!L'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!K'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!K'+str(ccf_row)+'/\'Inputs and Outputs\'!L'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!M'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!L'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!L'+str(ccf_row)+'/\'Inputs and Outputs\'!M'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!N'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!M'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!M'+str(ccf_row)+'/\'Inputs and Outputs\'!N'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!O'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!N'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!N'+str(ccf_row)+'/\'Inputs and Outputs\'!O'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!P'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!O'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!O'+str(ccf_row)+'/\'Inputs and Outputs\'!P'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!Q'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!P'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!P'+str(ccf_row)+'/\'Inputs and Outputs\'!Q'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!R'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!Q'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!Q'+str(ccf_row)+'/\'Inputs and Outputs\'!R'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!S'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!R'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!R'+str(ccf_row)+'/\'Inputs and Outputs\'!S'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!T'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!S'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!S'+str(ccf_row)+'/\'Inputs and Outputs\'!T'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!U'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!T'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!T'+str(ccf_row)+'/\'Inputs and Outputs\'!U'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!V'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!U'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!U'+str(ccf_row)+'/\'Inputs and Outputs\'!V'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!W'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!V'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!V'+str(ccf_row)+'/\'Inputs and Outputs\'!W'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!X'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!W'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!W'+str(ccf_row)+'/\'Inputs and Outputs\'!X'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!Y'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!X'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!X'+str(ccf_row)+'/\'Inputs and Outputs\'!Y'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!Z'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!Y'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!Y'+str(ccf_row)+'/\'Inputs and Outputs\'!Z'+str(fcf_row)+')), IF(\'Inputs and Outputs\'!AA'+str(ccf_row)+'<0,1,IF(\'Inputs and Outputs\'!Z'+str(ccf_row)+'>0,0,-\'Inputs and Outputs\'!Z'+str(ccf_row)+'/\'Inputs and Outputs\'!AA'+str(fcf_row)+')))))'
        inandout_sheet.write_formula('E10', spp_formula_string, d['proj_fin_format_spp'])

    def add_third_party_own_project_economics_summary(fcf, ccf):

        inandout_sheet.write('D5', 'RESULTS', d['subheader_format'])
        inandout_sheet.write_blank('E5', None, d['subheader_format_right'])
        inandout_sheet.write('D6', 'Annual payment to third-party, $', d['text_format'])
        inandout_sheet.write('D7', 'Third-party Owner NPC, $', d['text_format'])
        inandout_sheet.write('D8', 'Host\'s NPV, $', d['text_format'])
        inandout_sheet.write('D9', 'Third-party Owner IRR, %', d['text_format'])
        inandout_sheet.write('D10', 'Third-party Owner Simple Payback Period, years', d['text_format'])
        inandout_sheet.write('F7', 'NOTE: A negative Net Present Cost can occur if incentives are greater than costs.', d['text_format'])
        inandout_sheet.write('F8', 'NOTE: This NPV can differ slightly (<1%) from the Webtool/API results due to rounding and the tolerance in the optimizer.', d['text_format'])

        inandout_sheet.write_formula('E6', '=Annual_payment_to_developer', d['proj_fin_format'])
        inandout_sheet.write_formula('E7', '=Net_present_cost_to_thirdparty', d['proj_fin_format'])
        inandout_sheet.write_formula('E8', '=Host_Net_Present_Value', d['proj_fin_format'])
        inandout_sheet.write_formula('E9', '=IF(E8=0,,IRR(Thirdparty_freecashflow_range, Developer_discount_rate/100))', d['proj_fin_format_decimal'])

        spp_formula_string = '=IF(\'Third-party Owner Cash Flow\'!AA'+ccf+' < 0, "Over 25", SUM(IF(\'Third-party Owner Cash Flow\'!C'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!B'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!B'+ccf+'/\'Third-party Owner Cash Flow\'!C'+fcf+')), IF(\'Third-party Owner Cash Flow\'!D'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!C'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!C'+ccf+'/\'Third-party Owner Cash Flow\'!D'+fcf+')), IF(\'Third-party Owner Cash Flow\'!E'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!D'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!D'+ccf+'/\'Third-party Owner Cash Flow\'!E'+fcf+')), IF(\'Third-party Owner Cash Flow\'!F'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!E'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!E'+ccf+'/\'Third-party Owner Cash Flow\'!F'+fcf+')), IF(\'Third-party Owner Cash Flow\'!G'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!F'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!F'+ccf+'/\'Third-party Owner Cash Flow\'!G'+fcf+')), IF(\'Third-party Owner Cash Flow\'!H'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!G'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!G'+ccf+'/\'Third-party Owner Cash Flow\'!H'+fcf+')), IF(\'Third-party Owner Cash Flow\'!I'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!H'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!H'+ccf+'/\'Third-party Owner Cash Flow\'!I'+fcf+')), IF(\'Third-party Owner Cash Flow\'!J'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!I'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!I'+ccf+'/\'Third-party Owner Cash Flow\'!J'+fcf+')), IF(\'Third-party Owner Cash Flow\'!K'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!J'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!J'+ccf+'/\'Third-party Owner Cash Flow\'!K'+fcf+')), IF(\'Third-party Owner Cash Flow\'!L'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!K'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!K'+ccf+'/\'Third-party Owner Cash Flow\'!L'+fcf+')), IF(\'Third-party Owner Cash Flow\'!M'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!L'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!L'+ccf+'/\'Third-party Owner Cash Flow\'!M'+fcf+')), IF(\'Third-party Owner Cash Flow\'!N'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!M'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!M'+ccf+'/\'Third-party Owner Cash Flow\'!N'+fcf+')), IF(\'Third-party Owner Cash Flow\'!O'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!N'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!N'+ccf+'/\'Third-party Owner Cash Flow\'!O'+fcf+')), IF(\'Third-party Owner Cash Flow\'!P'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!O'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!O'+ccf+'/\'Third-party Owner Cash Flow\'!P'+fcf+')), IF(\'Third-party Owner Cash Flow\'!Q'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!P'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!P'+ccf+'/\'Third-party Owner Cash Flow\'!Q'+fcf+')), IF(\'Third-party Owner Cash Flow\'!R'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!Q'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!Q'+ccf+'/\'Third-party Owner Cash Flow\'!R'+fcf+')), IF(\'Third-party Owner Cash Flow\'!S'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!R'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!R'+ccf+'/\'Third-party Owner Cash Flow\'!S'+fcf+')), IF(\'Third-party Owner Cash Flow\'!T'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!S'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!S'+ccf+'/\'Third-party Owner Cash Flow\'!T'+fcf+')), IF(\'Third-party Owner Cash Flow\'!U'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!T'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!T'+ccf+'/\'Third-party Owner Cash Flow\'!U'+fcf+')), IF(\'Third-party Owner Cash Flow\'!V'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!U'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!U'+ccf+'/\'Third-party Owner Cash Flow\'!V'+fcf+')), IF(\'Third-party Owner Cash Flow\'!W'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!V'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!V'+ccf+'/\'Third-party Owner Cash Flow\'!W'+fcf+')), IF(\'Third-party Owner Cash Flow\'!X'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!W'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!W'+ccf+'/\'Third-party Owner Cash Flow\'!X'+fcf+')), IF(\'Third-party Owner Cash Flow\'!Y'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!X'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!X'+ccf+'/\'Third-party Owner Cash Flow\'!Y'+fcf+')), IF(\'Third-party Owner Cash Flow\'!Z'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!Y'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!Y'+ccf+'/\'Third-party Owner Cash Flow\'!Z'+fcf+')), IF(\'Third-party Owner Cash Flow\'!AA'+ccf+'<0,1,IF(\'Third-party Owner Cash Flow\'!Z'+ccf+'>0,0,-\'Third-party Owner Cash Flow\'!Z'+ccf+'/\'Third-party Owner Cash Flow\'!AA'+fcf+'))))'
        inandout_sheet.write_formula('E10', spp_formula_string, d['proj_fin_format_spp'])

    ###### BAU SHEET (DIRECT OWN)
    def add_bau_direct_own_sheet():
        baucashf_sheet = proforma.add_worksheet('BAU Cash Flow')

        baucashf_sheet.set_column(0, 0, 24.25)
        baucashf_sheet.set_column('B:AA', 10.38)

        baucashf_sheet.write('A1', 'BAU Cash Flow', o['header_format'])
        baucashf_sheet.write_row('A2', ['ANNUAL VALUES']+list(range(0,26)), o['subheader_format'])
        baucashf_sheet.write('A3', 'Business as Usual electricity bill ($)', o['text_format'])
        baucashf_sheet.write('A4', 'Business as Usual export credits ($)', o['text_format'])
        baucashf_sheet.write('A5', 'Business as Usual boiler fuel bill ($)', o['text_format'])
        baucashf_sheet.write('A6', 'Operation and Maintenance (O&M)', o['text_format'])
        baucashf_sheet.write('A7', 'Existing PV cost in $/kW', o['text_format_indent'])
        baucashf_sheet.write('A8', 'Existing Generator fixed O&M cost', o['text_format_indent'])
        baucashf_sheet.write('A9', 'Existing Generator variable O&M cost', o['text_format_indent'])
        baucashf_sheet.write('A10', 'Existing Generator fuel cost ($)', o['text_format_indent'])
        baucashf_sheet.write('A11', 'Total operating expenses', o['text_format_2'])
        baucashf_sheet.write('A12', 'Tax deductible operating expenses', o['text_format_2'])

        baucashf_sheet.write_dynamic_array_formula('C3:AA3', '=-BAU_annual_electricity_bill * (1 + Elec_cost_escal_pct/100)^C2:AA2', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C4:AA4', '=BAU_annual_export_to_grid_benefits * (1 + Elec_cost_escal_pct/100)^C2:AA2', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C5:AA5', '=(-1 * (BAU_boiler_fuel_bill_annual_sum * (1 + Boiler_fuel_cost_escal_pct/100)^C2:AA2))', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C7:AA7', '=-PV_OM_cost * (1 + OM_cost_escal_pct/100)^C2:AA2 * PV_existing_kw', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C8:AA8', '=-Generator_fixed_backup_cost * (1 + OM_cost_escal_pct/100)^C2:AA2 * Generator_existing_kw', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C9:AA9', '=-Generator_variable_backup_cost * (1 + OM_cost_escal_pct/100)^C2:AA2 * Generator_annual_electricity_gen_kwh_bau', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C10:AA10', '=-Diesel_BAU_fuel_used_cost * (1 + Generator_fuel_cost_escal_pct/100)^C2:AA2', o['text_format'])

        for idx in range(2, 27): ## C to AA
            col = base_upper_case_letters[idx] # C through AA
            baucashf_sheet.write_formula(col+'11', '=SUM('+col+'3:'+col+'10)', o['text_format_2'])
            baucashf_sheet.write_formula(col+'12', '=IF(Offtaker_tax_rate > 0, '+col+'11, 0)', o['text_format_2'])


        baucashf_sheet.write_row('A14', ['Production-based incentives (PBI)']+[None]*26, o['subheader_format'])
        baucashf_sheet.write('A15', 'Existing PV Combined PBI', o['text_format_2'])
        baucashf_sheet.write('A16', 'Total taxable cash incentives', o['text_format_2'])
        baucashf_sheet.write('A17', 'Total non-taxable cash incentives', o['text_format_2'])

        baucashf_sheet.write_row('A19', ['Total Cash Flows']+[None]*26, o['subheader_format'])
        baucashf_sheet.write('A20', 'Net Operating expenses, after-tax', o['text_format'])
        baucashf_sheet.write('A21', 'Total Cash incentives, after-tax', o['text_format'])
        baucashf_sheet.write('A22', 'Free Cash Flow', o['text_format_2'])
        baucashf_sheet.write('A23', 'Discounted Cash Flow', o['text_format_2'])
        baucashf_sheet.write('A24', 'BAU Life Cycle Cost', o['standalone_bold_text_format'])

        baucashf_sheet.write_dynamic_array_formula('C20:AA20', '=(C11:AA11 - C12:AA12) + C12:AA12 * (1 - Offtaker_tax_rate/100)', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C21:AA21', '=(C16:AA16 * (1 - Offtaker_tax_rate/100)) + C17:AA17', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C22:AA22', '=C20:AA20 + C21:AA21', o['text_format_2'])
        proforma.define_name('BAU_free_cash_flow_range', '=\'BAU Cash Flow\'!$B$22:$AA$22')
        baucashf_sheet.write_dynamic_array_formula('C23:AA23', '=C22:AA22 / (1 + Offtaker_discount_rate/100)^C2:AA2', o['text_format_2'])
        baucashf_sheet.write_formula('B24', '=SUM(B23:AA23)', o['standalone_bold_text_format'])

    ## HOST CASHFLOW SHEET 3rd PARTY
    def add_host_cash_flow_thirdpartyown():
        baucashf_sheet = proforma.add_worksheet('Host Cash Flow')

        baucashf_sheet.set_column(0, 0, 24.25)
        baucashf_sheet.set_column('B:AA', 10.38)

        baucashf_sheet.write('A1', 'Host Cash Flow', o['header_format'])
        baucashf_sheet.write_row('A2', ['Operating Expenses']+list(range(0,26)), o['subheader_format'])
        baucashf_sheet.write('A3', 'Business as Usual electricity bill ($)', o['text_format'])
        baucashf_sheet.write('A4', 'Business as Usual export credits ($)', o['text_format'])
        baucashf_sheet.write('A5', 'Electricity bill with optimal system before export credits', o['text_format'])
        baucashf_sheet.write('A6', 'Export credits with optimal system', o['text_format'])
        baucashf_sheet.write('A7', 'Business as Usual boiler fuel bill ($)', o['text_format'])
        baucashf_sheet.write('A8', 'Boiler fuel bill with optimal systems ($)', o['text_format'])
        baucashf_sheet.write('A9', 'CHP fuel bill with optimal systems ($)', o['text_format'])
        baucashf_sheet.write('A10', 'Payment to Third-party Owner', o['text_format'])
        baucashf_sheet.write('A11', 'Business as Usual Generator fuel cost ($)', o['text_format'])
        baucashf_sheet.write('A12', 'Business as Usual Generator fixed O&M cost ($)', o['text_format'])
        baucashf_sheet.write('A13', 'Generator fuel cost with optimal system ($)', o['text_format'])
        baucashf_sheet.write('A14', 'Existing PV fixed O&M cost ($)', o['text_format'])
        baucashf_sheet.write('A15', 'Business as Usual Free Cash Flow', o['text_format_2'])
        baucashf_sheet.write('A16', 'Optimal Free Cash Flow', o['text_format_2'])
        baucashf_sheet.write('A17', 'Net Energy Costs ($)', o['text_format_2'])
        baucashf_sheet.write('A18', 'Tax deductible Electricity Costs ($)', o['text_format_2'])

        # row = add_operating_expenses(row, 'Existing PV fixed O&M cost', '')

        baucashf_sheet.write_dynamic_array_formula('C3:AA3', '=-BAU_annual_electricity_bill * (1 + Elec_cost_escal_pct/100)^C2:AA2', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C4:AA4', '=BAU_annual_export_to_grid_benefits * (1 + Elec_cost_escal_pct/100)^C2:AA2', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C5:AA5', '=-OPT_annual_electricity_bill * (1 + Elec_cost_escal_pct/100)^C2:AA2', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C6:AA6', '=OPT_annual_export_to_grid_benefits * (1 + Elec_cost_escal_pct/100)^C2:AA2', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C7:AA7', '=-BAU_boiler_fuel_bill_annual_sum * (1 + Boiler_fuel_cost_escal_pct/100)^C2:AA2', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C8:AA8', '=-OPT_boiler_fuel_bill_annual_sum * (1 + Boiler_fuel_cost_escal_pct/100)^C2:AA2', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C9:AA9', '=-CHP_fuels_annual_fuel_bill_sum * (1 + CHP_fuel_cost_escal_rate/100)^C2:AA2', o['text_format'])
        baucashf_sheet.write_array_formula('C10:AA10', '{=-Annual_payment_to_developer}', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C11:AA11', '=-Diesel_BAU_fuel_used_cost * (1 + Generator_fuel_cost_escal_pct/100)^C2:AA2', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C12:AA12', '=-Generator_fixed_backup_cost * Generator_existing_kw * (1 + OM_cost_escal_pct/100)^C2:AA2', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C13:AA13', '=-Diesel_fuel_used_cost * (1 + Generator_fuel_cost_escal_pct/100)^C2:AA2', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C14:AA14', '=-PV_OM_cost * PV_existing_kw * (1 + OM_cost_escal_pct/100)^C2:AA2', o['text_format'])
        baucashf_sheet.write_array_formula('C15:AA15', '{=C3:AA3 + C4:AA4 + C11:AA11  + C12:AA12 + C14:AA14}', o['text_format_2'])
        baucashf_sheet.write_array_formula('C16:AA16', '{=C5:AA5 + C6:AA6 + C10:AA10 + C12:AA12 + C13:AA13 + C14:AA14}', o['text_format_2'])
        baucashf_sheet.write_array_formula('C17:AA17', '{=-C3:AA3 - C4:AA4 + C5:AA5 + C6:AA6 + C10:AA10 - C11:AA11 + C13:AA13 - C7:AA7 + C8:AA8 + C9:AA9}', o['text_format_2'])
        baucashf_sheet.write_array_formula('C18:AA18', '{=IF(Offtaker_tax_rate/100 > 0, C17:AA17, 0)}', o['text_format_2'])

        baucashf_sheet.write_row('A20', ['Total Cash Flows']+[None]*26, o['subheader_format'])
        baucashf_sheet.write('A21', 'Net Operating expense, after tax', o['text_format_2'])
        baucashf_sheet.write_array_formula('C21:AA21', '{=(C17:AA17 - C18:AA18) + C18:AA18*(1-Offtaker_tax_rate/100)}', o['text_format_2'])
        baucashf_sheet.write('A22', 'Discounted Cash Flow', o['text_format_2'])
        baucashf_sheet.write_array_formula('C22:AA22', '{=C21:AA21/((1+Offtaker_discount_rate/100)^C2:AA2)}', o['text_format_2'])
        baucashf_sheet.write('A23', 'Host Net Present Value', o['standalone_bold_text_format'])
        baucashf_sheet.write_formula('B23', '=SUM(B22:AA22)', o['standalone_bold_text_format'])
        proforma.define_name('Host_Net_Present_Value', '=\'Host Cash Flow\'!$B$23')

    #### MAIN
    # Create a workbook and three worksheets.
    proforma = xlsxwriter.Workbook(output, {"in_memory": True})

    # Add styles
    d, o = create_styles(proforma)

    third_party_own = results['inputs']['Financial']['third_party_ownership'] # BOOL

    if third_party_own:
        discount_rate_fieldname = 'Developer_discount_rate'
        tax_rate_fieldname = 'Developer_tax_rate'
    else:
        discount_rate_fieldname = 'Offtaker_discount_rate'
        tax_rate_fieldname = 'Offtaker_tax_rate'

    # Create inandout sheet
    inandout_sheet = proforma.add_worksheet('Inputs and Outputs')

    # set column widths
    inandout_sheet.set_column('A:A', 74)
    inandout_sheet.set_column('B:B', 14.75)
    inandout_sheet.set_column('C:C', 13.25)
    inandout_sheet.set_column('D:D', 23.88)
    inandout_sheet.set_column('E:E', 23.88)
    inandout_sheet.set_column('F:F', 26.88)

    inandout_sheet.write('A1', 'Results Summary and Inputs', d['header_format'])
    inandout_sheet.write('A2', 'OPTIMAL SYSTEM DESIGN (with existing)', d['subheader_format'])

    start_row = 3
    shift = 0 # quickly shift local rows to adjust new rows

    section_end = optimal_system_design(start_row, shift, discount_rate_fieldname)

    inandout_sheet.write('A'+str(section_end+1), 'ANNUAL RESULTS', d['subheader_format'])
    # start_row, shift = 0
    section_end = annual_results(section_end+2, 0)

    inandout_sheet.write('A'+str(section_end+1), 'SYSTEM COSTS', d['subheader_format'])
    section_end = system_costs(section_end+2,0)

    inandout_sheet.write('A'+str(section_end+1), 'ANALYSIS PARAMETERS', d['subheader_format'])
    section_end = analysis_parameters(section_end+2,0,third_party_own)

    inandout_sheet.write('A'+str(section_end+1), 'TAX AND INSURANCE PARAMETERS', d['subheader_format'])
    section_end = tax_insurance_params(section_end+2, 0, third_party_own)

    inandout_sheet.write('A'+str(section_end+1), 'PV TAX CREDITS', d['subheader_format'])
    section_end = pv_tax_credits(section_end+2, 0)
    inandout_sheet.write('A'+str(section_end+1), 'PV DIRECT CASH INCENTIVES', d['subheader_format'])
    section_end = pv_direct_cash_incentives(section_end+2, 0)
    inandout_sheet.write('A'+str(section_end+1), 'WIND TAX CREDITS', d['subheader_format'])
    section_end = wind_tax_credits(section_end+2, 0)
    inandout_sheet.write('A'+str(section_end+1), 'WIND DIRECT CASH INCENTIVES', d['subheader_format'])
    section_end = wind_direct_cash_incentives(section_end+2, 0)
    inandout_sheet.write('A'+str(section_end+1), 'BATTERY TAX CREDITS', d['subheader_format'])
    section_end = battery_tax_credits(section_end+2, 0)
    inandout_sheet.write('A'+str(section_end+1), 'BATTERY DIRECT CASH INCENTIVES', d['subheader_format'])
    section_end = battery_direct_cash_incentives(section_end+2, 0)
    inandout_sheet.write('A'+str(section_end+1), 'CHP TAX CREDITS', d['subheader_format'])
    section_end = chp_tax_credits(section_end+2, 0)
    inandout_sheet.write('A'+str(section_end+1), 'CHP DIRECT CASH INCENTIVES', d['subheader_format'])
    section_end = chp_direct_cash_incentives(section_end+2, 0)
    inandout_sheet.write('A'+str(section_end+1), 'GHP TAX CREDITS', d['subheader_format'])
    section_end = ghp_tax_credits(section_end+2, 0)
    inandout_sheet.write('A'+str(section_end+1), 'GHP DIRECT CASH INCENTIVES', d['subheader_format'])
    section_end = ghp_direct_cash_incentives(section_end+2, 0)

    section_end, macrs_option_year_row, macrs_bonus_fraction_row = add_tech_depreciation_info(section_end)

    ## ANNUAL VALUES first two columns
    section_end += 2
    inandout_sheet.write_row('A'+str(section_end+1), ['ANNUAL VALUES']+list(range(0,26)), d['subheader_format'])

    section_end+=1
    annual_value_rows = copy(section_end)

    annual_values_row_labels = [
        ['PV Annual electricity (kWh)', 0],
        ['Existing PV Annual electricity (kWh)', 0],
        ['Wind Annual electricity (kWh)', 0],
        ['Backup Generator Annual electricity (kWh)', 0],
        ['CHP Annual electricity (kWh)', 0],
        ['CHP Annual heat (MMBtu)', 0],
        ['Steam Turbine Annual electricity (kWh)', 0],
        ['Steam Turbine Annual heat (MMBtu)', 0],
        ['ASHP Space Heater Annual Heat (MMBtu)', 0],
        ['ASHP Water Heater Annual Heat (MMBtu)', 0],
        ['PV Federal depreciation percentages (fraction)', 0],
        ['Wind Federal depreciation percentages (fraction)', 0],
        ['Battery Federal depreciation percentages (fraction)', 0],
        ['CHP Federal depreciation percentages (fraction)', 0],
        ['Absorption Chiller Federal depreciation percentages (fraction)', 0],
        ['ASHP Space Heater Federal depreciation percentages (fraction)', 0],
        ['ASHP Water Heater Federal depreciation percentages (fraction)', 0],
        ['Hot TES Federal depreciation percentages (fraction)', 0],
        ['Cold TES Federal depreciation percentages (fraction)', 0],
        ['Steam turbine Federal depreciation percentages (fraction)', 0],
        ['GHP Federal depreciation percentages (fraction)', 0]
    ]

    if not third_party_own:
        annual_values_row_labels.append(['Free Cash Flow', None])
        annual_values_row_labels.append(['Cumulative Free Cash Flow', None])

    # Add first two column values
    for val in annual_values_row_labels:
        inandout_sheet.write('A'+str(section_end+1), val[0])
        inandout_sheet.write('B'+str(section_end+1), val[1])
        section_end+=1

    annual_value_rows = add_annual_generation_values(annual_value_rows)

    proforma.define_name('PV_depreciation_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+1)+':$AA$'+str(annual_value_rows+1))
    proforma.define_name('Wind_depreciation_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+2)+':$AA$'+str(annual_value_rows+2))
    proforma.define_name('Battery_depreciation_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+3)+':$AA$'+str(annual_value_rows+3))
    proforma.define_name('CHP_depreciation_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+4)+':$AA$'+str(annual_value_rows+4))
    proforma.define_name('AbsorptionChiller_depreciation_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+5)+':$AA$'+str(annual_value_rows+5))
    proforma.define_name('ASHPSpaceHeater_depreciation_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+6)+':$AA$'+str(annual_value_rows+6))
    proforma.define_name('ASHPWaterHeater_depreciation_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+7)+':$AA$'+str(annual_value_rows+7))
    proforma.define_name('HotTES_depreciation_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+8)+':$AA$'+str(annual_value_rows+8))
    proforma.define_name('ColdTES_depreciation_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+9)+':$AA$'+str(annual_value_rows+9))
    proforma.define_name('SteamTurbine_depreciation_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+10)+':$AA$'+str(annual_value_rows+10))
    proforma.define_name('GHP_depreciation_range', '=\'Inputs and Outputs\'!$C$'+str(annual_value_rows+11)+':$AA$'+str(annual_value_rows+11))

    annual_value_rows = add_macrs_years_for_techs(annual_value_rows, macrs_option_year_row)

    if not third_party_own:
        ## CASH FLOW LINES LEFT.
        inandout_sheet.write_array_formula('B'+ str(annual_value_rows+1)+ ':AA' +str(annual_value_rows+1), '{=OPT_free_cash_flow_range-BAU_free_cash_flow_range}', d['proj_fin_format'])
        proforma.define_name('Net_free_cash_flow_range', '=\'Inputs and Outputs\'!$B$'+str(annual_value_rows+1)+':$AA$'+str(annual_value_rows+1))
        fcf_row = annual_value_rows+1

        annual_value_rows += 1
        inandout_sheet.write_blank('A'+ str(annual_value_rows+1), None)
        inandout_sheet.write_formula('B'+str(annual_value_rows+1), '=\'Inputs and Outputs\'!B'+str(annual_value_rows))
        for idx in range(2, 27): # C to AA
            col = base_upper_case_letters[idx] # C through AA
            col_1 = base_upper_case_letters[idx-1] # B through Z
            
            inandout_sheet.write_formula(
                col+str(annual_value_rows+1),
                '='+col+str(annual_value_rows)+'+'+col_1+str(annual_value_rows+1),
                d['proj_fin_format']
            )
        ccf_row = annual_value_rows+1

    # ^[^,]* regex to find all chars till first ","

    ###### OPT CASHFLOW SHEET
    if third_party_own:
        optcashf_sheet = proforma.add_worksheet('Third-party Owner Cash Flow')
        optcashf_sheet.write('A1', 'Third-party Cash Flow', o['header_format'])
        sheet = 'Third-party Owner Cash Flow'
    else:
        optcashf_sheet = proforma.add_worksheet('Optimal Cash Flow')
        optcashf_sheet.write('A1', 'Optimal Cash Flow', o['header_format'])
        sheet = 'Optimal Cash Flow'

    # column widths
    optcashf_sheet.set_column('A:A', 31.75)
    optcashf_sheet.set_column('B:AA', 10.38)
    optcashf_sheet.freeze_panes(2,0)

    optcashf_sheet.write_row('A2', ['Operating Year']+list(range(0,26)), o['year_format'])

    optcashf_sheet.write_row('A4', ['Operating Expenses']+[None]*26, o['subheader_format'])

    row = 5
    row, Battery_kw_replacement_row, Battery_kwh_replacement_row = add_operating_expense_rows(row, sheet, third_party_own)
    row = complete_operating_expense_rows(Battery_kw_replacement_row, Battery_kwh_replacement_row, row, tax_rate_fieldname)
    row += 3
    row = add_direct_cash_incentives(row, sheet)
    row = add_capital_depreciation_LCOE_calculations(row, sheet, tax_rate_fieldname)
    row = add_federal_itc_calculations(row, sheet)
    row = add_total_cash_flow_calculations(row, sheet, discount_rate_fieldname, tax_rate_fieldname)

    if third_party_own:
        optcashf_sheet.write('A'+str(row), 'Third-party Owner Net Present Cost', o['text_format_2'])
        proforma.define_name('Net_present_cost_to_thirdparty', '=\'Third-party Owner Cash Flow\'!$B$'+str(row))
        row += 1
        optcashf_sheet.write_row('A'+str(row), ['Capital Recovery Factor', '=Developer_discount_rate/100 * POWER(1 + Developer_discount_rate/100, Analysis_period_years) / (POWER(1 + Developer_discount_rate/100, Analysis_period_years) - 1) / (1 - Developer_tax_rate/100)'], o['text_format_decimal'])
        proforma.define_name('Capital_recovery_factor_thirdparty', '=\'Third-party Owner Cash Flow\'!$B$'+str(row))
        row +=1
        optcashf_sheet.write('A'+str(row), 'Income from Host', o['text_format'])
        optcashf_sheet.write_array_formula('C'+str(row)+':AA'+str(row), '{=Capital_recovery_factor_thirdparty*(-1)* Net_present_cost_to_thirdparty}', o['text_format'])
        proforma.define_name('Annual_payment_to_developer', '=\'Third-party Owner Cash Flow\'!$C$'+str(row))
        row+=1
        optcashf_sheet.write('A'+str(row), 'Income from Host, after-tax', o['text_format'])
        optcashf_sheet.write_array_formula('C'+str(row)+':AA'+str(row), '=Capital_recovery_factor_thirdparty*(-1)* Net_present_cost_to_thirdparty* (1 - Developer_tax_rate/100)', o['text_format'])
        row+=1
        optcashf_sheet.write('A'+str(row), 'Discounted Income from Host', o['text_format'])
        optcashf_sheet.write_array_formula('C'+str(row)+':AA'+str(row), '=(Capital_recovery_factor_thirdparty*(-1)* Net_present_cost_to_thirdparty * (1 - Developer_tax_rate/100))/(1 + Developer_discount_rate/100)^1', o['text_format'])
        row+=1
        optcashf_sheet.write_row('A'+str(row), ['NPV of Income from Host', '=SUM(C'+str(row-1)+':AA'+str(row-1)+')'], o['text_format'])
        row+=1
        optcashf_sheet.write('A'+str(row), 'Free Cash Flow after Income', o['text_format'])
        optcashf_sheet.write_formula('B'+str(row), '=B'+str(row-8), o['text_format'])
        optcashf_sheet.write_array_formula('C'+str(row)+':AA'+str(row), '=C'+str(row-8)+':AA'+str(row-8)+'+C'+str(row-3)+':AA'+str(row-3), o['text_format'])
        proforma.define_name('Thirdparty_freecashflow_range', '=\'Third-party Owner Cash Flow\'!$B$'+str(row)+':$AA$'+str(row))
        thirdparty_fcf_row = str(row)
        row+=1
        optcashf_sheet.write('A'+str(row), 'Cumulative Free Cash Flow after Income', o['text_format'])
        optcashf_sheet.write_formula('B'+str(row), '=B'+str(row-1), o['text_format'])
        optcashf_sheet.write_array_formula('C'+str(row)+':AA'+str(row), '=C'+str(row-1)+':AA'+str(row-1)+'+B'+str(row)+':Z'+str(row), o['text_format'])
        thirdparty_ccf_row = str(row)

    #### BAU SHEET (DIRECT OWN) or HOST CASH FLOW (THIRD PARTY OWN)
    if not third_party_own:
        add_bau_direct_own_sheet()
    else:
        add_host_cash_flow_thirdpartyown()

    ## SUMMARY PROJECT ECONOMICS, defined in end as there may be dependencies to BAU/HOST sheets
    if not third_party_own:
        add_direct_own_project_economics_summary()
    else:
        add_third_party_own_project_economics_summary(thirdparty_fcf_row, thirdparty_ccf_row)

    proforma.close()

    # return proforma
