# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

# Keep Python lean and predictable inside containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Runtime libs: libpq for psycopg2 to talk to PostgreSQL
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first so this layer is cached across code changes
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the project
COPY . .

# Collect static assets (e.g. Django admin) into STATIC_ROOT
RUN python manage.py collectstatic --noinput || true

# Run as an unprivileged user (with a real home so gunicorn's control server works)
RUN addgroup --system app \
    && adduser --system --ingroup app --home /home/app app \
    && chown -R app:app /app /home/app
USER app

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
