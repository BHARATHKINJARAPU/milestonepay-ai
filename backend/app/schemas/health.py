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
