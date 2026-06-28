from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    host: str = "localhost"
    port: int = 5432
    user: str = "passhub"
    password: str = "passhub"
    db: str = "passhub"

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class StorageSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STORAGE_")

    provider: Literal["minio", "gcs"] = "minio"
    endpoint: str = "localhost:9000"
    access_key: str = "passhub"
    secret_key: str = "passhub123"
    bucket: str = "passhub-documents"
    secure: bool = False
    gcs_project_id: str | None = None
    gcs_bucket: str | None = None


class SecuritySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SECURITY_")

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_minutes: int = 60 * 24 * 7
    google_oauth_client_id: str | None = None
    google_oauth_client_secret: str | None = None


class ObservabilitySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OTEL_")

    enabled: bool = False
    service_name: str = "passhub-api"
    exporter_endpoint: str | None = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "PassHub API"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    log_level: str = "INFO"
    log_json: bool = False

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)


@lru_cache
def get_settings() -> Settings:
    return Settings()
