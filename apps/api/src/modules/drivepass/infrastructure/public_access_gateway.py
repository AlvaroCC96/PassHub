from datetime import date
from uuid import UUID

from src.application.ports import StorageProvider
from src.modules.drivepass.documents.application.ports import (
    DocumentVersionRepository,
    VehicleDocumentRepository,
)
from src.modules.drivepass.documents.domain.value_objects import DocumentVisibility
from src.modules.drivepass.vehicles.application.ports import VehicleRepository
from src.modules.public_access.application.ports import (
    PublicDocumentSummary,
    VehiclePublicInfo,
)

_PUBLIC_VISIBILITY = DocumentVisibility.PUBLIC_AFTER_PIN


class DrivePassPublicAccessGateway:
    """Implements `PublicVehicleGateway` using DrivePass's existing repositories
    and `StorageProvider`.  This is the single file that imports both modules;
    everything above it in public_access (domain/application) never touches
    `src.modules.drivepass`."""

    def __init__(
        self,
        *,
        vehicle_repository: VehicleRepository,
        document_repository: VehicleDocumentRepository,
        version_repository: DocumentVersionRepository,
        storage_provider: StorageProvider,
    ) -> None:
        self._vehicles = vehicle_repository
        self._documents = document_repository
        self._versions = version_repository
        self._storage = storage_provider

    async def get_vehicle_info(self, vehicle_id: UUID) -> VehiclePublicInfo | None:
        vehicle = await self._vehicles.get_by_id(vehicle_id)
        if vehicle is None:
            return None
        return VehiclePublicInfo(
            id=vehicle.id,
            brand=vehicle.brand,
            model=vehicle.model,
            year=vehicle.year,
        )

    async def list_public_documents(self, vehicle_id: UUID) -> list[PublicDocumentSummary]:
        documents = await self._documents.list_for_vehicle(vehicle_id)
        today = date.today()
        result: list[PublicDocumentSummary] = []
        for doc in documents:
            if doc.visibility != _PUBLIC_VISIBILITY:
                continue
            if doc.current_version_id is None:
                continue
            doc.recompute_status(today=today)
            result.append(
                PublicDocumentSummary(
                    id=doc.id,
                    document_type=doc.document_type.value,
                    status=doc.status.value,
                )
            )
        return result

    async def get_document_signed_url(
        self,
        *,
        document_id: UUID,
        vehicle_id: UUID,
        expires_in_seconds: int,
    ) -> str | None:
        doc = await self._documents.get_by_id(document_id)
        if doc is None or doc.vehicle_id != vehicle_id:
            return None
        if doc.visibility != _PUBLIC_VISIBILITY:
            return None
        if doc.current_version_id is None:
            return None
        version = await self._versions.get_by_id(doc.current_version_id)
        if version is None:
            return None
        return await self._storage.get_presigned_url(
            key=version.storage_path,
            bucket=version.storage_bucket,
            expires_in_seconds=expires_in_seconds,
        )
