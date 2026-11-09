import logging
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import AccountType, MemberRole, ProjectStatus
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.project import (
    AddMemberRequest,
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectStatusUpdateRequest,
    ProjectUpdateRequest,
)
from app.schemas.project_activity import (
    ProjectActivityListResponse,
    ProjectActivityResponse,
)
from app.schemas.analytics import ProjectAiSummaryResponse
from app.services.activity_service import activity_service
from app.services.analytics_service import analytics_service
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["Project Management"])

# Valid status transitions
ALLOWED_TRANSITIONS = {
    ProjectStatus.DRAFT: {ProjectStatus.ACTIVE, ProjectStatus.ARCHIVED},
    ProjectStatus.ACTIVE: {ProjectStatus.COMPLETED, ProjectStatus.ARCHIVED},
    ProjectStatus.COMPLETED: {ProjectStatus.ARCHIVED},
    ProjectStatus.ARCHIVED: {ProjectStatus.ACTIVE},  # Allow reactivation
}


def _get_project_with_members(project_id: uuid.UUID, db: Session) -> Optional[Project]:
    """Helper to query project eager-loading its members and user profiles."""
    return (
        db.query(Project)
        .options(
            joinedload(Project.members).joinedload(ProjectMember.user),
            joinedload(Project.creator),
        )
        .filter(Project.id == project_id)
        .first()
    )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new freelance project",
    description="Creates a project in PostgreSQL and automatically registers the creator as its first member.",
)
def create_project(
    req: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Create a new project and add current user as its initial member."""
    # Determine creator's project role matching their account type
    creator_role = (
        MemberRole.CLIENT
        if current_user.account_type == AccountType.CLIENT
        else MemberRole.FREELANCER
    )

    project = Project(
        title=req.title.strip(),
        description=req.description.strip(),
        budget_amount=req.budget_amount,
        currency=req.currency,
        deadline=req.deadline,
        status=ProjectStatus.DRAFT,
        created_by_id=current_user.id,
    )
    db.add(project)
    db.flush()  # Generate project.id

    # Automatically add creator as first project member
    initial_member = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role=creator_role,
    )
    db.add(initial_member)
    db.commit()

    # Record creation activity
    try:
        activity_service.record_activity(
            db=db,
            project_id=project.id,
            activity_type="project_created",
            title=f"Project '{project.title}' Created",
            actor_user_id=current_user.id,
            description=f"Project initialized by {current_user.full_name} ({creator_role.value}) with budget {project.currency} {float(project.budget_amount):,.2f}.",
        )
    except Exception as exc:
        logger.warning("Could not record project creation activity: %s", exc)

    loaded_project = _get_project_with_members(project.id, db)
    logger.info("Project created: %s (id: %s) by %s", loaded_project.title, loaded_project.id, current_user.email)
    return loaded_project


@router.get(
    "",
    response_model=ProjectListResponse,
    status_code=status.HTTP_200_OK,
    summary="List accessible projects",
    description="Returns all projects where the authenticated user is a registered member.",
)
def list_projects(
    status_filter: Optional[ProjectStatus] = Query(None, alias="status", description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectListResponse:
    """Return projects where current user is a member, optionally filtered by status."""
    query = (
        db.query(Project)
        .join(ProjectMember, Project.id == ProjectMember.project_id)
        .filter(ProjectMember.user_id == current_user.id)
        .options(
            joinedload(Project.members).joinedload(ProjectMember.user),
            joinedload(Project.creator),
        )
    )

    if status_filter:
        query = query.filter(Project.status == status_filter)

    projects = query.order_by(Project.created_at.desc()).all()
    return ProjectListResponse(
        projects=projects,
        total=len(projects),
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project details",
    description="Retrieves project information, membership details, and current status.",
)
def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Retrieve single project by ID if current user is a member."""
    project = _get_project_with_members(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    # Check that current user is a member of this project
    is_member = any(m.user_id == current_user.id for m in project.members)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project.",
        )

    return project


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update project details",
    description="Allows the project creator to update title, description, budget, or deadline.",
)
def update_project(
    project_id: uuid.UUID,
    req: ProjectUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Update project metadata if current user is the creator."""
    project = _get_project_with_members(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    if project.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project creator can edit project details.",
        )

    if req.title is not None:
        project.title = req.title.strip()
    if req.description is not None:
        project.description = req.description.strip()
    if req.budget_amount is not None:
        project.budget_amount = req.budget_amount
    if req.currency is not None:
        project.currency = req.currency
    if req.deadline is not None:
        project.deadline = req.deadline

    db.commit()
    return _get_project_with_members(project_id, db)


@router.post(
    "/{project_id}/members",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Add a collaborator to the project",
    description="Allows project creator to add a registered collaborator with the complementary role by email.",
)
def add_project_member(
    project_id: uuid.UUID,
    req: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Add a registered collaborator with the complementary role to a project."""
    project = _get_project_with_members(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    # 1. Creator authorization check
    if project.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project creator can add collaborators.",
        )

    # 2. Look up collaborator by email
    normalized_email = req.email.lower().strip()
    collaborator = db.query(User).filter(func.lower(User.email) == normalized_email).first()
    if not collaborator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No registered user found with this email address.",
        )

    # 3. Cannot add yourself
    if collaborator.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot add yourself as a collaborator.",
        )

    # 4. Must have the complementary account type
    expected_type = (
        AccountType.FREELANCER
        if current_user.account_type == AccountType.CLIENT
        else AccountType.CLIENT
    )
    if collaborator.account_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Collaborator must have the complementary account type ({expected_type.value}). User is registered as '{collaborator.account_type.value}'.",
        )

    # 5. Check if user is already a member
    if any(m.user_id == collaborator.id for m in project.members):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this project.",
        )

    # 6. Max 1 client and 1 freelancer per project
    collaborator_role = (
        MemberRole.FREELANCER
        if collaborator.account_type == AccountType.FREELANCER
        else MemberRole.CLIENT
    )
    if any(m.role == collaborator_role for m in project.members):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This project already has an assigned {collaborator_role.value}.",
        )

    # Add collaborator member
    new_member = ProjectMember(
        project_id=project.id,
        user_id=collaborator.id,
        role=collaborator_role,
    )
    db.add(new_member)
    db.commit()

    # Record collaborator addition activity and dispatch user notification
    try:
        activity_service.record_activity(
            db=db,
            project_id=project.id,
            activity_type="collaborator_added",
            title=f"Collaborator Joined: {collaborator.full_name}",
            actor_user_id=current_user.id,
            description=f"{collaborator.full_name} joined project as {collaborator_role.value}.",
        )
        notification_service.create_notification(
            db=db,
            user_id=collaborator.id,
            notification_type="collaborator_added",
            title="Invited to Project",
            message=f"You have been added to '{project.title}' as {collaborator_role.value} by {current_user.full_name}.",
            action_url=f"/projects/{project.id}",
            project_id=project.id,
        )
    except Exception as exc:
        logger.warning("Could not record collaborator activity/notification: %s", exc)

    logger.info("Added %s as %s to project %s", collaborator.email, collaborator_role.value, project.id)
    return _get_project_with_members(project_id, db)


@router.patch(
    "/{project_id}/status",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Change project status",
    description="Allows the project creator to change status with strict transition validation.",
)
def update_project_status(
    project_id: uuid.UUID,
    req: ProjectStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Transition project status if creator and transition is valid."""
    project = _get_project_with_members(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    if project.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project creator can update the project status.",
        )

    current_status = project.status
    target_status = req.status

    if current_status == target_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project is already in '{target_status.value}' status.",
        )

    valid_targets = ALLOWED_TRANSITIONS.get(current_status, set())
    if target_status not in valid_targets:
        allowed_str = ", ".join(f"'{s.value}'" for s in valid_targets)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from '{current_status.value}' to '{target_status.value}'. Allowed transitions: [{allowed_str}].",
        )

    project.status = target_status
    db.commit()

    logger.info("Project %s transitioned from %s to %s", project.id, current_status.value, target_status.value)
    return _get_project_with_members(project_id, db)


@router.get(
    "/{project_id}/activities",
    response_model=ProjectActivityListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project activity timeline",
    description="Returns chronological audit trail of all project events visible only to project members.",
)
def get_project_activities(
    project_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectActivityListResponse:
    """Retrieve chronological activity events for authorized project members."""
    project = _get_project_with_members(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    if not any(m.user_id == current_user.id for m in project.members):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to view activities for this project.",
        )

    activities, total = activity_service.get_project_activities(db, project_id, skip=skip, limit=limit)
    return ProjectActivityListResponse(
        activities=[
            ProjectActivityResponse(
                id=a.id,
                project_id=a.project_id,
                actor_user_id=a.actor_user_id,
                actor_name=a.actor.full_name if a.actor else None,
                activity_type=a.activity_type,
                title=a.title,
                description=a.description,
                activity_metadata=a.activity_metadata or {},
                created_at=a.created_at,
            )
            for a in activities
        ],
        total=total,
    )


@router.get(
    "/{project_id}/ai-summary",
    response_model=ProjectAiSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project AI health summary",
    description="Returns Gemini-powered or factual project health assessment and risk evaluation.",
)
def get_project_ai_summary(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectAiSummaryResponse:
    """Convenience alias route for project AI summary."""
    return analytics_service.get_project_ai_summary(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )


