import asyncio
from datetime import timedelta
from typing import BinaryIO

import google.auth
import google.auth.transport.requests
from google.cloud import storage as gcs

from src.application.ports import StorageObject
from src.core.config import Settings


class GoogleCloudStorageProvider:
    """`StorageProvider` adapter for Google Cloud Storage.

    On Cloud Run the service account identity is used automatically via
    `google.auth.default()` — no key file needed, provided the service account
    has `roles/storage.objectAdmin` on the bucket and
    `roles/iam.serviceAccountTokenCreator` on itself (required for V4 signed URLs).

    Locally, set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json` to use a
    downloaded service account key, or keep `STORAGE_PROVIDER=minio` for the
    MinIO path (recommended for local dev).
    """

    def __init__(self, settings: Settings) -> None:
        self._bucket_name = settings.storage.gcs_bucket or settings.storage.bucket
        # `google.auth.default()` resolves credentials in this order:
        # 1. GOOGLE_APPLICATION_CREDENTIALS env var (service account JSON key)
        # 2. gcloud CLI default credentials (for local testing with gcloud auth)
        # 3. Compute Engine / Cloud Run metadata server (production)
        self._credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        self._client = gcs.Client(
            credentials=self._credentials,
            project=settings.storage.gcs_project_id or project,
        )

    def _resolve_bucket(self, bucket: str | None) -> str:
        return bucket or self._bucket_name

    async def upload(
        self, *, key: str, data: BinaryIO, content_type: str, bucket: str | None = None
    ) -> StorageObject:
        target_bucket = self._resolve_bucket(bucket)
        payload = data.read()
        blob = self._client.bucket(target_bucket).blob(key)
        await asyncio.to_thread(blob.upload_from_string, payload, content_type=content_type)
        return StorageObject(
            key=key,
            bucket=target_bucket,
            content_type=content_type,
            size_bytes=len(payload),
        )

    async def download(self, *, key: str, bucket: str | None = None) -> bytes:
        blob = self._client.bucket(self._resolve_bucket(bucket)).blob(key)
        return await asyncio.to_thread(blob.download_as_bytes)

    async def delete(self, *, key: str, bucket: str | None = None) -> None:
        blob = self._client.bucket(self._resolve_bucket(bucket)).blob(key)
        await asyncio.to_thread(blob.delete)

    async def get_presigned_url(
        self, *, key: str, bucket: str | None = None, expires_in_seconds: int = 3600
    ) -> str:
        blob = self._client.bucket(self._resolve_bucket(bucket)).blob(key)

        # Refresh credentials so the access token used for signing is current.
        # On Cloud Run this hits the metadata server; locally it uses the key file.
        auth_request = google.auth.transport.requests.Request()
        await asyncio.to_thread(self._credentials.refresh, auth_request)

        # V4 signed URLs require either a service account key (signing happens
        # locally) or a valid access_token + service_account_email pair so GCS
        # can call the IAM signBlob API on our behalf.
        sa_email = getattr(self._credentials, "service_account_email", None)
        access_token = getattr(self._credentials, "token", None)

        return await asyncio.to_thread(
            blob.generate_signed_url,
            expiration=timedelta(seconds=expires_in_seconds),
            version="v4",
            method="GET",
            service_account_email=sa_email,
            access_token=access_token,
        )
