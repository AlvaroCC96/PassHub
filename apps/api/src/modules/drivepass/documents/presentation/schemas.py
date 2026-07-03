from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel
from src.modules.drivepass.documents.application.dto import DocumentStatusSummary
from src.modules.drivepass.documents.domain.entities import DocumentVersion, VehicleDocument
from src.modules.drivepass.documents.domain.value_objects import (
    DocumentStatus,
    DocumentType,
    DocumentVisibility,
    OverallDocumentStatus,
)


class VehicleDocumentResponse(BaseModel):
    id: UUID
    document_type: DocumentType
    display_name: str
    status: DocumentStatus
    visibility: DocumentVisibility
    is_required: bool
    issue_date: date | None
    expiration_date: date | None
    current_version_id: UUID | None

    @classmethod
    def from_domain(cls, document: VehicleDocument) -> "VehicleDocumentResponse":
        return cls(
            id=document.id,
            document_type=document.document_type,
            display_name=document.display_name,
            status=document.status,
            visibility=document.visibility,
            is_required=document.is_required,
            issue_date=document.issue_date,
            expiration_date=document.expiration_date,
            current_version_id=document.current_version_id,
        )


class DocumentStatusSummaryResponse(BaseModel):
    total_documents: int
    required_documents: int
    uploaded_documents: int
    missing_required_documents: int
    expired_documents: int
    expiring_soon_documents: int
    completion_percentage: int
    overall_status: OverallDocumentStatus

    @classmethod
    def from_dto(cls, summary: DocumentStatusSummary) -> "DocumentStatusSummaryResponse":
        return cls(
            total_documents=summary.total_documents,
            required_documents=summary.required_documents,
            uploaded_documents=summary.uploaded_documents,
            missing_required_documents=summary.missing_required_documents,
            expired_documents=summary.expired_documents,
            expiring_soon_documents=summary.expiring_soon_documents,
            completion_percentage=summary.completion_percentage,
            overall_status=summary.overall_status,
        )


class SetVisibilityRequest(BaseModel):
    visibility: DocumentVisibility


class DownloadUrlResponse(BaseModel):
    url: str
    expires_in: int


class DocumentVersionResponse(BaseModel):
    id: UUID
    version_number: int
    original_filename: str
    content_type: str
    file_size_bytes: int
    uploaded_by_user_id: UUID
    uploaded_at: datetime
    is_current: bool

    @classmethod
    def from_domain(cls, version: DocumentVersion) -> "DocumentVersionResponse":
        return cls(
            id=version.id,
            version_number=version.version_number,
            original_filename=version.original_filename,
            content_type=version.content_type,
            file_size_bytes=version.file_size_bytes,
            uploaded_by_user_id=version.uploaded_by_user_id,
            uploaded_at=version.uploaded_at,
            is_current=version.is_current,
        )
