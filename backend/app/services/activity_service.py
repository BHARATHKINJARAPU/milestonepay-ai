import logging
from typing import Any, Dict, List, Optional, Tuple
import uuid
from sqlalchemy.orm import Session, joinedload

from app.models.project_activity import ProjectActivity

logger = logging.getLogger(__name__)


class ActivityService:
    """Manages recording and retrieval of chronological project activity events."""

    def record_activity(
        self,
        db: Session,
        project_id: uuid.UUID,
        activity_type: str,
        title: str,
        actor_user_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProjectActivity:
        """Create and persist an activity log event for a project."""
        try:
            # Clean metadata to prevent storing sensitive tokens or credentials
            safe_metadata = {}
            if metadata:
                for k, v in metadata.items():
                    if k.lower() not in {"password", "token", "secret", "access_token", "client_secret"}:
                        safe_metadata[k] = v

            activity = ProjectActivity(
                project_id=project_id,
                actor_user_id=actor_user_id,
                activity_type=activity_type,
                title=title,
                description=description,
                activity_metadata=safe_metadata,
            )
            db.add(activity)
            db.commit()
            db.refresh(activity)
            logger.info("Recorded activity '%s' for project %s", title, project_id)
            return activity
        except Exception as exc:
            db.rollback()
            logger.error("Failed to record activity for project %s: %s", project_id, exc)
            raise

    def get_project_activities(
        self,
        db: Session,
        project_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[ProjectActivity], int]:
        """Retrieve paginated activity history for a project with actor information."""
        query = (
            db.query(ProjectActivity)
            .options(joinedload(ProjectActivity.actor))
            .filter(ProjectActivity.project_id == project_id)
        )
        total = query.count()
        activities = (
            query.order_by(ProjectActivity.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return activities, total


activity_service = ActivityService()

