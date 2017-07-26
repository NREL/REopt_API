from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from reo.api import RunInputResource
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(RunInputResource())

urlpatterns = [
    url(r'^$', include('reo.urls'), name='reopt'),
    url(r'^proforma/', include('proforma.urls'), name='proforma'),
    url(r'^reopt/', include('reo.urls'), name='reopt'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
    url(r'^resilience_stats/', include('resilience_stats.urls'), name='resilience_stats'),
]

urlpatterns += staticfiles_urlpatterns()

