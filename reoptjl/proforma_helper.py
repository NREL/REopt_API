import xlsxwriter
import pandas as pd
import numpy as np
import os


import xlsxwriter
import pandas as pd
import json
import numpy as np

def proforma_helper(results:dict, output):
    # Create a workbook and three worksheets.
    
    ## Large formulas
    spp_years = '=IF(\'Inputs and Outputs\'!B202=0,"", IF(\'Inputs and Outputs\'!AA202 < 0, "Over 25", SUM(IF(\'Inputs and Outputs\'!C202<0,1,IF(\'Inputs and Outputs\'!B202>0,0,-\'Inputs and Outputs\'!B202/\'Inputs and Outputs\'!C201)), IF(\'Inputs and Outputs\'!D202<0,1,IF(\'Inputs and Outputs\'!C202>0,0,-\'Inputs and Outputs\'!C202/\'Inputs and Outputs\'!D201)), IF(\'Inputs and Outputs\'!E202<0,1,IF(\'Inputs and Outputs\'!D202>0,0,-\'Inputs and Outputs\'!D202/\'Inputs and Outputs\'!E201)), IF(\'Inputs and Outputs\'!F202<0,1,IF(\'Inputs and Outputs\'!E202>0,0,-\'Inputs and Outputs\'!E202/\'Inputs and Outputs\'!F201)), IF(\'Inputs and Outputs\'!G202<0,1,IF(\'Inputs and Outputs\'!F202>0,0,-\'Inputs and Outputs\'!F202/\'Inputs and Outputs\'!G201)), IF(\'Inputs and Outputs\'!H202<0,1,IF(\'Inputs and Outputs\'!G202>0,0,-\'Inputs and Outputs\'!G202/\'Inputs and Outputs\'!H201)), IF(\'Inputs and Outputs\'!I202<0,1,IF(\'Inputs and Outputs\'!H202>0,0,-\'Inputs and Outputs\'!H202/\'Inputs and Outputs\'!I201)), IF(\'Inputs and Outputs\'!J202<0,1,IF(\'Inputs and Outputs\'!I202>0,0,-\'Inputs and Outputs\'!I202/\'Inputs and Outputs\'!J201)), IF(\'Inputs and Outputs\'!K202<0,1,IF(\'Inputs and Outputs\'!J202>0,0,-\'Inputs and Outputs\'!J202/\'Inputs and Outputs\'!K201)), IF(\'Inputs and Outputs\'!L202<0,1,IF(\'Inputs and Outputs\'!K202>0,0,-\'Inputs and Outputs\'!K202/\'Inputs and Outputs\'!L201)), IF(\'Inputs and Outputs\'!M202<0,1,IF(\'Inputs and Outputs\'!L202>0,0,-\'Inputs and Outputs\'!L202/\'Inputs and Outputs\'!M201)), IF(\'Inputs and Outputs\'!N202<0,1,IF(\'Inputs and Outputs\'!M202>0,0,-\'Inputs and Outputs\'!M202/\'Inputs and Outputs\'!N201)), IF(\'Inputs and Outputs\'!O202<0,1,IF(\'Inputs and Outputs\'!N202>0,0,-\'Inputs and Outputs\'!N202/\'Inputs and Outputs\'!O201)), IF(\'Inputs and Outputs\'!P202<0,1,IF(\'Inputs and Outputs\'!O202>0,0,-\'Inputs and Outputs\'!O202/\'Inputs and Outputs\'!P201)), IF(\'Inputs and Outputs\'!Q202<0,1,IF(\'Inputs and Outputs\'!P202>0,0,-\'Inputs and Outputs\'!P202/\'Inputs and Outputs\'!Q201)), IF(\'Inputs and Outputs\'!R202<0,1,IF(\'Inputs and Outputs\'!Q202>0,0,-\'Inputs and Outputs\'!Q202/\'Inputs and Outputs\'!R201)), IF(\'Inputs and Outputs\'!S202<0,1,IF(\'Inputs and Outputs\'!R202>0,0,-\'Inputs and Outputs\'!R202/\'Inputs and Outputs\'!S201)), IF(\'Inputs and Outputs\'!T202<0,1,IF(\'Inputs and Outputs\'!S202>0,0,-\'Inputs and Outputs\'!S202/\'Inputs and Outputs\'!T201)), IF(\'Inputs and Outputs\'!U202<0,1,IF(\'Inputs and Outputs\'!T202>0,0,-\'Inputs and Outputs\'!T202/\'Inputs and Outputs\'!U201)), IF(\'Inputs and Outputs\'!V202<0,1,IF(\'Inputs and Outputs\'!U202>0,0,-\'Inputs and Outputs\'!U202/\'Inputs and Outputs\'!V201)), IF(\'Inputs and Outputs\'!W202<0,1,IF(\'Inputs and Outputs\'!V202>0,0,-\'Inputs and Outputs\'!V202/\'Inputs and Outputs\'!W201)), IF(\'Inputs and Outputs\'!X202<0,1,IF(\'Inputs and Outputs\'!W202>0,0,-\'Inputs and Outputs\'!W202/\'Inputs and Outputs\'!X201)), IF(\'Inputs and Outputs\'!Y202<0,1,IF(\'Inputs and Outputs\'!X202>0,0,-\'Inputs and Outputs\'!X202/\'Inputs and Outputs\'!Y201)), IF(\'Inputs and Outputs\'!Z202<0,1,IF(\'Inputs and Outputs\'!Y202>0,0,-\'Inputs and Outputs\'!Y202/\'Inputs and Outputs\'!Z201)), IF(\'Inputs and Outputs\'!AA202<0,1,IF(\'Inputs and Outputs\'!Z202>0,0,-\'Inputs and Outputs\'!Z202/\'Inputs and Outputs\'!AA201)))))'
    spp_years_third_party = '=IF(\'Third-party Owner Cash Flow\'!AA164 < 0, "Over 25", SUM(IF(\'Third-party Owner Cash Flow\'!C164<0,1,IF(\'Third-party Owner Cash Flow\'!B164>0,0,-\'Third-party Owner Cash Flow\'!B164/\'Third-party Owner Cash Flow\'!C163)), IF(\'Third-party Owner Cash Flow\'!D164<0,1,IF(\'Third-party Owner Cash Flow\'!C164>0,0,-\'Third-party Owner Cash Flow\'!C164/\'Third-party Owner Cash Flow\'!D163)), IF(\'Third-party Owner Cash Flow\'!E164<0,1,IF(\'Third-party Owner Cash Flow\'!D164>0,0,-\'Third-party Owner Cash Flow\'!D164/\'Third-party Owner Cash Flow\'!E163)), IF(\'Third-party Owner Cash Flow\'!F164<0,1,IF(\'Third-party Owner Cash Flow\'!E164>0,0,-\'Third-party Owner Cash Flow\'!E164/\'Third-party Owner Cash Flow\'!F163)), IF(\'Third-party Owner Cash Flow\'!G164<0,1,IF(\'Third-party Owner Cash Flow\'!F164>0,0,-\'Third-party Owner Cash Flow\'!F164/\'Third-party Owner Cash Flow\'!G163)), IF(\'Third-party Owner Cash Flow\'!H164<0,1,IF(\'Third-party Owner Cash Flow\'!G164>0,0,-\'Third-party Owner Cash Flow\'!G164/\'Third-party Owner Cash Flow\'!H163)), IF(\'Third-party Owner Cash Flow\'!I164<0,1,IF(\'Third-party Owner Cash Flow\'!H164>0,0,-\'Third-party Owner Cash Flow\'!H164/\'Third-party Owner Cash Flow\'!I163)), IF(\'Third-party Owner Cash Flow\'!J164<0,1,IF(\'Third-party Owner Cash Flow\'!I164>0,0,-\'Third-party Owner Cash Flow\'!I164/\'Third-party Owner Cash Flow\'!J163)), IF(\'Third-party Owner Cash Flow\'!K164<0,1,IF(\'Third-party Owner Cash Flow\'!J164>0,0,-\'Third-party Owner Cash Flow\'!J164/\'Third-party Owner Cash Flow\'!K163)), IF(\'Third-party Owner Cash Flow\'!L164<0,1,IF(\'Third-party Owner Cash Flow\'!K164>0,0,-\'Third-party Owner Cash Flow\'!K164/\'Third-party Owner Cash Flow\'!L163)), IF(\'Third-party Owner Cash Flow\'!M164<0,1,IF(\'Third-party Owner Cash Flow\'!L164>0,0,-\'Third-party Owner Cash Flow\'!L164/\'Third-party Owner Cash Flow\'!M163)), IF(\'Third-party Owner Cash Flow\'!N164<0,1,IF(\'Third-party Owner Cash Flow\'!M164>0,0,-\'Third-party Owner Cash Flow\'!M164/\'Third-party Owner Cash Flow\'!N163)), IF(\'Third-party Owner Cash Flow\'!O164<0,1,IF(\'Third-party Owner Cash Flow\'!N164>0,0,-\'Third-party Owner Cash Flow\'!N164/\'Third-party Owner Cash Flow\'!O163)), IF(\'Third-party Owner Cash Flow\'!P164<0,1,IF(\'Third-party Owner Cash Flow\'!O164>0,0,-\'Third-party Owner Cash Flow\'!O164/\'Third-party Owner Cash Flow\'!P163)), IF(\'Third-party Owner Cash Flow\'!Q164<0,1,IF(\'Third-party Owner Cash Flow\'!P164>0,0,-\'Third-party Owner Cash Flow\'!P164/\'Third-party Owner Cash Flow\'!Q163)), IF(\'Third-party Owner Cash Flow\'!R164<0,1,IF(\'Third-party Owner Cash Flow\'!Q164>0,0,-\'Third-party Owner Cash Flow\'!Q164/\'Third-party Owner Cash Flow\'!R163)), IF(\'Third-party Owner Cash Flow\'!S164<0,1,IF(\'Third-party Owner Cash Flow\'!R164>0,0,-\'Third-party Owner Cash Flow\'!R164/\'Third-party Owner Cash Flow\'!S163)), IF(\'Third-party Owner Cash Flow\'!T164<0,1,IF(\'Third-party Owner Cash Flow\'!S164>0,0,-\'Third-party Owner Cash Flow\'!S164/\'Third-party Owner Cash Flow\'!T163)), IF(\'Third-party Owner Cash Flow\'!U164<0,1,IF(\'Third-party Owner Cash Flow\'!T164>0,0,-\'Third-party Owner Cash Flow\'!T164/\'Third-party Owner Cash Flow\'!U163)), IF(\'Third-party Owner Cash Flow\'!V164<0,1,IF(\'Third-party Owner Cash Flow\'!U164>0,0,-\'Third-party Owner Cash Flow\'!U164/\'Third-party Owner Cash Flow\'!V163)), IF(\'Third-party Owner Cash Flow\'!W164<0,1,IF(\'Third-party Owner Cash Flow\'!V164>0,0,-\'Third-party Owner Cash Flow\'!V164/\'Third-party Owner Cash Flow\'!W163)), IF(\'Third-party Owner Cash Flow\'!X164<0,1,IF(\'Third-party Owner Cash Flow\'!W164>0,0,-\'Third-party Owner Cash Flow\'!W164/\'Third-party Owner Cash Flow\'!X163)), IF(\'Third-party Owner Cash Flow\'!Y164<0,1,IF(\'Third-party Owner Cash Flow\'!X164>0,0,-\'Third-party Owner Cash Flow\'!X164/\'Third-party Owner Cash Flow\'!Y163)), IF(\'Third-party Owner Cash Flow\'!Z164<0,1,IF(\'Third-party Owner Cash Flow\'!Y164>0,0,-\'Third-party Owner Cash Flow\'!Y164/\'Third-party Owner Cash Flow\'!Z163)), IF(\'Third-party Owner Cash Flow\'!AA164<0,1,IF(\'Third-party Owner Cash Flow\'!Z164>0,0,-\'Third-party Owner Cash Flow\'!Z164/\'Third-party Owner Cash Flow\'!AA163))))'

    # Create a workbook and three worksheets.
    proforma = xlsxwriter.Workbook(output, {"in_memory": True})

    base_upper_case_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                            'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA']

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

    # Generic function to pull values or get 0 instead of Null
    def get_value(one:str, two:str, three:str):
        try:
            if two in results[one].keys():
                if results[one][two][three] == None:
                    return 0.0
                if type(results[one][two][three]) == str: # API bugs?
                    return float(results[one][two][three])
                return results[one][two][three]
            else:
                return 0.0
        except:
            # print('error on ', one,two,three)
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

    # create sheet
    inandout_sheet = proforma.add_worksheet('Inputs and Outputs')

    # set column widths
    inandout_sheet.set_column('A:A', 74)
    inandout_sheet.set_column('B:B', 14.75)
    inandout_sheet.set_column('C:C', 13.25)
    inandout_sheet.set_column('D:D', 23.88)
    inandout_sheet.set_column('E:E', 23.88)
    inandout_sheet.set_column('F:F', 26.88)

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

    inandout_sheet.write('A92', 'TAX AND INSURANCE PARAMETERS', d['subheader_format'])

    if results['inputs']['Financial']['third_party_ownership']:
        inandout_sheet.write('A89', 'Nominal third-party discount rate (%/year)', d['text_format'])
        inandout_sheet.write('A90', 'Nominal Host discount rate (%/year)', d['text_format'])

        inandout_sheet.write('A93', 'Third-party owner Federal income tax rate (%)', d['text_format'])
        inandout_sheet.write('A94', 'Host Federal income tax rate (%)', d['text_format'])
    else:
        inandout_sheet.write('A89', 'Nominal discount rate (%/year)', d['text_format'])
        inandout_sheet.write('A93', 'Federal income tax rate (%)', d['text_format'])
        inandout_sheet.write_blank('A90', None, d['text_format']) # intentionally left blank
        inandout_sheet.write_blank('A94', None, d['text_format']) # intentionally left blank

    # 2 from now on...
    inandout_sheet.write('A96', 'PV TAX CREDITS', d['subheader_format'])
    inandout_sheet.write('A97', 'Investment tax credit (ITC)', d['bold_text_format'])
    inandout_sheet.write('A98', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A99', 'Federal', d['text_format_indent_2'])
    inandout_sheet.write('A101', 'PV DIRECT CASH INCENTIVES', d['subheader_format'])
    inandout_sheet.write('A102', 'Investment based incentive (IBI)', d['bold_text_format'])
    inandout_sheet.write('A103', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A104', 'State (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A105', 'Utility (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A106', 'Capacity based incentive (CBI)', d['bold_text_format'])
    inandout_sheet.write('A107', 'Federal ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A108', 'State  ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A109', 'Utility  ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A110', 'Production based incentive (PBI)', d['bold_text_format'])
    inandout_sheet.write('A111', 'Combined ($/kWh)', d['text_format_indent_2'])
    inandout_sheet.write('A113', 'WIND TAX CREDITS', d['subheader_format'])
    inandout_sheet.write('A114', 'Investment tax credit (ITC)', d['bold_text_format'])
    inandout_sheet.write('A115', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A116', 'Federal', d['text_format_indent_2'])
    inandout_sheet.write('A118', 'WIND DIRECT CASH INCENTIVES', d['subheader_format'])
    inandout_sheet.write('A119', 'Investment based incentive (IBI)', d['bold_text_format'])
    inandout_sheet.write('A120', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A121', 'State (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A122', 'Utility (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A123', 'Capacity based incentive (CBI)', d['bold_text_format'])
    inandout_sheet.write('A124', 'Federal ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A125', 'State  ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A126', 'Utility  ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A127', 'Production based incentive (PBI)', d['bold_text_format'])
    inandout_sheet.write('A128', 'Combined ($/kWh)', d['text_format_indent_2'])
    inandout_sheet.write('A130', 'BATTERY TAX CREDITS', d['subheader_format'])
    inandout_sheet.write('A131', 'Investment tax credit (ITC)', d['bold_text_format'])
    inandout_sheet.write('A132', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A133', 'Federal', d['text_format_indent_2'])
    inandout_sheet.write('A135', 'BATTERY DIRECT CASH INCENTIVES', d['subheader_format'])
    inandout_sheet.write('A136', 'Investment based incentive (IBI)', d['bold_text_format'])
    inandout_sheet.write('A137', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A138', 'State (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A139', 'Utility (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A140', 'Capacity based incentive (CBI)', d['bold_text_format'])
    inandout_sheet.write('A141', 'Total ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A142', 'Total  ($/Wh)', d['text_format_indent_2'])
    inandout_sheet.write('A144', 'CHP TAX CREDITS', d['subheader_format'])
    inandout_sheet.write('A145', 'Investment tax credit (ITC)', d['bold_text_format'])
    inandout_sheet.write('A146', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A147', 'Federal', d['text_format_indent_2'])
    inandout_sheet.write('A149', 'CHP DIRECT CASH INCENTIVES', d['subheader_format'])
    inandout_sheet.write('A150', 'Investment based incentive (IBI)', d['bold_text_format'])
    inandout_sheet.write('A151', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A152', 'State (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A153', 'Utility (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A154', 'Capacity based incentive (CBI)', d['bold_text_format'])
    inandout_sheet.write('A155', 'Federal ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A156', 'State  ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A157', 'Utility  ($/W)', d['text_format_indent_2'])
    inandout_sheet.write('A158', 'Production based incentive (PBI)', d['bold_text_format'])
    inandout_sheet.write('A159', 'Combined ($/kWh)', d['text_format_indent_2'])
    inandout_sheet.write('A161', 'GHP TAX CREDITS', d['subheader_format'])
    inandout_sheet.write('A162', 'Investment tax credit (ITC)', d['bold_text_format'])
    inandout_sheet.write('A163', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A164', 'Federal', d['text_format_indent_2'])
    inandout_sheet.write('A166', 'GHP DIRECT CASH INCENTIVES', d['subheader_format'])
    inandout_sheet.write('A167', 'Investment based incentive (IBI)', d['bold_text_format'])
    inandout_sheet.write('A168', 'As percentage', d['text_format_indent'])
    inandout_sheet.write('A169', 'State (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A170', 'Utility (% of total installed cost)', d['text_format_indent_2'])
    inandout_sheet.write('A171', 'Capacity based incentive (CBI)', d['bold_text_format'])
    inandout_sheet.write('A172', 'Federal ($/ton)', d['text_format_indent_2'])
    inandout_sheet.write('A173', 'State  ($/ton)', d['text_format_indent_2'])
    inandout_sheet.write('A174', 'Utility  ($/ton)', d['text_format_indent_2'])
    inandout_sheet.write('A175', 'Production based incentive (PBI)', d['bold_text_format'])
    inandout_sheet.write('A176', 'Combined ($/kWh)', d['text_format_indent_2'])
    inandout_sheet.write('A178', 'DEPRECIATION', d['subheader_format'])
    inandout_sheet.write('A179', 'Federal (years)', d['text_format'])
    inandout_sheet.write('A180', 'Federal bonus fraction', d['text_format'])
    inandout_sheet.write('A183', 'ANNUAL VALUES', d['subheader_format'])
    inandout_sheet.write('A184', 'PV Annual electricity (kWh)', d['text_format'])
    inandout_sheet.write('A185', 'Existing PV Annual electricity (kWh)', d['text_format'])
    inandout_sheet.write('A186', 'Wind Annual electricity (kWh)', d['text_format'])
    inandout_sheet.write('A187', 'Backup Generator Annual electricity (kWh)', d['text_format'])
    inandout_sheet.write('A188', 'CHP Annual electricity (kWh)', d['text_format'])
    inandout_sheet.write('A189', 'CHP Annual heat (MMBtu)', d['text_format'])
    inandout_sheet.write('A190', 'Steam Turbine Annual electricity (kWh)', d['text_format'])
    inandout_sheet.write('A191', 'Steam Turbine Annual heat (MMBtu)', d['text_format'])
    inandout_sheet.write('A192', 'PV Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A193', 'Wind Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A194', 'Battery Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A195', 'CHP Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A196', 'Absorption Chiller Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A197', 'Hot TES Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A198', 'Cold TES Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A199', 'Steam turbine Federal depreciation percentages (fraction)', d['text_format'])
    inandout_sheet.write('A200', 'GHP Federal depreciation percentages (fraction)', d['text_format'])

    if results['inputs']['Financial']['third_party_ownership'] == False:
        inandout_sheet.write('A201', 'Free Cash Flow', d['text_format'])
        inandout_sheet.write('A202', 'Cumulative Free Cash Flow', d['text_format'])


    inandout_sheet.write_blank('B1', None, d['header_format_right'])
    inandout_sheet.write_blank('B2', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B21', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B50', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B83', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B92', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B96', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C96', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D96', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B101', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C101', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D101', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('E101', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B113', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C113', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D113', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B118', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C118', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D118', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('E118', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B130', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C130', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D130', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B135', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C135', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D135', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('E135', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B144', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C144', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D144', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B149', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C149', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D149', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('E149', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B161', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C161', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D161', None, d['subheader_format_right'])
    inandout_sheet.write_blank('B166', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('C166', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('D166', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('E166', None, d['subheader_format_right'])
    inandout_sheet.write_blank('M178', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('N178', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('O178', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('P178', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('Q178', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('R178', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('S178', None, d['subheader_format_mid'])
    inandout_sheet.write_blank('T178', None, d['subheader_format_right'])
    inandout_sheet.write('D5', 'RESULTS', d['subheader_format'])
    inandout_sheet.write_blank('E5', None, d['subheader_format_right'])

    if results['inputs']['Financial']['third_party_ownership']:
        inandout_sheet.write('D6', 'Annual payment to third-party, $', d['text_format'])
        inandout_sheet.write('D7', 'Third-party Owner NPC, $', d['text_format'])
        inandout_sheet.write('D8', 'Hosts NPV, $', d['text_format'])
        inandout_sheet.write('D9', 'Third-party Owner IRR, %', d['text_format'])
        inandout_sheet.write('D10', 'Third-party Owner Simple Payback Period, years', d['text_format'])
        inandout_sheet.write('F7', 'NOTE: A negative Net Present Cost can occur if incentives are greater than costs.', d['text_format'])
        inandout_sheet.write('F8', 'NOTE: This NPV can differ slightly (<1%) from the Webtool/API results due to rounding and the tolerance in the optimizer.', d['text_format'])
    else:
        inandout_sheet.write('D6', 'Business as usual LCC, $', d['text_format'])
        inandout_sheet.write('D7', 'Optimal LCC, $', d['text_format'])
        inandout_sheet.write('D8', 'NPV, $', d['text_format'])
        inandout_sheet.write('D9', 'IRR, %', d['text_format'])
        inandout_sheet.write('D10', 'Simple Payback Period, years', d['text_format'])
        inandout_sheet.write('F7', 'NOTE: A negative LCC indicates a profit (for example when production based incentives are greater than costs.', d['text_format'])
        inandout_sheet.write('F8', 'NOTE: This NPV can differ slightly (<1%) from the Webtool/API results due to rounding and the tolerance in the optimizer.', d['text_format'])

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

    # Tax and insurance parameters
    if results['inputs']['Financial']['third_party_ownership']:
        inandout_sheet.write('B89', 100*get_value('inputs','Financial','owner_discount_rate_fraction'), d['text_format_right_decimal'])
        inandout_sheet.write('B90', 100*get_value('inputs','Financial','offtaker_discount_rate_fraction'), d['text_format_right_decimal'])

        inandout_sheet.write('B93', 100*get_value('inputs','Financial','owner_tax_rate_fraction'), d['text_format'])
        inandout_sheet.write('B94', 100*get_value('inputs','Financial','offtaker_tax_rate_fraction'), d['text_format'])
    else:
        inandout_sheet.write('B89', 100*get_value('inputs','Financial','offtaker_discount_rate_fraction'), d['text_format'])
        inandout_sheet.write('B93', 100*get_value('inputs','Financial','offtaker_tax_rate_fraction'), d['text_format'])
        inandout_sheet.write_blank('B90', None, d['text_format']) # intentionally left blank
        inandout_sheet.write_blank('B94', None, d['text_format']) # intentionally left blank

    ## PV Tax credits section
    bases = [97, 114, 131, 145, 162]
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
        inandout_sheet.write(k+'178', i, d['subheader_format_mid'])
        inandout_sheet.write(k+'179', get_value('inputs', j, 'macrs_option_years'), d['text_format'])
        inandout_sheet.write(k+'180', get_value('inputs', j, 'macrs_bonus_fraction'), d['text_format'])

    inandout_sheet.write('L178', 'MACRS SCHEDULES (INFORMATIONAL ONLY)', d['subheader_format'])
    inandout_sheet.write('L179', 'Year', d['standalone_bold_text_format'])
    inandout_sheet.write('L180', '5-Year', d['standalone_bold_text_format'])
    inandout_sheet.write('L181', '7-Year', d['standalone_bold_text_format'])
    inandout_sheet.write('M179', 1, d['text_format'])
    inandout_sheet.write('N179', 2, d['text_format'])
    inandout_sheet.write('O179', 3, d['text_format'])
    inandout_sheet.write('P179', 4, d['text_format'])
    inandout_sheet.write('Q179', 5, d['text_format'])
    inandout_sheet.write('R179', 6, d['text_format'])
    inandout_sheet.write('S179', 7, d['text_format_right_center_align'])
    inandout_sheet.write('T179', 8, d['text_format_right_center_align'])
    inandout_sheet.write('M180', 0.2, d['text_format'])
    inandout_sheet.write('N180', 0.32, d['text_format'])
    inandout_sheet.write('O180', 0.192, d['text_format'])
    inandout_sheet.write('P180', 0.1152, d['text_format'])
    inandout_sheet.write('Q180', 0.1152, d['text_format'])
    inandout_sheet.write('R180', 0.0576, d['text_format'])
    inandout_sheet.write_blank('S180', None, d['text_format_right_center_align'])
    inandout_sheet.write_blank('T180', None, d['text_format_right_center_align'])
    inandout_sheet.write('M181', 0.1429, d['text_format'])
    inandout_sheet.write('N181', 0.2449, d['text_format'])
    inandout_sheet.write('O181', 0.1749, d['text_format'])
    inandout_sheet.write('P181', 0.1249, d['text_format'])
    inandout_sheet.write('Q181', 0.0893, d['text_format'])
    inandout_sheet.write('R181', 0.0892, d['text_format'])
    inandout_sheet.write('S181', 0.0893, d['text_format_right_center_align'])
    inandout_sheet.write('T181', 0.0446, d['text_format_right_center_align'])

    ## Annual values
    for idx in range(184,201):
        inandout_sheet.write('B'+str(idx), 0, d['year_0_format'])

    for idx in range(1,27):
        inandout_sheet.write(base_upper_case_letters[idx]+'183', idx-1, d['subheader_format_mid'])

    ## PV Tax credits section
    bases = [97, 114, 131, 145, 162]
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
        inandout_sheet.write(base_upper_case_letters[idx]+'184', '=B27*(1 - (B5/100))^'+str(idx-2), d['proj_fin_format'])
        inandout_sheet.write(base_upper_case_letters[idx]+'185', '=B26*(1 - (B5/100))^'+str(idx-2), d['proj_fin_format'])
        inandout_sheet.write(base_upper_case_letters[idx]+'186', '=B29', d['proj_fin_format'])
        inandout_sheet.write(base_upper_case_letters[idx]+'187', '=B30', d['proj_fin_format'])
        inandout_sheet.write(base_upper_case_letters[idx]+'188', '=B31', d['proj_fin_format'])
        inandout_sheet.write(base_upper_case_letters[idx]+'189', '=B38', d['proj_fin_format'])
        inandout_sheet.write(base_upper_case_letters[idx]+'190', '=B33', d['proj_fin_format'])
        inandout_sheet.write(base_upper_case_letters[idx]+'191', '=B39', d['proj_fin_format'])

    for cidx in range(2,27):
        for ridx in range(192, 201):
            inandout_sheet.write(base_upper_case_letters[cidx]+str(ridx), 0.0, d['proj_fin_format_decimal'])

    ## MACRS depreciation fraction over the years
    bases = [192, 193, 194, 195, 196, 197, 198, 199, 200]
    techs = ['PV', 'Wind', 'ElectricStorage', 'CHP', 'AbsorptionChiller', 'HotThermalStorage', 'ColdThermalStorage', 'SteamTurbine', 'GHP']

    for b,t in zip(bases, techs):
        if get_value('inputs',t,'macrs_option_years') == 7:
            inandout_sheet.write_formula('C'+str(b),'=M181',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('D'+str(b),'=N181',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('E'+str(b),'=O181',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('F'+str(b),'=P181',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('G'+str(b),'=Q181',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('H'+str(b),'=R181',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('I'+str(b),'=S181',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('J'+str(b),'=T181',d['proj_fin_format_decimal'])
        elif get_value('inputs',t,'macrs_option_years') == 5:
            inandout_sheet.write_formula('C'+str(b),'=M180',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('D'+str(b),'=N180',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('E'+str(b),'=O180',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('F'+str(b),'=P180',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('G'+str(b),'=Q180',d['proj_fin_format_decimal'])
            inandout_sheet.write_formula('H'+str(b),'=R180',d['proj_fin_format_decimal'])
        else:
            pass

    ### OPTIMAL SHEET
    if results['inputs']['Financial']['third_party_ownership'] == False:
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
            optcashf_sheet.write_formula(col+'28', '=IF(\'Inputs and Outputs\'!B93 > 0, '+col+'27, 0)', o['text_format_2'])
        
        # direct cash incentives
        
        optcashf_sheet.write_formula('B32', '=MIN((\'Inputs and Outputs\'!B104/100)*(\'Inputs and Outputs\'!B52-B33-B38),\'Inputs and Outputs\'!C104)', o['text_format'])
        optcashf_sheet.write_formula('B33', '=MIN((\'Inputs and Outputs\'!B105/100)*\'Inputs and Outputs\'!B52,\'Inputs and Outputs\'!C105)', o['text_format'])
        optcashf_sheet.write_formula('B34', '=SUM(B32,B33)', o['text_format'])
        optcashf_sheet.write_blank('B35', None, o['text_format'])
        optcashf_sheet.write_formula('B36', '=MIN(\'Inputs and Outputs\'!B107*\'Inputs and Outputs\'!B3*1000,\'Inputs and Outputs\'!C107)', o['text_format'])
        optcashf_sheet.write_formula('B37', '=MIN(\'Inputs and Outputs\'!B108*\'Inputs and Outputs\'!B3*1000,\'Inputs and Outputs\'!C108)', o['text_format'])
        optcashf_sheet.write_formula('B38', '=MIN(\'Inputs and Outputs\'!B109*\'Inputs and Outputs\'!B3*1000,\'Inputs and Outputs\'!C109)', o['text_format'])
        optcashf_sheet.write_formula('B39', '=SUM(B36,B37,B38)', o['text_format'])
        optcashf_sheet.write_blank('B40', None, o['text_format'])
        
        optcashf_sheet.write_formula('B41', '=MIN((\'Inputs and Outputs\'!B121/100)*(\'Inputs and Outputs\'!B53-B42-B47),\'Inputs and Outputs\'!C121)', o['text_format'])
        optcashf_sheet.write_formula('B42', '=MIN((\'Inputs and Outputs\'!B122/100)*\'Inputs and Outputs\'!B53,\'Inputs and Outputs\'!C122)', o['text_format'])
        optcashf_sheet.write_formula('B43', '=SUM(B41,B42)', o['text_format'])
        optcashf_sheet.write_blank('B44', None, o['text_format'])
        optcashf_sheet.write_formula('B45', '=MIN(\'Inputs and Outputs\'!B124*\'Inputs and Outputs\'!B7*1000,\'Inputs and Outputs\'!C124)', o['text_format'])
        optcashf_sheet.write_formula('B46', '=MIN(\'Inputs and Outputs\'!B125*\'Inputs and Outputs\'!B7*1000,\'Inputs and Outputs\'!C125)', o['text_format'])
        optcashf_sheet.write_formula('B47', '=MIN(\'Inputs and Outputs\'!B126*\'Inputs and Outputs\'!B7*1000,\'Inputs and Outputs\'!C126)', o['text_format'])
        optcashf_sheet.write_formula('B48', '=SUM(B45,B46,B47)', o['text_format'])
        optcashf_sheet.write_blank('B49', None, o['text_format'])
        
        optcashf_sheet.write_formula('B50', '=MIN((\'Inputs and Outputs\'!B138/100)*(\'Inputs and Outputs\'!B55),\'Inputs and Outputs\'!C138)', o['text_format'])
        optcashf_sheet.write_formula('B51', '=MIN((\'Inputs and Outputs\'!B139/100)*\'Inputs and Outputs\'!B55,\'Inputs and Outputs\'!C139)', o['text_format'])
        optcashf_sheet.write_formula('B52', '=SUM(B50,B51)', o['text_format'])
        optcashf_sheet.write_blank('B53', None, o['text_format'])
        optcashf_sheet.write_formula('B54', '=MIN(\'Inputs and Outputs\'!B141*\'Inputs and Outputs\'!B11*1000,\'Inputs and Outputs\'!C141)', o['text_format'])
        optcashf_sheet.write_formula('B55', '=MIN(\'Inputs and Outputs\'!B142*\'Inputs and Outputs\'!B12*1000,\'Inputs and Outputs\'!C142)', o['text_format'])
        optcashf_sheet.write_formula('B56', '=SUM(B54,B55)', o['text_format'])
        optcashf_sheet.write_blank('B57', None, o['text_format'])
        
        optcashf_sheet.write_formula('B58', '=MIN((\'Inputs and Outputs\'!B152/100)*(\'Inputs and Outputs\'!B56-B59-B64),\'Inputs and Outputs\'!C152)', o['text_format'])
        optcashf_sheet.write_formula('B59', '=MIN((\'Inputs and Outputs\'!B153/100)*\'Inputs and Outputs\'!B56,\'Inputs and Outputs\'!C153)', o['text_format'])
        optcashf_sheet.write_formula('B60', '=SUM(B58,B59)', o['text_format'])
        optcashf_sheet.write_blank('B61', None, o['text_format'])
        optcashf_sheet.write_formula('B62', '=MIN(\'Inputs and Outputs\'!B155*\'Inputs and Outputs\'!B13*1000,\'Inputs and Outputs\'!C155)', o['text_format'])
        optcashf_sheet.write_formula('B63', '=MIN(\'Inputs and Outputs\'!B156*\'Inputs and Outputs\'!B13*1000,\'Inputs and Outputs\'!C156)', o['text_format'])
        optcashf_sheet.write_formula('B64', '=MIN(\'Inputs and Outputs\'!B157*\'Inputs and Outputs\'!B13*1000,\'Inputs and Outputs\'!C157)', o['text_format'])
        optcashf_sheet.write_formula('B65', '=SUM(B62,B63,B64)', o['text_format'])
        optcashf_sheet.write_blank('B66', None, o['text_format'])
        
        optcashf_sheet.write_formula('B67', '=SUM(B34,B39,B43,B48,B52,B56,B60,B65)', o['text_format'])
        optcashf_sheet.write_blank('B68', None, o['text_format'])
        
        optcashf_sheet.write_formula('B70', '=MIN((\'Inputs and Outputs\'!B169/100)*(\'Inputs and Outputs\'!B61-B71-B76),\'Inputs and Outputs\'!C169)', o['text_format'])
        optcashf_sheet.write_formula('B71', '=MIN((\'Inputs and Outputs\'!B170/100)*\'Inputs and Outputs\'!B61,\'Inputs and Outputs\'!C170)', o['text_format'])
        optcashf_sheet.write_formula('B72', '=SUM(B70,B71)', o['text_format'])
        optcashf_sheet.write_blank('B73', None, o['text_format'])
        optcashf_sheet.write_formula('B74', '=MIN(\'Inputs and Outputs\'!B172*\'Inputs and Outputs\'!B18,\'Inputs and Outputs\'!C172)', o['text_format'])
        optcashf_sheet.write_formula('B75', '=MIN(\'Inputs and Outputs\'!B173*\'Inputs and Outputs\'!B18,\'Inputs and Outputs\'!C173)', o['text_format'])
        optcashf_sheet.write_formula('B76', '=MIN(\'Inputs and Outputs\'!B174*\'Inputs and Outputs\'!B18,\'Inputs and Outputs\'!C174)', o['text_format'])
        optcashf_sheet.write_formula('B77', '=SUM(B74,B75,B76)', o['text_format'])
        optcashf_sheet.write_blank('B78', None, o['text_format'])
        
        optcashf_sheet.write_formula('B79', '=SUM(B34,B39,B43,B48,B52,B56,B60,B65,B72,B77)', o['text_format'])
        optcashf_sheet.write_blank('B80', None, o['text_format'])
        
        for idx in range(2, 27):
            col = base_upper_case_letters[idx] # C through AA
            expcol = base_upper_case_letters[idx-1] # B through Z for exponent
            
            optcashf_sheet.write_formula(
                col+'82',
                '=IF('+str(idx-2)+' < \'Inputs and Outputs\'!E111, MIN(\'Inputs and Outputs\'!B111 * (\'Inputs and Outputs\'!'+col+'184 - \'Inputs and Outputs\'!'+col+'185), \'Inputs and Outputs\'!C111 * (1 - \'Inputs and Outputs\'!B5/100)^'+str(idx-2)+'), 0)',
                o['text_format']
            )
        
            optcashf_sheet.write_formula(
                col+'83',
                '=IF('+str(idx-2)+' < \'Inputs and Outputs\'!E111, MIN(\'Inputs and Outputs\'!B111 * (\'Inputs and Outputs\'!'+col+'185), \'Inputs and Outputs\'!C111 * (1 - \'Inputs and Outputs\'!B5/100)^'+str(idx-2)+'), 0)',
                o['text_format']
            )
            
            optcashf_sheet.write_formula(
                col+'84',
                '=IF('+str(idx-2)+' < \'Inputs and Outputs\'!E128, MIN(\'Inputs and Outputs\'!B128 * \'Inputs and Outputs\'!'+col+'186, \'Inputs and Outputs\'!C128), 0)',
                o['text_format']
            )
        
            optcashf_sheet.write_formula(
                col+'85',
                '=IF('+str(idx-2)+' < \'Inputs and Outputs\'!E159, MIN(\'Inputs and Outputs\'!B159 * \'Inputs and Outputs\'!'+col+'188, \'Inputs and Outputs\'!C159), 0)',
                o['text_format']
            )
        
            optcashf_sheet.write_formula(
                col+'86',
                '=IF(\'Inputs and Outputs\'!D109="Yes", '+col+'82, 0) + IF(\'Inputs and Outputs\'!D111="Yes", '+col+'83, 0) + IF(\'Inputs and Outputs\'!D128="Yes", '+col+'84, 0)+IF(\'Inputs and Outputs\'!D159="Yes", '+col+'85, 0)',
                o['text_format_2']
            )
        
            optcashf_sheet.write_formula(
                col+'87',
                '=IF(\'Inputs and Outputs\'!D111="No", '+col+'82, 0) + IF(\'Inputs and Outputs\'!D111="No", '+col+'83, 0)+IF(\'Inputs and Outputs\'!D128="No", '+col+'84, 0)+IF(\'Inputs and Outputs\'!D159="No", '+col+'85, 0)',
                o['text_format_2']
            )
        
        optcashf_sheet.write_formula(
            'B86',
            '=IF(\'Inputs and Outputs\'!D104="Yes", B32, 0) + IF(\'Inputs and Outputs\'!D105="Yes", B33, 0) + IF(\'Inputs and Outputs\'!D107="Yes", B36,0) + IF(\'Inputs and Outputs\'!D108="Yes", B37, 0) + IF(\'Inputs and Outputs\'!D109="Yes", B38, 0)+IF(\'Inputs and Outputs\'!D138="Yes", B50, 0)+IF(\'Inputs and Outputs\'!D139="Yes", B51, 0)+IF(\'Inputs and Outputs\'!D141="Yes", B54, 0)+IF(\'Inputs and Outputs\'!D142="Yes", B55, 0)+IF(\'Inputs and Outputs\'!D121="Yes", B41, 0)+IF(\'Inputs and Outputs\'!D122="Yes", B42, 0)+IF(\'Inputs and Outputs\'!D125="Yes", B45, 0)+IF(\'Inputs and Outputs\'!D124="Yes", B46, 0)+IF(\'Inputs and Outputs\'!D126="Yes", B47, 0)+IF(\'Inputs and Outputs\'!D152="Yes", B58, 0)+IF(\'Inputs and Outputs\'!D153="Yes", B59, 0)+IF(\'Inputs and Outputs\'!D156="Yes", B62, 0)+IF(\'Inputs and Outputs\'!D155="Yes", B63, 0)+IF(\'Inputs and Outputs\'!D157="Yes", B64, 0)+IF(\'Inputs and Outputs\'!D169="Yes", B70, 0)+IF(\'Inputs and Outputs\'!D170="Yes", B71, 0)+IF(\'Inputs and Outputs\'!D173="Yes", B74, 0)+IF(\'Inputs and Outputs\'!D172="Yes", B75, 0)+IF(\'Inputs and Outputs\'!D174="Yes", B76, 0)',
            o['text_format_2']
        )
        optcashf_sheet.write_formula(
            'B87',
            '=IF(\'Inputs and Outputs\'!D104="No", B32, 0) + IF(\'Inputs and Outputs\'!D105="No", B33, 0) + IF(\'Inputs and Outputs\'!D107="No", B36,0) + IF(\'Inputs and Outputs\'!D108="No", B37, 0) + IF(\'Inputs and Outputs\'!D109="No", B38, 0) + IF(\'Inputs and Outputs\'!D111="No", B82, 0) + IF(\'Inputs and Outputs\'!D111="No", B83, 0)+IF(\'Inputs and Outputs\'!D138="No", B50, 0)+IF(\'Inputs and Outputs\'!D139="No", B51, 0)+IF(\'Inputs and Outputs\'!D141="No", B54, 0)+IF(\'Inputs and Outputs\'!D142="No", B55, 0)+IF(\'Inputs and Outputs\'!D121="No", B41, 0)+IF(\'Inputs and Outputs\'!D122="No", B42, 0)+IF(\'Inputs and Outputs\'!D125="No", B45, 0)+IF(\'Inputs and Outputs\'!D124="No", B46, 0)+IF(\'Inputs and Outputs\'!D126="No", B47, 0)+IF(\'Inputs and Outputs\'!D128="No", B84, 0)+IF(\'Inputs and Outputs\'!D152="No", B58, 0)+IF(\'Inputs and Outputs\'!D153="No", B59, 0)+IF(\'Inputs and Outputs\'!D156="No", B62, 0)+IF(\'Inputs and Outputs\'!D155="No", B63, 0)+IF(\'Inputs and Outputs\'!D157="No", B64, 0)+IF(\'Inputs and Outputs\'!D159="No", B85, 0)+IF(\'Inputs and Outputs\'!D169="No", B70, 0)+IF(\'Inputs and Outputs\'!D170="No", B71, 0)+IF(\'Inputs and Outputs\'!D173="No", B74, 0)+IF(\'Inputs and Outputs\'!D172="No", B75, 0)+IF(\'Inputs and Outputs\'!D174="No", B76, 0)',
            o['text_format_2']
        )
        
        ## Capital depreciation
        # PV
        optcashf_sheet.write_dynamic_array_formula('C91:AA91', '=\'Inputs and Outputs\'!C192:AA192', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B92',
            '=IF(OR(\'Inputs and Outputs\'!B179=5,\'Inputs and Outputs\'!B179=7),(B142-IF(\'Inputs and Outputs\'!D99="Yes",0.5*MIN(\'Inputs and Outputs\'!B99/100*B142,\'Inputs and Outputs\'!C99),0)),0)',
            o['text_format']
        )
        
        optcashf_sheet.write_formula(
            'B93',
            '=B92*(1-\'Inputs and Outputs\'!B180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D94:AA94', '=B93*D91:AA91', o['text_format'])
        optcashf_sheet.write_formula(
            'C94',
            '=B93*C91 + (B92*\'Inputs and Outputs\'!B180)',
            o['text_format']
        )
        
        # Wind
        optcashf_sheet.write_dynamic_array_formula('C96:AA96', '=\'Inputs and Outputs\'!C193:AA193', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B97',
            '=IF(OR(\'Inputs and Outputs\'!D179=5,\'Inputs and Outputs\'!D179=7),(B144-IF(\'Inputs and Outputs\'!D116="Yes",0.5*MIN(\'Inputs and Outputs\'!B116/100*B144,\'Inputs and Outputs\'!C116),0)),0)',
            o['text_format']
        )
        
        optcashf_sheet.write_formula(
            'B98',
            '=B97*(1-\'Inputs and Outputs\'!D180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D99:AA99', '=B98*D96:AA96', o['text_format'])
        optcashf_sheet.write_formula(
            'C99',
            '=B98*C96 + (B97*\'Inputs and Outputs\'!D180)',
            o['text_format']
        )
        
        # Battery
        optcashf_sheet.write_dynamic_array_formula('C101:AA101', '=\'Inputs and Outputs\'!C194:AA194', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B102',
            '=IF(OR(\'Inputs and Outputs\'!C179=5,\'Inputs and Outputs\'!C179=7),(B146-IF(\'Inputs and Outputs\'!D133="Yes",0.5*MIN(\'Inputs and Outputs\'!B133/100*B146,\'Inputs and Outputs\'!C133),0)),0)',
            o['text_format']
        )
        optcashf_sheet.write_formula(
            'B103',
            '=B102*(1-\'Inputs and Outputs\'!C180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D104:AA104', '=B103*D101:AA101', o['text_format'])
        optcashf_sheet.write_formula(
            'C104',
            '=B103*C101 + (B102*\'Inputs and Outputs\'!C180)',
            o['text_format']
        )
        
        # CHP
        optcashf_sheet.write_dynamic_array_formula('C106:AA106', '=\'Inputs and Outputs\'!C195:AA195', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B107',
            '=IF(OR(\'Inputs and Outputs\'!E179=5,\'Inputs and Outputs\'!E179=7),(B148-IF(\'Inputs and Outputs\'!D147="Yes",0.5*MIN(\'Inputs and Outputs\'!B147/100*B148,\'Inputs and Outputs\'!C147),0)),0)',
            o['text_format']
        )
        optcashf_sheet.write_formula(
            'B108',
            '=B107*(1-\'Inputs and Outputs\'!E180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D109:AA109', '=B108*D106:AA106', o['text_format'])
        optcashf_sheet.write_formula(
            'C109',
            '=B108*C106 + (B107*\'Inputs and Outputs\'!E180)',
            o['text_format']
        )
        
        # ABS CH
        optcashf_sheet.write_dynamic_array_formula('C111:AA111', '=\'Inputs and Outputs\'!C196:AA196', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B112',
            '=IF(OR(\'Inputs and Outputs\'!F179=5,\'Inputs and Outputs\'!F179=7),\'Inputs and Outputs\'!B57,0)',
            o['text_format']
        )
        optcashf_sheet.write_formula(
            'B113',
            '=B112*(1-\'Inputs and Outputs\'!F180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D114:AA114', '=B113*D111:AA111', o['text_format'])
        optcashf_sheet.write_formula(
            'C114',
            '=B113*C111 + (B112*\'Inputs and Outputs\'!F180)',
            o['text_format']
        )
        
        # HOT TES
        optcashf_sheet.write_dynamic_array_formula('C116:AA116', '=\'Inputs and Outputs\'!C197:AA197', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B117',
            '=IF(OR(\'Inputs and Outputs\'!G179=5,\'Inputs and Outputs\'!G179=7),\'Inputs and Outputs\'!B58,0)',
            o['text_format']
        )
        optcashf_sheet.write_formula(
            'B118',
            '=B117*(1-\'Inputs and Outputs\'!G180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D119:AA119', '=B118*D116:AA116', o['text_format'])
        optcashf_sheet.write_formula(
            'C119',
            '=B118*C116 + (B117*\'Inputs and Outputs\'!G180)',
            o['text_format']
        )
        
        # COLD TES
        optcashf_sheet.write_dynamic_array_formula('C121:AA121', '=\'Inputs and Outputs\'!C198:AA198', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B122',
            '=IF(OR(\'Inputs and Outputs\'!H179=5,\'Inputs and Outputs\'!H179=7),\'Inputs and Outputs\'!B59,0)',
            o['text_format']
        )
        optcashf_sheet.write_formula(
            'B123',
            '=B122*(1-\'Inputs and Outputs\'!H180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D124:AA124', '=B123*D121:AA121', o['text_format'])
        optcashf_sheet.write_formula(
            'C124',
            '=B123*C121 + (B122*\'Inputs and Outputs\'!H180)',
            o['text_format']
        )
        
        # STM Turb
        optcashf_sheet.write_dynamic_array_formula('C126:AA126', '=\'Inputs and Outputs\'!C199:AA199', o['text_format_decimal'])
        
        optcashf_sheet.write_formula(
            'B128',
            '=B127*(1-\'Inputs and Outputs\'!I180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D129:AA129', '=B128*D126:AA126', o['text_format'])
        optcashf_sheet.write_formula(
            'C129',
            '=B128*C126 + (B127*\'Inputs and Outputs\'!I180)',
            o['text_format']
        )
        
        # GHP
        optcashf_sheet.write_dynamic_array_formula('C131:AA131', '=\'Inputs and Outputs\'!C200:AA200', o['text_format_decimal'])
        
        optcashf_sheet.write_formula(
            'B132',
            '=IF(OR(\'Inputs and Outputs\'!J179=5,\'Inputs and Outputs\'!J179=7),(B150-IF(\'Inputs and Outputs\'!D164="Yes",0.5*MIN(\'Inputs and Outputs\'!B164/100*B150,\'Inputs and Outputs\'!C164),0)),0)',
            o['text_format']
        )
        optcashf_sheet.write_formula(
            'B133',
            '=B132*(1-\'Inputs and Outputs\'!J180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D134:AA134', '=B133*D131:AA131', o['text_format'])
        optcashf_sheet.write_formula(
            'C134',
            '=B133*C131 + (B132*\'Inputs and Outputs\'!J180)',
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
        optcashf_sheet.write_dynamic_array_formula('C138:AA138', '=((-1 * C10:AA10) + C94:AA94) * \'Inputs and Outputs\'!B93/100', o['text_format_2'])
        optcashf_sheet.write_dynamic_array_formula('C139:AA139', '=((-1 * C12:AA12) + C99:AA99) * \'Inputs and Outputs\'!B93/100', o['text_format_2'])
        
        ## federal ITC
        optcashf_sheet.write_formula('B142', '=\'Inputs and Outputs\'!B52-IF(\'Inputs and Outputs\'!E104="Yes",B32,0)-IF(\'Inputs and Outputs\'!E105="Yes",B33,0)-IF(\'Inputs and Outputs\'!E107="Yes",B36,0)-IF(\'Inputs and Outputs\'!E108="Yes",B37,0)-IF(\'Inputs and Outputs\'!E109="Yes",B38,0)', o['text_format'])
        optcashf_sheet.write_formula('B144', '=\'Inputs and Outputs\'!B53-IF(\'Inputs and Outputs\'!E121="Yes",B41,0)-IF(\'Inputs and Outputs\'!E122="Yes",B42,0)-IF(\'Inputs and Outputs\'!E124="Yes",B45,0)-IF(\'Inputs and Outputs\'!E125="Yes",B46,0)-IF(\'Inputs and Outputs\'!E126="Yes",B47,0)', o['text_format'])
        optcashf_sheet.write_formula('B146', '=\'Inputs and Outputs\'!B55-IF(\'Inputs and Outputs\'!E138="Yes",B50,0)-IF(\'Inputs and Outputs\'!E139="Yes",B51,0)-IF(\'Inputs and Outputs\'!E141="Yes",B54,0)-IF(\'Inputs and Outputs\'!E142="Yes",B55,0)', o['text_format'])
        optcashf_sheet.write_formula('B148', '=\'Inputs and Outputs\'!B56-IF(\'Inputs and Outputs\'!E152="Yes",B58,0)-IF(\'Inputs and Outputs\'!E153="Yes",B59,0)-IF(\'Inputs and Outputs\'!E155="Yes",B62,0)-IF(\'Inputs and Outputs\'!E156="Yes",B63,0)-IF(\'Inputs and Outputs\'!E157="Yes",B64,0)', o['text_format'])
        optcashf_sheet.write_formula('B150', '=\'Inputs and Outputs\'!B61-IF(\'Inputs and Outputs\'!E169="Yes",B70,0)-IF(\'Inputs and Outputs\'!E170="Yes",B71,0)-IF(\'Inputs and Outputs\'!E172="Yes",B74,0)-IF(\'Inputs and Outputs\'!E173="Yes",B75,0)-IF(\'Inputs and Outputs\'!E174="Yes",B76,0)', o['text_format'])
        
        optcashf_sheet.write_formula('C143', '=MIN(\'Inputs and Outputs\'!B99/100*B142,\'Inputs and Outputs\'!C99)')
        optcashf_sheet.write_formula('C145', '=MIN(\'Inputs and Outputs\'!B116/100*B144,\'Inputs and Outputs\'!C116)', o['text_format'])
        optcashf_sheet.write_formula('C147', '=MIN(\'Inputs and Outputs\'!B133/100*B146,\'Inputs and Outputs\'!C133)', o['text_format'])
        optcashf_sheet.write_formula('C149', '=MIN(\'Inputs and Outputs\'!B147/100*B148,\'Inputs and Outputs\'!C147)')
        optcashf_sheet.write_formula('C151', '=MIN(\'Inputs and Outputs\'!B164/100*B150,\'Inputs and Outputs\'!C162)', o['text_format'])
        optcashf_sheet.write_formula('C152', '=SUM(C143, C145, C147, C149, C151)', o['text_format_2'])
        
        # Total Cash Flows
        optcashf_sheet.write_formula('B155', '=-\'Inputs and Outputs\'!B51', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C156:AA156', '=(C27:AA27 - C28:AA28) + C28:AA28 * (1 - \'Inputs and Outputs\'!B93/100)', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('B157:AA157', '=(B86:AA86 * (1 - \'Inputs and Outputs\'!B93/100)) + B87:AA87', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C158:AA158', '=C135:AA135 * \'Inputs and Outputs\'!B93/100', o['text_format'])
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
    else:
        optcashf_sheet = proforma.add_worksheet('Third-party Owner Cash Flow')
        optcashf_sheet.write('A1', 'Third-party Cash Flow', o['header_format'])
        optcashf_sheet.write('A2', 'Operating Year', o['year_format'])
        optcashf_sheet.write('A4', 'Operating Expenses', o['subheader_format'])
        optcashf_sheet.write('A5', 'Operation and Maintenance (O&M)', o['text_format'])
        optcashf_sheet.write('A6', 'New PV fixed O&M cost', o['text_format_indent'])
        optcashf_sheet.write('A7', 'Existing PV fixed O&M cost', o['text_format'])
        optcashf_sheet.write('A8', 'Wind fixed O&M cost', o['text_format_indent'])
        optcashf_sheet.write('A9', 'Generator fixed O&M cost', o['text_format_indent'])
        optcashf_sheet.write('A10', 'Generator variable O&M cost', o['text_format_indent'])
        optcashf_sheet.write('A11', 'Battery kW replacement cost ', o['text_format_indent'])
        optcashf_sheet.write('A12', 'Battery kWh replacement cost ', o['text_format_indent'])
        optcashf_sheet.write('A13', 'CHP fixed O&M cost', o['text_format_indent'])
        optcashf_sheet.write('A14', 'CHP variable generation O&M cost', o['text_format_indent'])
        optcashf_sheet.write('A15', 'CHP runtime O&M cost', o['text_format_indent'])
        optcashf_sheet.write('A16', 'Absorption Chiller fixed O&M cost', o['text_format_indent'])
        optcashf_sheet.write('A17', 'Chilled water TES fixed O&M cost', o['text_format_indent'])
        optcashf_sheet.write('A18', 'Hot water TES fixed O&M cost', o['text_format_indent'])
        optcashf_sheet.write('A19', 'Steam turbine fixed O&M cost', o['text_format_indent'])
        optcashf_sheet.write('A20', 'Steam turbine variable generation O&M cost', o['text_format_indent'])
        optcashf_sheet.write('A21', 'GHP fixed O&M cost', o['text_format_indent'])
        optcashf_sheet.write('A22', 'Total operating expenses', o['text_format_2'])
        optcashf_sheet.write('A23', 'Tax deductible operating expenses', o['text_format_2'])
        
        optcashf_sheet.write('A25', 'Direct Cash Incentives', o['subheader_format'])
        optcashf_sheet.write('A26', 'PV Investment-based incentives (IBI)', o['text_format'])
        optcashf_sheet.write('A27', 'State IBI', o['text_format_indent'])
        optcashf_sheet.write('A28', 'Utility IBI', o['text_format_indent'])
        optcashf_sheet.write('A29', 'Total', o['text_format_indent'])
        optcashf_sheet.write('A30', 'PV Capacity-based incentives (CBI)', o['text_format'])
        optcashf_sheet.write('A31', 'Federal CBI', o['text_format_indent'])
        optcashf_sheet.write('A32', 'State CBI', o['text_format_indent'])
        optcashf_sheet.write('A33', 'Utility CBI', o['text_format_indent'])
        optcashf_sheet.write('A34', 'Total', o['text_format_indent'])
        optcashf_sheet.write('A35', 'Wind Investment-based incentives (IBI)', o['text_format'])
        optcashf_sheet.write('A36', 'State IBI', o['text_format_indent'])
        optcashf_sheet.write('A37', 'Utility IBI', o['text_format_indent'])
        optcashf_sheet.write('A38', 'Total', o['text_format_indent'])
        optcashf_sheet.write('A39', 'Wind Capacity-based incentives (CBI)', o['text_format'])
        optcashf_sheet.write('A40', 'Federal CBI', o['text_format_indent'])
        optcashf_sheet.write('A41', 'State CBI', o['text_format_indent'])
        optcashf_sheet.write('A42', 'Utility CBI', o['text_format_indent'])
        optcashf_sheet.write('A43', 'Total', o['text_format_indent'])
        optcashf_sheet.write('A44', 'Battery Investment-based incentives (IBI)', o['text_format'])
        optcashf_sheet.write('A45', 'State IBI', o['text_format_indent'])
        optcashf_sheet.write('A46', 'Utility IBI', o['text_format_indent'])
        optcashf_sheet.write('A47', 'Total', o['text_format_indent'])
        optcashf_sheet.write('A48', 'Battery Capacity-based incentives (CBI)', o['text_format'])
        optcashf_sheet.write('A49', 'Total Power (per kW) CBI', o['text_format_indent'])
        optcashf_sheet.write('A50', 'Total Storage Capacity (per kWh) CBI', o['text_format_indent'])
        optcashf_sheet.write('A51', 'Total', o['text_format_indent'])
        optcashf_sheet.write('A51', 'CHP Investment-based incentives (IBI)', o['text_format'])
        optcashf_sheet.write('A52', 'State IBI', o['text_format_indent'])
        optcashf_sheet.write('A53', 'Utility IBI', o['text_format_indent'])
        optcashf_sheet.write('A55', 'Total', o['text_format_indent'])
        optcashf_sheet.write('A56', 'CHP Capacity-based incentives (CBI)', o['text_format'])
        optcashf_sheet.write('A57', 'Federal CBI', o['text_format_indent'])
        optcashf_sheet.write('A58', 'State CBI', o['text_format_indent'])
        optcashf_sheet.write('A59', 'Utility CBI', o['text_format_indent'])
        optcashf_sheet.write('A60', 'Total', o['text_format_indent'])
        
        optcashf_sheet.write('A62', 'Total CBI and IBI', o['text_format'])
        
        optcashf_sheet.write('A64', 'GHP Investment-based incentives (IBI)', o['text_format'])
        optcashf_sheet.write('A65', 'State IBI', o['text_format_indent'])
        optcashf_sheet.write('A66', 'Utility IBI', o['text_format_indent'])
        optcashf_sheet.write('A67', 'Total', o['text_format_indent'])
        optcashf_sheet.write('A68', 'GHP Capacity-based incentives (CBI)', o['text_format'])
        optcashf_sheet.write('A69', 'Federal CBI', o['text_format_indent'])
        optcashf_sheet.write('A70', 'State CBI', o['text_format_indent'])
        optcashf_sheet.write('A71', 'Utility CBI', o['text_format_indent'])
        optcashf_sheet.write('A72', 'Total', o['text_format_indent'])
        
        optcashf_sheet.write('A74', 'Total CBI and IBI', o['text_format'])
        
        optcashf_sheet.write('A76', 'Production-based incentives (PBI)', o['text_format'])
        optcashf_sheet.write('A77', 'New PV Combined PBI', o['text_format_indent'])
        optcashf_sheet.write('A78', 'Existing PV Combined PBI', o['text_format_indent'])
        optcashf_sheet.write('A79', 'Wind Combined PBI', o['text_format_indent'])
        optcashf_sheet.write('A80', 'CHP Combined PBI', o['text_format_indent'])
        optcashf_sheet.write('A81', 'Total taxable cash incentives', o['text_format_2'])
        optcashf_sheet.write('A82', 'Total non-taxable cash incentives', o['text_format_2'])

        optcashf_sheet.write('A84', 'Capital Depreciation', o['subheader_format'])
        optcashf_sheet.write('A85', 'PV Depreciation, Commercial only', o['text_format'])
        optcashf_sheet.write('A86', 'Percentage', o['text_format_indent'])
        optcashf_sheet.write('A87', 'Bonus Basis', o['text_format_indent'])
        optcashf_sheet.write('A88', 'Basis', o['text_format_indent'])
        optcashf_sheet.write('A89', 'Amount', o['text_format_indent'])
        optcashf_sheet.write('A90', 'Wind Depreciation, Commercial only', o['text_format'])
        optcashf_sheet.write('A91', 'Percentage', o['text_format_indent'])
        optcashf_sheet.write('A92', 'Bonus Basis', o['text_format_indent'])
        optcashf_sheet.write('A93', 'Basis', o['text_format_indent'])
        optcashf_sheet.write('A94', 'Amount', o['text_format_indent'])
        optcashf_sheet.write('A95', 'Battery Depreciation, Commercial only', o['text_format'])
        optcashf_sheet.write('A96', 'Percentage', o['text_format_indent'])
        optcashf_sheet.write('A97', 'Bonus Basis', o['text_format_indent'])
        optcashf_sheet.write('A98', 'Basis', o['text_format_indent'])
        optcashf_sheet.write('A99', 'Amount', o['text_format_indent'])
        optcashf_sheet.write('A100', 'CHP Depreciation, Commercial only', o['text_format'])
        optcashf_sheet.write('A101', 'Percentage', o['text_format_indent'])
        optcashf_sheet.write('A102', 'Bonus Basis', o['text_format_indent'])
        optcashf_sheet.write('A103', 'Basis', o['text_format_indent'])
        optcashf_sheet.write('A104', 'Amount', o['text_format_indent'])
        optcashf_sheet.write('A105', 'Absorption Chiller Depreciation, Commercial only', o['text_format'])
        optcashf_sheet.write('A106', 'Percentage', o['text_format_indent'])
        optcashf_sheet.write('A107', 'Bonus Basis', o['text_format_indent'])
        optcashf_sheet.write('A108', 'Basis', o['text_format_indent'])
        optcashf_sheet.write('A109', 'Amount', o['text_format_indent'])
        optcashf_sheet.write('A110', 'Hot TES Depreciation, Commercial only', o['text_format'])
        optcashf_sheet.write('A111', 'Percentage', o['text_format_indent'])
        optcashf_sheet.write('A112', 'Bonus Basis', o['text_format_indent'])
        optcashf_sheet.write('A113', 'Basis', o['text_format_indent'])
        optcashf_sheet.write('A114', 'Amount', o['text_format_indent'])
        optcashf_sheet.write('A115', 'Cold TES Depreciation, Commercial only', o['text_format'])
        optcashf_sheet.write('A116', 'Percentage', o['text_format_indent'])
        optcashf_sheet.write('A117', 'Bonus Basis', o['text_format_indent'])
        optcashf_sheet.write('A118', 'Basis', o['text_format_indent'])
        optcashf_sheet.write('A119', 'Amount', o['text_format_indent'])
        optcashf_sheet.write('A120', 'Steam Turbine Depreciation, Commercial only', o['text_format'])
        optcashf_sheet.write('A121', 'Percentage', o['text_format_indent'])
        optcashf_sheet.write('A122', 'Bonus Basis', o['text_format_indent'])
        optcashf_sheet.write('A123', 'Basis', o['text_format_indent'])
        optcashf_sheet.write('A124', 'Amount', o['text_format_indent'])
        optcashf_sheet.write('A125', 'GHP Depreciation, Commercial only', o['text_format'])
        optcashf_sheet.write('A126', 'Percentage', o['text_format_indent'])
        optcashf_sheet.write('A127', 'Bonus Basis', o['text_format_indent'])
        optcashf_sheet.write('A128', 'Basis', o['text_format_indent'])
        optcashf_sheet.write('A129', 'Amount', o['text_format_indent'])
        optcashf_sheet.write('A130', 'Total depreciation', o['text_format_2'])
        
        optcashf_sheet.write('A132', 'Tax benefits for LCOE Calculations', o['subheader_format'])
        optcashf_sheet.write('A133', 'PV income tax savings, $', o['text_format_2'])
        optcashf_sheet.write('A134', 'Wind income tax savings, $', o['text_format_2'])
        
        optcashf_sheet.write('A136', 'Federal Investment Tax Credit', o['subheader_format'])
        optcashf_sheet.write('A137', 'Federal ITC basis: PV', o['text_format'])
        optcashf_sheet.write('A138', 'Federal ITC amount: PV', o['text_format'])
        optcashf_sheet.write('A139', 'Federal ITC basis: Wind', o['text_format'])
        optcashf_sheet.write('A140', 'Federal ITC amount: Wind', o['text_format'])
        optcashf_sheet.write('A141', 'Federal ITC basis: Battery', o['text_format'])
        optcashf_sheet.write('A142', 'Federal ITC amount: Battery', o['text_format'])
        optcashf_sheet.write('A143', 'Federal ITC basis: CHP', o['text_format'])
        optcashf_sheet.write('A144', 'Federal ITC amount: CHP', o['text_format'])
        optcashf_sheet.write('A145', 'Federal ITC basis: GHP', o['text_format'])
        optcashf_sheet.write('A146', 'Federal ITC amount: GHP', o['text_format'])
        optcashf_sheet.write('A147', 'Total Federal ITC', o['text_format_2'])

        optcashf_sheet.write('A149', 'Total Cash Flows', o['subheader_format'])
        optcashf_sheet.write('A150', 'Upfront Capital Cost', o['text_format'])
        optcashf_sheet.write('A151', 'Operating expenses, after-tax', o['text_format'])
        optcashf_sheet.write('A152', 'Total Cash incentives, after-tax', o['text_format'])
        optcashf_sheet.write('A153', 'Depreciation Tax Shield', o['text_format'])
        optcashf_sheet.write('A154', 'Investment Tax Credit', o['text_format'])
        optcashf_sheet.write('A155', 'Free Cash Flow before income', o['text_format_2'])
        optcashf_sheet.write('A156', 'Discounted Cash Flow', o['text_format_2'])
        optcashf_sheet.write('A157', 'Third-party Owner Net Present Cost', o['standalone_bold_text_format'])
        optcashf_sheet.write('A158', 'Capital Recovery Factor', o['text_format'])
        optcashf_sheet.write('A159', 'Income from Host', o['text_format'])
        optcashf_sheet.write('A160', 'Income from Host, after-tax', o['text_format'])
        optcashf_sheet.write('A161', 'Discounted Income from Host', o['text_format'])
        optcashf_sheet.write('A162', 'NPV of Income from Host', o['text_format_2'])
        optcashf_sheet.write('A163', 'Free Cash Flow after income', o['text_format_2'])
        optcashf_sheet.write('A164', 'Cumulative Free Cash Flow after income', o['standalone_bold_text_format'])

        # column widths
        optcashf_sheet.set_column('A:A', 31.75)
        optcashf_sheet.set_column('B:AA', 10.38)
        optcashf_sheet.freeze_panes(2,0)
        
        # Static fields
        for idx in range(1,27):
            optcashf_sheet.write(base_upper_case_letters[idx]+'2', idx-1, o['year_format'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'4', None, o['subheader_format'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'25', None, o['subheader_format'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'84', None, o['subheader_format'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'132', None, o['subheader_format'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'136', None, o['subheader_format'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'149', None, o['subheader_format'])

            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'22', None, o['text_format_2'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'23', None, o['text_format_2'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'81', None, o['text_format_2'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'82', None, o['text_format_2'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'130', None, o['text_format_2'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'133', None, o['text_format_2'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'134', None, o['text_format_2'])
            
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'147', None, o['text_format_2'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'155', None, o['text_format_2'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'156', None, o['text_format_2'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'162', None, o['text_format_2'])
            optcashf_sheet.write_blank(base_upper_case_letters[idx]+'163', None, o['text_format_2'])

        optcashf_sheet.write_dynamic_array_formula('C6:AA6', '=-\'Inputs and Outputs\'!B63 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2 * (\'Inputs and Outputs\'!B3 - \'Inputs and Outputs\'!B4)', o['text_format']) # Only NEW PV capacity
        optcashf_sheet.write_dynamic_array_formula('C7:AA7', '=-\'Inputs and Outputs\'!B63 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2 * (0)', o['text_format']) # existing PV
        optcashf_sheet.write_dynamic_array_formula('C8:AA8', '=-\'Inputs and Outputs\'!B64 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2 * (\'Inputs and Outputs\'!B7)', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C9:AA9', '=-\'Inputs and Outputs\'!B65 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2 * (0)', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C10:AA10', '=-\'Inputs and Outputs\'!B66 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2 * (\'Inputs and Outputs\'!B30)', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C11:AA11', '=-IF(C2:AA2 = \'Inputs and Outputs\'!B70, \'Inputs and Outputs\'!B11 * \'Inputs and Outputs\'!B69, 0)', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C12:AA12', '=-IF(C2:AA2 = \'Inputs and Outputs\'!B70, \'Inputs and Outputs\'!B12 * \'Inputs and Outputs\'!B71, 0)', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C13:AA13', '=-\'Inputs and Outputs\'!B73 * \'Inputs and Outputs\'!B13 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C14:AA14', '=-\'Inputs and Outputs\'!B74 * \'Inputs and Outputs\'!B31 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C15:AA15', '=-\'Inputs and Outputs\'!B75 * \'Inputs and Outputs\'!B13 * \'Inputs and Outputs\'!B32 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C16:AA16', '=-\'Inputs and Outputs\'!B76 * \'Inputs and Outputs\'!B14 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C17:AA17', '=-\'Inputs and Outputs\'!B77 * \'Inputs and Outputs\'!B15 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C18:AA18', '=-\'Inputs and Outputs\'!B78 * \'Inputs and Outputs\'!B16 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C19:AA19', '=-\'Inputs and Outputs\'!B79 * \'Inputs and Outputs\'!B17 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C20:AA20', '=-\'Inputs and Outputs\'!B80 * \'Inputs and Outputs\'!B33 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C21:AA21', '=-\'Inputs and Outputs\'!B81 * (1+\'Inputs and Outputs\'!B85/100)^C2:AA2', o['text_format'])

        for idx in range(2, 27):
            col = base_upper_case_letters[idx] # C through AA
            optcashf_sheet.write_formula(col+'22', '=SUM('+col+'5:'+col+'21)', o['text_format_2'])
            optcashf_sheet.write_formula(col+'23', '=IF(\'Inputs and Outputs\'!B93 > 0, '+col+'22, 0)', o['text_format_2'])

        # PV direct cash incentives
        optcashf_sheet.write_formula('B27', '=MIN((\'Inputs and Outputs\'!B104/100)*(\'Inputs and Outputs\'!B52 - B28 - B33),\'Inputs and Outputs\'!C104)', o['text_format'])
        optcashf_sheet.write_formula('B28', '=MIN((\'Inputs and Outputs\'!B105/100)*\'Inputs and Outputs\'!B52,\'Inputs and Outputs\'!C105)', o['text_format'])
        optcashf_sheet.write_formula('B29', '=SUM(B27,B28)', o['text_format'])
        optcashf_sheet.write_blank('B30', None, o['text_format'])
        optcashf_sheet.write_formula('B31', '=MIN(\'Inputs and Outputs\'!B107*\'Inputs and Outputs\'!B3*1000,\'Inputs and Outputs\'!C107)', o['text_format'])
        optcashf_sheet.write_formula('B32', '=MIN(\'Inputs and Outputs\'!B108*\'Inputs and Outputs\'!B3*1000,\'Inputs and Outputs\'!C108)', o['text_format'])
        optcashf_sheet.write_formula('B33', '=MIN(\'Inputs and Outputs\'!B109*\'Inputs and Outputs\'!B3*1000,\'Inputs and Outputs\'!C109)', o['text_format'])
        optcashf_sheet.write_formula('B34', '=SUM(B31,B32,B33)', o['text_format'])
        optcashf_sheet.write_blank('B35', None, o['text_format'])
        # Wind direct cash incentives
        optcashf_sheet.write_formula('B36', '=MIN((\'Inputs and Outputs\'!B121/100)*(\'Inputs and Outputs\'!B53 - B42 - B37),\'Inputs and Outputs\'!C121)', o['text_format'])
        optcashf_sheet.write_formula('B37', '=MIN((\'Inputs and Outputs\'!B122/100)*\'Inputs and Outputs\'!B53,\'Inputs and Outputs\'!C122)', o['text_format'])
        optcashf_sheet.write_formula('B38', '=SUM(B36,B37)', o['text_format'])
        optcashf_sheet.write_blank('B39', None, o['text_format'])
        optcashf_sheet.write_formula('B40', '=MIN(\'Inputs and Outputs\'!B124*\'Inputs and Outputs\'!B7*1000,\'Inputs and Outputs\'!C124)', o['text_format'])
        optcashf_sheet.write_formula('B41', '=MIN(\'Inputs and Outputs\'!B125*\'Inputs and Outputs\'!B7*1000,\'Inputs and Outputs\'!C125)', o['text_format'])
        optcashf_sheet.write_formula('B42', '=MIN(\'Inputs and Outputs\'!B126*\'Inputs and Outputs\'!B7*1000,\'Inputs and Outputs\'!C126)', o['text_format'])
        optcashf_sheet.write_formula('B43', '=SUM(B40,B41,B42)', o['text_format'])
        optcashf_sheet.write_blank('B44', None, o['text_format'])
        # Battery direct cash incentives
        optcashf_sheet.write_formula('B45', '=MIN((\'Inputs and Outputs\'!B138/100)*(\'Inputs and Outputs\'!B55),\'Inputs and Outputs\'!C138)', o['text_format'])
        optcashf_sheet.write_formula('B46', '=MIN((\'Inputs and Outputs\'!B139/100)*\'Inputs and Outputs\'!B55,\'Inputs and Outputs\'!C139)', o['text_format'])
        optcashf_sheet.write_formula('B47', '=SUM(B45,B46)', o['text_format'])
        optcashf_sheet.write_blank('B48', None, o['text_format'])
        optcashf_sheet.write_formula('B49', '=MIN(\'Inputs and Outputs\'!B141*\'Inputs and Outputs\'!B11*1000,\'Inputs and Outputs\'!C141)', o['text_format'])
        optcashf_sheet.write_formula('B50', '=MIN(\'Inputs and Outputs\'!B142*\'Inputs and Outputs\'!B12*1000,\'Inputs and Outputs\'!C142)', o['text_format'])
        optcashf_sheet.write_formula('B51', '=SUM(B49,B50)', o['text_format'])
        optcashf_sheet.write_blank('B52', None, o['text_format'])
        # CHP direct cash incentives
        optcashf_sheet.write_formula('B53', '=MIN((\'Inputs and Outputs\'!B152/100)*(\'Inputs and Outputs\'!B56 - B59 - B64),\'Inputs and Outputs\'!C152)', o['text_format'])
        optcashf_sheet.write_formula('B54', '=MIN((\'Inputs and Outputs\'!B153/100)*\'Inputs and Outputs\'!B56,\'Inputs and Outputs\'!C153)', o['text_format'])
        optcashf_sheet.write_formula('B55', '=SUM(B53,B54)', o['text_format'])
        optcashf_sheet.write_blank('B56', None, o['text_format'])
        optcashf_sheet.write_formula('B57', '=MIN(\'Inputs and Outputs\'!B155*\'Inputs and Outputs\'!B13*1000,\'Inputs and Outputs\'!C155)', o['text_format'])
        optcashf_sheet.write_formula('B58', '=MIN(\'Inputs and Outputs\'!B156*\'Inputs and Outputs\'!B13*1000,\'Inputs and Outputs\'!C156)', o['text_format'])
        optcashf_sheet.write_formula('B59', '=MIN(\'Inputs and Outputs\'!B157*\'Inputs and Outputs\'!B13*1000,\'Inputs and Outputs\'!C157)', o['text_format'])
        optcashf_sheet.write_formula('B60', '=SUM(B57,B58,B59)', o['text_format'])
        
        optcashf_sheet.write_formula('B62', '=SUM(B29,B34,B38,B43,B47,B51,B55,B60)', o['text_format'])
        
        optcashf_sheet.write_formula('B64', '=MIN((\'Inputs and Outputs\'!B169/100)*(\'Inputs and Outputs\'!B61 - B71 - B76),\'Inputs and Outputs\'!C169)', o['text_format'])
        optcashf_sheet.write_formula('B65', '=MIN((\'Inputs and Outputs\'!B170/100)*\'Inputs and Outputs\'!B61,\'Inputs and Outputs\'!C170)', o['text_format'])
        optcashf_sheet.write_formula('B66', '=SUM(B64,B65)', o['text_format'])
        optcashf_sheet.write_blank('B67', None, o['text_format'])
        optcashf_sheet.write_formula('B68', '=MIN(\'Inputs and Outputs\'!B172*\'Inputs and Outputs\'!B18,\'Inputs and Outputs\'!C172)', o['text_format'])
        optcashf_sheet.write_formula('B69', '=MIN(\'Inputs and Outputs\'!B173*\'Inputs and Outputs\'!B18,\'Inputs and Outputs\'!C173)', o['text_format'])
        optcashf_sheet.write_formula('B70', '=MIN(\'Inputs and Outputs\'!B174*\'Inputs and Outputs\'!B18,\'Inputs and Outputs\'!C174)', o['text_format'])
        optcashf_sheet.write_formula('B71', '=SUM(B68,B69,B70)', o['text_format'])
        optcashf_sheet.write_blank('B72', None, o['text_format'])
        
        optcashf_sheet.write_formula('B74', '=SUM(B29,B34,B38,B43,B47,B51,B55,B60,B67,B72)', o['text_format'])

        for idx in range(2, 27):
            col = base_upper_case_letters[idx] # C through AA
            expcol = base_upper_case_letters[idx-1] # B through Z for exponent
            
            optcashf_sheet.write_formula(
                col+'77',
                '=IF('+str(idx-2)+' < \'Inputs and Outputs\'!E113, MIN(\'Inputs and Outputs\'!B113 * (\'Inputs and Outputs\'!'+col+'186 - \'Inputs and Outputs\'!'+col+'187), \'Inputs and Outputs\'!C113 * (1 - \'Inputs and Outputs\'!B5/100)^'+str(idx-2)+'), 0)',
                o['text_format']
            )
        
            optcashf_sheet.write_formula(
                col+'78',
                '=IF('+str(idx-2)+' < \'Inputs and Outputs\'!E113, MIN(\'Inputs and Outputs\'!B113 * (\'Inputs and Outputs\'!'+col+'187), \'Inputs and Outputs\'!C113 * (1 - \'Inputs and Outputs\'!B5/100)^'+str(idx-2)+'), 0)',
                o['text_format']
            )
            
            optcashf_sheet.write_formula(
                col+'79',
                '=IF('+str(idx-2)+' < \'Inputs and Outputs\'!E130, MIN(\'Inputs and Outputs\'!B130 * \'Inputs and Outputs\'!'+col+'188, \'Inputs and Outputs\'!C130), 0)',
                o['text_format']
            )
        
            optcashf_sheet.write_formula(
                col+'80',
                '=IF('+str(idx-2)+' < \'Inputs and Outputs\'!E161, MIN(\'Inputs and Outputs\'!B161 * \'Inputs and Outputs\'!'+col+'190, \'Inputs and Outputs\'!C161), 0)',
                o['text_format']
            )
        
            optcashf_sheet.write_formula(
                col+'81',
                '=IF(\'Inputs and Outputs\'!D111="Yes", '+col+'82, 0) + IF(\'Inputs and Outputs\'!D113="Yes", '+col+'83, 0) + IF(\'Inputs and Outputs\'!D130="Yes", '+col+'84, 0)+IF(\'Inputs and Outputs\'!D160="Yes", '+col+'85, 0)',
                o['text_format_2']
            )
        
            optcashf_sheet.write_formula(
                col+'82',
                '=IF(\'Inputs and Outputs\'!D113="No", '+col+'82, 0) + IF(\'Inputs and Outputs\'!D113="No", '+col+'83, 0)+IF(\'Inputs and Outputs\'!D130="No", '+col+'84, 0)+IF(\'Inputs and Outputs\'!D161="No", '+col+'85, 0)',
                o['text_format_2']
            )
        
        optcashf_sheet.write_formula(
            'B81',
            '=IF(\'Inputs and Outputs\'!D106="Yes", B32, 0) + IF(\'Inputs and Outputs\'!D107="Yes", B33, 0) + IF(\'Inputs and Outputs\'!D109="Yes", B36,0) + IF(\'Inputs and Outputs\'!D110="Yes", B37, 0) + IF(\'Inputs and Outputs\'!D111="Yes", B38, 0)+IF(\'Inputs and Outputs\'!D140="Yes", B50, 0)+IF(\'Inputs and Outputs\'!D141="Yes", B51, 0)+IF(\'Inputs and Outputs\'!D143="Yes", B54, 0)+IF(\'Inputs and Outputs\'!D144="Yes", B55, 0)+IF(\'Inputs and Outputs\'!D123="Yes", B41, 0)+IF(\'Inputs and Outputs\'!D124="Yes", B42, 0)+IF(\'Inputs and Outputs\'!D127="Yes", B45, 0)+IF(\'Inputs and Outputs\'!D126="Yes", B46, 0)+IF(\'Inputs and Outputs\'!D128="Yes", B47, 0)+IF(\'Inputs and Outputs\'!D154="Yes", B58, 0)+IF(\'Inputs and Outputs\'!D155="Yes", B59, 0)+IF(\'Inputs and Outputs\'!D158="Yes", B62, 0)+IF(\'Inputs and Outputs\'!D157="Yes", B63, 0)+IF(\'Inputs and Outputs\'!D159="Yes", B64, 0)+IF(\'Inputs and Outputs\'!D171="Yes", B70, 0)+IF(\'Inputs and Outputs\'!D172="Yes", B71, 0)+IF(\'Inputs and Outputs\'!D175="Yes", B74, 0)+IF(\'Inputs and Outputs\'!D174="Yes", B75, 0)+IF(\'Inputs and Outputs\'!D176="Yes", B76, 0)',
            o['text_format_2']
        )
        optcashf_sheet.write_formula(
            'B82',
            '=IF(\'Inputs and Outputs\'!D106="No", B32, 0) + IF(\'Inputs and Outputs\'!D107="No", B33, 0) + IF(\'Inputs and Outputs\'!D109="No", B36,0) + IF(\'Inputs and Outputs\'!D110="No", B37, 0) + IF(\'Inputs and Outputs\'!D111="No", B38, 0) + IF(\'Inputs and Outputs\'!D113="No", B82, 0) + IF(\'Inputs and Outputs\'!D113="No", B83, 0)+IF(\'Inputs and Outputs\'!D140="No", B50, 0)+IF(\'Inputs and Outputs\'!D141="No", B51, 0)+IF(\'Inputs and Outputs\'!D143="No", B54, 0)+IF(\'Inputs and Outputs\'!D144="No", B55, 0)+IF(\'Inputs and Outputs\'!D123="No", B41, 0)+IF(\'Inputs and Outputs\'!D124="No", B42, 0)+IF(\'Inputs and Outputs\'!D127="No", B45, 0)+IF(\'Inputs and Outputs\'!D126="No", B46, 0)+IF(\'Inputs and Outputs\'!D128="No", B47, 0)+IF(\'Inputs and Outputs\'!D130="No", B84, 0)+IF(\'Inputs and Outputs\'!D154="No", B58, 0)+IF(\'Inputs and Outputs\'!D155="No", B59, 0)+IF(\'Inputs and Outputs\'!D158="No", B62, 0)+IF(\'Inputs and Outputs\'!D157="No", B63, 0)+IF(\'Inputs and Outputs\'!D159="No", B64, 0)+IF(\'Inputs and Outputs\'!D161="No", B85, 0)+IF(\'Inputs and Outputs\'!D171="No", B70, 0)+IF(\'Inputs and Outputs\'!D172="No", B71, 0)+IF(\'Inputs and Outputs\'!D175="No", B74, 0)+IF(\'Inputs and Outputs\'!D174="No", B75, 0)+IF(\'Inputs and Outputs\'!D176="No", B76, 0)',
            o['text_format_2']
        )

        ## Capital depreciation
        # PV
        optcashf_sheet.write_dynamic_array_formula('C86:AA86', '=\'Inputs and Outputs\'!C192:AA192', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B87',
            '=IF(OR(\'Inputs and Outputs\'!B179=5,\'Inputs and Outputs\'!B179=7),(B137-IF(\'Inputs and Outputs\'!D99="Yes",0.5*MIN(\'Inputs and Outputs\'!B99/100*B137,\'Inputs and Outputs\'!C99),0)),0)',
            o['text_format']
        )
        
        optcashf_sheet.write_formula(
            'B88',
            '=B87*(1-\'Inputs and Outputs\'!B180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D89:AA89', '=B88*D86:AA86', o['text_format'])
        optcashf_sheet.write_formula(
            'C89',
            '=B88*C86 + (B87*\'Inputs and Outputs\'!B180)',
            o['text_format']
        )
        
        # Wind
        optcashf_sheet.write_dynamic_array_formula('C91:AA91', '=\'Inputs and Outputs\'!C193:AA193', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B92',
            '=IF(OR(\'Inputs and Outputs\'!D179=5,\'Inputs and Outputs\'!D179=7),(B139-IF(\'Inputs and Outputs\'!D116="Yes",0.5*MIN(\'Inputs and Outputs\'!B116/100*B139,\'Inputs and Outputs\'!C116),0)),0)',
            o['text_format']
        )
        
        optcashf_sheet.write_formula(
            'B93',
            '=B92*(1-\'Inputs and Outputs\'!D180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D94:AA94', '=B93*D91:AA91', o['text_format'])
        optcashf_sheet.write_formula(
            'C94',
            '=B93*C91 + (B92*\'Inputs and Outputs\'!D180)',
            o['text_format']
        )
        
        # Battery
        optcashf_sheet.write_dynamic_array_formula('C96:AA96', '=\'Inputs and Outputs\'!C194:AA194', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B97',
            '=IF(OR(\'Inputs and Outputs\'!C179=5,\'Inputs and Outputs\'!C179=7),(B141-IF(\'Inputs and Outputs\'!D133="Yes",0.5*MIN(\'Inputs and Outputs\'!B133/100*B141,\'Inputs and Outputs\'!C133),0)),0)',
            o['text_format']
        )
        optcashf_sheet.write_formula(
            'B98',
            '=B97*(1-\'Inputs and Outputs\'!C180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D99:AA99', '=B98*D96:AA96', o['text_format'])
        optcashf_sheet.write_formula(
            'C99',
            '=B98*C96 + (B97*\'Inputs and Outputs\'!C180)',
            o['text_format']
        )
        
        # CHP
        optcashf_sheet.write_dynamic_array_formula('C101:AA101', '=\'Inputs and Outputs\'!C195:AA195', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B102',
            '=IF(OR(\'Inputs and Outputs\'!E179=5,\'Inputs and Outputs\'!E179=7),(B143-IF(\'Inputs and Outputs\'!D147="Yes",0.5*MIN(\'Inputs and Outputs\'!B147/100*B143,\'Inputs and Outputs\'!C147),0)),0)',
            o['text_format']
        )
        optcashf_sheet.write_formula(
            'B103',
            '=B102*(1-\'Inputs and Outputs\'!E180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D104:AA104', '=B103*D101:AA101', o['text_format'])
        optcashf_sheet.write_formula(
            'C104',
            '=B103*C101 + (B102*\'Inputs and Outputs\'!E180)',
            o['text_format']
        )
        
        # ABS CH
        optcashf_sheet.write_dynamic_array_formula('C106:AA106', '=\'Inputs and Outputs\'!C196:AA196', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B107',
            '=IF(OR(\'Inputs and Outputs\'!F179=5,\'Inputs and Outputs\'!F179=7),\'Inputs and Outputs\'!B57,0)',
            o['text_format']
        )
        optcashf_sheet.write_formula(
            'B108',
            '=B107*(1-\'Inputs and Outputs\'!F180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D109:AA109', '=B108*D106:AA106', o['text_format'])
        optcashf_sheet.write_formula(
            'C109',
            '=B108*C106 + (B107*\'Inputs and Outputs\'!F180)',
            o['text_format']
        )
        
        # HOT TES
        optcashf_sheet.write_dynamic_array_formula('C111:AA111', '=\'Inputs and Outputs\'!C197:AA197', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B112',
            '=IF(OR(\'Inputs and Outputs\'!G179=5,\'Inputs and Outputs\'!G179=7),\'Inputs and Outputs\'!B58,0)',
            o['text_format']
        )
        optcashf_sheet.write_formula(
            'B113',
            '=B112*(1-\'Inputs and Outputs\'!G180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D114:AA114', '=B113*D111:AA111', o['text_format'])
        optcashf_sheet.write_formula(
            'C114',
            '=B113*C111 + (B112*\'Inputs and Outputs\'!G180)',
            o['text_format']
        )
        
        # COLD TES
        optcashf_sheet.write_dynamic_array_formula('C116:AA116', '=\'Inputs and Outputs\'!C198:AA198', o['text_format_decimal'])
        optcashf_sheet.write_formula(
            'B117',
            '=IF(OR(\'Inputs and Outputs\'!H179=5,\'Inputs and Outputs\'!H179=7),\'Inputs and Outputs\'!B59,0)',
            o['text_format']
        )
        optcashf_sheet.write_formula(
            'B118',
            '=B117*(1-\'Inputs and Outputs\'!H180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D119:AA119', '=B118*D116:AA116', o['text_format'])
        optcashf_sheet.write_formula(
            'C119',
            '=B118*C116 + (B117*\'Inputs and Outputs\'!H180)',
            o['text_format']
        )
        
        # STM Turb
        optcashf_sheet.write_dynamic_array_formula('C121:AA121', '=\'Inputs and Outputs\'!C199:AA199', o['text_format_decimal'])
        
        optcashf_sheet.write_formula(
            'B123',
            '=B122*(1-\'Inputs and Outputs\'!I180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D124:AA124', '=B123*D121:AA121', o['text_format'])
        optcashf_sheet.write_formula(
            'C124',
            '=B123*C121 + (B122*\'Inputs and Outputs\'!I180)',
            o['text_format']
        )
        
        # GHP
        optcashf_sheet.write_dynamic_array_formula('C126:AA126', '=\'Inputs and Outputs\'!C200:AA200', o['text_format_decimal'])
        
        optcashf_sheet.write_formula(
            'B127',
            '=IF(OR(\'Inputs and Outputs\'!J179=5,\'Inputs and Outputs\'!J179=7),(B145-IF(\'Inputs and Outputs\'!D164="Yes",0.5*MIN(\'Inputs and Outputs\'!B164/100*B145,\'Inputs and Outputs\'!C164),0)),0)',
            o['text_format']
        )
        optcashf_sheet.write_formula(
            'B128',
            '=B127*(1-\'Inputs and Outputs\'!J180)',
            o['text_format']
        )
        optcashf_sheet.write_dynamic_array_formula('D129:AA129', '=B128*D126:AA126', o['text_format'])
        optcashf_sheet.write_formula(
            'C129',
            '=B128*C126 + (B127*\'Inputs and Outputs\'!J180)',
            o['text_format']
        )
        
        for idx in range(2, 27):
            col = base_upper_case_letters[idx] # C through AA
            
            optcashf_sheet.write_formula(
                col+'130',
                '=SUM('+col+'94,'+col+'99,'+col+'104,'+col+'109,'+col+'114,'+col+'119,'+col+'124,'+col+'129,'+col+'89)',
                o['text_format_2']
            )

        # Tax benefits for LCOE calculations
        optcashf_sheet.write_dynamic_array_formula('C133:AA133', '=((-1 * C6:AA6) + C89:AA89) * \'Inputs and Outputs\'!B93/100', o['text_format_2'])
        optcashf_sheet.write_dynamic_array_formula('C134:AA134', '=((-1 * C8:AA8) + C94:AA94) * \'Inputs and Outputs\'!B93/100', o['text_format_2'])
        
        ## federal ITC
        optcashf_sheet.write_formula('B137', '=\'Inputs and Outputs\'!B52-IF(\'Inputs and Outputs\'!E104="Yes",B27,0)-IF(\'Inputs and Outputs\'!E105="Yes",B28,0)-IF(\'Inputs and Outputs\'!E107="Yes",B31,0)-IF(\'Inputs and Outputs\'!E108="Yes",B32,0)-IF(\'Inputs and Outputs\'!E109="Yes",B33,0)', o['text_format'])
        optcashf_sheet.write_formula('B139', '=\'Inputs and Outputs\'!B53-IF(\'Inputs and Outputs\'!E121="Yes",B36,0)-IF(\'Inputs and Outputs\'!E122="Yes",B37,0)-IF(\'Inputs and Outputs\'!E124="Yes",B40,0)-IF(\'Inputs and Outputs\'!E125="Yes",B41,0)-IF(\'Inputs and Outputs\'!E126="Yes",B42,0)', o['text_format'])
        optcashf_sheet.write_formula('B141', '=\'Inputs and Outputs\'!B55-IF(\'Inputs and Outputs\'!E138="Yes",B45,0)-IF(\'Inputs and Outputs\'!E139="Yes",B46,0)-IF(\'Inputs and Outputs\'!E141="Yes",B49,0)-IF(\'Inputs and Outputs\'!E142="Yes",B50,0)', o['text_format'])
        optcashf_sheet.write_formula('B143', '=\'Inputs and Outputs\'!B56-IF(\'Inputs and Outputs\'!E152="Yes",B53,0)-IF(\'Inputs and Outputs\'!E153="Yes",B54,0)-IF(\'Inputs and Outputs\'!E155="Yes",B57,0)-IF(\'Inputs and Outputs\'!E156="Yes",B58,0)-IF(\'Inputs and Outputs\'!E157="Yes",B59,0)', o['text_format'])
        optcashf_sheet.write_formula('B145', '=\'Inputs and Outputs\'!B61-IF(\'Inputs and Outputs\'!E169="Yes",B65,0)-IF(\'Inputs and Outputs\'!E170="Yes",B66,0)-IF(\'Inputs and Outputs\'!E172="Yes",B69,0)-IF(\'Inputs and Outputs\'!E173="Yes",B70,0)-IF(\'Inputs and Outputs\'!E174="Yes",B71,0)', o['text_format'])
        
        optcashf_sheet.write_formula('C138', '=MIN(\'Inputs and Outputs\'!B99/100*B137,\'Inputs and Outputs\'!C99)')
        optcashf_sheet.write_formula('C140', '=MIN(\'Inputs and Outputs\'!B116/100*B139,\'Inputs and Outputs\'!C116)', o['text_format'])
        optcashf_sheet.write_formula('C142', '=MIN(\'Inputs and Outputs\'!B133/100*B141,\'Inputs and Outputs\'!C133)', o['text_format'])
        optcashf_sheet.write_formula('C144', '=MIN(\'Inputs and Outputs\'!B147/100*B143,\'Inputs and Outputs\'!C147)')
        optcashf_sheet.write_formula('C146', '=MIN(\'Inputs and Outputs\'!B164/100*B145,\'Inputs and Outputs\'!C162)', o['text_format'])
        optcashf_sheet.write_formula('C147', '=SUM(C138, C140, C142, C144, C146)', o['text_format_2'])

        # Total Cash Flows
        optcashf_sheet.write_formula('B150', '=-\'Inputs and Outputs\'!B51', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C151:AA151', '=(C22:AA22 - C23:AA23) + C23:AA23 * (1 - \'Inputs and Outputs\'!B93/100)', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('B152:AA152', '=(B81:AA81 * (1 - \'Inputs and Outputs\'!B93/100)) + B82:AA82', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C153:AA153', '=C130:AA130 * \'Inputs and Outputs\'!B93/100', o['text_format'])
        optcashf_sheet.write_dynamic_array_formula('C154:AA154', '=C147:AA147', o['text_format'])
        
        optcashf_sheet.write_dynamic_array_formula('C155:AA155', '=C151:AA151 + C152:AA152 + C153:AA153 + C154:AA154', o['text_format_2'])
        optcashf_sheet.write_dynamic_array_formula('C156:AA156', '=C155:AA155 / (1 + \'Inputs and Outputs\'!B89/100)^C2:AA2', o['text_format_2'])
        
        # GHP residual value subtracted from capital costs
        ghxresidualvalue = get_value('outputs','GHP','ghx_residual_value_present_value')
        # print(ghxresidualvalue)
        optcashf_sheet.write_formula('B155', '=B150+B152+'+str(ghxresidualvalue), o['text_format_2'])
        optcashf_sheet.write_formula('B156', '=B150+B152+'+str(ghxresidualvalue), o['text_format_2'])    
        optcashf_sheet.write_formula('B157', '=SUM(B156:AA156)', o['standalone_bold_text_format'])

        optcashf_sheet.write_formula('B158', '=\'Inputs and Outputs\'!B89/100 * POWER(1 + \'Inputs and Outputs\'!B89/100, \'Inputs and Outputs\'!B84) / (POWER(1 + \'Inputs and Outputs\'!B89/100, \'Inputs and Outputs\'!B84) - 1) / (1 - \'Inputs and Outputs\'!B93/100)')
        
        optcashf_sheet.write_array_formula('C159:AA159', '=-B157 * B158', o['text_format_2'])    
        optcashf_sheet.write_array_formula('C160:AA160', '= C159 * (1 - \'Inputs and Outputs\'!B93/100)', o['standalone_bold_text_format'])
        optcashf_sheet.write_dynamic_array_formula('C161:AA161', '=C160:AA160 /  (1 + \'Inputs and Outputs\'!B89/100)^C2:AA2', o['text_format_2'])
        optcashf_sheet.write_formula('B162', '=SUM(C161:AA161)', o['text_format_2'])    
        
        optcashf_sheet.write_formula('B163', '=B155', o['standalone_bold_text_format'])
        optcashf_sheet.write_dynamic_array_formula('C163:AA163', '=C155:AA155 + C160:AA160', o['standalone_bold_text_format'])
        
        optcashf_sheet.write_formula('B164', '=B163', o['standalone_bold_text_format'])
        optcashf_sheet.write_array_formula('C164:AA164', '=C163:AA163 + B164:Z164', o['standalone_bold_text_format'])
        
        # for cell in ['B139', 'B135', 'B27', 'B28']:
        #     optcashf_sheet.write_blank(cell, None, o['text_format_2'])

    ## BAU SHEET
    if results['inputs']['Financial']['third_party_ownership'] == False:
        baucashf_sheet = proforma.add_worksheet('BAU Cash Flow')
        baucashf_sheet.write('A1', 'BAU Cash Flow', o['header_format'])
    else:
        baucashf_sheet = proforma.add_worksheet('Host Cash Flow')
        baucashf_sheet.write('A1', 'Host Cash Flow', o['header_format'])


    baucashf_sheet.write('A2', 'Operating Expenses', o['year_format'])
    baucashf_sheet.write('A3', 'Business as Usual electricity bill ($)', o['text_format'])
    baucashf_sheet.write('A4', 'Business as Usual export credits ($)', o['text_format'])

    for idx in range(0,26):
        baucashf_sheet.write(1,1+idx, idx, o['year_format'])

    baucashf_sheet.write_dynamic_array_formula('C3:AA3', '=-\'Inputs and Outputs\'!B22 * (1 + \'Inputs and Outputs\'!B86/100)^C2:AA2', o['text_format'])
        
    baucashf_sheet.write_dynamic_array_formula('C4:AA4', '=\'Inputs and Outputs\'!B23 * (1 + \'Inputs and Outputs\'!B86/100)^C2:AA2', o['text_format'])

    if results['inputs']['Financial']['third_party_ownership'] == False:
        baucashf_sheet.write('A5', 'Business as Usual boiler fuel bill ($)', o['text_format'])
        baucashf_sheet.write('A6', 'Operation and Maintenance (O&M)', o['text_format'])
        baucashf_sheet.write('A7', 'Existing PV cost in $/kW', o['text_format_indent'])
        baucashf_sheet.write('A8', 'Existing Generator fixed O&M cost', o['text_format_indent'])
        baucashf_sheet.write('A9', 'Existing Generator variable O&M cost', o['text_format_indent'])
        baucashf_sheet.write('A10', 'Existing Generator fuel cost ($)', o['text_format_indent'])
        baucashf_sheet.write('A11', 'Total operating expenses', o['text_format_2'])
        baucashf_sheet.write('A12', 'Tax deductible operating expenses', o['text_format_2'])
        baucashf_sheet.write('A14', 'Production-based incentives (PBI)', o['subheader_format'])
        baucashf_sheet.write('A15', 'Existing PV Combined PBI', o['text_format_2'])
        baucashf_sheet.write('A16', 'Total taxable cash incentives', o['text_format_2'])
        baucashf_sheet.write('A17', 'Total non-taxable cash incentives', o['text_format_2'])
        baucashf_sheet.write('A19', 'Total Cash Flows', o['subheader_format'])
        baucashf_sheet.write('A20', 'Net Operating expenses, after-tax', o['text_format'])
        baucashf_sheet.write('A21', 'Total Cash incentives, after-tax', o['text_format'])
        baucashf_sheet.write('A22', 'Free Cash Flow', o['text_format_2'])
        baucashf_sheet.write('A23', 'Discounted Cash Flow', o['text_format_2'])
        baucashf_sheet.write('A24', 'BAU Life Cycle Cost', o['standalone_bold_text_format'])

        for idx in range(0,26):
            baucashf_sheet.write_blank(13,1+idx, None, o['subheader_format'])
            baucashf_sheet.write_blank(18,1+idx, None, o['subheader_format'])

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
        baucashf_sheet.write_dynamic_array_formula('C12:AA12', '=IF(\'Inputs and Outputs\'!B93 > 0, C11:AA11, 0)', o['text_format_2'])
        baucashf_sheet.write_dynamic_array_formula('C15:AA15', '=IF(B2:Z2 < \'Inputs and Outputs\'!E111, MIN(\'Inputs and Outputs\'!B111 * \'Inputs and Outputs\'!C185:AA185, \'Inputs and Outputs\'!C111 * (1 - \'Inputs and Outputs\'!B5/100)^B2:Z2), 0)', o['text_format_2'])
        baucashf_sheet.write_dynamic_array_formula('C16:AA16', '=IF(\'Inputs and Outputs\'!D111="Yes", C15:AA15, 0)', o['text_format_2'])
        
        baucashf_sheet.write_dynamic_array_formula('C17:AA17', '=IF(\'Inputs and Outputs\'!D111="No", C15:AA15, 0)', o['text_format_2'])
        
        baucashf_sheet.write_dynamic_array_formula('C20:AA20', '=(C11:AA11 - C12:AA12) + C12:AA12 * (1 - \'Inputs and Outputs\'!B93/100)', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C21:AA21', '=(C16:AA16 * (1 - \'Inputs and Outputs\'!B93/100)) + C17:AA17', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C22:AA22', '=C20:AA20 + C21:AA21', o['text_format_2'])
        baucashf_sheet.write_dynamic_array_formula('C23:AA23', '=C22:AA22 / (1 + \'Inputs and Outputs\'!B89/100)^C2:AA2', o['text_format_2'])
        
        baucashf_sheet.write_blank('B11', None, o['text_format_2'])
        baucashf_sheet.write_blank('B12', None, o['text_format_2'])
        baucashf_sheet.write_blank('B16', None, o['text_format_2'])
        baucashf_sheet.write_blank('B17', None, o['text_format_2'])
        baucashf_sheet.write_blank('B22', None, o['text_format_2'])
        baucashf_sheet.write_blank('B23', None, o['text_format_2'])
        
        baucashf_sheet.write_formula('B24', '=SUM(B23:AA23)', o['standalone_bold_text_format'])
    else:
        baucashf_sheet.write('A5', 'Electricity bill with optimal system before export credits', o['text_format'])
        baucashf_sheet.write('A6', 'Export credits with optimal system', o['text_format'])
        baucashf_sheet.write('A7', 'Business as Usual boiler fuel bill ($)', o['text_format'])
        baucashf_sheet.write('A8', 'Boiler fuel bill with optimal systems ($)', o['text_format'])
        baucashf_sheet.write('A9', 'CHP fuel bill with optimal systems ($)', o['text_format'])
        baucashf_sheet.write('A10', 'Payment to Third-party Owner', o['text_format'])
        baucashf_sheet.write('A11', 'Business as Usual Generator fuel cost ($)', o['text_format'])
        baucashf_sheet.write('A12', 'Generator fuel cost with optimal system ($)', o['text_format'])
        baucashf_sheet.write('A13', 'Business as Usual Free Cash Flow', o['text_format_2'])
        baucashf_sheet.write('A14', 'Optimal Case Free Cash Flow', o['text_format_2'])
        baucashf_sheet.write('A15', 'Net Energy Costs', o['text_format_2'])
        baucashf_sheet.write('A16', 'Tax deductible Electricity Costs', o['text_format_2'])
        baucashf_sheet.write('A18', 'Total Cash Flows', o['subheader_format'])
        baucashf_sheet.write('A19', 'Net Operating expenses, after-tax', o['text_format_2'])
        baucashf_sheet.write('A20', 'Discounted Cash Flow', o['text_format'])
        baucashf_sheet.write('A21', 'Host Net Present Value', o['text_format'])

        baucashf_sheet.write_dynamic_array_formula('C5:AA5', '=(-1 * (\'Inputs and Outputs\'!B24 * (1 + \'Inputs and Outputs\'!B86/100)^C2:AA2))', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C6:AA6', '=(-1 * (\'Inputs and Outputs\'!B25 * (1 + \'Inputs and Outputs\'!B86/100)^C2:AA2))', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C7:AA7', '=(-1 * (\'Inputs and Outputs\'!B35 * (1 + \'Inputs and Outputs\'!B87/100)^C2:AA2))', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C8:AA8', '=(-1 * (\'Inputs and Outputs\'!B36 * (1 + \'Inputs and Outputs\'!B87/100)^C2:AA2))', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C9:AA9', '=(-1 * (\'Inputs and Outputs\'!B37 * (1 + \'Inputs and Outputs\'!B88/100)^C2:AA2))', o['text_format'])
        baucashf_sheet.write_array_formula('C10:AA10', '=-\'Third-party Owner Cash Flow\'!C159', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C11:AA11', '=(-1 * (\'Inputs and Outputs\'!B68 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2))', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C12:AA12', '=(-1 * (\'Inputs and Outputs\'!B67 * (1 + \'Inputs and Outputs\'!B85/100)^C2:AA2))', o['text_format'])

        for idx in range(2,27):
            col = base_upper_case_letters[idx]
            baucashf_sheet.write_formula(12,idx, '='+col+'3 + '+col+'4 + '+col+'11', o['text_format'])
        
        baucashf_sheet.write_array_formula('C14:AA14', '=C5:AA5 + C6:AA6 + C10:AA10 + C12:AA12', o['text_format'])
        baucashf_sheet.write_array_formula('C15:AA15', '=-C3:AA3 - C4:AA4 + C5:AA5 + C6:AA6 + C10:AA10 - C11:AA11 + C12:AA12 - C7:AA7 + C8:AA8 + C9:AA9', o['text_format'])
        
        baucashf_sheet.write_dynamic_array_formula('C16:AA16', '=IF(\'Inputs and Outputs\'!B93 > 0, C15:AA15, 0)', o['text_format'])

        baucashf_sheet.write_dynamic_array_formula('C19:AA19', '=(C15:AA15-C16:AA16) + C16:AA16*(1 - \'Inputs and Outputs\'!B94/100)', o['text_format'])
        baucashf_sheet.write_dynamic_array_formula('C20:AA20', '=C19:AA19/(1 + \'Inputs and Outputs\'!B90/100^(C2:AA2))', o['text_format'])
        baucashf_sheet.write_formula('B21', '=SUM(B20:AA20)', o['text_format'])
        
    baucashf_sheet.set_column(0, 0, 24.25)
    baucashf_sheet.set_column('B:AA', 10.38)


    ### CROSS SHEET FORMULAS
    pv_lcoe_formula = None
    wind_lcoe_formula = None
    if results['inputs']['Financial']['third_party_ownership']:
        pv_lcoe_formula = '=ROUND(((\'Inputs and Outputs\'!B52 + -1*(NPV(\'Inputs and Outputs\'!B89/100,\'Third-party Owner Cash Flow\'!C10:\'Third-party Owner Cash Flow\'!AA10)) - SUM(\'Third-party Owner Cash Flow\'!B39,\'Third-party Owner Cash Flow\'!B34,NPV(\'Inputs and Outputs\'!B89/100,\'Third-party Owner Cash Flow\'!C82:\'Third-party Owner Cash Flow\'!AA82),NPV(\'Inputs and Outputs\'!B89/100,\'Third-party Owner Cash Flow\'!C143),NPV(\'Inputs and Outputs\'!B89/100,\'Third-party Owner Cash Flow\'!C138:\'Third-party Owner Cash Flow\'!AA138))) ) / ((NPV(\'Inputs and Outputs\'!B89/100,\'Inputs and Outputs\'!C184:\'Inputs and Outputs\'!AA184) - NPV(\'Inputs and Outputs\'!B89/100,\'Inputs and Outputs\'!C185:\'Inputs and Outputs\'!AA185))), 4)'
        wind_lcoe_formula = '=ROUND((B53 + (-1 * NPV(B89/100,\'Third-party Owner Cash Flow\'!C8:\'Third-party Owner Cash Flow\'!AA8)) - SUM(\'Third-party Owner Cash Flow\'!B43,\'Third-party Owner Cash Flow\'!B38,NPV(B89/100,\'Third-party Owner Cash Flow\'!C79:\'Third-party Owner Cash Flow\'!AA79),NPV(B89/100,\'Third-party Owner Cash Flow\'!C140),NPV(B89/100,\'Third-party Owner Cash Flow\'!C134:\'Third-party Owner Cash Flow\'!AA134)))/ NPV(B89/100, C186:AA186),4)'
    else:
        pv_lcoe_formula = '=ROUND(((\'Inputs and Outputs\'!B52 + -1*(NPV(\'Inputs and Outputs\'!B89/100,\'Optimal Cash Flow\'!C10:\'Optimal Cash Flow\'!AA10)) - SUM(\'Optimal Cash Flow\'!B39,\'Optimal Cash Flow\'!B34,NPV(\'Inputs and Outputs\'!B89/100,\'Optimal Cash Flow\'!C82:\'Optimal Cash Flow\'!AA82),NPV(\'Inputs and Outputs\'!B89/100,\'Optimal Cash Flow\'!C143),NPV(\'Inputs and Outputs\'!B89/100,\'Optimal Cash Flow\'!C138:\'Optimal Cash Flow\'!AA138))) ) / ((NPV(\'Inputs and Outputs\'!B89/100,\'Inputs and Outputs\'!C184:\'Inputs and Outputs\'!AA184) - NPV(\'Inputs and Outputs\'!B89/100,\'Inputs and Outputs\'!C185:\'Inputs and Outputs\'!AA185))), 4)'
        wind_lcoe_formula = '=ROUND((B53 + (-1 * NPV(B89/100,\'Optimal Cash Flow\'!C12:\'Optimal Cash Flow\'!AA12)) - SUM(\'Optimal Cash Flow\'!B48,\'Optimal Cash Flow\'!B43,NPV(B89/100,\'Optimal Cash Flow\'!C84:\'Optimal Cash Flow\'!AA84),NPV(B89/100,\'Optimal Cash Flow\'!C145),NPV(B89/100,\'Optimal Cash Flow\'!C139:\'Optimal Cash Flow\'!AA139)))/ NPV(B89/100, C184:AA184),4)'
        
    if 'PV' in results['outputs'].keys():
        inandout_sheet.write_formula('B6', pv_lcoe_formula, d['text_format_right_decimal'])
    else:
        inandout_sheet.write_number('B6', 0.0, d['text_format_right_decimal'])

    if 'Wind' in results['outputs'].keys():
        inandout_sheet.write_formula('B8', wind_lcoe_formula)
    else:
        inandout_sheet.write_number('B8', 0.0, d['text_format_right_decimal'])

    if results['inputs']['Financial']['third_party_ownership'] == False:
        inandout_sheet.write_formula('B201', '=\'Optimal Cash Flow\'!B160 - \'BAU Cash Flow\'!B22', d['year_0_format'])
        inandout_sheet.write_dynamic_array_formula('C201:AA201', '=\'Optimal Cash Flow\'!C160:AA160 - \'BAU Cash Flow\'!C22:AA22', d['proj_fin_format'])
        
        inandout_sheet.write_formula('B202', '=B201', d['year_0_format'])
        for idx in range(2, 27):
            col = base_upper_case_letters[idx] # C through AA
            col_1 = base_upper_case_letters[idx-1] # B through Z
            
            inandout_sheet.write_formula(
                col+'202',
                '='+col+'201+'+col_1+'202',
                d['proj_fin_format']
            )

        inandout_sheet.write_formula('E6', '=-\'BAU Cash Flow\'!B24', d['proj_fin_format'])
        inandout_sheet.write_formula('E7', '=-\'Optimal Cash Flow\'!B162', d['proj_fin_format'])
        inandout_sheet.write_formula('E8', '=E6 - E7', d['proj_fin_format'])
        inandout_sheet.write_formula('E9', '=IF(E8=0,"",IRR(B201:AA201, \'Inputs and Outputs\'!B89/100))', d['proj_fin_format_decimal'])
        inandout_sheet.write_formula('E10', spp_years, d['proj_fin_format_spp'])
    else:
        inandout_sheet.write_formula('E6', '=\'Third-party Owner Cash Flow\'!C159', d['proj_fin_format'])
        inandout_sheet.write_formula('E7', '=-\'Third-party Owner Cash Flow\'!B157', d['proj_fin_format'])
        inandout_sheet.write_formula('E8', '=\'Host Cash Flow\'!B21', d['proj_fin_format'])
        inandout_sheet.write_formula('E9', '=IF(E8=0,,IRR(\'Third-party Owner Cash Flow\'!B163:\'Third-party Owner Cash Flow\'!AA163,\'Inputs and Outputs\'!B89/100))', d['proj_fin_format_decimal'])
        inandout_sheet.write_formula('E10', spp_years_third_party, d['proj_fin_format_spp'])

    proforma.close()

    return proforma
