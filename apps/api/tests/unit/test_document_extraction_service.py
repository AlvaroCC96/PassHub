from uuid import UUID, uuid4

import pytest
from src.application.ports import AIExtractionRequest, AIExtractionResult
from src.core.exceptions import ConflictError, NotFoundError
from src.modules.intelligence.application.cost_estimator import AICostEstimator
from src.modules.intelligence.application.ports import (
    ExtractionSourceDocument,
    FieldApplicationOutcome,
)
from src.modules.intelligence.application.services import DocumentExtractionService
from src.modules.intelligence.domain.entities import DocumentExtractedField, DocumentExtraction
from src.modules.intelligence.domain.value_objects import ExtractionStatus

PADRON_FIELDS = (
    "plate",
    "brand",
    "model",
    "year",
    "color",
    "vin",
    "chassis_number",
    "engine_number",
    "owner_name",
    "owner_rut",
)


def _empty_padron_fields() -> dict:
    return {name: {"value": None, "confidence": None} for name in PADRON_FIELDS}


class FakeAIProvider:
    def __init__(self, *, result: AIExtractionResult | None = None, exc: Exception | None = None):
        self.result = result
        self.exc = exc
        self.calls: list[AIExtractionRequest] = []

    async def extract(self, request: AIExtractionRequest) -> AIExtractionResult:
        self.calls.append(request)
        if self.exc is not None:
            raise self.exc
        assert self.result is not None
        return self.result


class FakeVehicleDocumentGateway:
    def __init__(self, *, source: ExtractionSourceDocument, owner_user_id: UUID) -> None:
        self._source = source
        self._owner_user_id = owner_user_id
        self.applied_calls: list[tuple] = []

    async def get_source_document(
        self, *, user_id: UUID, document_id: UUID
    ) -> ExtractionSourceDocument:
        if user_id != self._owner_user_id or document_id != self._source.document_id:
            raise NotFoundError("Document not found", error_code="document_not_found")
        return self._source

    async def apply_confirmed_fields(
        self, *, user_id: UUID, document_id: UUID, document_type: str, fields: dict
    ) -> FieldApplicationOutcome:
        self.applied_calls.append((user_id, document_id, document_type, fields))
        return FieldApplicationOutcome(
            applied_fields=[k for k, v in fields.items() if v is not None],
            skipped_fields=[],
            plate_mismatch=False,
        )


class FakeExtractionRepository:
    def __init__(self) -> None:
        self.by_id: dict[UUID, DocumentExtraction] = {}

    async def get_by_id(self, extraction_id: UUID) -> DocumentExtraction | None:
        return self.by_id.get(extraction_id)

    async def list_for_document(self, document_id: UUID) -> list[DocumentExtraction]:
        return [e for e in self.by_id.values() if e.document_id == document_id]

    async def add(self, extraction: DocumentExtraction) -> None:
        self.by_id[extraction.id] = extraction

    async def save(self, extraction: DocumentExtraction) -> None:
        self.by_id[extraction.id] = extraction


class FakeFieldRepository:
    def __init__(self) -> None:
        self.fields: list[DocumentExtractedField] = []

    async def list_for_extraction(self, extraction_id: UUID) -> list[DocumentExtractedField]:
        return [f for f in self.fields if f.extraction_id == extraction_id]

    async def add_many(self, fields: list[DocumentExtractedField]) -> None:
        self.fields.extend(fields)

    async def update_value(
        self, *, extraction_id: UUID, field_name: str, field_value: str | None, source: str
    ) -> None:
        for field in self.fields:
            if field.extraction_id == extraction_id and field.field_name == field_name:
                field.field_value = field_value
                field.normalized_value = field_value
                field.source = source


def _source(
    *, document_type: str = "PADRON", content_type: str = "image/png", vehicle_plate: str = "ABCD12"
) -> ExtractionSourceDocument:
    return ExtractionSourceDocument(
        document_id=uuid4(),
        document_version_id=uuid4(),
        vehicle_id=uuid4(),
        document_type=document_type,
        vehicle_plate=vehicle_plate,
        content_bytes=b"\x89PNG\r\n\x1a\n" + b"\x00" * 16,
        content_type=content_type,
        original_filename="padron.png",
    )


def _service(
    *, source: ExtractionSourceDocument, user_id: UUID, ai_provider: FakeAIProvider
) -> tuple[DocumentExtractionService, FakeVehicleDocumentGateway, FakeExtractionRepository]:
    gateway = FakeVehicleDocumentGateway(source=source, owner_user_id=user_id)
    extractions = FakeExtractionRepository()
    service = DocumentExtractionService(
        extraction_repository=extractions,
        field_repository=FakeFieldRepository(),
        gateway=gateway,
        ai_provider=ai_provider,  # type: ignore[arg-type]
        cost_estimator=AICostEstimator(),
        provider_name="openai",
        model="gpt-4o-mini",
    )
    return service, gateway, extractions


async def test_extract_valid_document_succeeds() -> None:
    source = _source()
    user_id = uuid4()
    fields = _empty_padron_fields()
    fields["plate"] = {"value": "ABCD12", "confidence": 0.98}
    fields["brand"] = {"value": "Toyota", "confidence": 0.95}
    ai_result = AIExtractionResult(
        raw_text="{}",
        parsed={
            "document_type": "PADRON",
            "confidence_score": 0.95,
            "fields": fields,
            "warnings": [],
            "requires_review": False,
        },
        model="gpt-4o-mini",
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        processing_time_ms=250,
    )
    service, _, _ = _service(
        source=source, user_id=user_id, ai_provider=FakeAIProvider(result=ai_result)
    )

    extraction = await service.extract(user_id=user_id, document_id=source.document_id)

    assert extraction.status == ExtractionStatus.COMPLETED
    assert extraction.confidence_score == 0.95
    assert extraction.estimated_cost_usd is not None
    assert extraction.total_tokens == 150


async def test_extract_rejects_document_from_another_user() -> None:
    source = _source()
    owner_id, intruder_id = uuid4(), uuid4()
    service, _, _ = _service(source=source, user_id=owner_id, ai_provider=FakeAIProvider())

    with pytest.raises(NotFoundError):
        await service.extract(user_id=intruder_id, document_id=source.document_id)


async def test_extract_saves_failed_extraction_on_provider_error() -> None:
    source = _source()
    user_id = uuid4()
    service, _, extractions = _service(
        source=source, user_id=user_id, ai_provider=FakeAIProvider(exc=RuntimeError("boom"))
    )

    extraction = await service.extract(user_id=user_id, document_id=source.document_id)

    assert extraction.status == ExtractionStatus.FAILED
    assert extraction.error_message is not None
    assert extractions.by_id[extraction.id].status == ExtractionStatus.FAILED


async def test_extract_saves_failed_extraction_when_pdf_has_no_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.modules.intelligence.application.services.extraction_service as service_module

    monkeypatch.setattr(service_module, "extract_pdf_text", lambda _bytes: None)
    source = _source(content_type="application/pdf")
    user_id = uuid4()
    service, _, _ = _service(source=source, user_id=user_id, ai_provider=FakeAIProvider())

    extraction = await service.extract(user_id=user_id, document_id=source.document_id)

    assert extraction.status == ExtractionStatus.FAILED
    assert "OCR" in (extraction.error_message or "")


async def test_extract_flags_plate_mismatch_as_warning() -> None:
    source = _source(vehicle_plate="ZZZZ99")
    user_id = uuid4()
    fields = _empty_padron_fields()
    fields["plate"] = {"value": "ABCD12", "confidence": 0.9}
    ai_result = AIExtractionResult(
        raw_text="{}",
        parsed={
            "document_type": "PADRON",
            "confidence_score": 0.9,
            "fields": fields,
            "warnings": [],
            "requires_review": False,
        },
        model="gpt-4o-mini",
        input_tokens=10,
        output_tokens=10,
        total_tokens=20,
        processing_time_ms=100,
    )
    service, _, _ = _service(
        source=source, user_id=user_id, ai_provider=FakeAIProvider(result=ai_result)
    )

    extraction = await service.extract(user_id=user_id, document_id=source.document_id)

    assert extraction.status == ExtractionStatus.COMPLETED
    assert extraction.requires_review is True
    assert any("does not match" in w for w in extraction.warnings)


async def test_confirm_applies_fields_via_gateway() -> None:
    source = _source()
    user_id = uuid4()
    fields = _empty_padron_fields()
    fields["brand"] = {"value": "Toyota", "confidence": 0.95}
    ai_result = AIExtractionResult(
        raw_text="{}",
        parsed={
            "document_type": "PADRON",
            "confidence_score": 0.95,
            "fields": fields,
            "warnings": [],
            "requires_review": False,
        },
        model="gpt-4o-mini",
        input_tokens=10,
        output_tokens=10,
        total_tokens=20,
        processing_time_ms=100,
    )
    service, gateway, _ = _service(
        source=source, user_id=user_id, ai_provider=FakeAIProvider(result=ai_result)
    )
    extraction = await service.extract(user_id=user_id, document_id=source.document_id)

    confirmed = await service.confirm(user_id=user_id, extraction_id=extraction.id)

    assert confirmed.status == ExtractionStatus.CONFIRMED
    assert confirmed.confirmed_at is not None
    assert len(gateway.applied_calls) == 1


async def test_reject_marks_extraction_rejected() -> None:
    source = _source()
    user_id = uuid4()
    ai_result = AIExtractionResult(
        raw_text="{}",
        parsed={
            "document_type": "PADRON",
            "confidence_score": 0.5,
            "fields": _empty_padron_fields(),
            "warnings": [],
            "requires_review": True,
        },
        model="gpt-4o-mini",
        input_tokens=10,
        output_tokens=10,
        total_tokens=20,
        processing_time_ms=100,
    )
    service, _, _ = _service(
        source=source, user_id=user_id, ai_provider=FakeAIProvider(result=ai_result)
    )
    extraction = await service.extract(user_id=user_id, document_id=source.document_id)

    rejected = await service.reject(user_id=user_id, extraction_id=extraction.id)

    assert rejected.status == ExtractionStatus.REJECTED
    assert rejected.rejected_at is not None


async def test_confirm_twice_raises_conflict() -> None:
    source = _source()
    user_id = uuid4()
    ai_result = AIExtractionResult(
        raw_text="{}",
        parsed={
            "document_type": "PADRON",
            "confidence_score": 0.95,
            "fields": _empty_padron_fields(),
            "warnings": [],
            "requires_review": False,
        },
        model="gpt-4o-mini",
        input_tokens=10,
        output_tokens=10,
        total_tokens=20,
        processing_time_ms=100,
    )
    service, _, _ = _service(
        source=source, user_id=user_id, ai_provider=FakeAIProvider(result=ai_result)
    )
    extraction = await service.extract(user_id=user_id, document_id=source.document_id)
    await service.confirm(user_id=user_id, extraction_id=extraction.id)

    with pytest.raises(ConflictError):
        await service.confirm(user_id=user_id, extraction_id=extraction.id)


async def test_confirm_applies_field_overrides_instead_of_ai_value() -> None:
    source = _source()
    user_id = uuid4()
    fields = _empty_padron_fields()
    fields["vin"] = {"value": None, "confidence": None}
    fields["chassis_number"] = {"value": "LAR18S31710837", "confidence": 0.8}
    ai_result = AIExtractionResult(
        raw_text="{}",
        parsed={
            "document_type": "PADRON",
            "confidence_score": 0.8,
            "fields": fields,
            "warnings": [],
            "requires_review": False,
        },
        model="gpt-4o-mini",
        input_tokens=10,
        output_tokens=10,
        total_tokens=20,
        processing_time_ms=100,
    )
    service, gateway, _ = _service(
        source=source, user_id=user_id, ai_provider=FakeAIProvider(result=ai_result)
    )
    extraction = await service.extract(user_id=user_id, document_id=source.document_id)

    confirmed = await service.confirm(
        user_id=user_id, extraction_id=extraction.id, field_overrides={"vin": "CORRECTED123"}
    )

    assert confirmed.extracted_data is not None
    assert confirmed.extracted_data["fields"]["vin"]["value"] == "CORRECTED123"
    assert confirmed.extracted_data["fields"]["vin"]["source"] == "manual"
    applied_fields = gateway.applied_calls[0][3]
    assert applied_fields["vin"] == "CORRECTED123"


async def test_confirm_ignores_overrides_for_unknown_field_names() -> None:
    source = _source()
    user_id = uuid4()
    ai_result = AIExtractionResult(
        raw_text="{}",
        parsed={
            "document_type": "PADRON",
            "confidence_score": 0.8,
            "fields": _empty_padron_fields(),
            "warnings": [],
            "requires_review": False,
        },
        model="gpt-4o-mini",
        input_tokens=10,
        output_tokens=10,
        total_tokens=20,
        processing_time_ms=100,
    )
    service, _, _ = _service(
        source=source, user_id=user_id, ai_provider=FakeAIProvider(result=ai_result)
    )
    extraction = await service.extract(user_id=user_id, document_id=source.document_id)

    confirmed = await service.confirm(
        user_id=user_id,
        extraction_id=extraction.id,
        field_overrides={"not_a_real_field": "ignored"},
    )

    assert confirmed.extracted_data is not None
    assert "not_a_real_field" not in confirmed.extracted_data["fields"]
