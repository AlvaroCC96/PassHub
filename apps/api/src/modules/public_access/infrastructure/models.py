import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.database import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class VehiclePublicAccessModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "vehicle_public_access"
    __table_args__ = (
        UniqueConstraint("vehicle_id", name="uq_vehicle_public_access_vehicle_id"),
        UniqueConstraint("public_token", name="uq_vehicle_public_access_public_token"),
        Index("ix_vehicle_public_access_vehicle_id", "vehicle_id"),
        Index("ix_vehicle_public_access_public_token", "public_token"),
    )

    # Plain UUID — no FK to `vehicles` so the public_access module stays
    # decoupled from drivepass at the schema level (same pattern as the
    # intelligence module for document_id/vehicle_id columns).
    vehicle_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True))
    public_token: Mapped[str] = mapped_column(String(64))
    pin_hash: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_access_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PublicSessionModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "public_sessions"
    __table_args__ = (
        Index("ix_public_sessions_vehicle_public_access_id", "vehicle_public_access_id"),
        Index("ix_public_sessions_expires_at", "expires_at"),
    )

    # Plain UUID — intentional: no FK constraint so public_sessions stays
    # cross-module-decoupled; application-layer cleanup handles cascade.
    vehicle_public_access_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True))
    session_token_hash: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
