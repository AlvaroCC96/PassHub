from dataclasses import dataclass

from src.modules.drivepass.documents.domain.value_objects import OverallDocumentStatus


@dataclass(frozen=True, slots=True)
class DocumentStatusSummary:
    total_documents: int
    required_documents: int
    uploaded_documents: int
    missing_required_documents: int
    expired_documents: int
    expiring_soon_documents: int
    completion_percentage: int
    overall_status: OverallDocumentStatus


@dataclass(frozen=True, slots=True)
class UploadResult:
    """What `StorageProvider.upload` plus our own hashing produces — kept
    separate from `StorageObject` because it also carries the checksum,
    which is a Documents concern, not a generic storage one."""

    storage_bucket: str
    storage_path: str
    content_type: str
    size_bytes: int
    checksum_sha256: str
