# Modules

Three modules exist today:

- `identity/` — Google login, JWT sessions, refresh-token rotation.
- `platform/` — the module catalog, per-user module enablement, feature
  flags, and platform settings. See [docs/platform-core.md](../../../../docs/platform-core.md).
- `drivepass/` — the first **business** module, organized as a bounded
  context with its own internal submodules (`vehicles/` today, `documents/`
  in Sprint 3). See [docs/drivepass-vehicles.md](../../../../docs/drivepass-vehicles.md).

Every future business module (`homepass`, `petpass`, `familypass`,
`healthpass`) is added the same way `drivepass` was, mirroring the same
Clean Architecture split used by the shared kernel:

```
modules/drivepass/
  presentation/router.py   # aggregates submodules under /api/v1/drivepass
  vehicles/
    domain/          # Vehicle, VehicleStatus, FuelType, Transmission
    application/      # VehicleRepository (port), VehicleService
    infrastructure/   # VehicleModel, SqlAlchemyVehicleRepository
    presentation/     # schemas, dependencies, router (mounted at /vehicles)
  documents/           # Sprint 3 — not built yet
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
`drivepass` is registered both as a router (`/api/v1/drivepass`) and in the
`platform_modules` catalog (`platform/infrastructure/seed.py`) as `ACTIVE`.
