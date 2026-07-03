from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.domain.base import Entity
from src.modules.public_access.domain.value_objects import PublicAccessStatus


class VehiclePublicAccess(Entity):
    """One public-access record per vehicle.  Carries the Base62 token that
    appears in the shareable URL and the Argon2 hash of the owner's PIN.

    The token is never reused: regenerating creates a new token on the same
    row (the old one becomes invalid immediately).  Soft-delete only —
    deleting a vehicle cascades to this record at the application layer, not
    at the DB level, since public_access is a separate module."""

    def __init__(
        self,
        *,
        id: UUID,
        vehicle_id: UUID,
        public_token: str,
        pin_hash: str,
        enabled: bool,
        failed_attempts: int,
        locked_until: datetime | None,
        last_access_at: datetime | None,
        last_success_at: datetime | None,
        created_at: datetime,
        updated_at: datetime,
        deleted_at: datetime | None,
    ) -> None:
        super().__init__(id)
        self.vehicle_id = vehicle_id
        self.public_token = public_token
        self.pin_hash = pin_hash
        self.enabled = enabled
        self.failed_attempts = failed_attempts
        self.locked_until = locked_until
        self.last_access_at = last_access_at
        self.last_success_at = last_success_at
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at

    @classmethod
    def create(
        cls,
        *,
        vehicle_id: UUID,
        public_token: str,
        pin_hash: str,
    ) -> "VehiclePublicAccess":
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            vehicle_id=vehicle_id,
            public_token=public_token,
            pin_hash=pin_hash,
            enabled=True,
            failed_attempts=0,
            locked_until=None,
            last_access_at=None,
            last_success_at=None,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    @property
    def status(self) -> PublicAccessStatus:
        now = datetime.now(UTC)
        if self.locked_until is not None and self.locked_until > now:
            return PublicAccessStatus.LOCKED
        if not self.enabled:
            return PublicAccessStatus.DISABLED
        return PublicAccessStatus.ACTIVE

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    def update_token(self, new_token: str) -> None:
        self.public_token = new_token

    def update_pin_hash(self, new_pin_hash: str) -> None:
        self.pin_hash = new_pin_hash

    def record_access_attempt(self) -> None:
        self.last_access_at = datetime.now(UTC)

    def record_success(self) -> None:
        now = datetime.now(UTC)
        self.last_access_at = now
        self.last_success_at = now
        self.failed_attempts = 0
        self.locked_until = None

    def increment_failed_attempts(self) -> None:
        self.failed_attempts += 1

    def lock_until(self, until: datetime) -> None:
        self.locked_until = until

    def unlock(self) -> None:
        self.locked_until = None
        self.failed_attempts = 0
