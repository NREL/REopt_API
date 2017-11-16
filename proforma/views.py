from tastypie.http import HttpResponse, HttpBadRequest
from tastypie.exceptions import ImmediateHttpResponse
from models import ProForma, ScenarioModel
import os
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from reo.utilities import API_Error
import json


def proforma(request):
    try:
        uuid = request.GET.get('run_uuid') 
        scenario = ScenarioModel.objects.get(run_uuid=uuid)

        try:
            pf = ProForma.objects.get(scenariomodel=scenario)
        except:
            pf = ProForma.create(scenariomodel=scenario)

        pf.generate_spreadsheet()
        pf.save()

        wrapper = FileWrapper(file(pf.output_file))
 
        response = HttpResponse(wrapper, content_type='application/force-download')
        response['Content-Length'] = os.path.getsize(pf.output_file)
        response['Content-Disposition'] = 'attachment; filename=%s' % (pf.output_file_name)
        return response

    except Exception as e:
        return HttpResponse(json.dumps(API_Error(e).response), content_type='application/json', status=400)
