from src.modules.drivepass.documents.domain.value_objects import DocumentType

#: Always required, regardless of any other document's state.
ALWAYS_REQUIRED_TYPES: frozenset[DocumentType] = frozenset(
    {DocumentType.PADRON, DocumentType.SOAP, DocumentType.PERMISO_CIRCULACION}
)

#: Required unless the vehicle has a currently-valid CERTIFICADO_HOMOLOGACION.
CONDITIONALLY_REQUIRED_TYPES: frozenset[DocumentType] = frozenset(
    {DocumentType.REVISION_TECNICA, DocumentType.CERTIFICADO_GASES}
)

#: Never required outright. CERTIFICADO_HOMOLOGACION sits here too — it's the
#: *condition*, not itself a required document.
ALWAYS_OPTIONAL_TYPES: frozenset[DocumentType] = frozenset(
    {DocumentType.SEGURO_PARTICULAR, DocumentType.CERTIFICADO_HOMOLOGACION}
)


def is_required(document_type: DocumentType, *, has_valid_homologation: bool) -> bool:
    if document_type in ALWAYS_REQUIRED_TYPES:
        return True
    if document_type in CONDITIONALLY_REQUIRED_TYPES:
        return not has_valid_homologation
    return False
