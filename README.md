# PassHub

PassHub is a multi-module SaaS platform. The **Platform Core** (Identity,
modules, feature flags, settings) is the product — **DrivePass** is its first
business module, not the whole system. Future modules (HomePass, PetPass,
HealthPass, FamilyPass) plug into the same core without it knowing anything
about vehicles, pets, or houses.

See [docs/architecture.md](docs/architecture.md) for the Sprint 0 scaffold
rationale and [docs/platform-core.md](docs/platform-core.md) for how modules,
per-user enablement, and feature flags fit together.

## Requirements

- Docker and Docker Compose v2 (`docker compose`, not `docker-compose`)
- Node.js >= 20 and [pnpm](https://pnpm.io) >= 9 (only needed for local
  linting/typechecking outside containers)
- Python 3.13 and [uv](https://docs.astral.sh/uv/) (only needed for running
  the API outside containers)
- A Google OAuth 2.0 client (Web application) if you want to exercise login —
  see [docs/platform-core.md](docs/platform-core.md#local-google-oauth-setup)

## Getting started

```bash
cp .env.example .env
# fill in SECURITY_GOOGLE_OAUTH_CLIENT_ID / SECURITY_GOOGLE_OAUTH_CLIENT_SECRET in .env
docker compose up --build
make migrate
make seed
```

Or, with the bootstrap script (copies `.env`, installs frontend deps, starts
containers):

```bash
./scripts/bootstrap.sh     # macOS/Linux
./scripts/bootstrap.ps1    # Windows
```

Once running:

| Service       | URL                                  |
| ------------- | ------------------------------------- |
| Web           | http://localhost:5173                |
| API docs      | http://localhost:8000/api/v1/docs    |
| API health    | http://localhost:8000/api/v1/health  |
| MinIO console | http://localhost:9001                |
| PgAdmin       | http://localhost:5050                |

Sign in at `/login` ("Continue with Google") and you'll land on `/app`, the
platform dashboard — DrivePass is enabled by default for every new account
and opens a placeholder at `/app/drive`.

## Architecture

Monorepo, Clean Architecture on the backend (`core`/`domain`/`application`/
`infrastructure`/`presentation`), ports & adapters for storage, auth, and
module enablement. Full rationale in [docs/architecture.md](docs/architecture.md).

```
PassHub/
  apps/
    web/        React + TypeScript + Vite + TailwindCSS frontend
    api/        FastAPI backend
      src/
        core/                  config, logging, DI, exceptions, middleware
        domain/, application/  shared-kernel domain primitives and ports
        infrastructure/        JWT, Argon2, MinIO/GCS, DB session & mixins
        modules/
          identity/            Google login, JWT sessions, refresh tokens
          platform/            module catalog, per-user enablement, feature flags, settings
          README.md            how a future business module (drivepass/...) plugs in
  packages/
    shared/     TypeScript types shared across frontend apps
    ui/         Shared React UI primitives
  infra/
    docker/     nginx, postgres init scripts
    ci/         GitLab CI job definitions
    gcp/        Future Terraform for Cloud Run/SQL/Storage
  docs/         Architecture and platform documentation
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
make seed                # idempotent platform seed (modules, feature flags, settings)
make lint                # ruff + eslint
make format               # ruff format + black
make typecheck            # mypy + tsc
make test                 # pytest + vitest
make pre-commit-install   # install git hooks
```

## Testing

- **pytest** for the API (`apps/api/tests`) — unit tests for `UserModuleService`
  business rules (enable/disable, COMING_SOON rejection, no duplicates, default
  module on signup) plus the Sprint 0 health-check integration test
- **Vitest** + **React Testing Library** for the frontend (`apps/web/src`) —
  `ModuleCard` and the DrivePass placeholder page
- **Playwright** scaffolding for end-to-end tests (`e2e/`), not yet written

## Roadmap

- **Sprint 0** — monorepo, Clean Architecture skeleton, Docker Compose stack,
  CI structure, no business logic
- **Sprint 1** — Identity: Google OAuth login, JWT access tokens, rotated
  refresh tokens, basic dashboard
- **Sprint 1.5 (this repository)** — Platform Core: module catalog, per-user
  module enablement, feature flags, platform settings, DrivePass shown as a
  module (not the app), HomePass/PetPass/HealthPass/FamilyPass as
  coming-soon placeholders
- **Sprint 2** — DrivePass: vehicles, document upload/storage
- **Sprint 3** — NFC-based access to vehicle documentation
- **Sprint 4** — AI-powered document data extraction
- **Future modules** — HomePass, PetPass, FamilyPass, HealthPass, built on
  the same Platform Core
