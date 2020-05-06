# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
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

        if scenario.status.lower() == "optimizing...":
            return HttpResponse("Problem is still solving. Please try again later.", status=425)  # too early status

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
        elif "Problem is still solving" in e.args:
            msg = e.args[0]
            return HttpResponse(msg, status=425)  # too early status
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = UnexpectedError(exc_type, exc_value, exc_traceback, task='proforma', run_uuid=run_uuid)
            err.save_to_db()
            return HttpResponse({"Error": str(err.message)}, status=400)
