from fastapi import Request, Response

PUBLIC_SESSION_COOKIE = "phs"
_COOKIE_PATH = "/api/v1/public"


def set_public_session_cookie(
    response: Response,
    *,
    raw_token: str,
    max_age: int,
    is_secure: bool,
) -> None:
    """Writes the public-session token as an HttpOnly cookie scoped to the
    public portal endpoints.  Never stored in JS-accessible storage."""
    response.set_cookie(
        PUBLIC_SESSION_COOKIE,
        raw_token,
        max_age=max_age,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        path=_COOKIE_PATH,
    )


def clear_public_session_cookie(response: Response, *, is_secure: bool) -> None:
    response.delete_cookie(PUBLIC_SESSION_COOKIE, path=_COOKIE_PATH, secure=is_secure)


def get_raw_session_token(request: Request) -> str | None:
    return request.cookies.get(PUBLIC_SESSION_COOKIE)
