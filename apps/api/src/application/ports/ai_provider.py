from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class AIExtractionRequest:
    """Provider-agnostic input. Exactly one of `image_base64` / `text` is set
    — image documents are sent as visual input, PDFs with extractable text
    are sent as text. Whichever provider implements `AIProvider` decides how
    to shape its own API call from this."""

    prompt: str
    json_schema: dict[str, Any]
    schema_name: str
    content_type: str
    image_base64: str | None = None
    text: str | None = None


@dataclass(frozen=True, slots=True)
class AIExtractionResult:
    """Provider-agnostic output. `raw_text` is the literal model output
    (stored as-is for audit/debugging); `parsed` is `raw_text` already
    `json.loads`-ed — callers still validate it against their own schema
    before trusting it. Token/cost fields are `None` when a provider can't
    report them, never fabricated."""

    raw_text: str
    parsed: dict[str, Any] | None
    model: str
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    processing_time_ms: int


class AIProvider(Protocol):
    """Port for structured document-data extraction via an LLM. Domain and
    application layers depend only on this contract — `OpenAIProvider` is
    today's only adapter; `GeminiProvider`/`ClaudeProvider`/`LocalProvider`
    are reserved names for future adapters that plug in without any change
    to code that depends on `AIProvider`."""

    async def extract(self, request: AIExtractionRequest) -> AIExtractionResult: ...


class OCRProvider(Protocol):
    """Port reserved for a future OCR fallback (scanned PDFs with no
    extractable text layer). Not implemented in this sprint — no adapter
    exists yet. Declared now so `DocumentExtractionService` has a stable
    seam to call into once one does, instead of a breaking change later."""

    async def extract_text(self, *, content_bytes: bytes, content_type: str) -> str: ...
