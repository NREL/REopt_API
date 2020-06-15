import os
import multiprocessing

# Bind to unix socket that nginx will proxy to.
if os.environ.get('TEST') is None:
    bind = 'unix:' + os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'tmp/gunicorn.sock')
else:
    bind = "127.0.0.1:8000"

# Based the number of workers on the number of CPU cores.
workers = multiprocessing.cpu_count()

# Note that the app currently has threading issues, so we explicitly want a
# non-thread worker process model.
worker_class = "sync"
threads = 1

# Log access log details to stdout.
accesslog = '-'

# Increase timeout for longer response times.
#
# This value should be be kept in sync with the xpress/mosel run timeout
# (defined in reo/models.py), and the nginx timeout (defined in
# config/deploy/templates/nginx/proxy_settings.conf.erb).
#
# This timeout should be greater than the xpress timeout, but less than the
# nginx timeout, to give the app an opportunity to handle timeouts more
# gracefully.
timeout = 435

# Set the appropriate DJANGO_SETTINGS_MODULE environment variable based on the
# current environment.
env = os.environ['APP_ENV']
if env == 'development':
    raw_env = ['DJANGO_SETTINGS_MODULE=reopt_api.dev_settings']
elif env == 'staging':
    raw_env = ['DJANGO_SETTINGS_MODULE=reopt_api.staging_settings']
elif env == 'production':
    raw_env = ['DJANGO_SETTINGS_MODULE=reopt_api.production_settings']
elif env == 'internal_c110p':
    raw_env = ['DJANGO_SETTINGS_MODULE=reopt_api.internal_c110p_settings']
else:
    raw_env = ['DJANGO_SETTINGS_MODULE=reopt_api.dev_settings']
