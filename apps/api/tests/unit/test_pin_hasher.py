from src.modules.public_access.infrastructure.pin_hasher import PinHasher

_hasher = PinHasher()


def test_hash_pin_returns_non_empty_string() -> None:
    result = _hasher.hash_pin("1234")
    assert isinstance(result, str)
    assert len(result) > 0


def test_hash_pin_does_not_return_plaintext() -> None:
    result = _hasher.hash_pin("1234")
    assert "1234" not in result


def test_verify_pin_correct() -> None:
    pin = "5678"
    pin_hash = _hasher.hash_pin(pin)
    assert _hasher.verify_pin(pin_hash=pin_hash, pin=pin) is True


def test_verify_pin_incorrect() -> None:
    pin_hash = _hasher.hash_pin("1234")
    assert _hasher.verify_pin(pin_hash=pin_hash, pin="0000") is False


def test_verify_pin_wrong_type_does_not_raise() -> None:
    pin_hash = _hasher.hash_pin("9999")
    assert _hasher.verify_pin(pin_hash=pin_hash, pin="") is False


def test_same_pin_produces_different_hashes() -> None:
    """Argon2 uses a random salt — two hashes of the same PIN must differ."""
    h1 = _hasher.hash_pin("1234")
    h2 = _hasher.hash_pin("1234")
    assert h1 != h2


def test_verify_pin_with_invalid_hash_returns_false() -> None:
    assert _hasher.verify_pin(pin_hash="not-a-valid-hash", pin="1234") is False
