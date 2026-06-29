import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.database import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin
from src.modules.drivepass.documents.domain.value_objects import (
    DocumentStatus,
    DocumentType,
    DocumentVisibility,
)


class VehicleDocumentModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "vehicle_documents"
    __table_args__ = (
        # Partial, not a plain UniqueConstraint: without `WHERE deleted_at IS
        # NULL`, a soft-deleted document would keep occupying its (vehicle,
        # type) slot, blocking `_ensure_initialized` from ever recreating
        # that type's MISSING row — verified live, this was the exact cause
        # of an IntegrityError on the next list call after a delete.
        Index(
            "uq_vehicle_documents_vehicle_type",
            "vehicle_id",
            "document_type",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
    )

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), index=True
    )
    document_type: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType, name="document_type"), index=True
    )
    display_name: Mapped[str] = mapped_column(String(150))
    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(DocumentStatus, name="document_status"), index=True
    )
    visibility: Mapped[DocumentVisibility] = mapped_column(
        SAEnum(DocumentVisibility, name="document_visibility"), default=DocumentVisibility.PRIVATE
    )
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Denormalized pointer to `document_versions.id` — deliberately NOT a
    # foreign key. A real FK would be circular (document_versions.document_id
    # already points back at this table), and this column is fully derivable
    # at any time from `document_versions WHERE document_id = ... AND
    # is_current`. Treat it as a cache, not a source of truth.
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )


class DocumentVersionModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint(
            "document_id", "version_number", name="uq_document_versions_document_number"
        ),
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("vehicle_documents.id", ondelete="CASCADE"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer)
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(255))
    storage_bucket: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[str] = mapped_column(String(1024))
    content_type: Mapped[str] = mapped_column(String(100))
    file_size_bytes: Mapped[int] = mapped_column(Integer)
    checksum_sha256: Mapped[str] = mapped_column(String(64))
    uploaded_by_user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
