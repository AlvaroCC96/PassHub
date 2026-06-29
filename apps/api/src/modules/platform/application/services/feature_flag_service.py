from uuid import UUID

from src.modules.platform.application.ports import (
    FeatureFlagRepository,
    PlatformModuleRepository,
    UserModuleRepository,
)
from src.modules.platform.domain.entities import FeatureFlag
from src.modules.platform.domain.value_objects import FeatureFlagScope, ModuleCode


class FeatureFlagService:
    """Flag storage plus a deliberately simple relevance rule — there is no
    rules engine yet. `GLOBAL` flags are relevant to everyone; `MODULE`
    flags are relevant only if the caller has that specific module enabled;
    `USER` flags are returned as-is until per-user overrides are modeled
    (none are seeded in this sprint)."""

    def __init__(
        self,
        flag_repository: FeatureFlagRepository,
        user_module_repository: UserModuleRepository,
        platform_module_repository: PlatformModuleRepository,
    ) -> None:
        self._flags = flag_repository
        self._user_modules = user_module_repository
        self._platform_modules = platform_module_repository

    async def list_relevant_for_user(self, user_id: UUID) -> list[FeatureFlag]:
        all_flags = await self._flags.list_all()
        enabled_codes = await self._enabled_module_codes(user_id)
        return [flag for flag in all_flags if self._is_relevant(flag, enabled_codes)]

    async def _enabled_module_codes(self, user_id: UUID) -> set[ModuleCode]:
        enabled_module_ids = {
            um.module_id for um in await self._user_modules.list_for_user(user_id) if um.is_enabled
        }
        if not enabled_module_ids:
            return set()
        modules = await self._platform_modules.list_all()
        return {m.code for m in modules if m.id in enabled_module_ids}

    @staticmethod
    def _is_relevant(flag: FeatureFlag, enabled_module_codes: set[ModuleCode]) -> bool:
        if flag.scope == FeatureFlagScope.MODULE:
            return flag.module_code is not None and flag.module_code in enabled_module_codes
        return True

    async def is_enabled(self, key: str) -> bool:
        flag = await self._flags.get_by_key(key)
        return flag is not None and flag.enabled
