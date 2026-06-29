from dataclasses import dataclass

from src.modules.platform.domain.entities import PlatformModule


@dataclass(frozen=True, slots=True)
class ModuleAvailability:
    """A `PlatformModule` joined with whether *this* user has it enabled —
    exactly the shape `GET /platform/modules` needs, computed once in
    `UserModuleService` instead of forcing the frontend to cross-reference
    two endpoints."""

    module: PlatformModule
    is_enabled: bool
