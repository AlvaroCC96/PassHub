from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class VehiclePublicInfo:
    id: UUID
    brand: str
    model: str
    year: int


@dataclass(frozen=True, slots=True)
class PublicDocumentSummary:
    id: UUID
    document_type: str
    status: str


class PublicVehicleGateway(Protocol):
    """Port that public_access uses to read vehicle/document data from DrivePass.

    `DrivePassPublicAccessGateway` in `drivepass/infrastructure/` is the only
    implementation — the same cross-module port pattern used by Intelligence's
    `VehicleDocumentGateway`."""

    async def get_vehicle_info(self, vehicle_id: UUID) -> VehiclePublicInfo | None:
        """Returns basic vehicle info. Returns None if vehicle not found."""
        ...

    async def list_public_documents(self, vehicle_id: UUID) -> list[PublicDocumentSummary]:
        """Returns documents with `PUBLIC_AFTER_PIN` visibility that have been
        uploaded (i.e. have a current version).  Status is recomputed from today's
        date before returning so `EXPIRING_SOON`/`EXPIRED` are always current."""
        ...

    async def get_document_signed_url(
        self,
        *,
        document_id: UUID,
        vehicle_id: UUID,
        expires_in_seconds: int,
    ) -> str | None:
        """Generates a presigned download URL for the current version of a
        `PUBLIC_AFTER_PIN` document.  Returns None if the document doesn't
        exist, doesn't belong to the vehicle, isn't PUBLIC_AFTER_PIN, or
        has no uploaded version."""
        ...
