# PassHub Architecture

## Why a monorepo

`apps/web` and `apps/api` evolve together at this stage, and `packages/shared`
/ `packages/ui` need to be consumed by source (not published) during early
development. pnpm workspaces gives that without adopting a build-orchestration
tool (Nx/Turborepo) before there is a second app to justify it.

## Why the backend is not organized around "vehicles"

DrivePass is the first module, not the product. The backend separates a
**shared kernel** — reusable by every future module — from **modules**, which
are bounded contexts:

```
apps/api/src/
  core/            cross-cutting concerns: config, logging, DI, exceptions, middleware, security primitives
  domain/          shared kernel domain primitives: Entity, AggregateRoot, ValueObject, DomainEvent
  application/     ports (StorageProvider, Repository, UnitOfWork) + generic DTOs
  infrastructure/  concrete adapters: MinIOStorageProvider, DB session/mixins, JWT helpers
  presentation/    FastAPI app factory, versioned routers (/api/v1)
  modules/         empty in Sprint 0 — see modules/README.md
```

A module (`drivepass`, `homepass`, ...) will depend on `core`, `domain.base`
and `application.ports`. The shared kernel never depends on a module. This is
the dependency rule that keeps "vehicle", "document", "pet" out of reusable
platform code.

## Ports & Adapters for cross-cutting capabilities

Storage, auth and (later) notifications/AI are defined as **ports** —
`Protocol` classes in `application/ports` — with concrete **adapters** in
`infrastructure/*`. `StorageProvider` is implemented today by
`MinIOStorageProvider`; a `GoogleCloudStorageProvider` will implement the same
port later. Nothing above the infrastructure layer changes when that happens —
only the binding registered in the DI `Container` (`core/di/container.py`).

## Database

No business tables exist yet. `infrastructure/database/mixins.py` defines
`UUIDMixin`, `TimestampMixin`, `SoftDeleteMixin`, and `AuditMixin` — every
future ORM model composes these instead of redefining identity, timestamps,
soft-delete, and audit columns per table. Alembic is wired to the async engine
and ready to autogenerate migrations once the first model is added.

## Security posture (prepared, not implemented)

`core/security/roles.py` defines the `Role` enum (`user`, `admin`).
`infrastructure/auth/jwt_handler.py` and `oauth_config.py` fix the shape JWT
issuance and Google OAuth will take. No login endpoint, password hashing, or
authorization middleware exists yet — Sprint 0 deliberately stops at the
contract.

## Domain events

`domain/events/base.py` defines `DomainEvent`. No dispatcher/event bus is
wired up. `AggregateRoot.record_event` / `pull_domain_events` exist so a
future use case can raise events without redesigning the base entity later.

## Observability

`core/middleware/request_id.py` assigns and propagates `X-Request-ID`,
binding it into every structured log line via `structlog` contextvars.
`infrastructure/observability/tracing.py` wires OpenTelemetry's
`TracerProvider` behind `OTEL_ENABLED` — disabled by default, no exporter
attached, no metrics shipped.

## Frontend

`apps/web` has no feature beyond what Sprint 0 requires: a router with five
routes (`/`, `/dashboard`, `/login`, an auth layout, and a catch-all 404), a
`ThemeProvider` for dark mode persisted to `localStorage`, and a typed
`apiFetch` wrapper around the versioned API. `packages/ui` holds the first two
genuinely shared primitives (`Button`, `Spinner`); everything else stays in
`apps/web` until a second consumer actually needs it.

## Configuration

Every setting is read once, centrally, in `apps/api/src/core/config/settings.py`
via `pydantic-settings`. No module calls `os.environ` directly. The frontend
mirrors this with a single `import.meta.env.VITE_API_BASE_URL` read inside
`lib/api-client.ts`.
