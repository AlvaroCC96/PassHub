from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.intelligence.domain.entities import DocumentExtractedField, DocumentExtraction
from src.modules.intelligence.infrastructure.models import (
    DocumentExtractedFieldModel,
    DocumentExtractionModel,
)


def _extraction_to_domain(model: DocumentExtractionModel) -> DocumentExtraction:
    return DocumentExtraction(
        id=model.id,
        document_id=model.document_id,
        document_version_id=model.document_version_id,
        vehicle_id=model.vehicle_id,
        user_id=model.user_id,
        provider=model.provider,
        model=model.model,
        prompt_version=model.prompt_version,
        status=model.status,
        raw_response=model.raw_response,
        extracted_data=model.extracted_data,
        confidence_score=(
            float(model.confidence_score) if model.confidence_score is not None else None
        ),
        input_tokens=model.input_tokens,
        output_tokens=model.output_tokens,
        total_tokens=model.total_tokens,
        estimated_cost_usd=(
            float(model.estimated_cost_usd) if model.estimated_cost_usd is not None else None
        ),
        processing_time_ms=model.processing_time_ms,
        error_message=model.error_message,
        confirmed_at=model.confirmed_at,
        rejected_at=model.rejected_at,
    )


def _field_to_domain(model: DocumentExtractedFieldModel) -> DocumentExtractedField:
    return DocumentExtractedField(
        id=model.id,
        extraction_id=model.extraction_id,
        field_name=model.field_name,
        field_value=model.field_value,
        normalized_value=model.normalized_value,
        confidence_score=(
            float(model.confidence_score) if model.confidence_score is not None else None
        ),
        source=model.source,
    )


class SqlAlchemyDocumentExtractionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, extraction_id: UUID) -> DocumentExtraction | None:
        model = await self._session.get(DocumentExtractionModel, extraction_id)
        return _extraction_to_domain(model) if model and not model.is_deleted else None

    async def list_for_document(self, document_id: UUID) -> list[DocumentExtraction]:
        stmt = (
            select(DocumentExtractionModel)
            .where(
                DocumentExtractionModel.document_id == document_id,
                DocumentExtractionModel.deleted_at.is_(None),
            )
            .order_by(DocumentExtractionModel.created_at.desc())
        )
        models = (await self._session.execute(stmt)).scalars().all()
        return [_extraction_to_domain(m) for m in models]

    async def add(self, extraction: DocumentExtraction) -> None:
        self._session.add(
            DocumentExtractionModel(
                id=extraction.id,
                document_id=extraction.document_id,
                document_version_id=extraction.document_version_id,
                vehicle_id=extraction.vehicle_id,
                user_id=extraction.user_id,
                provider=extraction.provider,
                model=extraction.model,
                prompt_version=extraction.prompt_version,
                status=extraction.status,
                raw_response=extraction.raw_response,
                extracted_data=extraction.extracted_data,
                confidence_score=extraction.confidence_score,
                input_tokens=extraction.input_tokens,
                output_tokens=extraction.output_tokens,
                total_tokens=extraction.total_tokens,
                estimated_cost_usd=extraction.estimated_cost_usd,
                processing_time_ms=extraction.processing_time_ms,
                error_message=extraction.error_message,
                confirmed_at=extraction.confirmed_at,
                rejected_at=extraction.rejected_at,
            )
        )
        await self._session.flush()

    async def save(self, extraction: DocumentExtraction) -> None:
        model = await self._session.get(DocumentExtractionModel, extraction.id)
        if model is None:
            raise LookupError(f"DocumentExtraction {extraction.id} does not exist")
        model.status = extraction.status
        model.raw_response = extraction.raw_response
        model.extracted_data = extraction.extracted_data
        model.confidence_score = extraction.confidence_score
        model.input_tokens = extraction.input_tokens
        model.output_tokens = extraction.output_tokens
        model.total_tokens = extraction.total_tokens
        model.estimated_cost_usd = extraction.estimated_cost_usd
        model.processing_time_ms = extraction.processing_time_ms
        model.error_message = extraction.error_message
        model.confirmed_at = extraction.confirmed_at
        model.rejected_at = extraction.rejected_at
        await self._session.flush()


class SqlAlchemyDocumentExtractedFieldRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_extraction(self, extraction_id: UUID) -> list[DocumentExtractedField]:
        stmt = select(DocumentExtractedFieldModel).where(
            DocumentExtractedFieldModel.extraction_id == extraction_id
        )
        models = (await self._session.execute(stmt)).scalars().all()
        return [_field_to_domain(m) for m in models]

    async def add_many(self, fields: list[DocumentExtractedField]) -> None:
        for entity_field in fields:
            self._session.add(
                DocumentExtractedFieldModel(
                    id=entity_field.id,
                    extraction_id=entity_field.extraction_id,
                    field_name=entity_field.field_name,
                    field_value=entity_field.field_value,
                    normalized_value=entity_field.normalized_value,
                    confidence_score=entity_field.confidence_score,
                    source=entity_field.source,
                )
            )
        await self._session.flush()

    async def update_value(
        self, *, extraction_id: UUID, field_name: str, field_value: str | None, source: str
    ) -> None:
        stmt = select(DocumentExtractedFieldModel).where(
            DocumentExtractedFieldModel.extraction_id == extraction_id,
            DocumentExtractedFieldModel.field_name == field_name,
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        if model is None:
            return
        model.field_value = field_value
        model.normalized_value = field_value
        model.source = source
        await self._session.flush()
