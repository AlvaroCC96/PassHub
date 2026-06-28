#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

if [ ! -f .env ]; then
  cp .env.development .env
  echo "Created .env from .env.development"
fi

echo "Installing frontend workspace dependencies..."
pnpm install

echo "Building and starting containers..."
docker compose up --build -d

echo "PassHub is starting:"
echo "  Web      -> http://localhost:5173"
echo "  API      -> http://localhost:8000/api/v1/docs"
echo "  MinIO    -> http://localhost:9001"
echo "  PgAdmin  -> http://localhost:5050"
