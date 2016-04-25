from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import Resource
from tastypie.bundle import Bundle

import subprocess
import os

# We need a generic object to shove data in and to get data from.
class REoptObject(object):
    def __init__(self, id=None, latitude=None, longitude=None, load_size=None, lcc=None):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.load_size = load_size
        self.lcc = lcc

class REoptRunResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.

    # mandatory inputs
    load_size = fields.FloatField(attribute="load_size")

    # currently unhandled
    id = fields.CharField(attribute='id')
    latitude = fields.FloatField(attribute='latitude', null=True)
    longitude = fields.FloatField(attribute='longitude', null=True)

    #outputs
    lcc = fields.FloatField(attribute="lcc",null=True)

    class Meta:
        resource_name = 'reopt'
        allowed_methods = ['get']
        object_class = REoptObject
        authorization = Authorization()


    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj['id']

        return kwargs

    def get_object_list(self, request):
        # note, running process is from reopt_api head
        # i.e, C:\Nick\Projects\api\env\src\reopt_api

        latitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")
        load_size = request.GET.get("load_size")

        # update inputs
        go = os.path.join("Xpress","Go.bat")
        dat_libary_path = os.path.join("Xpress","DatLibrary")

        if load_size > 0:
            load_size_file = open(os.path.join(dat_libary_path,"LoadSize","LoadSize.dat"),'w')
            load_size_file.write("AnnualElecLoad: [\n")
            load_size_file.write(str(load_size) + "\t,\n")
            load_size_file.write("]")
            load_size_file.close()

        # remove old output
        output_file = os.path.join("Xpress","OUT.txt")
        if os.path.exists(output_file):
            os.remove(output_file)

        # call express
        subprocess.call(go)

        # parse outputs
        lcc = []
        output = open(output_file,'r')
        for line in output:
            if "LCC" in line:
                eq_ind = line.index("=")
                lcc = line[eq_ind+2:len(line)]

        results = []
        new_obj = REoptObject("optimize",latitude, longitude, load_size, lcc)
        results.append(new_obj)
        return results

    def obj_get_list(self, bundle, **kwargs):
        # filtering disabled for brevity
        return self.get_object_list(bundle.request)

    #def obj_get(self, bundle, **kwargs):
    #    return REoptObject("10",40.1,-115.0)


