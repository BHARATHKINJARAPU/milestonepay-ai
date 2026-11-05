from functools import lru_cache
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate backend root directory reliably
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and backend/.env file."""

    APP_NAME: str = "MilestonePay AI"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = (
        "postgresql+psycopg://milestonepay:milestonepay_dev_password@localhost:5432/milestonepay_dev"
    )
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH) if ENV_PATH.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            # Split comma-separated string if provided in .env
            origins = [item.strip() for item in value.split(",") if item.strip()]
            return origins
        elif isinstance(value, list):
            return value
        return ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()


settings = get_settings()
