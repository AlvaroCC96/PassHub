from uuid import UUID

from src.modules.platform.application.services import UserModuleService


class PlatformUserProvisioner:
    """Implements Identity's `NewUserProvisioner` port. This is the one
    concrete seam between the two modules — Identity only ever sees the
    port, never this class or `UserModuleService` directly."""

    def __init__(self, user_module_service: UserModuleService) -> None:
        self._user_module_service = user_module_service

    async def on_user_registered(self, *, user_id: UUID) -> None:
        await self._user_module_service.enable_default_modules_for_new_user(user_id)
