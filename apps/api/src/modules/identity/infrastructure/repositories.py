from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.identity.domain.entities import RefreshToken, User
from src.modules.identity.domain.value_objects import AuthProvider
from src.modules.identity.infrastructure.models import RefreshTokenModel, UserModel


def _user_to_domain(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        full_name=model.full_name,
        avatar_url=model.avatar_url,
        provider=model.provider,
        provider_subject_id=model.provider_subject_id,
        role=model.role,
        is_active=model.is_active,
        last_login_at=model.last_login_at,
    )


def _refresh_token_to_domain(model: RefreshTokenModel) -> RefreshToken:
    return RefreshToken(
        id=model.id,
        user_id=model.user_id,
        secret_hash=model.secret_hash,
        expires_at=model.expires_at,
        revoked_at=model.revoked_at,
        replaced_by_id=model.replaced_by_id,
    )


class SqlAlchemyUserRepository:
    """`UserRepository` adapter backed by SQLAlchemy. Translates between the
    `users` ORM model and the `User` domain entity in both directions."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return _user_to_domain(model) if model else None

    async def get_by_provider_identity(
        self, *, provider: AuthProvider, provider_subject_id: str
    ) -> User | None:
        stmt = select(UserModel).where(
            UserModel.provider == provider, UserModel.provider_subject_id == provider_subject_id
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return _user_to_domain(model) if model else None

    async def add(self, user: User) -> None:
        self._session.add(
            UserModel(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                avatar_url=user.avatar_url,
                provider=user.provider,
                provider_subject_id=user.provider_subject_id,
                role=user.role,
                is_active=user.is_active,
                last_login_at=user.last_login_at,
            )
        )
        await self._session.flush()

    async def save(self, user: User) -> None:
        model = await self._session.get(UserModel, user.id)
        if model is None:
            raise LookupError(f"User {user.id} does not exist")
        model.email = user.email
        model.full_name = user.full_name
        model.avatar_url = user.avatar_url
        model.role = user.role
        model.is_active = user.is_active
        model.last_login_at = user.last_login_at
        await self._session.flush()


class SqlAlchemyRefreshTokenRepository:
    """`RefreshTokenRepository` adapter backed by SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, token_id: UUID) -> RefreshToken | None:
        model = await self._session.get(RefreshTokenModel, token_id)
        return _refresh_token_to_domain(model) if model else None

    async def add(self, token: RefreshToken) -> None:
        self._session.add(
            RefreshTokenModel(
                id=token.id,
                user_id=token.user_id,
                secret_hash=token.secret_hash,
                expires_at=token.expires_at,
                revoked_at=token.revoked_at,
                replaced_by_id=token.replaced_by_id,
            )
        )
        await self._session.flush()

    async def save(self, token: RefreshToken) -> None:
        model = await self._session.get(RefreshTokenModel, token.id)
        if model is None:
            raise LookupError(f"RefreshToken {token.id} does not exist")
        model.revoked_at = token.revoked_at
        model.replaced_by_id = token.replaced_by_id
        await self._session.flush()
