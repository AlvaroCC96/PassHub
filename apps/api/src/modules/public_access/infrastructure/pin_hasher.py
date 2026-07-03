from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError


class PinHasher:
    """Hashes and verifies 4-digit PINs using Argon2id.

    The raw PIN is never stored, never logged, and never returned by any
    endpoint.  `hash_pin` is called once on creation/change; `verify_pin`
    is called on each authentication attempt.

    Argon2id defaults from `argon2-cffi` (time_cost=3, memory_cost=65536,
    parallelism=4) are intentionally kept — they are strong enough for a
    4-digit PIN when combined with the rate-limit + lockout enforced at the
    application layer."""

    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    def hash_pin(self, pin: str) -> str:
        return self._hasher.hash(pin)

    def verify_pin(self, *, pin_hash: str, pin: str) -> bool:
        try:
            return self._hasher.verify(pin_hash, pin)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False
