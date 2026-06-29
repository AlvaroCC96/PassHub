from typing import Protocol
from uuid import UUID

from src.modules.platform.domain.entities import PlatformModule
from src.modules.platform.domain.value_objects import ModuleCode


class PlatformModuleRepository(Protocol):
    async def get_by_id(self, module_id: UUID) -> PlatformModule | None: ...

    async def get_by_code(self, code: ModuleCode) -> PlatformModule | None: ...

    async def list_all(self) -> list[PlatformModule]: ...

    async def add(self, module: PlatformModule) -> None: ...

    async def save(self, module: PlatformModule) -> None: ...
