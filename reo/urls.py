from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$',views.index, name='index'),
    url(r'^definition/',views.definition, name='definition'),
    url(r'^check_inputs/',views.check_inputs, name='check_inputs'),
    url(r'^downloads/',views.get_download, name='get_download'),
]
