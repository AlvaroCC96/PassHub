from src.application.ports import AIProvider
from src.core.config import Settings
from src.core.di import Container
from src.infrastructure.ai.openai_provider import OpenAIProvider


def register_intelligence_bindings(container: Container, settings: Settings) -> None:
    """Only `"openai"` has a real adapter today — `register_intelligence_bindings`
    is the one place that would change to swap it for Gemini/Claude/local,
    nothing above `AIProvider` would need to."""
    if settings.ai.provider == "openai":
        container.bind(AIProvider, lambda: OpenAIProvider(settings))  # type: ignore[type-abstract]
        return
    raise NotImplementedError(f"AI provider '{settings.ai.provider}' has no adapter yet")
