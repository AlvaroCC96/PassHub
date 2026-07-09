import re
from uuid import UUID

from pydantic import BaseModel, field_validator

_PIN_PATTERN = re.compile(r"^\d{4}$")


def _validate_pin(pin: str) -> str:
    if not _PIN_PATTERN.match(pin):
        raise ValueError("PIN must be exactly 4 numeric digits")
    return pin


# ── Private endpoint schemas ─────────────────────────────────────────────────


class SetupPublicAccessRequest(BaseModel):
    pin: str

    @field_validator("pin")
    @classmethod
    def pin_must_be_4_digits(cls, v: str) -> str:
        return _validate_pin(v)


class SetEnabledRequest(BaseModel):
    enabled: bool


class ChangePinRequest(BaseModel):
    old_pin: str
    new_pin: str

    @field_validator("old_pin", "new_pin")
    @classmethod
    def pin_must_be_4_digits(cls, v: str) -> str:
        return _validate_pin(v)


class PublicAccessResponse(BaseModel):
    enabled: bool
    public_token: str
    public_url: str
    failed_attempts: int
    locked: bool
    status: str


class PublicLinkResponse(BaseModel):
    url: str


# ── Public endpoint schemas ───────────────────────────────────────────────────


class VerifyPinRequest(BaseModel):
    pin: str

    @field_validator("pin")
    @classmethod
    def pin_must_be_4_digits(cls, v: str) -> str:
        return _validate_pin(v)


class VerifyPinResponse(BaseModel):
    authenticated: bool
    expires_in: int
    session_token: str  # for mobile/Safari: stored in sessionStorage, sent as X-Public-Session header


class VehiclePublicInfoResponse(BaseModel):
    vehicle: str
    year: int
    requires_pin: bool
    enabled: bool
    locked: bool


class PublicDocumentResponse(BaseModel):
    id: UUID
    type: str
    status: str


class DownloadUrlResponse(BaseModel):
    url: str
