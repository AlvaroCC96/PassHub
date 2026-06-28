from typing import Protocol
from uuid import UUID

from src.modules.identity.domain.entities import RefreshToken


class RefreshTokenRepository(Protocol):
    async def get_by_id(self, token_id: UUID) -> RefreshToken | None: ...

    async def add(self, token: RefreshToken) -> None: ...

    async def save(self, token: RefreshToken) -> None: ...
