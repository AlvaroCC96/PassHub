from enum import StrEnum


class ExtractableDocumentType(StrEnum):
    """Mirrors `DocumentType`'s 7 vehicle-document values in
    `src.modules.drivepass.documents.domain.value_objects.document_type` —
    declared independently, by value, so Intelligence's domain never imports
    DrivePass. `LICENCIA_CONDUCIR` has no entry here for the same reason it's
    excluded from DrivePass's own `VEHICLE_DOCUMENT_TYPES`: it isn't a
    vehicle document."""

    PADRON = "PADRON"
    SOAP = "SOAP"
    REVISION_TECNICA = "REVISION_TECNICA"
    CERTIFICADO_GASES = "CERTIFICADO_GASES"
    CERTIFICADO_HOMOLOGACION = "CERTIFICADO_HOMOLOGACION"
    PERMISO_CIRCULACION = "PERMISO_CIRCULACION"
    SEGURO_PARTICULAR = "SEGURO_PARTICULAR"


#: Field names the extraction schema asks the model for, per document type.
#: `plate` is first and present everywhere — every vehicle document carries
#: the plate, and it's how `DocumentExtractionService` cross-checks the
#: extraction against the vehicle it was uploaded under.
EXTRACTABLE_FIELD_NAMES: dict[ExtractableDocumentType, tuple[str, ...]] = {
    ExtractableDocumentType.PADRON: (
        "plate",
        "brand",
        "model",
        "year",
        "color",
        "vin",
        "chassis_number",
        "engine_number",
        "owner_name",
        "owner_rut",
    ),
    ExtractableDocumentType.SOAP: (
        "plate",
        "insurance_company",
        "policy_number",
        "issue_date",
        "expiration_date",
    ),
    ExtractableDocumentType.REVISION_TECNICA: (
        "plate",
        "inspection_date",
        "expiration_date",
        "inspection_result",
        "plant_name",
    ),
    ExtractableDocumentType.CERTIFICADO_GASES: (
        "plate",
        "issue_date",
        "expiration_date",
        "result",
    ),
    ExtractableDocumentType.PERMISO_CIRCULACION: (
        "plate",
        "municipality",
        "issue_date",
        "expiration_date",
        "paid_amount",
    ),
    ExtractableDocumentType.CERTIFICADO_HOMOLOGACION: (
        "plate",
        "brand",
        "model",
        "year",
        "vin",
        "issue_date",
        "expiration_date",
    ),
    ExtractableDocumentType.SEGURO_PARTICULAR: (
        "plate",
        "insurance_company",
        "policy_number",
        "issue_date",
        "expiration_date",
        "coverage_type",
    ),
}

#: Fields that, once confirmed, are written back onto `VehicleDocument`
#: itself (`update_dates`) rather than just kept as informational metadata.
DOCUMENT_DATE_FIELDS: tuple[str, ...] = ("issue_date", "expiration_date")

#: Fields that, once confirmed for a PADRON extraction, are written back
#: onto `Vehicle` — guarded by the plate-match check (see
#: `domain.rules.plate_matches`). `chassis_number` isn't its own `Vehicle`
#: column — many Padrón documents print only "N° de Chasis" with no field
#: labeled "VIN" at all, so the gateway falls back to `chassis_number` for
#: `vehicle.vin` whenever `vin` itself comes back empty.
VEHICLE_IDENTITY_FIELDS: tuple[str, ...] = (
    "brand",
    "model",
    "year",
    "color",
    "vin",
    "engine_number",
)
