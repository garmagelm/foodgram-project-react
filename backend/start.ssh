#!/bin/bash
python manage.py migrate && \
python manage.py collectstatic --no-input && \
gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000