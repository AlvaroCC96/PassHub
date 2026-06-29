from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from src.core.exceptions import ConflictError
from src.domain.base import Entity
from src.modules.intelligence.domain.prompts import PROMPT_VERSION
from src.modules.intelligence.domain.value_objects import ExtractionStatus


class DocumentExtraction(Entity):
    """One AI extraction attempt against one `DocumentVersion`. `extracted_data`
    is the AI's full parsed response (`{document_type, confidence_score,
    fields, warnings, requires_review}`) — `confidence_score` is also kept as
    its own column so extractions can be sorted/filtered without unpacking
    JSON. Reprocessing a document never mutates a row in place: it creates a
    brand-new `DocumentExtraction`, so `list_for_document` is a full audit
    trail of every attempt, confirmed or not."""

    def __init__(
        self,
        *,
        id: UUID,
        document_id: UUID,
        document_version_id: UUID,
        vehicle_id: UUID,
        user_id: UUID,
        provider: str,
        model: str,
        prompt_version: str,
        status: ExtractionStatus,
        raw_response: dict[str, Any] | None = None,
        extracted_data: dict[str, Any] | None = None,
        confidence_score: float | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        total_tokens: int | None = None,
        estimated_cost_usd: float | None = None,
        processing_time_ms: int | None = None,
        error_message: str | None = None,
        confirmed_at: datetime | None = None,
        rejected_at: datetime | None = None,
    ) -> None:
        super().__init__(id)
        self.document_id = document_id
        self.document_version_id = document_version_id
        self.vehicle_id = vehicle_id
        self.user_id = user_id
        self.provider = provider
        self.model = model
        self.prompt_version = prompt_version
        self.status = status
        self.raw_response = raw_response
        self.extracted_data = extracted_data
        self.confidence_score = confidence_score
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = total_tokens
        self.estimated_cost_usd = estimated_cost_usd
        self.processing_time_ms = processing_time_ms
        self.error_message = error_message
        self.confirmed_at = confirmed_at
        self.rejected_at = rejected_at

    @classmethod
    def request(
        cls,
        *,
        document_id: UUID,
        document_version_id: UUID,
        vehicle_id: UUID,
        user_id: UUID,
        provider: str,
        model: str,
    ) -> "DocumentExtraction":
        return cls(
            id=uuid4(),
            document_id=document_id,
            document_version_id=document_version_id,
            vehicle_id=vehicle_id,
            user_id=user_id,
            provider=provider,
            model=model,
            prompt_version=PROMPT_VERSION,
            status=ExtractionStatus.PENDING,
        )

    @property
    def warnings(self) -> list[str]:
        if self.extracted_data is None:
            return []
        return list(self.extracted_data.get("warnings", []))

    @property
    def requires_review(self) -> bool:
        if self.extracted_data is None:
            return False
        return bool(self.extracted_data.get("requires_review", False))

    def mark_completed(
        self,
        *,
        extracted_data: dict[str, Any],
        raw_response: dict[str, Any],
        confidence_score: float | None,
        input_tokens: int | None,
        output_tokens: int | None,
        total_tokens: int | None,
        estimated_cost_usd: float | None,
        processing_time_ms: int,
    ) -> None:
        self.status = ExtractionStatus.COMPLETED
        self.extracted_data = extracted_data
        self.raw_response = raw_response
        self.confidence_score = confidence_score
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = total_tokens
        self.estimated_cost_usd = estimated_cost_usd
        self.processing_time_ms = processing_time_ms

    def mark_failed(
        self,
        *,
        error_message: str,
        raw_response: dict[str, Any] | None = None,
        processing_time_ms: int | None = None,
    ) -> None:
        self.status = ExtractionStatus.FAILED
        self.error_message = error_message
        self.raw_response = raw_response
        self.processing_time_ms = processing_time_ms

    def confirm(self) -> None:
        if self.status != ExtractionStatus.COMPLETED:
            raise ConflictError(
                "Only a completed extraction can be confirmed",
                error_code="extraction_not_completed",
            )
        self.status = ExtractionStatus.CONFIRMED
        self.confirmed_at = datetime.now(UTC)

    def reject(self) -> None:
        if self.status != ExtractionStatus.COMPLETED:
            raise ConflictError(
                "Only a completed extraction can be rejected",
                error_code="extraction_not_completed",
            )
        self.status = ExtractionStatus.REJECTED
        self.rejected_at = datetime.now(UTC)
