from urllib.parse import urlencode

import httpx
from src.core.config import Settings
from src.modules.identity.application.dto import OAuthUserProfile

GOOGLE_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleOAuthProvider:
    """`OAuthProvider` adapter for Google's OAuth 2.0 / OpenID Connect flow.
    Apple and Microsoft providers will sit next to this file and implement
    the same port — nothing in `application` or `presentation` depends on
    Google specifically.
    """

    def __init__(self, settings: Settings) -> None:
        self._client_id = settings.security.google_oauth_client_id
        self._client_secret = settings.security.google_oauth_client_secret
        self._redirect_uri = settings.security.google_oauth_redirect_uri

    def get_authorization_url(self, *, state: str) -> str:
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }
        return f"{GOOGLE_AUTHORIZATION_ENDPOINT}?{urlencode(params)}"

    async def exchange_code(self, *, code: str) -> OAuthUserProfile:
        async with httpx.AsyncClient(timeout=10.0) as client:
            token_response = await client.post(
                GOOGLE_TOKEN_ENDPOINT,
                data={
                    "code": code,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "redirect_uri": self._redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            token_response.raise_for_status()
            access_token = token_response.json()["access_token"]

            userinfo_response = await client.get(
                GOOGLE_USERINFO_ENDPOINT, headers={"Authorization": f"Bearer {access_token}"}
            )
            userinfo_response.raise_for_status()
            payload = userinfo_response.json()

        return OAuthUserProfile(
            provider_subject_id=payload["sub"],
            email=payload["email"],
            full_name=payload.get("name"),
            avatar_url=payload.get("picture"),
        )
