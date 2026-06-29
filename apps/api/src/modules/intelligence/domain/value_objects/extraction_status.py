from enum import StrEnum


class ExtractionStatus(StrEnum):
    """Lifecycle of one `DocumentExtraction`. `PROCESSING` exists for a
    future async pipeline (queues are explicitly out of scope this sprint —
    extraction runs synchronously inside the request, so callers only ever
    observe `PENDING` for an instant before `COMPLETED`/`FAILED`)."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
