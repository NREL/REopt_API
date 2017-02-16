from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$',views.index, name='index'),
    url(r'^check_inputs/',views.check_inputs, name='check_inputs'),
    url(r'^get_tooltips/',views.get_tooltips, name='get_tooltips'),
]