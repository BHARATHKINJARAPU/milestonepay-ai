from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class ProjectActivityResponse(BaseModel):
    """Schema for a project activity timeline event."""

    id: uuid.UUID
    project_id: uuid.UUID
    actor_user_id: Optional[uuid.UUID] = None
    actor_name: Optional[str] = None
    activity_type: str
    title: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="activity_metadata")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProjectActivityListResponse(BaseModel):
    """Paginated collection of project activity events."""

    activities: List[ProjectActivityResponse]
    total: int

