from dataclasses import dataclass

from src.domain.base import ValueObject


@dataclass(frozen=True, slots=True)
class Permission(ValueObject):
    """Placeholder for fine-grained authorization, layered on top of `Role`.

    Not enforced anywhere yet — no endpoint checks a `Permission`, and no
    table persists one. It exists so a future RBAC sprint can introduce
    `RolePermission` associations without redesigning `User`.
    """

    code: str
