# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
from . import views
from reo import views as reoviews
from django.urls import re_path

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
    re_path(r'^peak_load_outage_times/?$', views.peak_load_outage_times),
    re_path(r'^invalid_urdb/?$', reoviews.invalid_urdb),
    re_path(r'^schedule_stats/?$', reoviews.schedule_stats),
]