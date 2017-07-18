from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from reo.api import RunInputResource
from proforma.api import ProFormaResource
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(RunInputResource())
v1_api.register(ProFormaResource())

urlpatterns = [
    # Examples:
    # url(r'^$', 'bookstore.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', include('reo.urls'), name='reopt'),
    url(r'^reopt/', include('reo.urls'), name='reopt'),
    url(r'^proforma/spreadsheet', include('reo.urls'), name='proforma/spreadsheet'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
]

urlpatterns += staticfiles_urlpatterns()

