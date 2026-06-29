import base64
from typing import Any
from uuid import UUID

from src.application.ports import AIExtractionRequest, AIProvider
from src.core.exceptions import NotFoundError, ValidationError
from src.core.logging import get_logger
from src.modules.intelligence.application.cost_estimator import AICostEstimator
from src.modules.intelligence.application.ports import (
    DocumentExtractedFieldRepository,
    DocumentExtractionRepository,
    ExtractionSourceDocument,
    VehicleDocumentGateway,
)
from src.modules.intelligence.domain.entities import DocumentExtractedField, DocumentExtraction
from src.modules.intelligence.domain.prompts import build_json_schema, build_prompt
from src.modules.intelligence.domain.rules import plate_matches
from src.modules.intelligence.domain.value_objects import (
    EXTRACTABLE_FIELD_NAMES,
    ExtractableDocumentType,
)
from src.modules.intelligence.infrastructure.parsers.pdf_text_extractor import extract_pdf_text

logger = get_logger(__name__)

_PDF_CONTENT_TYPE = "application/pdf"


class DocumentExtractionService:
    """Orchestrates one extraction end to end: fetch the file via the
    `VehicleDocumentGateway` port, build a provider-agnostic request, call
    `AIProvider`, validate the shape of what comes back, and persist the
    result — completed or failed, an extraction row is always written so
    nothing about a request silently disappears. Never touches DrivePass or
    OpenAI directly; both are ports."""

    def __init__(
        self,
        *,
        extraction_repository: DocumentExtractionRepository,
        field_repository: DocumentExtractedFieldRepository,
        gateway: VehicleDocumentGateway,
        ai_provider: AIProvider,
        cost_estimator: AICostEstimator,
        provider_name: str,
        model: str,
    ) -> None:
        self._extractions = extraction_repository
        self._fields = field_repository
        self._gateway = gateway
        self._ai_provider = ai_provider
        self._cost_estimator = cost_estimator
        self._provider_name = provider_name
        self._model = model

    async def extract(self, *, user_id: UUID, document_id: UUID) -> DocumentExtraction:
        source = await self._gateway.get_source_document(user_id=user_id, document_id=document_id)
        try:
            document_type = ExtractableDocumentType(source.document_type)
        except ValueError as exc:
            raise ValidationError(
                f"'{source.document_type}' does not support AI extraction",
                error_code="unsupported_document_type",
            ) from exc

        extraction = DocumentExtraction.request(
            document_id=source.document_id,
            document_version_id=source.document_version_id,
            vehicle_id=source.vehicle_id,
            user_id=user_id,
            provider=self._provider_name,
            model=self._model,
        )
        await self._extractions.add(extraction)
        logger.info(
            "AI_EXTRACTION_REQUESTED",
            category="intelligence.audit",
            extraction_id=str(extraction.id),
            document_id=str(document_id),
            vehicle_id=str(source.vehicle_id),
            user_id=str(user_id),
        )

        image_base64, text = self._build_ai_input(source)
        if image_base64 is None and text is None:
            extraction.mark_failed(
                error_message="PDF has no extractable text layer; OCR is not implemented yet."
            )
            await self._extractions.save(extraction)
            logger.info(
                "AI_EXTRACTION_FAILED",
                category="intelligence.audit",
                extraction_id=str(extraction.id),
                document_id=str(document_id),
                reason="no_extractable_text",
            )
            return extraction

        request = AIExtractionRequest(
            prompt=build_prompt(document_type),
            json_schema=build_json_schema(document_type),
            schema_name="drivepass_document_extraction",
            content_type=source.content_type,
            image_base64=image_base64,
            text=text,
        )

        try:
            result = await self._ai_provider.extract(request)
        except Exception as exc:
            extraction.mark_failed(error_message=str(exc)[:500])
            await self._extractions.save(extraction)
            logger.info(
                "AI_EXTRACTION_FAILED",
                category="intelligence.audit",
                extraction_id=str(extraction.id),
                document_id=str(document_id),
                reason="provider_error",
            )
            return extraction

        if not self._is_well_formed(result.parsed, document_type):
            extraction.mark_failed(
                error_message="AI response did not match the expected schema",
                raw_response={"raw_text": result.raw_text},
                processing_time_ms=result.processing_time_ms,
            )
            await self._extractions.save(extraction)
            logger.info(
                "AI_EXTRACTION_FAILED",
                category="intelligence.audit",
                extraction_id=str(extraction.id),
                document_id=str(document_id),
                reason="invalid_schema",
            )
            return extraction

        extracted_data = dict(result.parsed)  # type: ignore[arg-type]
        self._cross_check_plate(extracted_data, source.vehicle_plate)

        cost = self._cost_estimator.estimate_usd(
            model=result.model, input_tokens=result.input_tokens, output_tokens=result.output_tokens
        )
        extraction.mark_completed(
            extracted_data=extracted_data,
            raw_response={"raw_text": result.raw_text},
            confidence_score=extracted_data.get("confidence_score"),
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            total_tokens=result.total_tokens,
            estimated_cost_usd=cost,
            processing_time_ms=result.processing_time_ms,
        )
        await self._extractions.save(extraction)

        fields = [
            DocumentExtractedField.create(
                extraction_id=extraction.id,
                field_name=name,
                field_value=payload.get("value"),
                normalized_value=payload.get("value"),
                confidence_score=payload.get("confidence"),
            )
            for name, payload in extracted_data.get("fields", {}).items()
        ]
        await self._fields.add_many(fields)

        logger.info(
            "AI_EXTRACTION_COMPLETED",
            category="intelligence.audit",
            extraction_id=str(extraction.id),
            document_id=str(document_id),
            confidence_score=extraction.confidence_score,
            total_tokens=extraction.total_tokens,
            estimated_cost_usd=extraction.estimated_cost_usd,
        )
        return extraction

    async def reprocess(self, *, user_id: UUID, document_id: UUID) -> DocumentExtraction:
        extraction = await self.extract(user_id=user_id, document_id=document_id)
        logger.info(
            "AI_EXTRACTION_REPROCESSED",
            category="intelligence.audit",
            extraction_id=str(extraction.id),
            document_id=str(document_id),
        )
        return extraction

    async def list_for_document(
        self, *, user_id: UUID, document_id: UUID
    ) -> list[DocumentExtraction]:
        await self._gateway.get_source_document(user_id=user_id, document_id=document_id)
        return await self._extractions.list_for_document(document_id)

    async def get(self, *, user_id: UUID, extraction_id: UUID) -> DocumentExtraction:
        extraction = await self._extractions.get_by_id(extraction_id)
        if extraction is None or extraction.user_id != user_id:
            raise NotFoundError("Extraction not found", error_code="extraction_not_found")
        return extraction

    async def get_fields(self, extraction_id: UUID) -> list[DocumentExtractedField]:
        return await self._fields.list_for_extraction(extraction_id)

    async def confirm(
        self,
        *,
        user_id: UUID,
        extraction_id: UUID,
        field_overrides: dict[str, str | None] | None = None,
    ) -> DocumentExtraction:
        """`field_overrides` lets the user correct a value they don't trust
        before it's applied — e.g. the AI read a chassis number into `vin`.
        Only field names that already exist in `extracted_data` can be
        overridden; anything else is silently ignored rather than injecting
        an unknown key. Overridden fields are persisted back onto both the
        extraction's `extracted_data` and their `DocumentExtractedField` row
        with `source="manual"`, so the audit trail shows they were
        corrected, not AI-detected as-is."""
        extraction = await self.get(user_id=user_id, extraction_id=extraction_id)
        extraction.confirm()

        extracted_data = extraction.extracted_data or {}
        fields_payload = extracted_data.get("fields", {})
        field_values: dict[str, str | None] = {
            name: payload.get("value") for name, payload in fields_payload.items()
        }

        edited_fields: list[str] = []
        for name, value in (field_overrides or {}).items():
            if name not in field_values:
                continue
            field_values[name] = value
            fields_payload[name] = {"value": value, "confidence": None, "source": "manual"}
            await self._fields.update_value(
                extraction_id=extraction.id, field_name=name, field_value=value, source="manual"
            )
            edited_fields.append(name)
        extraction.extracted_data = extracted_data

        await self._extractions.save(extraction)

        outcome = await self._gateway.apply_confirmed_fields(
            user_id=user_id,
            document_id=extraction.document_id,
            document_type=extracted_data.get("document_type", ""),
            fields=field_values,
        )
        logger.info(
            "AI_EXTRACTION_CONFIRMED",
            category="intelligence.audit",
            extraction_id=str(extraction_id),
            document_id=str(extraction.document_id),
            applied_fields=outcome.applied_fields,
            skipped_fields=outcome.skipped_fields,
            plate_mismatch=outcome.plate_mismatch,
            edited_fields=edited_fields,
        )
        return extraction

    async def reject(self, *, user_id: UUID, extraction_id: UUID) -> DocumentExtraction:
        extraction = await self.get(user_id=user_id, extraction_id=extraction_id)
        extraction.reject()
        await self._extractions.save(extraction)
        logger.info(
            "AI_EXTRACTION_REJECTED",
            category="intelligence.audit",
            extraction_id=str(extraction_id),
            document_id=str(extraction.document_id),
        )
        return extraction

    @staticmethod
    def _build_ai_input(source: ExtractionSourceDocument) -> tuple[str | None, str | None]:
        if source.content_type == _PDF_CONTENT_TYPE:
            text = extract_pdf_text(source.content_bytes)
            return None, text
        return base64.b64encode(source.content_bytes).decode("ascii"), None

    @staticmethod
    def _cross_check_plate(extracted_data: dict[str, Any], vehicle_plate: str) -> None:
        plate_payload = extracted_data.get("fields", {}).get("plate")
        extracted_plate = plate_payload.get("value") if plate_payload else None
        if extracted_plate and not plate_matches(extracted_plate, vehicle_plate):
            warnings = list(extracted_data.get("warnings", []))
            warnings.append(
                f"Extracted plate '{extracted_plate}' does not match this vehicle's "
                f"plate '{vehicle_plate}'."
            )
            extracted_data["warnings"] = warnings
            extracted_data["requires_review"] = True

    @staticmethod
    def _is_well_formed(
        parsed: dict[str, Any] | None, document_type: ExtractableDocumentType
    ) -> bool:
        if parsed is None:
            return False
        if parsed.get("document_type") != document_type.value:
            return False
        fields = parsed.get("fields")
        if not isinstance(fields, dict):
            return False
        return set(fields.keys()) == set(EXTRACTABLE_FIELD_NAMES[document_type])
