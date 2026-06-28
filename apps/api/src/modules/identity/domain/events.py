from dataclasses import dataclass
from uuid import UUID

from src.domain.events import DomainEvent
from src.modules.identity.domain.value_objects import AuthProvider


@dataclass(frozen=True, kw_only=True)
class UserRegistered(DomainEvent):
    user_id: UUID
    provider: AuthProvider


@dataclass(frozen=True, kw_only=True)
class UserLoggedIn(DomainEvent):
    user_id: UUID
    provider: AuthProvider
