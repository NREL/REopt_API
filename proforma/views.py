import os
import sys
import uuid
from django.http import JsonResponse
from proforma.models import ProForma, ScenarioModel
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from reo.exceptions import UnexpectedError


def proforma(request, run_uuid):

    try:
        uuid.UUID(run_uuid)  # raises ValueError if not valid uuid

    except ValueError as e:
        if e.args[0] == "badly formed hexadecimal UUID string":
            resp = {"Error": e.args[0]}
            return JsonResponse(resp, status=400)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value, exc_traceback, task='proforma', run_uuid=run_uuid)
            err.save_to_db()
            return JsonResponse({"Error": str(err.message)}, status=400)

    try:
        scenario = ScenarioModel.objects.get(run_uuid=run_uuid)

        try:  # see if Proforma already created
            pf = ProForma.objects.get(scenariomodel=scenario)
        except:
            pf = ProForma.create(scenariomodel=scenario)

        pf.generate_spreadsheet()
        pf.save()

        wrapper = FileWrapper(open(pf.output_file, "rb"))
 
        response = HttpResponse(wrapper, content_type='application/vnd.ms-excel.sheet.macroEnabled.12')
        response['Content-Length'] = os.path.getsize(pf.output_file)
        response['Content-Disposition'] = 'attachment; filename=%s' % (pf.output_file_name)
        return response

    except Exception as e:

        if type(e).__name__ == 'DoesNotExist':
            msg = "Scenario {} does not exist.".format(run_uuid)
            return HttpResponse(msg, status=404)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value, exc_traceback, task='proforma', run_uuid=run_uuid)
            err.save_to_db()
            return HttpResponse({"Error": str(err.message)}, status=400)
