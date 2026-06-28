#!/usr/bin/env bash
set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: scripts/new-migration.sh <message>" >&2
  exit 1
fi

docker compose exec api uv run alembic revision --autogenerate -m "$1"
