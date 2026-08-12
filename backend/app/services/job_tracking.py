from app.core.cosmos import get_contracts_container
from app.documents.enums import JobStage, JobStatus
from app.documents.shapes import JobDocument, utc_now


def _save(job: JobDocument) -> None:
    get_contracts_container().upsert_item(job.to_item())


def start(job: JobDocument, stage: JobStage) -> None:
    job.stage = stage
    job.status = JobStatus.RUNNING
    job.error_message = None
    # a retry keeps the time the work first began
    job.started_at = job.started_at or utc_now()
    job.finished_at = None
    _save(job)


def succeed(job: JobDocument) -> None:
    job.status = JobStatus.SUCCEEDED
    job.error_message = None
    job.finished_at = utc_now()
    _save(job)


def fail(job: JobDocument, reason: str) -> None:
    job.status = JobStatus.FAILED
    job.error_message = reason
    job.finished_at = utc_now()
    _save(job)
