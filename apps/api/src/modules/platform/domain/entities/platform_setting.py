from typing import Any
from uuid import UUID

from src.domain.base import Entity


class PlatformSetting(Entity):
    """A global, JSON-valued platform configuration entry (brand name,
    default module, etc.). Every setting seeded in this sprint is meant to
    be public — there is no `is_public` flag yet. Add one before seeding
    anything sensitive here; `PlatformSettingService.list_public` currently
    returns everything."""

    def __init__(self, *, id: UUID, key: str, value: Any, description: str) -> None:
        super().__init__(id)
        self.key = key
        self.value = value
        self.description = description
