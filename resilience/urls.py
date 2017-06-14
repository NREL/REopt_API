from django.conf.urls import url, include
from . import views

def get_current_api():
    return "Resilience v 0.0.1"

urlpatterns = [
    url(r'^$',views.index, name='index'),
    ]
