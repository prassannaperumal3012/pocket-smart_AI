from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    app_name: str = "PocketSmart AI"

    environment: str = Field(
        default="development",
        validation_alias="ENVIRONMENT",
    )

    secret_key: str = Field(
        default="change-me-in-production",
        validation_alias="SECRET_KEY",
    )

    session_secret: str = Field(
        default="change-me-session-secret",
        validation_alias="SESSION_SECRET",
    )

    database_url: str = Field(
        default=f"sqlite:///{(BASE_DIR / 'pocketsmart.db').as_posix()}",
        validation_alias="DATABASE_URL",
    )

    gemini_api_key: str | None = Field(
        default=None,
        validation_alias="GEMINI_API_KEY",
    )

    gemini_model: str = Field(
        default="gemini-2.5-flash",
        validation_alias="GEMINI_MODEL",
    )

    jwt_expire_minutes: int = Field(
        default=1440,
        validation_alias="JWT_EXPIRE_MINUTES",
    )

    max_upload_mb: int = Field(
        default=5,
        validation_alias="MAX_UPLOAD_MB",
    )

    cors_origins_raw: str = Field(
        default="http://127.0.0.1:8000,http://localhost:8000",
        validation_alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            item.strip()
            for item in self.cors_origins_raw.split(",")
            if item.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Return the application's cached settings instance."""
    return Settings()


settings: Settings = get_settings()
