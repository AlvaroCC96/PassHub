import hashlib
import secrets
from uuid import UUID

from src.core.exceptions import NotFoundError
from src.modules.public_access.application.ports import PublicSessionRepository
from src.modules.public_access.domain.entities import PublicSession
from src.modules.public_access.domain.entities.public_session import SESSION_DURATION_MINUTES


def _hash_token(raw_token: str) -> str:
    """SHA-256 hash of a session token.  Session tokens are long random strings
    (not passwords) so SHA-256 is appropriate — Argon2 is reserved for PINs."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


class PublicSessionService:
    """Manages short-lived anonymous sessions for the public vehicle portal.

    The plaintext session token is generated here and returned to the caller
    exactly once — only the SHA-256 hash is stored.  Sessions expire after
    `session_duration_minutes` and can be explicitly revoked."""

    def __init__(
        self,
        *,
        session_repository: PublicSessionRepository,
        session_duration_minutes: int = SESSION_DURATION_MINUTES,
    ) -> None:
        self._sessions = session_repository
        self._session_duration_minutes = session_duration_minutes

    async def create(
        self,
        *,
        vehicle_public_access_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[PublicSession, str]:
        raw_token = secrets.token_urlsafe(32)
        session = PublicSession.create(
            vehicle_public_access_id=vehicle_public_access_id,
            session_token_hash=_hash_token(raw_token),
            duration_minutes=self._session_duration_minutes,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self._sessions.add(session)
        return session, raw_token

    async def validate(self, *, raw_token: str) -> PublicSession | None:
        session = await self._sessions.get_by_token_hash(_hash_token(raw_token))
        if session is None or not session.is_valid():
            return None
        return session

    async def revoke(self, *, session_id: UUID) -> None:
        session = await self._sessions.get_by_id(session_id)
        if session is None:
            raise NotFoundError("Session not found", error_code="session_not_found")
        session.revoke()
        await self._sessions.save(session)

    async def revoke_all_for_access(self, *, vehicle_public_access_id: UUID) -> None:
        await self._sessions.revoke_all_for_access(vehicle_public_access_id)

    async def expire_stale(self) -> int:
        """Mark all elapsed sessions as revoked.  Returns the count of sessions
        affected.  Intended to be called from a periodic maintenance task."""
        return await self._sessions.expire_stale()
