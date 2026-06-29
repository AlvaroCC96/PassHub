from uuid import UUID

from src.domain.base import Entity
from src.modules.platform.domain.value_objects import ModuleCode, ModuleStatus


class PlatformModule(Entity):
    """A business module catalog entry (DrivePass, HomePass, ...). Defines
    what the module *is* at the platform level — display metadata and
    lifecycle status. Whether a given user has it turned on is a separate
    concept, tracked by `UserModule`."""

    def __init__(
        self,
        *,
        id: UUID,
        code: ModuleCode,
        name: str,
        description: str,
        icon: str,
        route_path: str,
        status: ModuleStatus,
        is_core: bool,
        sort_order: int,
    ) -> None:
        super().__init__(id)
        self.code = code
        self.name = name
        self.description = description
        self.icon = icon
        self.route_path = route_path
        self.status = status
        self.is_core = is_core
        self.sort_order = sort_order

    @property
    def is_enableable(self) -> bool:
        """Only ACTIVE modules can be turned on/off by a user. COMING_SOON
        and INACTIVE modules are visible but locked; DEPRECATED ones are
        hidden from the catalog entirely (see `PlatformModuleService`)."""
        return self.status == ModuleStatus.ACTIVE
