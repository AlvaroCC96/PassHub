from uuid import UUID, uuid4

import pytest
from src.core.exceptions import ConflictError, NotFoundError
from src.modules.platform.application.services import UserModuleService
from src.modules.platform.domain.entities import PlatformModule, UserModule
from src.modules.platform.domain.value_objects import ModuleCode, ModuleStatus


class FakePlatformModuleRepository:
    def __init__(self, modules: list[PlatformModule]) -> None:
        self._by_id = {m.id: m for m in modules}

    async def get_by_id(self, module_id: UUID) -> PlatformModule | None:
        return self._by_id.get(module_id)

    async def get_by_code(self, code: ModuleCode) -> PlatformModule | None:
        return next((m for m in self._by_id.values() if m.code == code), None)

    async def list_all(self) -> list[PlatformModule]:
        return list(self._by_id.values())

    async def add(self, module: PlatformModule) -> None:
        self._by_id[module.id] = module

    async def save(self, module: PlatformModule) -> None:
        self._by_id[module.id] = module


class FakeUserModuleRepository:
    def __init__(self) -> None:
        self._rows: dict[tuple[UUID, UUID], UserModule] = {}

    async def get(self, *, user_id: UUID, module_id: UUID) -> UserModule | None:
        return self._rows.get((user_id, module_id))

    async def list_for_user(self, user_id: UUID) -> list[UserModule]:
        return [row for (uid, _), row in self._rows.items() if uid == user_id]

    async def add(self, user_module: UserModule) -> None:
        self._rows[(user_module.user_id, user_module.module_id)] = user_module

    async def save(self, user_module: UserModule) -> None:
        self._rows[(user_module.user_id, user_module.module_id)] = user_module


def _make_module(
    code: ModuleCode, status: ModuleStatus, *, is_core: bool = False
) -> PlatformModule:
    return PlatformModule(
        id=uuid4(),
        code=code,
        name=code.value,
        description="test module",
        icon="star",
        route_path=f"/app/{code.value.lower()}",
        status=status,
        is_core=is_core,
        sort_order=1,
    )


@pytest.fixture
def active_module() -> PlatformModule:
    return _make_module(ModuleCode.DRIVE_PASS, ModuleStatus.ACTIVE)


@pytest.fixture
def coming_soon_module() -> PlatformModule:
    return _make_module(ModuleCode.HOME_PASS, ModuleStatus.COMING_SOON)


@pytest.fixture
def core_module() -> PlatformModule:
    return _make_module(ModuleCode.FAMILY_PASS, ModuleStatus.ACTIVE, is_core=True)


def _service(*modules: PlatformModule) -> UserModuleService:
    return UserModuleService(
        FakeUserModuleRepository(), FakePlatformModuleRepository(list(modules))
    )


async def test_list_modules_with_status_marks_nothing_enabled_for_new_user(
    active_module: PlatformModule, coming_soon_module: PlatformModule
) -> None:
    service = _service(active_module, coming_soon_module)
    availabilities = await service.list_modules_with_status_for_user(uuid4())

    assert {a.module.code for a in availabilities} == {ModuleCode.DRIVE_PASS, ModuleCode.HOME_PASS}
    assert all(not a.is_enabled for a in availabilities)


async def test_enable_active_module_succeeds(active_module: PlatformModule) -> None:
    service = _service(active_module)
    user_id = uuid4()

    result = await service.enable(user_id=user_id, code=ModuleCode.DRIVE_PASS)

    assert result.is_enabled is True
    enabled = await service.list_enabled_for_user(user_id)
    assert [a.module.code for a in enabled] == [ModuleCode.DRIVE_PASS]


async def test_enable_coming_soon_module_is_rejected(coming_soon_module: PlatformModule) -> None:
    service = _service(coming_soon_module)

    with pytest.raises(ConflictError):
        await service.enable(user_id=uuid4(), code=ModuleCode.HOME_PASS)


async def test_enable_nonexistent_module_raises_not_found() -> None:
    service = _service()

    with pytest.raises(NotFoundError):
        await service.enable(user_id=uuid4(), code=ModuleCode.PET_PASS)


async def test_enabling_twice_does_not_duplicate_user_module(active_module: PlatformModule) -> None:
    service = _service(active_module)
    user_id = uuid4()

    await service.enable(user_id=user_id, code=ModuleCode.DRIVE_PASS)
    await service.enable(user_id=user_id, code=ModuleCode.DRIVE_PASS)

    enabled = await service.list_enabled_for_user(user_id)
    assert len(enabled) == 1


async def test_disable_enabled_module_succeeds(active_module: PlatformModule) -> None:
    service = _service(active_module)
    user_id = uuid4()
    await service.enable(user_id=user_id, code=ModuleCode.DRIVE_PASS)

    result = await service.disable(user_id=user_id, code=ModuleCode.DRIVE_PASS)

    assert result.is_enabled is False
    assert await service.list_enabled_for_user(user_id) == []


async def test_disable_core_module_is_rejected(core_module: PlatformModule) -> None:
    service = _service(core_module)
    user_id = uuid4()
    await service.enable(user_id=user_id, code=ModuleCode.FAMILY_PASS)

    with pytest.raises(ConflictError):
        await service.disable(user_id=user_id, code=ModuleCode.FAMILY_PASS)


async def test_enable_default_modules_for_new_user_enables_drive_pass(
    active_module: PlatformModule,
) -> None:
    service = _service(active_module)
    user_id = uuid4()

    await service.enable_default_modules_for_new_user(user_id)

    enabled = await service.list_enabled_for_user(user_id)
    assert [a.module.code for a in enabled] == [ModuleCode.DRIVE_PASS]
