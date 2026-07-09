import secrets

from fastapi import Request, Response
from src.core.config import Settings
from src.core.exceptions import ForbiddenError

REFRESH_TOKEN_COOKIE = "ph_refresh_token"
CSRF_COOKIE = "ph_csrf_token"
CSRF_HEADER = "x-csrf-token"
OAUTH_STATE_COOKIE = "ph_oauth_state"


def set_session_cookies(
    response: Response, *, settings: Settings, refresh_token_value: str, max_age: int
) -> str:
    """Sets the HttpOnly refresh-token cookie plus a paired, JS-readable CSRF
    cookie. Returns the new CSRF token so callers needing it can use it too."""
    is_secure = settings.environment != "development"
    # In production the frontend and API are on different origins (*.run.app
    # subdomains). SameSite=None (requires Secure) allows cross-origin POST
    # requests (e.g. /auth/refresh from the SPA) to include these cookies.
    # In development both services share localhost so Lax is fine.
    samesite: str = "none" if is_secure else "lax"
    response.set_cookie(
        REFRESH_TOKEN_COOKIE,
        refresh_token_value,
        max_age=max_age,
        httponly=True,
        secure=is_secure,
        samesite=samesite,
        path="/api/v1/auth",
    )
    csrf_token = secrets.token_urlsafe(32)
    response.set_cookie(
        CSRF_COOKIE,
        csrf_token,
        max_age=max_age,
        httponly=False,
        secure=is_secure,
        samesite=samesite,
        # Path scoping for cookie *visibility to JS* is matched against the
        # current document's path, not the path of whatever request the
        # script later makes. The frontend lives at /login, /dashboard,
        # /auth/callback, etc. (none of which are under /api/v1/auth), so a
        # cookie scoped to /api/v1/auth would never show up in
        # `document.cookie` there — only path="/" makes it universally
        # readable by frontend pages while still being sent on every request.
        path="/",
    )
    return csrf_token


def clear_session_cookies(response: Response, *, settings: Settings) -> None:
    response.delete_cookie(REFRESH_TOKEN_COOKIE, path="/api/v1/auth")
    response.delete_cookie(CSRF_COOKIE, path="/")


def set_oauth_state_cookie(response: Response, *, settings: Settings, state: str) -> None:
    response.set_cookie(
        OAUTH_STATE_COOKIE,
        state,
        max_age=600,
        httponly=True,
        secure=settings.environment != "development",
        samesite="lax",
        path="/api/v1/auth",
    )


def pop_oauth_state_cookie(request: Request, response: Response) -> str | None:
    state = request.cookies.get(OAUTH_STATE_COOKIE)
    response.delete_cookie(OAUTH_STATE_COOKIE, path="/api/v1/auth")
    return state


def verify_csrf(request: Request) -> None:
    """Double-submit cookie check for cookie-authenticated, state-changing
    endpoints (`/auth/refresh`, `/auth/logout`). The header must echo the
    value of the non-HttpOnly CSRF cookie — a cross-site form/script cannot
    read that cookie to forge a matching header."""
    cookie_value = request.cookies.get(CSRF_COOKIE)
    header_value = request.headers.get(CSRF_HEADER)
    if not cookie_value or not header_value or cookie_value != header_value:
        raise ForbiddenError("CSRF token missing or invalid", error_code="csrf_validation_failed")
