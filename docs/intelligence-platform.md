# Intelligence Platform — AI Document Extraction

## Modelo

`intelligence` is a new **top-level module**, a sibling of `identity`,
`platform`, and `drivepass` — not a submodule of `drivepass`. Submodules of
the same module (`vehicles`/`documents`) are allowed to depend on each other
directly; Intelligence and DrivePass are different modules, so they
communicate through a port, the same pattern Identity and Platform already
use for `NewUserProvisioner`:

```
modules/
  intelligence/
    domain/
      value_objects/  ExtractionStatus, ExtractableDocumentType, EXTRACTABLE_FIELD_NAMES
      rules.py         normalize_plate, plate_matches, confidence_band (mirrors DrivePass's own rules by value)
      prompts.py        PROMPT_VERSION, build_prompt(), build_json_schema()
      entities/         DocumentExtraction, DocumentExtractedField
    application/
      ports/            VehicleDocumentGateway (port Intelligence defines), DocumentExtractionRepository, DocumentExtractedFieldRepository
      cost_estimator.py AICostEstimator
      services/         DocumentExtractionService
    infrastructure/
      models.py         DocumentExtractionModel, DocumentExtractedFieldModel
      repositories.py
      parsers/pdf_text_extractor.py
      bindings.py        register_intelligence_bindings — binds AIProvider to OpenAIProvider
    presentation/
      dependencies.py, schemas.py, router.py (mounted at /intelligence)
  drivepass/
    infrastructure/
      intelligence_gateway.py  # DrivePassDocumentGateway — implements Intelligence's port
```

**Why a port instead of direct imports**: Identity/Platform's existing port
(`NewUserProvisioner`) is a one-way *notification* — Identity doesn't need
anything back. Intelligence's relationship with DrivePass is different: it
needs to *read* a document's file and *write back* confirmed metadata. That's
still a real cross-module dependency, so it gets the same treatment —
Intelligence declares the shape it needs (`VehicleDocumentGateway`, in its
own `application/ports/`), and `drivepass/infrastructure/intelligence_gateway.py`
implements it using DrivePass's existing `VehicleDocumentRepository`,
`DocumentVersionRepository`, `StorageProvider`, and `VehicleService` — the
one file in the codebase that imports both modules. Intelligence's
domain/application layers never import anything from `src.modules.drivepass`;
`ExtractableDocumentType` mirrors `DocumentType`'s 7 vehicle-document values
independently, by value, the same way the frontend mirrors backend enums.

The gateway is constructed in `intelligence/presentation/dependencies.py` by
composing DrivePass's own public dependency-providers via FastAPI `Depends`
— the same presentation-layer composition Identity's router already uses to
hand Platform's `UserModuleService` to `PlatformUserProvisioner`.

## AIProvider — provider abstraction

`src/application/ports/ai_provider.py` defines `AIProvider` (one method,
`extract(request) -> result`, both provider-agnostic dataclasses) at the
shared-kernel level, the same tier as `StorageProvider`. `OpenAIProvider`
(`src/infrastructure/ai/openai_provider.py`) is the only real adapter today,
using the **Responses API with Structured Outputs** (`text.format` = a
strict JSON Schema) — the model cannot return a shape the service doesn't
expect; a malformed response is treated as a parse failure, not trusted.

`GeminiProvider`, `ClaudeProvider`, `LocalProvider` are reserved names (see
`AISettings.provider`'s `Literal`) — no adapters exist yet.
`register_intelligence_bindings` is the one place that picks the adapter
from `AI_PROVIDER`; nothing above `AIProvider` would need to change to add
one.

An `OCRProvider` port is declared (`src/application/ports/ai_provider.py`)
but has **no implementation** — reserved for a future OCR fallback (see
Roadmap below).

## Variables de entorno

```
OPENAI_API_KEY=        # deliberately NOT under the AI_ prefix — the conventional name
AI_PROVIDER=openai      # openai | gemini | claude | local (only openai has an adapter)
AI_MODEL=gpt-4o-mini    # passed straight to the provider, fully configurable
```

The key lives in `.env` only (gitignored) — `.env.development` (committed)
always ships with `OPENAI_API_KEY=` empty. It's read once into
`AISettings.openai_api_key` and never logged, never returned by any
endpoint, never stored in the database — `DocumentExtraction.provider`
stores `"openai"`, never the key.

## Feature flag

Gated by `ai.document_extraction.enabled` (seeded `GLOBAL`, `enabled=False`
by default — see `platform/infrastructure/seed.py`, already seeded before
this sprint as a placeholder). `require_ai_extraction_enabled`
(`intelligence/presentation/dependencies.py`) is a router-level dependency
on `POST /documents/{id}/extract` and `POST /documents/{id}/reprocess` —
disabled returns `403 ai_extraction_disabled`, not a silent no-op. The
frontend mirrors this with `useFeatureFlag("ai.document_extraction.enabled")`
(`apps/web/src/platform/useFeatureFlags.ts`) — the "Analizar con IA" section
on a document's detail page doesn't render at all when the flag is off.

Toggle it: `UPDATE feature_flags SET enabled = true WHERE key = 'ai.document_extraction.enabled';`
(no admin UI yet).

## Flujo de extracción

1. `POST /intelligence/documents/{document_id}/extract` — `DocumentExtractionService.extract`
   calls the gateway's `get_source_document` (ownership-checked: 404 for a
   document that doesn't exist or isn't the caller's vehicle), which returns
   file bytes + content type + the vehicle's current plate.
2. The raw `document_type` string is parsed into `ExtractableDocumentType`;
   anything that doesn't parse (e.g. `LICENCIA_CONDUCIR`) is rejected with
   `422 unsupported_document_type` before any AI call.
3. **Images** are base64-encoded and sent as visual input. **PDFs** are run
   through `extract_pdf_text` (`pypdf`, no OCR) first; if there's no usable
   text layer, the extraction is saved as `FAILED` with a clear
   `error_message` — no AI call is made (saves cost), and no OCR fallback
   exists yet.
4. The prompt (`domain/prompts.py`, versioned `drivepass-document-extraction-v1`)
   and a strict JSON Schema (one entry per field, built dynamically per
   document type from `EXTRACTABLE_FIELD_NAMES`) go to `AIProvider.extract`.
5. The response is validated again at the application layer (shape, key set,
   `document_type` echo) — even though Structured Outputs already enforces
   the schema, a `FAILED` extraction is always preferred over trusting an
   unchecked response.
6. If the extracted `plate` doesn't match the vehicle's own (normalized),
   a warning is appended and `requires_review` is forced `true` — this
   happens regardless of what the model itself reported.
7. A `DocumentExtraction` row is saved (`COMPLETED` or `FAILED`, always),
   plus one `DocumentExtractedField` row per field (`source="ai"`).
8. `POST .../reprocess` is the same `extract` flow — it always creates a
   **new** `DocumentExtraction` row, never overwrites one, so
   `GET .../extractions` is a full audit trail of every attempt.

## Confirmación manual — nunca automática

Metadata is never written onto `Vehicle`/`VehicleDocument` until the user
explicitly calls `POST /extractions/{id}/confirm`. Two independent layers
enforce this:

- `DocumentExtraction.confirm()` only transitions `COMPLETED -> CONFIRMED`
  (anything else raises `409 extraction_not_completed`).
- Only `DocumentExtractionService.confirm` ever calls
  `gateway.apply_confirmed_fields` — `extract`/`reprocess` never do.

**What gets applied, per document type** (`drivepass/infrastructure/intelligence_gateway.py`):

- `issue_date`/`expiration_date` (any type that extracts them) → written onto
  the `VehicleDocument` via `update_dates` + `recompute_status` — this is
  what lets a confirmed CERTIFICADO_HOMOLOGACION's "VÁLIDO HASTA" date
  correctly drive whether REVISION_TECNICA/CERTIFICADO_GASES are required.
- `brand`/`model`/`year`/`color`/`vin`/`engine_number` for **PADRON and
  CERTIFICADO_HOMOLOGACION only** (both carry the vehicle's own identity) →
  written onto `Vehicle`, **guarded by a plate-match check**: if the
  extracted plate doesn't normalize to the vehicle's own, every identity
  field is skipped (`plate_mismatch: true` in the response) — confirming
  doesn't silently overwrite a vehicle's identity off the back of a
  misread plate.
- `vin` has a fallback: many Padrón documents print only "N° de Chasis"
  with no field labeled "VIN" at all. If `vin` itself comes back empty,
  `chassis_number` is used to populate `vehicle.vin` instead.
- Every other field (`insurance_company`, `policy_number`,
  `inspection_result`, `municipality`, `paid_amount`, `coverage_type`,
  `owner_name`, `owner_rut`, ...) has no destination column — it stays
  informational, visible in `extracted_data`/`DocumentExtractedField` rows,
  never applied anywhere.

### Corrección manual de un campo

The AI doesn't always get a field right — a common real case is mixing up
`vin` and `chassis_number`, or misreading a plate. `POST .../confirm`
accepts an optional body:

```json
{ "fields": { "vin": "9BWZZZ377VT004251" } }
```

Only field names that already exist in the extraction's `extracted_data`
can be overridden (an unknown key is silently ignored, never injected).
Overridden fields get `confidence: null` and `source: "manual"` — both in
the extraction's own `extracted_data` and in the corresponding
`DocumentExtractedField` row — so the audit trail shows it was corrected by
a human, not just AI-detected. The corrected value (not the AI's original)
is what gets applied to `Vehicle`/`VehicleDocument`. The frontend's
`ExtractedFieldList` renders every field as an editable input while an
extraction is `COMPLETED` (not after `CONFIRMED`/`REJECTED`), and only sends
the fields that actually changed.

## Tipos de extracción soportados

7 types, mirroring DrivePass's `VEHICLE_DOCUMENT_TYPES`
(`EXTRACTABLE_FIELD_NAMES` in `domain/value_objects/extractable_document_type.py`):

| Type | Fields |
| --- | --- |
| PADRON | plate, brand, model, year, color, vin, chassis_number, engine_number, owner_name, owner_rut |
| SOAP | plate, insurance_company, policy_number, issue_date, expiration_date |
| REVISION_TECNICA | plate, inspection_date, expiration_date, inspection_result, plant_name |
| CERTIFICADO_GASES | plate, issue_date, expiration_date, result |
| PERMISO_CIRCULACION | plate, municipality, issue_date, expiration_date, paid_amount |
| CERTIFICADO_HOMOLOGACION | plate, brand, model, year, vin, issue_date, expiration_date |
| SEGURO_PARTICULAR | plate, insurance_company, policy_number, issue_date, expiration_date, coverage_type |

`vin` and `expiration_date` were added to CERTIFICADO_HOMOLOGACION after
live testing showed real Chilean homologación certificates print both
("VIN" and "VÁLIDO HASTA"/"VIGENCIA HASTA") — without `expiration_date`,
confirming a homologación extraction could never correct the date that
`VehicleDocumentService._homologation_is_valid` depends on.

## Schema de respuesta

Strict JSON Schema, one object per field
(`{"value": string|null, "confidence": number|null}`), plus
`document_type`, `confidence_score`, `warnings: string[]`,
`requires_review: bool` at the top level — see `domain/prompts.py:build_json_schema`.
Every object sets `additionalProperties: false` and lists every key in
`required` (OpenAI's strict mode rejects schemas that don't); optional
values use a `["string", "null"]` type union rather than an absent key.

## Cost tracking

`AICostEstimator` (`application/cost_estimator.py`) has a static
model→price table (`$/1M tokens`, input and output separately). Token
counts always come from the provider's own response, never estimated. A
real gotcha found via live testing: the Responses API echoes back a
**dated snapshot** (`gpt-4o-mini-2024-07-18`) even when the request asked
for the bare alias `gpt-4o-mini` — `estimate_usd` matches the **longest
known price-table key that the returned model string starts with**, not an
exact key, or the live cost would always resolve to `null`. An unknown
model (typo, or a price-table gap) still resolves to `null` rather than a
guessed number.

## Auditoría

`AI_EXTRACTION_REQUESTED`, `AI_EXTRACTION_COMPLETED`, `AI_EXTRACTION_FAILED`,
`AI_EXTRACTION_CONFIRMED` (includes `applied_fields`/`skipped_fields`/
`plate_mismatch`/`edited_fields`), `AI_EXTRACTION_REJECTED`,
`AI_EXTRACTION_REPROCESSED` — `category="intelligence.audit"`, same
structlog pattern every other module uses.

## Endpoints

All under `/api/v1/intelligence`, all requiring an authenticated user who
owns the document's vehicle (enforced inside the gateway, not assumed):

| Method | Path | Notes |
| --- | --- | --- |
| POST | `/documents/{document_id}/extract` | 201; gated by the feature flag |
| POST | `/documents/{document_id}/reprocess` | 201; always a new extraction row; gated |
| GET | `/documents/{document_id}/extractions` | History, newest first |
| GET | `/extractions/{extraction_id}` | Detail, includes per-field rows |
| POST | `/extractions/{extraction_id}/confirm` | Optional `{"fields": {...}}` body for corrections |
| POST | `/extractions/{extraction_id}/reject` | No metadata is ever applied |

## Seguridad

- Every endpoint requires a valid access token; ownership is re-verified
  inside the gateway on every call (same vehicle/document a request
  doesn't own → `404`, never `403`, so existence is never leaked).
- `OPENAI_API_KEY` lives only in backend settings — never sent to the
  frontend, never stored in the database, never logged.
- `raw_response` stores the model's literal text output for debugging —
  document content itself is never logged, only IDs and aggregate numbers
  (token counts, confidence, timing).
- Soft delete (`deleted_at` on `document_extractions`) exists at the schema
  level for a future "delete my extraction history" feature — no endpoint
  exposes it yet.

## Frontend

`apps/web/src/intelligence/` (hooks) +
`apps/web/src/components/AIExtraction*.tsx`,
`ConfidenceBadge.tsx`, `ExtractedFieldList.tsx`, `ExtractionWarningList.tsx`,
`ConfirmExtractionButton.tsx`, `RejectExtractionButton.tsx`. Wired into
`DocumentDetailPage` behind `useFeatureFlag` — the whole "Análisis con IA"
section doesn't render when the flag is off or the document has no
uploaded version yet. `AIExtractionResultPanel` keeps local edit state per
extraction (reset via a `useEffect` keyed on `extraction.id`, e.g. after
reprocessing) and only sends the fields that actually changed as overrides.

**`LoadingModal`** (`components/LoadingModal.tsx`) covers the AI call
itself — `AIExtractionButton` shows it for the full duration of
`extract`/`reprocess`, since a real OpenAI round-trip is several seconds,
long enough that a disabled button alone isn't enough feedback.

**`useConfirmDialog`** (`components/useConfirmDialog.tsx` + `ConfirmDialog.tsx`)
is a small SweetAlert-style hook — `const { confirm, dialog } = useConfirmDialog()`,
then `if (!(await confirm({ title, message, variant }))) return;` — used
everywhere a destructive or hard-to-reverse action is one click away:
confirming/rejecting an extraction, and deleting a vehicle or a document
(replacing the native `window.confirm` those already had, for a consistent
look). `ConfirmExtractionButton`/`RejectExtractionButton` also disable
themselves immediately on `mutation.isSuccess` (not just `isPending`) —
without that, a second click after a successful confirm could fire before
the query invalidation re-render landed, hitting the server's
`409 extraction_not_completed` on an already-confirmed extraction.

## Roadmap OCR

`OCRProvider` is declared as a port with **zero implementations**. Today, a
PDF with no extractable text layer (a flat scan) is saved as `FAILED` with
`error_message` explaining why, and the AI provider is never called for it.
A future sprint can implement `OCRProvider` (e.g. Cloud Vision) and wire it
as a fallback inside `DocumentExtractionService._build_ai_input` without
changing the port contract any other code depends on.

## Fuera de alcance (explícito)

No chatbot/Copilot, no NFC, no QR, no public portal, no notifications, no
batch processing, no Pub/Sub queues (extraction is synchronous within the
request — `PROCESSING` status exists but is never observed), no Cloud
Vision/OCR yet, no automatic analysis on upload (a user must press
"Analizar con IA").
