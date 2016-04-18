# myapp/api.py
from tastypie.resources import ModelResource
from reo.models import REoptRun


class REoptRunResource(ModelResource):
    class Meta:
        queryset = REoptRun.objects.all()
        resource_name = 'reopt'