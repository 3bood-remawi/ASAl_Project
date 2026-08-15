from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.documents.enums import JobStage, JobStatus


class UploadStatus(BaseModel):
    job_id: UUID
    version_id: UUID
    stage: JobStage
    status: JobStatus
    error_message: str | None = None
    last_changed_at: datetime
