from src.core.exceptions import NotFoundError
from src.modules.platform.application.ports import PlatformModuleRepository
from src.modules.platform.domain.entities import PlatformModule
from src.modules.platform.domain.value_objects import ModuleCode, ModuleStatus

#: Statuses shown in the catalog. DEPRECATED modules are a backend lifecycle
#: state — once a module reaches it, it should stop being offered to anyone,
#: not just show up "locked" the way COMING_SOON does.
_VISIBLE_STATUSES = frozenset({ModuleStatus.ACTIVE, ModuleStatus.COMING_SOON})


class PlatformModuleService:
    """Read access to the module catalog. Enabling/disabling per user is
    `UserModuleService`'s job — this service only knows about modules as
    platform-wide entities."""

    def __init__(self, repository: PlatformModuleRepository) -> None:
        self._repository = repository

    async def list_visible_modules(self) -> list[PlatformModule]:
        modules = await self._repository.list_all()
        visible = [m for m in modules if m.status in _VISIBLE_STATUSES]
        return sorted(visible, key=lambda m: m.sort_order)

    async def get_by_code(self, code: ModuleCode) -> PlatformModule:
        module = await self._repository.get_by_code(code)
        if module is None:
            raise NotFoundError(f"Module '{code}' does not exist", error_code="module_not_found")
        return module
