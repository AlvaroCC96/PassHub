"""JWT encode/decode utilities, scaffolded for the upcoming auth module.

No authentication flow is implemented in Sprint 0 — this only fixes the
contract (token claims shape, expiry settings sourced from `SecuritySettings`)
so the auth module can be built directly on top of it.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt

from src.core.config import Settings


def create_access_token(settings: Settings, *, subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.security.jwt_access_token_expire_minutes)
    claims: dict[str, Any] = {"sub": subject, "exp": expire, **(extra_claims or {})}
    return jwt.encode(claims, settings.security.jwt_secret, algorithm=settings.security.jwt_algorithm)


def decode_token(settings: Settings, token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.security.jwt_secret, algorithms=[settings.security.jwt_algorithm])
