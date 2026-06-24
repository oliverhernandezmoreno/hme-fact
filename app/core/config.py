from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl, Field, RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "HME Fact"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    DEBUG: bool = False
    BACKEND_CORS_ORIGINS: list[AnyUrl] = Field(default_factory=list)

    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "hme_fact"
    POSTGRES_USER: str = "hme_fact"
    POSTGRES_PASSWORD: str = "hme_fact"

    REDIS_URL: RedisDsn = "redis://redis:6379/0"

    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    LOG_LEVEL: str = "INFO"

    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "ChangeMe123!"
    FIRST_SUPERUSER_FULL_NAME: str = "Platform Admin"
    SII_BASE_URL: str = "https://api.sii.example.local"
    SII_PROVIDER: str = "simpleapi"
    SIMPLEAPI_BASE_URL: str = "https://api.simpleapi.cl"
    SIMPLEAPI_API_KEY: str = ""
    SIMPLEAPI_TIMEOUT: float = 30.0
    TAX_PROVIDER_MAX_RETRIES: int = 3
    TAX_PROVIDER_BACKOFF_BASE_SECONDS: float = 0.5

    CELERY_BROKER_URL: RedisDsn | str = "redis://redis:6379/2"
    CELERY_RESULT_BACKEND: RedisDsn | str = "redis://redis:6379/2"

    SMTP_HOST: str = "mailhog"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@hmefact.cl"

    FILE_STORAGE_DRIVER: Literal["local"] = "local"
    LOCAL_STORAGE_PATH: str = "/tmp/hme_fact_storage"

    PDF_RENDERER: Literal["reportlab", "xhtml2pdf"] = "xhtml2pdf"
    CERTIFICATE_ENCRYPTION_KEY: str = "replace-this-with-a-32-byte-key!"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return (
            "postgresql+psycopg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
