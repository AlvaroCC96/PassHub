# GCP Infrastructure

Empty in Sprint 0. This is where Terraform (or equivalent IaC) for the
production targets will live once the platform is ready to deploy:

- Cloud Run services (`api`, `web`)
- Cloud SQL (PostgreSQL) instance
- Cloud Storage buckets (replacing MinIO via `GoogleCloudStorageProvider`)
- Artifact Registry repositories
- Secret Manager entries (mirroring `.env.production`)
- Cloud Monitoring / Cloud Logging sinks
- Cloud Scheduler jobs

No deployment is configured yet — `.gitlab-ci.yml` stops at the `build` stage.
