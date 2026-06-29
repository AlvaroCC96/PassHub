import io
from datetime import timedelta
from typing import BinaryIO

from minio import Minio

from src.application.ports import StorageObject, StorageProvider
from src.core.config import Settings


class MinIOStorageProvider(StorageProvider):
    """`StorageProvider` adapter backed by MinIO — used for local development
    and self-hosted deployments. A future `GoogleCloudStorageProvider` will sit
    next to this file and implement the same port for Cloud Storage; nothing
    outside `infrastructure/storage` needs to change when that happens.
    """

    def __init__(self, settings: Settings) -> None:
        self._default_bucket = settings.storage.bucket
        self._client = Minio(
            settings.storage.endpoint,
            access_key=settings.storage.access_key,
            secret_key=settings.storage.secret_key,
            secure=settings.storage.secure,
            region=settings.storage.region,
        )
        # Presigned URLs are handed to a browser, which can't resolve the
        # internal Docker service name `endpoint` points at — only the
        # host-mapped `public_endpoint`. Same credentials, same bucket,
        # different hostname baked into the signature. `region` is pinned on
        # both clients so signing never tries to reach MinIO over the network
        # to ask for it first — see `StorageSettings.region`.
        self._public_client = Minio(
            settings.storage.resolved_public_endpoint,
            access_key=settings.storage.access_key,
            secret_key=settings.storage.secret_key,
            secure=settings.storage.secure,
            region=settings.storage.region,
        )

    def _ensure_bucket(self, bucket: str) -> None:
        if not self._client.bucket_exists(bucket):
            self._client.make_bucket(bucket)

    async def upload(
        self, *, key: str, data: BinaryIO, content_type: str, bucket: str | None = None
    ) -> StorageObject:
        target_bucket = bucket or self._default_bucket
        self._ensure_bucket(target_bucket)

        payload = data.read()
        self._client.put_object(
            target_bucket, key, io.BytesIO(payload), length=len(payload), content_type=content_type
        )
        return StorageObject(
            key=key, bucket=target_bucket, content_type=content_type, size_bytes=len(payload)
        )

    async def download(self, *, key: str, bucket: str | None = None) -> bytes:
        target_bucket = bucket or self._default_bucket
        response = self._client.get_object(target_bucket, key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    async def delete(self, *, key: str, bucket: str | None = None) -> None:
        self._client.remove_object(bucket or self._default_bucket, key)

    async def get_presigned_url(
        self, *, key: str, bucket: str | None = None, expires_in_seconds: int = 3600
    ) -> str:
        return self._public_client.presigned_get_object(
            bucket or self._default_bucket, key, expires=timedelta(seconds=expires_in_seconds)
        )
