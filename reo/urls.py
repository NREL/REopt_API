from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings

from IPython import embed
embed()

print "AAAA"
urlpatterns = [
    url(r'^errors/', views.errors, name='errors'),
    url(r'^annual_kwh/', views.annual_kwh, name='annual_kwh'),
    url(r'^invalid_urdb/', views.invalid_urdb, name='invalid_urdb'),
    url(r'^help/', views.help, name='help'),
    url(r'^results/', views.results, name='results'),
    url(r'^simulated_load/', views.simulated_load, name='simulated_load'),
    url(r'^generator_efficiency/', views.generator_efficiency, name='generator_efficiency'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
