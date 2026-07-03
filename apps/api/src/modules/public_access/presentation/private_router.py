from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import Settings, get_settings
from src.core.exceptions import NotFoundError
from src.core.logging import get_logger
from src.infrastructure.database import get_db_session
from src.modules.drivepass.vehicles.domain.entities import Vehicle
from src.modules.public_access.application.services import (
    PublicAccessService,
    PublicSessionService,
)
from src.modules.public_access.domain.entities import VehiclePublicAccess
from src.modules.public_access.domain.events import (
    PUBLIC_ACCESS_CREATED,
    PUBLIC_ACCESS_DISABLED,
    PUBLIC_ACCESS_ENABLED,
    PUBLIC_PIN_CHANGED,
    PUBLIC_TOKEN_REGENERATED,
)
from src.modules.public_access.domain.value_objects import PublicAccessStatus
from src.modules.public_access.presentation.dependencies import (
    get_owned_vehicle_for_public_access,
    get_public_access_service,
    get_public_session_service,
)
from src.modules.public_access.presentation.schemas import (
    ChangePinRequest,
    PublicAccessResponse,
    PublicLinkResponse,
    SetEnabledRequest,
    SetupPublicAccessRequest,
)

logger = get_logger(__name__)

router = APIRouter()


def _to_response(access: VehiclePublicAccess, *, public_url: str) -> PublicAccessResponse:
    return PublicAccessResponse(
        enabled=access.enabled,
        public_token=access.public_token,
        public_url=public_url,
        failed_attempts=access.failed_attempts,
        locked=access.status == PublicAccessStatus.LOCKED,
        status=access.status.value,
    )


def _build_public_url(settings: Settings, token: str) -> str:
    return f"{settings.public_access.portal_base_url}/p/{token}"


@router.get("/", response_model=PublicAccessResponse)
async def get_public_access(
    vehicle: Vehicle = Depends(get_owned_vehicle_for_public_access),
    access_service: PublicAccessService = Depends(get_public_access_service),
    settings: Settings = Depends(get_settings),
) -> PublicAccessResponse:
    access = await access_service.get_access_for_vehicle(vehicle.id)
    if access is None or access.deleted_at is not None:
        raise NotFoundError(
            "No public access configured for this vehicle",
            error_code="public_access_not_found",
        )
    return _to_response(access, public_url=_build_public_url(settings, access.public_token))


@router.post("/setup", response_model=PublicAccessResponse, status_code=status.HTTP_201_CREATED)
async def setup_public_access(
    body: SetupPublicAccessRequest,
    vehicle: Vehicle = Depends(get_owned_vehicle_for_public_access),
    access_service: PublicAccessService = Depends(get_public_access_service),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_db_session),
) -> PublicAccessResponse:
    access, created = await access_service.setup(vehicle_id=vehicle.id, pin=body.pin)
    await session.commit()
    logger.info(
        PUBLIC_ACCESS_CREATED if created else "PUBLIC_PIN_UPDATED",
        category="public_access.audit",
        vehicle_id=str(vehicle.id),
    )
    return _to_response(access, public_url=_build_public_url(settings, access.public_token))


@router.patch("/enabled", response_model=PublicAccessResponse)
async def set_enabled(
    body: SetEnabledRequest,
    vehicle: Vehicle = Depends(get_owned_vehicle_for_public_access),
    access_service: PublicAccessService = Depends(get_public_access_service),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_db_session),
) -> PublicAccessResponse:
    if body.enabled:
        await access_service.enable(vehicle_id=vehicle.id)
    else:
        await access_service.disable(vehicle_id=vehicle.id)
    await session.commit()
    logger.info(
        PUBLIC_ACCESS_ENABLED if body.enabled else PUBLIC_ACCESS_DISABLED,
        category="public_access.audit",
        vehicle_id=str(vehicle.id),
    )
    access = await access_service.get_access_for_vehicle(vehicle.id)
    assert access is not None
    return _to_response(access, public_url=_build_public_url(settings, access.public_token))


@router.post("/pin", status_code=status.HTTP_204_NO_CONTENT)
async def change_pin(
    body: ChangePinRequest,
    vehicle: Vehicle = Depends(get_owned_vehicle_for_public_access),
    access_service: PublicAccessService = Depends(get_public_access_service),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    await access_service.change_pin(
        vehicle_id=vehicle.id, old_pin=body.old_pin, new_pin=body.new_pin
    )
    await session.commit()
    logger.info(
        PUBLIC_PIN_CHANGED,
        category="public_access.audit",
        vehicle_id=str(vehicle.id),
    )


@router.post("/regenerate", response_model=PublicAccessResponse)
async def regenerate_token(
    vehicle: Vehicle = Depends(get_owned_vehicle_for_public_access),
    access_service: PublicAccessService = Depends(get_public_access_service),
    session_service: PublicSessionService = Depends(get_public_session_service),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_db_session),
) -> PublicAccessResponse:
    access = await access_service.regenerate_token(vehicle_id=vehicle.id)
    # Revoke all sessions that used the previous token.
    await session_service.revoke_all_for_access(
        vehicle_public_access_id=access.id
    )
    await session.commit()
    logger.info(
        PUBLIC_TOKEN_REGENERATED,
        category="public_access.audit",
        vehicle_id=str(vehicle.id),
    )
    return _to_response(access, public_url=_build_public_url(settings, access.public_token))


@router.get("/link", response_model=PublicLinkResponse)
async def get_link(
    vehicle: Vehicle = Depends(get_owned_vehicle_for_public_access),
    access_service: PublicAccessService = Depends(get_public_access_service),
    settings: Settings = Depends(get_settings),
) -> PublicLinkResponse:
    access = await access_service.get_access_for_vehicle(vehicle.id)
    if access is None or access.deleted_at is not None:
        raise NotFoundError(
            "No public access configured for this vehicle",
            error_code="public_access_not_found",
        )
    return PublicLinkResponse(url=_build_public_url(settings, access.public_token))
