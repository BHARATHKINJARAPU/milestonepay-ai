import logging
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.submission import (
    ClientReviewRequest,
    CreateSubmissionRequest,
    MilestoneSubmissionListResponse,
    MilestoneSubmissionResponse,
)
from app.services import submission_service
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Milestone Deliverable Submissions"])


# ============================================================================
# PROJECT & MILESTONE SCOPED SUBMISSION ROUTES
# ============================================================================

@router.post(
    "/projects/{project_id}/milestones/{milestone_id}/submissions",
    response_model=MilestoneSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new draft deliverable submission attempt",
    description="Initiates a new submission attempt for an agreed milestone. Only the assigned freelancer can create submissions.",
)
def create_submission(
    project_id: uuid.UUID,
    milestone_id: uuid.UUID,
    req: CreateSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a draft milestone submission attempt."""
    return submission_service.create_submission_draft(
        project_id=project_id,
        milestone_id=milestone_id,
        current_user=current_user,
        req=req,
        db=db,
    )


@router.get(
    "/projects/{project_id}/milestones/{milestone_id}/submissions",
    response_model=MilestoneSubmissionListResponse,
    summary="List all submission attempts for a milestone",
    description="Returns all submission attempts for this milestone, ordered by attempt number descending.",
)
def list_milestone_submissions(
    project_id: uuid.UUID,
    milestone_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all submission attempts for a milestone."""
    submissions = submission_service.get_milestone_submissions(
        project_id=project_id,
        milestone_id=milestone_id,
        current_user=current_user,
        db=db,
    )
    return MilestoneSubmissionListResponse(submissions=submissions, total=len(submissions))


# ============================================================================
# SUBMISSION DETAIL & WORKFLOW ROUTES
# ============================================================================

@router.get(
    "/submissions/{submission_id}",
    response_model=MilestoneSubmissionResponse,
    summary="Get submission details with evidence and AI evaluations",
    description="Retrieves a complete submission record including evidence artifacts and evaluation reviews.",
)
def get_submission(
    submission_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve single submission attempt details."""
    return submission_service.get_submission_by_id(
        submission_id=submission_id,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/submissions/{submission_id}/evidence",
    response_model=MilestoneSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload evidence artifacts to a draft submission",
    description="Uploads one or more evidence files (PDF, PNG, JPG, TXT up to 10MB each) to an unsubmitted draft.",
)
async def upload_evidence(
    submission_id: uuid.UUID,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload evidence files to a draft submission."""
    return await submission_service.upload_submission_evidence(
        submission_id=submission_id,
        current_user=current_user,
        files=files,
        db=db,
    )


@router.delete(
    "/submissions/{submission_id}/evidence/{evidence_id}",
    response_model=MilestoneSubmissionResponse,
    summary="Delete an evidence artifact from a draft submission",
    description="Removes an evidence file and purges it from storage while the submission is still in draft.",
)
def delete_evidence(
    submission_id: uuid.UUID,
    evidence_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an evidence file from a draft submission."""
    return submission_service.delete_submission_evidence(
        submission_id=submission_id,
        evidence_id=evidence_id,
        current_user=current_user,
        db=db,
    )


@router.get(
    "/submissions/{submission_id}/evidence/{evidence_id}",
    summary="Download or view an authenticated evidence artifact",
    description="Streams an evidence file if the user is an authorized project member.",
)
def download_evidence(
    submission_id: uuid.UUID,
    evidence_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stream evidence artifact for authenticated project members."""
    submission = submission_service.get_submission_by_id(
        submission_id=submission_id,
        current_user=current_user,
        db=db,
    )

    evidence = next((e for e in submission.evidence if e.id == evidence_id), None)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence artifact not found.",
        )

    file_path = storage_service.get_file_path(evidence.storage_key)
    return FileResponse(
        path=str(file_path),
        filename=evidence.original_filename,
        media_type=evidence.media_type,
    )


@router.post(
    "/submissions/{submission_id}/submit",
    response_model=MilestoneSubmissionResponse,
    summary="Submit deliverable work and trigger Gemini AI evaluation",
    description="Transitions draft to submitted, locks files, and triggers Gemini AI to evaluate evidence against agreed acceptance criteria.",
)
def submit_work(
    submission_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit work and trigger AI evaluation."""
    return submission_service.submit_work(
        submission_id=submission_id,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/submissions/{submission_id}/evaluate",
    response_model=MilestoneSubmissionResponse,
    summary="Re-evaluate submitted deliverable with Gemini AI",
    description="Runs a fresh evaluation of the submitted evidence against the agreed acceptance criteria.",
)
def retry_evaluation(
    submission_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Re-run AI evaluation on a submitted deliverable."""
    return submission_service.retry_evaluation(
        submission_id=submission_id,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/submissions/{submission_id}/approve",
    response_model=MilestoneSubmissionResponse,
    summary="Client approves submitted milestone deliverable",
    description="Authorizes client approval of the milestone work, advancing milestone status to approved.",
)
def client_approve(
    submission_id: uuid.UUID,
    req: Optional[ClientReviewRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Client approves milestone deliverable."""
    comment = req.comment if req else None
    return submission_service.client_approve_submission(
        submission_id=submission_id,
        current_user=current_user,
        comment=comment,
        db=db,
    )


@router.post(
    "/submissions/{submission_id}/request-revision",
    response_model=MilestoneSubmissionResponse,
    summary="Client requests revision on submitted milestone deliverable",
    description="Records client feedback comment and returns submission and milestone to revision_requested status.",
)
def client_request_revision(
    submission_id: uuid.UUID,
    req: ClientReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Client requests revision on submitted deliverable."""
    return submission_service.client_request_revision(
        submission_id=submission_id,
        current_user=current_user,
        comment=req.comment or "",
        db=db,
    )

