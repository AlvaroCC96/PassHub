from typing import Protocol
from uuid import UUID

from src.modules.drivepass.documents.domain.entities import VehicleDocument
from src.modules.drivepass.documents.domain.value_objects import DocumentType


class VehicleDocumentRepository(Protocol):
    async def get_by_id(self, document_id: UUID) -> VehicleDocument | None: ...

    async def get_by_vehicle_and_type(
        self, *, vehicle_id: UUID, document_type: DocumentType
    ) -> VehicleDocument | None: ...

    async def list_for_vehicle(self, vehicle_id: UUID) -> list[VehicleDocument]: ...

    async def add(self, document: VehicleDocument) -> None: ...

    async def save(self, document: VehicleDocument) -> None: ...

    async def soft_delete(self, document: VehicleDocument) -> None: ...
