#! /bin/bash
docker-compose --file docker-compose.xpress.yml build
docker-compose --file docker-compose.xpress.yml run celery python manage.py test -v 2 --failfast --noinput
