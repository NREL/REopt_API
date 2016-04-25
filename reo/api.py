from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import Resource
from tastypie.bundle import Bundle

# We need a generic object to shove data in/get data from.
class REoptObject(object):
    def __init__(self, id=None, latitude=None, longitude=None):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude

class REoptRunResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.
    id = fields.CharField(attribute='id')
    latitude = fields.FloatField(attribute='latitude')
    longitude = fields.FloatField(attribute='latitude')

    class Meta:
        resource_name = 'reopt'
        allowed_methods = ['get']
        object_class = REoptObject
        authorization = Authorization()

    # The following methods will need overriding regardless of your
    # data source.
    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj['id']

        return kwargs

    def get_object_list(self, request):
        results = []
        new_obj = REoptObject("id1", 40.1, -115.0)
        results.append(new_obj)
        return results

    def obj_get_list(self, bundle, **kwargs):
        # filtering disabled for brevity
        return self.get_object_list(bundle.request)

    def obj_get(self, bundle, **kwargs):

        return REoptObject("id1",40.1,-115.0)


