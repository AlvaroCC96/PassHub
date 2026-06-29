from enum import StrEnum


class DocumentStatus(StrEnum):
    MISSING = "MISSING"
    UPLOADED = "UPLOADED"
    VALID = "VALID"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"
    #: No automatic rule sets this yet (e.g. an electric vehicle not needing
    #: CERTIFICADO_GASES). Declared for a future sprint, same as `REJECTED`
    #: (no moderation endpoint exists to set it today).
    NOT_APPLICABLE = "NOT_APPLICABLE"
