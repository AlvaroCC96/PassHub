import json
import time
from typing import Any

from openai import AsyncOpenAI

from src.application.ports import AIExtractionRequest, AIExtractionResult
from src.core.config import Settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIProvider:
    """Implements `AIProvider` via the Responses API with Structured Outputs
    (`text.format` = strict JSON schema) — the model physically cannot
    return a shape `DocumentExtractionService` doesn't expect. No call site
    outside this file knows it's talking to OpenAI specifically."""

    def __init__(self, settings: Settings) -> None:
        self._model = settings.ai.model
        self._timeout_seconds = settings.ai.request_timeout_seconds
        self._client = AsyncOpenAI(api_key=settings.ai.openai_api_key)

    async def extract(self, request: AIExtractionRequest) -> AIExtractionResult:
        content: list[dict[str, Any]] = [{"type": "input_text", "text": request.prompt}]
        if request.image_base64 is not None:
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:{request.content_type};base64,{request.image_base64}",
                }
            )
        elif request.text is not None:
            content.append({"type": "input_text", "text": f"Document text:\n{request.text}"})

        started_at = time.monotonic()
        # The SDK's overloads want precise TypedDicts for `input`/`text`; we
        # build them as plain dicts so this file stays free of OpenAI's
        # generated param types leaking into the rest of the call chain.
        response = await self._client.responses.create(  # type: ignore[call-overload]
            model=self._model,
            input=[{"role": "user", "content": content}],
            text={
                "format": {
                    "type": "json_schema",
                    "name": request.schema_name,
                    "schema": request.json_schema,
                    "strict": True,
                }
            },
            timeout=self._timeout_seconds,
        )
        processing_time_ms = int((time.monotonic() - started_at) * 1000)

        raw_text = response.output_text
        try:
            parsed = json.loads(raw_text)
        except (json.JSONDecodeError, TypeError):
            # Structured Outputs is supposed to make this unreachable, but a
            # malformed/truncated response is still a real possibility (e.g.
            # hitting `max_output_tokens`) — never let a parse failure here
            # propagate as an unhandled exception.
            parsed = None

        usage = response.usage
        return AIExtractionResult(
            raw_text=raw_text,
            parsed=parsed if isinstance(parsed, dict) else None,
            model=response.model,
            input_tokens=usage.input_tokens if usage else None,
            output_tokens=usage.output_tokens if usage else None,
            total_tokens=usage.total_tokens if usage else None,
            processing_time_ms=processing_time_ms,
        )
