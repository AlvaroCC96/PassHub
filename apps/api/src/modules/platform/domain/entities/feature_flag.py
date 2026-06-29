from uuid import UUID

from src.domain.base import Entity
from src.modules.platform.domain.value_objects import FeatureFlagScope, ModuleCode


class FeatureFlag(Entity):
    """A simple on/off switch. No evaluation engine yet — `scope`/`module_code`
    only describe *what a flag is about*; `FeatureFlagService` does the
    (currently simple) job of deciding which flags are relevant to a caller."""

    def __init__(
        self,
        *,
        id: UUID,
        key: str,
        description: str,
        enabled: bool,
        scope: FeatureFlagScope,
        module_code: ModuleCode | None = None,
    ) -> None:
        super().__init__(id)
        self.key = key
        self.description = description
        self.enabled = enabled
        self.scope = scope
        self.module_code = module_code
