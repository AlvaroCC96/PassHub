from src.application.ports import StorageProvider
from src.core.config import Settings
from src.core.di import Container
from src.infrastructure.storage import GoogleCloudStorageProvider, MinIOStorageProvider


def register_document_bindings(container: Container, settings: Settings) -> None:
    """Binds `StorageProvider` to the configured backend.

    STORAGE_PROVIDER=minio  → MinIOStorageProvider  (local / self-hosted)
    STORAGE_PROVIDER=gcs    → GoogleCloudStorageProvider (Cloud Run / GCP)
    """
    if settings.storage.provider == "gcs":
        container.bind(StorageProvider, lambda: GoogleCloudStorageProvider(settings))  # type: ignore[type-abstract]
    else:
        container.bind(StorageProvider, lambda: MinIOStorageProvider(settings))  # type: ignore[type-abstract]
