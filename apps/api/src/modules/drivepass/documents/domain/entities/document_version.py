from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.domain.base import Entity


class DocumentVersion(Entity):
    """An immutable upload. Replacing a document never overwrites a file —
    it creates a new version and flips `is_current`. Past versions are kept
    (and never deleted by anything in this sprint) so a document's history
    is always reconstructable."""

    def __init__(
        self,
        *,
        id: UUID,
        document_id: UUID,
        version_number: int,
        original_filename: str,
        stored_filename: str,
        storage_bucket: str,
        storage_path: str,
        content_type: str,
        file_size_bytes: int,
        checksum_sha256: str,
        uploaded_by_user_id: UUID,
        uploaded_at: datetime,
        is_current: bool = True,
    ) -> None:
        super().__init__(id)
        self.document_id = document_id
        self.version_number = version_number
        self.original_filename = original_filename
        self.stored_filename = stored_filename
        self.storage_bucket = storage_bucket
        self.storage_path = storage_path
        self.content_type = content_type
        self.file_size_bytes = file_size_bytes
        self.checksum_sha256 = checksum_sha256
        self.uploaded_by_user_id = uploaded_by_user_id
        self.uploaded_at = uploaded_at
        self.is_current = is_current

    @classmethod
    def create(
        cls,
        *,
        document_id: UUID,
        version_number: int,
        original_filename: str,
        stored_filename: str,
        storage_bucket: str,
        storage_path: str,
        content_type: str,
        file_size_bytes: int,
        checksum_sha256: str,
        uploaded_by_user_id: UUID,
    ) -> "DocumentVersion":
        return cls(
            id=uuid4(),
            document_id=document_id,
            version_number=version_number,
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_bucket=storage_bucket,
            storage_path=storage_path,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            checksum_sha256=checksum_sha256,
            uploaded_by_user_id=uploaded_by_user_id,
            uploaded_at=datetime.now(UTC),
            is_current=True,
        )
