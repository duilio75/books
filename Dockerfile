# syntax=docker/dockerfile:1

# ---- Frontend build stage ----
# Compile CSS/JS with webpack into frontend/build (incl. manifest.json)
FROM node:22-slim AS frontend
WORKDIR /frontend
# Install deps first so this layer is cached across source changes
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
# Build the assets
COPY frontend/ ./
RUN npm run build

# ---- Python base ----
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

# Bring in the compiled frontend assets from the node stage so that
# collectstatic and django-webpack-loader can find them at frontend/build
COPY --from=frontend /frontend/build ./frontend/build

# Collect static assets (Django admin + webpack output) into STATIC_ROOT
RUN python manage.py collectstatic --noinput || true

# Run as an unprivileged user (with a real home so gunicorn's control server works).
# Create the media mount point up front so the volume inherits app ownership and is writable.
RUN addgroup --system app \
    && adduser --system --ingroup app --home /home/app app \
    && mkdir -p /app/media \
    && chown -R app:app /app /home/app
USER app

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
