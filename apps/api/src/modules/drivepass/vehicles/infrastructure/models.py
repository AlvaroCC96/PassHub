import uuid

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.database import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin
from src.modules.drivepass.vehicles.domain.value_objects import (
    FuelType,
    Transmission,
    VehicleStatus,
)


class VehicleModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "vehicles"
    __table_args__ = (
        # Two active, non-deleted vehicles for the same user can never share
        # a plate — but an archived/deleted one doesn't block reusing it.
        Index(
            "uq_vehicles_active_user_plate",
            "user_id",
            "plate",
            unique=True,
            postgresql_where="status = 'ACTIVE' AND deleted_at IS NULL",
        ),
        Index("ix_vehicles_plate", "plate"),
        Index("ix_vehicles_favorite", "favorite"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    plate: Mapped[str] = mapped_column(String(20))
    brand: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))
    year: Mapped[int] = mapped_column(Integer)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vin: Mapped[str | None] = mapped_column(String(32), nullable=True)
    engine_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fuel_type: Mapped[FuelType] = mapped_column(
        SAEnum(FuelType, name="vehicle_fuel_type"), default=FuelType.UNKNOWN
    )
    transmission: Mapped[Transmission] = mapped_column(
        SAEnum(Transmission, name="vehicle_transmission"), default=Transmission.UNKNOWN
    )
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[VehicleStatus] = mapped_column(
        SAEnum(VehicleStatus, name="vehicle_status"), default=VehicleStatus.ACTIVE, index=True
    )

    # Prepared for future sprints (NFC, public portal) — unused today.
    nfc_uuid: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    public_pin_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    public_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    vehicle_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
