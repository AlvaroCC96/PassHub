from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.core.exceptions import LockedError, NotFoundError, ValidationError
from src.modules.public_access.application.ports import PublicAccessRepository
from src.modules.public_access.domain.entities import VehiclePublicAccess
from src.modules.public_access.domain.value_objects import PublicAccessStatus
from src.modules.public_access.infrastructure.pin_hasher import PinHasher
from src.modules.public_access.infrastructure.token_generator import PublicTokenGenerator

_DEFAULT_MAX_FAILED_ATTEMPTS = 5
_DEFAULT_LOCKOUT_MINUTES = 15


class PublicAccessService:
    """Manages the lifecycle of a vehicle's public access record.

    One record per vehicle — `setup` acts as an upsert so the client can call
    it both to create and to update the PIN without checking existence first.

    Rate-limiting is enforced inside `verify_pin`:
    - Each wrong PIN increments `failed_attempts`.
    - At `max_failed_attempts` consecutive failures the record is locked for
      `lockout_minutes`; while locked, PIN verification is refused entirely
      (423 LockedError) so the counter can't be brute-forced."""

    def __init__(
        self,
        *,
        access_repository: PublicAccessRepository,
        token_generator: PublicTokenGenerator,
        pin_hasher: PinHasher,
        max_failed_attempts: int = _DEFAULT_MAX_FAILED_ATTEMPTS,
        lockout_minutes: int = _DEFAULT_LOCKOUT_MINUTES,
    ) -> None:
        self._access = access_repository
        self._token_generator = token_generator
        self._pin_hasher = pin_hasher
        self._max_failed_attempts = max_failed_attempts
        self._lockout_minutes = lockout_minutes

    async def setup(self, *, vehicle_id: UUID, pin: str) -> tuple[VehiclePublicAccess, bool]:
        """Upsert: creates the record on first call, updates the PIN on subsequent
        calls.  Returns (access, created) — `created=False` means the PIN was
        updated on an existing record."""
        existing = await self._access.get_by_vehicle_id(vehicle_id)
        if existing is not None and existing.deleted_at is None:
            existing.update_pin_hash(self._pin_hasher.hash_pin(pin))
            await self._access.save(existing)
            return existing, False
        token = self._token_generator.generate()
        pin_hash = self._pin_hasher.hash_pin(pin)
        access = VehiclePublicAccess.create(
            vehicle_id=vehicle_id,
            public_token=token,
            pin_hash=pin_hash,
        )
        await self._access.add(access)
        return access, True

    async def change_pin(self, *, vehicle_id: UUID, old_pin: str, new_pin: str) -> None:
        access = await self._get_active(vehicle_id)
        if not self._pin_hasher.verify_pin(pin_hash=access.pin_hash, pin=old_pin):
            raise ValidationError("Incorrect current PIN", error_code="incorrect_pin")
        access.update_pin_hash(self._pin_hasher.hash_pin(new_pin))
        await self._access.save(access)

    async def verify_pin(self, *, public_token: str, pin: str) -> VehiclePublicAccess:
        """Verifies the PIN for a public token.  Returns the access record on
        success.  The caller is responsible for creating the session."""
        access = await self._access.get_by_public_token(public_token)
        if access is None or access.deleted_at is not None or not access.enabled:
            raise NotFoundError("Public token not found", error_code="not_found")
        if access.status == PublicAccessStatus.LOCKED:
            raise LockedError(
                "Access is temporarily locked due to too many failed attempts",
                error_code="access_locked",
            )
        if not self._pin_hasher.verify_pin(pin_hash=access.pin_hash, pin=pin):
            access.increment_failed_attempts()
            if access.failed_attempts >= self._max_failed_attempts:
                access.lock_until(
                    datetime.now(UTC) + timedelta(minutes=self._lockout_minutes)
                )
                await self._access.save(access)
                raise LockedError(
                    f"Too many failed attempts — access locked for {self._lockout_minutes} minutes",
                    error_code="access_locked",
                )
            await self._access.save(access)
            raise ValidationError("Incorrect PIN", error_code="incorrect_pin")
        access.record_success()
        await self._access.save(access)
        return access

    async def get_access_for_vehicle(self, vehicle_id: UUID) -> VehiclePublicAccess | None:
        return await self._access.get_by_vehicle_id(vehicle_id)

    async def get_by_public_token(self, public_token: str) -> VehiclePublicAccess | None:
        return await self._access.get_by_public_token(public_token)

    async def regenerate_token(self, *, vehicle_id: UUID) -> VehiclePublicAccess:
        access = await self._get_active(vehicle_id)
        access.update_token(self._token_generator.generate())
        await self._access.save(access)
        return access

    async def enable(self, *, vehicle_id: UUID) -> None:
        access = await self._get_active(vehicle_id)
        access.enable()
        await self._access.save(access)

    async def disable(self, *, vehicle_id: UUID) -> None:
        access = await self._get_active(vehicle_id)
        access.disable()
        await self._access.save(access)

    async def increment_failed_attempts(self, *, access_id: UUID) -> None:
        access = await self._get_by_id(access_id)
        access.increment_failed_attempts()
        await self._access.save(access)

    async def lock(self, *, access_id: UUID, until: datetime) -> None:
        access = await self._get_by_id(access_id)
        access.lock_until(until)
        await self._access.save(access)

    async def unlock(self, *, access_id: UUID) -> None:
        access = await self._get_by_id(access_id)
        access.unlock()
        await self._access.save(access)

    async def _get_active(self, vehicle_id: UUID) -> VehiclePublicAccess:
        access = await self._access.get_by_vehicle_id(vehicle_id)
        if access is None or access.deleted_at is not None:
            raise NotFoundError(
                "No public access found for this vehicle",
                error_code="public_access_not_found",
            )
        return access

    async def _get_by_id(self, access_id: UUID) -> VehiclePublicAccess:
        access = await self._access.get_by_id(access_id)
        if access is None or access.deleted_at is not None:
            raise NotFoundError(
                "Public access record not found",
                error_code="public_access_not_found",
            )
        return access
