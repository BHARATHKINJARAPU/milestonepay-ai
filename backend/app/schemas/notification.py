from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    """Schema for user notification."""

    id: uuid.UUID
    user_id: uuid.UUID
    project_id: Optional[uuid.UUID] = None
    milestone_id: Optional[uuid.UUID] = None
    notification_type: str
    title: str
    message: str
    action_url: Optional[str] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Paginated collection of notifications with unread count."""

    notifications: List[NotificationResponse]
    total: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    """Unread notification count badge response."""

    unread_count: int

