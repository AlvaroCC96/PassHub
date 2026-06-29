from uuid import UUID, uuid4

from src.domain.base import Entity


class DocumentExtractedField(Entity):
    """One row per field the AI returned for one `DocumentExtraction` —
    denormalized out of `extracted_data` JSON into queryable rows (e.g. "show
    every expiration_date extracted across a user's documents"). `source` is
    `"ai"` for every row created today; reserved for `"manual"` once a future
    sprint lets a user correct a single field instead of rejecting the whole
    extraction."""

    def __init__(
        self,
        *,
        id: UUID,
        extraction_id: UUID,
        field_name: str,
        field_value: str | None,
        normalized_value: str | None,
        confidence_score: float | None,
        source: str = "ai",
    ) -> None:
        super().__init__(id)
        self.extraction_id = extraction_id
        self.field_name = field_name
        self.field_value = field_value
        self.normalized_value = normalized_value
        self.confidence_score = confidence_score
        self.source = source

    @classmethod
    def create(
        cls,
        *,
        extraction_id: UUID,
        field_name: str,
        field_value: str | None,
        normalized_value: str | None,
        confidence_score: float | None,
    ) -> "DocumentExtractedField":
        return cls(
            id=uuid4(),
            extraction_id=extraction_id,
            field_name=field_name,
            field_value=field_value,
            normalized_value=normalized_value,
            confidence_score=confidence_score,
        )
