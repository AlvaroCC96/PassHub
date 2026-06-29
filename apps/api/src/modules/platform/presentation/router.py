from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database import get_db_session
from src.modules.identity.presentation.dependencies import CurrentUser
from src.modules.platform.application.services import (
    FeatureFlagService,
    PlatformSettingService,
    UserModuleService,
)
from src.modules.platform.domain.value_objects import ModuleCode
from src.modules.platform.presentation.dependencies import (
    get_feature_flag_service,
    get_platform_setting_service,
    get_user_module_service,
)
from src.modules.platform.presentation.schemas import (
    FeatureFlagResponse,
    PlatformModuleResponse,
    PlatformSettingResponse,
)

router = APIRouter()


@router.get("/modules", response_model=list[PlatformModuleResponse])
async def list_modules(
    current_user: CurrentUser,
    user_module_service: UserModuleService = Depends(get_user_module_service),
) -> list[PlatformModuleResponse]:
    """Every ACTIVE or COMING_SOON module, flagged with whether the caller
    has it enabled. INACTIVE/DEPRECATED modules never appear here."""
    availabilities = await user_module_service.list_modules_with_status_for_user(current_user.id)
    return [PlatformModuleResponse.from_availability(a) for a in availabilities]


@router.get("/modules/enabled", response_model=list[PlatformModuleResponse])
async def list_enabled_modules(
    current_user: CurrentUser,
    user_module_service: UserModuleService = Depends(get_user_module_service),
) -> list[PlatformModuleResponse]:
    availabilities = await user_module_service.list_enabled_for_user(current_user.id)
    return [PlatformModuleResponse.from_availability(a) for a in availabilities]


@router.post("/modules/{module_code}/enable", response_model=PlatformModuleResponse)
async def enable_module(
    module_code: ModuleCode,
    current_user: CurrentUser,
    user_module_service: UserModuleService = Depends(get_user_module_service),
    session: AsyncSession = Depends(get_db_session),
) -> PlatformModuleResponse:
    availability = await user_module_service.enable(user_id=current_user.id, code=module_code)
    await session.commit()
    return PlatformModuleResponse.from_availability(availability)


@router.post("/modules/{module_code}/disable", response_model=PlatformModuleResponse)
async def disable_module(
    module_code: ModuleCode,
    current_user: CurrentUser,
    user_module_service: UserModuleService = Depends(get_user_module_service),
    session: AsyncSession = Depends(get_db_session),
) -> PlatformModuleResponse:
    availability = await user_module_service.disable(user_id=current_user.id, code=module_code)
    await session.commit()
    return PlatformModuleResponse.from_availability(availability)


@router.get("/feature-flags", response_model=list[FeatureFlagResponse])
async def list_feature_flags(
    current_user: CurrentUser,
    feature_flag_service: FeatureFlagService = Depends(get_feature_flag_service),
) -> list[FeatureFlagResponse]:
    flags = await feature_flag_service.list_relevant_for_user(current_user.id)
    return [FeatureFlagResponse.from_domain(f) for f in flags]


@router.get("/settings/public", response_model=list[PlatformSettingResponse])
async def list_public_settings(
    setting_service: PlatformSettingService = Depends(get_platform_setting_service),
) -> list[PlatformSettingResponse]:
    """The one endpoint in this router that does not require authentication."""
    settings = await setting_service.list_public()
    return [PlatformSettingResponse.from_domain(s) for s in settings]
