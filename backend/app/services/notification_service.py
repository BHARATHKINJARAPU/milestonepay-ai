from datetime import datetime, timezone
import logging
from typing import List, Optional, Tuple
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """Manages creation, filtering, and lifecycle of user notifications."""

    def create_notification(
        self,
        db: Session,
        user_id: uuid.UUID,
        notification_type: str,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        project_id: Optional[uuid.UUID] = None,
        milestone_id: Optional[uuid.UUID] = None,
    ) -> Notification:
        """Create and persist a new user notification."""
        try:
            notification = Notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                action_url=action_url,
                project_id=project_id,
                milestone_id=milestone_id,
                is_read=False,
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            logger.info("Notification %s created for user %s: '%s'", notification.id, user_id, title)
            return notification
        except Exception as exc:
            db.rollback()
            logger.error("Failed to create notification for user %s: %s", user_id, exc)
            raise

    def get_user_notifications(
        self,
        db: Session,
        user_id: uuid.UUID,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Notification], int, int]:
        """Retrieve paginated notifications and total/unread counts for an authenticated user."""
        base_query = db.query(Notification).filter(Notification.user_id == user_id)
        
        unread_count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa: E712
        ).count()

        if unread_only:
            query = base_query.filter(Notification.is_read == False)  # noqa: E712
        else:
            query = base_query

        total = query.count()
        notifications = (
            query.order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return notifications, total, unread_count

    def get_unread_count(self, db: Session, user_id: uuid.UUID) -> int:
        """Get total unread notifications count for badge indicators."""
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa: E712
        ).count()

    def mark_as_read(
        self,
        db: Session,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Notification:
        """Mark a single notification as read if owned by the user."""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        ).first()

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or access denied.",
            )

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(notification)

        return notification

    def mark_all_as_read(self, db: Session, user_id: uuid.UUID) -> int:
        """Mark all unread notifications as read for the user."""
        now = datetime.now(timezone.utc)
        updated_count = (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read == False,  # noqa: E712
            )
            .update(
                {"is_read": True, "read_at": now},
                synchronize_session=False,
            )
        )
        db.commit()
        return updated_count

    def delete_notification(
        self,
        db: Session,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """Delete a notification owned by the current user."""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        ).first()

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or access denied.",
            )

        db.delete(notification)
        db.commit()


notification_service = NotificationService()

