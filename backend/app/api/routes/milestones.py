import logging
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.milestone import (
    CreateManualPlanRequest,
    GenerateMilestonePlanRequest,
    MilestonePlanListResponse,
    MilestonePlanResponse,
    RequestRevisionRequest,
    UpdateMilestonePlanRequest,
)
from app.services import milestone_plan_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects/{project_id}/milestone-plans", tags=["Milestone Plans"])


@router.post(
    "/generate",
    response_model=MilestonePlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate milestone plan using Gemini AI",
    description="Invokes Google Gemini with structured output to analyze the project brief and generate measurable milestones.",
)
def generate_ai_milestone_plan(
    project_id: uuid.UUID,
    req: GenerateMilestonePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate and persist an AI-structured milestone plan proposal."""
    return milestone_plan_service.generate_ai_milestone_plan(
        project_id=project_id,
        current_user=current_user,
        req=req,
        db=db,
    )


@router.post(
    "/manual",
    response_model=MilestonePlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create milestone plan manually",
    description="Allows a project member to manually define milestones with budget allocations and durations.",
)
def create_manual_milestone_plan(
    project_id: uuid.UUID,
    req: CreateManualPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a manual milestone plan."""
    return milestone_plan_service.create_manual_milestone_plan(
        project_id=project_id,
        current_user=current_user,
        req=req,
        db=db,
    )


@router.get(
    "",
    response_model=MilestonePlanListResponse,
    summary="List milestone plan versions for a project",
    description="Returns all milestone plan versions for this project ordered by version descending.",
)
def list_project_milestone_plans(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all milestone plan versions for the project."""
    plans = milestone_plan_service.get_project_plans(
        project_id=project_id,
        current_user=current_user,
        db=db,
    )
    return MilestonePlanListResponse(plans=plans, total=len(plans))


@router.get(
    "/{plan_id}",
    response_model=MilestonePlanResponse,
    summary="Get milestone plan details",
    description="Retrieves a specific milestone plan version with its milestones and reviews.",
)
def get_milestone_plan(
    project_id: uuid.UUID,
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a single milestone plan version."""
    return milestone_plan_service.get_plan_by_id(
        project_id=project_id,
        plan_id=plan_id,
        current_user=current_user,
        db=db,
    )


@router.patch(
    "/{plan_id}",
    response_model=MilestonePlanResponse,
    summary="Update draft milestone plan",
    description="Edits milestone plan content or individual milestones while in draft or revision_requested status.",
)
def update_milestone_plan(
    project_id: uuid.UUID,
    plan_id: uuid.UUID,
    req: UpdateMilestonePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a draft or revision_requested milestone plan."""
    return milestone_plan_service.update_draft_plan(
        project_id=project_id,
        plan_id=plan_id,
        current_user=current_user,
        req=req,
        db=db,
    )


@router.post(
    "/{plan_id}/submit-for-approval",
    response_model=MilestonePlanResponse,
    summary="Submit milestone plan for bilateral approval",
    description="Locks plan content and transitions state to pending_approval. Requires both Client and Freelancer to be members.",
)
def submit_milestone_plan_for_approval(
    project_id: uuid.UUID,
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit milestone plan for bilateral approval."""
    return milestone_plan_service.submit_plan_for_approval(
        project_id=project_id,
        plan_id=plan_id,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/{plan_id}/approve",
    response_model=MilestonePlanResponse,
    summary="Approve milestone plan",
    description="Records authenticated user approval. When both Client and Freelancer approve, the plan is marked 'agreed' and project is activated.",
)
def approve_milestone_plan(
    project_id: uuid.UUID,
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Approve milestone plan."""
    return milestone_plan_service.approve_plan(
        project_id=project_id,
        plan_id=plan_id,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/{plan_id}/request-revision",
    response_model=MilestonePlanResponse,
    summary="Request milestone plan revision",
    description="Submits revision feedback comments and returns plan status to 'revision_requested' for further editing.",
)
def request_milestone_plan_revision(
    project_id: uuid.UUID,
    plan_id: uuid.UUID,
    req: RequestRevisionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Request revisions on a pending milestone plan."""
    return milestone_plan_service.request_plan_revision(
        project_id=project_id,
        plan_id=plan_id,
        current_user=current_user,
        comment=req.comment,
        db=db,
    )
