from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ExtractionSourceDocument:
    """Everything `DocumentExtractionService` needs from a DrivePass document
    without importing DrivePass. `document_type` is DrivePass's raw enum
    value (e.g. `"PADRON"`) — Intelligence parses it into its own
    `ExtractableDocumentType` and treats anything that doesn't parse as
    unsupported, rather than the gateway deciding what's extractable."""

    document_id: UUID
    document_version_id: UUID
    vehicle_id: UUID
    document_type: str
    vehicle_plate: str
    content_bytes: bytes
    content_type: str
    original_filename: str


@dataclass(frozen=True, slots=True)
class FieldApplicationOutcome:
    applied_fields: list[str] = field(default_factory=list)
    skipped_fields: list[str] = field(default_factory=list)
    plate_mismatch: bool = False


class VehicleDocumentGateway(Protocol):
    """Port Intelligence defines for the one thing it needs from DrivePass:
    read a document's current file for extraction, and write back fields
    the user has confirmed. DrivePass supplies the adapter
    (`DrivePassDocumentGateway`) — Intelligence's domain and application
    layers never import anything from `src.modules.drivepass`."""

    async def get_source_document(
        self, *, user_id: UUID, document_id: UUID
    ) -> ExtractionSourceDocument: ...

    async def apply_confirmed_fields(
        self,
        *,
        user_id: UUID,
        document_id: UUID,
        document_type: str,
        fields: dict[str, str | None],
    ) -> FieldApplicationOutcome: ...
