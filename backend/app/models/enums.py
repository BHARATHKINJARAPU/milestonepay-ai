import enum


class AccountType(str, enum.Enum):
    FREELANCER = "freelancer"
    CLIENT = "client"


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MemberRole(str, enum.Enum):
    FREELANCER = "freelancer"
    CLIENT = "client"


class PlanStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    REVISION_REQUESTED = "revision_requested"
    AGREED = "agreed"


class PlanGenerationSource(str, enum.Enum):
    AI = "ai"
    MANUAL = "manual"


class ReviewDecision(str, enum.Enum):
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"


class MilestoneStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    REVISION_REQUESTED = "revision_requested"
    APPROVED = "approved"


class SubmissionStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REVISION_REQUESTED = "revision_requested"
    APPROVED = "approved"


class AIReviewStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ClientSubmissionDecision(str, enum.Enum):
    APPROVED = "approved"
    REVISION_REQUESTED = "revision_requested"


class CriterionEvaluationStatus(str, enum.Enum):
    MET = "met"
    PARTIALLY_MET = "partially_met"
    NOT_DEMONSTRATED = "not_demonstrated"
    UNABLE_TO_ASSESS = "unable_to_assess"


class PaymentProvider(str, enum.Enum):
    MOCK = "mock"
    PAYPAL = "paypal"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    ORDER_CREATED = "order_created"
    PAYER_APPROVED = "payer_approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentEventSource(str, enum.Enum):
    MOCK = "mock"
    PAYPAL_API = "paypal_api"
    PAYPAL_WEBHOOK = "paypal_webhook"


class WebhookProcessingStatus(str, enum.Enum):
    RECEIVED = "received"
    VERIFIED = "verified"
    PROCESSED = "processed"
    FAILED = "failed"


class MilestonePaymentStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PENDING = "pending"
    COMPLETED = "completed"



