#!/usr/bin/env bash
# Deploy the frontend image to Cloud Run.
# Usage: ./scripts/deploy-web.sh
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID}"
REGION="${REGION:-us-central1}"
REPO="passhub"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/passhub-web:${TAG:-latest}"
SERVICE_NAME="passhub-web"

echo "▶ Deploying ${SERVICE_NAME} to Cloud Run (${REGION})"

gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE}" \
  --region="${REGION}" \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --min-instances=0 \
  --max-instances=5 \
  --cpu=1 \
  --memory=512Mi \
  --timeout=30 \
  --project="${PROJECT_ID}"

echo "✓ Frontend deployed."
echo "  URL: $(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)' --project=${PROJECT_ID})"
