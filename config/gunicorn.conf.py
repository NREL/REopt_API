import os
import multiprocessing

# Bind to unix socket that nginx will proxy to.
bind = 'unix:' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tmp/gunicorn.sock')

# Based the number of workers on the number of CPU cores.
workers = multiprocessing.cpu_count()

# Log access log details to stdout.
accesslog = '-'

# Set the appropriate DJANGO_SETTINGS_MODULE environment variable based on the
# current environment.
env = os.environ['APP_ENV']
if env == 'development':
    raw_env = ['DJANGO_SETTINGS_MODULE=reopt_api.dev_settings']
elif env == 'staging':
    raw_env = ['DJANGO_SETTINGS_MODULE=reopt_api.staging_settings']
else:
    raise TypeError('Unknown APP_ENV')
