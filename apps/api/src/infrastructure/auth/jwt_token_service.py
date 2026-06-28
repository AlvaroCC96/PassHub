from typing import Any

from jose import JWTError

from src.application.ports import TokenClaims, TokenService
from src.core.config import Settings
from src.core.exceptions import UnauthorizedError
from src.infrastructure.auth.jwt_handler import create_access_token, decode_token


class JWTTokenService(TokenService):
    """`TokenService` adapter backed by `python-jose`. Translates library-level
    JWT errors into `UnauthorizedError` so callers never depend on `jose`."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create_access_token(
        self, *, subject: str, extra_claims: dict[str, Any] | None = None
    ) -> tuple[str, int]:
        token = create_access_token(self._settings, subject=subject, extra_claims=extra_claims)
        ttl_seconds = self._settings.security.jwt_access_token_expire_minutes * 60
        return token, ttl_seconds

    def decode_access_token(self, token: str) -> TokenClaims:
        try:
            payload = decode_token(self._settings, token)
        except JWTError as exc:
            raise UnauthorizedError(
                "Invalid or expired access token", error_code="invalid_token"
            ) from exc

        subject = payload.pop("sub", None)
        if not subject:
            raise UnauthorizedError("Access token is missing a subject", error_code="invalid_token")

        payload.pop("exp", None)
        return TokenClaims(subject=subject, claims=payload)
