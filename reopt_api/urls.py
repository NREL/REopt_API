from django.conf.urls import include, url
from django.contrib import admin
from reo.api import REoptRunResource
from tastypie.api import Api

reopt_resource = REoptRunResource("reopt_api-1.0-py2.7_ted.egg")

v1_api = Api(api_name='v1')
v1_api.register(reopt_resource)

urlpatterns = [
    # Examples:
    # url(r'^$', 'bookstore.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', include('reo.urls'), name='reopt'),
    url(r'^reopt/', include('reo.urls'), name='reopt'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),

]
