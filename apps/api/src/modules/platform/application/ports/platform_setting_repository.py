from typing import Protocol

from src.modules.platform.domain.entities import PlatformSetting


class PlatformSettingRepository(Protocol):
    async def get_by_key(self, key: str) -> PlatformSetting | None: ...

    async def list_all(self) -> list[PlatformSetting]: ...

    async def add(self, setting: PlatformSetting) -> None: ...
