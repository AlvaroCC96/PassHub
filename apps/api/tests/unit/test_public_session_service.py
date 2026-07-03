"""Unit tests for PublicSessionService (Sprint 4.5 Part 2)."""
import hashlib
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from src.core.exceptions import NotFoundError
from src.modules.public_access.application.services import PublicSessionService
from src.modules.public_access.domain.entities import PublicSession


# ── In-memory fakes ───────────────────────────────────────────────────────────


class FakePublicSessionRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, PublicSession] = {}
        self.revoke_all_calls: list[UUID] = []

    async def get_by_id(self, session_id: UUID) -> PublicSession | None:
        return self._by_id.get(session_id)

    async def get_by_token_hash(self, token_hash: str) -> PublicSession | None:
        return next((s for s in self._by_id.values() if s.session_token_hash == token_hash), None)

    async def add(self, session: PublicSession) -> None:
        self._by_id[session.id] = session

    async def save(self, session: PublicSession) -> None:
        self._by_id[session.id] = session

    async def revoke_all_for_access(self, vehicle_public_access_id: UUID) -> None:
        self.revoke_all_calls.append(vehicle_public_access_id)
        for s in self._by_id.values():
            if s.vehicle_public_access_id == vehicle_public_access_id:
                s.revoke()

    async def expire_stale(self) -> int:
        count = 0
        for s in self._by_id.values():
            if s.expires_at < datetime.now(UTC) and s.revoked_at is None:
                s.revoke()
                count += 1
        return count


def _service() -> tuple[PublicSessionService, FakePublicSessionRepository]:
    repo = FakePublicSessionRepository()
    svc = PublicSessionService(session_repository=repo)
    return svc, repo


def _sha256(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


# ── create ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_returns_session_and_raw_token() -> None:
    svc, repo = _service()
    access_id = uuid4()

    session, raw_token = await svc.create(vehicle_public_access_id=access_id)

    assert session.vehicle_public_access_id == access_id
    assert len(raw_token) > 0
    # Hash stored in DB must match the raw token.
    assert session.session_token_hash == _sha256(raw_token)
    assert repo._by_id[session.id] is session


@pytest.mark.asyncio
async def test_create_raw_token_not_stored_directly() -> None:
    """The plaintext token must never be stored — only the hash."""
    svc, repo = _service()
    session, raw_token = await svc.create(vehicle_public_access_id=uuid4())

    stored = repo._by_id[session.id]
    assert stored.session_token_hash != raw_token


@pytest.mark.asyncio
async def test_create_generates_unique_tokens() -> None:
    svc, _ = _service()
    access_id = uuid4()
    tokens = {(await svc.create(vehicle_public_access_id=access_id))[1] for _ in range(20)}
    assert len(tokens) == 20


# ── validate ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_validate_returns_session_for_valid_token() -> None:
    svc, _ = _service()
    _, raw_token = await svc.create(vehicle_public_access_id=uuid4())

    session = await svc.validate(raw_token=raw_token)

    assert session is not None
    assert session.is_valid()


@pytest.mark.asyncio
async def test_validate_returns_none_for_unknown_token() -> None:
    svc, _ = _service()
    result = await svc.validate(raw_token="not-a-real-token")
    assert result is None


@pytest.mark.asyncio
async def test_validate_returns_none_for_expired_session() -> None:
    svc, repo = _service()
    _, raw_token = await svc.create(vehicle_public_access_id=uuid4())

    # Force-expire the session.
    session = await repo.get_by_token_hash(_sha256(raw_token))
    assert session is not None
    session.expires_at = datetime.now(UTC) - timedelta(seconds=1)

    result = await svc.validate(raw_token=raw_token)
    assert result is None


@pytest.mark.asyncio
async def test_validate_returns_none_for_revoked_session() -> None:
    svc, _ = _service()
    session, raw_token = await svc.create(vehicle_public_access_id=uuid4())
    await svc.revoke(session_id=session.id)

    result = await svc.validate(raw_token=raw_token)
    assert result is None


# ── revoke ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_revoke_marks_session_as_revoked() -> None:
    svc, repo = _service()
    session, _ = await svc.create(vehicle_public_access_id=uuid4())

    await svc.revoke(session_id=session.id)

    saved = repo._by_id[session.id]
    assert saved.revoked_at is not None


@pytest.mark.asyncio
async def test_revoke_raises_for_unknown_session_id() -> None:
    svc, _ = _service()
    with pytest.raises(NotFoundError):
        await svc.revoke(session_id=uuid4())


# ── revoke_all_for_access ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_revoke_all_for_access_revokes_all_matching_sessions() -> None:
    svc, repo = _service()
    access_id = uuid4()
    other_access_id = uuid4()

    s1, _ = await svc.create(vehicle_public_access_id=access_id)
    s2, _ = await svc.create(vehicle_public_access_id=access_id)
    s3, _ = await svc.create(vehicle_public_access_id=other_access_id)

    await svc.revoke_all_for_access(vehicle_public_access_id=access_id)

    assert repo._by_id[s1.id].revoked_at is not None
    assert repo._by_id[s2.id].revoked_at is not None
    assert repo._by_id[s3.id].revoked_at is None  # Different access, untouched.


# ── expire_stale ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_expire_stale_returns_count_of_expired_sessions() -> None:
    svc, repo = _service()
    access_id = uuid4()

    s1, _ = await svc.create(vehicle_public_access_id=access_id)
    s2, _ = await svc.create(vehicle_public_access_id=access_id)
    s3, _ = await svc.create(vehicle_public_access_id=access_id)

    # Manually expire s1 and s2.
    repo._by_id[s1.id].expires_at = datetime.now(UTC) - timedelta(minutes=1)
    repo._by_id[s2.id].expires_at = datetime.now(UTC) - timedelta(minutes=1)

    count = await svc.expire_stale()

    assert count == 2
    assert repo._by_id[s3.id].revoked_at is None  # Still active.
