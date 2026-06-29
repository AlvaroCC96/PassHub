from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelPricing:
    input_per_1m_tokens_usd: float
    output_per_1m_tokens_usd: float


#: Deliberately simple and editable in one place — not fetched from a
#: pricing API. Unknown models (a typo'd `AI_MODEL`, or a future provider
#: with no entry yet) resolve to `None` rather than a guessed number; the
#: spec is explicit that an unknown cost must be stored as `null`, never
#: fabricated.
_KNOWN_PRICING: dict[str, ModelPricing] = {
    "gpt-4o-mini": ModelPricing(input_per_1m_tokens_usd=0.15, output_per_1m_tokens_usd=0.60),
    "gpt-4o": ModelPricing(input_per_1m_tokens_usd=2.50, output_per_1m_tokens_usd=10.00),
    "gpt-4.1-mini": ModelPricing(input_per_1m_tokens_usd=0.40, output_per_1m_tokens_usd=1.60),
    "gpt-4.1": ModelPricing(input_per_1m_tokens_usd=2.00, output_per_1m_tokens_usd=8.00),
}


class AICostEstimator:
    """Token counts come from the provider's own response (never estimated);
    this only turns them into a dollar figure from a static price table."""

    def __init__(self, pricing: dict[str, ModelPricing] | None = None) -> None:
        self._pricing = pricing if pricing is not None else _KNOWN_PRICING

    def estimate_usd(
        self, *, model: str, input_tokens: int | None, output_tokens: int | None
    ) -> float | None:
        if input_tokens is None or output_tokens is None:
            return None
        pricing = self._lookup_pricing(model)
        if pricing is None:
            return None
        cost = (input_tokens / 1_000_000) * pricing.input_per_1m_tokens_usd
        cost += (output_tokens / 1_000_000) * pricing.output_per_1m_tokens_usd
        return round(cost, 6)

    def _lookup_pricing(self, model: str) -> ModelPricing | None:
        if model in self._pricing:
            return self._pricing[model]
        # OpenAI's Responses API echoes back a dated snapshot
        # (e.g. "gpt-4o-mini-2024-07-18") even when the request asked for
        # the bare alias — match the longest known prefix instead of
        # requiring an exact key.
        matches = [key for key in self._pricing if model.startswith(key)]
        if not matches:
            return None
        best = max(matches, key=len)
        return self._pricing[best]
