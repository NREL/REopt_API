from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.

# env = os.environ['APP_ENV']
# if env == 'development':
#     raw_env = 'reopt_api.dev_settings'
# elif env == 'staging':
#     raw_env = 'reopt_api.staging_settings'
# elif env == 'production':
#     raw_env = 'reopt_api.production_settings'
# else:
#     raise TypeError('Unknown APP_ENV')
#
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reopt_api.dev_settings')

app = Celery('reopt_api')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_url = 'redis://localhost:6379/0'

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print 'Request: {0!r}'.format(self.request)
