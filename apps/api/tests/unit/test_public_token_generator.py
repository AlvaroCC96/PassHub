import string

from src.modules.public_access.infrastructure.token_generator import (
    _BASE62_ALPHABET,
    _TOKEN_LENGTH,
    PublicTokenGenerator,
)

_generator = PublicTokenGenerator()


def test_token_has_correct_length() -> None:
    token = _generator.generate()
    assert len(token) == _TOKEN_LENGTH


def test_token_uses_only_base62_characters() -> None:
    token = _generator.generate()
    allowed = set(string.ascii_letters + string.digits)
    assert all(ch in allowed for ch in token)


def test_base62_alphabet_has_62_chars() -> None:
    assert len(_BASE62_ALPHABET) == 62
    assert len(set(_BASE62_ALPHABET)) == 62


def test_tokens_are_unique() -> None:
    tokens = {_generator.generate() for _ in range(1000)}
    assert len(tokens) == 1000, "Expected 1000 unique tokens; got duplicates"


def test_tokens_are_not_guessable_by_prefix() -> None:
    """No two tokens should share an identical first-8-character prefix."""
    prefixes = [_generator.generate()[:8] for _ in range(1000)]
    # Allow some collisions (birthday problem at 62^8 ≈ 2e14) but zero here
    # statistically validates the CSPRNG is not outputting constant values.
    assert len(set(prefixes)) > 990
