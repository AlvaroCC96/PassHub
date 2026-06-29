from dataclasses import dataclass

from src.application.ports import Hasher, NewUserProvisioner, TokenService
from src.core.config import Settings
from src.core.exceptions import UnauthorizedError
from src.core.logging import get_logger
from src.modules.identity.application.dto import TokenPair
from src.modules.identity.application.ports import (
    OAuthProvider,
    RefreshTokenRepository,
    UserRepository,
)
from src.modules.identity.application.token_issuance import issue_token_pair
from src.modules.identity.domain.entities import User
from src.modules.identity.domain.value_objects import AuthProvider

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class LoginWithGoogleResult:
    user: User
    tokens: TokenPair


class LoginWithGoogleUseCase:
    """Exchanges a Google authorization code for a session: creates the user
    on first access, refreshes their profile on every subsequent login, and
    issues a new access/refresh token pair."""

    def __init__(
        self,
        *,
        oauth_provider: OAuthProvider,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        token_service: TokenService,
        hasher: Hasher,
        settings: Settings,
        new_user_provisioner: NewUserProvisioner,
    ) -> None:
        self._oauth_provider = oauth_provider
        self._user_repository = user_repository
        self._refresh_token_repository = refresh_token_repository
        self._token_service = token_service
        self._hasher = hasher
        self._settings = settings
        self._new_user_provisioner = new_user_provisioner

    async def execute(self, *, code: str) -> LoginWithGoogleResult:
        try:
            profile = await self._oauth_provider.exchange_code(code=code)
        except Exception:
            logger.warning(
                "login_failed",
                category="identity.audit",
                provider="google",
                reason="code_exchange_failed",
            )
            raise UnauthorizedError(
                "Could not authenticate with Google", error_code="oauth_exchange_failed"
            ) from None

        user = await self._user_repository.get_by_provider_identity(
            provider=AuthProvider.GOOGLE, provider_subject_id=profile.provider_subject_id
        )
        if user is None:
            user = User.register(
                email=profile.email,
                full_name=profile.full_name,
                avatar_url=profile.avatar_url,
                provider=AuthProvider.GOOGLE,
                provider_subject_id=profile.provider_subject_id,
            )
            await self._user_repository.add(user)
            await self._new_user_provisioner.on_user_registered(user_id=user.id)
            logger.info("user_registered", category="identity.audit", user_id=str(user.id))
        else:
            user.update_profile(full_name=profile.full_name, avatar_url=profile.avatar_url)

        user.record_login()
        await self._user_repository.save(user)

        tokens, refresh_token = issue_token_pair(
            user_id=user.id,
            role_claim=user.role.value,
            provider=user.provider,
            token_service=self._token_service,
            hasher=self._hasher,
            settings=self._settings,
        )
        await self._refresh_token_repository.add(refresh_token)

        logger.info(
            "login_succeeded", category="identity.audit", user_id=str(user.id), provider="google"
        )
        return LoginWithGoogleResult(user=user, tokens=tokens)
