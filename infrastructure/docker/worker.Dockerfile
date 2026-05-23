# ===============================================
# Celery Worker Dockerfile
# ===============================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend application
COPY backend/app /app/app

# Create storage directories
RUN mkdir -p /app/storage/{media,assets,temp}

# Run Celery worker
CMD ["celery", "-A", "app.workers.celery_app", "worker", "--loglevel=info"]