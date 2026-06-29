from datetime import UTC, date, datetime
from uuid import UUID

from src.application.ports import StorageProvider
from src.core.exceptions import NotFoundError
from src.modules.drivepass.documents.application.ports import (
    DocumentVersionRepository,
    VehicleDocumentRepository,
)
from src.modules.drivepass.documents.domain.value_objects import DocumentType
from src.modules.drivepass.vehicles.application.services import VehicleService
from src.modules.drivepass.vehicles.domain.entities import normalize_plate
from src.modules.intelligence.application.ports import (
    ExtractionSourceDocument,
    FieldApplicationOutcome,
)

#: Fields applied straight onto `VehicleDocument` (issue/expiration only —
#: every other extracted field for non-PADRON types is informational, kept
#: in `DocumentExtractedField` rows but never written onto an entity).
_DOCUMENT_DATE_FIELDS = ("issue_date", "expiration_date")

#: Fields applied onto `Vehicle` when a PADRON or CERTIFICADO_HOMOLOGACION
#: extraction is confirmed, guarded by the plate-match check below — both
#: document types carry the vehicle's identity (CERTIFICADO_HOMOLOGACION
#: just doesn't print color/engine_number, so those simply stay absent from
#: `fields` and are skipped as a no-op).
_VEHICLE_IDENTITY_FIELDS = ("brand", "model", "year", "color", "vin", "engine_number")
_VEHICLE_IDENTITY_DOCUMENT_TYPES = (
    DocumentType.PADRON.value,
    DocumentType.CERTIFICADO_HOMOLOGACION.value,
)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


class DrivePassDocumentGateway:
    """Implements Intelligence's `VehicleDocumentGateway` port. This is the
    one file in the codebase that imports both `drivepass` and
    `intelligence` — everywhere else, each module only sees the port."""

    def __init__(
        self,
        *,
        document_repository: VehicleDocumentRepository,
        version_repository: DocumentVersionRepository,
        storage_provider: StorageProvider,
        vehicle_service: VehicleService,
    ) -> None:
        self._documents = document_repository
        self._versions = version_repository
        self._storage = storage_provider
        self._vehicles = vehicle_service

    async def get_source_document(
        self, *, user_id: UUID, document_id: UUID
    ) -> ExtractionSourceDocument:
        document = await self._documents.get_by_id(document_id)
        if document is None:
            raise NotFoundError("Document not found", error_code="document_not_found")
        # Ownership is enforced here, not assumed — same 404-for-both-cases
        # rule `VehicleService.get_for_user` already applies.
        vehicle = await self._vehicles.get_for_user(user_id=user_id, vehicle_id=document.vehicle_id)

        if document.current_version_id is None:
            raise NotFoundError(
                "Document has no uploaded version yet", error_code="no_version_uploaded"
            )
        version = await self._versions.get_by_id(document.current_version_id)
        if version is None:
            raise NotFoundError("Document version not found", error_code="version_not_found")

        content_bytes = await self._storage.download(
            key=version.storage_path, bucket=version.storage_bucket
        )
        return ExtractionSourceDocument(
            document_id=document.id,
            document_version_id=version.id,
            vehicle_id=vehicle.id,
            document_type=document.document_type.value,
            vehicle_plate=vehicle.plate,
            content_bytes=content_bytes,
            content_type=version.content_type,
            original_filename=version.original_filename,
        )

    async def apply_confirmed_fields(
        self,
        *,
        user_id: UUID,
        document_id: UUID,
        document_type: str,
        fields: dict[str, str | None],
    ) -> FieldApplicationOutcome:
        document = await self._documents.get_by_id(document_id)
        if document is None:
            raise NotFoundError("Document not found", error_code="document_not_found")
        vehicle = await self._vehicles.get_for_user(user_id=user_id, vehicle_id=document.vehicle_id)

        applied: list[str] = []
        skipped: list[str] = []
        plate_mismatch = False

        date_updates = {f: _parse_date(fields.get(f)) for f in _DOCUMENT_DATE_FIELDS}
        if any(name in fields for name in _DOCUMENT_DATE_FIELDS):
            document.update_dates(
                issue_date=date_updates["issue_date"] or document.issue_date,
                expiration_date=date_updates["expiration_date"] or document.expiration_date,
            )
            document.recompute_status(today=datetime.now(UTC).date())
            await self._documents.save(document)
            applied.extend(name for name, value in date_updates.items() if value is not None)
            skipped.extend(
                name
                for name in _DOCUMENT_DATE_FIELDS
                if name in fields and date_updates[name] is None
            )

        if document_type in _VEHICLE_IDENTITY_DOCUMENT_TYPES:
            extracted_plate = fields.get("plate")
            if extracted_plate and normalize_plate(extracted_plate) != vehicle.plate:
                plate_mismatch = True
                skipped.extend(_VEHICLE_IDENTITY_FIELDS)
            else:
                vehicle_updates: dict[str, str] = {
                    name: value
                    for name in _VEHICLE_IDENTITY_FIELDS
                    if (value := fields.get(name)) is not None
                }
                # Many Padrón documents print only "N° de Chasis", with no
                # field labeled "VIN" at all — fall back to it so `vin`
                # still gets populated instead of silently staying empty.
                if "vin" not in vehicle_updates:
                    chassis_number = fields.get("chassis_number")
                    if chassis_number is not None:
                        vehicle_updates["vin"] = chassis_number

                if vehicle_updates:
                    year_raw = vehicle_updates.get("year")
                    year = vehicle.year
                    if year_raw is not None:
                        try:
                            year = int(year_raw)
                        except ValueError:
                            vehicle_updates.pop("year", None)

                    await self._vehicles.update(
                        user_id=user_id,
                        vehicle_id=vehicle.id,
                        plate=vehicle.plate,
                        brand=vehicle_updates.get("brand", vehicle.brand),
                        model=vehicle_updates.get("model", vehicle.model),
                        year=year,
                        color=vehicle_updates.get("color", vehicle.color),
                        vin=vehicle_updates.get("vin", vehicle.vin),
                        engine_number=vehicle_updates.get("engine_number", vehicle.engine_number),
                        nickname=vehicle.nickname,
                        fuel_type=vehicle.fuel_type,
                        transmission=vehicle.transmission,
                    )
                    applied.extend(vehicle_updates.keys())

        return FieldApplicationOutcome(
            applied_fields=applied, skipped_fields=skipped, plate_mismatch=plate_mismatch
        )
