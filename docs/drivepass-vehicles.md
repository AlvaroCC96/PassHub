# DrivePass — Vehicle Management

## Modelo

`DrivePass` is a bounded context with internal submodules — `vehicles` today,
`documents` (Sprint 3) next to it:

```
modules/drivepass/
  presentation/router.py        # aggregates submodules under /drivepass
  vehicles/
    domain/        Vehicle entity, VehicleStatus/FuelType/Transmission
    application/   VehicleRepository (port), VehicleService
    infrastructure/  VehicleModel, SqlAlchemyVehicleRepository
    presentation/  schemas, dependencies, router (mounted at /vehicles)
```

`Vehicle` belongs to exactly one user (`user_id`). Ownership is never assumed
— `VehicleService` re-checks it on every read/write by loading the vehicle
and comparing `user_id`, raising the same `404 vehicle_not_found` whether the
vehicle doesn't exist or simply isn't the caller's. This is deliberate: a 403
would confirm a vehicle ID belongs to *someone*.

Two simplifications from how this module could have been split, kept for
consistency with `identity`/`platform`:

- **One `VehicleService`, not a separate "domain service" + "application
  service."** Every other module in this codebase uses a single `*Service`
  per concern; introducing another layer here would be ceremony without new
  behavior.
- **No standalone `VehicleDTO`/`VehicleMapper` classes.** ORM↔domain mapping
  is a free function inside `repositories.py` (`_to_domain`), and the
  Pydantic response schema maps directly from the domain entity
  (`VehicleResponse.from_domain`) — the same pattern `PlatformModuleResponse`
  and `CurrentUserResponse` already use.

## Patente (plate) — normalization and uniqueness

Plates are normalized on every write: uppercased, spaces and dashes
stripped (`normalize_plate` in `domain/entities/vehicle.py`). `ABCD-12`,
`abcd 12`, and `ABCD12` are the same plate.

Uniqueness is **not** a plain `UNIQUE(user_id, plate)` constraint. The
business rule is "no two *active* vehicles share a plate" — a flat unique
constraint would conflict with soft delete (deleting a vehicle would
permanently block ever reusing its plate). Instead:

```sql
CREATE UNIQUE INDEX uq_vehicles_active_user_plate
  ON vehicles (user_id, plate)
  WHERE status = 'ACTIVE' AND deleted_at IS NULL;
```

`VehicleService` also checks this at the application level before writing,
so a violation surfaces as a clean `409 plate_already_registered` instead of
a raw database `IntegrityError`. Verified live: creating, deleting, then
re-creating a vehicle with the same plate works; creating two active
vehicles with the same plate for the same user does not.

## Favorito (favorite)

At most one vehicle per user has `favorite = true`. There's no database
constraint enforcing this (a partial unique index on `favorite` would need
a `WHERE favorite` clause across the whole table per user, which Postgres
doesn't directly support as a simple unique index) — it's enforced by
`VehicleService.set_favorite`, which unfavorites the user's current
favorite (if any) and favorites the target in the same request. Verified:
favoriting vehicle B after vehicle A automatically un-favorites A.

## Validaciones

Enforced in `Vehicle._validate` (domain, not just request schemas — so the
rule holds no matter what calls `Vehicle.register`/`update_details`):

- `plate`, `brand`, `model` are required (non-empty after normalization).
- `year` must be between 1900 and *next calendar year* — computed at
  validation time, not hardcoded, so the upper bound moves with the clock.

File uploads, MIME/extension/size checks, and checksums are **not** part of
this sprint — there's no file storage here yet. That's Sprint 3.

## Endpoints

All under `/api/v1/drivepass/vehicles`, all requiring an authenticated user:

| Method | Path                  | Notes                                          |
| ------ | --------------------- | ----------------------------------------------- |
| GET    | `/`                   | Lists the caller's vehicles                      |
| GET    | `/favorite`           | 404 if none set — declared before `/{id}` so FastAPI doesn't match it as an id |
| GET    | `/{vehicle_id}`       | 404 if missing or not owned                      |
| POST   | `/`                   | 201; 409 on duplicate active plate               |
| PUT    | `/{vehicle_id}`       | Full update; 409 on plate conflict with another vehicle |
| DELETE | `/{vehicle_id}`       | 204; soft delete (archives + frees the plate)    |
| PATCH  | `/{vehicle_id}/favorite` | Sets favorite, unsets any previous one        |

## Auditoría

`vehicle_created`, `vehicle_updated`, `vehicle_deleted`, `vehicle_favorited`
— structured log entries tagged `category="drivepass.audit"`, the same
pattern Identity and Platform Core use (no event bus exists yet; see
`docs/platform-core.md` for why that's deferred rather than built per-module).

## Frontend

Routes: `/app/drive` (hub — vehicle preview + "coming soon" cards for
Documents/NFC/AI/Expiration Alerts), `/app/drive/vehicles` (full list),
`/app/drive/vehicles/new`, `/app/drive/vehicles/:vehicleId`,
`/app/drive/vehicles/:vehicleId/edit`. Each vehicle page has a contextual
"← Back to ..." link (list → DrivePass hub, detail → My Vehicles, form →
the vehicle being edited or the list when creating).

`VehicleForm` is shared between create and edit — same component, same
inline validation, different submit handler (`useCreateVehicle` vs.
`useUpdateVehicle`).

## Seguridad

- Every vehicle endpoint requires a valid access token (`CurrentUser`
  dependency) — no public vehicle data exists.
- Ownership is re-verified server-side on every request; the frontend never
  decides what a user can see.
- No vehicle data leaves the database to a third party in this sprint —
  there's no file storage, no public portal, no NFC.

## Próximo sprint

Sprint 3 adds `modules/drivepass/documents/` next to `vehicles/` — file
storage via the existing `StorageProvider` port, document versioning, and
signed URLs. `nfc_uuid`, `public_pin_hash`, `public_enabled`, and
`vehicle_score` already exist on `Vehicle` (unused) for the NFC/public-portal
sprint after that.
