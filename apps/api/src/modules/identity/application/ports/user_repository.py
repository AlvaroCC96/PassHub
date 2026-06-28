from typing import Protocol
from uuid import UUID

from src.modules.identity.domain.entities import User
from src.modules.identity.domain.value_objects import AuthProvider


class UserRepository(Protocol):
    async def get_by_id(self, user_id: UUID) -> User | None: ...

    async def get_by_provider_identity(
        self, *, provider: AuthProvider, provider_subject_id: str
    ) -> User | None: ...

    async def add(self, user: User) -> None: ...

    async def save(self, user: User) -> None: ...
