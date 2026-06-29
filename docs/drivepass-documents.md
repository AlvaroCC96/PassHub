# DrivePass — Document Management

## Modelo

`documents` is a second submodule inside `drivepass`, alongside `vehicles`,
mounted under the same vehicle in the aggregator router:

```
modules/drivepass/
  presentation/router.py        # aggregates submodules under /drivepass
  vehicles/                     # Sprint 2
  documents/
    domain/
      value_objects/  DocumentType, DocumentStatus, DocumentVisibility, OverallDocumentStatus
      rules.py        which document types are required, conditionally required, or optional
      file_validation.py  size/MIME/extension checks, checksum
      entities/        VehicleDocument, DocumentVersion
    application/
      ports/           VehicleDocumentRepository, DocumentVersionRepository (protocols)
      dto.py           DocumentStatusSummary
      storage_paths.py build_storage_key(...)
      services/        VehicleDocumentService
    infrastructure/    VehicleDocumentModel, DocumentVersionModel, repositories, StorageProvider bindings
    presentation/      schemas, dependencies (ownership), router (mounted at /vehicles/{vehicle_id}/documents)
```

Documents depend directly on Vehicles (`get_owned_vehicle` in
`documents/presentation/dependencies.py` calls `VehicleService.get_for_user`)
because both are submodules of the same `drivepass` module — no port is
needed for that, unlike cross-module dependencies (Identity↔Platform), which
always go through a port.

A `VehicleDocument` is one *slot* per `(vehicle_id, document_type)` — it
always exists once a vehicle is created (lazily, see below) even with no
file uploaded yet, so the checklist UI always has something to render.
A `DocumentVersion` is one uploaded file; `VehicleDocument.current_version_id`
points at the active one. Replacing a document creates a new version and
marks the previous one as not current — nothing is ever overwritten or
deleted in storage.

## Checklist automático

There's no explicit "create the checklist" step. `VehicleDocumentService`
lazily creates a `MISSING` row for any of the 7 vehicle document types
(`VEHICLE_DOCUMENT_TYPES`, everything except `LICENCIA_CONDUCIR`, which
belongs to the user, not the vehicle) that doesn't already exist for that
vehicle, every time the vehicle's documents are listed or summarized
(`_ensure_initialized`). This also means deleting a document (soft delete)
and then listing again recreates it as `MISSING` — verified live, including
through the unique-index fix described below.

## Tipos de documento y reglas de obligatoriedad

`domain/rules.py`:

- **Always required**: `PADRON`, `SOAP`, `PERMISO_CIRCULACION`.
- **Conditionally required**: `REVISION_TECNICA`, `CERTIFICADO_GASES` — each
  only required if the vehicle doesn't already have a *valid* (non-expired,
  uploaded) `CERTIFICADO_HOMOLOGACION`. `is_required` is recomputed on every
  sync, not fixed at creation.
- **Always optional**: `SEGURO_PARTICULAR`, and `CERTIFICADO_HOMOLOGACION`
  itself (it's the *condition* the other two check, not a required document
  on its own).
- `LICENCIA_CONDUCIR` exists as an enum value (placeholder for a future
  user-level, not vehicle-level, document) but is excluded from
  `VEHICLE_DOCUMENT_TYPES` and never created by this service.

## Estado del documento

`VehicleDocument.recompute_status` derives status purely from
`current_version_id` and `expiration_date` — it's a pure function of state,
not something set imperatively at upload time, so it stays correct as the
clock moves forward even with no new writes:

- No version uploaded → `MISSING`.
- Version uploaded, no `expiration_date` → `UPLOADED`.
- Version uploaded, `expiration_date` in the past → `EXPIRED`.
- Version uploaded, `expiration_date` within `EXPIRING_SOON_WINDOW_DAYS`
  (30 days) → `EXPIRING_SOON`.
- Version uploaded, `expiration_date` further out → `VALID`.

`REJECTED` and `NOT_APPLICABLE` are not derived — out of scope for this
sprint (no review/moderation flow exists), kept only as enum values for a
future sprint.

`_sync_all` recomputes every document's status (and `is_required` for
conditional types) on every list/summary call, using the current date —
verified live that a document's status flips from `VALID` to
`EXPIRING_SOON` purely by changing its `expiration_date`, no other write
needed.

## Validación de archivos

`domain/file_validation.py` — no `python-magic`/`libmagic` dependency,
just raw magic-byte sniffing on the first bytes of the upload:

| Sniffed type | Magic bytes              | Allowed extensions |
| ------------ | ------------------------- | ------------------- |
| PDF          | `%PDF-`                   | `.pdf`               |
| JPEG         | `\xff\xd8\xff`             | `.jpg`, `.jpeg`      |
| PNG          | `\x89PNG\r\n\x1a\n`         | `.png`               |
| WEBP         | `RIFF....WEBP`             | `.webp`              |

`validate_upload` rejects (with a specific error code, not a generic 400):
empty files (`empty_file`), files over 10 MB (`file_too_large`), content
whose sniffed type isn't in the allow-list (`unsupported_file_type`), a
sniffed type that doesn't match the declared filename's extension
(`file_content_mismatch`), and filenames with no extension
(`missing_file_extension`). The declared `Content-Type` header is never
trusted — only the sniffed bytes are. `compute_checksum` (sha256) is stored
per version for integrity, not currently surfaced to the client.

## Almacenamiento

Files go to MinIO (local) / GCS (future) through the existing
`StorageProvider` port — first real consumer of that port outside its own
infrastructure tests. Storage key layout
(`application/storage_paths.py`):

```
users/{user_id}/vehicles/{vehicle_id}/documents/{document_type}/{version_id}/{filename}
```

Keyed by `version_id`, not overwritten in place — every version's file
stays in the bucket even after being superseded or soft-deleted at the
metadata level.

Downloads never proxy through the API or return a raw bucket URL — every
download request mints a fresh presigned URL
(`get_download_url`, 300s expiry) and logs an audit event, which is why the
frontend hook for it (`useDocumentDownloadUrl`) is a mutation, not a query:
each call has a side effect (a new signed URL, a new audit log line), not
just a cached read.

Two MinIO clients exist in `MinIOStorageProvider`: one using the internal
Docker service-discovery hostname for all object operations, and a second
("public") client used only for `get_presigned_url`, pointed at
`STORAGE_PUBLIC_ENDPOINT` (`localhost:9000` locally) — otherwise the signed
URL would contain a hostname unreachable from outside Docker. Both clients
pin `region` (`STORAGE_REGION`, default `us-east-1`) so the MinIO SDK
doesn't make a live region-lookup network call against an endpoint that
isn't reachable from where the call originates before signing.

## Unicidad y soft delete

Same pattern as the vehicle plate (`docs/drivepass-vehicles.md`): a flat
`UniqueConstraint(vehicle_id, document_type)` would permanently block
re-creating a document slot after a soft delete. Fixed with a partial
unique index instead:

```sql
CREATE UNIQUE INDEX uq_vehicle_documents_vehicle_type
  ON vehicle_documents (vehicle_id, document_type)
  WHERE deleted_at IS NULL;
```

Verified live: soft-deleting a document, then listing the vehicle's
documents again, recreates that type as a fresh `MISSING` row instead of
raising `IntegrityError`.

## Endpoints

All under `/api/v1/drivepass/vehicles/{vehicle_id}/documents`, all requiring
an authenticated user who owns `vehicle_id` (enforced by `get_owned_vehicle`,
which reuses `VehicleService.get_for_user` and raises the same
`404 vehicle_not_found` whether the vehicle doesn't exist or isn't the
caller's):

| Method | Path                              | Notes                                                    |
| ------ | ---------------------------------- | --------------------------------------------------------- |
| GET    | `/`                                 | Lists all 7 document slots, auto-initializing missing ones |
| GET    | `/status`                           | Aggregate summary; declared before `/{document_id}` to avoid path collision |
| POST   | `/`                                 | Initial upload for a document type (multipart)             |
| GET    | `/{document_id}`                    | Single document detail                                     |
| POST   | `/{document_id}/versions`           | Replace — uploads a new version (multipart)                 |
| GET    | `/{document_id}/versions`           | Version history, newest first                               |
| GET    | `/{document_id}/download-url`       | Mints a fresh presigned URL (300s)                           |
| DELETE | `/{document_id}`                    | 204; soft delete                                            |

All five endpoints that mutate state (`POST /`, `POST .../versions`,
`DELETE /{document_id}`, and the lazy-init side effect inside `GET /` and
`GET /status`) explicitly `await session.commit()` — there's no
commit-on-response middleware in this codebase, so a route that forgets it
silently no-ops the write while still returning a success response. This
was caught live (a 201 upload response with nothing persisted in Postgres)
before being fixed across all of them.

## Auditoría

`document_uploaded`, `document_version_created`, `document_download_url_created`,
`document_deleted`, `document_status_calculated` — `category="drivepass.audit"`,
same structlog pattern as Vehicles and every other module.

## Frontend

Routes: `/app/drive/vehicles/:vehicleId/documents` (checklist + status
summary for one vehicle) and
`/app/drive/vehicles/:vehicleId/documents/:documentId` (single document,
its versions, upload/replace/view/delete actions). Reached from a
"Documents" button on `VehicleDetailPage`, next to Edit/Remove.

Uploads go through `FormData`, not JSON — `apiFetch` (`lib/api-client.ts`)
detects a `FormData` body and skips forcing `Content-Type: application/json`
so the browser can set the multipart boundary itself.
`DocumentUploadModal` is shared between initial upload (`documentType` prop)
and replace (`documentId` prop) — same dropzone, same validation feedback,
different mutation underneath.

## Seguridad

- Every document endpoint requires a valid access token and re-verifies
  vehicle ownership server-side — no public document data exists yet
  (`PUBLIC_AFTER_PIN` visibility and the public vehicle portal are out of
  scope for this sprint).
- Uploaded file content is sniffed and validated server-side regardless of
  what the client claims; the declared `Content-Type` is never trusted.
- Signed download URLs expire in 5 minutes and are minted per-request, never
  cached or reused across requests.

## Fuera de alcance (explícito)

No OCR/AI extraction, no NFC, no expiration notifications, no driver's
license implementation (enum placeholder only), no public PIN/QR sharing,
no document review/moderation (`REJECTED` status unused), no advanced admin
tooling. These are reserved for later sprints per the roadmap.

## Próximo sprint

Sprint 4 (per the roadmap) adds NFC-based access to vehicle documentation,
building on `nfc_uuid`/`public_pin_hash`/`public_enabled` already present
(unused) on `Vehicle`.
