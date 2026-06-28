from dataclasses import dataclass
from typing import BinaryIO, Protocol


@dataclass(frozen=True, slots=True)
class StorageObject:
    """Result of a storage write — never leaks a provider-specific shape."""

    key: str
    bucket: str
    content_type: str
    size_bytes: int


class StorageProvider(Protocol):
    """Port for binary object storage. The domain and application layers depend
    only on this contract. `MinIOStorageProvider` implements it for local/dev;
    a future `GoogleCloudStorageProvider` will implement it for production
    without any change to code that depends on `StorageProvider`.
    """

    async def upload(
        self, *, key: str, data: BinaryIO, content_type: str, bucket: str | None = None
    ) -> StorageObject: ...

    async def download(self, *, key: str, bucket: str | None = None) -> bytes: ...

    async def delete(self, *, key: str, bucket: str | None = None) -> None: ...

    async def get_presigned_url(
        self, *, key: str, bucket: str | None = None, expires_in_seconds: int = 3600
    ) -> str: ...
