from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<user_id>[0-9a-z-]+)/summary/?$', views.summary, name='summary'),
    url(r'rename/?$', views.update_user_id, name='update_user_id'),
]