from typing import Protocol
from uuid import UUID

from src.modules.platform.domain.entities import UserModule


class UserModuleRepository(Protocol):
    async def get(self, *, user_id: UUID, module_id: UUID) -> UserModule | None: ...

    async def list_for_user(self, user_id: UUID) -> list[UserModule]: ...

    async def add(self, user_module: UserModule) -> None: ...

    async def save(self, user_module: UserModule) -> None: ...
