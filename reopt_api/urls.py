from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from reo.api import RunInputResource
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(RunInputResource())

urlpatterns = [
    url(r'^v1/proforma/', include('proforma.urls'), name='proforma'),
    url(r'^v1/resilience_stats/', include('resilience_stats.urls'), name='resilience_stats'),
    url(r'^v1/', include('reo.urls'), name='reopt'),
    url(r'', include(v1_api.urls)),
]

urlpatterns += staticfiles_urlpatterns()

