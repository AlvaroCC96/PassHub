from src.modules.intelligence.application.cost_estimator import AICostEstimator


def test_estimate_usd_matches_dated_model_snapshot() -> None:
    estimator = AICostEstimator()

    cost = estimator.estimate_usd(
        model="gpt-4o-mini-2024-07-18", input_tokens=1_000_000, output_tokens=1_000_000
    )

    assert cost == 0.75  # 0.15 (input) + 0.60 (output) per 1M tokens


def test_estimate_usd_returns_none_for_unknown_model() -> None:
    estimator = AICostEstimator()

    cost = estimator.estimate_usd(model="some-future-model", input_tokens=100, output_tokens=100)

    assert cost is None


def test_estimate_usd_returns_none_without_token_counts() -> None:
    estimator = AICostEstimator()

    cost = estimator.estimate_usd(model="gpt-4o-mini", input_tokens=None, output_tokens=50)

    assert cost is None
