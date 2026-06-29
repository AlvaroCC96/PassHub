import re
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.core.exceptions import ValidationError
from src.domain.base import Entity
from src.modules.drivepass.vehicles.domain.value_objects import (
    FuelType,
    Transmission,
    VehicleStatus,
)

MIN_YEAR = 1900
_PLATE_STRIP_PATTERN = re.compile(r"[\s-]+")


def normalize_plate(raw_plate: str) -> str:
    """Uppercase, no spaces, no dashes — `ABCD-12` and `abcd 12` are the same plate."""
    return _PLATE_STRIP_PATTERN.sub("", raw_plate).upper()


def _max_year() -> int:
    return datetime.now(UTC).year + 1


class Vehicle(Entity):
    """A vehicle owned by exactly one user. Ownership is enforced by every
    caller checking `user_id`, never by this entity (it has no notion of
    "current user"). Carries fields with no behavior yet (`nfc_uuid`,
    `public_pin_hash`, `public_enabled`, `vehicle_score`) so NFC/public-portal
    sprints don't need a breaking schema change to add them.
    """

    def __init__(
        self,
        *,
        id: UUID,
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
        favorite: bool = False,
        status: VehicleStatus = VehicleStatus.ACTIVE,
        nfc_uuid: UUID | None = None,
        public_pin_hash: str | None = None,
        public_enabled: bool = False,
        vehicle_score: int | None = None,
    ) -> None:
        super().__init__(id)
        self.user_id = user_id
        self.plate = plate
        self.brand = brand
        self.model = model
        self.year = year
        self.color = color
        self.vin = vin
        self.engine_number = engine_number
        self.nickname = nickname
        self.fuel_type = fuel_type
        self.transmission = transmission
        self.favorite = favorite
        self.status = status
        self.nfc_uuid = nfc_uuid
        self.public_pin_hash = public_pin_hash
        self.public_enabled = public_enabled
        self.vehicle_score = vehicle_score

    @staticmethod
    def _validate(*, plate: str, brand: str, model: str, year: int) -> None:
        if not plate:
            raise ValidationError("Plate is required", error_code="plate_required")
        if not brand:
            raise ValidationError("Brand is required", error_code="brand_required")
        if not model:
            raise ValidationError("Model is required", error_code="model_required")
        if year < MIN_YEAR or year > _max_year():
            raise ValidationError(
                f"Year must be between {MIN_YEAR} and {_max_year()}", error_code="invalid_year"
            )

    @classmethod
    def register(
        cls,
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
    ) -> "Vehicle":
        normalized_plate = normalize_plate(plate)
        cls._validate(plate=normalized_plate, brand=brand, model=model, year=year)
        return cls(
            id=uuid4(),
            user_id=user_id,
            plate=normalized_plate,
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

    def update_details(
        self,
        *,
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
    ) -> None:
        normalized_plate = normalize_plate(plate)
        self._validate(plate=normalized_plate, brand=brand, model=model, year=year)
        self.plate = normalized_plate
        self.brand = brand
        self.model = model
        self.year = year
        self.color = color
        self.vin = vin
        self.engine_number = engine_number
        self.nickname = nickname
        self.fuel_type = fuel_type
        self.transmission = transmission

    def mark_as_favorite(self) -> None:
        self.favorite = True

    def unmark_as_favorite(self) -> None:
        self.favorite = False

    def archive(self) -> None:
        """Called as part of soft-deleting the vehicle — frees up its plate
        for reuse (the partial unique index only covers ACTIVE, non-deleted
        rows) and keeps it out of any "active vehicles" listing."""
        self.status = VehicleStatus.ARCHIVED
        self.favorite = False
