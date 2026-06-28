import secrets
from uuid import UUID

from src.application.ports import Hasher, TokenService
from src.core.config import Settings
from src.modules.identity.application.dto import TokenPair
from src.modules.identity.domain.entities import RefreshToken
from src.modules.identity.domain.value_objects import AuthProvider


def issue_token_pair(
    *,
    user_id: UUID,
    role_claim: str,
    provider: AuthProvider,
    token_service: TokenService,
    hasher: Hasher,
    settings: Settings,
) -> tuple[TokenPair, RefreshToken]:
    """Mints an access token (JWT) and a refresh token (opaque secret) for a
    user. Returns the client-facing `TokenPair` alongside the `RefreshToken`
    entity the caller must persist — the plaintext secret is never returned
    inside the entity itself, only inside `TokenPair.refresh_token_value`.
    """
    access_token, access_ttl = token_service.create_access_token(
        subject=str(user_id), extra_claims={"role": role_claim, "provider": provider.value}
    )

    secret = secrets.token_urlsafe(48)
    refresh_ttl_minutes = settings.security.jwt_refresh_token_expire_minutes
    refresh_token = RefreshToken.new(
        user_id=user_id, secret_hash=hasher.hash(secret), ttl_minutes=refresh_ttl_minutes
    )

    token_pair = TokenPair(
        access_token=access_token,
        access_token_expires_in=access_ttl,
        refresh_token_value=refresh_token.to_token_value(secret),
        refresh_token_expires_in=refresh_ttl_minutes * 60,
    )
    return token_pair, refresh_token
