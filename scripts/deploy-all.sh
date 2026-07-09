#!/usr/bin/env bash
# Full build + deploy pipeline for PassHub.
# Run this after setting all required env vars.
#
# Required:
#   export PROJECT_ID=your-gcp-project
#   export VITE_API_BASE_URL=https://passhub-api-XXXXX.run.app/api/v1
#
# Optional:
#   export REGION=us-central1   (default)
#   export TAG=latest            (default)
#
# Usage: ./scripts/deploy-all.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo " PassHub — Full Deploy to GCP"
echo " Project : ${PROJECT_ID:?Set PROJECT_ID}"
echo " Region  : ${REGION:-us-central1}"
echo " Tag     : ${TAG:-latest}"
echo "========================================"

# 1. Configure Docker auth for Artifact Registry
echo ""
echo "▶ Step 1/4 — Configuring Docker auth"
gcloud auth configure-docker "${REGION:-us-central1}-docker.pkg.dev" --quiet

# 2. Build & push backend
echo ""
echo "▶ Step 2/4 — Building & pushing backend"
bash "${SCRIPT_DIR}/build-api.sh"

# 3. Build & push frontend
echo ""
echo "▶ Step 3/4 — Building & pushing frontend"
bash "${SCRIPT_DIR}/build-web.sh"

# 4. Deploy both services
echo ""
echo "▶ Step 4/4 — Deploying to Cloud Run"
bash "${SCRIPT_DIR}/deploy-api.sh"
bash "${SCRIPT_DIR}/deploy-web.sh"

echo ""
echo "========================================"
echo " ✓ Deploy complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Run migrations: ./scripts/migrate.sh"
echo "  2. Update Google OAuth redirect URI in Cloud Console"
echo "  3. Update CORS_ORIGINS in the API Cloud Run service"
echo "  4. Smoke test: https://passhub-api-XXXXX.run.app/api/v1/health"
