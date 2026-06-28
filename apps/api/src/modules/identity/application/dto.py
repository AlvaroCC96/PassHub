from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.core.security import Role
from src.modules.identity.domain.value_objects import AuthProvider


@dataclass(frozen=True, slots=True)
class OAuthUserProfile:
    """Normalized profile returned by any `OAuthProvider` adapter, regardless
    of which identity provider it came from."""

    provider_subject_id: str
    email: str
    full_name: str | None
    avatar_url: str | None


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    access_token_expires_in: int
    refresh_token_value: str
    refresh_token_expires_in: int


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    id: UUID
    email: str
    full_name: str | None
    avatar_url: str | None
    role: Role
    provider: AuthProvider
    last_login_at: datetime | None
