from typing import Protocol


class Hasher(Protocol):
    """Port for one-way hashing of secrets (refresh tokens today, passwords for
    the `LOCAL` auth provider later). Reusable across modules — nothing above
    `infrastructure` should know which algorithm backs it.
    """

    def hash(self, value: str) -> str: ...

    def verify(self, value: str, hashed: str) -> bool: ...
