from django.conf.urls import include, url
from django.contrib import admin
from reo.api import REoptRunResource

reopt_resource = REoptRunResource()

urlpatterns = [
    # Examples:
    # url(r'^$', 'bookstore.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$',include('reo.urls'),name='reopt'),
    url(r'^reopt/',include('reo.urls'),name='reopt'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(reopt_resource.urls)),

]
