from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.resilience_stats, name='resilience_stats'),
]
