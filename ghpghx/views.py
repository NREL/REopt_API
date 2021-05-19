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
import traceback as tb
import uuid
import copy
import csv
import json
import pandas as pd
import logging
from django.http import JsonResponse
from django.http import HttpResponse
from django.template import  loader
from django.views.decorators.csrf import csrf_exempt
from ghpghx.resources import UUIDFilter
from ghpghx.models import ModelManager
# from ghpghx.exceptions import UnexpectedError  #, RequestError  # should we save bad requests? could be sql injection attack?
# from ghpghx.validators import ValidateNestedInput

log = logging.getLogger(__name__)


def make_error_resp(msg):
        resp = dict()
        resp['messages'] = {'error': msg}
        resp['outputs'] = dict()
        resp['status'] = 'error'
        return resp


def health(request):
    return HttpResponse("OK")


def errors(request, page_uuid):

    template= loader.get_template("errors.html")
    return HttpResponse(template.render())


def help(request):

    try:
        # TODO response = SOME FORM GENERATED FROM MODELS.PY?
        # Somehow recreate nested_inputs_definitions from models.py models?
        #response = copy.deepcopy(nested_input_definitions)
        response = {}
        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({"Error": "Unexpected error in help endpoint: {}".format(e.args[0])}, status=500)


def results(request, ghp_uuid):
    try:
        uuid.UUID(ghp_uuid)  # raises ValueError if not valid uuid

    except ValueError as e:
        if e.args[0] == "badly formed hexadecimal UUID string":
            resp = make_error_resp(e.args[0])
            return JsonResponse(resp, status=400)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            resp = make_error_resp("Error when trying to process ghp_uuid")
            return JsonResponse(resp, status=400)

    try:
        d = ModelManager.make_response(ghp_uuid)  # ModelManager has some internal exception handling

        response = JsonResponse(d)
        return response

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        resp = make_error_resp("Error when trying to make_response")
        return JsonResponse(resp, status=500)

@csrf_exempt  # Required for POST, but not GET requests
def post_exmpl(request):
    """
    Description
    :param year: query param
    :return: response field
    """
    try:
        if request.method == "GET":
            msg = "Successful GET request"
            resp = {}
        elif request.method == "POST":
            request_dict = json.loads(request.body)
            msg = "Successful POST request"
            resp = request_dict
        response = JsonResponse(
            {
                "message": msg,
                "echo_post": resp
            }
        )
        return response

    except ValueError as e:
        return JsonResponse({"Error": str(e.args[0])}, status=400)

    except KeyError as e:
        return JsonResponse({"Error. Missing": str(e.args[0])}, status=400)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.args[0],
                                                                            tb.format_tb(exc_traceback))
        log.debug(debug_msg)
        return JsonResponse({"Error": "Unexpected error in post_exmpl endpoint. Check log for more."}, status=500)