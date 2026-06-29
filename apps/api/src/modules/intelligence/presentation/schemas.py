from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from src.modules.intelligence.domain.entities import DocumentExtractedField, DocumentExtraction
from src.modules.intelligence.domain.value_objects import ExtractionStatus


class ConfirmExtractionRequest(BaseModel):
    """Optional body for `POST /extractions/{id}/confirm` — lets the caller
    correct one or more field values before they're applied, e.g. when the
    AI mixed up `vin` and `chassis_number`. Omitted or `fields=None` confirms
    the AI's values unchanged."""

    fields: dict[str, str | None] | None = None


class DocumentExtractedFieldResponse(BaseModel):
    id: UUID
    field_name: str
    field_value: str | None
    normalized_value: str | None
    confidence_score: float | None
    source: str

    @classmethod
    def from_domain(cls, field: DocumentExtractedField) -> "DocumentExtractedFieldResponse":
        return cls(
            id=field.id,
            field_name=field.field_name,
            field_value=field.field_value,
            normalized_value=field.normalized_value,
            confidence_score=field.confidence_score,
            source=field.source,
        )


class DocumentExtractionResponse(BaseModel):
    id: UUID
    document_id: UUID
    document_version_id: UUID
    vehicle_id: UUID
    status: ExtractionStatus
    provider: str
    model: str
    prompt_version: str
    extracted_data: dict[str, Any] | None
    confidence_score: float | None
    warnings: list[str]
    requires_review: bool
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    estimated_cost_usd: float | None
    processing_time_ms: int | None
    error_message: str | None
    confirmed_at: datetime | None
    rejected_at: datetime | None

    @classmethod
    def from_domain(cls, extraction: DocumentExtraction) -> "DocumentExtractionResponse":
        return cls(
            id=extraction.id,
            document_id=extraction.document_id,
            document_version_id=extraction.document_version_id,
            vehicle_id=extraction.vehicle_id,
            status=extraction.status,
            provider=extraction.provider,
            model=extraction.model,
            prompt_version=extraction.prompt_version,
            extracted_data=extraction.extracted_data,
            confidence_score=extraction.confidence_score,
            warnings=extraction.warnings,
            requires_review=extraction.requires_review,
            input_tokens=extraction.input_tokens,
            output_tokens=extraction.output_tokens,
            total_tokens=extraction.total_tokens,
            estimated_cost_usd=extraction.estimated_cost_usd,
            processing_time_ms=extraction.processing_time_ms,
            error_message=extraction.error_message,
            confirmed_at=extraction.confirmed_at,
            rejected_at=extraction.rejected_at,
        )


class DocumentExtractionDetailResponse(DocumentExtractionResponse):
    fields: list[DocumentExtractedFieldResponse]

    @classmethod
    def from_domain_with_fields(
        cls, extraction: DocumentExtraction, fields: list[DocumentExtractedField]
    ) -> "DocumentExtractionDetailResponse":
        base = DocumentExtractionResponse.from_domain(extraction)
        return cls(
            **base.model_dump(),
            fields=[DocumentExtractedFieldResponse.from_domain(f) for f in fields],
        )
