#!/usr/bin/env bash
# Deploy the backend image to Cloud Run.
# All secrets must already exist in Secret Manager before running this.
# Usage: ./scripts/deploy-api.sh
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID}"
REGION="${REGION:-us-central1}"
REPO="passhub"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/passhub-api:${TAG:-latest}"
SERVICE_NAME="passhub-api"

echo "▶ Deploying ${SERVICE_NAME} to Cloud Run (${REGION})"

gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE}" \
  --region="${REGION}" \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --min-instances=0 \
  --max-instances=10 \
  --cpu=1 \
  --memory=1Gi \
  --timeout=60 \
  --set-env-vars="ENVIRONMENT=production,DEBUG=false,LOG_JSON=true" \
  --set-secrets="\
POSTGRES_HOST=passhub-db-host:latest,\
POSTGRES_PASSWORD=passhub-db-password:latest,\
POSTGRES_USER=passhub-db-user:latest,\
POSTGRES_DB=passhub-db-name:latest,\
SECURITY_JWT_SECRET=passhub-jwt-secret:latest,\
SECURITY_GOOGLE_OAUTH_CLIENT_ID=passhub-google-client-id:latest,\
SECURITY_GOOGLE_OAUTH_CLIENT_SECRET=passhub-google-client-secret:latest,\
OPENAI_API_KEY=passhub-openai-api-key:latest" \
  --project="${PROJECT_ID}"

echo "✓ Backend deployed."
echo "  URL: $(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)' --project=${PROJECT_ID})"
