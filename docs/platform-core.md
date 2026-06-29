# Platform Core

## What PassHub Core is

PassHub is not DrivePass with a different name on the login screen. The
**Platform Core** — Identity, the module catalog, per-user module
enablement, feature flags, and platform settings — is the product. DrivePass
is the first **module** built on top of it; HomePass, PetPass, HealthPass,
and FamilyPass are meant to be added the same way, without the core ever
needing to know what a vehicle or a pet is.

This sprint builds that core. It deliberately implements zero business logic
for any module — no vehicles, no documents, no AI, no NFC. What it does
implement is the machinery that lets a module *exist* on the platform:
declared in a catalog, turned on or off per user, gated behind a feature
flag, and given a place to render in the frontend.

## What a module is

A `PlatformModule` is a catalog row: a `code` (`DRIVE_PASS`, `HOME_PASS`, ...),
display metadata (name, description, icon, route), and a lifecycle `status`:

| Status        | Meaning                                                      |
| -------------- | ------------------------------------------------------------- |
| `ACTIVE`       | Real, can be enabled/disabled by users                       |
| `COMING_SOON`  | Visible in the catalog, shown locked, cannot be enabled       |
| `INACTIVE`     | Hidden from the catalog entirely                              |
| `DEPRECATED`   | Hidden from the catalog entirely                              |

Module *display* fields and status are owned by code (`platform/infrastructure/seed.py`),
not by an admin UI — there isn't one yet. Re-running the seed re-syncs them.

## How modules get enabled per user

Whether *a module exists* and whether *a specific user has it on* are two
different things, modeled as two different entities:

- `PlatformModule` — the catalog row, platform-wide.
- `UserModule` — one row per `(user_id, module_id)` pair, `ENABLED` or
  `DISABLED`.

`UserModuleService` is the only thing that writes `UserModule` rows. It
enforces the rules the sprint asked for: only `ACTIVE` modules can be
enabled, core modules can't be disabled, and enabling twice never creates a
duplicate row (the unique constraint on `(user_id, module_id)` backs that up
at the database level too, not just in application code).

## DrivePass auto-enable: the Identity ↔ Platform seam

When a brand-new user registers through Google, DrivePass should already be
on. Identity doesn't import Platform to make that happen — it depends on a
port:

```python
# application/ports/user_provisioning.py (shared kernel)
class NewUserProvisioner(Protocol):
    async def on_user_registered(self, *, user_id: UUID) -> None: ...
```

`LoginWithGoogleUseCase` calls this port once, right after persisting a new
user — it has no idea who implements it. `platform/infrastructure/user_provisioner.py`
provides `PlatformUserProvisioner`, which wraps `UserModuleService.enable_default_modules_for_new_user`.
The two are wired together in exactly one place: `identity/presentation/router.py`'s
`/auth/callback` endpoint constructs the concrete adapter and passes it into
the use case. Nothing in Identity's domain or application layer — and
nothing in `/auth/callback`'s request/response contract — changed to make
this work.

This is the same dependency-inversion pattern the rest of the platform uses
for storage (`StorageProvider`) and auth (`TokenService`, `Hasher`): a port
in the shared kernel, a concrete adapter in the module that cares, wired at
the composition/presentation layer.

**Known limitation:** this hook only fires for *new* registrations. Accounts
created during the Identity sprint, before Platform existed, have no
`UserModule` rows at all — they'll see every module as not-enabled until they
enable DrivePass themselves from the dashboard. There's no backfill migration
for this; it wasn't worth one for a handful of pre-Platform test accounts in
an unreleased product, but it's worth knowing about before assuming "every
user has DrivePass."

## Feature flags

`FeatureFlag` is a key/enabled/scope row, nothing more — there is no rules
engine. `FeatureFlagService.list_relevant_for_user` applies the only
relevance rule implemented so far:

- `GLOBAL` flags are relevant to everyone.
- `MODULE` flags are relevant only if the caller has that specific module
  enabled (checked by mapping the flag's `module_code` to the user's enabled
  `PlatformModule` rows — not by string-matching the key).
- `USER` flags are returned as-is; per-user overrides aren't modeled yet
  (none are seeded).

`drivepass.enabled` is seeded as `MODULE`-scoped — it only shows up in
`GET /platform/feature-flags` for a user who has DrivePass turned on, which
was verified against a real account during this sprint (enabling DrivePass
makes the flag appear; disabling it makes it disappear).

## Platform settings

`PlatformSetting` is a JSON-valued key/value row (`platform.public_brand_name`,
`platform.default_module`). There is no `is_public` flag yet — every setting
seeded today is meant to be public, so `GET /platform/settings/public` (the
only unauthenticated endpoint in this router) returns all of them. Add an
`is_public` column before seeding anything that shouldn't be world-readable.

## Endpoints

| Method | Path                                       | Auth | Notes                                  |
| ------ | ------------------------------------------- | ---- | --------------------------------------- |
| GET    | `/api/v1/platform/modules`                  | yes  | All `ACTIVE`/`COMING_SOON` modules, flagged with `is_enabled` for the caller |
| GET    | `/api/v1/platform/modules/enabled`          | yes  | Subset where `is_enabled` is true        |
| POST   | `/api/v1/platform/modules/{code}/enable`    | yes  | 409 if not `ACTIVE`                      |
| POST   | `/api/v1/platform/modules/{code}/disable`   | yes  | 409 if core or not currently enabled     |
| GET    | `/api/v1/platform/feature-flags`            | yes  | Filtered by the relevance rule above     |
| GET    | `/api/v1/platform/settings/public`          | no   | The only public endpoint in this router  |

## Frontend

`/app` is the dashboard — sections for the user's enabled modules, modules
available to enable, and modules coming soon, built from a single
`GET /platform/modules` call (`usePlatformModules`). `/app/drive` is
DrivePass's placeholder: title, subtitle, and five static cards
(Vehicles/Documents/NFC Access/AI Extraction/Expiration Alerts), explicitly
not implementing any of them yet.

`ModuleCard` renders three states: enabled (a link to `route_path`),
`COMING_SOON` (locked, badge, no interaction), and active-but-not-enabled
(a button that calls `POST /platform/modules/{code}/enable` and refetches).

## Rules enforced (and where)

- Only `ACTIVE` modules are enableable — `UserModuleService.enable`, backed
  by a unit test (`test_enable_coming_soon_module_is_rejected`).
- Core modules can't be disabled — `UserModuleService.disable`
  (`test_disable_core_module_is_rejected`). No seeded module is core today;
  the rule exists for when one is.
- Enabling twice never duplicates — the unique `(user_id, module_id)`
  constraint plus `UserModuleService.enable`'s existing-row check
  (`test_enabling_twice_does_not_duplicate_user_module`).
- `INACTIVE`/`DEPRECATED` modules never appear as available —
  `PlatformModuleService.list_visible_modules` filters them out before
  anything downstream sees them.
- All `/platform/*` endpoints require an authenticated user except
  `/platform/settings/public`.

## A bug this sprint actually hit

The frontend's dashboard route is `/app`, per spec. The web container's
Docker `WORKDIR` was also `/app` — and Vite's dev-server static middleware,
finding no client-side route to serve, falls back to resolving the request
path against the OS filesystem. A request for `/app` resolved to the
container's own root directory, which exists, so Vite tried to `read()` a
directory and crashed with `EISDIR`. Fixed by moving the web container's
`WORKDIR` to `/workspace` — confirmed working in both the Vite dev server and
the Nginx production build.
