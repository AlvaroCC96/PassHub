from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from src.core.exceptions import UnauthorizedError
from src.domain.base import Entity

TOKEN_VALUE_SEPARATOR = "."


class RefreshToken(Entity):
    """A long-lived credential that can be exchanged for a new access token.

    The plaintext secret is never held by this entity past construction — only
    `secret_hash` is persisted. Hashing itself is the application layer's job
    (via the `Hasher` port), keeping this entity free of infrastructure
    dependencies.
    """

    def __init__(
        self,
        *,
        id: UUID,
        user_id: UUID,
        secret_hash: str,
        expires_at: datetime,
        revoked_at: datetime | None = None,
        replaced_by_id: UUID | None = None,
    ) -> None:
        super().__init__(id)
        self.user_id = user_id
        self.secret_hash = secret_hash
        self.expires_at = expires_at
        self.revoked_at = revoked_at
        self.replaced_by_id = replaced_by_id

    @classmethod
    def new(cls, *, user_id: UUID, secret_hash: str, ttl_minutes: int) -> "RefreshToken":
        expires_at = datetime.now(UTC) + timedelta(minutes=ttl_minutes)
        return cls(id=uuid4(), user_id=user_id, secret_hash=secret_hash, expires_at=expires_at)

    @property
    def is_valid(self) -> bool:
        return self.revoked_at is None and self.expires_at > datetime.now(UTC)

    def revoke(self, *, replaced_by_id: UUID | None = None) -> None:
        self.revoked_at = datetime.now(UTC)
        self.replaced_by_id = replaced_by_id

    def to_token_value(self, secret: str) -> str:
        return f"{self.id}{TOKEN_VALUE_SEPARATOR}{secret}"

    @staticmethod
    def parse_token_value(value: str) -> tuple[UUID, str]:
        """Splits the client-facing token into its lookup id and secret."""
        token_id_part, _, secret = value.partition(TOKEN_VALUE_SEPARATOR)
        if not secret:
            raise UnauthorizedError("Malformed refresh token", error_code="invalid_token")
        try:
            return UUID(token_id_part), secret
        except ValueError as exc:
            raise UnauthorizedError("Malformed refresh token", error_code="invalid_token") from exc
