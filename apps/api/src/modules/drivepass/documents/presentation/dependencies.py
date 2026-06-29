from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ports import StorageProvider
from src.core.config import Settings, get_settings
from src.core.di import get_container
from src.infrastructure.database import get_db_session
from src.modules.drivepass.documents.application.ports import (
    DocumentVersionRepository,
    VehicleDocumentRepository,
)
from src.modules.drivepass.documents.application.services import VehicleDocumentService
from src.modules.drivepass.documents.infrastructure.repositories import (
    SqlAlchemyDocumentVersionRepository,
    SqlAlchemyVehicleDocumentRepository,
)
from src.modules.drivepass.vehicles.application.services import VehicleService
from src.modules.drivepass.vehicles.domain.entities import Vehicle
from src.modules.drivepass.vehicles.presentation.dependencies import get_vehicle_service
from src.modules.identity.presentation.dependencies import CurrentUser


def get_storage_provider() -> StorageProvider:
    return get_container().resolve(StorageProvider)  # type: ignore[type-abstract]


def get_vehicle_document_repository(
    session: AsyncSession = Depends(get_db_session),
) -> VehicleDocumentRepository:
    return SqlAlchemyVehicleDocumentRepository(session)


def get_document_version_repository(
    session: AsyncSession = Depends(get_db_session),
) -> DocumentVersionRepository:
    return SqlAlchemyDocumentVersionRepository(session)


def get_vehicle_document_service(
    document_repository: VehicleDocumentRepository = Depends(get_vehicle_document_repository),
    version_repository: DocumentVersionRepository = Depends(get_document_version_repository),
    storage_provider: StorageProvider = Depends(get_storage_provider),
    settings: Settings = Depends(get_settings),
) -> VehicleDocumentService:
    return VehicleDocumentService(
        document_repository=document_repository,
        version_repository=version_repository,
        storage_provider=storage_provider,
        settings=settings,
    )


async def get_owned_vehicle(
    vehicle_id: UUID,
    current_user: CurrentUser,
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> Vehicle:
    """Every document endpoint depends on this — `VehicleService.get_for_user`
    already raises 404 for a vehicle that doesn't exist or isn't the
    caller's, so document endpoints get ownership enforcement for free
    instead of re-implementing it against `vehicle_documents` directly."""
    return await vehicle_service.get_for_user(user_id=current_user.id, vehicle_id=vehicle_id)
