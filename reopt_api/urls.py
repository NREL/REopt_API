from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from reo.api import Job
from tastypie.api import Api
from reo import views
from proforma.views import proforma

v1_api = Api(api_name='v1')
v1_api.register(Job())

urlpatterns = [
    url(r'^v1/job/(?P<run_uuid>[0-9a-f-]+)/proforma/$', proforma, name='proforma'),
    url(r'^v1/job/(?P<run_uuid>[0-9a-f-]+)/resilience_stats/$', include('resilience_stats.urls'), name='resilience_stats'),
    url(r'^v1/job/(?P<run_uuid>[0-9a-f-]+)/results/$', views.results, name='results'),
    url(r'^v1/help/$', views.help, name='help'),
    url(r'^v1/invalid_urdb/$', views.invalid_urdb, name='invalid_urdb'),
    url(r'^v1/annual_kwh/$', views.annual_kwh, name='annual_kwh'),
    url(r'', include(v1_api.urls), name='job'),
]

urlpatterns += staticfiles_urlpatterns()
