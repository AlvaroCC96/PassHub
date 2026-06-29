from typing import Any

from pydantic import BaseModel
from src.modules.platform.application.dto import ModuleAvailability
from src.modules.platform.domain.entities import FeatureFlag, PlatformSetting
from src.modules.platform.domain.value_objects import FeatureFlagScope, ModuleCode, ModuleStatus


class PlatformModuleResponse(BaseModel):
    code: ModuleCode
    name: str
    description: str
    icon: str
    route_path: str
    status: ModuleStatus
    is_core: bool
    sort_order: int
    is_enabled: bool

    @classmethod
    def from_availability(cls, availability: ModuleAvailability) -> "PlatformModuleResponse":
        module = availability.module
        return cls(
            code=module.code,
            name=module.name,
            description=module.description,
            icon=module.icon,
            route_path=module.route_path,
            status=module.status,
            is_core=module.is_core,
            sort_order=module.sort_order,
            is_enabled=availability.is_enabled,
        )


class FeatureFlagResponse(BaseModel):
    key: str
    description: str
    enabled: bool
    scope: FeatureFlagScope
    module_code: ModuleCode | None

    @classmethod
    def from_domain(cls, flag: FeatureFlag) -> "FeatureFlagResponse":
        return cls(
            key=flag.key,
            description=flag.description,
            enabled=flag.enabled,
            scope=flag.scope,
            module_code=flag.module_code,
        )


class PlatformSettingResponse(BaseModel):
    key: str
    value: Any
    description: str

    @classmethod
    def from_domain(cls, setting: PlatformSetting) -> "PlatformSettingResponse":
        return cls(key=setting.key, value=setting.value, description=setting.description)
