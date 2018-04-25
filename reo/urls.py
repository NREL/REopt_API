from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^annual_kwh/', views.annual_kwh, name='annual_kwh'),
    url(r'^invalid_urdb/', views.invalid_urdb, name='invalid_urdb'),
    url(r'^help/', views.help, name='help'),
    url(r'^results/', views.results, name='results'),
    url(r'^simulated_load/', views.simulated_load, name='simulated_load'),
    url(r'^generator_efficiency/', views.generator_efficiency, name='generator_efficiency'),
]
