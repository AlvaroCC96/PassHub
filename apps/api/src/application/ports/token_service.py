from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class TokenClaims:
    """Decoded JWT payload, already validated for signature and expiry."""

    subject: str
    claims: dict[str, Any]


class TokenService(Protocol):
    """Port for issuing and verifying short-lived bearer tokens (JWTs).

    Reusable across modules — any future module that needs to issue a
    signed, short-lived token depends on this port rather than on `jose`
    or any other concrete JWT library.
    """

    def create_access_token(
        self, *, subject: str, extra_claims: dict[str, Any] | None = None
    ) -> tuple[str, int]:
        """Returns the encoded token and its TTL in seconds."""
        ...

    def decode_access_token(self, token: str) -> TokenClaims: ...
