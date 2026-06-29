# Modules

Two modules exist today:

- `identity/` — Google login, JWT sessions, refresh-token rotation.
- `platform/` — the module catalog, per-user module enablement, feature
  flags, and platform settings. See [docs/platform-core.md](../../../../docs/platform-core.md).

Every future **business** module (`drivepass`, `homepass`, `petpass`,
`familypass`, `healthpass`) is added here the same way, mirroring the same
Clean Architecture split used by the shared kernel:

```
modules/
  drivepass/
    domain/          # Vehicle, Document, etc. — entities specific to this module
    application/      # use cases, module-specific ports/DTOs
    infrastructure/   # ORM models, concrete repositories
    presentation/     # FastAPI routers mounted under /api/v1/drivepass
```

A module depends on `core`, `domain.base`, and `application.ports` from the
shared kernel (e.g. `StorageProvider`, `Repository`, `UnitOfWork`,
`NewUserProvisioner`) but the shared kernel never depends on a module, and
modules don't import each other's internals — `identity` and `platform` are
wired together only at the presentation layer (`identity/presentation/router.py`
constructs `platform`'s `PlatformUserProvisioner` and passes it through the
`NewUserProvisioner` port). Any new business module follows the same rule.

Modules are registered in `presentation/api/v1/__init__.py` by including
their router, and (if they have stateless adapters) bound in the DI
`Container` — see `identity/infrastructure/bindings.py` for an example.
DrivePass itself is registered in the `platform_modules` catalog
(`platform/infrastructure/seed.py`) as `ACTIVE`, but has no FastAPI router or
business logic yet — only the placeholder frontend page at `/app/drive`.
