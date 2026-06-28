from src.core.logging import get_logger
from src.modules.identity.application.ports import RefreshTokenRepository
from src.modules.identity.domain.entities import RefreshToken

logger = get_logger(__name__)


class LogoutUseCase:
    """Revokes a refresh token. Idempotent and silent on an already-invalid
    token — a logout should never fail visibly just because the session was
    already gone."""

    def __init__(self, *, refresh_token_repository: RefreshTokenRepository) -> None:
        self._refresh_token_repository = refresh_token_repository

    async def execute(self, *, token_value: str | None) -> None:
        if not token_value:
            return

        try:
            token_id, _ = RefreshToken.parse_token_value(token_value)
        except Exception:
            return

        record = await self._refresh_token_repository.get_by_id(token_id)
        if record is None or record.revoked_at is not None:
            return

        record.revoke()
        await self._refresh_token_repository.save(record)
        logger.info("logout", category="identity.audit", user_id=str(record.user_id))
