from enum import StrEnum


class PublicAccessStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    LOCKED = "LOCKED"
