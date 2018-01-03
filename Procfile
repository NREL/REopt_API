web: $DEPLOY_CURRENT_PATH/bin/server
worker: celery -A reopt_api worker --loglevel=info
manager: celery -A reopt_api flower --port=5555
