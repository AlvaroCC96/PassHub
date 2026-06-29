from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.drivepass.vehicles.domain.entities import Vehicle
from src.modules.drivepass.vehicles.domain.value_objects import VehicleStatus
from src.modules.drivepass.vehicles.infrastructure.models import VehicleModel


def _to_domain(model: VehicleModel) -> Vehicle:
    return Vehicle(
        id=model.id,
        user_id=model.user_id,
        plate=model.plate,
        brand=model.brand,
        model=model.model,
        year=model.year,
        color=model.color,
        vin=model.vin,
        engine_number=model.engine_number,
        nickname=model.nickname,
        fuel_type=model.fuel_type,
        transmission=model.transmission,
        favorite=model.favorite,
        status=model.status,
        nfc_uuid=model.nfc_uuid,
        public_pin_hash=model.public_pin_hash,
        public_enabled=model.public_enabled,
        vehicle_score=model.vehicle_score,
    )


class SqlAlchemyVehicleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        model = await self._session.get(VehicleModel, vehicle_id)
        return _to_domain(model) if model and not model.is_deleted else None

    async def get_active_by_user_and_plate(self, *, user_id: UUID, plate: str) -> Vehicle | None:
        stmt = select(VehicleModel).where(
            VehicleModel.user_id == user_id,
            VehicleModel.plate == plate,
            VehicleModel.status == VehicleStatus.ACTIVE,
            VehicleModel.deleted_at.is_(None),
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return _to_domain(model) if model else None

    async def list_for_user(self, user_id: UUID) -> list[Vehicle]:
        stmt = (
            select(VehicleModel)
            .where(VehicleModel.user_id == user_id, VehicleModel.deleted_at.is_(None))
            .order_by(VehicleModel.created_at.desc())
        )
        models = (await self._session.execute(stmt)).scalars().all()
        return [_to_domain(m) for m in models]

    async def get_favorite_for_user(self, user_id: UUID) -> Vehicle | None:
        stmt = select(VehicleModel).where(
            VehicleModel.user_id == user_id,
            VehicleModel.favorite.is_(True),
            VehicleModel.deleted_at.is_(None),
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return _to_domain(model) if model else None

    async def add(self, vehicle: Vehicle) -> None:
        self._session.add(
            VehicleModel(
                id=vehicle.id,
                user_id=vehicle.user_id,
                plate=vehicle.plate,
                brand=vehicle.brand,
                model=vehicle.model,
                year=vehicle.year,
                color=vehicle.color,
                vin=vehicle.vin,
                engine_number=vehicle.engine_number,
                nickname=vehicle.nickname,
                fuel_type=vehicle.fuel_type,
                transmission=vehicle.transmission,
                favorite=vehicle.favorite,
                status=vehicle.status,
                nfc_uuid=vehicle.nfc_uuid,
                public_pin_hash=vehicle.public_pin_hash,
                public_enabled=vehicle.public_enabled,
                vehicle_score=vehicle.vehicle_score,
            )
        )
        await self._session.flush()

    async def save(self, vehicle: Vehicle) -> None:
        model = await self._session.get(VehicleModel, vehicle.id)
        if model is None:
            raise LookupError(f"Vehicle {vehicle.id} does not exist")
        model.plate = vehicle.plate
        model.brand = vehicle.brand
        model.model = vehicle.model
        model.year = vehicle.year
        model.color = vehicle.color
        model.vin = vehicle.vin
        model.engine_number = vehicle.engine_number
        model.nickname = vehicle.nickname
        model.fuel_type = vehicle.fuel_type
        model.transmission = vehicle.transmission
        model.favorite = vehicle.favorite
        model.status = vehicle.status
        await self._session.flush()

    async def soft_delete(self, vehicle: Vehicle) -> None:
        model = await self._session.get(VehicleModel, vehicle.id)
        if model is None:
            raise LookupError(f"Vehicle {vehicle.id} does not exist")
        model.status = vehicle.status
        model.favorite = vehicle.favorite
        model.deleted_at = datetime.now(UTC)
        await self._session.flush()
