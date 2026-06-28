from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ports import Hasher, TokenService
from src.core.config import Settings, get_settings
from src.core.di import get_container
from src.core.exceptions import UnauthorizedError
from src.infrastructure.database import get_db_session
from src.modules.identity.application.ports import (
    OAuthProvider,
    RefreshTokenRepository,
    UserRepository,
)
from src.modules.identity.application.use_cases import GetCurrentUserUseCase
from src.modules.identity.domain.entities import User
from src.modules.identity.infrastructure.repositories import (
    SqlAlchemyRefreshTokenRepository,
    SqlAlchemyUserRepository,
)

_bearer_scheme = HTTPBearer(auto_error=False)


def get_token_service() -> TokenService:
    return get_container().resolve(TokenService)  # type: ignore[type-abstract]


def get_hasher() -> Hasher:
    return get_container().resolve(Hasher)  # type: ignore[type-abstract]


def get_oauth_provider() -> OAuthProvider:
    return get_container().resolve(OAuthProvider)  # type: ignore[type-abstract]


def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_refresh_token_repository(
    session: AsyncSession = Depends(get_db_session),
) -> RefreshTokenRepository:
    return SqlAlchemyRefreshTokenRepository(session)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    token_service: TokenService = Depends(get_token_service),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    """The platform-wide "who is calling" dependency. Decodes the bearer JWT,
    loads the user it identifies, and rejects anything that doesn't resolve
    to an active account. Any module's protected endpoint depends on this."""
    if credentials is None:
        raise UnauthorizedError("Missing bearer token", error_code="missing_token")

    claims = token_service.decode_access_token(credentials.credentials)
    try:
        user_id = UUID(claims.subject)
    except ValueError as exc:
        raise UnauthorizedError("Invalid token subject", error_code="invalid_token") from exc

    return await GetCurrentUserUseCase(user_repository=user_repository).execute(user_id=user_id)


CurrentUser = Annotated[User, Depends(get_current_user)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
