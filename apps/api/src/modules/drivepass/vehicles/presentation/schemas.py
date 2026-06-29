from uuid import UUID

from pydantic import BaseModel, Field
from src.modules.drivepass.vehicles.domain.entities import Vehicle
from src.modules.drivepass.vehicles.domain.value_objects import (
    FuelType,
    Transmission,
    VehicleStatus,
)


class VehicleCreateRequest(BaseModel):
    plate: str = Field(min_length=1, max_length=20)
    brand: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int
    color: str | None = Field(default=None, max_length=50)
    vin: str | None = Field(default=None, max_length=32)
    engine_number: str | None = Field(default=None, max_length=64)
    nickname: str | None = Field(default=None, max_length=100)
    fuel_type: FuelType = FuelType.UNKNOWN
    transmission: Transmission = Transmission.UNKNOWN


class VehicleUpdateRequest(BaseModel):
    plate: str = Field(min_length=1, max_length=20)
    brand: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int
    color: str | None = Field(default=None, max_length=50)
    vin: str | None = Field(default=None, max_length=32)
    engine_number: str | None = Field(default=None, max_length=64)
    nickname: str | None = Field(default=None, max_length=100)
    fuel_type: FuelType = FuelType.UNKNOWN
    transmission: Transmission = Transmission.UNKNOWN


class VehicleResponse(BaseModel):
    id: UUID
    plate: str
    brand: str
    model: str
    year: int
    color: str | None
    vin: str | None
    engine_number: str | None
    nickname: str | None
    fuel_type: FuelType
    transmission: Transmission
    favorite: bool
    status: VehicleStatus

    @classmethod
    def from_domain(cls, vehicle: Vehicle) -> "VehicleResponse":
        return cls(
            id=vehicle.id,
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
        )
