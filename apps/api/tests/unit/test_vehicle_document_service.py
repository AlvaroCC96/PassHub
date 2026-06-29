from datetime import UTC, datetime
from typing import BinaryIO
from uuid import UUID, uuid4

import pytest
from src.application.ports import StorageObject
from src.core.config import Settings
from src.core.exceptions import NotFoundError, ValidationError
from src.modules.drivepass.documents.application.services import VehicleDocumentService
from src.modules.drivepass.documents.domain.entities import DocumentVersion, VehicleDocument
from src.modules.drivepass.documents.domain.value_objects import DocumentStatus, DocumentType

MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
MINIMAL_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


class FakeVehicleDocumentRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, VehicleDocument] = {}

    async def get_by_id(self, document_id: UUID) -> VehicleDocument | None:
        return self._by_id.get(document_id)

    async def get_by_vehicle_and_type(
        self, *, vehicle_id: UUID, document_type: DocumentType
    ) -> VehicleDocument | None:
        return next(
            (
                d
                for d in self._by_id.values()
                if d.vehicle_id == vehicle_id and d.document_type == document_type
            ),
            None,
        )

    async def list_for_vehicle(self, vehicle_id: UUID) -> list[VehicleDocument]:
        return [d for d in self._by_id.values() if d.vehicle_id == vehicle_id]

    async def add(self, document: VehicleDocument) -> None:
        self._by_id[document.id] = document

    async def save(self, document: VehicleDocument) -> None:
        self._by_id[document.id] = document

    async def soft_delete(self, document: VehicleDocument) -> None:
        self._by_id.pop(document.id, None)


class FakeDocumentVersionRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, DocumentVersion] = {}

    async def get_by_id(self, version_id: UUID) -> DocumentVersion | None:
        return self._by_id.get(version_id)

    async def list_for_document(self, document_id: UUID) -> list[DocumentVersion]:
        versions = [v for v in self._by_id.values() if v.document_id == document_id]
        return sorted(versions, key=lambda v: v.version_number, reverse=True)

    async def count_for_document(self, document_id: UUID) -> int:
        return len([v for v in self._by_id.values() if v.document_id == document_id])

    async def add(self, version: DocumentVersion) -> None:
        self._by_id[version.id] = version

    async def mark_all_not_current(self, document_id: UUID) -> None:
        for version in self._by_id.values():
            if version.document_id == document_id:
                version.is_current = False


class FakeStorageProvider:
    def __init__(self) -> None:
        self.uploaded: dict[str, bytes] = {}

    async def upload(
        self, *, key: str, data: BinaryIO, content_type: str, bucket: str | None = None
    ) -> StorageObject:
        payload = data.read()
        self.uploaded[key] = payload
        return StorageObject(
            key=key,
            bucket=bucket or "test-bucket",
            content_type=content_type,
            size_bytes=len(payload),
        )

    async def download(self, *, key: str, bucket: str | None = None) -> bytes:
        return self.uploaded[key]

    async def delete(self, *, key: str, bucket: str | None = None) -> None:
        self.uploaded.pop(key, None)

    async def get_presigned_url(
        self, *, key: str, bucket: str | None = None, expires_in_seconds: int = 3600
    ) -> str:
        return f"https://fake-storage.test/{bucket}/{key}?expires={expires_in_seconds}"


def _service() -> tuple[VehicleDocumentService, FakeStorageProvider]:
    storage = FakeStorageProvider()
    service = VehicleDocumentService(
        document_repository=FakeVehicleDocumentRepository(),
        version_repository=FakeDocumentVersionRepository(),
        storage_provider=storage,  # type: ignore[arg-type]
        settings=Settings(),
    )
    return service, storage


async def test_list_for_vehicle_initializes_full_checklist() -> None:
    service, _ = _service()
    vehicle_id = uuid4()

    documents = await service.list_for_vehicle(vehicle_id)

    assert len(documents) == 7
    required_types = {d.document_type for d in documents if d.is_required}
    assert required_types == {
        DocumentType.PADRON,
        DocumentType.SOAP,
        DocumentType.PERMISO_CIRCULACION,
        DocumentType.REVISION_TECNICA,
        DocumentType.CERTIFICADO_GASES,
    }
    assert all(d.status == DocumentStatus.MISSING for d in documents)


async def test_upload_valid_document_succeeds() -> None:
    service, storage = _service()
    vehicle_id, user_id = uuid4(), uuid4()

    document = await service.upload_initial(
        vehicle_id=vehicle_id,
        user_id=user_id,
        document_type=DocumentType.PADRON,
        filename="padron.pdf",
        content_bytes=MINIMAL_PDF,
        issue_date=None,
        expiration_date=None,
        visibility=None,
    )

    assert document.status == DocumentStatus.UPLOADED
    assert document.current_version_id is not None
    assert len(storage.uploaded) == 1
    stored_key = next(iter(storage.uploaded))
    assert f"/vehicles/{vehicle_id}/documents/PADRON/" in stored_key


async def test_upload_rejects_disallowed_file_type() -> None:
    service, _ = _service()

    with pytest.raises(ValidationError):
        await service.upload_initial(
            vehicle_id=uuid4(),
            user_id=uuid4(),
            document_type=DocumentType.SOAP,
            filename="not-a-real.pdf",
            content_bytes=b"plain text pretending to be a pdf",
            issue_date=None,
            expiration_date=None,
            visibility=None,
        )


async def test_upload_rejects_file_over_10mb() -> None:
    service, _ = _service()
    oversized = MINIMAL_PDF + b"0" * (10 * 1024 * 1024 + 1)

    with pytest.raises(ValidationError):
        await service.upload_initial(
            vehicle_id=uuid4(),
            user_id=uuid4(),
            document_type=DocumentType.SOAP,
            filename="big.pdf",
            content_bytes=oversized,
            issue_date=None,
            expiration_date=None,
            visibility=None,
        )


async def test_upload_rejects_non_vehicle_document_type() -> None:
    service, _ = _service()

    with pytest.raises(ValidationError):
        await service.upload_initial(
            vehicle_id=uuid4(),
            user_id=uuid4(),
            document_type=DocumentType.LICENCIA_CONDUCIR,
            filename="license.pdf",
            content_bytes=MINIMAL_PDF,
            issue_date=None,
            expiration_date=None,
            visibility=None,
        )


async def test_document_from_one_vehicle_is_not_visible_from_another() -> None:
    service, _ = _service()
    vehicle_id, other_vehicle_id, user_id = uuid4(), uuid4(), uuid4()

    document = await service.upload_initial(
        vehicle_id=vehicle_id,
        user_id=user_id,
        document_type=DocumentType.PADRON,
        filename="padron.pdf",
        content_bytes=MINIMAL_PDF,
        issue_date=None,
        expiration_date=None,
        visibility=None,
    )

    with pytest.raises(NotFoundError):
        await service.get_document(vehicle_id=other_vehicle_id, document_id=document.id)


async def test_new_version_supersedes_the_previous_one() -> None:
    service, _ = _service()
    vehicle_id, user_id = uuid4(), uuid4()

    first = await service.upload_initial(
        vehicle_id=vehicle_id,
        user_id=user_id,
        document_type=DocumentType.SOAP,
        filename="soap-v1.pdf",
        content_bytes=MINIMAL_PDF,
        issue_date=None,
        expiration_date=None,
        visibility=None,
    )
    first_version_id = first.current_version_id

    updated = await service.upload_new_version(
        vehicle_id=vehicle_id,
        document_id=first.id,
        user_id=user_id,
        filename="soap-v2.png",
        content_bytes=MINIMAL_PNG,
        issue_date=None,
        expiration_date=None,
        visibility=None,
    )

    assert updated.current_version_id != first_version_id
    versions = await service._versions.list_for_document(first.id)  # noqa: SLF001
    assert len(versions) == 2
    superseded = next(v for v in versions if v.id == first_version_id)
    assert superseded.is_current is False


async def test_get_download_url_returns_signed_url() -> None:
    service, _ = _service()
    vehicle_id, user_id = uuid4(), uuid4()

    document = await service.upload_initial(
        vehicle_id=vehicle_id,
        user_id=user_id,
        document_type=DocumentType.PADRON,
        filename="padron.pdf",
        content_bytes=MINIMAL_PDF,
        issue_date=None,
        expiration_date=None,
        visibility=None,
    )

    url, expires_in = await service.get_download_url(vehicle_id=vehicle_id, document_id=document.id)

    assert expires_in == 300
    assert url.startswith("https://fake-storage.test/")


async def test_status_summary_reflects_required_and_missing_documents() -> None:
    service, _ = _service()
    vehicle_id, user_id = uuid4(), uuid4()

    await service.upload_initial(
        vehicle_id=vehicle_id,
        user_id=user_id,
        document_type=DocumentType.PADRON,
        filename="padron.pdf",
        content_bytes=MINIMAL_PDF,
        issue_date=None,
        expiration_date=None,
        visibility=None,
    )

    summary = await service.get_status_summary(vehicle_id)

    assert summary.total_documents == 7
    assert summary.required_documents == 5  # no valid CERTIFICADO_HOMOLOGACION yet
    assert summary.uploaded_documents == 1
    assert summary.missing_required_documents == 4
    assert summary.completion_percentage == 20
    assert summary.overall_status.value == "INCOMPLETE"


async def test_valid_homologation_makes_conditional_documents_optional() -> None:
    service, _ = _service()
    vehicle_id, user_id = uuid4(), uuid4()
    far_future = datetime.now(UTC).date().replace(year=datetime.now(UTC).year + 1)

    await service.upload_initial(
        vehicle_id=vehicle_id,
        user_id=user_id,
        document_type=DocumentType.CERTIFICADO_HOMOLOGACION,
        filename="homologacion.pdf",
        content_bytes=MINIMAL_PDF,
        issue_date=None,
        expiration_date=far_future,
        visibility=None,
    )

    documents = await service.list_for_vehicle(vehicle_id)
    conditional = {
        d.document_type: d.is_required
        for d in documents
        if d.document_type in (DocumentType.REVISION_TECNICA, DocumentType.CERTIFICADO_GASES)
    }
    assert conditional == {
        DocumentType.REVISION_TECNICA: False,
        DocumentType.CERTIFICADO_GASES: False,
    }


async def test_delete_then_list_recreates_a_fresh_missing_row() -> None:
    service, _ = _service()
    vehicle_id, user_id = uuid4(), uuid4()

    document = await service.upload_initial(
        vehicle_id=vehicle_id,
        user_id=user_id,
        document_type=DocumentType.PADRON,
        filename="padron.pdf",
        content_bytes=MINIMAL_PDF,
        issue_date=None,
        expiration_date=None,
        visibility=None,
    )
    await service.delete(vehicle_id=vehicle_id, document_id=document.id)

    documents = await service.list_for_vehicle(vehicle_id)
    padron = next(d for d in documents if d.document_type == DocumentType.PADRON)
    assert padron.status == DocumentStatus.MISSING
    assert padron.id != document.id


async def test_list_versions_returns_full_history_newest_first() -> None:
    service, _ = _service()
    vehicle_id, user_id = uuid4(), uuid4()

    document = await service.upload_initial(
        vehicle_id=vehicle_id,
        user_id=user_id,
        document_type=DocumentType.SOAP,
        filename="soap-v1.pdf",
        content_bytes=MINIMAL_PDF,
        issue_date=None,
        expiration_date=None,
        visibility=None,
    )
    await service.upload_new_version(
        vehicle_id=vehicle_id,
        document_id=document.id,
        user_id=user_id,
        filename="soap-v2.png",
        content_bytes=MINIMAL_PNG,
        issue_date=None,
        expiration_date=None,
        visibility=None,
    )

    versions = await service.list_versions(vehicle_id=vehicle_id, document_id=document.id)

    assert [v.version_number for v in versions] == [2, 1]
    assert versions[0].is_current is True
    assert versions[1].is_current is False


async def test_upload_to_nonexistent_document_raises_not_found() -> None:
    service, _ = _service()

    with pytest.raises(NotFoundError):
        await service.upload_new_version(
            vehicle_id=uuid4(),
            document_id=uuid4(),
            user_id=uuid4(),
            filename="x.pdf",
            content_bytes=MINIMAL_PDF,
            issue_date=None,
            expiration_date=None,
            visibility=None,
        )
