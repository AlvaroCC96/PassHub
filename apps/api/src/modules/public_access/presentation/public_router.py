from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import Settings, get_settings
from src.core.exceptions import NotFoundError
from src.core.logging import get_logger
from src.infrastructure.database import get_db_session
from src.modules.public_access.application.ports import PublicVehicleGateway
from src.modules.public_access.application.services import (
    PublicAccessService,
    PublicSessionService,
)
from src.modules.public_access.domain.entities import PublicSession, VehiclePublicAccess
from src.modules.public_access.domain.events import (
    PUBLIC_SESSION_CREATED,
    PUBLIC_SESSION_REVOKED,
)
from src.modules.public_access.domain.value_objects import PublicAccessStatus
from src.modules.public_access.presentation.cookies import (
    clear_public_session_cookie,
    set_public_session_cookie,
)
from src.modules.public_access.presentation.dependencies import (
    get_active_public_access,
    get_authenticated_public_session,
    get_public_access_service,
    get_public_session_service,
    get_vehicle_gateway,
)
from src.modules.public_access.presentation.schemas import (
    DownloadUrlResponse,
    PublicDocumentResponse,
    VehiclePublicInfoResponse,
    VerifyPinRequest,
    VerifyPinResponse,
)

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=VehiclePublicInfoResponse)
async def get_vehicle_public_info(
    access: VehiclePublicAccess = Depends(get_active_public_access),
    gateway: PublicVehicleGateway = Depends(get_vehicle_gateway),
) -> VehiclePublicInfoResponse:
    info = await gateway.get_vehicle_info(access.vehicle_id)
    if info is None:
        raise NotFoundError("Resource not found", error_code="not_found")
    return VehiclePublicInfoResponse(
        vehicle=f"{info.brand} {info.model}",
        year=info.year,
        requires_pin=access.pin_hash is not None,
        enabled=access.enabled,
        locked=access.status == PublicAccessStatus.LOCKED,
    )


@router.post("/verify-pin", response_model=VerifyPinResponse)
async def verify_pin(
    body: VerifyPinRequest,
    response: Response,
    access: VehiclePublicAccess = Depends(get_active_public_access),
    access_service: PublicAccessService = Depends(get_public_access_service),
    session_service: PublicSessionService = Depends(get_public_session_service),
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db_session),
) -> VerifyPinResponse:
    await access_service.verify_pin(public_token=access.public_token, pin=body.pin)

    session, raw_token = await session_service.create(
        vehicle_public_access_id=access.id,
    )
    await db.commit()

    session_duration_seconds = settings.public_access.session_duration_minutes * 60
    set_public_session_cookie(
        response,
        raw_token=raw_token,
        max_age=session_duration_seconds,
        is_secure=settings.is_production,
    )
    logger.info(
        PUBLIC_SESSION_CREATED,
        category="public_access.audit",
        vehicle_public_access_id=str(access.id),
    )
    return VerifyPinResponse(
        authenticated=True,
        expires_in=session_duration_seconds,
        session_token=raw_token,
    )


@router.get("/documents", response_model=list[PublicDocumentResponse])
async def list_documents(
    access: VehiclePublicAccess = Depends(get_active_public_access),
    _session: PublicSession = Depends(get_authenticated_public_session),
    gateway: PublicVehicleGateway = Depends(get_vehicle_gateway),
) -> list[PublicDocumentResponse]:
    docs = await gateway.list_public_documents(access.vehicle_id)
    return [
        PublicDocumentResponse(id=doc.id, type=doc.document_type, status=doc.status)
        for doc in docs
    ]


@router.get("/documents/{document_id}/download-url", response_model=DownloadUrlResponse)
async def get_document_download_url(
    document_id: str,
    access: VehiclePublicAccess = Depends(get_active_public_access),
    _session: PublicSession = Depends(get_authenticated_public_session),
    gateway: PublicVehicleGateway = Depends(get_vehicle_gateway),
    settings: Settings = Depends(get_settings),
) -> DownloadUrlResponse:
    try:
        doc_uuid = UUID(document_id)
    except ValueError:
        raise NotFoundError("Document not found", error_code="not_found") from None

    signed_url_ttl = settings.public_access.signed_url_duration_minutes * 60
    url = await gateway.get_document_signed_url(
        document_id=doc_uuid,
        vehicle_id=access.vehicle_id,
        expires_in_seconds=signed_url_ttl,
    )
    if url is None:
        raise NotFoundError("Document not found", error_code="not_found")
    return DownloadUrlResponse(url=url)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    access: VehiclePublicAccess = Depends(get_active_public_access),
    session: PublicSession = Depends(get_authenticated_public_session),
    session_service: PublicSessionService = Depends(get_public_session_service),
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    await session_service.revoke(session_id=session.id)
    await db.commit()
    clear_public_session_cookie(response, is_secure=settings.is_production)
    logger.info(
        PUBLIC_SESSION_REVOKED,
        category="public_access.audit",
        vehicle_public_access_id=str(access.id),
    )
