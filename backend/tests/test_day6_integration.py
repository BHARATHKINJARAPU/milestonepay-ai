import uuid
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.main import app
from app.models.enums import (
    AccountType,
    MemberRole,
    MilestonePaymentStatus,
    MilestoneStatus,
    PaymentProvider,
    PaymentStatus,
    PlanStatus,
    ProjectStatus,
)
from app.models.milestone import Milestone
from app.models.milestone_plan import MilestonePlan
from app.models.notification import Notification
from app.models.payment import Payment
from app.models.project import Project
from app.models.project_activity import ProjectActivity
from app.models.project_member import ProjectMember
from app.models.user import User
from app.services.activity_service import activity_service
from app.services.analytics_service import analytics_service
from app.services.notification_service import notification_service

client = TestClient(app)


@pytest.fixture
def db_session():
    """Provide a database session fixture."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_users(db_session: Session):
    """Create test client and freelancer users."""
    uid = uuid.uuid4().hex[:6]
    client_user = User(
        email=f"client_{uid}@test.com",
        password_hash="hashed_pw",
        full_name="Alice Client",
        account_type=AccountType.CLIENT,
        is_active=True,
    )
    freelancer_user = User(
        email=f"freelancer_{uid}@test.com",
        password_hash="hashed_pw",
        full_name="Bob Freelancer",
        account_type=AccountType.FREELANCER,
        is_active=True,
    )
    other_user = User(
        email=f"other_{uid}@test.com",
        password_hash="hashed_pw",
        full_name="Charlie Other",
        account_type=AccountType.CLIENT,
        is_active=True,
    )
    db_session.add_all([client_user, freelancer_user, other_user])
    db_session.commit()
    db_session.refresh(client_user)
    db_session.refresh(freelancer_user)
    db_session.refresh(other_user)
    return client_user, freelancer_user, other_user


@pytest.fixture
def test_project_with_milestones(db_session: Session, test_users):
    """Create a project with both members, an agreed plan, and milestones."""
    client_user, freelancer_user, _ = test_users
    project = Project(
        title="Fintech Mobile App",
        description="Comprehensive fintech application with payments and AI verification.",
        budget_amount=Decimal("3000.00"),
        currency="USD",
        status=ProjectStatus.ACTIVE,
        created_by_id=client_user.id,
    )
    db_session.add(project)
    db_session.flush()

    m_client = ProjectMember(project_id=project.id, user_id=client_user.id, role=MemberRole.CLIENT)
    m_free = ProjectMember(project_id=project.id, user_id=freelancer_user.id, role=MemberRole.FREELANCER)
    db_session.add_all([m_client, m_free])

    plan = MilestonePlan(
        project_id=project.id,
        version=1,
        status=PlanStatus.AGREED,
        project_summary="Plan v1",
        total_amount=Decimal("3000.00"),
        currency="USD",
        created_by_id=client_user.id,
    )
    db_session.add(plan)
    db_session.flush()

    m1 = Milestone(
        plan_id=plan.id,
        sequence_number=1,
        title="Design System & Architecture",
        description="Figma and architecture diagrams",
        deliverables=["Figma file"],
        acceptance_criteria=["Design guidelines complete"],
        estimated_duration_days=7,
        budget_percentage=Decimal("33.33"),
        amount=Decimal("1000.00"),
        currency="USD",
        status=MilestoneStatus.APPROVED,
        payment_status=MilestonePaymentStatus.COMPLETED,
    )
    m2 = Milestone(
        plan_id=plan.id,
        sequence_number=2,
        title="Backend API & Payments",
        description="FastAPI, PostgreSQL and PayPal",
        deliverables=["GitHub repo"],
        acceptance_criteria=["Payments working"],
        estimated_duration_days=10,
        budget_percentage=Decimal("66.67"),
        amount=Decimal("2000.00"),
        currency="USD",
        status=MilestoneStatus.IN_PROGRESS,
        payment_status=MilestonePaymentStatus.UNPAID,
    )
    db_session.add_all([m1, m2])
    db_session.commit()
    db_session.refresh(project)
    db_session.refresh(m1)
    db_session.refresh(m2)
    return project, m1, m2


# -----------------------------------------------------------------------------
# NOTIFICATION TESTS
# -----------------------------------------------------------------------------

def test_notification_creation_and_unread_count(db_session: Session, test_users):
    client_user, _, _ = test_users
    n = notification_service.create_notification(
        db=db_session,
        user_id=client_user.id,
        notification_type="test_event",
        title="Welcome Notification",
        message="This is a test notification message.",
    )
    assert n.id is not None
    assert n.is_read is False

    unread_count = notification_service.get_unread_count(db=db_session, user_id=client_user.id)
    assert unread_count >= 1


def test_notification_read_lifecycle(db_session: Session, test_users):
    client_user, _, _ = test_users
    n = notification_service.create_notification(
        db=db_session,
        user_id=client_user.id,
        notification_type="lifecycle_event",
        title="Test Action",
        message="Please review.",
    )
    # Mark single as read
    updated = notification_service.mark_as_read(db=db_session, notification_id=n.id, user_id=client_user.id)
    assert updated.is_read is True
    assert updated.read_at is not None

    # Mark all as read
    n2 = notification_service.create_notification(
        db=db_session,
        user_id=client_user.id,
        notification_type="lifecycle_event_2",
        title="Second Notice",
        message="Please check again.",
    )
    assert n2.is_read is False
    updated_count = notification_service.mark_all_as_read(db=db_session, user_id=client_user.id)
    assert updated_count >= 1

    unread_after = notification_service.get_unread_count(db=db_session, user_id=client_user.id)
    assert unread_after == 0


def test_notification_isolation_and_delete(db_session: Session, test_users):
    client_user, freelancer_user, _ = test_users
    n = notification_service.create_notification(
        db=db_session,
        user_id=client_user.id,
        notification_type="private_event",
        title="Confidential Alert",
        message="Only client should see this.",
    )

    # Freelancer attempts to mark client notification as read -> 404
    freelancer_token = create_access_token(str(freelancer_user.id))
    r = client.patch(
        f"/api/v1/notifications/{n.id}/read",
        headers={"Authorization": f"Bearer {freelancer_token}"},
    )
    assert r.status_code == 404

    # Client can delete own notification
    client_token = create_access_token(str(client_user.id))
    r_del = client.delete(
        f"/api/v1/notifications/{n.id}",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r_del.status_code == 204


# -----------------------------------------------------------------------------
# PROJECT ACTIVITY TIMELINE TESTS
# -----------------------------------------------------------------------------

def test_project_activity_recording_and_retrieval(db_session: Session, test_users, test_project_with_milestones):
    client_user, freelancer_user, other_user = test_users
    project, _, _ = test_project_with_milestones

    act = activity_service.record_activity(
        db=db_session,
        project_id=project.id,
        activity_type="plan_reviewed",
        title="Milestone Plan Reviewed",
        actor_user_id=client_user.id,
        description="Client reviewed and approved milestone plan v1.",
        metadata={"version": 1},
    )
    assert act.id is not None
    assert act.activity_type == "plan_reviewed"

    # Member (freelancer) retrieves activities -> 200
    freelancer_token = create_access_token(str(freelancer_user.id))
    r = client.get(
        f"/api/v1/projects/{project.id}/activities",
        headers={"Authorization": f"Bearer {freelancer_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert any(a["title"] == "Milestone Plan Reviewed" for a in data["activities"])

    # Non-member attempts to retrieve activities -> 403
    other_token = create_access_token(str(other_user.id))
    r_forbidden = client.get(
        f"/api/v1/projects/{project.id}/activities",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert r_forbidden.status_code == 403


# -----------------------------------------------------------------------------
# DASHBOARD & FINANCIAL ANALYTICS TESTS
# -----------------------------------------------------------------------------

def test_dashboard_analytics_client_and_freelancer(db_session: Session, test_users, test_project_with_milestones):
    client_user, freelancer_user, _ = test_users
    project, m1, m2 = test_project_with_milestones

    # Record 1 real PayPal payment and 1 Mock payment
    pay_paypal = Payment(
        milestone_id=m1.id,
        project_id=project.id,
        client_user_id=client_user.id,
        freelancer_user_id=freelancer_user.id,
        provider=PaymentProvider.PAYPAL,
        provider_order_id=f"PP-ORD-{uuid.uuid4().hex[:8]}",
        provider_capture_id=f"PP-CAP-{uuid.uuid4().hex[:8]}",
        amount=Decimal("1000.00"),
        currency="USD",
        status=PaymentStatus.COMPLETED,
        idempotency_key=f"pay-pp-{uuid.uuid4().hex[:8]}",
        provider_metadata={"provider": "paypal"},
    )
    pay_mock = Payment(
        milestone_id=m2.id,
        project_id=project.id,
        client_user_id=client_user.id,
        freelancer_user_id=freelancer_user.id,
        provider=PaymentProvider.MOCK,
        provider_order_id=f"MOCK-ORD-{uuid.uuid4().hex[:8]}",
        provider_capture_id=f"MOCK-CAP-{uuid.uuid4().hex[:8]}",
        amount=Decimal("500.00"),
        currency="USD",
        status=PaymentStatus.COMPLETED,
        idempotency_key=f"pay-mock-{uuid.uuid4().hex[:8]}",
        provider_metadata={"provider": "mock"},
    )
    db_session.add_all([pay_paypal, pay_mock])
    db_session.commit()

    # Query Client Dashboard Analytics
    client_token = create_access_token(str(client_user.id))
    r_client = client.get(
        "/api/v1/analytics/dashboard",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r_client.status_code == 200
    c_data = r_client.json()
    assert c_data["role"] == "client"
    assert c_data["projects"]["total"] >= 1
    assert c_data["milestones"]["total"] >= 2

    # Verify separation of PayPal and Mock payments
    payments_summary = c_data["payments"]
    assert any(p["currency"] == "USD" and p["amount"] == 1000.0 for p in payments_summary["completed_paypal_by_currency"])
    assert any(p["currency"] == "USD" and p["amount"] == 500.0 for p in payments_summary["completed_mock_by_currency"])

    # Query Freelancer Dashboard Analytics
    freelancer_token = create_access_token(str(freelancer_user.id))
    r_free = client.get(
        "/api/v1/analytics/dashboard",
        headers={"Authorization": f"Bearer {freelancer_token}"},
    )
    assert r_free.status_code == 200
    f_data = r_free.json()
    assert f_data["role"] == "freelancer"
    assert f_data["projects"]["total"] >= 1


def test_payment_analytics_and_trends(test_users, test_project_with_milestones):
    client_user, _, _ = test_users
    client_token = create_access_token(str(client_user.id))

    r = client.get(
        "/api/v1/analytics/payments",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "payments_summary" in data
    assert "trends" in data


def test_project_ai_summary_endpoint(test_users, test_project_with_milestones):
    client_user, _, other_user = test_users
    project, _, _ = test_project_with_milestones

    # Authorized member gets AI or fallback summary
    client_token = create_access_token(str(client_user.id))
    r = client.get(
        f"/api/v1/projects/{project.id}/ai-summary",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200
    summary = r.json()
    assert summary["project_id"] == str(project.id)
    assert "executive_summary" in summary
    assert "progress_assessment" in summary
    assert len(summary["key_accomplishments"]) >= 1

    # Non-member gets 403 Forbidden
    other_token = create_access_token(str(other_user.id))
    r_forbidden = client.get(
        f"/api/v1/projects/{project.id}/ai-summary",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert r_forbidden.status_code == 403
