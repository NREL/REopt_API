from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.index, name='index'),
    url(r'^annual_kwh/', views.annual_kwh, name='annual_kwh'),
    url(r'^invalid_urdb/', views.invalid_urdb, name='invalid_urdb'),
    url(r'^default_api_inputs/', views.default_api_inputs, name='default_api_inputs'),
    url(r'^help/', views.help, name='help'),
    url(r'^check_inputs/',views.check_inputs, name='check_inputs'),
    url(r'^results/', views.results, name='results'),
]
