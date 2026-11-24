# Backend image: the api, and later the worker and maintenance with another command (ADR-0001).
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
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
COPY app ./app
RUN useradd --create-home --uid 10001 app
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
