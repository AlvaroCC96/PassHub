"""Unit tests for PublicAccessService (Sprint 4.5 Part 2)."""
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from src.core.exceptions import LockedError, NotFoundError, ValidationError
from src.modules.public_access.application.services import PublicAccessService
from src.modules.public_access.domain.entities import VehiclePublicAccess
from src.modules.public_access.domain.value_objects import PublicAccessStatus


# ── In-memory fakes ───────────────────────────────────────────────────────────


class FakePublicAccessRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, VehiclePublicAccess] = {}

    async def get_by_id(self, access_id: UUID) -> VehiclePublicAccess | None:
        return self._by_id.get(access_id)

    async def get_by_vehicle_id(self, vehicle_id: UUID) -> VehiclePublicAccess | None:
        return next((a for a in self._by_id.values() if a.vehicle_id == vehicle_id), None)

    async def get_by_public_token(self, public_token: str) -> VehiclePublicAccess | None:
        return next((a for a in self._by_id.values() if a.public_token == public_token), None)

    async def add(self, access: VehiclePublicAccess) -> None:
        self._by_id[access.id] = access

    async def save(self, access: VehiclePublicAccess) -> None:
        self._by_id[access.id] = access


class FakeTokenGenerator:
    def __init__(self, token: str = "FakeToken0000000000000") -> None:
        self._token = token
        self.call_count = 0

    def generate(self) -> str:
        self.call_count += 1
        return self._token


class FakePinHasher:
    """Trivial hasher — stores pin in clear, prefixed with 'hash:'."""

    def hash_pin(self, pin: str) -> str:
        return f"hash:{pin}"

    def verify_pin(self, *, pin_hash: str, pin: str) -> bool:
        return pin_hash == f"hash:{pin}"


def _service(
    repo: FakePublicAccessRepository | None = None,
    token: str = "TestToken1234567890000",
) -> tuple[PublicAccessService, FakePublicAccessRepository, FakeTokenGenerator]:
    r = repo or FakePublicAccessRepository()
    gen = FakeTokenGenerator(token=token)
    svc = PublicAccessService(access_repository=r, token_generator=gen, pin_hasher=FakePinHasher())
    return svc, r, gen


# ── setup (upsert) ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_setup_creates_new_record() -> None:
    svc, repo, gen = _service()
    vehicle_id = uuid4()

    access, created = await svc.setup(vehicle_id=vehicle_id, pin="1234")

    assert created is True
    assert access.vehicle_id == vehicle_id
    assert access.public_token == gen._token
    assert FakePinHasher().verify_pin(pin_hash=access.pin_hash, pin="1234")
    assert access.enabled is True
    assert await repo.get_by_vehicle_id(vehicle_id) is access


@pytest.mark.asyncio
async def test_setup_updates_pin_on_existing_record() -> None:
    svc, repo, _ = _service()
    vehicle_id = uuid4()

    _, _ = await svc.setup(vehicle_id=vehicle_id, pin="1111")
    access, created = await svc.setup(vehicle_id=vehicle_id, pin="9999")

    assert created is False
    assert FakePinHasher().verify_pin(pin_hash=access.pin_hash, pin="9999")


@pytest.mark.asyncio
async def test_setup_creates_only_one_record_per_vehicle() -> None:
    svc, repo, _ = _service()
    vehicle_id = uuid4()

    await svc.setup(vehicle_id=vehicle_id, pin="0000")
    await svc.setup(vehicle_id=vehicle_id, pin="1111")

    all_records = list(repo._by_id.values())
    assert len(all_records) == 1


# ── enable / disable ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_enable_and_disable() -> None:
    svc, _, _ = _service()
    vehicle_id = uuid4()
    await svc.setup(vehicle_id=vehicle_id, pin="1234")

    await svc.disable(vehicle_id=vehicle_id)
    access = await svc.get_access_for_vehicle(vehicle_id)
    assert access is not None
    assert access.enabled is False

    await svc.enable(vehicle_id=vehicle_id)
    access = await svc.get_access_for_vehicle(vehicle_id)
    assert access is not None
    assert access.enabled is True


@pytest.mark.asyncio
async def test_enable_raises_when_no_access_exists() -> None:
    svc, _, _ = _service()
    with pytest.raises(NotFoundError):
        await svc.enable(vehicle_id=uuid4())


# ── change_pin ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_change_pin_succeeds_with_correct_old_pin() -> None:
    svc, _, _ = _service()
    vehicle_id = uuid4()
    await svc.setup(vehicle_id=vehicle_id, pin="1234")

    await svc.change_pin(vehicle_id=vehicle_id, old_pin="1234", new_pin="5678")

    access = await svc.get_access_for_vehicle(vehicle_id)
    assert access is not None
    assert FakePinHasher().verify_pin(pin_hash=access.pin_hash, pin="5678")


@pytest.mark.asyncio
async def test_change_pin_rejects_wrong_old_pin() -> None:
    svc, _, _ = _service()
    vehicle_id = uuid4()
    await svc.setup(vehicle_id=vehicle_id, pin="1234")

    with pytest.raises(ValidationError, match="Incorrect"):
        await svc.change_pin(vehicle_id=vehicle_id, old_pin="0000", new_pin="5678")


# ── verify_pin ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_verify_pin_success_resets_failed_attempts() -> None:
    svc, repo, _ = _service()
    vehicle_id = uuid4()
    access, _ = await svc.setup(vehicle_id=vehicle_id, pin="1234")
    # Manually bump failed_attempts.
    access.increment_failed_attempts()
    await repo.save(access)

    result = await svc.verify_pin(public_token=access.public_token, pin="1234")

    assert result.failed_attempts == 0
    assert result.locked_until is None


@pytest.mark.asyncio
async def test_verify_pin_wrong_increments_failed_attempts() -> None:
    svc, repo, _ = _service()
    vehicle_id = uuid4()
    access, _ = await svc.setup(vehicle_id=vehicle_id, pin="1234")

    with pytest.raises(ValidationError):
        await svc.verify_pin(public_token=access.public_token, pin="0000")

    saved = await repo.get_by_vehicle_id(vehicle_id)
    assert saved is not None
    assert saved.failed_attempts == 1


@pytest.mark.asyncio
async def test_verify_pin_locks_after_5_failures() -> None:
    svc, repo, _ = _service()
    vehicle_id = uuid4()
    access, _ = await svc.setup(vehicle_id=vehicle_id, pin="1234")

    for _ in range(4):
        with pytest.raises(ValidationError):
            await svc.verify_pin(public_token=access.public_token, pin="0000")

    # 5th failure must raise LockedError and set locked_until.
    with pytest.raises(LockedError):
        await svc.verify_pin(public_token=access.public_token, pin="0000")

    saved = await repo.get_by_vehicle_id(vehicle_id)
    assert saved is not None
    assert saved.status == PublicAccessStatus.LOCKED
    assert saved.locked_until is not None


@pytest.mark.asyncio
async def test_verify_pin_rejects_while_locked() -> None:
    svc, repo, _ = _service()
    vehicle_id = uuid4()
    access, _ = await svc.setup(vehicle_id=vehicle_id, pin="1234")
    # Lock the record manually.
    access.lock_until(datetime.now(UTC) + timedelta(minutes=15))
    await repo.save(access)

    with pytest.raises(LockedError):
        await svc.verify_pin(public_token=access.public_token, pin="1234")


@pytest.mark.asyncio
async def test_verify_pin_not_found_raises_not_found() -> None:
    svc, _, _ = _service()
    with pytest.raises(NotFoundError):
        await svc.verify_pin(public_token="doesnotexist", pin="1234")


@pytest.mark.asyncio
async def test_verify_pin_disabled_access_raises_not_found() -> None:
    svc, _, _ = _service()
    vehicle_id = uuid4()
    access, _ = await svc.setup(vehicle_id=vehicle_id, pin="1234")
    await svc.disable(vehicle_id=vehicle_id)

    with pytest.raises(NotFoundError):
        await svc.verify_pin(public_token=access.public_token, pin="1234")


# ── regenerate_token ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_regenerate_token_changes_public_token() -> None:
    svc, _, gen = _service(token="OriginalToken0000000000")
    vehicle_id = uuid4()
    access, _ = await svc.setup(vehicle_id=vehicle_id, pin="1234")
    original_token = access.public_token

    gen._token = "NewToken00000000000000"
    updated = await svc.regenerate_token(vehicle_id=vehicle_id)

    assert updated.public_token != original_token
    assert updated.public_token == "NewToken00000000000000"


@pytest.mark.asyncio
async def test_regenerate_token_raises_when_no_access() -> None:
    svc, _, _ = _service()
    with pytest.raises(NotFoundError):
        await svc.regenerate_token(vehicle_id=uuid4())
