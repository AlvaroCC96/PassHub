#!/usr/bin/env bash
# Build and push the backend Docker image to Artifact Registry.
# Usage: ./scripts/build-api.sh
# Required env vars: PROJECT_ID, REGION (defaults below)
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID}"
REGION="${REGION:-us-central1}"
REPO="passhub"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/passhub-api"
TAG="${TAG:-latest}"

echo "▶ Building backend image: ${IMAGE}:${TAG}"
docker build \
  --platform linux/amd64 \
  -t "${IMAGE}:${TAG}" \
  -f apps/api/Dockerfile \
  apps/api/

echo "▶ Pushing ${IMAGE}:${TAG}"
docker push "${IMAGE}:${TAG}"

echo "✓ Backend image pushed: ${IMAGE}:${TAG}"
