from datetime import UTC, date, datetime
from io import BytesIO
from uuid import UUID, uuid4

from src.application.ports import StorageProvider
from src.core.config import Settings
from src.core.exceptions import NotFoundError, ValidationError
from src.core.logging import get_logger
from src.modules.drivepass.documents.application.dto import DocumentStatusSummary
from src.modules.drivepass.documents.application.ports import (
    DocumentVersionRepository,
    VehicleDocumentRepository,
)
from src.modules.drivepass.documents.application.storage_paths import build_storage_key
from src.modules.drivepass.documents.domain.entities import DocumentVersion, VehicleDocument
from src.modules.drivepass.documents.domain.file_validation import (
    compute_checksum,
    safe_filename,
    validate_upload,
)
from src.modules.drivepass.documents.domain.rules import is_required
from src.modules.drivepass.documents.domain.value_objects import (
    VEHICLE_DOCUMENT_TYPES,
    DocumentStatus,
    DocumentType,
    DocumentVisibility,
    OverallDocumentStatus,
)

DOWNLOAD_URL_EXPIRY_SECONDS = 300

logger = get_logger(__name__)


class VehicleDocumentService:
    """Owns the per-vehicle document checklist: lazily creating the MISSING
    rows, keeping `is_required`/`status` in sync with the clock and with
    CERTIFICADO_HOMOLOGACION's own state, and brokering every upload through
    `StorageProvider` so nothing here knows it's MinIO underneath."""

    def __init__(
        self,
        *,
        document_repository: VehicleDocumentRepository,
        version_repository: DocumentVersionRepository,
        storage_provider: StorageProvider,
        settings: Settings,
    ) -> None:
        self._documents = document_repository
        self._versions = version_repository
        self._storage = storage_provider
        self._bucket = settings.storage.bucket

    async def list_for_vehicle(self, vehicle_id: UUID) -> list[VehicleDocument]:
        await self._ensure_initialized(vehicle_id)
        documents = await self._documents.list_for_vehicle(vehicle_id)
        await self._sync_all(documents)
        return documents

    async def get_document(self, *, vehicle_id: UUID, document_id: UUID) -> VehicleDocument:
        document = await self._documents.get_by_id(document_id)
        if document is None or document.vehicle_id != vehicle_id:
            raise NotFoundError("Document not found", error_code="document_not_found")
        return document

    async def list_versions(self, *, vehicle_id: UUID, document_id: UUID) -> list[DocumentVersion]:
        await self.get_document(vehicle_id=vehicle_id, document_id=document_id)  # ownership check
        return await self._versions.list_for_document(document_id)

    async def get_status_summary(self, vehicle_id: UUID) -> DocumentStatusSummary:
        documents = await self.list_for_vehicle(vehicle_id)

        required = [d for d in documents if d.is_required]
        missing_required = [d for d in required if d.status == DocumentStatus.MISSING]
        expired = [d for d in documents if d.status == DocumentStatus.EXPIRED]
        expiring_soon = [d for d in documents if d.status == DocumentStatus.EXPIRING_SOON]
        uploaded = [d for d in documents if d.current_version_id is not None]

        completion = 100
        if required:
            completion = round(100 * (len(required) - len(missing_required)) / len(required))

        if missing_required:
            overall = OverallDocumentStatus.INCOMPLETE
        elif expired:
            overall = OverallDocumentStatus.EXPIRED
        elif expiring_soon:
            overall = OverallDocumentStatus.WARNING
        else:
            overall = OverallDocumentStatus.COMPLETE

        summary = DocumentStatusSummary(
            total_documents=len(documents),
            required_documents=len(required),
            uploaded_documents=len(uploaded),
            missing_required_documents=len(missing_required),
            expired_documents=len(expired),
            expiring_soon_documents=len(expiring_soon),
            completion_percentage=completion,
            overall_status=overall,
        )
        logger.info(
            "document_status_calculated",
            category="drivepass.audit",
            vehicle_id=str(vehicle_id),
            overall_status=overall.value,
            completion_percentage=completion,
        )
        return summary

    async def upload_initial(
        self,
        *,
        vehicle_id: UUID,
        user_id: UUID,
        document_type: DocumentType,
        filename: str,
        content_bytes: bytes,
        issue_date: date | None,
        expiration_date: date | None,
        visibility: DocumentVisibility | None,
    ) -> VehicleDocument:
        if document_type not in VEHICLE_DOCUMENT_TYPES:
            raise ValidationError(
                f"'{document_type}' is not a vehicle document type",
                error_code="invalid_document_type",
            )
        await self._ensure_initialized(vehicle_id)
        document = await self._documents.get_by_vehicle_and_type(
            vehicle_id=vehicle_id, document_type=document_type
        )
        if document is None:
            raise NotFoundError("Document not found", error_code="document_not_found")

        return await self._upload_version(
            document=document,
            user_id=user_id,
            filename=filename,
            content_bytes=content_bytes,
            issue_date=issue_date,
            expiration_date=expiration_date,
            visibility=visibility,
        )

    async def upload_new_version(
        self,
        *,
        vehicle_id: UUID,
        document_id: UUID,
        user_id: UUID,
        filename: str,
        content_bytes: bytes,
        issue_date: date | None,
        expiration_date: date | None,
        visibility: DocumentVisibility | None,
    ) -> VehicleDocument:
        document = await self.get_document(vehicle_id=vehicle_id, document_id=document_id)
        return await self._upload_version(
            document=document,
            user_id=user_id,
            filename=filename,
            content_bytes=content_bytes,
            issue_date=issue_date,
            expiration_date=expiration_date,
            visibility=visibility,
        )

    async def get_download_url(self, *, vehicle_id: UUID, document_id: UUID) -> tuple[str, int]:
        document = await self.get_document(vehicle_id=vehicle_id, document_id=document_id)
        if document.current_version_id is None:
            raise NotFoundError(
                "Document has no uploaded version yet", error_code="no_version_uploaded"
            )

        version = await self._versions.get_by_id(document.current_version_id)
        if version is None:
            raise NotFoundError("Document version not found", error_code="version_not_found")

        url = await self._storage.get_presigned_url(
            key=version.storage_path,
            bucket=version.storage_bucket,
            expires_in_seconds=DOWNLOAD_URL_EXPIRY_SECONDS,
        )
        logger.info(
            "document_download_url_created",
            category="drivepass.audit",
            vehicle_id=str(vehicle_id),
            document_id=str(document_id),
        )
        return url, DOWNLOAD_URL_EXPIRY_SECONDS

    async def set_visibility(
        self, *, vehicle_id: UUID, document_id: UUID, visibility: DocumentVisibility
    ) -> VehicleDocument:
        document = await self.get_document(vehicle_id=vehicle_id, document_id=document_id)
        document.set_visibility(visibility)
        await self._documents.save(document)
        logger.info(
            "document_visibility_changed",
            category="drivepass.audit",
            vehicle_id=str(vehicle_id),
            document_id=str(document_id),
            visibility=visibility.value,
        )
        return document

    async def delete(self, *, vehicle_id: UUID, document_id: UUID) -> None:
        document = await self.get_document(vehicle_id=vehicle_id, document_id=document_id)
        await self._documents.soft_delete(document)
        logger.info(
            "document_deleted",
            category="drivepass.audit",
            vehicle_id=str(vehicle_id),
            document_id=str(document_id),
        )

    async def _upload_version(
        self,
        *,
        document: VehicleDocument,
        user_id: UUID,
        filename: str,
        content_bytes: bytes,
        issue_date: date | None,
        expiration_date: date | None,
        visibility: DocumentVisibility | None,
    ) -> VehicleDocument:
        content_type = validate_upload(
            filename=filename, size_bytes=len(content_bytes), content_bytes=content_bytes
        )
        stored_name = safe_filename(filename)
        version_id = uuid4()
        key = build_storage_key(
            user_id=user_id,
            vehicle_id=document.vehicle_id,
            document_type=document.document_type,
            version_id=version_id,
            filename=stored_name,
        )

        storage_object = await self._storage.upload(
            key=key, data=BytesIO(content_bytes), content_type=content_type, bucket=self._bucket
        )
        checksum = compute_checksum(content_bytes)

        existing_count = await self._versions.count_for_document(document.id)
        await self._versions.mark_all_not_current(document.id)
        version = DocumentVersion(
            id=version_id,
            document_id=document.id,
            version_number=existing_count + 1,
            original_filename=filename,
            stored_filename=stored_name,
            storage_bucket=storage_object.bucket,
            storage_path=key,
            content_type=content_type,
            file_size_bytes=storage_object.size_bytes,
            checksum_sha256=checksum,
            uploaded_by_user_id=user_id,
            uploaded_at=datetime.now(UTC),
            is_current=True,
        )
        await self._versions.add(version)

        document.attach_version(
            version.id,
            issue_date=issue_date,
            expiration_date=expiration_date,
            visibility=visibility,
        )
        document.recompute_status(today=datetime.now(UTC).date())
        await self._documents.save(document)

        event = "document_uploaded" if version.version_number == 1 else "document_version_created"
        logger.info(
            event,
            category="drivepass.audit",
            vehicle_id=str(document.vehicle_id),
            document_id=str(document.id),
            version_number=version.version_number,
        )
        return document

    async def _ensure_initialized(self, vehicle_id: UUID) -> None:
        existing = await self._documents.list_for_vehicle(vehicle_id)
        existing_types = {d.document_type for d in existing}
        missing_types = VEHICLE_DOCUMENT_TYPES - existing_types
        if not missing_types:
            return

        homologation_valid = self._homologation_is_valid(existing, today=datetime.now(UTC).date())
        for document_type in missing_types:
            document = VehicleDocument.create_missing(
                vehicle_id=vehicle_id,
                document_type=document_type,
                is_required=is_required(document_type, has_valid_homologation=homologation_valid),
            )
            await self._documents.add(document)

    async def _sync_all(self, documents: list[VehicleDocument]) -> None:
        today = datetime.now(UTC).date()
        for document in documents:
            document.recompute_status(today=today)

        homologation_valid = self._homologation_is_valid(documents, today=today)
        for document in documents:
            required = is_required(
                document.document_type, has_valid_homologation=homologation_valid
            )
            if required != document.is_required:
                document.set_required(required)
            await self._documents.save(document)

    @staticmethod
    def _homologation_is_valid(documents: list[VehicleDocument], *, today: date) -> bool:
        homologation = next(
            (d for d in documents if d.document_type == DocumentType.CERTIFICADO_HOMOLOGACION), None
        )
        if homologation is None or homologation.current_version_id is None:
            return False
        if homologation.expiration_date is None:
            return True
        return homologation.expiration_date >= today
