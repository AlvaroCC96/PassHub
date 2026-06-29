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
    #: The endpoint signed URLs are generated against. Inside Docker, the API
    #: talks to MinIO via the service name (`minio:9000`) — but that hostname
    #: is meaningless to a browser, which needs the host-mapped port instead.
    #: Defaults to `endpoint` so single-endpoint setups (and GCS) don't need
    #: to set this at all.
    public_endpoint: str | None = None
    access_key: str = "passhub"
    secret_key: str = "passhub123"
    bucket: str = "passhub-documents"
    secure: bool = False
    #: Pinned explicitly so the MinIO SDK never makes a live "get bucket
    #: region" call before signing a URL — that call would go out over
    #: `endpoint`, which the client generating a *public* presigned URL may
    #: not even be able to reach (e.g. `localhost:9000` from inside a
    #: container). With the region already known, signing is pure local
    #: cryptography, no network round-trip required.
    region: str = "us-east-1"
    gcs_project_id: str | None = None
    gcs_bucket: str | None = None

    @property
    def resolved_public_endpoint(self) -> str:
        return self.public_endpoint or self.endpoint


class SecuritySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SECURITY_")

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_minutes: int = 60 * 24 * 30
    google_oauth_client_id: str | None = None
    google_oauth_client_secret: str | None = None
    google_oauth_redirect_uri: str = "http://localhost:8000/api/v1/auth/callback"


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_")

    #: Which `AIProvider` adapter the container binds. Only "openai" has a
    #: real implementation today — "gemini"/"claude"/"local" are reserved
    #: names for future adapters, not yet implemented.
    provider: Literal["openai", "gemini", "claude", "local"] = "openai"
    model: str = "gpt-4o-mini"
    #: Deliberately not under the `AI_` prefix — `OPENAI_API_KEY` is the
    #: conventional name every OpenAI-adjacent tool (SDKs, CLIs) looks for.
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    #: Hard ceiling so a single extraction can't run away on cost — applies
    #: to the file sent to the provider, independent of the 10MB document
    #: upload limit in `drivepass/documents`.
    max_input_file_size_bytes: int = 15 * 1024 * 1024
    request_timeout_seconds: int = 60


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
    frontend_url: str = "http://localhost:5173"
    log_level: str = "INFO"
    log_json: bool = False

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    ai: AISettings = Field(default_factory=AISettings)


@lru_cache
def get_settings() -> Settings:
    return Settings()
