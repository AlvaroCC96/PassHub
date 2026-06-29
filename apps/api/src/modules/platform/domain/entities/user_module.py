from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.domain.base import Entity
from src.modules.platform.domain.value_objects import UserModuleStatus


class UserModule(Entity):
    """Tracks whether a specific user has a specific module turned on. One
    row per (user, module) pair — enforced at the persistence layer by a
    unique constraint, not just by convention here."""

    def __init__(
        self,
        *,
        id: UUID,
        user_id: UUID,
        module_id: UUID,
        status: UserModuleStatus,
        enabled_at: datetime,
        disabled_at: datetime | None = None,
    ) -> None:
        super().__init__(id)
        self.user_id = user_id
        self.module_id = module_id
        self.status = status
        self.enabled_at = enabled_at
        self.disabled_at = disabled_at

    @classmethod
    def create_enabled(cls, *, user_id: UUID, module_id: UUID) -> "UserModule":
        return cls(
            id=uuid4(),
            user_id=user_id,
            module_id=module_id,
            status=UserModuleStatus.ENABLED,
            enabled_at=datetime.now(UTC),
        )

    @property
    def is_enabled(self) -> bool:
        return self.status == UserModuleStatus.ENABLED

    def enable(self) -> None:
        self.status = UserModuleStatus.ENABLED
        self.enabled_at = datetime.now(UTC)
        self.disabled_at = None

    def disable(self) -> None:
        self.status = UserModuleStatus.DISABLED
        self.disabled_at = datetime.now(UTC)
