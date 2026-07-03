from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database import get_db_session
from src.modules.drivepass.documents.application.services import VehicleDocumentService
from src.modules.drivepass.documents.domain.value_objects import DocumentType, DocumentVisibility
from src.modules.drivepass.documents.presentation.dependencies import (
    get_owned_vehicle,
    get_vehicle_document_service,
)
from src.modules.drivepass.documents.presentation.schemas import (
    DocumentStatusSummaryResponse,
    DocumentVersionResponse,
    DownloadUrlResponse,
    SetVisibilityRequest,
    VehicleDocumentResponse,
)
from src.modules.drivepass.vehicles.domain.entities import Vehicle
from src.modules.identity.presentation.dependencies import CurrentUser

router = APIRouter()


@router.get("/", response_model=list[VehicleDocumentResponse])
async def list_documents(
    vehicle: Vehicle = Depends(get_owned_vehicle),
    document_service: VehicleDocumentService = Depends(get_vehicle_document_service),
    session: AsyncSession = Depends(get_db_session),
) -> list[VehicleDocumentResponse]:
    # Listing isn't read-only here: it lazily creates the MISSING checklist
    # rows and re-syncs status/is_required, so this commits too.
    documents = await document_service.list_for_vehicle(vehicle.id)
    await session.commit()
    return [VehicleDocumentResponse.from_domain(d) for d in documents]


# Declared before `/{document_id}` — otherwise FastAPI would match "status"
# as a document_id.
@router.get("/status", response_model=DocumentStatusSummaryResponse)
async def get_documents_status(
    vehicle: Vehicle = Depends(get_owned_vehicle),
    document_service: VehicleDocumentService = Depends(get_vehicle_document_service),
    session: AsyncSession = Depends(get_db_session),
) -> DocumentStatusSummaryResponse:
    summary = await document_service.get_status_summary(vehicle.id)
    await session.commit()
    return DocumentStatusSummaryResponse.from_dto(summary)


@router.post("/", response_model=VehicleDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    current_user: CurrentUser,
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    issue_date: date | None = Form(None),
    expiration_date: date | None = Form(None),
    visibility: DocumentVisibility | None = Form(None),
    vehicle: Vehicle = Depends(get_owned_vehicle),
    document_service: VehicleDocumentService = Depends(get_vehicle_document_service),
    session: AsyncSession = Depends(get_db_session),
) -> VehicleDocumentResponse:
    content = await file.read()
    document = await document_service.upload_initial(
        vehicle_id=vehicle.id,
        user_id=current_user.id,
        document_type=document_type,
        filename=file.filename or "upload",
        content_bytes=content,
        issue_date=issue_date,
        expiration_date=expiration_date,
        visibility=visibility,
    )
    await session.commit()
    return VehicleDocumentResponse.from_domain(document)


@router.get("/{document_id}", response_model=VehicleDocumentResponse)
async def get_document(
    document_id: UUID,
    vehicle: Vehicle = Depends(get_owned_vehicle),
    document_service: VehicleDocumentService = Depends(get_vehicle_document_service),
) -> VehicleDocumentResponse:
    document = await document_service.get_document(vehicle_id=vehicle.id, document_id=document_id)
    return VehicleDocumentResponse.from_domain(document)


@router.post("/{document_id}/versions", response_model=VehicleDocumentResponse)
async def upload_new_version(
    document_id: UUID,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    issue_date: date | None = Form(None),
    expiration_date: date | None = Form(None),
    visibility: DocumentVisibility | None = Form(None),
    vehicle: Vehicle = Depends(get_owned_vehicle),
    document_service: VehicleDocumentService = Depends(get_vehicle_document_service),
    session: AsyncSession = Depends(get_db_session),
) -> VehicleDocumentResponse:
    content = await file.read()
    document = await document_service.upload_new_version(
        vehicle_id=vehicle.id,
        document_id=document_id,
        user_id=current_user.id,
        filename=file.filename or "upload",
        content_bytes=content,
        issue_date=issue_date,
        expiration_date=expiration_date,
        visibility=visibility,
    )
    await session.commit()
    return VehicleDocumentResponse.from_domain(document)


@router.get("/{document_id}/versions", response_model=list[DocumentVersionResponse])
async def list_document_versions(
    document_id: UUID,
    vehicle: Vehicle = Depends(get_owned_vehicle),
    document_service: VehicleDocumentService = Depends(get_vehicle_document_service),
) -> list[DocumentVersionResponse]:
    versions = await document_service.list_versions(vehicle_id=vehicle.id, document_id=document_id)
    return [DocumentVersionResponse.from_domain(v) for v in versions]


@router.get("/{document_id}/download-url", response_model=DownloadUrlResponse)
async def get_download_url(
    document_id: UUID,
    vehicle: Vehicle = Depends(get_owned_vehicle),
    document_service: VehicleDocumentService = Depends(get_vehicle_document_service),
) -> DownloadUrlResponse:
    url, expires_in = await document_service.get_download_url(
        vehicle_id=vehicle.id, document_id=document_id
    )
    return DownloadUrlResponse(url=url, expires_in=expires_in)


@router.patch("/{document_id}/visibility", response_model=VehicleDocumentResponse)
async def set_document_visibility(
    document_id: UUID,
    body: SetVisibilityRequest,
    vehicle: Vehicle = Depends(get_owned_vehicle),
    document_service: VehicleDocumentService = Depends(get_vehicle_document_service),
    session: AsyncSession = Depends(get_db_session),
) -> VehicleDocumentResponse:
    document = await document_service.set_visibility(
        vehicle_id=vehicle.id,
        document_id=document_id,
        visibility=body.visibility,
    )
    await session.commit()
    return VehicleDocumentResponse.from_domain(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    vehicle: Vehicle = Depends(get_owned_vehicle),
    document_service: VehicleDocumentService = Depends(get_vehicle_document_service),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    await document_service.delete(vehicle_id=vehicle.id, document_id=document_id)
    await session.commit()
