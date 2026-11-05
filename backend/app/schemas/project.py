import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import MemberRole, ProjectStatus
from app.schemas.auth import UserResponse


class ProjectCreateRequest(BaseModel):
    """Payload for creating a new project."""

    title: str = Field(..., min_length=3, max_length=255, description="Project title")
    description: str = Field(..., min_length=10, description="Project description and requirements")
    budget_amount: Decimal = Field(..., gt=0, description="Total budget amount")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="3-letter currency code")
    deadline: Optional[date] = Field(default=None, description="Optional target deadline")

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, v: str) -> str:
        return v.upper()


class ProjectUpdateRequest(BaseModel):
    """Payload for updating project details (creator only)."""

    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    budget_amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    deadline: Optional[date] = None

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, v: Optional[str]) -> Optional[str]:
        return v.upper() if v else None


class ProjectStatusUpdateRequest(BaseModel):
    """Payload for changing project status."""

    status: ProjectStatus = Field(..., description="Target status: active, completed, or archived")


class AddMemberRequest(BaseModel):
    """Payload for adding a registered collaborator by email."""

    email: EmailStr = Field(..., description="Email address of the registered collaborator")


class ProjectMemberResponse(BaseModel):
    """Project membership information including basic user profile."""

    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    role: MemberRole
    joined_at: datetime
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(BaseModel):
    """Project representation including creator and members."""

    id: uuid.UUID
    title: str
    description: str
    budget_amount: Decimal
    currency: str
    deadline: Optional[date]
    status: ProjectStatus
    created_by_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    members: List[ProjectMemberResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """List of projects accessible to current user."""

    projects: List[ProjectResponse]
    total: int
