from enum import StrEnum


class Role(StrEnum):
    """Platform-wide RBAC roles. Module-specific permissions will compose on top
    of these in future sprints — no authorization logic is implemented yet."""

    USER = "user"
    ADMIN = "admin"
