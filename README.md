# PassHub

PassHub is a multi-module SaaS platform. **DrivePass**, the first module,
lets users store vehicle documentation, grant access via NFC, and extract
document data with AI. This repository currently contains **Sprint 0**: the
platform scaffold, with no business logic implemented yet.

See [docs/architecture.md](docs/architecture.md) for the architectural
decisions and their justification.

## Requirements

- Docker and Docker Compose v2 (`docker compose`, not `docker-compose`)
- Node.js >= 20 and [pnpm](https://pnpm.io) >= 9 (only needed for local
  linting/typechecking outside containers)
- Python 3.13 and [uv](https://docs.astral.sh/uv/) (only needed for running
  the API outside containers)

## Getting started

```bash
cp .env.example .env
docker compose up --build
```

Or, with the bootstrap script (copies `.env`, installs frontend deps, starts
containers):

```bash
./scripts/bootstrap.sh     # macOS/Linux
./scripts/bootstrap.ps1    # Windows
```

Once running:

| Service       | URL                                 |
|---------------|--------------------------------------|
| Web           | http://localhost:5173               |
| API docs      | http://localhost:8000/api/v1/docs   |
| API health    | http://localhost:8000/api/v1/health |
| MinIO console | http://localhost:9001               |
| PgAdmin       | http://localhost:5050               |

## Architecture

Monorepo, Clean Architecture on the backend, ports & adapters for storage,
auth, and (later) notifications/AI. Full rationale in
[docs/architecture.md](docs/architecture.md).

```
PassHub/
  apps/
    web/        React + TypeScript + Vite + TailwindCSS frontend
    api/        FastAPI backend (Clean Architecture: core/domain/application/infrastructure/presentation)
  packages/
    shared/     TypeScript types shared across frontend apps
    ui/         Shared React UI primitives
  infra/
    docker/     nginx, postgres init scripts
    ci/         GitLab CI job definitions
    gcp/        Future Terraform for Cloud Run/SQL/Storage
  docs/         Architecture documentation
  scripts/      Bootstrap and maintenance scripts
```

## Technology stack

**Frontend** — React, TypeScript, Vite, TailwindCSS, TanStack Query, React Router
**Backend** — Python 3.13, FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic V2
**Database** — PostgreSQL
**Storage** — MinIO locally, behind a `StorageProvider` port swappable for
Google Cloud Storage without touching the domain
**Future infrastructure** — Cloud Run, Cloud SQL, Cloud Storage, Artifact
Registry, Secret Manager, Cloud Monitoring/Logging, Cloud Scheduler
**CI** — GitLab CI

## Commands

```bash
make up                  # docker compose up --build
make down                # docker compose down
make logs                # follow container logs
make migrate             # apply Alembic migrations
make revision name="..." # generate a new Alembic migration
make lint                # ruff + eslint
make format               # ruff format + black
make typecheck            # mypy + tsc
make test                 # pytest + vitest
make pre-commit-install   # install git hooks
```

## Testing

Test runners are configured, not yet exercised with business-logic tests:

- **pytest** + **pytest-asyncio** for the API (`apps/api/tests`)
- **Vitest** + **React Testing Library** for the frontend (`apps/web/src`)
- **Playwright** scaffolding for end-to-end tests (`e2e/`)

## Roadmap

- **Sprint 0 (this repository)** — monorepo, Clean Architecture skeleton,
  Docker Compose stack, CI structure, no business logic
- **Sprint 1** — Authentication (JWT + Google OAuth), RBAC enforcement
- **Sprint 2** — DrivePass: vehicles, document upload/storage
- **Sprint 3** — NFC-based access to vehicle documentation
- **Sprint 4** — AI-powered document data extraction
- **Future modules** — HomePass, PetPass, FamilyPass, HealthPass, built on
  the same shared kernel
