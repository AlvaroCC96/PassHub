from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database import get_db_session
from src.modules.identity.presentation.dependencies import CurrentUser
from src.modules.intelligence.application.services import DocumentExtractionService
from src.modules.intelligence.presentation.dependencies import (
    get_extraction_service,
    require_ai_extraction_enabled,
)
from src.modules.intelligence.presentation.schemas import (
    ConfirmExtractionRequest,
    DocumentExtractionDetailResponse,
    DocumentExtractionResponse,
)

router = APIRouter()


@router.post(
    "/documents/{document_id}/extract",
    response_model=DocumentExtractionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_ai_extraction_enabled)],
)
async def extract_document(
    document_id: UUID,
    current_user: CurrentUser,
    extraction_service: DocumentExtractionService = Depends(get_extraction_service),
    session: AsyncSession = Depends(get_db_session),
) -> DocumentExtractionResponse:
    extraction = await extraction_service.extract(user_id=current_user.id, document_id=document_id)
    await session.commit()
    return DocumentExtractionResponse.from_domain(extraction)


@router.post(
    "/documents/{document_id}/reprocess",
    response_model=DocumentExtractionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_ai_extraction_enabled)],
)
async def reprocess_document(
    document_id: UUID,
    current_user: CurrentUser,
    extraction_service: DocumentExtractionService = Depends(get_extraction_service),
    session: AsyncSession = Depends(get_db_session),
) -> DocumentExtractionResponse:
    extraction = await extraction_service.reprocess(
        user_id=current_user.id, document_id=document_id
    )
    await session.commit()
    return DocumentExtractionResponse.from_domain(extraction)


@router.get("/documents/{document_id}/extractions", response_model=list[DocumentExtractionResponse])
async def list_document_extractions(
    document_id: UUID,
    current_user: CurrentUser,
    extraction_service: DocumentExtractionService = Depends(get_extraction_service),
) -> list[DocumentExtractionResponse]:
    extractions = await extraction_service.list_for_document(
        user_id=current_user.id, document_id=document_id
    )
    return [DocumentExtractionResponse.from_domain(e) for e in extractions]


@router.get("/extractions/{extraction_id}", response_model=DocumentExtractionDetailResponse)
async def get_extraction(
    extraction_id: UUID,
    current_user: CurrentUser,
    extraction_service: DocumentExtractionService = Depends(get_extraction_service),
) -> DocumentExtractionDetailResponse:
    extraction = await extraction_service.get(user_id=current_user.id, extraction_id=extraction_id)
    fields = await extraction_service.get_fields(extraction_id)
    return DocumentExtractionDetailResponse.from_domain_with_fields(extraction, fields)


@router.post("/extractions/{extraction_id}/confirm", response_model=DocumentExtractionResponse)
async def confirm_extraction(
    extraction_id: UUID,
    current_user: CurrentUser,
    payload: ConfirmExtractionRequest | None = None,
    extraction_service: DocumentExtractionService = Depends(get_extraction_service),
    session: AsyncSession = Depends(get_db_session),
) -> DocumentExtractionResponse:
    extraction = await extraction_service.confirm(
        user_id=current_user.id,
        extraction_id=extraction_id,
        field_overrides=payload.fields if payload else None,
    )
    await session.commit()
    return DocumentExtractionResponse.from_domain(extraction)


@router.post("/extractions/{extraction_id}/reject", response_model=DocumentExtractionResponse)
async def reject_extraction(
    extraction_id: UUID,
    current_user: CurrentUser,
    extraction_service: DocumentExtractionService = Depends(get_extraction_service),
    session: AsyncSession = Depends(get_db_session),
) -> DocumentExtractionResponse:
    extraction = await extraction_service.reject(
        user_id=current_user.id, extraction_id=extraction_id
    )
    await session.commit()
    return DocumentExtractionResponse.from_domain(extraction)
