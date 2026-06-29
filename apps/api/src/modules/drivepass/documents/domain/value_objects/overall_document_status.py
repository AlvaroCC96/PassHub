from enum import StrEnum


class OverallDocumentStatus(StrEnum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    WARNING = "WARNING"
    EXPIRED = "EXPIRED"
