from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from keys import *

# set the default Django settings module for the 'celery' program.

try:
    env = os.environ['APP_ENV']

    if env == 'development':
        raw_env = 'reopt_api.dev_settings'
        redis_host = ':' + dev_redis_password + '@reopt-dev-db1.nrel.gov'
    elif env == 'staging':
        raw_env = 'reopt_api.staging_settings'
        redis_host = ':' + staging_redis_password + '@reopt-stage-db1.nrel.gov'
    elif env == 'production':
        raw_env = 'reopt_api.production_settings'
        redis_host = ':' + production_redis_password + '@reopt-prod-db1.nrel.gov'
    else:
        raw_env = 'reopt_api.dev_settings'
        redis_host = 'localhost'

except KeyError:
    """
    This catch is necessary for running celery from command line when testing/developing locally.
    APP_ENV is defined in config/deploy/[development, production, staging].rb files for servers.
    For testing and local development, APP_ENV *can *be defined in .env file (see README.md),
    which `honcho` loads before running Procfile.
    """
    raw_env = 'reopt_api.dev_settings'
    redis_host = 'localhost'
#
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

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print 'Request: {0!r}'.format(self.request)
