import logging
import uuid
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.enums import MemberRole, PlanGenerationSource, PlanStatus, ProjectStatus, ReviewDecision
from app.models.milestone import Milestone
from app.models.milestone_plan import MilestonePlan
from app.models.milestone_plan_review import MilestonePlanReview
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.milestone import (
    CreateManualPlanRequest,
    GenerateMilestonePlanRequest,
    UpdateMilestonePlanRequest,
)
from app.services.activity_service import activity_service
from app.services.gemini_service import GeminiService, gemini_service
from app.services.notification_service import notification_service
from app.services.milestone_generator import (
    SYSTEM_INSTRUCTION,
    build_user_prompt,
    calculate_milestone_dates,
    calculate_milestone_finances,
    validate_milestone_dependencies,
)

logger = logging.getLogger(__name__)


def _verify_project_membership(project_id: uuid.UUID, user: User, db: Session) -> Tuple[Project, ProjectMember]:
    """Verify that project exists and current user is a registered member."""
    project = (
        db.query(Project)
        .options(
            joinedload(Project.members).joinedload(ProjectMember.user),
            joinedload(Project.creator),
        )
        .filter(Project.id == project_id)
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    user_membership = next((m for m in project.members if m.user_id == user.id), None)
    if not user_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project.",
        )

    return project, user_membership



def _get_loaded_plan(plan_id: uuid.UUID, db: Session) -> Optional[MilestonePlan]:
    """Helper to query a plan with eager-loaded milestones and reviews."""
    return (
        db.query(MilestonePlan)
        .options(
            joinedload(MilestonePlan.milestones),
            joinedload(MilestonePlan.reviews).joinedload(MilestonePlanReview.reviewer),
            joinedload(MilestonePlan.creator),
        )
        .filter(MilestonePlan.id == plan_id)
        .first()
    )


def generate_ai_milestone_plan(
    project_id: uuid.UUID,
    current_user: User,
    req: GenerateMilestonePlanRequest,
    db: Session,
    ai_service: Optional[GeminiService] = None,
) -> MilestonePlan:
    """Generate and persist an AI-structured milestone plan draft for a project."""
    project, _ = _verify_project_membership(project_id, current_user, db)

    # 1. Determine next version number for this project
    latest_version = (
        db.query(func.max(MilestonePlan.version))
        .filter(MilestonePlan.project_id == project_id)
        .scalar()
        or 0
    )
    next_version = latest_version + 1

    # 2. Build prompt for Gemini
    prompt = build_user_prompt(
        title=project.title,
        description=project.description,
        total_budget=project.budget_amount,
        currency=project.currency,
        deadline=project.deadline,
        additional_instructions=req.additional_instructions,
    )

    # 3. Call AI Service
    generator = ai_service or gemini_service
    try:
        analysis = generator.generate_milestone_plan(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION,
        )
    except ValueError as e:
        logger.error("Gemini generation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Unexpected error during AI generation: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {str(e)}",
        )

    # 4. Validate milestone dependencies
    validate_milestone_dependencies(analysis.milestones)

    # 5. Calculate finances & exact monetary allocations
    financial_milestones = calculate_milestone_finances(
        milestones=analysis.milestones,
        total_budget=project.budget_amount,
        currency=project.currency,
    )

    # 6. Calculate timeline dates
    dated_milestones = calculate_milestone_dates(
        milestones=financial_milestones,
        deadline=project.deadline,
    )

    # 7. Persist in database transaction
    plan = MilestonePlan(
        project_id=project.id,
        version=next_version,
        status=PlanStatus.DRAFT,
        project_summary=analysis.project_summary.strip(),
        total_amount=project.budget_amount,
        currency=project.currency,
        assumptions=analysis.assumptions,
        clarifying_questions=analysis.clarifying_questions,
        risks=analysis.risks,
        needs_clarification=analysis.needs_clarification,
        generation_source=PlanGenerationSource.AI,
        ai_model=getattr(generator, "model", "gemini"),
        created_by_id=current_user.id,
    )
    db.add(plan)
    db.flush()

    # Add milestone records
    for m in dated_milestones:
        milestone = Milestone(
            plan_id=plan.id,
            sequence_number=int(m["sequence_number"]),
            title=m["title"].strip(),
            description=m["description"].strip(),
            deliverables=m["deliverables"],
            acceptance_criteria=m["acceptance_criteria"],
            estimated_duration_days=int(m["estimated_duration_days"]),
            start_date=m.get("start_date"),
            due_date=m.get("due_date"),
            budget_percentage=m["budget_percentage"],
            amount=m["amount"],
            currency=project.currency,
            dependencies=m.get("dependencies", []),
        )
        db.add(milestone)

    db.commit()
    logger.info("Successfully saved AI Milestone Plan v%d for project %s", plan.version, project.id)
    return _get_loaded_plan(plan.id, db)


def create_manual_milestone_plan(
    project_id: uuid.UUID,
    current_user: User,
    req: CreateManualPlanRequest,
    db: Session,
) -> MilestonePlan:
    """Author and persist a manual milestone plan draft."""
    project, _ = _verify_project_membership(project_id, current_user, db)

    latest_version = (
        db.query(func.max(MilestonePlan.version))
        .filter(MilestonePlan.project_id == project_id)
        .scalar()
        or 0
    )
    next_version = latest_version + 1

    try:
        validate_milestone_dependencies(req.milestones)
        financial_milestones = calculate_milestone_finances(
            milestones=req.milestones,
            total_budget=project.budget_amount,
            currency=project.currency,
        )
        dated_milestones = calculate_milestone_dates(
            milestones=financial_milestones,
            deadline=project.deadline,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    plan = MilestonePlan(
        project_id=project.id,
        version=next_version,
        status=PlanStatus.DRAFT,
        project_summary=req.project_summary.strip(),
        total_amount=project.budget_amount,
        currency=project.currency,
        assumptions=req.assumptions,
        clarifying_questions=req.clarifying_questions,
        risks=req.risks,
        needs_clarification=False,
        generation_source=PlanGenerationSource.MANUAL,
        ai_model=None,
        created_by_id=current_user.id,
    )
    db.add(plan)
    db.flush()

    for m in dated_milestones:
        milestone = Milestone(
            plan_id=plan.id,
            sequence_number=int(m["sequence_number"]),
            title=m["title"].strip(),
            description=m["description"].strip(),
            deliverables=m["deliverables"],
            acceptance_criteria=m["acceptance_criteria"],
            estimated_duration_days=int(m["estimated_duration_days"]),
            start_date=m.get("start_date"),
            due_date=m.get("due_date"),
            budget_percentage=m["budget_percentage"],
            amount=m["amount"],
            currency=project.currency,
            dependencies=m.get("dependencies", []),
        )
        db.add(milestone)

    db.commit()
    logger.info("Created manual milestone plan v%d for project %s", plan.version, project.id)
    return _get_loaded_plan(plan.id, db)


def get_project_plans(project_id: uuid.UUID, current_user: User, db: Session) -> List[MilestonePlan]:
    """Retrieve all plan versions for a project."""
    _verify_project_membership(project_id, current_user, db)
    plans = (
        db.query(MilestonePlan)
        .options(
            joinedload(MilestonePlan.milestones),
            joinedload(MilestonePlan.reviews).joinedload(MilestonePlanReview.reviewer),
            joinedload(MilestonePlan.creator),
        )
        .filter(MilestonePlan.project_id == project_id)
        .order_by(MilestonePlan.version.desc())
        .all()
    )
    return plans


def get_plan_by_id(project_id: uuid.UUID, plan_id: uuid.UUID, current_user: User, db: Session) -> MilestonePlan:
    """Retrieve single plan version."""
    _verify_project_membership(project_id, current_user, db)
    plan = _get_loaded_plan(plan_id, db)
    if not plan or plan.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone plan not found for this project.",
        )
    return plan


def update_draft_plan(
    project_id: uuid.UUID,
    plan_id: uuid.UUID,
    current_user: User,
    req: UpdateMilestonePlanRequest,
    db: Session,
) -> MilestonePlan:
    """Update milestone plan content if in DRAFT or REVISION_REQUESTED state."""
    project, _ = _verify_project_membership(project_id, current_user, db)
    plan = (
        db.query(MilestonePlan)
        .filter(MilestonePlan.id == plan_id, MilestonePlan.project_id == project_id)
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone plan not found.",
        )

    # Protect locked / agreed versions
    if plan.status not in (PlanStatus.DRAFT, PlanStatus.REVISION_REQUESTED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot edit plan in '{plan.status.value}' status. Only draft or revision-requested versions can be modified.",
        )

    if req.project_summary is not None:
        plan.project_summary = req.project_summary.strip()
    if req.assumptions is not None:
        plan.assumptions = req.assumptions
    if req.clarifying_questions is not None:
        plan.clarifying_questions = req.clarifying_questions
    if req.risks is not None:
        plan.risks = req.risks

    # Update milestones if supplied
    if req.milestones is not None:
        try:
            validate_milestone_dependencies(req.milestones)
            financial_milestones = calculate_milestone_finances(
                milestones=req.milestones,
                total_budget=project.budget_amount,
                currency=project.currency,
            )
            dated_milestones = calculate_milestone_dates(
                milestones=financial_milestones,
                deadline=project.deadline,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        # Clear existing milestones and replace
        db.query(Milestone).filter(Milestone.plan_id == plan.id).delete()
        db.flush()

        for m in dated_milestones:
            milestone = Milestone(
                plan_id=plan.id,
                sequence_number=int(m["sequence_number"]),
                title=m["title"].strip(),
                description=m["description"].strip(),
                deliverables=m["deliverables"],
                acceptance_criteria=m["acceptance_criteria"],
                estimated_duration_days=int(m["estimated_duration_days"]),
                start_date=m.get("start_date"),
                due_date=m.get("due_date"),
                budget_percentage=m["budget_percentage"],
                amount=m["amount"],
                currency=project.currency,
                dependencies=m.get("dependencies", []),
            )
            db.add(milestone)

    db.commit()
    logger.info("Updated milestone plan %s (v%d)", plan.id, plan.version)
    return _get_loaded_plan(plan.id, db)


def submit_plan_for_approval(
    project_id: uuid.UUID,
    plan_id: uuid.UUID,
    current_user: User,
    db: Session,
) -> MilestonePlan:
    """Submit milestone plan for bilateral agreement between Client and Freelancer."""
    project, _ = _verify_project_membership(project_id, current_user, db)
    plan = _get_loaded_plan(plan_id, db)
    if not plan or plan.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone plan not found.",
        )

    # 1. Verify project has both Client and Freelancer
    member_roles = {m.role for m in project.members}
    if MemberRole.CLIENT not in member_roles or MemberRole.FREELANCER not in member_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A plan cannot be submitted for approval until both a Client and a Freelancer are linked to the project.",
        )

    # 2. Check milestone count
    if not plan.milestones:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot submit an empty plan without milestones.",
        )

    # 3. Check allowed status
    if plan.status not in (PlanStatus.DRAFT, PlanStatus.REVISION_REQUESTED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan is already in '{plan.status.value}' status.",
        )

    plan.status = PlanStatus.PENDING_APPROVAL
    db.commit()

    # Record activity and notify project members
    try:
        activity_service.record_activity(
            db=db,
            project_id=project.id,
            activity_type="milestone_plan_submitted",
            title=f"Plan v{plan.version} Submitted for Review",
            actor_user_id=current_user.id,
            description=f"{current_user.full_name} submitted milestone plan v{plan.version} with {len(plan.milestones)} milestone(s).",
        )
        for m in project.members:
            if m.user_id != current_user.id:
                notification_service.create_notification(
                    db=db,
                    user_id=m.user_id,
                    notification_type="milestone_plan_submitted",
                    title="Milestone Plan Awaiting Review",
                    message=f"{current_user.full_name} submitted plan v{plan.version} for '{project.title}'.",
                    action_url=f"/projects/{project.id}/milestones",
                    project_id=project.id,
                )
    except Exception as exc:
        logger.warning("Could not record activity/notification: %s", exc)

    logger.info("Plan v%d submitted for approval on project %s", plan.version, project.id)
    return _get_loaded_plan(plan.id, db)


def approve_plan(
    project_id: uuid.UUID,
    plan_id: uuid.UUID,
    current_user: User,
    db: Session,
) -> MilestonePlan:
    """Record authenticated member approval. Marks plan as agreed if both parties approve."""
    project, membership = _verify_project_membership(project_id, current_user, db)
    plan = _get_loaded_plan(plan_id, db)
    if not plan or plan.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone plan not found.",
        )

    if plan.status != PlanStatus.PENDING_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan cannot be approved in '{plan.status.value}' status. It must be pending approval.",
        )

    # Upsert user approval review
    review = (
        db.query(MilestonePlanReview)
        .filter(
            MilestonePlanReview.plan_id == plan.id,
            MilestonePlanReview.reviewer_user_id == current_user.id,
        )
        .first()
    )
    if not review:
        review = MilestonePlanReview(
            plan_id=plan.id,
            reviewer_user_id=current_user.id,
            reviewer_role=membership.role,
            decision=ReviewDecision.APPROVED,
            comment="Approved milestone proposal version.",
        )
        db.add(review)
    else:
        review.decision = ReviewDecision.APPROVED
        review.comment = "Approved milestone proposal version."

    db.flush()

    # Check if both Client and Freelancer have approved this version
    all_reviews = (
        db.query(MilestonePlanReview)
        .filter(MilestonePlanReview.plan_id == plan.id)
        .all()
    )
    approved_roles = {r.reviewer_role for r in all_reviews if r.decision == ReviewDecision.APPROVED}

    if MemberRole.CLIENT in approved_roles and MemberRole.FREELANCER in approved_roles:
        plan.status = PlanStatus.AGREED
        logger.info("Milestone Plan v%d on project %s is fully AGREED!", plan.version, project.id)
        # Advance project to ACTIVE if currently in DRAFT
        if project.status == ProjectStatus.DRAFT:
            project.status = ProjectStatus.ACTIVE

        # Record agreement activity and notify members
        try:
            activity_service.record_activity(
                db=db,
                project_id=project.id,
                activity_type="milestone_plan_agreed",
                title=f"Milestone Plan v{plan.version} Agreed & Locked",
                actor_user_id=current_user.id,
                description=f"Both parties agreed to milestone plan v{plan.version} with {len(plan.milestones)} milestone(s). Work may begin.",
            )
            for m in project.members:
                notification_service.create_notification(
                    db=db,
                    user_id=m.user_id,
                    notification_type="milestone_plan_agreed",
                    title="Milestone Plan Agreed!",
                    message=f"Plan v{plan.version} for '{project.title}' is officially agreed and active.",
                    action_url=f"/projects/{project.id}/milestones",
                    project_id=project.id,
                )
        except Exception as exc:
            logger.warning("Could not record plan agreed activity/notification: %s", exc)

    db.commit()
    return _get_loaded_plan(plan.id, db)


def request_plan_revision(
    project_id: uuid.UUID,
    plan_id: uuid.UUID,
    current_user: User,
    comment: str,
    db: Session,
) -> MilestonePlan:
    """Record revision request with user comment, marking plan as revision_requested."""
    project, membership = _verify_project_membership(project_id, current_user, db)
    plan = _get_loaded_plan(plan_id, db)
    if not plan or plan.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone plan not found.",
        )

    if plan.status != PlanStatus.PENDING_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Revisions can only be requested on pending plans. Current status: '{plan.status.value}'.",
        )

    review = (
        db.query(MilestonePlanReview)
        .filter(
            MilestonePlanReview.plan_id == plan.id,
            MilestonePlanReview.reviewer_user_id == current_user.id,
        )
        .first()
    )
    if not review:
        review = MilestonePlanReview(
            plan_id=plan.id,
            reviewer_user_id=current_user.id,
            reviewer_role=membership.role,
            decision=ReviewDecision.CHANGES_REQUESTED,
            comment=comment.strip(),
        )
        db.add(review)
    else:
        review.decision = ReviewDecision.CHANGES_REQUESTED
        review.comment = comment.strip()

    plan.status = PlanStatus.REVISION_REQUESTED
    db.commit()

    # Record revision requested activity and dispatch notification
    try:
        activity_service.record_activity(
            db=db,
            project_id=project.id,
            activity_type="revision_requested",
            title=f"Revision Requested on Plan v{plan.version}",
            actor_user_id=current_user.id,
            description=f"{current_user.full_name} ({membership.role.value}) requested revisions: '{comment.strip()}'",
        )
        for m in project.members:
            if m.user_id != current_user.id:
                notification_service.create_notification(
                    db=db,
                    user_id=m.user_id,
                    notification_type="revision_requested",
                    title="Plan Revisions Requested",
                    message=f"{current_user.full_name} requested revisions on plan v{plan.version}: '{comment.strip()[:80]}'",
                    action_url=f"/projects/{project.id}/milestones",
                    project_id=project.id,
                )
    except Exception as exc:
        logger.warning("Could not record plan revision activity/notification: %s", exc)

    logger.info("Revision requested for plan v%d by %s", plan.version, current_user.email)
    return _get_loaded_plan(plan.id, db)
