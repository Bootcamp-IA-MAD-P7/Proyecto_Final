# Backend image: the api, and later the worker and maintenance with another command (ADR-0001).
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
# FFmpeg: ffprobe validates the received audio by its content (add-class-reception).
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt

# Development: make, test and lint tools; the source is mounted by compose.override.yaml.
FROM base AS dev
ENV RUFF_NO_CACHE=true
RUN apt-get update \
    && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY . .
EXPOSE 8000
CMD ["make", "dev"]

# Production: only the application code, run by an unprivileged user.
FROM base AS prod
COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app
# Private audio directory (AUDIO_STORAGE_DIR), writable only by the app user.
RUN useradd --create-home --uid 10001 app \
    && mkdir -p data/audio \
    && chown -R app:app data \
    && chmod -R 700 data
USER app
EXPOSE 8000
CMD ["sh", "-c", "python -m app.db.migrate && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
