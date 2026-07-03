from datetime import date, timedelta
from uuid import UUID, uuid4

from src.domain.base import Entity
from src.modules.drivepass.documents.domain.value_objects import (
    DocumentStatus,
    DocumentType,
    DocumentVisibility,
)
from src.modules.drivepass.documents.domain.value_objects.document_type import (
    DOCUMENT_TYPE_LABELS,
)

EXPIRING_SOON_WINDOW_DAYS = 30


class VehicleDocument(Entity):
    """One row per (vehicle, document type) — always exists once a vehicle's
    document checklist has been initialized, even before anything was ever
    uploaded (`status=MISSING`). `current_version_id` is a denormalized
    pointer into `DocumentVersion`, not a foreign key — see
    `infrastructure/models.py` for why (avoids a circular FK with
    `document_versions`, which itself points back at this table)."""

    def __init__(
        self,
        *,
        id: UUID,
        vehicle_id: UUID,
        document_type: DocumentType,
        display_name: str,
        status: DocumentStatus,
        visibility: DocumentVisibility,
        is_required: bool,
        issue_date: date | None = None,
        expiration_date: date | None = None,
        current_version_id: UUID | None = None,
    ) -> None:
        super().__init__(id)
        self.vehicle_id = vehicle_id
        self.document_type = document_type
        self.display_name = display_name
        self.status = status
        self.visibility = visibility
        self.is_required = is_required
        self.issue_date = issue_date
        self.expiration_date = expiration_date
        self.current_version_id = current_version_id

    @classmethod
    def create_missing(
        cls, *, vehicle_id: UUID, document_type: DocumentType, is_required: bool
    ) -> "VehicleDocument":
        return cls(
            id=uuid4(),
            vehicle_id=vehicle_id,
            document_type=document_type,
            display_name=DOCUMENT_TYPE_LABELS[document_type],
            status=DocumentStatus.MISSING,
            visibility=DocumentVisibility.PRIVATE,
            is_required=is_required,
        )

    def set_required(self, is_required: bool) -> None:
        self.is_required = is_required

    def set_visibility(self, visibility: DocumentVisibility) -> None:
        self.visibility = visibility

    def update_dates(self, *, issue_date: date | None, expiration_date: date | None) -> None:
        """Corrects `issue_date`/`expiration_date` without touching
        `current_version_id` — used when confirmed AI-extracted metadata
        only refines dates on a document that already has a file."""
        self.issue_date = issue_date
        self.expiration_date = expiration_date

    def attach_version(
        self,
        version_id: UUID,
        *,
        issue_date: date | None,
        expiration_date: date | None,
        visibility: DocumentVisibility | None,
    ) -> None:
        self.current_version_id = version_id
        if issue_date is not None:
            self.issue_date = issue_date
        if expiration_date is not None:
            self.expiration_date = expiration_date
        if visibility is not None:
            self.visibility = visibility

    def recompute_status(self, *, today: date) -> None:
        """Re-derives `status` from `current_version_id`/`expiration_date`.
        Called every time a vehicle's documents are read, not just on
        upload — `EXPIRING_SOON`/`EXPIRED` are purely functions of the
        clock, not of any write event."""
        if self.status in (DocumentStatus.REJECTED, DocumentStatus.NOT_APPLICABLE):
            return  # not derived from version/date state — left to a future moderation flow
        if self.current_version_id is None:
            self.status = DocumentStatus.MISSING
            return
        if self.expiration_date is None:
            self.status = DocumentStatus.UPLOADED
            return
        if self.expiration_date < today:
            self.status = DocumentStatus.EXPIRED
        elif self.expiration_date <= today + timedelta(days=EXPIRING_SOON_WINDOW_DAYS):
            self.status = DocumentStatus.EXPIRING_SOON
        else:
            self.status = DocumentStatus.VALID
