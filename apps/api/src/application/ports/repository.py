from typing import Protocol, TypeVar
from uuid import UUID

from src.domain.base import Entity

T = TypeVar("T", bound=Entity)


class Repository(Protocol[T]):
    """Generic persistence port. Each module defines its own concrete
    repository interfaces on top of this shape; no business entity is
    declared yet in Sprint 0."""

    async def get_by_id(self, entity_id: UUID) -> T | None: ...

    async def add(self, entity: T) -> None: ...

    async def delete(self, entity: T) -> None: ...
