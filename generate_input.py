import os, json

dev = False

if dev:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reopt_api.dev_settings")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reopt_api.staging_settings")

try:
    from django.contrib.postgres.fields import ArrayField
except:
    from django.contrib.postgres.fields import *

from reo.models import RunInput


def get_curl_by_id(id):
    data = RunInput.objects.get(pk=id).__dict__
    data =  {k:v for k,v in data.items() if bool(v) and k not in ['__len__','_state','created','id','api_version']}
    data_json = json.dumps(data)

    print data_json

get_curl_by_id(1049)