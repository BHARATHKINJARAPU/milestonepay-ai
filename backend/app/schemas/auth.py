import re
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.models.enums import AccountType


class UserRegisterRequest(BaseModel):
    """Payload for registering a new user."""

    full_name: str = Field(..., min_length=2, max_length=255, description="Full name of the user")
    email: EmailStr = Field(..., description="Unique email address")
    password: str = Field(..., min_length=8, max_length=128, description="Strong user password")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Confirmation password")
    account_type: AccountType = Field(..., description="Role type: freelancer or client")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one alphabetical letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        return v

    @model_validator(mode="after")
    def verify_passwords_match(self) -> "UserRegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Password and confirmation password do not match.")
        return self


class UserLoginRequest(BaseModel):
    """Payload for authenticating a user."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """User profile response without sensitive hash data."""

    id: uuid.UUID
    full_name: str
    email: str
    account_type: AccountType
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """JWT authentication response payload."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

