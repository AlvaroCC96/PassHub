from enum import StrEnum


class DocumentType(StrEnum):
    """Every document type PassHub knows about. `LICENCIA_CONDUCIR` belongs to
    a user, not a vehicle — it's declared here (mirroring how Identity's
    `AuthProvider` declares values with no working flow yet) so the column
    type doesn't need a breaking migration when driver's licenses are
    implemented. `VEHICLE_DOCUMENT_TYPES` is what every vehicle-document
    endpoint actually accepts."""

    PADRON = "PADRON"
    SOAP = "SOAP"
    REVISION_TECNICA = "REVISION_TECNICA"
    CERTIFICADO_GASES = "CERTIFICADO_GASES"
    CERTIFICADO_HOMOLOGACION = "CERTIFICADO_HOMOLOGACION"
    PERMISO_CIRCULACION = "PERMISO_CIRCULACION"
    SEGURO_PARTICULAR = "SEGURO_PARTICULAR"
    LICENCIA_CONDUCIR = "LICENCIA_CONDUCIR"


VEHICLE_DOCUMENT_TYPES: frozenset[DocumentType] = frozenset(
    {
        DocumentType.PADRON,
        DocumentType.SOAP,
        DocumentType.REVISION_TECNICA,
        DocumentType.CERTIFICADO_GASES,
        DocumentType.CERTIFICADO_HOMOLOGACION,
        DocumentType.PERMISO_CIRCULACION,
        DocumentType.SEGURO_PARTICULAR,
    }
)

DOCUMENT_TYPE_LABELS: dict[DocumentType, str] = {
    DocumentType.PADRON: "Padrón",
    DocumentType.SOAP: "SOAP",
    DocumentType.REVISION_TECNICA: "Revisión Técnica",
    DocumentType.CERTIFICADO_GASES: "Certificado de Gases",
    DocumentType.CERTIFICADO_HOMOLOGACION: "Certificado de Homologación",
    DocumentType.PERMISO_CIRCULACION: "Permiso de Circulación",
    DocumentType.SEGURO_PARTICULAR: "Seguro Particular",
    DocumentType.LICENCIA_CONDUCIR: "Licencia de Conducir",
}
