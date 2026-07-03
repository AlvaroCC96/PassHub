from datetime import UTC, datetime, timedelta
from uuid import uuid4

from src.modules.public_access.domain.entities import SESSION_DURATION_MINUTES, PublicSession
from src.modules.public_access.domain.value_objects import SessionStatus


def _make_session(**overrides: object) -> PublicSession:
    now = datetime.now(UTC)
    defaults: dict[str, object] = {
        "id": uuid4(),
        "vehicle_public_access_id": uuid4(),
        "session_token_hash": "abc123",
        "expires_at": now + timedelta(minutes=SESSION_DURATION_MINUTES),
        "ip_address": None,
        "user_agent": None,
        "created_at": now,
        "revoked_at": None,
    }
    defaults.update(overrides)
    return PublicSession(**defaults)  # type: ignore[arg-type]


def test_active_session_is_valid() -> None:
    session = _make_session()
    assert session.is_valid() is True
    assert session.status == SessionStatus.ACTIVE


def test_expired_session_is_not_valid() -> None:
    past = datetime.now(UTC) - timedelta(seconds=1)
    session = _make_session(expires_at=past)
    assert session.is_valid() is False
    assert session.status == SessionStatus.EXPIRED


def test_revoked_session_is_not_valid() -> None:
    session = _make_session()
    session.revoke()
    assert session.is_valid() is False
    assert session.status == SessionStatus.REVOKED


def test_revoke_sets_revoked_at() -> None:
    session = _make_session()
    assert session.revoked_at is None
    session.revoke()
    assert session.revoked_at is not None


def test_session_duration_is_10_minutes() -> None:
    assert SESSION_DURATION_MINUTES == 10


def test_create_factory_sets_correct_expiry() -> None:
    before = datetime.now(UTC)
    session = PublicSession.create(
        vehicle_public_access_id=uuid4(),
        session_token_hash="somehash",
    )
    after = datetime.now(UTC)
    expected_min = before + timedelta(minutes=SESSION_DURATION_MINUTES)
    expected_max = after + timedelta(minutes=SESSION_DURATION_MINUTES)
    assert expected_min <= session.expires_at <= expected_max


def test_create_factory_session_is_valid() -> None:
    session = PublicSession.create(
        vehicle_public_access_id=uuid4(),
        session_token_hash="somehash",
    )
    assert session.is_valid() is True


def test_revoked_beats_expired_in_status() -> None:
    """A session that is both past expiry and explicitly revoked reports REVOKED."""
    past = datetime.now(UTC) - timedelta(hours=1)
    session = _make_session(expires_at=past)
    session.revoke()
    assert session.status == SessionStatus.REVOKED
