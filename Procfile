web: gunicorn evocation.wsgi --max-requests 1000
celery: celery -A evocation worker -l info
