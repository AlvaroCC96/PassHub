from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.platform.domain.entities import (
    FeatureFlag,
    PlatformModule,
    PlatformSetting,
    UserModule,
)
from src.modules.platform.domain.value_objects import ModuleCode
from src.modules.platform.infrastructure.models import (
    FeatureFlagModel,
    PlatformModuleModel,
    PlatformSettingModel,
    UserModuleModel,
)


def _module_to_domain(model: PlatformModuleModel) -> PlatformModule:
    return PlatformModule(
        id=model.id,
        code=model.code,
        name=model.name,
        description=model.description,
        icon=model.icon,
        route_path=model.route_path,
        status=model.status,
        is_core=model.is_core,
        sort_order=model.sort_order,
    )


def _user_module_to_domain(model: UserModuleModel) -> UserModule:
    return UserModule(
        id=model.id,
        user_id=model.user_id,
        module_id=model.module_id,
        status=model.status,
        enabled_at=model.enabled_at,
        disabled_at=model.disabled_at,
    )


def _flag_to_domain(model: FeatureFlagModel) -> FeatureFlag:
    return FeatureFlag(
        id=model.id,
        key=model.key,
        description=model.description,
        enabled=model.enabled,
        scope=model.scope,
        module_code=model.module_code,
    )


def _setting_to_domain(model: PlatformSettingModel) -> PlatformSetting:
    return PlatformSetting(
        id=model.id, key=model.key, value=model.value, description=model.description
    )


class SqlAlchemyPlatformModuleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, module_id: UUID) -> PlatformModule | None:
        model = await self._session.get(PlatformModuleModel, module_id)
        return _module_to_domain(model) if model and not model.is_deleted else None

    async def get_by_code(self, code: ModuleCode) -> PlatformModule | None:
        stmt = select(PlatformModuleModel).where(
            PlatformModuleModel.code == code, PlatformModuleModel.deleted_at.is_(None)
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return _module_to_domain(model) if model else None

    async def list_all(self) -> list[PlatformModule]:
        stmt = select(PlatformModuleModel).where(PlatformModuleModel.deleted_at.is_(None))
        models = (await self._session.execute(stmt)).scalars().all()
        return [_module_to_domain(m) for m in models]

    async def add(self, module: PlatformModule) -> None:
        self._session.add(
            PlatformModuleModel(
                id=module.id,
                code=module.code,
                name=module.name,
                description=module.description,
                icon=module.icon,
                route_path=module.route_path,
                status=module.status,
                is_core=module.is_core,
                sort_order=module.sort_order,
            )
        )
        await self._session.flush()

    async def save(self, module: PlatformModule) -> None:
        model = await self._session.get(PlatformModuleModel, module.id)
        if model is None:
            raise LookupError(f"PlatformModule {module.id} does not exist")
        model.name = module.name
        model.description = module.description
        model.icon = module.icon
        model.route_path = module.route_path
        model.status = module.status
        model.is_core = module.is_core
        model.sort_order = module.sort_order
        await self._session.flush()


class SqlAlchemyUserModuleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, *, user_id: UUID, module_id: UUID) -> UserModule | None:
        stmt = select(UserModuleModel).where(
            UserModuleModel.user_id == user_id, UserModuleModel.module_id == module_id
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return _user_module_to_domain(model) if model else None

    async def list_for_user(self, user_id: UUID) -> list[UserModule]:
        stmt = select(UserModuleModel).where(UserModuleModel.user_id == user_id)
        models = (await self._session.execute(stmt)).scalars().all()
        return [_user_module_to_domain(m) for m in models]

    async def add(self, user_module: UserModule) -> None:
        self._session.add(
            UserModuleModel(
                id=user_module.id,
                user_id=user_module.user_id,
                module_id=user_module.module_id,
                status=user_module.status,
                enabled_at=user_module.enabled_at,
                disabled_at=user_module.disabled_at,
            )
        )
        await self._session.flush()

    async def save(self, user_module: UserModule) -> None:
        model = await self._session.get(UserModuleModel, user_module.id)
        if model is None:
            raise LookupError(f"UserModule {user_module.id} does not exist")
        model.status = user_module.status
        model.enabled_at = user_module.enabled_at
        model.disabled_at = user_module.disabled_at
        await self._session.flush()


class SqlAlchemyFeatureFlagRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_key(self, key: str) -> FeatureFlag | None:
        stmt = select(FeatureFlagModel).where(FeatureFlagModel.key == key)
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return _flag_to_domain(model) if model else None

    async def list_all(self) -> list[FeatureFlag]:
        models = (await self._session.execute(select(FeatureFlagModel))).scalars().all()
        return [_flag_to_domain(m) for m in models]

    async def add(self, flag: FeatureFlag) -> None:
        self._session.add(
            FeatureFlagModel(
                id=flag.id,
                key=flag.key,
                description=flag.description,
                enabled=flag.enabled,
                scope=flag.scope,
                module_code=flag.module_code,
            )
        )
        await self._session.flush()


class SqlAlchemyPlatformSettingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_key(self, key: str) -> PlatformSetting | None:
        stmt = select(PlatformSettingModel).where(PlatformSettingModel.key == key)
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return _setting_to_domain(model) if model else None

    async def list_all(self) -> list[PlatformSetting]:
        models = (await self._session.execute(select(PlatformSettingModel))).scalars().all()
        return [_setting_to_domain(m) for m in models]

    async def add(self, setting: PlatformSetting) -> None:
        self._session.add(
            PlatformSettingModel(
                id=setting.id, key=setting.key, value=setting.value, description=setting.description
            )
        )
        await self._session.flush()
