from datetime import date
from uuid import UUID, uuid4

from src.modules.drivepass.documents.domain.entities import VehicleDocument
from src.modules.drivepass.documents.domain.value_objects import (
    DocumentStatus,
    DocumentType,
    DocumentVisibility,
)
from src.modules.drivepass.infrastructure.intelligence_gateway import DrivePassDocumentGateway
from src.modules.drivepass.vehicles.application.services import VehicleService
from src.modules.drivepass.vehicles.domain.entities import Vehicle


class FakeVehicleDocumentRepository:
    def __init__(self, document: VehicleDocument) -> None:
        self._document = document

    async def get_by_id(self, document_id: UUID) -> VehicleDocument | None:
        return self._document if document_id == self._document.id else None

    async def save(self, document: VehicleDocument) -> None:
        self._document = document


class FakeVehicleRepository:
    def __init__(self, vehicle: Vehicle) -> None:
        self.vehicle = vehicle

    async def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        return self.vehicle if vehicle_id == self.vehicle.id else None

    async def get_active_by_user_and_plate(self, *, user_id: UUID, plate: str) -> Vehicle | None:
        return None

    async def list_for_user(self, user_id: UUID) -> list[Vehicle]:
        return [self.vehicle]

    async def get_favorite_for_user(self, user_id: UUID) -> Vehicle | None:
        return None

    async def add(self, vehicle: Vehicle) -> None:
        self.vehicle = vehicle

    async def save(self, vehicle: Vehicle) -> None:
        self.vehicle = vehicle

    async def soft_delete(self, vehicle: Vehicle) -> None:
        pass


def _homologacion_document(vehicle_id: UUID) -> VehicleDocument:
    return VehicleDocument(
        id=uuid4(),
        vehicle_id=vehicle_id,
        document_type=DocumentType.CERTIFICADO_HOMOLOGACION,
        display_name="Certificado de Homologación",
        status=DocumentStatus.UPLOADED,
        visibility=DocumentVisibility.PRIVATE,
        is_required=False,
        current_version_id=uuid4(),
    )


async def test_apply_confirmed_fields_writes_vin_and_expiration_for_homologacion() -> None:
    user_id = uuid4()
    vehicle = Vehicle.register(
        user_id=user_id, plate="ABCD12", brand="Toyota", model="Yaris", year=2020
    )
    document = _homologacion_document(vehicle.id)

    document_repo = FakeVehicleDocumentRepository(document)
    vehicle_repo = FakeVehicleRepository(vehicle)
    vehicle_service = VehicleService(vehicle_repo)
    gateway = DrivePassDocumentGateway(
        document_repository=document_repo,  # type: ignore[arg-type]
        version_repository=None,  # type: ignore[arg-type]
        storage_provider=None,  # type: ignore[arg-type]
        vehicle_service=vehicle_service,
    )

    outcome = await gateway.apply_confirmed_fields(
        user_id=user_id,
        document_id=document.id,
        document_type=DocumentType.CERTIFICADO_HOMOLOGACION.value,
        fields={
            "plate": "ABCD12",
            "vin": "9BWZZZ377VT004251",
            "expiration_date": "2027-03-31",
        },
    )

    assert outcome.plate_mismatch is False
    assert "vin" in outcome.applied_fields
    assert "expiration_date" in outcome.applied_fields
    assert document.expiration_date == date(2027, 3, 31)
    assert document.status == DocumentStatus.VALID
    assert vehicle_repo.vehicle.vin == "9BWZZZ377VT004251"
