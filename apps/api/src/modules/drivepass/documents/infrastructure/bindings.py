from src.application.ports import StorageProvider
from src.core.config import Settings
from src.core.di import Container
from src.infrastructure.storage import MinIOStorageProvider


def register_document_bindings(container: Container, settings: Settings) -> None:
    """First real binding of `StorageProvider` — it existed since Sprint 0
    but nothing used it until Documents. Swapping MinIO for
    `GoogleCloudStorageProvider` in production is a one-line change here,
    not a change to anything in `application` or `presentation`."""
    container.bind(StorageProvider, lambda: MinIOStorageProvider(settings))  # type: ignore[type-abstract]
