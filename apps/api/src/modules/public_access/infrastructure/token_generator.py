import secrets
import string

_BASE62_ALPHABET = string.ascii_letters + string.digits  # a-z A-Z 0-9  (62 chars)
_TOKEN_LENGTH = 22


class PublicTokenGenerator:
    """Generates URL-safe Base62 tokens for the public vehicle portal.

    22 Base62 characters → ~131 bits of entropy (log2(62^22) ≈ 131), which is
    far above the OWASP recommendation of 128 bits for session identifiers.
    `secrets.choice` uses the OS CSPRNG, so the output is not predictable even
    if an attacker knows the alphabet.

    The token is NOT derived from any vehicle ID or timestamp — it's purely
    random, so enumerating tokens to discover valid vehicles is infeasible."""

    TOKEN_LENGTH: int = _TOKEN_LENGTH

    def generate(self) -> str:
        return "".join(secrets.choice(_BASE62_ALPHABET) for _ in range(_TOKEN_LENGTH))
