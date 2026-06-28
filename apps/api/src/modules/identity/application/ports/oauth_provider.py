from typing import Protocol

from src.modules.identity.application.dto import OAuthUserProfile


class OAuthProvider(Protocol):
    """Port for exchanging an OAuth authorization code for a normalized user
    profile. `GoogleOAuthProvider` is the only implementation in this sprint;
    Apple/Microsoft providers will implement the same port later."""

    def get_authorization_url(self, *, state: str) -> str: ...

    async def exchange_code(self, *, code: str) -> OAuthUserProfile: ...
