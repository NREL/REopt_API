from api_definitions import *
from django.shortcuts import render
import json
from django.http import HttpResponse
from validators import REoptResourceValidation
from django.views.static import serve

def index(request):
    api_inputs = {}
    reference = inputs(full_list=True)
    for k,v in reference.items():
        api_inputs[k]={'req':bool(reference[k].get('req'))}
        api_inputs[k]['type'] = reference[k].get('type').__name__
        api_inputs[k]['description'] = reference[k].get('description')

        units  = reference[k].get('units')
        if units:
            api_inputs[k]['description'] = "%s (%s)" % (api_inputs[k]['description'],units)

        api_inputs[k]['validations'] = "min: %s \n max: %s \n restrict to: %s" % (reference[k].get('min'),reference[k].get('max'),reference[k].get('restrict_to'))

    api_outputs = outputs()
    return render(request,'template.html',{'api_inputs':api_inputs,'api_outputs':api_outputs})

def check_inputs(request):

    checker = REoptResourceValidation()
    errors  ={"Errors":{}}

    bdy = unicode(request.body, 'latin-1')
    parsed_request = json.loads(bdy)
    
    scrubbed_request = {}
    for k,v in parsed_request.items():
        if k in inputs(full_list=True).keys():
            scrubbed_request[k] = v
        else:
            errors["Errors"][k] = ["Not  Valid Input Name"]

    
    errors = checker.check_individual(scrubbed_request,errors)


    if errors == {}:
        return HttpResponse(json.dumps({"Errors":{}}), content_type='application/json')    
    else:
        return HttpResponse(json.dumps(errors), content_type='application/json')

def get_download(request):

    lookup_fileExt = {'proforma':".pdf"}

    file_type = request.GET['file_type']
    run_id = request.GET['run_id']
    filename = file_type + "_" + run_id + lookup_fileExt[file_type]

    path_to_file = os.path.join(os.getcwd(),'Xpress','Downloads', filename)
   
    return serve(request, os.path.basename(path_to_file), os.path.dirname(path_to_file))
   

def get_tooltips(request):
    response = {}
    for k, df in inputs().items():
        message = df['tool_tip'] + " "
        
        if df.get('restrict_to') is not None:
            message += "Possible values include " + ", ".join( [str(i) for i in df['restrict_to'] if i is not None ] ) + ". "
        if df.get('units') is not None:
            message += "Units: " + df['units'] + ". "
        if message is None:
            print k, df

        if df.get('req'):
            message += "This value is required. "
        else:
            message += "This value is not required. "

        response[k] = message
    
    return HttpResponse(json.dumps(response), content_type='application/json')    
    