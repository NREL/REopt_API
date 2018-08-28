from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<user_uuid>[0-9a-f-]+)/summary/?$', views.summary, name='summary'),
    url(r'rename/?$', views.add_user_uuid, name='add_user_uuid'),
    ]