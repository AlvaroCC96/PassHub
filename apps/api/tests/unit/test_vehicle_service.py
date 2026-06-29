from uuid import UUID, uuid4

import pytest
from src.core.exceptions import ConflictError, NotFoundError, ValidationError
from src.modules.drivepass.vehicles.application.services import VehicleService
from src.modules.drivepass.vehicles.domain.entities import Vehicle
from src.modules.drivepass.vehicles.domain.value_objects import (
    FuelType,
    Transmission,
    VehicleStatus,
)


class FakeVehicleRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, Vehicle] = {}

    async def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        vehicle = self._by_id.get(vehicle_id)
        if vehicle is None or vehicle.status == VehicleStatus.ARCHIVED:
            return None
        return vehicle

    async def get_active_by_user_and_plate(self, *, user_id: UUID, plate: str) -> Vehicle | None:
        return next(
            (
                v
                for v in self._by_id.values()
                if v.user_id == user_id and v.plate == plate and v.status == VehicleStatus.ACTIVE
            ),
            None,
        )

    async def list_for_user(self, user_id: UUID) -> list[Vehicle]:
        return [v for v in self._by_id.values() if v.user_id == user_id]

    async def get_favorite_for_user(self, user_id: UUID) -> Vehicle | None:
        return next((v for v in self._by_id.values() if v.user_id == user_id and v.favorite), None)

    async def add(self, vehicle: Vehicle) -> None:
        self._by_id[vehicle.id] = vehicle

    async def save(self, vehicle: Vehicle) -> None:
        self._by_id[vehicle.id] = vehicle

    async def soft_delete(self, vehicle: Vehicle) -> None:
        self._by_id[vehicle.id] = vehicle


def _service() -> VehicleService:
    return VehicleService(FakeVehicleRepository())


def _create_kwargs(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "plate": "abcd12",
        "brand": "Toyota",
        "model": "Yaris",
        "year": 2022,
        "color": "Red",
        "vin": None,
        "engine_number": None,
        "nickname": None,
        "fuel_type": FuelType.UNKNOWN,
        "transmission": Transmission.UNKNOWN,
    }
    base.update(overrides)
    return base


async def test_create_vehicle_normalizes_plate_and_succeeds() -> None:
    service = _service()
    user_id = uuid4()

    vehicle = await service.create(user_id=user_id, **_create_kwargs())

    assert vehicle.plate == "ABCD12"
    assert vehicle.status == VehicleStatus.ACTIVE


async def test_create_vehicle_rejects_duplicate_active_plate_for_same_user() -> None:
    service = _service()
    user_id = uuid4()
    await service.create(user_id=user_id, **_create_kwargs())

    with pytest.raises(ConflictError):
        await service.create(user_id=user_id, **_create_kwargs(brand="Honda"))


async def test_create_vehicle_allows_same_plate_for_different_users() -> None:
    service = _service()
    await service.create(user_id=uuid4(), **_create_kwargs())

    # Should not raise — plate uniqueness is scoped per user.
    vehicle = await service.create(user_id=uuid4(), **_create_kwargs())
    assert vehicle.plate == "ABCD12"


async def test_create_vehicle_rejects_future_year() -> None:
    service = _service()

    with pytest.raises(ValidationError):
        await service.create(user_id=uuid4(), **_create_kwargs(year=3000))


async def test_update_vehicle_succeeds() -> None:
    service = _service()
    user_id = uuid4()
    vehicle = await service.create(user_id=user_id, **_create_kwargs())

    updated = await service.update(
        user_id=user_id,
        vehicle_id=vehicle.id,
        **_create_kwargs(nickname="Daily driver"),
    )

    assert updated.nickname == "Daily driver"


async def test_update_vehicle_rejects_conflicting_plate() -> None:
    service = _service()
    user_id = uuid4()
    await service.create(user_id=user_id, **_create_kwargs(plate="AAAA11"))
    second = await service.create(user_id=user_id, **_create_kwargs(plate="BBBB22"))

    with pytest.raises(ConflictError):
        await service.update(
            user_id=user_id, vehicle_id=second.id, **_create_kwargs(plate="AAAA11")
        )


async def test_delete_vehicle_archives_and_removes_from_active_list() -> None:
    service = _service()
    user_id = uuid4()
    vehicle = await service.create(user_id=user_id, **_create_kwargs())

    await service.delete(user_id=user_id, vehicle_id=vehicle.id)

    remaining_active = [
        v for v in await service.list_for_user(user_id) if v.status == VehicleStatus.ACTIVE
    ]
    assert remaining_active == []


async def test_delete_then_recreate_with_same_plate_succeeds() -> None:
    service = _service()
    user_id = uuid4()
    vehicle = await service.create(user_id=user_id, **_create_kwargs())
    await service.delete(user_id=user_id, vehicle_id=vehicle.id)

    # Should not raise — the archived vehicle no longer occupies the plate.
    recreated = await service.create(user_id=user_id, **_create_kwargs())
    assert recreated.plate == "ABCD12"


async def test_set_favorite_unsets_previous_favorite() -> None:
    service = _service()
    user_id = uuid4()
    first = await service.create(user_id=user_id, **_create_kwargs(plate="AAAA11"))
    second = await service.create(user_id=user_id, **_create_kwargs(plate="BBBB22"))

    await service.set_favorite(user_id=user_id, vehicle_id=first.id)
    result = await service.set_favorite(user_id=user_id, vehicle_id=second.id)

    assert result.favorite is True
    assert first.favorite is False


async def test_get_favorite_raises_not_found_when_none_set() -> None:
    service = _service()

    with pytest.raises(NotFoundError):
        await service.get_favorite_for_user(uuid4())


async def test_ownership_is_enforced_for_other_users_vehicle() -> None:
    service = _service()
    owner_id = uuid4()
    other_user_id = uuid4()
    vehicle = await service.create(user_id=owner_id, **_create_kwargs())

    with pytest.raises(NotFoundError):
        await service.get_for_user(user_id=other_user_id, vehicle_id=vehicle.id)
