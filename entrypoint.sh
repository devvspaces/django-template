#!/bin/bash

# Django
python manage.py migrate
python manage.py create_admin
python manage.py collectstatic --no-input

# Django Celery Results
# python manage.py migrate django_celery_results

# Start supervisor (will handle nginx, gunicorn, celery, and flower)
exec /usr/bin/supervisord -n
