import enum


class DocumentType(str, enum.Enum):
    ORGANIZATION = "organization"
    USER = "user"
    CONTRACT = "contract"
    VERSION = "version"
    JOB = "job"
    CHUNK = "chunk"


class UserRole(str, enum.Enum):
    EDITOR = "editor"
    APPROVER = "approver"


class ContractStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    ARCHIVED = "archived"


class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    EXTRACTING = "extracting"
    DONE = "done"
    FAILED = "failed"


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CORRECTED = "corrected"
    REJECTED = "rejected"


class FindingType(str, enum.Enum):
    RISKY_LANGUAGE = "risky_language"
    MISSING_CLAUSE = "missing_clause"
    MISSING_PROTECTION = "missing_protection"
    UNFAIR_LANGUAGE = "unfair_language"


class Severity(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FindingStatus(str, enum.Enum):
    OPEN = "open"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    OVERRIDDEN = "overridden"


class DecisionType(str, enum.Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    OVERRIDE = "override"


class ReminderStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    SENT = "sent"
    FAILED = "failed"


class SenderType(str, enum.Enum):
    USER = "user"
    AI = "ai"


class CitationTargetType(str, enum.Enum):
    CHUNK = "chunk"
    CLAUSE = "clause"


class JobStage(str, enum.Enum):
    UPLOAD = "upload"
    EXTRACTION = "extraction"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RETRYING = "retrying"
