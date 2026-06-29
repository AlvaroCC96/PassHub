import pytest
from src.core.exceptions import ForbiddenError
from src.modules.intelligence.presentation.dependencies import require_ai_extraction_enabled


class _FakeFeatureFlagService:
    def __init__(self, *, enabled: bool) -> None:
        self._enabled = enabled

    async def is_enabled(self, key: str) -> bool:
        return self._enabled


async def test_raises_forbidden_when_flag_disabled() -> None:
    with pytest.raises(ForbiddenError):
        await require_ai_extraction_enabled(
            feature_flag_service=_FakeFeatureFlagService(enabled=False)  # type: ignore[arg-type]
        )


async def test_passes_when_flag_enabled() -> None:
    await require_ai_extraction_enabled(
        feature_flag_service=_FakeFeatureFlagService(enabled=True)  # type: ignore[arg-type]
    )
