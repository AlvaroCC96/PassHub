from enum import StrEnum


class DocumentVisibility(StrEnum):
    PRIVATE = "PRIVATE"
    OWNER_ONLY = "OWNER_ONLY"
    #: Wired to nothing yet — the public NFC portal (a future sprint) is what
    #: will actually check a PIN before honoring this value.
    PUBLIC_AFTER_PIN = "PUBLIC_AFTER_PIN"
