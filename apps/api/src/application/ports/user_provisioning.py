from typing import Protocol
from uuid import UUID


class NewUserProvisioner(Protocol):
    """Port a module implements to react to a brand-new user account.

    Identity calls this once, right after persisting a newly registered
    user, without knowing who implements it. Platform is the first (and
    currently only) implementer — it enables the default module set — but
    nothing in Identity's domain or application layer references Platform
    directly. The concrete adapter is wired in at the presentation layer.
    """

    async def on_user_registered(self, *, user_id: UUID) -> None: ...
