# Multi-stage production Dockerfile for StudyBridge
FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

WORKDIR /app/backend

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "studybridge.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
