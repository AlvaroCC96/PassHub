from enum import StrEnum


class ModuleCode(StrEnum):
    """Identifies a business module. Adding a new module (e.g. a future
    `OFFICE_PASS`) means adding a value here and a seed row — nothing in the
    platform core hardcodes business logic per module."""

    DRIVE_PASS = "DRIVE_PASS"
    HOME_PASS = "HOME_PASS"
    PET_PASS = "PET_PASS"
    HEALTH_PASS = "HEALTH_PASS"
    FAMILY_PASS = "FAMILY_PASS"
