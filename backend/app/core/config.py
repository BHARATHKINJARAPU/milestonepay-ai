from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Union
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
    JWT_SECRET_KEY: str = "milestonepay_dev_jwt_secret_key_849302194820194820194820"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    MAX_EVIDENCE_FILES: int = 5

    # Day 5: Payment Configuration & PayPal Developer Sandbox
    PAYMENT_PROVIDER: str = "mock"
    PAYPAL_MODE: str = "sandbox"
    PAYPAL_ENVIRONMENT: Optional[str] = None
    PAYPAL_API_BASE_URL: str = "https://api-m.sandbox.paypal.com"
    PAYPAL_BASE_URL: Optional[str] = None
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    PAYPAL_WEBHOOK_ID: Optional[str] = None
    PAYPAL_CURRENCY: str = "USD"
    PAYPAL_REQUEST_TIMEOUT_SECONDS: float = 20.0

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH) if ENV_PATH.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("GEMINI_MODEL", mode="before")
    @classmethod
    def normalize_gemini_model(cls, v: Optional[str]) -> str:
        if not v or not v.strip():
            return "gemini-2.5-flash"
        # Normalize "Gemini 2.5 Flash" to "gemini-2.5-flash"
        normalized = v.strip().lower().replace(" ", "-")
        if not normalized.startswith("gemini-"):
            normalized = f"gemini-{normalized}"
        return normalized

    @field_validator("PAYMENT_PROVIDER", mode="before")
    @classmethod
    def validate_payment_provider(cls, v: str, info) -> str:
        provider = v.strip().lower()
        if provider in ("paypal", "paypal_sandbox", "paypal-sandbox"):
            provider = "paypal"
        elif provider not in ("mock", "paypal"):
            raise ValueError(f"Invalid PAYMENT_PROVIDER '{v}'. Allowed options: 'mock', 'paypal'.")
        env = info.data.get("ENVIRONMENT", "development")
        if isinstance(env, str) and env.strip().lower() == "production" and provider == "mock":
            raise ValueError("Mock payment provider is strictly forbidden in production mode.")
        return provider

    @field_validator("PAYPAL_MODE", mode="before")
    @classmethod
    def assemble_paypal_mode(cls, v: Optional[str], info) -> str:
        env_alias = info.data.get("PAYPAL_ENVIRONMENT")
        if env_alias and str(env_alias).strip():
            return str(env_alias).strip().lower()
        if v and v.strip():
            return v.strip().lower()
        return "sandbox"

    @field_validator("PAYPAL_API_BASE_URL", mode="before")
    @classmethod
    def assemble_paypal_base_url(cls, v: Optional[str], info) -> str:
        base_url_alias = info.data.get("PAYPAL_BASE_URL")
        if base_url_alias and str(base_url_alias).strip():
            return str(base_url_alias).strip().rstrip("/")
        if v and v.strip():
            return v.strip().rstrip("/")
        mode = info.data.get("PAYPAL_MODE", "sandbox")
        if isinstance(mode, str) and mode.strip().lower() == "live":
            return "https://api-m.paypal.com"
        return "https://api-m.sandbox.paypal.com"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        default_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://80r0xrhx-5173.inc1.devtunnels.ms",
        ]
        if isinstance(value, str):
            # Split comma-separated string if provided in .env
            origins = [item.strip() for item in value.split(",") if item.strip()]
            for d in default_origins:
                if d not in origins:
                    origins.append(d)
            return origins
        elif isinstance(value, list):
            for d in default_origins:
                if d not in value:
                    value.append(d)
            return value
        return default_origins


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()


settings = get_settings()

