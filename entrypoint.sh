#!/bin/sh
set -e

# Apply database migrations before starting the server
python manage.py migrate --noinput

# Hand off to the container command (gunicorn by default)
exec "$@"
