from src.application.ports import Hasher, TokenService
from src.core.config import Settings
from src.core.exceptions import UnauthorizedError
from src.core.logging import get_logger
from src.modules.identity.application.dto import TokenPair
from src.modules.identity.application.ports import RefreshTokenRepository, UserRepository
from src.modules.identity.application.token_issuance import issue_token_pair
from src.modules.identity.domain.entities import RefreshToken

logger = get_logger(__name__)


class RefreshAccessTokenUseCase:
    """Validates a refresh token and rotates it: the presented token is
    revoked and a brand new one is issued, so a stolen-and-reused token is
    immediately detectable (its `replaced_by_id` will already be set)."""

    def __init__(
        self,
        *,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        token_service: TokenService,
        hasher: Hasher,
        settings: Settings,
    ) -> None:
        self._user_repository = user_repository
        self._refresh_token_repository = refresh_token_repository
        self._token_service = token_service
        self._hasher = hasher
        self._settings = settings

    async def execute(self, *, token_value: str) -> TokenPair:
        token_id, secret = RefreshToken.parse_token_value(token_value)

        record = await self._refresh_token_repository.get_by_id(token_id)
        if (
            record is None
            or not record.is_valid
            or not self._hasher.verify(secret, record.secret_hash)
        ):
            logger.warning("refresh_failed", category="identity.audit", token_id=str(token_id))
            raise UnauthorizedError(
                "Invalid or expired refresh token", error_code="invalid_refresh_token"
            )

        user = await self._user_repository.get_by_id(record.user_id)
        if user is None or not user.is_active:
            logger.warning("refresh_failed", category="identity.audit", token_id=str(token_id))
            raise UnauthorizedError(
                "Invalid or expired refresh token", error_code="invalid_refresh_token"
            )

        tokens, new_refresh_token = issue_token_pair(
            user_id=user.id,
            role_claim=user.role.value,
            provider=user.provider,
            token_service=self._token_service,
            hasher=self._hasher,
            settings=self._settings,
        )

        # The new row must exist before the old row's `replaced_by_id` FK can
        # point to it — insert first, then revoke-and-link the old token.
        await self._refresh_token_repository.add(new_refresh_token)
        record.revoke(replaced_by_id=new_refresh_token.id)
        await self._refresh_token_repository.save(record)

        logger.info("token_refreshed", category="identity.audit", user_id=str(user.id))
        return tokens
