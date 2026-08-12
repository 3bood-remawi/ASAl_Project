from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.documents.enums import (
    ContractStatus,
    DocumentType,
    JobStage,
    JobStatus,
    ProcessingStatus,
    UserRole,
)

CONTRACTS_CONTAINER = "contracts"
CHUNKS_CONTAINER = "chunks"
PARTITION_KEY_PATH = "/organizationId"

# all-MiniLM-L6-v2, agreed with Zaina and Nagham
EMBEDDING_DIM = 384


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Document(BaseModel):
    """What every document carries. organizationId is the partition key."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    id: str
    type: DocumentType
    organization_id: str

    def to_item(self) -> dict[str, Any]:
        """The dict to hand to Cosmos. camelCase, JSON-safe."""
        return self.model_dump(mode="json", by_alias=True)


class OrganizationDocument(Document):
    type: DocumentType = DocumentType.ORGANIZATION
    name: str
    created_at: datetime = Field(default_factory=utc_now)


class UserDocument(Document):
    type: DocumentType = DocumentType.USER
    external_id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=utc_now)


class ContractDocument(Document):
    type: DocumentType = DocumentType.CONTRACT
    name: str
    status: ContractStatus = ContractStatus.UPLOADED
    created_by: str
    created_at: datetime = Field(default_factory=utc_now)


class VersionDocument(Document):
    type: DocumentType = DocumentType.VERSION
    contract_id: str
    version_number: int = 1
    file_name: str
    file_path: str
    file_type: str | None = None
    file_size_bytes: int | None = None
    file_hash: str | None = None
    page_count: int | None = None
    language: str = "en"
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    # extraction writes this, the contract page and citations read it
    full_text: str | None = None
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=utc_now)


class JobDocument(Document):
    type: DocumentType = DocumentType.JOB
    version_id: str
    stage: JobStage = JobStage.UPLOAD
    status: JobStatus = JobStatus.PENDING
    attempt: int = 1
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class ChunkDocument(Document):
    type: DocumentType = DocumentType.CHUNK
    version_id: str
    chunk_order: int
    text: str
    page_number: int | None = None
    bounding_boxes: list[dict[str, float]] = Field(default_factory=list)
    char_start: int | None = None
    char_end: int | None = None
    language: str | None = None
    heading_path: str | None = None
    token_count: int | None = None
    embedding: list[float] | None = None
    created_at: datetime = Field(default_factory=utc_now)
