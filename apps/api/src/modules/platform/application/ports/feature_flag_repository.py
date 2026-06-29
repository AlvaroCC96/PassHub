from typing import Protocol

from src.modules.platform.domain.entities import FeatureFlag


class FeatureFlagRepository(Protocol):
    async def get_by_key(self, key: str) -> FeatureFlag | None: ...

    async def list_all(self) -> list[FeatureFlag]: ...

    async def add(self, flag: FeatureFlag) -> None: ...
