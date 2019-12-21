from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from keys import *

# set the default Django settings module for the 'celery' program.
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
