from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.annual_kwh, name='annual_kwh'),
]