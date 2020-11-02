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
from __future__ import absolute_import, unicode_literals  # recommended by celery documentation
import os
import logging
from celery import Celery
from celery.signals import after_setup_logger
from keys import *

# set the default Django settings module for the 'celery' program.
try:
    env = os.environ['APP_ENV']

    if env == 'internal_c110p':
        raw_env = 'reopt_api.internal_c110p_settings'
        redis_host = ':' + dev_redis_password + '@localhost'
    elif env == 'development':
        raw_env = 'reopt_api.dev_settings'
        redis_host = ':' + dev_redis_password + '@' + dev_redis_host
    elif env == 'staging':
        raw_env = 'reopt_api.staging_settings'
        redis_host = ':' + staging_redis_password + '@' + staging_redis_host
    elif env == 'production':
        raw_env = 'reopt_api.production_settings'
        redis_host = ':' + production_redis_password + '@' + production_redis_host
    else:
        raw_env = 'reopt_api.dev_settings'
        redis_host = os.environ.get('REDIS_HOST', 'localhost')

except KeyError:
    """
    This catch is necessary for running celery from command line when testing/developing locally.
    APP_ENV is defined in config/deploy/[development, production, staging].rb files for servers.
    For testing and local development, APP_ENV *can* be defined in .env file (see README.md),
    which `honcho` or `foreman` loads before running Procfile.
    """
    raw_env = 'reopt_api.dev_settings'
    redis_host = os.environ.get('REDIS_HOST', 'localhost')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', raw_env)

app = Celery('reopt_api')

# # Example of killing celery task:
# app.control.revoke('a879bf13-6689-41bc-bd23-ad6a05920f24', terminate=True)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_url = 'redis://' + redis_host + ':6379/0'

# Create separate queues for each server (naming each queue after the server's
# hostname). Since the worker jobs currently all have to be processes on the
# same server (so the input/output files can be shared across jobs), having
# server-specific queues is a simplistic way to ensure processing remains on a
# single server.
app.conf.task_default_queue = os.environ.get('APP_QUEUE_NAME', 'localhost')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    # file_formatter = logging.Formatter(
    #     '%(asctime)s %(name)-12s %(levelname)-8s %(filename)s::%(funcName)s line %(lineno)s %(message)s')
    console_formatter = logging.Formatter(
        '%(name)-12s %(levelname)-8s %(filename)s::%(funcName)s line %(lineno)s %(message)s')

    # logfile = os.path.join(os.getcwd(), "log", "reopt_api.log")
    #
    # file_handler = logging.FileHandler(filename=logfile, mode='a')
    # file_handler.setFormatter(file_formatter)
    # file_handler.setLevel(logging.INFO)
    # logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
