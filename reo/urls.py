from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^annual_kwh/', views.annual_kwh, name='annual_kwh'),
    url(r'^invalid_urdb/', views.invalid_urdb, name='invalid_urdb'),
    url(r'^help/', views.help, name='help'),
    url(r'^results/', views.results, name='results'),
]
