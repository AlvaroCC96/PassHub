from uuid import UUID

from src.modules.drivepass.documents.domain.value_objects import DocumentType


def build_storage_key(
    *, user_id: UUID, vehicle_id: UUID, document_type: DocumentType, version_id: UUID, filename: str
) -> str:
    return f"users/{user_id}/vehicles/{vehicle_id}/documents/{document_type.value}/{version_id}/{filename}"
