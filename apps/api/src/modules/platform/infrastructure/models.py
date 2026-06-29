import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.database import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin
from src.modules.platform.domain.value_objects import (
    FeatureFlagScope,
    ModuleCode,
    ModuleStatus,
    UserModuleStatus,
)

# Defined once and reused across columns — two separate `SAEnum(ModuleCode, ...)`
# instances with the same `name` would make Alembic try to create the
# `module_code` Postgres enum type twice.
_module_code_type = SAEnum(ModuleCode, name="module_code")


class PlatformModuleModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "platform_modules"

    code: Mapped[ModuleCode] = mapped_column(_module_code_type, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    icon: Mapped[str] = mapped_column(String(50))
    route_path: Mapped[str] = mapped_column(String(255))
    status: Mapped[ModuleStatus] = mapped_column(
        SAEnum(ModuleStatus, name="module_status"), index=True
    )
    is_core: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class UserModuleModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_modules"
    __table_args__ = (UniqueConstraint("user_id", "module_id", name="uq_user_modules_user_module"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("platform_modules.id", ondelete="CASCADE")
    )
    status: Mapped[UserModuleStatus] = mapped_column(
        SAEnum(UserModuleStatus, name="user_module_status"), index=True
    )
    enabled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class FeatureFlagModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "feature_flags"

    key: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(500))
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    scope: Mapped[FeatureFlagScope] = mapped_column(
        SAEnum(FeatureFlagScope, name="feature_flag_scope")
    )
    module_code: Mapped[ModuleCode | None] = mapped_column(_module_code_type, nullable=True)


class PlatformSettingModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "platform_settings"

    key: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    value: Mapped[Any] = mapped_column(JSONB)
    description: Mapped[str] = mapped_column(String(500))
