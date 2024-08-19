# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
from . import views
from reo import views as reoviews
from django.urls import register_converter, re_path

class UUIDListConverter:
    regex = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(;([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}))*'

    def to_python(self, value):
        return value.split(';')

    def to_url(self, value):
        return ';'.join(value)

# Register the custom converter
register_converter(UUIDListConverter, 'uuidlist')

urlpatterns = [
    re_path(r'^job/(?P<run_uuid>[0-9a-f-]+)/results/?$', views.results),
    re_path(r'^help/?$', views.help),
    re_path(r'^job/inputs/?$', views.inputs),
    re_path(r'^job/outputs/?$', views.outputs),
    re_path(r'^chp_defaults/?$', views.chp_defaults),
    re_path(r'^absorption_chiller_defaults/?$', views.absorption_chiller_defaults),
    re_path(r'^avert_emissions_profile/?$', views.avert_emissions_profile),
    re_path(r'^cambium_emissions_profile/?$', views.cambium_emissions_profile),
    re_path(r'^easiur_costs/?$', views.easiur_costs),
    re_path(r'^simulated_load/?$', views.simulated_load),
    re_path(r'^user/(?P<user_uuid>[0-9a-f-]+)/summary/?$', views.summary),
    re_path(r'^user/(?P<user_uuid>[0-9a-f-]+)/summary_by_chunk/(?P<chunk>[0-9]+)/?$', views.summary_by_chunk),
    re_path(r'^user/(?P<user_uuid>[0-9a-f-]+)/unlink/(?P<run_uuid>[0-9a-f-]+)/?$', views.unlink),
    re_path(r'^ghp_efficiency_thermal_factors/?$', views.ghp_efficiency_thermal_factors),
    re_path(r'^peak_load_outage_times/?$', views.peak_load_outage_times),
    re_path(r'^invalid_urdb/?$', reoviews.invalid_urdb),
    re_path(r'^schedule_stats/?$', reoviews.schedule_stats),
    re_path(r'^get_existing_chiller_default_cop/?$', views.get_existing_chiller_default_cop),
    re_path(r'^job/comparison_table/(?P<run_uuids>[0-9a-f\-;]+)/$', views.create_custom_comparison_table),
]
