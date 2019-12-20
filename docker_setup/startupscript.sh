#!/bin/bash

cp /to_share/* /share
cp /share/keys.py /data/github/reopt_api/keys.py

if [ "$SOLVER" == "xpress" ]; then cp /share/xpauth.xpr /opt/xpressmp/bin/xpauth.xpr  ;fi

cd /data/github/reopt_api
pip3 install -r requirements.txt --exists-action w

/etc/init.d/postgresql start
celery -A reopt_api worker --loglevel=info &
redis-server &
python manage.py migrate

printf yes | python manage.py collectstatic
python manage.py runserver 0.0.0.0:8000
