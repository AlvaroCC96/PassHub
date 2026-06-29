"""Idempotent platform seed data.

Module *display* fields (name, description, icon, route_path, sort_order,
status, is_core) are owned by this file, not by any admin UI — re-running the
seed re-syncs them to whatever is defined here. Feature flags and settings
are insert-if-missing only: once a flag has been toggled at runtime, reseeding
must never silently reset it.

Run with: `uv run python -m src.modules.platform.infrastructure.seed`
"""

import asyncio
import logging
from dataclasses import dataclass
from uuid import uuid4

from src.infrastructure.database.session import session_scope
from src.modules.platform.domain.entities import FeatureFlag, PlatformModule, PlatformSetting
from src.modules.platform.domain.value_objects import FeatureFlagScope, ModuleCode, ModuleStatus
from src.modules.platform.infrastructure.repositories import (
    SqlAlchemyFeatureFlagRepository,
    SqlAlchemyPlatformModuleRepository,
    SqlAlchemyPlatformSettingRepository,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class _ModuleSeed:
    code: ModuleCode
    name: str
    description: str
    icon: str
    route_path: str
    status: ModuleStatus
    is_core: bool
    sort_order: int


@dataclass(frozen=True, slots=True)
class _FlagSeed:
    key: str
    description: str
    enabled: bool
    scope: FeatureFlagScope
    module_code: ModuleCode | None = None


@dataclass(frozen=True, slots=True)
class _SettingSeed:
    key: str
    value: object
    description: str


MODULE_SEEDS: tuple[_ModuleSeed, ...] = (
    _ModuleSeed(
        code=ModuleCode.DRIVE_PASS,
        name="DrivePass",
        description="Digital vehicle identity and document vault.",
        icon="car",
        route_path="/app/drive",
        status=ModuleStatus.ACTIVE,
        is_core=False,
        sort_order=1,
    ),
    _ModuleSeed(
        code=ModuleCode.HOME_PASS,
        name="HomePass",
        description="Home documentation, insurance, and shared expenses.",
        icon="home",
        route_path="/app/home",
        status=ModuleStatus.COMING_SOON,
        is_core=False,
        sort_order=2,
    ),
    _ModuleSeed(
        code=ModuleCode.PET_PASS,
        name="PetPass",
        description="Pets, vaccines, and veterinary records.",
        icon="paw",
        route_path="/app/pets",
        status=ModuleStatus.COMING_SOON,
        is_core=False,
        sort_order=3,
    ),
    _ModuleSeed(
        code=ModuleCode.HEALTH_PASS,
        name="HealthPass",
        description="Personal medical records and checkups.",
        icon="heart",
        route_path="/app/health",
        status=ModuleStatus.COMING_SOON,
        is_core=False,
        sort_order=4,
    ),
    _ModuleSeed(
        code=ModuleCode.FAMILY_PASS,
        name="FamilyPass",
        description="Shared documentation for the whole family.",
        icon="users",
        route_path="/app/family",
        status=ModuleStatus.COMING_SOON,
        is_core=False,
        sort_order=5,
    ),
)

FEATURE_FLAG_SEEDS: tuple[_FlagSeed, ...] = (
    _FlagSeed(
        key="drivepass.enabled",
        description="Master switch for the DrivePass module.",
        enabled=True,
        scope=FeatureFlagScope.MODULE,
        module_code=ModuleCode.DRIVE_PASS,
    ),
    _FlagSeed(
        key="ai.document_extraction.enabled",
        description="AI-powered document data extraction (not implemented yet).",
        enabled=False,
        scope=FeatureFlagScope.GLOBAL,
    ),
    _FlagSeed(
        key="nfc.public_portal.enabled",
        description="Public NFC-accessible vehicle document portal (not implemented yet).",
        enabled=False,
        scope=FeatureFlagScope.GLOBAL,
    ),
    _FlagSeed(
        key="notifications.expiration_reminders.enabled",
        description="Expiration reminder notifications (not implemented yet).",
        enabled=False,
        scope=FeatureFlagScope.GLOBAL,
    ),
)

SETTING_SEEDS: tuple[_SettingSeed, ...] = (
    _SettingSeed(
        key="platform.public_brand_name", value="PassHub", description="Public brand name."
    ),
    _SettingSeed(
        key="platform.default_module",
        value=ModuleCode.DRIVE_PASS.value,
        description="Module the dashboard highlights by default.",
    ),
)


async def seed_platform_data() -> None:
    async with session_scope() as session:
        module_repo = SqlAlchemyPlatformModuleRepository(session)
        for module_seed in MODULE_SEEDS:
            existing = await module_repo.get_by_code(module_seed.code)
            if existing is None:
                await module_repo.add(
                    PlatformModule(
                        id=uuid4(),
                        code=module_seed.code,
                        name=module_seed.name,
                        description=module_seed.description,
                        icon=module_seed.icon,
                        route_path=module_seed.route_path,
                        status=module_seed.status,
                        is_core=module_seed.is_core,
                        sort_order=module_seed.sort_order,
                    )
                )
                logger.info("seeded module %s", module_seed.code)
            else:
                existing.name = module_seed.name
                existing.description = module_seed.description
                existing.icon = module_seed.icon
                existing.route_path = module_seed.route_path
                existing.status = module_seed.status
                existing.is_core = module_seed.is_core
                existing.sort_order = module_seed.sort_order
                await module_repo.save(existing)

        flag_repo = SqlAlchemyFeatureFlagRepository(session)
        for flag_seed in FEATURE_FLAG_SEEDS:
            if await flag_repo.get_by_key(flag_seed.key) is None:
                await flag_repo.add(
                    FeatureFlag(
                        id=uuid4(),
                        key=flag_seed.key,
                        description=flag_seed.description,
                        enabled=flag_seed.enabled,
                        scope=flag_seed.scope,
                        module_code=flag_seed.module_code,
                    )
                )
                logger.info("seeded feature flag %s", flag_seed.key)

        setting_repo = SqlAlchemyPlatformSettingRepository(session)
        for setting_seed in SETTING_SEEDS:
            if await setting_repo.get_by_key(setting_seed.key) is None:
                await setting_repo.add(
                    PlatformSetting(
                        id=uuid4(),
                        key=setting_seed.key,
                        value=setting_seed.value,
                        description=setting_seed.description,
                    )
                )
                logger.info("seeded platform setting %s", setting_seed.key)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_platform_data())
