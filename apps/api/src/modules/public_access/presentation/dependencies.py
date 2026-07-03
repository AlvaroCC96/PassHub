from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ports import StorageProvider
from src.core.config import Settings, get_settings
from src.core.di import get_container
from src.core.exceptions import NotFoundError, UnauthorizedError
from src.infrastructure.database import get_db_session
from src.modules.drivepass.documents.application.ports import (
    DocumentVersionRepository,
    VehicleDocumentRepository,
)
from src.modules.drivepass.documents.infrastructure.repositories import (
    SqlAlchemyDocumentVersionRepository,
    SqlAlchemyVehicleDocumentRepository,
)
from src.modules.drivepass.infrastructure.public_access_gateway import (
    DrivePassPublicAccessGateway,
)
from src.modules.drivepass.vehicles.application.ports import VehicleRepository
from src.modules.drivepass.vehicles.domain.entities import Vehicle
from src.modules.drivepass.vehicles.infrastructure.repositories import (
    SqlAlchemyVehicleRepository,
)
from src.modules.identity.presentation.dependencies import CurrentUser
from src.modules.public_access.application.ports import PublicVehicleGateway
from src.modules.public_access.application.ports.public_access_repository import (
    PublicAccessRepository,
)
from src.modules.public_access.application.ports.public_session_repository import (
    PublicSessionRepository,
)
from src.modules.public_access.application.services import (
    PublicAccessService,
    PublicSessionService,
)
from src.modules.public_access.domain.entities import PublicSession, VehiclePublicAccess
from src.modules.public_access.infrastructure.pin_hasher import PinHasher
from src.modules.public_access.infrastructure.repositories import (
    SqlAlchemyPublicAccessRepository,
    SqlAlchemyPublicSessionRepository,
)
from src.modules.public_access.infrastructure.token_generator import PublicTokenGenerator
from src.modules.public_access.presentation.cookies import get_raw_session_token

_pin_hasher = PinHasher()
_token_generator = PublicTokenGenerator()


def get_storage_provider() -> StorageProvider:
    return get_container().resolve(StorageProvider)  # type: ignore[type-abstract]


def get_vehicle_repository(
    session: AsyncSession = Depends(get_db_session),
) -> VehicleRepository:
    return SqlAlchemyVehicleRepository(session)


def get_document_repository(
    session: AsyncSession = Depends(get_db_session),
) -> VehicleDocumentRepository:
    return SqlAlchemyVehicleDocumentRepository(session)


def get_version_repository(
    session: AsyncSession = Depends(get_db_session),
) -> DocumentVersionRepository:
    return SqlAlchemyDocumentVersionRepository(session)


def get_public_access_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PublicAccessRepository:
    return SqlAlchemyPublicAccessRepository(session)


def get_public_session_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PublicSessionRepository:
    return SqlAlchemyPublicSessionRepository(session)


def get_vehicle_gateway(
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repository),
    document_repo: VehicleDocumentRepository = Depends(get_document_repository),
    version_repo: DocumentVersionRepository = Depends(get_version_repository),
    storage: StorageProvider = Depends(get_storage_provider),
) -> PublicVehicleGateway:
    return DrivePassPublicAccessGateway(
        vehicle_repository=vehicle_repo,
        document_repository=document_repo,
        version_repository=version_repo,
        storage_provider=storage,
    )


def get_public_access_service(
    repo: PublicAccessRepository = Depends(get_public_access_repository),
    settings: Settings = Depends(get_settings),
) -> PublicAccessService:
    return PublicAccessService(
        access_repository=repo,
        token_generator=_token_generator,
        pin_hasher=_pin_hasher,
        max_failed_attempts=settings.public_access.max_failed_attempts,
        lockout_minutes=settings.public_access.lockout_minutes,
    )


def get_public_session_service(
    repo: PublicSessionRepository = Depends(get_public_session_repository),
    settings: Settings = Depends(get_settings),
) -> PublicSessionService:
    return PublicSessionService(
        session_repository=repo,
        session_duration_minutes=settings.public_access.session_duration_minutes,
    )


async def get_owned_vehicle_for_public_access(
    vehicle_id: UUID,
    current_user: CurrentUser,
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repository),
) -> Vehicle:
    """Rejects with 404 if the vehicle doesn't exist or doesn't belong to the
    calling user — same ownership enforcement pattern as drivepass documents."""
    vehicle = await vehicle_repo.get_by_id(vehicle_id)
    if vehicle is None or vehicle.user_id != current_user.id:
        raise NotFoundError("Vehicle not found", error_code="not_found")
    return vehicle


async def get_active_public_access(
    public_token: str,
    access_service: PublicAccessService = Depends(get_public_access_service),
) -> VehiclePublicAccess:
    """Resolves a public_token to its `VehiclePublicAccess`.  Returns 404 for
    unknown tokens AND for tokens whose access is disabled — callers never
    learn whether the token ever existed."""
    access = await access_service.get_by_public_token(public_token)
    if access is None or access.deleted_at is not None or not access.enabled:
        raise NotFoundError("Resource not found", error_code="not_found")
    return access


async def get_authenticated_public_session(
    request: Request,
    access: VehiclePublicAccess = Depends(get_active_public_access),
    session_service: PublicSessionService = Depends(get_public_session_service),
) -> PublicSession:
    """Validates the public session cookie for endpoints that require a PIN
    to have been verified first.  Returns 401 if missing/expired/revoked."""
    raw_token = get_raw_session_token(request)
    if raw_token is None:
        raise UnauthorizedError("Session required", error_code="session_required")
    session = await session_service.validate(raw_token=raw_token)
    if session is None or session.vehicle_public_access_id != access.id:
        raise UnauthorizedError("Session expired or invalid", error_code="session_expired")
    return session
