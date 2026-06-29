from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database import get_db_session
from src.modules.platform.application.ports import (
    FeatureFlagRepository,
    PlatformModuleRepository,
    PlatformSettingRepository,
    UserModuleRepository,
)
from src.modules.platform.application.services import (
    FeatureFlagService,
    PlatformModuleService,
    PlatformSettingService,
    UserModuleService,
)
from src.modules.platform.infrastructure.repositories import (
    SqlAlchemyFeatureFlagRepository,
    SqlAlchemyPlatformModuleRepository,
    SqlAlchemyPlatformSettingRepository,
    SqlAlchemyUserModuleRepository,
)


def get_platform_module_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PlatformModuleRepository:
    return SqlAlchemyPlatformModuleRepository(session)


def get_user_module_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserModuleRepository:
    return SqlAlchemyUserModuleRepository(session)


def get_feature_flag_repository(
    session: AsyncSession = Depends(get_db_session),
) -> FeatureFlagRepository:
    return SqlAlchemyFeatureFlagRepository(session)


def get_platform_setting_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PlatformSettingRepository:
    return SqlAlchemyPlatformSettingRepository(session)


def get_platform_module_service(
    repository: PlatformModuleRepository = Depends(get_platform_module_repository),
) -> PlatformModuleService:
    return PlatformModuleService(repository)


def get_user_module_service(
    user_module_repository: UserModuleRepository = Depends(get_user_module_repository),
    platform_module_repository: PlatformModuleRepository = Depends(get_platform_module_repository),
) -> UserModuleService:
    return UserModuleService(user_module_repository, platform_module_repository)


def get_feature_flag_service(
    flag_repository: FeatureFlagRepository = Depends(get_feature_flag_repository),
    user_module_repository: UserModuleRepository = Depends(get_user_module_repository),
    platform_module_repository: PlatformModuleRepository = Depends(get_platform_module_repository),
) -> FeatureFlagService:
    return FeatureFlagService(flag_repository, user_module_repository, platform_module_repository)


def get_platform_setting_service(
    repository: PlatformSettingRepository = Depends(get_platform_setting_repository),
) -> PlatformSettingService:
    return PlatformSettingService(repository)
