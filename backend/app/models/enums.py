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
