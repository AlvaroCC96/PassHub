from uuid import UUID

from src.core.exceptions import ConflictError
from src.core.logging import get_logger
from src.modules.platform.application.dto import ModuleAvailability
from src.modules.platform.application.ports import PlatformModuleRepository, UserModuleRepository
from src.modules.platform.application.services.platform_module_service import (
    PlatformModuleService,
)
from src.modules.platform.domain.entities import UserModule
from src.modules.platform.domain.value_objects import ModuleCode

logger = get_logger(__name__)

#: Modules every new account gets out of the box. DrivePass is the only
#: business module that exists today — this list is the single place that
#: will grow as future modules earn a default-on spot.
_DEFAULT_MODULES_FOR_NEW_USERS = (ModuleCode.DRIVE_PASS,)


class UserModuleService:
    """Per-user module enablement: the bridge between the platform catalog
    (`PlatformModuleService`) and a specific account's `UserModule` rows."""

    def __init__(
        self,
        user_module_repository: UserModuleRepository,
        platform_module_repository: PlatformModuleRepository,
    ) -> None:
        self._user_modules = user_module_repository
        self._platform_modules = PlatformModuleService(platform_module_repository)
        self._platform_module_repository = platform_module_repository

    async def list_modules_with_status_for_user(self, user_id: UUID) -> list[ModuleAvailability]:
        modules = await self._platform_modules.list_visible_modules()
        user_modules = {um.module_id: um for um in await self._user_modules.list_for_user(user_id)}
        return [
            ModuleAvailability(module=module, is_enabled=_is_enabled(user_modules.get(module.id)))
            for module in modules
        ]

    async def list_enabled_for_user(self, user_id: UUID) -> list[ModuleAvailability]:
        availabilities = await self.list_modules_with_status_for_user(user_id)
        return [a for a in availabilities if a.is_enabled]

    async def enable(self, *, user_id: UUID, code: ModuleCode) -> ModuleAvailability:
        module = await self._platform_modules.get_by_code(code)
        if not module.is_enableable:
            raise ConflictError(
                f"Module '{code}' is not available to enable (status: {module.status})",
                error_code="module_not_enableable",
            )

        existing = await self._user_modules.get(user_id=user_id, module_id=module.id)
        if existing is not None:
            if not existing.is_enabled:
                existing.enable()
                await self._user_modules.save(existing)
        else:
            user_module = UserModule.create_enabled(user_id=user_id, module_id=module.id)
            await self._user_modules.add(user_module)

        logger.info(
            "module_enabled",
            category="platform.audit",
            user_id=str(user_id),
            module_code=code.value,
        )
        return ModuleAvailability(module=module, is_enabled=True)

    async def disable(self, *, user_id: UUID, code: ModuleCode) -> ModuleAvailability:
        module = await self._platform_modules.get_by_code(code)
        if module.is_core:
            raise ConflictError(
                f"Module '{code}' is core and cannot be disabled", error_code="module_is_core"
            )

        existing = await self._user_modules.get(user_id=user_id, module_id=module.id)
        if existing is None or not existing.is_enabled:
            raise ConflictError(
                f"Module '{code}' is not enabled for this user", error_code="module_not_enabled"
            )

        existing.disable()
        await self._user_modules.save(existing)
        logger.info(
            "module_disabled",
            category="platform.audit",
            user_id=str(user_id),
            module_code=code.value,
        )
        return ModuleAvailability(module=module, is_enabled=False)

    async def enable_default_modules_for_new_user(self, user_id: UUID) -> None:
        """Called once, right after a brand-new account is created (see
        `NewUserProvisioner`). Failures here intentionally propagate — if a
        default module can't be enabled, the signup should fail loudly
        rather than silently leave the user without it."""
        for code in _DEFAULT_MODULES_FOR_NEW_USERS:
            module = await self._platform_module_repository.get_by_code(code)
            if module is None or not module.is_enableable:
                continue
            user_module = UserModule.create_enabled(user_id=user_id, module_id=module.id)
            await self._user_modules.add(user_module)
            logger.info(
                "module_enabled",
                category="platform.audit",
                user_id=str(user_id),
                module_code=code.value,
                reason="default_for_new_user",
            )


def _is_enabled(user_module: UserModule | None) -> bool:
    return user_module is not None and user_module.is_enabled
