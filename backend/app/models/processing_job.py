import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.models.enums import JobStage, JobStatus


class ProcessingJob(Base):
    __tablename__ = "processing_job"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id", ondelete="CASCADE"), nullable=False)
    version_id = Column(UUID(as_uuid=True), ForeignKey("contract_version.id", ondelete="CASCADE"), nullable=False)
    stage = Column(String(50), nullable=False, default=JobStage.UPLOAD.value)
    status = Column(String(50), nullable=False, default=JobStatus.PENDING.value)
    attempt = Column(Integer, nullable=False, default=1)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)