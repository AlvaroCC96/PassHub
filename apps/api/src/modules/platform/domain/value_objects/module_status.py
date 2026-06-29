from enum import StrEnum


class ModuleStatus(StrEnum):
    """Lifecycle state of a module at the platform level — independent of
    whether any given user has it enabled (see `UserModuleStatus`)."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    COMING_SOON = "COMING_SOON"
    DEPRECATED = "DEPRECATED"
