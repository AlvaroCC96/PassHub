from uuid import UUID

from src.core.exceptions import ConflictError, NotFoundError
from src.core.logging import get_logger
from src.modules.drivepass.vehicles.application.ports import VehicleRepository
from src.modules.drivepass.vehicles.domain.entities import Vehicle, normalize_plate
from src.modules.drivepass.vehicles.domain.value_objects import FuelType, Transmission

logger = get_logger(__name__)


class VehicleService:
    """Owns every business rule around a user's vehicle fleet: ownership
    checks, plate-uniqueness among active vehicles, and the single-favorite
    invariant. Nothing above this calls `VehicleRepository` directly."""

    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    async def list_for_user(self, user_id: UUID) -> list[Vehicle]:
        return await self._repository.list_for_user(user_id)

    async def get_for_user(self, *, user_id: UUID, vehicle_id: UUID) -> Vehicle:
        return await self._get_owned(user_id=user_id, vehicle_id=vehicle_id)

    async def get_favorite_for_user(self, user_id: UUID) -> Vehicle:
        vehicle = await self._repository.get_favorite_for_user(user_id)
        if vehicle is None:
            raise NotFoundError("No favorite vehicle set", error_code="favorite_not_set")
        return vehicle

    async def create(
        self,
        *,
        user_id: UUID,
        plate: str,
        brand: str,
        model: str,
        year: int,
        color: str | None = None,
        vin: str | None = None,
        engine_number: str | None = None,
        nickname: str | None = None,
        fuel_type: FuelType = FuelType.UNKNOWN,
        transmission: Transmission = Transmission.UNKNOWN,
    ) -> Vehicle:
        vehicle = Vehicle.register(
            user_id=user_id,
            plate=plate,
            brand=brand,
            model=model,
            year=year,
            color=color,
            vin=vin,
            engine_number=engine_number,
            nickname=nickname,
            fuel_type=fuel_type,
            transmission=transmission,
        )
        await self._ensure_plate_available(user_id=user_id, plate=vehicle.plate)
        await self._repository.add(vehicle)
        logger.info(
            "vehicle_created",
            category="drivepass.audit",
            user_id=str(user_id),
            vehicle_id=str(vehicle.id),
        )
        return vehicle

    async def update(
        self,
        *,
        user_id: UUID,
        vehicle_id: UUID,
        plate: str,
        brand: str,
        model: str,
        year: int,
        color: str | None,
        vin: str | None,
        engine_number: str | None,
        nickname: str | None,
        fuel_type: FuelType,
        transmission: Transmission,
    ) -> Vehicle:
        vehicle = await self._get_owned(user_id=user_id, vehicle_id=vehicle_id)

        normalized_plate = normalize_plate(plate)
        if normalized_plate != vehicle.plate:
            await self._ensure_plate_available(
                user_id=user_id, plate=normalized_plate, exclude_vehicle_id=vehicle.id
            )

        vehicle.update_details(
            plate=plate,
            brand=brand,
            model=model,
            year=year,
            color=color,
            vin=vin,
            engine_number=engine_number,
            nickname=nickname,
            fuel_type=fuel_type,
            transmission=transmission,
        )
        await self._repository.save(vehicle)
        logger.info(
            "vehicle_updated",
            category="drivepass.audit",
            user_id=str(user_id),
            vehicle_id=str(vehicle.id),
        )
        return vehicle

    async def delete(self, *, user_id: UUID, vehicle_id: UUID) -> None:
        vehicle = await self._get_owned(user_id=user_id, vehicle_id=vehicle_id)
        vehicle.archive()
        await self._repository.soft_delete(vehicle)
        logger.info(
            "vehicle_deleted",
            category="drivepass.audit",
            user_id=str(user_id),
            vehicle_id=str(vehicle.id),
        )

    async def set_favorite(self, *, user_id: UUID, vehicle_id: UUID) -> Vehicle:
        vehicle = await self._get_owned(user_id=user_id, vehicle_id=vehicle_id)

        current_favorite = await self._repository.get_favorite_for_user(user_id)
        if current_favorite is not None and current_favorite.id != vehicle.id:
            current_favorite.unmark_as_favorite()
            await self._repository.save(current_favorite)

        if not vehicle.favorite:
            vehicle.mark_as_favorite()
            await self._repository.save(vehicle)

        logger.info(
            "vehicle_favorited",
            category="drivepass.audit",
            user_id=str(user_id),
            vehicle_id=str(vehicle.id),
        )
        return vehicle

    async def _get_owned(self, *, user_id: UUID, vehicle_id: UUID) -> Vehicle:
        vehicle = await self._repository.get_by_id(vehicle_id)
        if vehicle is None or vehicle.user_id != user_id:
            # Same error for "doesn't exist" and "exists but isn't yours" —
            # never reveal that a vehicle belonging to someone else exists.
            raise NotFoundError("Vehicle not found", error_code="vehicle_not_found")
        return vehicle

    async def _ensure_plate_available(
        self, *, user_id: UUID, plate: str, exclude_vehicle_id: UUID | None = None
    ) -> None:
        existing = await self._repository.get_active_by_user_and_plate(user_id=user_id, plate=plate)
        if existing is not None and existing.id != exclude_vehicle_id:
            raise ConflictError(
                f"You already have an active vehicle with plate '{plate}'",
                error_code="plate_already_registered",
            )
