from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from src.application.ports import Hasher


class Argon2Hasher(Hasher):
    """`Hasher` adapter backed by Argon2id. Used to hash refresh-token secrets
    before they are persisted — the plaintext value is never stored."""

    def __init__(self) -> None:
        self._impl = PasswordHasher()

    def hash(self, value: str) -> str:
        return self._impl.hash(value)

    def verify(self, value: str, hashed: str) -> bool:
        try:
            return self._impl.verify(hashed, value)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False
