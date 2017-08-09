from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$',views.index, name='index'),
    url(r'^annual_kwh/', views.annual_kwh, name='annual_kwh'),
    url(r'^check_inputs/',views.check_inputs, name='check_inputs'),
]
