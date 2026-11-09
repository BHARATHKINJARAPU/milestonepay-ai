from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema for basic API health status."""
    status: str = Field(default="ok", description="Service operational status")
    service: str = Field(default="milestonepay-api", description="Service identifier")


class ReadyResponse(BaseModel):
    """Schema for API and database readiness status."""
    status: str = Field(default="ready", description="Readiness status")
    service: str = Field(default="milestonepay-api", description="Service identifier")
    database: str = Field(default="connected", description="Database connection status")


class ErrorResponse(BaseModel):
    """Safe error response schema."""
    detail: str = Field(description="Safe error description")


class GeminiDiagnosticInfo(BaseModel):
    """Safe diagnostics summary for Google Gemini AI integration."""
    configured: bool
    model: str
    status: str
    key_masked: str = "Configured (Safe)"


class PayPalDiagnosticInfo(BaseModel):
    """Safe diagnostics summary for PayPal REST API integration."""
    provider: str
    mode: str
    base_url: str
    client_id_configured: bool
    client_secret_configured: bool
    oauth_authenticated: bool
    currency: str
    status: str


class DatabaseDiagnosticInfo(BaseModel):
    """Safe diagnostics summary for PostgreSQL database."""
    status: str
    engine: str = "PostgreSQL"


class WebhookDiagnosticInfo(BaseModel):
    """Safe diagnostics summary for payment webhooks."""
    configured: bool
    status: str
    endpoint: str = "/api/v1/webhooks/paypal"
    note: str


class IntegrationsDiagnosticResponse(BaseModel):
    """Unified system integration status report (no credentials exposed)."""
    service: str = "milestonepay-api"
    environment: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    database: DatabaseDiagnosticInfo
    gemini: GeminiDiagnosticInfo
    paypal: PayPalDiagnosticInfo
    webhook: WebhookDiagnosticInfo
