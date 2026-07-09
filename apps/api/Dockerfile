FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Non-root user — Cloud Run security best practice
RUN groupadd --gid 1001 appgroup && useradd --uid 1001 --gid appgroup --no-create-home appuser

COPY pyproject.toml ./
RUN uv sync --no-install-project

COPY . .
RUN uv sync

# Cloud Run injects PORT=8080; local docker-compose overrides CMD directly
EXPOSE 8080

USER appuser

CMD ["sh", "-c", "uv run uvicorn src.presentation.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
