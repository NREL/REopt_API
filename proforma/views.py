from tastypie.http import HttpResponse, HttpBadRequest
from tastypie.exceptions import ImmediateHttpResponse
from models import ProForma, REoptResponse
import os
from django.http import HttpResponse
from wsgiref.util import FileWrapper


def proforma(request):
    uuid = request.GET.get('run_uuid')

    try:
        run_output = REoptResponse.objects.get(uuid=uuid)

        try:
            pf = ProForma.objects.get(run_output=run_output)
        except:
            pf = ProForma.create(run_output=run_output)

        pf.save()

        wrapper = FileWrapper(file(pf.output_file))
        response = HttpResponse(wrapper, content_type='application/force-download')
        response['Content-Length'] = os.path.getsize(pf.output_file)
        response['Content-Disposition'] = 'attachment; filename=%s' % (pf.output_file_name)
        return response

    except:
        raise ImmediateHttpResponse(HttpBadRequest("Invalid UUID"))
