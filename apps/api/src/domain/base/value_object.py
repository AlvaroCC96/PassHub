from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValueObject:
    """Marker base for immutable value objects, compared by value via dataclass equality."""
