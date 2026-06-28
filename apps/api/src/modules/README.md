# Modules

This directory is intentionally empty in Sprint 0.

Each future business module (`drivepass`, `homepass`, `petpass`, `familypass`,
`healthpass`) will be added here as its own bounded context, mirroring the
same Clean Architecture split used by the shared kernel:

```
modules/
  drivepass/
    domain/          # Vehicle, Document, etc. — entities specific to this module
    application/      # use cases, module-specific ports/DTOs
    infrastructure/   # ORM models, concrete repositories
    presentation/     # FastAPI routers mounted under /api/v1/drivepass
```

A module depends on `core`, `domain.base`, and `application.ports` from the
shared kernel (e.g. `StorageProvider`, `Repository`, `UnitOfWork`) but the
shared kernel never depends on a module. This is what keeps `vehicles`,
`pets`, or any other business concept out of the reusable platform code.

Modules are registered in `presentation/main.py` by including their router
and binding their concrete adapters in the DI `Container` — no module is
registered yet.
