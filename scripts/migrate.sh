#!/usr/bin/env bash
# Run Alembic migrations against Cloud SQL.
# This connects directly from your local machine via Cloud SQL Auth Proxy.
#
# Prerequisites:
#   1. Install Cloud SQL Auth Proxy:
#      https://cloud.google.com/sql/docs/postgres/connect-auth-proxy
#   2. Start the proxy in another terminal:
#      cloud-sql-proxy PROJECT_ID:REGION:INSTANCE_NAME --port 5433
#   3. Set env vars below and run this script.
#
# Usage:
#   export POSTGRES_HOST=127.0.0.1
#   export POSTGRES_PORT=5433
#   export POSTGRES_USER=passhub
#   export POSTGRES_PASSWORD=your_password
#   export POSTGRES_DB=passhub
#   ./scripts/migrate.sh
set -euo pipefail

POSTGRES_HOST="${POSTGRES_HOST:-127.0.0.1}"
POSTGRES_PORT="${POSTGRES_PORT:-5433}"
POSTGRES_USER="${POSTGRES_USER:?Set POSTGRES_USER}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD}"
POSTGRES_DB="${POSTGRES_DB:-passhub}"

export POSTGRES_HOST POSTGRES_PORT POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB

echo "▶ Running Alembic migrations"
echo "  Target: ${POSTGRES_USER}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"

cd apps/api
uv run alembic upgrade head

echo "✓ Migrations complete."
