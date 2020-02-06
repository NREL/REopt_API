from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.load_builder, name='load_builder'),
]