from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.drivepass.documents.domain.entities import DocumentVersion, VehicleDocument
from src.modules.drivepass.documents.domain.value_objects import DocumentType
from src.modules.drivepass.documents.infrastructure.models import (
    DocumentVersionModel,
    VehicleDocumentModel,
)


def _document_to_domain(model: VehicleDocumentModel) -> VehicleDocument:
    return VehicleDocument(
        id=model.id,
        vehicle_id=model.vehicle_id,
        document_type=model.document_type,
        display_name=model.display_name,
        status=model.status,
        visibility=model.visibility,
        is_required=model.is_required,
        issue_date=model.issue_date,
        expiration_date=model.expiration_date,
        current_version_id=model.current_version_id,
    )


def _version_to_domain(model: DocumentVersionModel) -> DocumentVersion:
    return DocumentVersion(
        id=model.id,
        document_id=model.document_id,
        version_number=model.version_number,
        original_filename=model.original_filename,
        stored_filename=model.stored_filename,
        storage_bucket=model.storage_bucket,
        storage_path=model.storage_path,
        content_type=model.content_type,
        file_size_bytes=model.file_size_bytes,
        checksum_sha256=model.checksum_sha256,
        uploaded_by_user_id=model.uploaded_by_user_id,
        uploaded_at=model.uploaded_at,
        is_current=model.is_current,
    )


class SqlAlchemyVehicleDocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, document_id: UUID) -> VehicleDocument | None:
        model = await self._session.get(VehicleDocumentModel, document_id)
        return _document_to_domain(model) if model and not model.is_deleted else None

    async def get_by_vehicle_and_type(
        self, *, vehicle_id: UUID, document_type: DocumentType
    ) -> VehicleDocument | None:
        stmt = select(VehicleDocumentModel).where(
            VehicleDocumentModel.vehicle_id == vehicle_id,
            VehicleDocumentModel.document_type == document_type,
            VehicleDocumentModel.deleted_at.is_(None),
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return _document_to_domain(model) if model else None

    async def list_for_vehicle(self, vehicle_id: UUID) -> list[VehicleDocument]:
        stmt = select(VehicleDocumentModel).where(
            VehicleDocumentModel.vehicle_id == vehicle_id, VehicleDocumentModel.deleted_at.is_(None)
        )
        models = (await self._session.execute(stmt)).scalars().all()
        return [_document_to_domain(m) for m in models]

    async def add(self, document: VehicleDocument) -> None:
        self._session.add(
            VehicleDocumentModel(
                id=document.id,
                vehicle_id=document.vehicle_id,
                document_type=document.document_type,
                display_name=document.display_name,
                status=document.status,
                visibility=document.visibility,
                is_required=document.is_required,
                issue_date=document.issue_date,
                expiration_date=document.expiration_date,
                current_version_id=document.current_version_id,
            )
        )
        await self._session.flush()

    async def save(self, document: VehicleDocument) -> None:
        model = await self._session.get(VehicleDocumentModel, document.id)
        if model is None:
            raise LookupError(f"VehicleDocument {document.id} does not exist")
        model.display_name = document.display_name
        model.status = document.status
        model.visibility = document.visibility
        model.is_required = document.is_required
        model.issue_date = document.issue_date
        model.expiration_date = document.expiration_date
        model.current_version_id = document.current_version_id
        await self._session.flush()

    async def soft_delete(self, document: VehicleDocument) -> None:
        model = await self._session.get(VehicleDocumentModel, document.id)
        if model is None:
            raise LookupError(f"VehicleDocument {document.id} does not exist")
        model.deleted_at = datetime.now(UTC)
        await self._session.flush()


class SqlAlchemyDocumentVersionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, version_id: UUID) -> DocumentVersion | None:
        model = await self._session.get(DocumentVersionModel, version_id)
        return _version_to_domain(model) if model and not model.is_deleted else None

    async def list_for_document(self, document_id: UUID) -> list[DocumentVersion]:
        stmt = (
            select(DocumentVersionModel)
            .where(
                DocumentVersionModel.document_id == document_id,
                DocumentVersionModel.deleted_at.is_(None),
            )
            .order_by(DocumentVersionModel.version_number.desc())
        )
        models = (await self._session.execute(stmt)).scalars().all()
        return [_version_to_domain(m) for m in models]

    async def count_for_document(self, document_id: UUID) -> int:
        stmt = select(func.count()).where(DocumentVersionModel.document_id == document_id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def add(self, version: DocumentVersion) -> None:
        self._session.add(
            DocumentVersionModel(
                id=version.id,
                document_id=version.document_id,
                version_number=version.version_number,
                original_filename=version.original_filename,
                stored_filename=version.stored_filename,
                storage_bucket=version.storage_bucket,
                storage_path=version.storage_path,
                content_type=version.content_type,
                file_size_bytes=version.file_size_bytes,
                checksum_sha256=version.checksum_sha256,
                uploaded_by_user_id=version.uploaded_by_user_id,
                uploaded_at=version.uploaded_at,
                is_current=version.is_current,
            )
        )
        await self._session.flush()

    async def mark_all_not_current(self, document_id: UUID) -> None:
        stmt = (
            update(DocumentVersionModel)
            .where(DocumentVersionModel.document_id == document_id)
            .values(is_current=False)
        )
        await self._session.execute(stmt)
        await self._session.flush()
