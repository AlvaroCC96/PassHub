import re

from src.modules.intelligence.domain.value_objects import (
    EXTRACTABLE_FIELD_NAMES,
    ExtractableDocumentType,
)

_PLATE_STRIP_PATTERN = re.compile(r"[\s-]+")


def normalize_plate(raw_plate: str) -> str:
    """Mirrors `drivepass.vehicles.domain.entities.vehicle.normalize_plate`
    by value (uppercase, no spaces/dashes) — duplicated rather than imported
    so Intelligence's domain stays free of DrivePass imports."""
    return _PLATE_STRIP_PATTERN.sub("", raw_plate).upper()


def plate_matches(extracted_plate: str | None, vehicle_plate: str) -> bool:
    """True only when the AI actually returned a plate and it normalizes to
    the same value as the vehicle's own. A missing/empty extracted plate is
    treated as a mismatch — never apply identity fields on an absence of
    evidence."""
    if not extracted_plate:
        return False
    return normalize_plate(extracted_plate) == normalize_plate(vehicle_plate)


def confidence_band(confidence: float | None) -> str:
    """`"high"` / `"medium"` / `"low"` thresholds the frontend's
    `ConfidenceBadge` mirrors exactly (>=0.90 / >=0.70 / below)."""
    if confidence is None:
        return "low"
    if confidence >= 0.90:
        return "high"
    if confidence >= 0.70:
        return "medium"
    return "low"


def required_extraction_fields(document_type: ExtractableDocumentType) -> tuple[str, ...]:
    return EXTRACTABLE_FIELD_NAMES[document_type]
