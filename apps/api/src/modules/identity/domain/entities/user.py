from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.core.exceptions import ForbiddenError
from src.core.security import Role
from src.domain.base import AggregateRoot
from src.modules.identity.domain.events import UserLoggedIn, UserRegistered
from src.modules.identity.domain.value_objects import AuthProvider


class User(AggregateRoot):
    """A platform account. Identity owns this entity; every other module
    references a user only by `id` — never by importing this class."""

    def __init__(
        self,
        *,
        id: UUID,
        email: str,
        full_name: str | None,
        avatar_url: str | None,
        provider: AuthProvider,
        provider_subject_id: str,
        role: Role = Role.USER,
        is_active: bool = True,
        last_login_at: datetime | None = None,
    ) -> None:
        super().__init__(id)
        self.email = email
        self.full_name = full_name
        self.avatar_url = avatar_url
        self.provider = provider
        self.provider_subject_id = provider_subject_id
        self.role = role
        self.is_active = is_active
        self.last_login_at = last_login_at

    @classmethod
    def register(
        cls,
        *,
        email: str,
        full_name: str | None,
        avatar_url: str | None,
        provider: AuthProvider,
        provider_subject_id: str,
    ) -> "User":
        user = cls(
            id=uuid4(),
            email=email.lower(),
            full_name=full_name,
            avatar_url=avatar_url,
            provider=provider,
            provider_subject_id=provider_subject_id,
        )
        user.record_event(UserRegistered(user_id=user.id, provider=provider))
        return user

    def update_profile(self, *, full_name: str | None, avatar_url: str | None) -> None:
        """Refreshes profile fields from the identity provider. Called on every
        login so the platform never drifts from the user's Google profile."""
        self.full_name = full_name
        self.avatar_url = avatar_url

    def record_login(self) -> None:
        if not self.is_active:
            raise ForbiddenError("Inactive user cannot log in", error_code="user_inactive")
        self.last_login_at = datetime.now(UTC)
        self.record_event(UserLoggedIn(user_id=self.id, provider=self.provider))
