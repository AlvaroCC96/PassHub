from src.modules.platform.application.ports import PlatformSettingRepository
from src.modules.platform.domain.entities import PlatformSetting


class PlatformSettingService:
    """See `PlatformSetting`'s docstring: there is no `is_public` flag yet,
    so `list_public` returns every setting. Safe today because only public
    values are seeded — revisit before adding anything sensitive here."""

    def __init__(self, repository: PlatformSettingRepository) -> None:
        self._repository = repository

    async def list_public(self) -> list[PlatformSetting]:
        return await self._repository.list_all()

    async def get(self, key: str) -> PlatformSetting | None:
        return await self._repository.get_by_key(key)
