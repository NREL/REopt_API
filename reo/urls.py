# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.urls import re_path

urlpatterns = [
    re_path(r'^annual_kwh/?$', views.annual_kwh),
    re_path(r'^invalid_urdb/?$', views.invalid_urdb),
    re_path(r'^help/?$', views.help),
    re_path(r'^job/(?P<run_uuid>[0-9a-f-]+)/results/?$', views.results),
    re_path(r'^simulated_load/?$', views.simulated_load),
    re_path(r'^emissions_profile/?$', views.emissions_profile),
    re_path(r'^easiur_costs/?$', views.easiur_costs),
    re_path(r'^fuel_emissions_rates/?$', views.fuel_emissions_rates),
    re_path('^generator_efficiency/?$', views.generator_efficiency),
    re_path(r'^chp_defaults/?$', views.chp_defaults),
    re_path(r'^loadprofile_chillerthermal_chiller_cop/?$', views.loadprofile_chillerthermal_chiller_cop),
    re_path(r'^absorption_chiller_defaults/?$', views.absorption_chiller_defaults),
    re_path(r'^schedule_stats/?$', views.schedule_stats),
    re_path(r'^ghp_efficiency_thermal_factors/?$', views.ghp_efficiency_thermal_factors),
    re_path(r'^job/(?P<run_uuid>[0-9a-f-]+)/remove/?$', views.remove),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
