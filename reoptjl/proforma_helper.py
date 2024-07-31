import xlsxwriter
import pandas as pd
import numpy as np
import os

# print('**', os.path.realpath(__file__))

# mapping = pd.read_csv('proforma_dependencies\mapping.csv')
# mapping_static = pd.read_csv('reoptjl\proforma_dependencies\static_fields.csv')

# inputs
def proforma_helper(results:dict, output):
    # Create a workbook and three worksheets.
    # proforma = xlsxwriter.Workbook('proforma.xlsx'output, {"in_memory": True})

    proforma = xlsxwriter.Workbook(output, {"in_memory": True})

    base_upper_case_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                            'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA']
    
    ## Large formulas
    spp_years = '=IF(\'Inputs and Outputs\'!B200=0,"", IF(\'Inputs and Outputs\'!AA200 < 0, "Over 25", SUM(IF(\'Inputs and Outputs\'!C200<0,1,IF(\'Inputs and Outputs\'!B200>0,0,-\'Inputs and Outputs\'!B200/\'Inputs and Outputs\'!C199)), IF(\'Inputs and Outputs\'!D200<0,1,IF(\'Inputs and Outputs\'!C200>0,0,-\'Inputs and Outputs\'!C200/\'Inputs and Outputs\'!D199)), IF(\'Inputs and Outputs\'!E200<0,1,IF(\'Inputs and Outputs\'!D200>0,0,-\'Inputs and Outputs\'!D200/\'Inputs and Outputs\'!E199)), IF(\'Inputs and Outputs\'!F200<0,1,IF(\'Inputs and Outputs\'!E200>0,0,-\'Inputs and Outputs\'!E200/\'Inputs and Outputs\'!F199)), IF(\'Inputs and Outputs\'!G200<0,1,IF(\'Inputs and Outputs\'!F200>0,0,-\'Inputs and Outputs\'!F200/\'Inputs and Outputs\'!G199)), IF(\'Inputs and Outputs\'!H200<0,1,IF(\'Inputs and Outputs\'!G200>0,0,-\'Inputs and Outputs\'!G200/\'Inputs and Outputs\'!H199)), IF(\'Inputs and Outputs\'!I200<0,1,IF(\'Inputs and Outputs\'!H200>0,0,-\'Inputs and Outputs\'!H200/\'Inputs and Outputs\'!I199)), IF(\'Inputs and Outputs\'!J200<0,1,IF(\'Inputs and Outputs\'!I200>0,0,-\'Inputs and Outputs\'!I200/\'Inputs and Outputs\'!J199)), IF(\'Inputs and Outputs\'!K200<0,1,IF(\'Inputs and Outputs\'!J200>0,0,-\'Inputs and Outputs\'!J200/\'Inputs and Outputs\'!K199)), IF(\'Inputs and Outputs\'!L200<0,1,IF(\'Inputs and Outputs\'!K200>0,0,-\'Inputs and Outputs\'!K200/\'Inputs and Outputs\'!L199)), IF(\'Inputs and Outputs\'!M200<0,1,IF(\'Inputs and Outputs\'!L200>0,0,-\'Inputs and Outputs\'!L200/\'Inputs and Outputs\'!M199)), IF(\'Inputs and Outputs\'!N200<0,1,IF(\'Inputs and Outputs\'!M200>0,0,-\'Inputs and Outputs\'!M200/\'Inputs and Outputs\'!N199)), IF(\'Inputs and Outputs\'!O200<0,1,IF(\'Inputs and Outputs\'!N200>0,0,-\'Inputs and Outputs\'!N200/\'Inputs and Outputs\'!O199)), IF(\'Inputs and Outputs\'!P200<0,1,IF(\'Inputs and Outputs\'!O200>0,0,-\'Inputs and Outputs\'!O200/\'Inputs and Outputs\'!P199)), IF(\'Inputs and Outputs\'!Q200<0,1,IF(\'Inputs and Outputs\'!P200>0,0,-\'Inputs and Outputs\'!P200/\'Inputs and Outputs\'!Q199)), IF(\'Inputs and Outputs\'!R200<0,1,IF(\'Inputs and Outputs\'!Q200>0,0,-\'Inputs and Outputs\'!Q200/\'Inputs and Outputs\'!R199)), IF(\'Inputs and Outputs\'!S200<0,1,IF(\'Inputs and Outputs\'!R200>0,0,-\'Inputs and Outputs\'!R200/\'Inputs and Outputs\'!S199)), IF(\'Inputs and Outputs\'!T200<0,1,IF(\'Inputs and Outputs\'!S200>0,0,-\'Inputs and Outputs\'!S200/\'Inputs and Outputs\'!T199)), IF(\'Inputs and Outputs\'!U200<0,1,IF(\'Inputs and Outputs\'!T200>0,0,-\'Inputs and Outputs\'!T200/\'Inputs and Outputs\'!U199)), IF(\'Inputs and Outputs\'!V200<0,1,IF(\'Inputs and Outputs\'!U200>0,0,-\'Inputs and Outputs\'!U200/\'Inputs and Outputs\'!V199)), IF(\'Inputs and Outputs\'!W200<0,1,IF(\'Inputs and Outputs\'!V200>0,0,-\'Inputs and Outputs\'!V200/\'Inputs and Outputs\'!W199)), IF(\'Inputs and Outputs\'!X200<0,1,IF(\'Inputs and Outputs\'!W200>0,0,-\'Inputs and Outputs\'!W200/\'Inputs and Outputs\'!X199)), IF(\'Inputs and Outputs\'!Y200<0,1,IF(\'Inputs and Outputs\'!X200>0,0,-\'Inputs and Outputs\'!X200/\'Inputs and Outputs\'!Y199)), IF(\'Inputs and Outputs\'!Z200<0,1,IF(\'Inputs and Outputs\'!Y200>0,0,-\'Inputs and Outputs\'!Y200/\'Inputs and Outputs\'!Z199)), IF(\'Inputs and Outputs\'!AA200<0,1,IF(\'Inputs and Outputs\'!Z200>0,0,-\'Inputs and Outputs\'!Z200/\'Inputs and Outputs\'!AA199)))))'

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

    ### FUNCTIONS
    # Generic function to pull values or get 0 instead of Null
    def get_value(one:str, two:str, three:str):
        try:
            if two in results[one].keys():
                if results[one][two][three] == None:
                    return 0.0
                if type(results[one][two][three]) == str: # API bugs?
                    return float(results[one][two][three])
                return results[one][two][three]
            else: # tech was excluded from run, avoid missing key errors.
                return 0.0
        except:
            # print('error on ', one,two,three) ## debug line
            return 0.0
        
    def get_chp_installed_cost_us_dollars():
        ## CHP installed cost determination
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
    
    ## INPUTS/OUTPUTS sheet
    # create sheet
    inandout_sheet = proforma.add_worksheet('Inputs and Outputs')

    ## INPUTS/OUTPUTS sheet

    ## STATIC FIXED FIELDS
    inandout_sheet.write('A1', 'Results Summary and Inputs', d['header_format'])
    inandout_sheet.write('A2', 'OPTIMAL SYSTEM DESIGN (with existing)', d['subheader_format'])
    inandout_sheet.write('A3', 'PV Nameplate capacity (kW), purchased', d['text_format'])
    inandout_sheet.write('A4', 'PV Nameplate capacity (kW), existing', d['text_format'])
    inandout_sheet.write('A5', 'PV degradation rate (%/year)', d['text_format'])
    inandout_sheet.write('A6', 'PV LCOE of New Capacity ($/kWh), nominal', d['text_format'])
    inandout_sheet.write('A7', 'Wind Nameplate capacity (kW), purchased', d['text_format'])
    inandout_sheet.write('A8', 'Wind LCOE ($/kWh), nominal', d['text_format'])
    inandout_sheet.write('A9', 'Backup Generator Nameplate capacity (kW), purchased', d['text_format'])
    inandout_sheet.write('A10', 'Backup Generator Nameplate capacity (kW), existing', d['text_format'])
    inandout_sheet.write('A11', 'Battery power (kW)', d['text_format'])
    inandout_sheet.write('A12', 'Battery capacity (kWh)', d['text_format'])
    inandout_sheet.write('A13', 'CHP capacity (kW)', d['text_format'])
    inandout_sheet.write('A14', 'Absorption chiller capacity (tons)', d['text_format'])
    inandout_sheet.write('A15', 'Chilled water TES capacity (gallons)', d['text_format'])
    inandout_sheet.write('A16', 'Hot water TES capacity (gallons)', d['text_format'])
    inandout_sheet.write('A17', 'Steam turbine capacity (kW)', d['text_format'])
    inandout_sheet.write('A18', 'GHP heat pump capacity (ton)', d['text_format'])
    inandout_sheet.write('A19', 'GHP ground heat exchanger size (ft)', d['text_format'])
    inandout_sheet.write('A21', 'ANNUAL RESULTS', d['subheader_format'])
    inandout_sheet.write('A22', 'Present value of annual Business as Usual electric utility bill ($/year)', d['text_format'])
    inandout_sheet.write('A23', 'Present value of annual Business as Usual export credits ($/year)', d['text_format'])
    inandout_sheet.write('A24', 'Present value of annual Optimal electric utility bill($/year)', d['text_format'])
    inandout_sheet.write('A25', 'Present value of annual Optimal export credits ($/year)', d['text_format'])
    inandout_sheet.write('A26', 'Existing PV electricity produced (kWh), Year 1', d['text_format'])
    inandout_sheet.write('A27', 'Total PV optimal electricity produced (kWh), Year 1', d['text_format'])
    inandout_sheet.write('A28', 'PV optimal electricity produced (kWh), Annual Average', d['text_format'])
    inandout_sheet.write('A29', 'Nominal annual optimal wind electricity produced (kWh/year)', d['text_format'])
    inandout_sheet.write('A30', 'Nominal annual optimal backup generator electricity produced (kWh/year)', d['text_format'])
    inandout_sheet.write('A31', 'CHP annual optimal electricity produced (kWh/year)', d['text_format'])
    inandout_sheet.write('A32', 'CHP annual runtime (hours/year)', d['text_format'])
    inandout_sheet.write('A33', 'Steam turbine annual optimal electricity produced (kWh/year)', d['text_format'])
    inandout_sheet.write('A34', 'Total optimal electricity produced (kWh/year)', d['text_format'])
    inandout_sheet.write('A35', 'Present value of annual Business as Usual boiler fuels utility bill ($/year)', d['text_format'])
    inandout_sheet.write('A36', 'Present value of annual Optimal boiler fuels utility bill ($/year)', d['text_format'])
    inandout_sheet.write('A37', 'Present value of annual CHP fuels utility bill ($/year)', d['text_format'])
    inandout_sheet.write('A38', 'CHP annual optimal thermal energy produced (MMBtu/year)', d['text_format'])
    inandout_sheet.write('A39', 'Steam turbine annual optimal thermal energy produced (MMBtu/year)', d['text_format'])
    inandout_sheet.write('A40', 'Percent electricity from on-site renewable resources', d['text_format'])
    inandout_sheet.write('A41', 'Percent reduction in annual electricity bill', d['text_format'])
    inandout_sheet.write('A42', 'Percent reduction in annual fuels bill', d['text_format'])
    inandout_sheet.write('A43', 'Year one total site carbon dioxide emissions (ton CO2)', d['text_format'])
    inandout_sheet.write('A44', 'Year one total site carbon dioxide emissions BAU (ton CO2)', d['text_format'])
    inandout_sheet.write('A45', 'Year one total carbon dioxide emissions from electric utility purchases (ton CO2)', d['text_format'])
    inandout_sheet.write('A46', 'Year one total carbon dioxide emissions from electric utility purchases BAU (ton CO2)', d['text_format'])
    inandout_sheet.write('A47', 'Year one total carbon dioxide emissions from on-site fuel burn (ton CO2)', d['text_format'])
    inandout_sheet.write('A48', 'Year one total carbon dioxide emissions from on-site fuel burn BAU (ton CO2)', d['text_format'])
    inandout_sheet.write('A50', 'SYSTEM COSTS', d['subheader_format'])
    inandout_sheet.write('A51', 'Total Installed Cost ($)', d['text_format'])
    inandout_sheet.write('A52', 'PV Installed Cost ($)', d['text_format'])
    inandout_sheet.write('A53', 'Wind Installed Cost ($)', d['text_format'])
    inandout_sheet.write('A54', 'Backup generator Installed Cost ($)', d['text_format'])
    inandout_sheet.write('A55', 'Battery Installed Cost ($)', d['text_format'])
    inandout_sheet.write('A56', 'CHP Installed Cost ($)', d['text_format'])
    inandout_sheet.write('A57', 'Absorption Chiller Installed Cost ($)', d['text_format'])
    inandout_sheet.write('A58', 'Hot water TES Installed Cost ($)', d['text_format'])
    inandout_sheet.write('A59', 'Chilled water TES Installed Cost ($)', d['text_format'])
    inandout_sheet.write('A60', 'Steam turbine Installed Cost ($)', d['text_format'])
    inandout_sheet.write('A61', 'GHP Installed Cost ($)', d['text_format'])
    inandout_sheet.write('A62', 'Operation and Maintenance (O&M)', d['bold_text_format'])
    inandout_sheet.write('A63', 'Fixed PV O&M ($/kW-yr)', d['text_format_indent'])
    inandout_sheet.write('A64', 'Fixed Wind O&M ($/kW-yr)', d['text_format_indent'])
    inandout_sheet.write('A65', 'Fixed Backup Generator O&M ($/kW-yr)', d['text_format_indent'])
    inandout_sheet.write('A66', 'Variable Backup Generator O&M ($/kWh)', d['text_format_indent'])
    inandout_sheet.write('A67', 'Diesel fuel used cost ($)', d['text_format_indent'])
    inandout_sheet.write('A68', 'Diesel BAU fuel used cost ($)', d['text_format_indent'])
    inandout_sheet.write('A69', 'Battery replacement cost ($/kW)', d['text_format_indent'])
    inandout_sheet.write('A70', 'Battery kW replacement year', d['text_format_indent'])
    inandout_sheet.write('A71', 'Battery replacement cost ($/kWh)', d['text_format_indent'])
    inandout_sheet.write('A72', 'Battery kWh replacement year', d['text_format_indent'])
    inandout_sheet.write('A73', 'Fixed CHP O&M cost ($/kW-yr)', d['text_format_indent'])
    inandout_sheet.write('A74', 'Variable CHP O&M cost ($/kWh)', d['text_format_indent'])
    inandout_sheet.write('A75', 'Runtime CHP O&M cost ($/kW-rated/run-hour)', d['text_format_indent'])
    inandout_sheet.write('A76', 'Fixed Absorption Chiller O&M cost ($/ton-yr)', d['text_format_indent'])
    inandout_sheet.write('A77', 'Fixed Chilled water TES O&M cost ($/gallon-year)', d['text_format_indent'])
    inandout_sheet.write('A78', 'Fixed Hot water TES O&M cost ($/gallon-year)', d['text_format_indent'])
    inandout_sheet.write('A79', 'Fixed Steam Turbine O&M ($/kW-yr)', d['text_format_indent'])
    inandout_sheet.write('A80', 'Variable Steam Turbine O&M ($/kWh)', d['text_format_indent'])
    inandout_sheet.write('A81', 'Fixed GHP O&M ($/yr)', d['text_format_indent'])
    inandout_sheet.write('A83', 'ANALYSIS PARAMETERS', d['subheader_format'])
    inandout_sheet.write('A84', 'Analysis period (years)', d['text_format'])
    inandout_sheet.write('A85', 'Nominal O&M cost escalation rate (%/year)', d['text_format'])
    inandout_sheet.write('A86', 'Nominal electric utility cost escalation rate (%/year)', d['text_format'])
    inandout_sheet.write('A87', 'Nominal boiler fuel cost escalation rate (%/year)', d['text_format'])
    inandout_sheet.write('A88', 'Nominal CHP fuel cost escalation rate (%/year)', d['text_format'])
    inandout_sheet.write('A89', 'Nominal discount rate (%/year)', d['text_format'])
    inandout_sheet.write('A91', 'TAX AND INSURANCE PARAMETERS', d['subheader_format'])
    inandout_sheet.write('A92', 'Federal income tax rate (%)', d['text_format'])
    inandout_sheet.write('A94', 'PV TAX CREDITS', d['subheader_format'])
    inandout_sheet.write('A95', 'Investment tax credit (ITC)', d['bold_text_format'])
    inandout_sheet.write('A96', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A97', 'Federal', d['text_format_indent_2'])
    inandout_sheet.write('A99', 'PV DIRECT CASH INCENTIVES', d['subheader_format'])
    inandout_sheet.write('A100', 'Investment based incentive (IBI)', d['bold_text_format'])
    inandout_sheet.write('A101', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A102', 'State (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A103', 'Utility (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A104', 'Capacity based incentive (CBI)', d['bold_text_format'])
    inandout_sheet.write('A105', 'Federal ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A106', 'State  ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A107', 'Utility  ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A108', 'Production based incentive (PBI)', d['bold_text_format'])
    inandout_sheet.write('A109', 'Combined ($/kWh)', d['text_format_indent_2'])
    inandout_sheet.write('A111', 'WIND TAX CREDITS', d['subheader_format'])
    inandout_sheet.write('A112', 'Investment tax credit (ITC)', d['bold_text_format'])
    inandout_sheet.write('A113', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A114', 'Federal', d['text_format_indent_2'])
    inandout_sheet.write('A116', 'WIND DIRECT CASH INCENTIVES', d['subheader_format'])
    inandout_sheet.write('A117', 'Investment based incentive (IBI)', d['bold_text_format'])
    inandout_sheet.write('A118', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A119', 'State (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A120', 'Utility (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A121', 'Capacity based incentive (CBI)', d['bold_text_format'])
    inandout_sheet.write('A122', 'Federal ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A123', 'State  ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A124', 'Utility  ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A125', 'Production based incentive (PBI)', d['bold_text_format'])
    inandout_sheet.write('A126', 'Combined ($/kWh)', d['text_format_indent_2'])
    inandout_sheet.write('A128', 'BATTERY TAX CREDITS', d['subheader_format'])
    inandout_sheet.write('A129', 'Investment tax credit (ITC)', d['bold_text_format'])
    inandout_sheet.write('A130', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A131', 'Federal', d['text_format_indent_2'])
    inandout_sheet.write('A133', 'BATTERY DIRECT CASH INCENTIVES', d['subheader_format'])
    inandout_sheet.write('A134', 'Investment based incentive (IBI)', d['bold_text_format'])
    inandout_sheet.write('A135', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A136', 'State (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A137', 'Utility (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A138', 'Capacity based incentive (CBI)', d['bold_text_format'])
    inandout_sheet.write('A139', 'Total ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A140', 'Total  ($/Wh)', d['text_format_indent_2'])
    inandout_sheet.write('A142', 'CHP TAX CREDITS', d['subheader_format'])
    inandout_sheet.write('A143', 'Investment tax credit (ITC)', d['bold_text_format'])
    inandout_sheet.write('A144', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A145', 'Federal', d['text_format_indent_2'])
    inandout_sheet.write('A147', 'CHP DIRECT CASH INCENTIVES', d['subheader_format'])
    inandout_sheet.write('A148', 'Investment based incentive (IBI)', d['bold_text_format'])
    inandout_sheet.write('A149', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A150', 'State (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A151', 'Utility (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A152', 'Capacity based incentive (CBI)', d['bold_text_format'])
    inandout_sheet.write('A153', 'Federal ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A154', 'State  ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A155', 'Utility  ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A156', 'Production based incentive (PBI)', d['bold_text_format'])
    inandout_sheet.write('A157', 'Combined ($/kWh)', d['text_format_indent_2'])
    inandout_sheet.write('A159', 'GHP TAX CREDITS', d['subheader_format'])
    inandout_sheet.write('A160', 'Investment tax credit (ITC)', d['bold_text_format'])
    inandout_sheet.write('A161', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A162', 'Federal', d['text_format_indent_2'])
    inandout_sheet.write('A164', 'GHP DIRECT CASH INCENTIVES', d['subheader_format'])
    inandout_sheet.write('A165', 'Investment based incentive (IBI)', d['bold_text_format'])
    inandout_sheet.write('A166', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A167', 'State (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A168', 'Utility (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A169', 'Capacity based incentive (CBI)', d['bold_text_format'])
    inandout_sheet.write('A170', 'Federal ($/ton)', d['text_format_indent_2'])
    inandout_sheet.write('A171', 'State  ($/ton)', d['text_format_indent_2'])
    inandout_sheet.write('A172', 'Utility  ($/ton)', d['text_format_indent_2'])
    inandout_sheet.write('A173', 'Production based incentive (PBI)', d['bold_text_format'])
    inandout_sheet.write('A174', 'Combined ($/kWh)', d['text_format_indent_2'])
    inandout_sheet.write('A176', 'DEPRECIATION', d['subheader_format'])
    inandout_sheet.write('A177', 'Federal (years)', d['text_format'])
    inandout_sheet.write('A178', 'Federal bonus fraction', d['text_format'])
    inandout_sheet.write('A181', 'ANNUAL VALUES', d['subheader_format'])
    inandout_sheet.write('A182', 'PV Annual electricity (kWh)', d['text_format'])
    inandout_sheet.write('A183', 'Existing PV Annual electricity (kWh)', d['text_format'])
    inandout_sheet.write('A184', 'Wind Annual electricity (kWh)', d['text_format'])
    inandout_sheet.write('A185', 'Backup Generator Annual electricity (kWh)', d['text_format'])
    inandout_sheet.write('A186', 'CHP Annual electricity (kWh)', d['text_format'])
    inandout_sheet.write('A187', 'CHP Annual heat (MMBtu)', d['text_format'])
    inandout_sheet.write('A188', 'Steam Turbine Annual electricity (kWh)', d['text_format'])
    inandout_sheet.write('A189', 'Steam Turbine Annual heat (MMBtu)', d['text_format'])
    inandout_sheet.write('A190', 'PV Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A191', 'Wind Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A192', 'Battery Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A193', 'CHP Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A194', 'Absorption Chiller Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A195', 'Hot TES Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A196', 'Cold TES Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A197', 'Steam turbine Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A198', 'GHP Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A199', 'Free Cash Flow', d['text_format'])
    inandout_sheet.write('A200', 'Cumulative Free Cash Flow', d['text_format'])

    inandout_sheet.write_blank('B1', None, d['header_format_right'])
    inandout_sheet.write_blank('B2', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B21', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B50', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B83', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B91', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B94', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C94', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D94', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B99', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C99', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D99', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('E99', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B111', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C111', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D111', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B116', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C116', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D116', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('E116', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B128', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C128', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D128', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B133', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C133', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D133', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('E133', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B142', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C142', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D142', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B147', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C147', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D147', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('E147', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B159', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C159', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D159', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B164', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C164', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D164', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('E164', None, d['subheader_format_right'])
    inandout_sheet.write_blank('M176', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('N176', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('O176', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('P176', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('Q176', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('R176', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('S176', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('T176', None, d['subheader_format_right'])
    inandout_sheet.write('D5', 'RESULTS', d['subheader_format'])
    inandout_sheet.write_blank('E5', None, d['subheader_format_right'])
    inandout_sheet.write('D6', 'Business as usual LCC, $', d['text_format'])
    inandout_sheet.write('D7', 'Optimal LCC, $', d['text_format'])
    inandout_sheet.write('D8', 'NPV, $', d['text_format'])
    inandout_sheet.write('D9', 'IRR, %', d['text_format'])
    inandout_sheet.write('D10', 'Simple Payback Period, years', d['text_format'])
    inandout_sheet.write('F7', 'NOTE: A negative LCC indicates a profit (for example when production based incentives are greater than costs.', d['text_format'])
    inandout_sheet.write('F8', 'NOTE: This NPV can differ slightly (<1%) from the Webtool/API results due to rounding and the tolerance in the optimizer.', d['text_format'])
    inandout_sheet.write('B181', '0', d['subheader_format_mid'])
    inandout_sheet.write('C181', '1', d['subheader_format_mid'])
    inandout_sheet.write('D181', '2', d['subheader_format_mid'])
    inandout_sheet.write('E181', '3', d['subheader_format_mid'])
    inandout_sheet.write('F181', '4', d['subheader_format_mid'])
    inandout_sheet.write('G181', '5', d['subheader_format_mid'])
    inandout_sheet.write('H181', '6', d['subheader_format_mid'])
    inandout_sheet.write('I181', '7', d['subheader_format_mid'])
    inandout_sheet.write('J181', '8', d['subheader_format_mid'])
    inandout_sheet.write('K181', '9', d['subheader_format_mid'])
    inandout_sheet.write('L181', '10', d['subheader_format_mid'])
    inandout_sheet.write('M181', '11', d['subheader_format_mid'])
    inandout_sheet.write('N181', '12', d['subheader_format_mid'])
    inandout_sheet.write('O181', '13', d['subheader_format_mid'])
    inandout_sheet.write('P181', '14', d['subheader_format_mid'])
    inandout_sheet.write('Q181', '15', d['subheader_format_mid'])
    inandout_sheet.write('R181', '16', d['subheader_format_mid'])
    inandout_sheet.write('S181', '17', d['subheader_format_mid'])
    inandout_sheet.write('T181', '18', d['subheader_format_mid'])
    inandout_sheet.write('U181', '19', d['subheader_format_mid'])
    inandout_sheet.write('V181', '20', d['subheader_format_mid'])
    inandout_sheet.write('W181', '21', d['subheader_format_mid'])
    inandout_sheet.write('X181', '22', d['subheader_format_mid'])
    inandout_sheet.write('Y181', '23', d['subheader_format_mid'])
    inandout_sheet.write('Z181', '24', d['subheader_format_mid'])
    inandout_sheet.write('AA181', '25', d['subheader_format_right'])

    # set column widths
    inandout_sheet.set_column('A:A', 74)
    inandout_sheet.set_column('B:B', 14.75)
    inandout_sheet.set_column('C:C', 13.25)
    inandout_sheet.set_column('D:D', 23.88)
    inandout_sheet.set_column('E:E', 23.88)
    inandout_sheet.set_column('F:F', 26.88)

    ## Optimal system design (with existing) ## directly parsed fields
    inandout_sheet.write('B3', get_value('outputs','PV','size_kw'), d['text_format_right'])
    inandout_sheet.write('B4', get_value('inputs','PV','existing_kw'), d['text_format_right'])
    inandout_sheet.write('B5', 100*get_value('inputs','PV','degradation_fraction'), d['text_format_right_decimal'])
    inandout_sheet.write('B7', get_value('outputs','Wind','size_kw'), d['text_format_right'])
    inandout_sheet.write('B9', get_value('outputs','Generator','size_kw'), d['text_format_right'])
    inandout_sheet.write('B10', get_value('inputs','Generator','existing_kw'), d['text_format_right'])
    inandout_sheet.write('B11', get_value('outputs','ElectricStorage','size_kw'), d['text_format_right'])
    inandout_sheet.write('B12', get_value('outputs','ElectricStorage','size_kwh'), d['text_format_right'])
    inandout_sheet.write('B13', get_value('outputs','CHP','size_kw'), d['text_format_right'])
    inandout_sheet.write('B14', get_value('outputs','AbsorptionChiller','size_ton'), d['text_format_right'])
    inandout_sheet.write('B15', get_value('outputs','ColdThermalStorage','size_gal'), d['text_format_right'])
    inandout_sheet.write('B16', get_value('outputs','HotThermalStorage','size_gal'), d['text_format_right'])
    inandout_sheet.write('B17', get_value('outputs', 'SteamTurbine', 'size_kw'), d['text_format_right'])
    inandout_sheet.write('B18', get_value('outputs','GHP','size_heat_pump_ton'), d['text_format_right'])

    try:
        heat_exchanger_size = results['outputs']['GHP']['ghpghx_chosen_outputs']['number_of_boreholes']*results['outputs']['GHP']['ghpghx_chosen_outputs']['length_boreholes_ft']
        print(heat_exchanger_size)
    except:
        heat_exchanger_size = 0
    inandout_sheet.write('B19', heat_exchanger_size, d['text_format_right'])

    ## ANNUAL RESULTS directly parsed fields
    inandout_sheet.write('B22', get_value('outputs','ElectricTariff','year_one_bill_before_tax_bau'), d['text_format_right'])
    inandout_sheet.write('B23', get_value('outputs','ElectricTariff','year_one_export_benefit_before_tax_bau'), d['text_format_right'])
    inandout_sheet.write('B24', get_value('outputs','ElectricTariff','year_one_bill_before_tax'), d['text_format_right'])
    inandout_sheet.write('B25', get_value('outputs','ElectricTariff','year_one_export_benefit_before_tax'), d['text_format_right'])
    inandout_sheet.write('B26', get_value('outputs','PV','year_one_energy_produced_kwh_bau'), d['text_format_right'])
    inandout_sheet.write('B27', get_value('outputs','PV','year_one_energy_produced_kwh'), d['text_format_right'])
    inandout_sheet.write('B28', get_value('outputs','PV','annual_energy_produced_kwh'), d['text_format_right'])
    inandout_sheet.write('B29', get_value('outputs','Wind','annual_energy_produced_kwh'), d['text_format_right'])
    inandout_sheet.write('B30', get_value('outputs','Generator','annual_energy_produced_kwh'), d['text_format_right'])
    inandout_sheet.write('B31', get_value('outputs','CHP','annual_electric_production_kwh'), d['text_format_right'])

    runtime_vec = 0.0
    try:
        runtime_vec = [1 for i in (results['outputs']['CHP']['electric_production_series_kw'] or []) if i > 0]
        inandout_sheet.write('B32',
                            sum(runtime_vec)/(results['inputs']['Settings']['time_steps_per_hour'] or 1),
                            d['text_format_right']
        )
    except:
        inandout_sheet.write('B32', runtime_vec, d['text_format_right'])

    inandout_sheet.write('B33', get_value('outputs','SteamTurbine','annual_electric_production_kwh'), d['text_format_right'])
    inandout_sheet.write('B35', get_value('outputs','ExistingBoiler','year_one_fuel_cost_before_tax_bau'), d['text_format_right'])
    inandout_sheet.write('B36', get_value('outputs','ExistingBoiler','year_one_fuel_cost_before_tax'), d['text_format_right'])
    inandout_sheet.write('B37', get_value('outputs','CHP','year_one_fuel_cost_before_tax'), d['text_format_right'])
    inandout_sheet.write('B38', get_value('outputs','CHP','annual_thermal_production_mmbtu'), d['text_format_right'])
    inandout_sheet.write('B39', get_value('outputs','SteamTurbine','annual_thermal_production_mmbtu'), d['text_format_right'])
    inandout_sheet.write('B43', get_value('outputs','Site','annual_emissions_tonnes_CO2'), d['text_format_right'])
    inandout_sheet.write('B44', get_value('outputs','Site','annual_emissions_tonnes_CO2_bau'), d['text_format_right'])
    inandout_sheet.write('B45', get_value('outputs','ElectricUtility','annual_emissions_tonnes_CO2'), d['text_format_right'])
    inandout_sheet.write('B46', get_value('outputs','ElectricUtility','annual_emissions_tonnes_CO2_bau'), d['text_format_right'])
    inandout_sheet.write('B47', get_value('outputs','Site','annual_emissions_from_fuelburn_tonnes_CO2'), d['text_format_right'])
    inandout_sheet.write('B48', get_value('outputs','Site','annual_emissions_from_fuelburn_tonnes_CO2_bau'), d['text_format_right'])

    # SYSTEM COSTS ## static values only
    inandout_sheet.write('B51', get_value('outputs','Financial','initial_capital_costs'), d['text_format_right'])
    inandout_sheet.write('B52', get_value('inputs','PV','installed_cost_per_kw')*(get_value('outputs','PV','size_kw')-get_value('inputs','PV','existing_kw')), d['text_format_right'])

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
                
    inandout_sheet.write('B53', install_cost*get_value('outputs','Wind','size_kw'), d['text_format_right'])
    inandout_sheet.write('B54', get_value('inputs','Generator','installed_cost_per_kw')*(get_value('outputs','Generator','size_kw')-get_value('inputs','Generator','existing_kw')), d['text_format_right'])
    inandout_sheet.write('B55', get_value('inputs','ElectricStorage','installed_cost_per_kwh')*get_value('outputs','ElectricStorage','size_kwh')+get_value('inputs','ElectricStorage','installed_cost_per_kw')*get_value('outputs','ElectricStorage','size_kw'), d['text_format_right'])
    inandout_sheet.write('B56', get_chp_installed_cost_us_dollars(), d['text_format_right'])
    inandout_sheet.write('B57', get_value('inputs','AbsorptionChiller','installed_cost_per_ton')*get_value('outputs','AbsorptionChiller','size_ton'), d['text_format_right'])
    inandout_sheet.write('B58', get_value('inputs','HotThermalStorage','installed_cost_per_gal')*get_value('outputs','HotThermalStorage','size_gal'), d['text_format_right'])
    inandout_sheet.write('B59', get_value('inputs','ColdThermalStorage','installed_cost_per_gal')*get_value('outputs','ColdThermalStorage','size_gal'), d['text_format_right'])
    inandout_sheet.write('B60', get_value('inputs','SteamTurbine','installed_cost_per_kw'), d['text_format_right'])
    inandout_sheet.write('B61', get_value('outputs','GHP','size_heat_pump_ton')*get_value('inputs','GHP','installed_cost_heatpump_per_ton') + heat_exchanger_size*get_value('inputs','GHP','installed_cost_ghx_per_ft') + get_value('inputs','GHP','building_sqft')*get_value('inputs','GHP','installed_cost_building_hydronic_loop_per_sqft'), d['text_format_right'])
    inandout_sheet.write_blank('B62', None, d['text_format_right'])
    inandout_sheet.write('B63', get_value('inputs','PV','om_cost_per_kw'), d['text_format_right'])
    inandout_sheet.write('B64', get_value('inputs','Wind','om_cost_per_kw'), d['text_format_right'])
    inandout_sheet.write('B65', get_value('inputs','Generator','om_cost_per_kw'), d['text_format_right'])
    inandout_sheet.write('B66', get_value('inputs','Generator','om_cost_per_kwh'), d['text_format_right'])
    inandout_sheet.write('B67', get_value('inputs','Generator','fuel_cost_per_gallon')*get_value('outputs','Generator','annual_fuel_consumption_gal'), d['text_format_right'])
    inandout_sheet.write('B68', get_value('inputs','Generator','fuel_cost_per_gallon')*get_value('outputs','Generator','annual_fuel_consumption_gal_bau'), d['text_format_right'])
    inandout_sheet.write('B69', get_value('inputs','ElectricStorage','replace_cost_per_kw'), d['text_format_right'])
    inandout_sheet.write('B70', get_value('inputs','ElectricStorage','inverter_replacement_year'), d['text_format_right'])
    inandout_sheet.write('B71', get_value('inputs','ElectricStorage','replace_cost_per_kwh'), d['text_format_right'])
    inandout_sheet.write('B72', get_value('inputs','ElectricStorage','battery_replacement_year'), d['text_format_right'])
    inandout_sheet.write('B73', get_value('inputs','CHP','om_cost_per_kw'), d['text_format_right_decimal'])
    inandout_sheet.write('B74', get_value('inputs','CHP','om_cost_per_kwh'), d['text_format_right_decimal'])
    inandout_sheet.write('B75', get_value('inputs','CHP','om_cost_per_hr_per_kw_rated'), d['text_format_right_decimal'])
    inandout_sheet.write('B76', get_value('inputs','AbsorptionChiller','om_cost_per_ton'), d['text_format_right'])
    inandout_sheet.write('B77', get_value('inputs','ColdThermalStorage','om_cost_per_gal'), d['text_format_right'])
    inandout_sheet.write('B78', get_value('inputs','HotThermalStorage','om_cost_per_gal'), d['text_format_right'])
    inandout_sheet.write('B79', get_value('inputs','SteamTurbine','om_cost_per_kw'), d['text_format_right'])
    inandout_sheet.write('B80', get_value('inputs','SteamTurbine','om_cost_per_kwh'), d['text_format_right'])
    inandout_sheet.write('B81', get_value('inputs','GHP','building_sqft')*get_value('inputs','GHP','om_cost_per_sqft_year'), d['text_format_right'])

    ## Analysis Parameters
    inandout_sheet.write('B84', get_value('inputs','Financial','analysis_years'), d['text_format_right'])
    inandout_sheet.write('B85', 100*get_value('inputs','Financial','om_cost_escalation_rate_fraction'), d['text_format_right_decimal'])
    inandout_sheet.write('B86', 100*get_value('inputs','Financial','elec_cost_escalation_rate_fraction'), d['text_format_right_decimal'])
    inandout_sheet.write('B87', 100*get_value('inputs','Financial','boiler_fuel_cost_escalation_rate_fraction'), d['text_format_right_decimal'])
    inandout_sheet.write('B88', 100*get_value('inputs','Financial','chp_fuel_cost_escalation_rate_fraction'), d['text_format_right_decimal'])

    # ## Add exrta rows in the formatting table.
    # if results['inputs']['Financial']['third_party_ownership']:
    #     inandout_sheet.write('A89', 'Nominal third-party discount rate (%/year)', d['text_format_right_decimal'])
    #     inandout_sheet.write('A90', 'Nominal Host discount rate (%/year)', d['text_format_right_decimal'])
    #     inandout_sheet.write('B89', 100*get_value('inputs','Financial','owner_discount_rate_fraction'), d['text_format_right_decimal'])
    #     inandout_sheet.write('B90', 100*get_value('inputs','Financial','offtaker_discount_rate_fraction'), d['text_format_right_decimal'])
    #     # Tax and insurance parameters
    #     inandout_sheet.write('A92', 'Third-party owner Federal income tax rate (%)', d['text_format_right_decimal'])
    #     inandout_sheet.write('A93', 'Host Federal income tax rate (%)', d['text_format_right_decimal'])
    #     inandout_sheet.write('B92', 100*get_value('inputs','Financial','owner_tax_rate_fraction'), d['text_format_right_decimal'])
    #     inandout_sheet.write('B93', 100*get_value('inputs','Financial','offtaker_tax_rate_fraction'), d['text_format_right_decimal'])

    inandout_sheet.write('B89', 100*get_value('inputs','Financial','offtaker_discount_rate_fraction'), d['text_format_right_decimal'])
    inandout_sheet.write('B90', 100*get_value('inputs','Financial','offtaker_discount_rate_fraction'), d['text_format_right_decimal'])
    # Tax and insurance parameters
    inandout_sheet.write('B92', 100*get_value('inputs','Financial','offtaker_tax_rate_fraction'), d['text_format_right_decimal'])

    ## PV Tax credits section
    bases = [95, 112, 129, 143, 160]
    techs = ['PV', 'Wind', 'Battery', 'CHP', 'GHP']

    for b,t in zip(bases, techs):

        inandout_sheet.write('D'+str(b), 'Reduces depreciation', d['text_format'])
        inandout_sheet.write('B'+str(b+1), '%', d['text_format_right_center_align'])
        inandout_sheet.write('C'+str(b+1), 'Maximum', d['text_format_right_center_align'])
        inandout_sheet.write('D'+str(b+1), 'Federal', d['text_format_right_center_align'])
        inandout_sheet.write('D'+str(b+5), 'Incentive is taxable', d['text_format_right_center_align'])
        inandout_sheet.write('E'+str(b+5), 'Reduces depreciation and ITC basis', d['text_format_right_center_align'])
        inandout_sheet.write('B'+str(b+6), '%', d['text_format'])
        inandout_sheet.write('C'+str(b+6), 'Maximum ($)', d['text_format'])
        inandout_sheet.write('D'+str(b+6), 'Federal', d['text_format'])
        inandout_sheet.write('E'+str(b+6), 'Federal', d['text_format'])
        inandout_sheet.write('B'+str(b+9), 'Amount ($/W)', d['text_format'])
        inandout_sheet.write('C'+str(b+9), 'Maximum ($)', d['text_format'])

        if t != 'Battery':
            inandout_sheet.write('B'+str(b+13), 'Amount ($/kWh)', d['text_format_right_center_align'])
            inandout_sheet.write('C'+str(b+13), 'Maximum ($/year)', d['text_format_right_center_align'])
            inandout_sheet.write('D'+str(b+13), 'Federal taxable', d['text_format_right_center_align'])
            inandout_sheet.write('E'+str(b+13), 'Term (years)', d['text_format_right_center_align'])
            inandout_sheet.write('F'+str(b+13), 'System size limit (kW)', d['text_format_right_center_align'])
        else:
            pass

    ## Depreciation and MACRS schedules
    techs = ['PV', 'BATTERY', 'WIND', 'CHP', 'Absorption Chiller', 'Hot TES', 'Cold TES', 'SteamTurbine', 'GHP']
    tech_key = ['PV', 'ElectricStorage', 'Wind', 'CHP', 'AbsorptionChiller', 'HotThermalStorage', 'ColdThermalStorage', 'SteamTurbine', 'GHP']
    cols = ['B','C','D','E','F','G','H','I','J']

    for (i,j,k) in zip(techs, tech_key, cols):
        inandout_sheet.write(k+'176', i, d['subheader_format_mid'])
        inandout_sheet.write(k+'177', get_value('inputs', j, 'macrs_option_years'), d['text_format'])
        inandout_sheet.write(k+'178', get_value('inputs', j, 'macrs_bonus_fraction'), d['text_format'])

    inandout_sheet.write('L176', 'MACRS SCHEDULES (INFORMATIONAL ONLY)', d['subheader_format'])
    inandout_sheet.write('L177', 'Year', d['standalone_bold_text_format'])
    inandout_sheet.write('L178', '5-Year', d['standalone_bold_text_format'])
    inandout_sheet.write('L179', '7-Year', d['standalone_bold_text_format'])
    inandout_sheet.write('M177', 1, d['text_format'])
    inandout_sheet.write('N177', 2, d['text_format'])
    inandout_sheet.write('O177', 3, d['text_format'])
    inandout_sheet.write('P177', 4, d['text_format'])
    inandout_sheet.write('Q177', 5, d['text_format'])
    inandout_sheet.write('R177', 6, d['text_format'])
    inandout_sheet.write('S177', 7, d['text_format_right_center_align'])
    inandout_sheet.write('T177', 8, d['text_format_right_center_align'])
    inandout_sheet.write('M178', 0.2, d['text_format'])
    inandout_sheet.write('N178', 0.32, d['text_format'])
    inandout_sheet.write('O178', 0.192, d['text_format'])
    inandout_sheet.write('P178', 0.1152, d['text_format'])
    inandout_sheet.write('Q178', 0.1152, d['text_format'])
    inandout_sheet.write('R178', 0.0576, d['text_format'])
    inandout_sheet.write_blank('S178', None, d['text_format_right_center_align'])
    inandout_sheet.write_blank('T178', None, d['text_format_right_center_align'])
    inandout_sheet.write('M179', 0.1429, d['text_format'])
    inandout_sheet.write('N179', 0.2449, d['text_format'])
    inandout_sheet.write('O179', 0.1749, d['text_format'])
    inandout_sheet.write('P179', 0.1249, d['text_format'])
    inandout_sheet.write('Q179', 0.0893, d['text_format'])
    inandout_sheet.write('R179', 0.0892, d['text_format'])
    inandout_sheet.write('S179', 0.0893, d['text_format_right_center_align'])
    inandout_sheet.write('T179', 0.0446, d['text_format_right_center_align'])

    ## Annual values
    for idx in range(182,199):
        inandout_sheet.write('B'+str(idx), 0, d['year_0_format'])

    for idx in range(2,27):
        inandout_sheet.write(base_upper_case_letters[idx]+'181', idx-1, d['subheader_format_mid'])

    ## PV Tax credits section
    bases = [95, 112, 129, 143, 160]
    techs = ['PV', 'Wind', 'ElectricStorage', 'CHP', 'GHP']

    for b,t in zip(bases, techs):

        if t not in ['ElectricStorage']:
            inandout_sheet.write('B'+str(b+2), 100*get_value('inputs',t,'federal_itc_fraction'), d['text_format']) # confirm formatting
        else:
            inandout_sheet.write('B'+str(b+2), 100*get_value('inputs',t,'total_itc_fraction'), d['text_format']) # confirm formatting
        inandout_sheet.write_number('C'+str(b+2), 1.0e10, d['scientific_text'])
        inandout_sheet.write('D'+str(b+2), 'Yes', d['text_format_right_center_align'])
        
        inandout_sheet.write('B'+str(b+7), get_value('inputs',t,'state_ibi_fraction'), d['text_format'])
        inandout_sheet.write('B'+str(b+8), get_value('inputs',t,'utility_ibi_fraction'), d['text_format'])
        
        inandout_sheet.write('C'+str(b+7), get_value('inputs',t,'state_ibi_max'), d['scientific_text'])
        inandout_sheet.write('C'+str(b+8), get_value('inputs',t,'utility_ibi_max'), d['scientific_text'])

        inandout_sheet.write('D'+str(b+7), 'No', d['text_format'])
        inandout_sheet.write('D'+str(b+8), 'No', d['text_format_right'])
        inandout_sheet.write('E'+str(b+7), 'Yes', d['text_format'])
        inandout_sheet.write('E'+str(b+8), 'Yes', d['text_format_right'])
        
        inandout_sheet.write_blank('D'+str(b+9), None, d['text_format_right'])
        inandout_sheet.write_blank('E'+str(b+9), None, d['text_format_right'])

        if t != 'ElectricStorage':
            inandout_sheet.write_number('B'+str(b+10), get_value('inputs',t,'federal_rebate_per_kw'), d['text_format'])
            inandout_sheet.write_number('B'+str(b+11), get_value('inputs',t,'state_rebate_per_kw'), d['text_format'])
            inandout_sheet.write_number('B'+str(b+12), get_value('inputs',t,'utility_rebate_per_kw'), d['text_format'])
            inandout_sheet.write_number('C'+str(b+10), 1.0e10, d['scientific_text'])
            inandout_sheet.write_number('C'+str(b+11), 1.0e10, d['scientific_text'])
            inandout_sheet.write_number('C'+str(b+12), 1.0e10, d['scientific_text'])
            inandout_sheet.write('D'+str(b+10), 'No', d['text_format_right'])
            inandout_sheet.write('D'+str(b+11), 'No', d['text_format_right'])
            inandout_sheet.write('D'+str(b+12), 'No', d['text_format_right'])
            inandout_sheet.write('E'+str(b+10), 'No', d['text_format_right'])
            inandout_sheet.write('E'+str(b+11), 'Yes', d['text_format_right'])
            inandout_sheet.write('E'+str(b+12), 'Yes', d['text_format_right'])
            inandout_sheet.write('B'+str(b+14), get_value('inputs',t,'production_incentive_per_kwh'), d['text_format'])
            inandout_sheet.write('C'+str(b+14), get_value('inputs',t,'production_incentive_max_benefit'), d['scientific_text'])
            inandout_sheet.write('D'+str(b+14), 'Yes', d['text_format_right_center_align'])
            inandout_sheet.write('E'+str(b+14), get_value('inputs',t,'production_incentive_years'), d['text_format_right_center_align'])
            inandout_sheet.write('F'+str(b+14), get_value('inputs',t,'production_incentive_max_kw'), d['scientific_text'])

    ## ANNUAL RESULTS FORMULAS
    inandout_sheet.write_formula('B34','=SUM(B27,B29,B31,B33)-B26',d['text_format_right'])
    inandout_sheet.write_formula('B40', '=ROUND((\'Inputs and Outputs\'!B29 + SUM(\'Inputs and Outputs\'!B28))/'+str(get_value('outputs','ElectricLoad','annual_calculated_kwh'))+',3)',d['text_format_right_percentage'])
    inandout_sheet.write_formula('B41','=IF(B22=0,"N/A",ROUND((B22 - B24)/B22,2))',d['text_format_right_percentage'])
    inandout_sheet.write_formula('B42','=IF(B35=0,"N/A",ROUND((B35 - SUM(B36, B37))/B35,2))',d['text_format_right_percentage'])

    # ANNUAL VALUES Formulas
    for idx in range(2,27):
        inandout_sheet.write(base_upper_case_letters[idx]+'182', '=B27*(1 - (B5/100))^'+str(idx-2), d['proj_fin_format'])
        inandout_sheet.write(base_upper_case_letters[idx]+'183', '=B26*(1 - (B5/100))^'+str(idx-2), d['proj_fin_format'])
        inandout_sheet.write(base_upper_case_letters[idx]+'184', '=B29', d['proj_fin_format'])
        inandout_sheet.write(base_upper_case_letters[idx]+'185', '=B30', d['proj_fin_format'])
        inandout_sheet.write(base_upper_case_letters[idx]+'186', '=B31', d['proj_fin_format'])
        inandout_sheet.write(base_upper_case_letters[idx]+'187', '=B38', d['proj_fin_format'])
        # inandout_sheet.ignore_errors({'inconsistent_formula': base_upper_case_letters[idx]+'187'}) # how to turn off this warning?
        inandout_sheet.write(base_upper_case_letters[idx]+'188', '=B33', d['proj_fin_format'])
        inandout_sheet.write(base_upper_case_letters[idx]+'189', '=B39', d['proj_fin_format'])

    for cidx in range(2,27):
        for ridx in range(190, 199):
            inandout_sheet.write(base_upper_case_letters[cidx]+str(ridx), 0.0, d['proj_fin_format_decimal'])

    ## MACRS depreciation fraction over the years
    bases = [190, 191, 192, 193, 194, 195, 196, 197, 198]
    techs = ['PV', 'Wind', 'ElectricStorage', 'CHP', 'AbsorptionChiller', 'HotThermalStorage', 'ColdThermalStorage', 'SteamTurbine', 'GHP']

    for b,t in zip(bases, techs):
        if get_value('inputs',t,'macrs_option_years') == 7:
            inandout_sheet.write_formula('C'+str(b),'=M179',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('D'+str(b),'=N179',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('E'+str(b),'=O179',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('F'+str(b),'=P179',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('G'+str(b),'=Q179',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('H'+str(b),'=R179',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('I'+str(b),'=S179',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('J'+str(b),'=T179',d['proj_fin_format_decimal'])
        elif get_value('inputs',t,'macrs_option_years') == 5:
            inandout_sheet.write_formula('C'+str(b),'=M178',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('D'+str(b),'=N178',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('E'+str(b),'=O178',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('F'+str(b),'=P178',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('G'+str(b),'=Q178',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('H'+str(b),'=R178',d['proj_fin_format_decimal'])
        else:
            pass

    ### OPTIMAL SHEET
    optcashf_sheet = proforma.add_worksheet('Optimal Cash Flow')

    optcashf_sheet.write('A1', 'Optimal Cash Flow', o['header_format'])
    optcashf_sheet.write('A2', 'Operating Year', o['year_format'])
    optcashf_sheet.write('A4', 'Operating Expenses', o['subheader_format'])
    optcashf_sheet.write('A5', 'Electricity bill with system before export credits', o['text_format'])
    optcashf_sheet.write('A6', 'Export credits with system', o['text_format'])
    optcashf_sheet.write('A7', 'Boiler fuel bill with system', o['text_format'])
    optcashf_sheet.write('A8', 'CHP fuel bill', o['text_format'])
    optcashf_sheet.write('A9', 'Operation and Maintenance (O&M)', o['text_format'])
    optcashf_sheet.write('A10', 'New PV fixed O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A11', 'Existing PV fixed O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A12', 'Wind fixed O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A13', 'Generator fixed O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A14', 'Generator variable O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A15', 'Generator diesel fuel cost ($)', o['text_format_indent'])
    optcashf_sheet.write('A16', 'Battery kW replacement cost ', o['text_format_indent'])
    optcashf_sheet.write('A17', 'Battery kWh replacement cost ', o['text_format_indent'])
    optcashf_sheet.write('A18', 'CHP fixed O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A19', 'CHP variable generation O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A20', 'CHP runtime O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A21', 'Absorption Chiller fixed O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A22', 'Chilled water TES fixed O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A23', 'Hot water TES fixed O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A24', 'Steam turbine fixed O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A25', 'Steam turbine variable generation O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A26', 'GHP fixed O&M cost', o['text_format_indent'])
    optcashf_sheet.write('A27', 'Total operating expenses', o['text_format_2'])
    optcashf_sheet.write('A28', 'Tax deductible operating expenses', o['text_format_2'])
    optcashf_sheet.write('A30', 'Direct Cash Incentives', o['subheader_format'])
    optcashf_sheet.write('A31', 'PV Investment-based incentives (IBI)', o['text_format'])
    optcashf_sheet.write('A32', 'State IBI', o['text_format_indent'])
    optcashf_sheet.write('A33', 'Utility IBI', o['text_format_indent'])
    optcashf_sheet.write('A34', 'Total', o['text_format_indent'])
    optcashf_sheet.write('A35', 'PV Capacity-based incentives (CBI)', o['text_format'])
    optcashf_sheet.write('A36', 'Federal CBI', o['text_format_indent'])
    optcashf_sheet.write('A37', 'State CBI', o['text_format_indent'])
    optcashf_sheet.write('A38', 'Utility CBI', o['text_format_indent'])
    optcashf_sheet.write('A39', 'Total', o['text_format_indent'])
    optcashf_sheet.write('A40', 'Wind Investment-based incentives (IBI)', o['text_format'])
    optcashf_sheet.write('A41', 'State IBI', o['text_format_indent'])
    optcashf_sheet.write('A42', 'Utility IBI', o['text_format_indent'])
    optcashf_sheet.write('A43', 'Total', o['text_format_indent'])
    optcashf_sheet.write('A44', 'Wind Capacity-based incentives (CBI)', o['text_format'])
    optcashf_sheet.write('A45', 'Federal CBI', o['text_format_indent'])
    optcashf_sheet.write('A46', 'State CBI', o['text_format_indent'])
    optcashf_sheet.write('A47', 'Utility CBI', o['text_format_indent'])
    optcashf_sheet.write('A48', 'Total', o['text_format_indent'])
    optcashf_sheet.write('A49', 'Battery Investment-based incentives (IBI)', o['text_format'])
    optcashf_sheet.write('A50', 'State IBI', o['text_format_indent'])
    optcashf_sheet.write('A51', 'Utility IBI', o['text_format_indent'])
    optcashf_sheet.write('A52', 'Total', o['text_format_indent'])
    optcashf_sheet.write('A53', 'Battery Capacity-based incentives (CBI)', o['text_format'])
    optcashf_sheet.write('A54', 'Total Power (per kW) CBI', o['text_format_indent'])
    optcashf_sheet.write('A55', 'Total Storage Capacity (per kWh) CBI', o['text_format_indent'])
    optcashf_sheet.write('A56', 'Total', o['text_format_indent'])
    optcashf_sheet.write('A57', 'CHP Investment-based incentives (IBI)', o['text_format'])
    optcashf_sheet.write('A58', 'State IBI', o['text_format_indent'])
    optcashf_sheet.write('A59', 'Utility IBI', o['text_format_indent'])
    optcashf_sheet.write('A60', 'Total', o['text_format_indent'])
    optcashf_sheet.write('A61', 'CHP Capacity-based incentives (CBI)', o['text_format'])
    optcashf_sheet.write('A62', 'Federal CBI', o['text_format_indent'])
    optcashf_sheet.write('A63', 'State CBI', o['text_format_indent'])
    optcashf_sheet.write('A64', 'Utility CBI', o['text_format_indent'])
    optcashf_sheet.write('A65', 'Total', o['text_format_indent'])
    optcashf_sheet.write('A67', 'Total CBI and IBI', o['text_format'])
    optcashf_sheet.write('A69', 'GHP Investment-based incentives (IBI)', o['text_format'])
    optcashf_sheet.write('A70', 'State IBI', o['text_format_indent'])
    optcashf_sheet.write('A71', 'Utility IBI', o['text_format_indent'])
    optcashf_sheet.write('A72', 'Total', o['text_format_indent'])
    optcashf_sheet.write('A73', 'GHP Capacity-based incentives (CBI)', o['text_format'])
    optcashf_sheet.write('A74', 'Federal CBI', o['text_format_indent'])
    optcashf_sheet.write('A75', 'State CBI', o['text_format_indent'])
    optcashf_sheet.write('A76', 'Utility CBI', o['text_format_indent'])
    optcashf_sheet.write('A77', 'Total', o['text_format_indent'])
    optcashf_sheet.write('A79', 'Total CBI and IBI', o['text_format'])
    optcashf_sheet.write('A81', 'Production-based incentives (PBI)', o['text_format'])
    optcashf_sheet.write('A82', 'New PV Combined PBI', o['text_format_indent'])
    optcashf_sheet.write('A83', 'Existing PV Combined PBI', o['text_format_indent'])
    optcashf_sheet.write('A84', 'Wind Combined PBI', o['text_format_indent'])
    optcashf_sheet.write('A85', 'CHP Combined PBI', o['text_format_indent'])
    optcashf_sheet.write('A86', 'Total taxable cash incentives', o['text_format_2'])
    optcashf_sheet.write('A87', 'Total non-taxable cash incentives', o['text_format_2'])
    optcashf_sheet.write('A89', 'Capital Depreciation', o['subheader_format'])
    optcashf_sheet.write('A90', 'PV Depreciation, Commercial only', o['text_format'])
    optcashf_sheet.write('A91', 'Percentage', o['text_format_indent'])
    optcashf_sheet.write('A92', 'Bonus Basis', o['text_format_indent'])
    optcashf_sheet.write('A93', 'Basis', o['text_format_indent'])
    optcashf_sheet.write('A94', 'Amount', o['text_format_indent'])
    optcashf_sheet.write('A95', 'Wind Depreciation, Commercial only', o['text_format'])
    optcashf_sheet.write('A96', 'Percentage', o['text_format_indent'])
    optcashf_sheet.write('A97', 'Bonus Basis', o['text_format_indent'])
    optcashf_sheet.write('A98', 'Basis', o['text_format_indent'])
    optcashf_sheet.write('A99', 'Amount', o['text_format_indent'])
    optcashf_sheet.write('A100', 'Battery Depreciation, Commercial only', o['text_format'])
    optcashf_sheet.write('A101', 'Percentage', o['text_format_indent'])
    optcashf_sheet.write('A102', 'Bonus Basis', o['text_format_indent'])
    optcashf_sheet.write('A103', 'Basis', o['text_format_indent'])
    optcashf_sheet.write('A104', 'Amount', o['text_format_indent'])
    optcashf_sheet.write('A105', 'CHP Depreciation, Commercial only', o['text_format'])
    optcashf_sheet.write('A106', 'Percentage', o['text_format_indent'])
    optcashf_sheet.write('A107', 'Bonus Basis', o['text_format_indent'])
    optcashf_sheet.write('A108', 'Basis', o['text_format_indent'])
    optcashf_sheet.write('A109', 'Amount', o['text_format_indent'])
    optcashf_sheet.write('A110', 'Absorption Chiller Depreciation, Commercial only', o['text_format'])
    optcashf_sheet.write('A111', 'Percentage', o['text_format_indent'])
    optcashf_sheet.write('A112', 'Bonus Basis', o['text_format_indent'])
    optcashf_sheet.write('A113', 'Basis', o['text_format_indent'])
    optcashf_sheet.write('A114', 'Amount', o['text_format_indent'])
    optcashf_sheet.write('A115', 'Hot TES Depreciation, Commercial only', o['text_format'])
    optcashf_sheet.write('A116', 'Percentage', o['text_format_indent'])
    optcashf_sheet.write('A117', 'Bonus Basis', o['text_format_indent'])
    optcashf_sheet.write('A118', 'Basis', o['text_format_indent'])
    optcashf_sheet.write('A119', 'Amount', o['text_format_indent'])
    optcashf_sheet.write('A120', 'Cold TES Depreciation, Commercial only', o['text_format'])
    optcashf_sheet.write('A121', 'Percentage', o['text_format_indent'])
    optcashf_sheet.write('A122', 'Bonus Basis', o['text_format_indent'])
    optcashf_sheet.write('A123', 'Basis', o['text_format_indent'])
    optcashf_sheet.write('A124', 'Amount', o['text_format_indent'])
    optcashf_sheet.write('A125', 'Steam Turbine Depreciation, Commercial only', o['text_format'])
    optcashf_sheet.write('A126', 'Percentage', o['text_format_indent'])
    optcashf_sheet.write('A127', 'Bonus Basis', o['text_format_indent'])
    optcashf_sheet.write('A128', 'Basis', o['text_format_indent'])
    optcashf_sheet.write('A129', 'Amount', o['text_format_indent'])
    optcashf_sheet.write('A130', 'GHP Depreciation, Commercial only', o['text_format'])
    optcashf_sheet.write('A131', 'Percentage', o['text_format_indent'])
    optcashf_sheet.write('A132', 'Bonus Basis', o['text_format_indent'])
    optcashf_sheet.write('A133', 'Basis', o['text_format_indent'])
    optcashf_sheet.write('A134', 'Amount', o['text_format_indent'])
    optcashf_sheet.write('A135', 'Total depreciation', o['text_format_2'])
    optcashf_sheet.write('A137', 'Tax benefits for LCOE Calculations', o['subheader_format'])
    optcashf_sheet.write('A138', 'PV income tax savings, $', o['text_format_2'])
    optcashf_sheet.write('A139', 'Wind income tax savings, $', o['text_format_2'])
    optcashf_sheet.write('A141', 'Federal Investment Tax Credit', o['subheader_format'])
    optcashf_sheet.write('A142', 'Federal ITC basis: PV', o['text_format'])
    optcashf_sheet.write('A143', 'Federal ITC amount: PV', o['text_format'])
    optcashf_sheet.write('A144', 'Federal ITC basis: Wind', o['text_format'])
    optcashf_sheet.write('A145', 'Federal ITC amount: Wind', o['text_format'])
    optcashf_sheet.write('A146', 'Federal ITC basis: Battery', o['text_format'])
    optcashf_sheet.write('A147', 'Federal ITC amount: Battery', o['text_format'])
    optcashf_sheet.write('A148', 'Federal ITC basis: CHP', o['text_format'])
    optcashf_sheet.write('A149', 'Federal ITC amount: CHP', o['text_format'])
    optcashf_sheet.write('A150', 'Federal ITC basis: GHP', o['text_format'])
    optcashf_sheet.write('A151', 'Federal ITC amount: GHP', o['text_format'])
    optcashf_sheet.write('A152', 'Total Federal ITC', o['text_format_2'])
    optcashf_sheet.write('A154', 'Total Cash Flows', o['subheader_format'])
    optcashf_sheet.write('A155', 'Upfront Capital Cost', o['text_format'])
    optcashf_sheet.write('A156', 'Operating expenses, after-tax', o['text_format'])
    optcashf_sheet.write('A157', 'Total Cash incentives, after-tax', o['text_format'])
    optcashf_sheet.write('A158', 'Depreciation Tax Shield', o['text_format'])
    optcashf_sheet.write('A159', 'Investment Tax Credit', o['text_format'])
    optcashf_sheet.write('A160', 'Free Cash Flow before income', o['text_format_2'])
    optcashf_sheet.write('A161', 'Discounted Cash Flow', o['text_format_2'])
    optcashf_sheet.write('A162', 'Optimal Life Cycle Cost', o['standalone_bold_text_format'])

    # column widths
    optcashf_sheet.set_column('A:A', 31.75)
    optcashf_sheet.set_column('B:AA', 10.38)
    optcashf_sheet.freeze_panes(2,0)

    # Static fields
    for idx in range(1,27):
        optcashf_sheet.write(base_upper_case_letters[idx]+'2', idx-1, o['year_format'])
        optcashf_sheet.write_blank(base_upper_case_letters[idx]+'4', None, o['subheader_format'])
        optcashf_sheet.write_blank(base_upper_case_letters[idx]+'30', None, o['subheader_format'])
        optcashf_sheet.write_blank(base_upper_case_letters[idx]+'89', None, o['subheader_format'])
        optcashf_sheet.write_blank(base_upper_case_letters[idx]+'137', None, o['subheader_format'])
        optcashf_sheet.write_blank(base_upper_case_letters[idx]+'141', None, o['subheader_format'])
        optcashf_sheet.write_blank(base_upper_case_letters[idx]+'154', None, o['subheader_format'])
        optcashf_sheet.write_blank(base_upper_case_letters[idx]+'152', None, o['text_format_2'])

    # operating expenses
    optcashf_sheet.write_dynamic_array_formula('C5:AA5', '=-\'Inputs and Outputs\'!B24 * (1 + \'Inputs and Outputs\'!B86/100)^C2:AA2', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C6:AA6', '=\'Inputs and Outputs\'!B25 * (1 + \'Inputs and Outputs\'!B86/100)^C2:AA2', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C7:AA7', '=(-1*(\'Inputs and Outputs\'!B36 * (1 + \'Inputs and Outputs\'!B87/100)^C2:AA2))', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C8:AA8', '=(-1*(\'Inputs and Outputs\'!B37 * (1 + \'Inputs and Outputs\'!B88/100)^C2:AA2))', o['text_format'])
        
    optcashf_sheet.write_dynamic_array_formula('C10:AA10', '=-\'Inputs and Outputs\'!B63 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2 * (\'Inputs and Outputs\'!B3 - \'Inputs and Outputs\'!B4)', o['text_format'])

    optcashf_sheet.write_dynamic_array_formula('C11:AA11', '=-\'Inputs and Outputs\'!B63 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2 * (\'Inputs and Outputs\'!B4)', o['text_format'])
        
    optcashf_sheet.write_dynamic_array_formula('C12:AA12', '=-\'Inputs and Outputs\'!B64 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2 * (\'Inputs and Outputs\'!B7)', o['text_format'])

    optcashf_sheet.write_dynamic_array_formula('C13:AA13', '=-\'Inputs and Outputs\'!B65 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2 * (\'Inputs and Outputs\'!B9 + \'Inputs and Outputs\'!B10)', o['text_format'])

    optcashf_sheet.write_dynamic_array_formula('C14:AA14', '=-\'Inputs and Outputs\'!B66 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2 * (\'Inputs and Outputs\'!B30)', o['text_format'])

    optcashf_sheet.write_dynamic_array_formula('C15:AA15', '=-\'Inputs and Outputs\'!B67 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])

    optcashf_sheet.write_dynamic_array_formula('C16:AA16', '=-IF(C2:AA2 = \'Inputs and Outputs\'!B70, \'Inputs and Outputs\'!B11 * \'Inputs and Outputs\'!B69, 0)', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C17:AA17', '=-IF(C2:AA2 = \'Inputs and Outputs\'!B70, \'Inputs and Outputs\'!B12 * \'Inputs and Outputs\'!B71, 0)', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C18:AA18', '=-\'Inputs and Outputs\'!B73 * \'Inputs and Outputs\'!B13 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C19:AA19', '=-\'Inputs and Outputs\'!B74 * \'Inputs and Outputs\'!B31 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C20:AA20', '=-\'Inputs and Outputs\'!B75 * \'Inputs and Outputs\'!B13 * \'Inputs and Outputs\'!B32 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C21:AA21', '=-\'Inputs and Outputs\'!B76 * \'Inputs and Outputs\'!B14 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C22:AA22', '=-\'Inputs and Outputs\'!B77 * \'Inputs and Outputs\'!B15 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C23:AA23', '=-\'Inputs and Outputs\'!B78 * \'Inputs and Outputs\'!B16 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C24:AA24', '=-\'Inputs and Outputs\'!B79 * \'Inputs and Outputs\'!B17 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C25:AA25', '=-\'Inputs and Outputs\'!B80 * \'Inputs and Outputs\'!B33 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C26:AA26', '=-\'Inputs and Outputs\'!B81 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])

    for idx in range(2, 27):
        col = base_upper_case_letters[idx] # C through AA
        optcashf_sheet.write_formula(col+'27', '=SUM('+col+'5:'+col+'26)', o['text_format_2'])
        optcashf_sheet.write_formula(col+'28', '=IF(\'Inputs and Outputs\'!B92 > 0, '+col+'27, 0)', o['text_format_2'])

    # direct cash incentives

    optcashf_sheet.write_formula('B32', '=MIN((\'Inputs and Outputs\'!B102/100)*(\'Inputs and Outputs\'!B52-B33-B38),\'Inputs and Outputs\'!C102)', o['text_format'])
    optcashf_sheet.write_formula('B33', '=MIN((\'Inputs and Outputs\'!B103/100)*\'Inputs and Outputs\'!B52,\'Inputs and Outputs\'!C103)', o['text_format'])
    optcashf_sheet.write_formula('B34', '=SUM(B32,B33)', o['text_format'])
    optcashf_sheet.write_blank('B35', None, o['text_format'])
    optcashf_sheet.write_formula('B36', '=MIN(\'Inputs and Outputs\'!B105*\'Inputs and Outputs\'!B3*1000,\'Inputs and Outputs\'!C105)', o['text_format'])
    optcashf_sheet.write_formula('B37', '=MIN(\'Inputs and Outputs\'!B106*\'Inputs and Outputs\'!B3*1000,\'Inputs and Outputs\'!C106)', o['text_format'])
    optcashf_sheet.write_formula('B38', '=MIN(\'Inputs and Outputs\'!B107*\'Inputs and Outputs\'!B3*1000,\'Inputs and Outputs\'!C107)', o['text_format'])
    optcashf_sheet.write_formula('B39', '=SUM(B36,B37,B38)', o['text_format'])
    optcashf_sheet.write_blank('B40', None, o['text_format'])

    optcashf_sheet.write_formula('B41', '=MIN((\'Inputs and Outputs\'!B119/100)*(\'Inputs and Outputs\'!B53-B42-B47),\'Inputs and Outputs\'!C119)', o['text_format'])
    optcashf_sheet.write_formula('B42', '=MIN((\'Inputs and Outputs\'!B120/100)*\'Inputs and Outputs\'!B53,\'Inputs and Outputs\'!C120)', o['text_format'])
    optcashf_sheet.write_formula('B43', '=SUM(B41,B42)', o['text_format'])
    optcashf_sheet.write_blank('B44', None, o['text_format'])
    optcashf_sheet.write_formula('B45', '=MIN(\'Inputs and Outputs\'!B122*\'Inputs and Outputs\'!B7*1000,\'Inputs and Outputs\'!C122)', o['text_format'])
    optcashf_sheet.write_formula('B46', '=MIN(\'Inputs and Outputs\'!B123*\'Inputs and Outputs\'!B7*1000,\'Inputs and Outputs\'!C123)', o['text_format'])
    optcashf_sheet.write_formula('B47', '=MIN(\'Inputs and Outputs\'!B124*\'Inputs and Outputs\'!B7*1000,\'Inputs and Outputs\'!C124)', o['text_format'])
    optcashf_sheet.write_formula('B48', '=SUM(B45,B46,B47)', o['text_format'])
    optcashf_sheet.write_blank('B49', None, o['text_format'])

    optcashf_sheet.write_formula('B50', '=MIN((\'Inputs and Outputs\'!B136/100)*(\'Inputs and Outputs\'!B55),\'Inputs and Outputs\'!C136)', o['text_format'])
    optcashf_sheet.write_formula('B51', '=MIN((\'Inputs and Outputs\'!B137/100)*\'Inputs and Outputs\'!B55,\'Inputs and Outputs\'!C137)', o['text_format'])
    optcashf_sheet.write_formula('B52', '=SUM(B50,B51)', o['text_format'])
    optcashf_sheet.write_blank('B53', None, o['text_format'])
    optcashf_sheet.write_formula('B54', '=MIN(\'Inputs and Outputs\'!B139*\'Inputs and Outputs\'!B11*1000,\'Inputs and Outputs\'!C139)', o['text_format'])
    optcashf_sheet.write_formula('B55', '=MIN(\'Inputs and Outputs\'!B140*\'Inputs and Outputs\'!B12*1000,\'Inputs and Outputs\'!C140)', o['text_format'])
    optcashf_sheet.write_formula('B56', '=SUM(B54,B55)', o['text_format'])
    optcashf_sheet.write_blank('B57', None, o['text_format'])

    optcashf_sheet.write_formula('B58', '=MIN((\'Inputs and Outputs\'!B150/100)*(\'Inputs and Outputs\'!B56-B59-B64),\'Inputs and Outputs\'!C150)', o['text_format'])
    optcashf_sheet.write_formula('B59', '=MIN((\'Inputs and Outputs\'!B151/100)*\'Inputs and Outputs\'!B56,\'Inputs and Outputs\'!C151)', o['text_format'])
    optcashf_sheet.write_formula('B60', '=SUM(B58,B59)', o['text_format'])
    optcashf_sheet.write_blank('B61', None, o['text_format'])
    optcashf_sheet.write_formula('B62', '=MIN(\'Inputs and Outputs\'!B153*\'Inputs and Outputs\'!B13*1000,\'Inputs and Outputs\'!C153)', o['text_format'])
    optcashf_sheet.write_formula('B63', '=MIN(\'Inputs and Outputs\'!B154*\'Inputs and Outputs\'!B13*1000,\'Inputs and Outputs\'!C154)', o['text_format'])
    optcashf_sheet.write_formula('B64', '=MIN(\'Inputs and Outputs\'!B155*\'Inputs and Outputs\'!B13*1000,\'Inputs and Outputs\'!C155)', o['text_format'])
    optcashf_sheet.write_formula('B65', '=SUM(B62,B63,B64)', o['text_format'])
    optcashf_sheet.write_blank('B66', None, o['text_format'])

    optcashf_sheet.write_formula('B67', '=SUM(B34,B39,B43,B48,B52,B56,B60,B65)', o['text_format'])
    optcashf_sheet.write_blank('B68', None, o['text_format'])

    optcashf_sheet.write_formula('B70', '=MIN((\'Inputs and Outputs\'!B167/100)*(\'Inputs and Outputs\'!B61-B71-B76),\'Inputs and Outputs\'!C167)', o['text_format'])
    optcashf_sheet.write_formula('B71', '=MIN((\'Inputs and Outputs\'!B168/100)*\'Inputs and Outputs\'!B61,\'Inputs and Outputs\'!C168)', o['text_format'])
    optcashf_sheet.write_formula('B72', '=SUM(B70,B71)', o['text_format'])
    optcashf_sheet.write_blank('B73', None, o['text_format'])
    optcashf_sheet.write_formula('B74', '=MIN(\'Inputs and Outputs\'!B170*\'Inputs and Outputs\'!B18,\'Inputs and Outputs\'!C170)', o['text_format'])
    optcashf_sheet.write_formula('B75', '=MIN(\'Inputs and Outputs\'!B171*\'Inputs and Outputs\'!B18,\'Inputs and Outputs\'!C171)', o['text_format'])
    optcashf_sheet.write_formula('B76', '=MIN(\'Inputs and Outputs\'!B172*\'Inputs and Outputs\'!B18,\'Inputs and Outputs\'!C172)', o['text_format'])
    optcashf_sheet.write_formula('B77', '=SUM(B74,B75,B76)', o['text_format'])
    optcashf_sheet.write_blank('B78', None, o['text_format'])

    optcashf_sheet.write_formula('B79', '=SUM(B34,B39,B43,B48,B52,B56,B60,B65,B72,B77)', o['text_format'])
    optcashf_sheet.write_blank('B80', None, o['text_format'])

    for idx in range(2, 27):
        col = base_upper_case_letters[idx] # C through AA
        expcol = base_upper_case_letters[idx-1] # B through Z for exponent
        
        optcashf_sheet.write_formula(
            col+'82',
            '=IF('+str(idx-2)+' < \'Inputs and Outputs\'!E109, MIN(\'Inputs and Outputs\'!B109 * (\'Inputs and Outputs\'!'+col+'182 - \'Inputs and Outputs\'!'+col+'183), \'Inputs and Outputs\'!C109 * (1 - \'Inputs and Outputs\'!B5/100)^'+str(idx-2)+'), 0)',
            o['text_format']
        )

        optcashf_sheet.write_formula(
            col+'83',
            '=IF('+str(idx-2)+' < \'Inputs and Outputs\'!E109, MIN(\'Inputs and Outputs\'!B109 * (\'Inputs and Outputs\'!'+col+'183), \'Inputs and Outputs\'!C109 * (1 - \'Inputs and Outputs\'!B5/100)^'+str(idx-2)+'), 0)',
            o['text_format']
        )
        
        optcashf_sheet.write_formula(
            col+'84',
            '=IF('+str(idx-2)+' < \'Inputs and Outputs\'!E126, MIN(\'Inputs and Outputs\'!B126 * \'Inputs and Outputs\'!'+col+'184, \'Inputs and Outputs\'!C126), 0)',
            o['text_format']
        )

        optcashf_sheet.write_formula(
            col+'85',
            '=IF('+str(idx-2)+' < \'Inputs and Outputs\'!E157, MIN(\'Inputs and Outputs\'!B157 * \'Inputs and Outputs\'!'+col+'186, \'Inputs and Outputs\'!C157), 0)',
            o['text_format']
        )

        optcashf_sheet.write_formula(
            col+'86',
            '=IF(\'Inputs and Outputs\'!D109="Yes", '+col+'82, 0) + IF(\'Inputs and Outputs\'!D109="Yes", '+col+'83, 0) + IF(\'Inputs and Outputs\'!D126="Yes", '+col+'84, 0)+IF(\'Inputs and Outputs\'!D157="Yes", '+col+'85, 0)',
            o['text_format_2']
        )

        optcashf_sheet.write_formula(
            col+'87',
            '=IF(\'Inputs and Outputs\'!D109="No", '+col+'82, 0) + IF(\'Inputs and Outputs\'!D109="No", '+col+'83, 0)+IF(\'Inputs and Outputs\'!D126="No", '+col+'84, 0)+IF(\'Inputs and Outputs\'!D157="No", '+col+'85, 0)',
            o['text_format_2']
        )

    optcashf_sheet.write_formula(
        'B86',
        '=IF(\'Inputs and Outputs\'!D102="Yes", B32, 0) + IF(\'Inputs and Outputs\'!D103="Yes", B33, 0) + IF(\'Inputs and Outputs\'!D105="Yes", B36,0) + IF(\'Inputs and Outputs\'!D106="Yes", B37, 0) + IF(\'Inputs and Outputs\'!D107="Yes", B38, 0)+IF(\'Inputs and Outputs\'!D136="Yes", B50, 0)+IF(\'Inputs and Outputs\'!D137="Yes", B51, 0)+IF(\'Inputs and Outputs\'!D139="Yes", B54, 0)+IF(\'Inputs and Outputs\'!D140="Yes", B55, 0)+IF(\'Inputs and Outputs\'!D119="Yes", B41, 0)+IF(\'Inputs and Outputs\'!D120="Yes", B42, 0)+IF(\'Inputs and Outputs\'!D123="Yes", B45, 0)+IF(\'Inputs and Outputs\'!D122="Yes", B46, 0)+IF(\'Inputs and Outputs\'!D124="Yes", B47, 0)+IF(\'Inputs and Outputs\'!D150="Yes", B58, 0)+IF(\'Inputs and Outputs\'!D151="Yes", B59, 0)+IF(\'Inputs and Outputs\'!D154="Yes", B62, 0)+IF(\'Inputs and Outputs\'!D153="Yes", B63, 0)+IF(\'Inputs and Outputs\'!D155="Yes", B64, 0)+IF(\'Inputs and Outputs\'!D167="Yes", B70, 0)+IF(\'Inputs and Outputs\'!D168="Yes", B71, 0)+IF(\'Inputs and Outputs\'!D171="Yes", B74, 0)+IF(\'Inputs and Outputs\'!D170="Yes", B75, 0)+IF(\'Inputs and Outputs\'!D172="Yes", B76, 0)',
        o['text_format_2']
    )
    optcashf_sheet.write_formula(
        'B87',
        '=IF(\'Inputs and Outputs\'!D102="No", B32, 0) + IF(\'Inputs and Outputs\'!D103="No", B33, 0) + IF(\'Inputs and Outputs\'!D105="No", B36,0) + IF(\'Inputs and Outputs\'!D106="No", B37, 0) + IF(\'Inputs and Outputs\'!D107="No", B38, 0) + IF(\'Inputs and Outputs\'!D109="No", B82, 0) + IF(\'Inputs and Outputs\'!D109="No", B83, 0)+IF(\'Inputs and Outputs\'!D136="No", B50, 0)+IF(\'Inputs and Outputs\'!D137="No", B51, 0)+IF(\'Inputs and Outputs\'!D139="No", B54, 0)+IF(\'Inputs and Outputs\'!D140="No", B55, 0)+IF(\'Inputs and Outputs\'!D119="No", B41, 0)+IF(\'Inputs and Outputs\'!D120="No", B42, 0)+IF(\'Inputs and Outputs\'!D123="No", B45, 0)+IF(\'Inputs and Outputs\'!D122="No", B46, 0)+IF(\'Inputs and Outputs\'!D124="No", B47, 0)+IF(\'Inputs and Outputs\'!D126="No", B84, 0)+IF(\'Inputs and Outputs\'!D150="No", B58, 0)+IF(\'Inputs and Outputs\'!D151="No", B59, 0)+IF(\'Inputs and Outputs\'!D154="No", B62, 0)+IF(\'Inputs and Outputs\'!D153="No", B63, 0)+IF(\'Inputs and Outputs\'!D155="No", B64, 0)+IF(\'Inputs and Outputs\'!D157="No", B85, 0)+IF(\'Inputs and Outputs\'!D167="No", B70, 0)+IF(\'Inputs and Outputs\'!D168="No", B71, 0)+IF(\'Inputs and Outputs\'!D171="No", B74, 0)+IF(\'Inputs and Outputs\'!D170="No", B75, 0)+IF(\'Inputs and Outputs\'!D172="No", B76, 0)',
        o['text_format_2']
    )

    ## Capital depreciation
    # PV
    optcashf_sheet.write_dynamic_array_formula('C91:AA91', '=\'Inputs and Outputs\'!C190:AA190', o['text_format_decimal'])
    optcashf_sheet.write_formula(
        'B92',
        '=IF(OR(\'Inputs and Outputs\'!B177=5,\'Inputs and Outputs\'!B177=7),(B142-IF(\'Inputs and Outputs\'!D97="Yes",0.5*MIN(\'Inputs and Outputs\'!B97/100*B142,\'Inputs and Outputs\'!C97),0)),0)',
        o['text_format']
    )

    optcashf_sheet.write_formula(
        'B93',
        '=B92*(1-\'Inputs and Outputs\'!B178)',
        o['text_format']
    )
    optcashf_sheet.write_dynamic_array_formula('D94:AA94', '=B93*D91:AA91', o['text_format'])
    optcashf_sheet.write_formula(
        'C94',
        '=B93*C91 + (B92*\'Inputs and Outputs\'!B178)',
        o['text_format']
    )

    # Wind
    optcashf_sheet.write_dynamic_array_formula('C96:AA96', '=\'Inputs and Outputs\'!C191:AA191', o['text_format_decimal'])
    optcashf_sheet.write_formula(
        'B97',
        '=IF(OR(\'Inputs and Outputs\'!D177=5,\'Inputs and Outputs\'!D177=7),(B144-IF(\'Inputs and Outputs\'!D114="Yes",0.5*MIN(\'Inputs and Outputs\'!B114/100*B144,\'Inputs and Outputs\'!C114),0)),0)',
        o['text_format']
    )

    optcashf_sheet.write_formula(
        'B98',
        '=B97*(1-\'Inputs and Outputs\'!D178)',
        o['text_format']
    )
    optcashf_sheet.write_dynamic_array_formula('D99:AA99', '=B98*D96:AA96', o['text_format'])
    optcashf_sheet.write_formula(
        'C99',
        '=B98*C96 + (B97*\'Inputs and Outputs\'!D178)',
        o['text_format']
    )

    # Battery
    optcashf_sheet.write_dynamic_array_formula('C101:AA101', '=\'Inputs and Outputs\'!C192:AA192', o['text_format_decimal'])
    optcashf_sheet.write_formula(
        'B102',
        '=IF(OR(\'Inputs and Outputs\'!C177=5,\'Inputs and Outputs\'!C177=7),(B146-IF(\'Inputs and Outputs\'!D131="Yes",0.5*MIN(\'Inputs and Outputs\'!B131/100*B146,\'Inputs and Outputs\'!C131),0)),0)',
        o['text_format']
    )
    optcashf_sheet.write_formula(
        'B103',
        '=B102*(1-\'Inputs and Outputs\'!C178)',
        o['text_format']
    )
    optcashf_sheet.write_dynamic_array_formula('D104:AA104', '=B103*D101:AA101', o['text_format'])
    optcashf_sheet.write_formula(
        'C104',
        '=B103*C101 + (B102*\'Inputs and Outputs\'!C178)',
        o['text_format']
    )

    # CHP
    optcashf_sheet.write_dynamic_array_formula('C106:AA106', '=\'Inputs and Outputs\'!C193:AA193', o['text_format_decimal'])
    optcashf_sheet.write_formula(
        'B107',
        '=IF(OR(\'Inputs and Outputs\'!E177=5,\'Inputs and Outputs\'!E177=7),(B148-IF(\'Inputs and Outputs\'!D145="Yes",0.5*MIN(\'Inputs and Outputs\'!B145/100*B148,\'Inputs and Outputs\'!C145),0)),0)',
        o['text_format']
    )
    optcashf_sheet.write_formula(
        'B108',
        '=B107*(1-\'Inputs and Outputs\'!E178)',
        o['text_format']
    )
    optcashf_sheet.write_dynamic_array_formula('D109:AA109', '=B108*D106:AA106', o['text_format'])
    optcashf_sheet.write_formula(
        'C109',
        '=B108*C106 + (B107*\'Inputs and Outputs\'!E178)',
        o['text_format']
    )

    # ABS CH
    optcashf_sheet.write_dynamic_array_formula('C111:AA111', '=\'Inputs and Outputs\'!C194:AA194', o['text_format_decimal'])
    optcashf_sheet.write_formula(
        'B112',
        '=IF(OR(\'Inputs and Outputs\'!F177=5,\'Inputs and Outputs\'!F177=7),\'Inputs and Outputs\'!B57,0)',
        o['text_format']
    )
    optcashf_sheet.write_formula(
        'B113',
        '=B112*(1-\'Inputs and Outputs\'!F178)',
        o['text_format']
    )
    optcashf_sheet.write_dynamic_array_formula('D114:AA114', '=B113*D111:AA111', o['text_format'])
    optcashf_sheet.write_formula(
        'C114',
        '=B113*C111 + (B112*\'Inputs and Outputs\'!F178)',
        o['text_format']
    )

    # HOT TES
    optcashf_sheet.write_dynamic_array_formula('C116:AA116', '=\'Inputs and Outputs\'!C195:AA195', o['text_format_decimal'])
    optcashf_sheet.write_formula(
        'B117',
        '=IF(OR(\'Inputs and Outputs\'!G177=5,\'Inputs and Outputs\'!G177=7),\'Inputs and Outputs\'!B58,0)',
        o['text_format']
    )
    optcashf_sheet.write_formula(
        'B118',
        '=B117*(1-\'Inputs and Outputs\'!G178)',
        o['text_format']
    )
    optcashf_sheet.write_dynamic_array_formula('D119:AA119', '=B118*D116:AA116', o['text_format'])
    optcashf_sheet.write_formula(
        'C119',
        '=B118*C116 + (B117*\'Inputs and Outputs\'!G178)',
        o['text_format']
    )

    # COLD TES
    optcashf_sheet.write_dynamic_array_formula('C121:AA121', '=\'Inputs and Outputs\'!C196:AA196', o['text_format_decimal'])
    optcashf_sheet.write_formula(
        'B122',
        '=IF(OR(\'Inputs and Outputs\'!H177=5,\'Inputs and Outputs\'!H177=7),\'Inputs and Outputs\'!B59,0)',
        o['text_format']
    )
    optcashf_sheet.write_formula(
        'B123',
        '=B122*(1-\'Inputs and Outputs\'!H178)',
        o['text_format']
    )
    optcashf_sheet.write_dynamic_array_formula('D124:AA124', '=B123*D121:AA121', o['text_format'])
    optcashf_sheet.write_formula(
        'C124',
        '=B123*C121 + (B122*\'Inputs and Outputs\'!H178)',
        o['text_format']
    )

    # STM Turb
    optcashf_sheet.write_dynamic_array_formula('C126:AA126', '=\'Inputs and Outputs\'!C197:AA197', o['text_format_decimal'])

    optcashf_sheet.write_formula(
        'B128',
        '=B127*(1-\'Inputs and Outputs\'!I178)',
        o['text_format']
    )
    optcashf_sheet.write_dynamic_array_formula('D129:AA129', '=B128*D126:AA126', o['text_format'])
    optcashf_sheet.write_formula(
        'C129',
        '=B128*C126 + (B127*\'Inputs and Outputs\'!I178)',
        o['text_format']
    )

    # GHP
    optcashf_sheet.write_dynamic_array_formula('C131:AA131', '=\'Inputs and Outputs\'!C198:AA198', o['text_format_decimal'])

    optcashf_sheet.write_formula(
        'B132',
        '=IF(OR(\'Inputs and Outputs\'!J177=5,\'Inputs and Outputs\'!J177=7),(B150-IF(\'Inputs and Outputs\'!D162="Yes",0.5*MIN(\'Inputs and Outputs\'!B162/100*B150,\'Inputs and Outputs\'!C162),0)),0)',
        o['text_format']
    )
    optcashf_sheet.write_formula(
        'B133',
        '=B132*(1-\'Inputs and Outputs\'!J178)',
        o['text_format']
    )
    optcashf_sheet.write_dynamic_array_formula('D134:AA134', '=B133*D131:AA131', o['text_format'])
    optcashf_sheet.write_formula(
        'C134',
        '=B133*C131 + (B132*\'Inputs and Outputs\'!J178)',
        o['text_format']
    )

    for idx in range(2, 27):
        col = base_upper_case_letters[idx] # C through AA
        
        optcashf_sheet.write_formula(
            col+'135',
            '=SUM('+col+'94,'+col+'99,'+col+'104,'+col+'109,'+col+'114,'+col+'119,'+col+'124,'+col+'129,'+col+'134)',
            o['text_format_2']
        )

    # Tax benefits for LCOE calculations
    optcashf_sheet.write_dynamic_array_formula('C138:AA138', '=((-1 * C10:AA10) + C94:AA94) * \'Inputs and Outputs\'!B92/100', o['text_format_2'])
    optcashf_sheet.write_dynamic_array_formula('C139:AA139', '=((-1 * C12:AA12) + C99:AA99) * \'Inputs and Outputs\'!B92/100', o['text_format_2'])

    ## federal ITC
    optcashf_sheet.write_formula('B142', '=\'Inputs and Outputs\'!B52-IF(\'Inputs and Outputs\'!E102="Yes",B32,0)-IF(\'Inputs and Outputs\'!E103="Yes",B33,0)-IF(\'Inputs and Outputs\'!E105="Yes",B36,0)-IF(\'Inputs and Outputs\'!E106="Yes",B37,0)-IF(\'Inputs and Outputs\'!E107="Yes",B38,0)', o['text_format'])
    optcashf_sheet.write_formula('B144', '=\'Inputs and Outputs\'!B53-IF(\'Inputs and Outputs\'!E119="Yes",B41,0)-IF(\'Inputs and Outputs\'!E120="Yes",B42,0)-IF(\'Inputs and Outputs\'!E122="Yes",B45,0)-IF(\'Inputs and Outputs\'!E123="Yes",B46,0)-IF(\'Inputs and Outputs\'!E124="Yes",B47,0)', o['text_format'])
    optcashf_sheet.write_formula('B146', '=\'Inputs and Outputs\'!B55-IF(\'Inputs and Outputs\'!E136="Yes",B50,0)-IF(\'Inputs and Outputs\'!E137="Yes",B51,0)-IF(\'Inputs and Outputs\'!E139="Yes",B54,0)-IF(\'Inputs and Outputs\'!E140="Yes",B55,0)', o['text_format'])
    optcashf_sheet.write_formula('B148', '=\'Inputs and Outputs\'!B56-IF(\'Inputs and Outputs\'!E150="Yes",B58,0)-IF(\'Inputs and Outputs\'!E151="Yes",B59,0)-IF(\'Inputs and Outputs\'!E153="Yes",B62,0)-IF(\'Inputs and Outputs\'!E154="Yes",B63,0)-IF(\'Inputs and Outputs\'!E155="Yes",B64,0)', o['text_format'])
    optcashf_sheet.write_formula('B150', '=\'Inputs and Outputs\'!B61-IF(\'Inputs and Outputs\'!E167="Yes",B70,0)-IF(\'Inputs and Outputs\'!E168="Yes",B71,0)-IF(\'Inputs and Outputs\'!E170="Yes",B74,0)-IF(\'Inputs and Outputs\'!E171="Yes",B75,0)-IF(\'Inputs and Outputs\'!E172="Yes",B76,0)', o['text_format'])

    optcashf_sheet.write_formula('C143', '=MIN(\'Inputs and Outputs\'!B97/100*B142,\'Inputs and Outputs\'!C97)')
    optcashf_sheet.write_formula('C145', '=MIN(\'Inputs and Outputs\'!B114/100*B144,\'Inputs and Outputs\'!C114)', o['text_format'])
    optcashf_sheet.write_formula('C147', '=MIN(\'Inputs and Outputs\'!B131/100*B146,\'Inputs and Outputs\'!C131)', o['text_format'])
    optcashf_sheet.write_formula('C149', '=MIN(\'Inputs and Outputs\'!B145/100*B148,\'Inputs and Outputs\'!C145)')
    optcashf_sheet.write_formula('C151', '=MIN(\'Inputs and Outputs\'!B162/100*B150,\'Inputs and Outputs\'!C162)', o['text_format'])
    optcashf_sheet.write_formula('C152', '=SUM(C143, C145, C147, C149, C151)', o['text_format_2'])

    # Total Cash Flows
    optcashf_sheet.write_formula('B155', '=-\'Inputs and Outputs\'!B51', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C156:AA156', '=(C27:AA27 - C28:AA28) + C28:AA28 * (1 - \'Inputs and Outputs\'!B92/100)', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('B157:AA157', '=(B86:AA86 * (1 - \'Inputs and Outputs\'!B92/100)) + B87:AA87', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C158:AA158', '=C135:AA135 * \'Inputs and Outputs\'!B92/100', o['text_format'])
    optcashf_sheet.write_dynamic_array_formula('C159:AA159', '=C152:AA152', o['text_format'])

    optcashf_sheet.write_dynamic_array_formula('C160:AA160', '=C156:AA156 + C157:AA157 + C158:AA158 + C159:AA159', o['text_format_2'])
    optcashf_sheet.write_dynamic_array_formula('C161:AA161', '=C160:AA160 / (1 + \'Inputs and Outputs\'!B89/100)^C2:AA2', o['text_format_2'])

    # GHP residual value subtracted from capital costs
    ghxresidualvalue = get_value('outputs','GHP','ghx_residual_value_present_value')
    # print(ghxresidualvalue)
    optcashf_sheet.write_formula('B160', '=B155+B157+'+str(ghxresidualvalue), o['text_format_2'])
    optcashf_sheet.write_formula('B161', '=B155+B157+'+str(ghxresidualvalue), o['text_format_2'])    
    optcashf_sheet.write_formula('B162', '=SUM(B161:AA161)', o['standalone_bold_text_format'])

    for cell in ['B139', 'B135', 'B27', 'B28']:
        optcashf_sheet.write_blank(cell, None, o['text_format_2'])

    ## BAU SHEET
    baucashf_sheet = proforma.add_worksheet('BAU Cash Flow')

    baucashf_sheet.write('A1', 'Operating Expenses', o['year_format'])
    baucashf_sheet.write('A2', 'Business as Usual electricity bill ($)', o['text_format'])
    baucashf_sheet.write('A3', 'Business as Usual export credits ($)', o['text_format'])
    baucashf_sheet.write('A4', 'Business as Usual boiler fuel bill ($)', o['text_format'])
    baucashf_sheet.write('A5', 'Operation and Maintenance (O&M)', o['text_format'])
    baucashf_sheet.write('A10', 'Total operating expenses', o['text_format_2'])
    baucashf_sheet.write('A11', 'Tax deductible operating expenses', o['text_format_2'])
    baucashf_sheet.write('A13', 'Production-based incentives (PBI)', o['subheader_format'])
    baucashf_sheet.write('A14', 'Existing PV Combined PBI', o['text_format_2'])
    baucashf_sheet.write('A15', 'Total taxable cash incentives', o['text_format_2'])
    baucashf_sheet.write('A16', 'Total non-taxable cash incentives', o['text_format_2'])
    baucashf_sheet.write('A18', 'Total Cash Flows', o['subheader_format'])
    baucashf_sheet.write('A19', 'Net Operating expenses, after-tax', o['text_format'])
    baucashf_sheet.write('A20', 'Total Cash incentives, after-tax', o['text_format'])
    baucashf_sheet.write('A21', 'Free Cash Flow', o['text_format_2'])
    baucashf_sheet.write('A22', 'Discounted Cash Flow', o['text_format_2'])
    baucashf_sheet.write('A23', 'BAU Life Cycle Cost', o['standalone_bold_text_format'])

    baucashf_sheet.set_column(0, 0, 24.25)
    baucashf_sheet.set_column('B:AA', 10.38)

    for idx in range(0,26):
        baucashf_sheet.write(1,1+idx, idx, o['year_format'])
        baucashf_sheet.write_blank(13,1+idx, None, o['subheader_format'])
        baucashf_sheet.write_blank(18,1+idx, None, o['subheader_format'])


    baucashf_sheet.write_dynamic_array_formula('C3:AA3', '=-\'Inputs and Outputs\'!B22 * (1 + \'Inputs and Outputs\'!B86/100)^C2:AA2', o['text_format'])

    baucashf_sheet.write_dynamic_array_formula('C4:AA4', '=\'Inputs and Outputs\'!B23 * (1 + \'Inputs and Outputs\'!B86/100)^C2:AA2', o['text_format'])

    baucashf_sheet.write_dynamic_array_formula('C5:AA5', '=(-1 * (\'Inputs and Outputs\'!B35 * (1 + \'Inputs and Outputs\'!B87/100)^C2:AA2))', o['text_format'])
    # Existing PV
    baucashf_sheet.write_dynamic_array_formula('C7:AA7', '=-\'Inputs and Outputs\'!B63 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2 * \'Inputs and Outputs\'!B4', o['text_format'])
    # Existing Generator fixed O&M cost
    baucashf_sheet.write_dynamic_array_formula('C8:AA8', '=-\'Inputs and Outputs\'!B65 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2 * (\'Inputs and Outputs\'!B9-\'Inputs and Outputs\'!B10)', o['text_format'])
    # Existing Generator variable O&M cost
    baucashf_sheet.write_dynamic_array_formula('C9:AA9', '=-\'Inputs and Outputs\'!B66 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2 * \'Inputs and Outputs\'!B30', o['text_format'])
    # Existing Generator fuel cost ($)
    baucashf_sheet.write_dynamic_array_formula('C10:AA10', '=-\'Inputs and Outputs\'!B68 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])

    for idx in range(2, 27):
        col = base_upper_case_letters[idx] # C through AA
        
        baucashf_sheet.write_formula(
            col+'11',
            '=SUM('+col+'3:'+col+'10)',
            o['text_format_2']
        )
    baucashf_sheet.write_dynamic_array_formula('C12:AA12', '=IF(\'Inputs and Outputs\'!B92 > 0, C11:AA11, 0)', o['text_format_2'])
    baucashf_sheet.write_dynamic_array_formula('C15:AA15', '=IF(B2:Z2 < \'Inputs and Outputs\'!E109, MIN(\'Inputs and Outputs\'!B109 * \'Inputs and Outputs\'!C183:AA183, \'Inputs and Outputs\'!C109 * (1 - \'Inputs and Outputs\'!B5/100)^B2:Z2), 0)', o['text_format_2'])
    baucashf_sheet.write_dynamic_array_formula('C16:AA16', '=IF(\'Inputs and Outputs\'!D109="Yes", C15:AA15, 0)', o['text_format_2'])

    baucashf_sheet.write_dynamic_array_formula('C17:AA17', '=IF(\'Inputs and Outputs\'!D109="No", C15:AA15, 0)', o['text_format_2'])

    baucashf_sheet.write_dynamic_array_formula('C20:AA20', '=(C11:AA11 - C12:AA12) + C12:AA12 * (1 - \'Inputs and Outputs\'!B92/100)', o['text_format'])
    baucashf_sheet.write_dynamic_array_formula('C21:AA21', '=(C16:AA16 * (1 - \'Inputs and Outputs\'!B92/100)) + C17:AA17', o['text_format'])
    baucashf_sheet.write_dynamic_array_formula('C22:AA22', '=C20:AA20 + C21:AA21', o['text_format_2'])
    baucashf_sheet.write_dynamic_array_formula('C23:AA23', '=C22:AA22 / (1 + \'Inputs and Outputs\'!B89/100)^C2:AA2', o['text_format_2'])

    baucashf_sheet.write_blank('B11', None, o['text_format_2'])
    baucashf_sheet.write_blank('B12', None, o['text_format_2'])
    baucashf_sheet.write_blank('B16', None, o['text_format_2'])
    baucashf_sheet.write_blank('B17', None, o['text_format_2'])
    baucashf_sheet.write_blank('B22', None, o['text_format_2'])
    baucashf_sheet.write_blank('B23', None, o['text_format_2'])
    baucashf_sheet.write('A7', 'Existing PV cost in $/kW', o['text_format_indent'])
    baucashf_sheet.write('A8', 'Existing Generator fixed O&M cost', o['text_format_indent'])
    baucashf_sheet.write('A9', 'Existing Generator variable O&M cost', o['text_format_indent'])
    baucashf_sheet.write('A10', 'Existing Generator fuel cost ($)', o['text_format_indent'])

    baucashf_sheet.write_formula('B24', '=SUM(B23:AA23)', o['standalone_bold_text_format'])

    ### CROSS SHEET FORMULAS
    if 'PV' in results['outputs'].keys():
        inandout_sheet.write_formula(
            'B6',
            '=ROUND(((\'Inputs and Outputs\'!B52 + -1*(NPV(\'Inputs and Outputs\'!B89/100,\'Optimal Cash Flow\'!C10:\'Optimal Cash Flow\'!AA10)) - SUM(\'Optimal Cash Flow\'!B39,\'Optimal Cash Flow\'!B34,NPV(\'Inputs and Outputs\'!B89/100,\'Optimal Cash Flow\'!C82:\'Optimal Cash Flow\'!AA82),NPV(\'Inputs and Outputs\'!B89/100,\'Optimal Cash Flow\'!C143),NPV(\'Inputs and Outputs\'!B89/100,\'Optimal Cash Flow\'!C138:\'Optimal Cash Flow\'!AA138))) ) / ((NPV(\'Inputs and Outputs\'!B89/100,\'Inputs and Outputs\'!C182:\'Inputs and Outputs\'!AA182) - NPV(\'Inputs and Outputs\'!B89/100,\'Inputs and Outputs\'!C183:\'Inputs and Outputs\'!AA183))), 4)',
            d['text_format_right_decimal']
        )
    else:
        inandout_sheet.write_number('B6', 0.0, d['text_format_right_decimal'])

    if 'Wind' in results['outputs'].keys():
        inandout_sheet.write_formula(
            'B8',
            '=ROUND((B53 + (-1 * NPV(B89/100,\'Optimal Cash Flow\'!C12:\'Optimal Cash Flow\'!AA12)) - SUM(\'Optimal Cash Flow\'!B48,\'Optimal Cash Flow\'!B43,NPV(B89/100,\'Optimal Cash Flow\'!C84:\'Optimal Cash Flow\'!AA84),NPV(B89/100,\'Optimal Cash Flow\'!C145),NPV(B89/100,\'Optimal Cash Flow\'!C139:\'Optimal Cash Flow\'!AA139)))/ NPV(B89/100, C184:AA184),4)'
        )
    else:
        inandout_sheet.write_number('B8', 0.0, d['text_format_right_decimal'])

    inandout_sheet.write_formula('B199', '=\'Optimal Cash Flow\'!B160 - \'BAU Cash Flow\'!B22', d['year_0_format'])
    inandout_sheet.write_dynamic_array_formula('C199:AA199', '=\'Optimal Cash Flow\'!C160:AA160 - \'BAU Cash Flow\'!C22:AA22', d['proj_fin_format'])

    inandout_sheet.write_formula('B200', '=B199', d['year_0_format'])
    for idx in range(2, 27):
        col = base_upper_case_letters[idx] # C through AA
        col_1 = base_upper_case_letters[idx-1] # B through Z
        
        inandout_sheet.write_formula(
            col+'200',
            '='+col+'199+'+col_1+'200',
            d['proj_fin_format']
        )

    inandout_sheet.write_formula('E6', '=-\'BAU Cash Flow\'!B24', d['proj_fin_format'])
    inandout_sheet.write_formula('E7', '=-\'Optimal Cash Flow\'!B162', d['proj_fin_format'])
    inandout_sheet.write_formula('E8', '=E6 - E7', d['proj_fin_format'])
    inandout_sheet.write_formula('E9', '=IF(E8=0,"",IRR(B199:AA199, \'Inputs and Outputs\'!B89/100))', d['proj_fin_format_decimal'])
    inandout_sheet.write_formula('E10', spp_years, d['proj_fin_format_spp'])

    # if results['inputs']['Financial']['third_party_ownership']:
    #     inandout_sheet.write('D9', 'Third-party Owner IRR, %', d['proj_fin_format_decimal'])

    proforma.close()

    return proforma

