from src.application.ports import Hasher, TokenService
from src.core.config import Settings
from src.core.di import Container
from src.infrastructure.auth import Argon2Hasher, JWTTokenService
from src.modules.identity.application.ports import OAuthProvider
from src.modules.identity.infrastructure.google_oauth_provider import GoogleOAuthProvider


def register_identity_bindings(container: Container, settings: Settings) -> None:
    """Wires the stateless adapters Identity depends on into the composition
    root. Repositories are not bound here — they need a request-scoped
    `AsyncSession` and are constructed directly in `presentation/dependencies.py`.
    """
    # Ports are Protocols — mypy's type-abstract check assumes `type[T]` means
    # "something callable to construct a T", which a bare Protocol isn't. Here
    # it's only ever used as a registry key, never instantiated directly.
    container.bind(TokenService, lambda: JWTTokenService(settings))  # type: ignore[type-abstract]
    container.bind(Hasher, lambda: Argon2Hasher())  # type: ignore[type-abstract]
    container.bind(OAuthProvider, lambda: GoogleOAuthProvider(settings))  # type: ignore[type-abstract]
