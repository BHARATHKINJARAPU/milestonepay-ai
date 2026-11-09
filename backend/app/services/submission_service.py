import datetime
import logging
from typing import List, Optional, Tuple
import uuid
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.enums import (
    AIReviewStatus,
    ClientSubmissionDecision,
    MemberRole,
    MilestoneStatus,
    PlanStatus,
    SubmissionStatus,
)
from app.models.milestone import Milestone
from app.models.milestone_plan import MilestonePlan
from app.models.milestone_submission import MilestoneSubmission
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.submission_evidence import SubmissionEvidence
from app.models.submission_review import AISubmissionReview, ClientSubmissionReview
from app.models.user import User
from app.schemas.submission import CreateSubmissionRequest
from app.services.activity_service import activity_service
from app.services.deliverable_evaluator import evaluate_submission
from app.services.evidence_processing_service import evidence_processing_service
from app.services.gemini_service import GeminiService, gemini_service
from app.services.notification_service import notification_service
from app.services.storage_service import MAX_EVIDENCE_FILES, storage_service

logger = logging.getLogger(__name__)


def _get_loaded_submission(submission_id: uuid.UUID, db: Session) -> Optional[MilestoneSubmission]:
    """Helper to query a submission with eager-loaded evidence, reviews, and submitter."""
    return (
        db.query(MilestoneSubmission)
        .options(
            joinedload(MilestoneSubmission.submitted_by),
            joinedload(MilestoneSubmission.evidence),
            joinedload(MilestoneSubmission.ai_reviews),
            joinedload(MilestoneSubmission.client_reviews).joinedload(ClientSubmissionReview.reviewer),
            joinedload(MilestoneSubmission.milestone).joinedload(Milestone.plan).joinedload(MilestonePlan.project),
        )
        .filter(MilestoneSubmission.id == submission_id)
        .first()
    )


def _verify_membership_and_milestone(
    project_id: uuid.UUID,
    milestone_id: uuid.UUID,
    user: User,
    db: Session,
) -> Tuple[Project, ProjectMember, Milestone]:
    """Verify that project exists, user is a member, and milestone belongs to project."""
    project = (
        db.query(Project)
        .options(joinedload(Project.members).joinedload(ProjectMember.user))
        .filter(Project.id == project_id)
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    membership = next((m for m in project.members if m.user_id == user.id), None)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project.",
        )

    milestone = (
        db.query(Milestone)
        .join(MilestonePlan, Milestone.plan_id == MilestonePlan.id)
        .options(joinedload(Milestone.plan))
        .filter(Milestone.id == milestone_id, MilestonePlan.project_id == project_id)
        .first()
    )
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found for this project.",
        )

    return project, membership, milestone


def create_submission_draft(
    project_id: uuid.UUID,
    milestone_id: uuid.UUID,
    current_user: User,
    req: CreateSubmissionRequest,
    db: Session,
) -> MilestoneSubmission:
    """Create a draft milestone submission attempt (Freelancer only, on agreed plans)."""
    _, membership, milestone = _verify_membership_and_milestone(
        project_id=project_id,
        milestone_id=milestone_id,
        user=current_user,
        db=db,
    )

    # 1. Submissions permitted only by assigned freelancer
    if membership.role != MemberRole.FREELANCER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned freelancer can create milestone deliverable submissions.",
        )

    # 2. Plan must be in AGREED status
    if milestone.plan.status != PlanStatus.AGREED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deliverable submissions are only permitted on agreed milestone plans.",
        )

    # 3. Acceptance criteria must exist
    if not milestone.acceptance_criteria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Milestone has no acceptance criteria defined. Members must configure criteria first.",
        )

    # 4. Prevent multiple conflicting active drafts
    existing_draft = (
        db.query(MilestoneSubmission)
        .filter(
            MilestoneSubmission.milestone_id == milestone.id,
            MilestoneSubmission.status == SubmissionStatus.DRAFT,
        )
        .first()
    )
    if existing_draft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active draft submission already exists for this milestone. Please complete or submit it.",
        )

    # 5. Check if milestone is already fully approved
    if milestone.status == MilestoneStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This milestone has already been approved. New submissions are not permitted.",
        )

    # 6. Determine next attempt number
    latest_attempt = (
        db.query(func.max(MilestoneSubmission.attempt_number))
        .filter(MilestoneSubmission.milestone_id == milestone.id)
        .scalar()
        or 0
    )
    next_attempt = latest_attempt + 1

    submission = MilestoneSubmission(
        milestone_id=milestone.id,
        submitted_by_id=current_user.id,
        attempt_number=next_attempt,
        description=req.description.strip(),
        notes=req.notes.strip() if req.notes else None,
        demonstration_url=req.demonstration_url.strip() if req.demonstration_url else None,
        acceptance_criteria_snapshot=milestone.acceptance_criteria,
        status=SubmissionStatus.DRAFT,
        ai_review_status=AIReviewStatus.PENDING,
    )
    db.add(submission)

    # Transition milestone to IN_PROGRESS if not already started
    if milestone.status == MilestoneStatus.NOT_STARTED:
        milestone.status = MilestoneStatus.IN_PROGRESS

    db.commit()
    logger.info("Created draft submission attempt #%d for milestone %s", next_attempt, milestone.id)
    return _get_loaded_submission(submission.id, db)


async def upload_submission_evidence(
    submission_id: uuid.UUID,
    current_user: User,
    files: List[UploadFile],
    db: Session,
) -> MilestoneSubmission:
    """Upload one or more evidence files for a draft submission."""
    submission = _get_loaded_submission(submission_id, db)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone submission not found.",
        )

    if submission.submitted_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the submitting freelancer can upload evidence to this draft.",
        )

    if submission.status != SubmissionStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Evidence can only be uploaded to draft submissions. Current status: '{submission.status.value}'.",
        )

    current_evidence_count = len(submission.evidence)
    if current_evidence_count + len(files) > MAX_EVIDENCE_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot exceed {MAX_EVIDENCE_FILES} evidence files per submission (currently {current_evidence_count}).",
        )

    for upload_file in files:
        storage_key, file_size, sha256_hash, media_type = await storage_service.save_uploaded_file(upload_file)
        evidence = SubmissionEvidence(
            submission_id=submission.id,
            uploaded_by_id=current_user.id,
            original_filename=upload_file.filename or "uploaded_evidence",
            storage_key=storage_key,
            media_type=media_type,
            file_size_bytes=file_size,
            sha256_hash=sha256_hash,
        )
        db.add(evidence)

    db.commit()
    logger.info("Uploaded %d evidence files to submission %s", len(files), submission.id)
    return _get_loaded_submission(submission.id, db)


def delete_submission_evidence(
    submission_id: uuid.UUID,
    evidence_id: uuid.UUID,
    current_user: User,
    db: Session,
) -> MilestoneSubmission:
    """Delete an evidence artifact from a draft submission."""
    submission = _get_loaded_submission(submission_id, db)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone submission not found.",
        )

    if submission.submitted_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the submitting freelancer can delete evidence from this draft.",
        )

    if submission.status != SubmissionStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Evidence can only be deleted while the submission is in draft status.",
        )

    evidence = next((e for e in submission.evidence if e.id == evidence_id), None)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence artifact not found.",
        )

    # Delete from disk
    storage_service.delete_file(evidence.storage_key)

    # Delete from database
    db.delete(evidence)
    db.commit()
    logger.info("Deleted evidence artifact %s from submission %s", evidence_id, submission.id)
    return _get_loaded_submission(submission.id, db)


def submit_work(
    submission_id: uuid.UUID,
    current_user: User,
    db: Session,
    ai_service: Optional[GeminiService] = None,
) -> MilestoneSubmission:
    """Finalize submission, transition state, and trigger Gemini AI deliverable evaluation."""
    submission = _get_loaded_submission(submission_id, db)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone submission not found.",
        )

    if submission.submitted_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the submitting freelancer can submit this deliverable.",
        )

    if submission.status != SubmissionStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Submission is already in '{submission.status.value}' status.",
        )

    # 1. Update submission and milestone status to SUBMITTED
    now = datetime.datetime.now(datetime.timezone.utc)
    submission.status = SubmissionStatus.SUBMITTED
    submission.submitted_at = now
    submission.ai_review_status = AIReviewStatus.PENDING

    milestone = submission.milestone
    milestone.status = MilestoneStatus.SUBMITTED

    # Commit submission state to database FIRST
    db.commit()
    logger.info("Submission %s (attempt #%d) marked SUBMITTED", submission.id, submission.attempt_number)

    # Record deliverable submission activity and notify client
    try:
        activity_service.record_activity(
            db=db,
            project_id=milestone.plan.project_id,
            activity_type="deliverable_submitted",
            title=f"Deliverable Submitted: '{milestone.title}'",
            actor_user_id=current_user.id,
            description=f"Attempt #{submission.attempt_number} submitted with {len(submission.evidence)} evidence file(s).",
        )
        for m in milestone.plan.project.members:
            if m.user_id != current_user.id:
                notification_service.create_notification(
                    db=db,
                    user_id=m.user_id,
                    notification_type="submission_received",
                    title=f"Deliverable Submitted for '{milestone.title}'",
                    message=f"{current_user.full_name} submitted deliverables for milestone '{milestone.title}'. Review evidence and AI evaluation.",
                    action_url=f"/projects/{milestone.plan.project_id}/submissions/{submission.id}",
                    project_id=milestone.plan.project_id,
                    milestone_id=milestone.id,
                )
    except Exception as exc:
        logger.warning("Could not record submission activity/notification: %s", exc)

    # 2. Trigger Gemini AI Evaluation
    _execute_ai_evaluation(
        submission=submission,
        milestone=milestone,
        review_version=1,
        ai_service=ai_service,
        db=db,
    )

    return _get_loaded_submission(submission.id, db)


def retry_evaluation(
    submission_id: uuid.UUID,
    current_user: User,
    db: Session,
    ai_service: Optional[GeminiService] = None,
) -> MilestoneSubmission:
    """Allow authorized project member to re-evaluate a submitted deliverable with Gemini AI."""
    submission = _get_loaded_submission(submission_id, db)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone submission not found.",
        )

    project = submission.milestone.plan.project
    membership = next((m for m in project.members if m.user_id == current_user.id), None)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project.",
        )

    if submission.status not in (SubmissionStatus.SUBMITTED, SubmissionStatus.REVISION_REQUESTED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Evaluation cannot be run on submissions in '{submission.status.value}' status.",
        )

    latest_review_version = (
        db.query(func.max(AISubmissionReview.review_version))
        .filter(AISubmissionReview.submission_id == submission.id)
        .scalar()
        or 0
    )
    next_review_version = latest_review_version + 1

    submission.ai_review_status = AIReviewStatus.PENDING
    db.commit()

    _execute_ai_evaluation(
        submission=submission,
        milestone=submission.milestone,
        review_version=next_review_version,
        ai_service=ai_service,
        db=db,
    )

    return _get_loaded_submission(submission.id, db)


def _execute_ai_evaluation(
    submission: MilestoneSubmission,
    milestone: Milestone,
    review_version: int,
    ai_service: Optional[GeminiService],
    db: Session,
) -> None:
    """Helper to extract evidence and perform AI evaluation, persisting audit review."""
    extracted_items = evidence_processing_service.process_all_evidence(submission.evidence)

    try:
        eval_report = evaluate_submission(
            milestone=milestone,
            submission=submission,
            evidence_items=extracted_items,
            ai_service=ai_service,
        )

        review = AISubmissionReview(
            submission_id=submission.id,
            review_version=review_version,
            overall_summary=eval_report.overall_summary,
            evaluation_results=[c.model_dump() for c in eval_report.criterion_evaluations],
            identified_gaps=eval_report.identified_gaps,
            recommendations=eval_report.recommendations,
            limitations=eval_report.limitations,
            areas_for_human_verification=eval_report.areas_for_human_verification,
            model_name=getattr(ai_service or gemini_service, "model", settings.GEMINI_MODEL),
            status="completed",
            raw_error=None,
        )
        db.add(review)
        submission.ai_review_status = AIReviewStatus.COMPLETED
        db.commit()
        logger.info("AI review version #%d completed for submission %s", review_version, submission.id)

    except Exception as e:
        logger.error("AI deliverable evaluation failed for submission %s: %s", submission.id, e)
        db.rollback()
        # Record failure on submission without rolling back the submitted state
        sub_record = db.query(MilestoneSubmission).filter(MilestoneSubmission.id == submission.id).first()
        if sub_record:
            sub_record.ai_review_status = AIReviewStatus.FAILED
            # Create failed review record for auditability
            failed_review = AISubmissionReview(
                submission_id=sub_record.id,
                review_version=review_version,
                overall_summary="Automated AI deliverable evaluation could not be completed at this time.",
                evaluation_results=[],
                identified_gaps=[],
                recommendations=[],
                limitations=["AI provider service temporarily unavailable or file processing failed."],
                areas_for_human_verification=["Full manual inspection by client required."],
                model_name=getattr(ai_service or gemini_service, "model", settings.GEMINI_MODEL),
                status="failed",
                raw_error=str(e),
            )
            db.add(failed_review)
            db.commit()


def client_approve_submission(
    submission_id: uuid.UUID,
    current_user: User,
    comment: Optional[str],
    db: Session,
) -> MilestoneSubmission:
    """Client approves submitted deliverable work, marking milestone approved."""
    submission = _get_loaded_submission(submission_id, db)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone submission not found.",
        )

    project = submission.milestone.plan.project
    membership = next((m for m in project.members if m.user_id == current_user.id), None)
    if not membership or membership.role != MemberRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned client can approve submitted milestone deliverables.",
        )

    if submission.status != SubmissionStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve submission in '{submission.status.value}' status. It must be submitted.",
        )

    # 1. Record Client Review
    review = ClientSubmissionReview(
        submission_id=submission.id,
        reviewer_user_id=current_user.id,
        decision=ClientSubmissionDecision.APPROVED,
        comment=comment.strip() if comment else "Deliverables approved by client.",
    )
    db.add(review)

    # 2. Update submission and milestone statuses
    submission.status = SubmissionStatus.APPROVED
    submission.milestone.status = MilestoneStatus.APPROVED

    db.commit()

    # Record client approval activity and notify submitting freelancer
    try:
        activity_service.record_activity(
            db=db,
            project_id=project.id,
            activity_type="milestone_approved",
            title=f"Milestone Approved: '{submission.milestone.title}'",
            actor_user_id=current_user.id,
            description=f"Client approved deliverables. Milestone value of {submission.milestone.currency} {float(submission.milestone.amount):,.2f} authorized for payment release.",
        )
        notification_service.create_notification(
            db=db,
            user_id=submission.submitted_by_id,
            notification_type="client_approved",
            title="Milestone Deliverables Approved!",
            message=f"Your deliverables for '{submission.milestone.title}' were approved by the client! Payment release is now available.",
            action_url=f"/projects/{project.id}/milestones",
            project_id=project.id,
            milestone_id=submission.milestone_id,
        )
    except Exception as exc:
        logger.warning("Could not record approval activity/notification: %s", exc)

    logger.info("Milestone %s and submission %s APPROVED by client %s", submission.milestone_id, submission.id, current_user.email)
    return _get_loaded_submission(submission.id, db)


def client_request_revision(
    submission_id: uuid.UUID,
    current_user: User,
    comment: str,
    db: Session,
) -> MilestoneSubmission:
    """Client requests revision on submitted deliverable work with required feedback."""
    submission = _get_loaded_submission(submission_id, db)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone submission not found.",
        )

    project = submission.milestone.plan.project
    membership = next((m for m in project.members if m.user_id == current_user.id), None)
    if not membership or membership.role != MemberRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned client can request revisions on milestone deliverables.",
        )

    if submission.status != SubmissionStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot request revisions on submission in '{submission.status.value}' status.",
        )

    if not comment or len(comment.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A specific revision comment (minimum 5 characters) is required.",
        )

    # 1. Record Client Review
    review = ClientSubmissionReview(
        submission_id=submission.id,
        reviewer_user_id=current_user.id,
        decision=ClientSubmissionDecision.REVISION_REQUESTED,
        comment=comment.strip(),
    )
    db.add(review)

    # 2. Update submission and milestone statuses
    submission.status = SubmissionStatus.REVISION_REQUESTED
    submission.milestone.status = MilestoneStatus.REVISION_REQUESTED

    db.commit()

    # Record revision requested activity and notify freelancer
    try:
        activity_service.record_activity(
            db=db,
            project_id=project.id,
            activity_type="revision_requested",
            title=f"Revision Requested on '{submission.milestone.title}'",
            actor_user_id=current_user.id,
            description=f"Client requested revision on submission #{submission.attempt_number}: {comment.strip()}",
        )
        notification_service.create_notification(
            db=db,
            user_id=submission.submitted_by_id,
            notification_type="revision_requested",
            title="Milestone Revisions Requested",
            message=f"Client requested changes on '{submission.milestone.title}': '{comment.strip()[:80]}'",
            action_url=f"/projects/{project.id}/submissions/{submission.id}",
            project_id=project.id,
            milestone_id=submission.milestone_id,
        )
    except Exception as exc:
        logger.warning("Could not record revision request activity/notification: %s", exc)

    logger.info("Revision requested for submission %s by client %s", submission.id, current_user.email)
    return _get_loaded_submission(submission.id, db)


def get_submission_by_id(
    submission_id: uuid.UUID,
    current_user: User,
    db: Session,
) -> MilestoneSubmission:
    """Retrieve detailed submission record if user is an authorized project member."""
    submission = _get_loaded_submission(submission_id, db)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone submission not found.",
        )

    project = submission.milestone.plan.project
    membership = next((m for m in project.members if m.user_id == current_user.id), None)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project.",
        )

    return submission


def get_milestone_submissions(
    project_id: uuid.UUID,
    milestone_id: uuid.UUID,
    current_user: User,
    db: Session,
) -> List[MilestoneSubmission]:
    """Retrieve all submission attempts for a milestone in attempt_number descending order."""
    _verify_membership_and_milestone(
        project_id=project_id,
        milestone_id=milestone_id,
        user=current_user,
        db=db,
    )

    submissions = (
        db.query(MilestoneSubmission)
        .options(
            joinedload(MilestoneSubmission.submitted_by),
            joinedload(MilestoneSubmission.evidence),
            joinedload(MilestoneSubmission.ai_reviews),
            joinedload(MilestoneSubmission.client_reviews).joinedload(ClientSubmissionReview.reviewer),
        )
        .filter(MilestoneSubmission.milestone_id == milestone_id)
        .order_by(MilestoneSubmission.attempt_number.desc())
        .all()
    )
    return submissions

