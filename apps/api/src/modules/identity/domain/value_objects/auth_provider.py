from enum import StrEnum


class AuthProvider(StrEnum):
    """Identity provider a `User` authenticated through. Only `GOOGLE` has a
    working login flow in this sprint — the others are declared so the
    `users.provider` column and domain model don't need a breaking change
    when local/Apple/Microsoft sign-in are implemented."""

    GOOGLE = "google"
    LOCAL = "local"
    APPLE = "apple"
    MICROSOFT = "microsoft"
