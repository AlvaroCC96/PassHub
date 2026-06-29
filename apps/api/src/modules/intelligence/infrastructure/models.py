import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.database import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin
from src.modules.intelligence.domain.value_objects import ExtractionStatus


class DocumentExtractionModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "document_extractions"
    __table_args__ = (Index("ix_document_extractions_document_id_created_at", "document_id", "id"),)

    # No FK to `vehicle_documents`/`document_versions` — same reasoning as
    # `VehicleDocumentModel.current_version_id`: Intelligence is a separate
    # top-level module from DrivePass and must not hard-depend on its
    # tables at the schema level either, only through `VehicleDocumentGateway`.
    document_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), index=True)
    document_version_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True))
    vehicle_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    provider: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(100))
    prompt_version: Mapped[str] = mapped_column(String(100))
    status: Mapped[ExtractionStatus] = mapped_column(
        SAEnum(ExtractionStatus, name="extraction_status"), index=True
    )
    raw_response: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    extracted_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost_usd: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DocumentExtractedFieldModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "document_extracted_fields"
    __table_args__ = (Index("ix_document_extracted_fields_extraction_id", "extraction_id"),)

    extraction_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("document_extractions.id", ondelete="CASCADE"),
        index=True,
    )
    field_name: Mapped[str] = mapped_column(String(100))
    field_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="ai")
