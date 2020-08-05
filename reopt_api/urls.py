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
from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse
from reo.api import Job
from resilience_stats.api import OutageSimJob
from tastypie.api import Api
from reo import views
from proforma.views import proforma
from resilience_stats.views import resilience_stats, financial_check

v1_api = Api(api_name='v1')
v1_api.register(Job())
v1_api.register(OutageSimJob())


def page_not_found(request, url):
    """
    If we could run with DEBUG = False, this custom 404 would not be necessary (see production_settings.py for more).
    This custom 404 is to avoid showing users too much information (i.e. traceback information) when they mistype a url.
    :param request:
    :param url:
    :return:
    """
    return HttpResponse("Invalid URL: {}".format(url), status=404)

urlpatterns = [
    url(r'^v1/job/(?P<run_uuid>[0-9a-f-]+)/proforma/?$', proforma, name='proforma'),
    url(r'^v1/job/(?P<run_uuid>[0-9a-f-]+)/resilience_stats/?$', resilience_stats, name='resilience_stats'),
    url(r'^v1/outagesimjob/(?P<run_uuid>[0-9a-f-]+)/?$', resilience_stats, name='resilience_stats'),
    url(r'^v1/job/(?P<run_uuid>[0-9a-f-]+)/resilience_stats/financial_check/?$', financial_check, name='financial_check'),  # preserving old behavior
    url(r'^v1/financial_check/?$', financial_check, name='financial_check'),
    url(r'^v1/job/(?P<run_uuid>[0-9a-f-]+)/results/?$', views.results, name='results'),
    url(r'^v1/job/(?P<run_uuid>[0-9a-f-]+)/remove/?$', views.remove, name='remove'),
    url(r'^v1/user/?', include('summary.urls'), name='summary'),
    url(r'^v1/load_builder/?', include('load_builder.urls'), name='load_builder'),
    url(r'^v1/help/?$', views.help, name='help'),
    url(r'^v1/invalid_urdb/?$', views.invalid_urdb, name='invalid_urdb'),
    url(r'^v1/annual_kwh/?$', views.annual_kwh, name='annual_kwh'),
    url(r'^v1/simulated_load/?$', views.simulated_load, name='simulated_load'),
    url(r'^v1/generator_efficiency/?$', views.generator_efficiency, name='generator_efficiency'),
    url(r'^v1/emissions_profile/?$', views.emissions_profile, name='emissions_profile'),
    url(r'^errors/(?P<page_uuid>.*)', views.errors, name='errors'),
    url(r'', include(v1_api.urls), name='job'),
    url(r'', include(v1_api.urls), name='outagesimjob'),
    url(r'(.*)', page_not_found, name='404'),
    ]

urlpatterns += staticfiles_urlpatterns()
