import secrets

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ports import Hasher, TokenService
from src.core.config import Settings, get_settings
from src.core.exceptions import UnauthorizedError
from src.infrastructure.database import get_db_session
from src.modules.identity.application.ports import (
    OAuthProvider,
    RefreshTokenRepository,
    UserRepository,
)
from src.modules.identity.application.use_cases import (
    LoginWithGoogleUseCase,
    LogoutUseCase,
    RefreshAccessTokenUseCase,
)
from src.modules.identity.presentation.cookies import (
    REFRESH_TOKEN_COOKIE,
    clear_session_cookies,
    pop_oauth_state_cookie,
    set_oauth_state_cookie,
    set_session_cookies,
    verify_csrf,
)
from src.modules.identity.presentation.dependencies import (
    CurrentUser,
    get_hasher,
    get_oauth_provider,
    get_refresh_token_repository,
    get_token_service,
    get_user_repository,
)
from src.modules.identity.presentation.schemas import (
    AccessTokenResponse,
    CurrentUserResponse,
    LoginInitiateResponse,
)
from src.modules.platform.application.services import UserModuleService
from src.modules.platform.infrastructure.user_provisioner import PlatformUserProvisioner
from src.modules.platform.presentation.dependencies import get_user_module_service

router = APIRouter()


@router.post("/login", response_model=LoginInitiateResponse)
async def login(
    response: Response,
    settings: Settings = Depends(get_settings),
    oauth_provider: OAuthProvider = Depends(get_oauth_provider),
) -> LoginInitiateResponse:
    """Kept for backwards compat. Prefer GET /auth/login."""
    state = secrets.token_urlsafe(24)
    set_oauth_state_cookie(response, settings=settings, state=state)
    return LoginInitiateResponse(
        authorization_url=oauth_provider.get_authorization_url(state=state)
    )


@router.get("/login")
async def login_redirect(
    settings: Settings = Depends(get_settings),
    oauth_provider: OAuthProvider = Depends(get_oauth_provider),
) -> RedirectResponse:
    """Browser-navigation path: SPA sets window.location.href to this URL.
    Being a first-party navigation, the browser stores the state cookie on
    the API domain without cross-site third-party cookie restrictions."""
    state = secrets.token_urlsafe(24)
    redirect = RedirectResponse(
        url=oauth_provider.get_authorization_url(state=state),
        status_code=status.HTTP_302_FOUND,
    )
    set_oauth_state_cookie(redirect, settings=settings, state=state)
    return redirect


@router.get("/callback")
async def callback(
    request: Request,
    code: str,
    state: str,
    settings: Settings = Depends(get_settings),
    oauth_provider: OAuthProvider = Depends(get_oauth_provider),
    token_service: TokenService = Depends(get_token_service),
    hasher: Hasher = Depends(get_hasher),
    user_repository: UserRepository = Depends(get_user_repository),
    refresh_token_repository: RefreshTokenRepository = Depends(get_refresh_token_repository),
    user_module_service: UserModuleService = Depends(get_user_module_service),
    session: AsyncSession = Depends(get_db_session),
) -> RedirectResponse:
    """Google redirects the browser here after the user grants consent. This
    is a full page navigation, not an XHR — so the only thing we can hand
    back to the SPA is a redirect. Tokens are never put in the URL: the
    refresh token is set as an HttpOnly cookie, and the frontend's callback
    page bootstraps an access token via `POST /auth/refresh` immediately
    after landing."""
    redirect = RedirectResponse(
        url=f"{settings.frontend_url}/auth/callback", status_code=status.HTTP_302_FOUND
    )

    expected_state = pop_oauth_state_cookie(request, redirect)
    if not expected_state or expected_state != state:
        raise UnauthorizedError("Invalid OAuth state", error_code="invalid_oauth_state")

    use_case = LoginWithGoogleUseCase(
        oauth_provider=oauth_provider,
        user_repository=user_repository,
        refresh_token_repository=refresh_token_repository,
        token_service=token_service,
        hasher=hasher,
        settings=settings,
        # The only seam between Identity and Platform: Identity depends on
        # the `NewUserProvisioner` port, Platform supplies this adapter.
        new_user_provisioner=PlatformUserProvisioner(user_module_service),
    )
    result = await use_case.execute(code=code)
    await session.commit()

    csrf_token = set_session_cookies(
        redirect,
        settings=settings,
        refresh_token_value=result.tokens.refresh_token_value,
        max_age=result.tokens.refresh_token_expires_in,
    )
    # Pass the CSRF token in the URL fragment so the SPA can bootstrap it
    # without having to read cross-origin cookies (which browsers block).
    # Fragments are never sent to the server and are stripped from history
    # by the callback page via history.replaceState().
    redirect.headers["location"] = (
        f"{settings.frontend_url}/auth/callback#csrf={csrf_token}"
    )
    return redirect


@router.post("/refresh", response_model=AccessTokenResponse, dependencies=[Depends(verify_csrf)])
async def refresh(
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
    token_service: TokenService = Depends(get_token_service),
    hasher: Hasher = Depends(get_hasher),
    user_repository: UserRepository = Depends(get_user_repository),
    refresh_token_repository: RefreshTokenRepository = Depends(get_refresh_token_repository),
    session: AsyncSession = Depends(get_db_session),
) -> AccessTokenResponse:
    """Rotates the refresh token (cookie) and mints a new access token. This
    is also how the SPA bootstraps a session after `/auth/callback` and after
    a full page reload, since the access token only ever lives in memory."""
    token_value = request.cookies.get(REFRESH_TOKEN_COOKIE)
    if not token_value:
        raise UnauthorizedError(
            "No refresh token cookie present", error_code="missing_refresh_token"
        )

    use_case = RefreshAccessTokenUseCase(
        user_repository=user_repository,
        refresh_token_repository=refresh_token_repository,
        token_service=token_service,
        hasher=hasher,
        settings=settings,
    )
    tokens = await use_case.execute(token_value=token_value)
    await session.commit()

    csrf_token = set_session_cookies(
        response,
        settings=settings,
        refresh_token_value=tokens.refresh_token_value,
        max_age=tokens.refresh_token_expires_in,
    )
    return AccessTokenResponse(
        access_token=tokens.access_token,
        expires_in=tokens.access_token_expires_in,
        csrf_token=csrf_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_csrf)])
async def logout(
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
    refresh_token_repository: RefreshTokenRepository = Depends(get_refresh_token_repository),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    token_value = request.cookies.get(REFRESH_TOKEN_COOKIE)
    use_case = LogoutUseCase(refresh_token_repository=refresh_token_repository)
    await use_case.execute(token_value=token_value)
    await session.commit()
    clear_session_cookies(response, settings=settings)


@router.get("/me", response_model=CurrentUserResponse)
async def me(current_user: CurrentUser) -> CurrentUserResponse:
    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
        provider=current_user.provider,
        last_login_at=current_user.last_login_at,
    )
