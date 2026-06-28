from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from src.core.security import Role
from src.modules.identity.domain.value_objects import AuthProvider


class LoginInitiateResponse(BaseModel):
    authorization_url: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class CurrentUserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str | None
    avatar_url: str | None
    role: Role
    provider: AuthProvider
    last_login_at: datetime | None
