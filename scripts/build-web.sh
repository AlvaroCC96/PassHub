#!/usr/bin/env bash
# Build and push the frontend Docker image to Artifact Registry.
# VITE_API_BASE_URL is baked into the image at build time.
# Usage: ./scripts/build-web.sh
# Required env vars: PROJECT_ID, VITE_API_BASE_URL
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID}"
REGION="${REGION:-us-central1}"
REPO="passhub"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/passhub-web"
TAG="${TAG:-latest}"
VITE_API_BASE_URL="${VITE_API_BASE_URL:?Set VITE_API_BASE_URL (e.g. https://passhub-api-xxx.run.app/api/v1)}"
VITE_APP_NAME="${VITE_APP_NAME:-PassHub}"

echo "▶ Building frontend image: ${IMAGE}:${TAG}"
echo "  VITE_API_BASE_URL=${VITE_API_BASE_URL}"
docker build \
  --platform linux/amd64 \
  --target runtime \
  --build-arg "VITE_API_BASE_URL=${VITE_API_BASE_URL}" \
  --build-arg "VITE_APP_NAME=${VITE_APP_NAME}" \
  -t "${IMAGE}:${TAG}" \
  -f apps/web/Dockerfile \
  .

echo "▶ Pushing ${IMAGE}:${TAG}"
docker push "${IMAGE}:${TAG}"

echo "✓ Frontend image pushed: ${IMAGE}:${TAG}"
