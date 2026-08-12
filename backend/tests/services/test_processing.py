import pytest

from app.documents.enums import JobStage, JobStatus, ProcessingStatus
from app.documents.shapes import JobDocument
from app.services import job_tracking, processing
from app.services.processing import (
    CORRUPT_PDF_MESSAGE,
    ENCRYPTED_PDF_MESSAGE,
    MISSING_FILE_MESSAGE,
    SCANNED_PDF_MESSAGE,
    UNEXPECTED_MESSAGE,
    message_for,
)
from app.services.text_extraction import CorruptPdfError, EncryptedPdfError, NoTextLayerError
from app.storage import ObjectNotFoundError

ORG = "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def job():
    return JobDocument(id="job-1", organization_id=ORG, version_id="version-1")


@pytest.fixture(autouse=True)
def no_cosmos(monkeypatch):
    """Job tracking writes to Cosmos, these tests only care about the document."""
    monkeypatch.setattr(job_tracking, "_save", lambda job: None)


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (NoTextLayerError("page 1 has no text"), SCANNED_PDF_MESSAGE),
        (EncryptedPdfError("password"), ENCRYPTED_PDF_MESSAGE),
        (CorruptPdfError("broken xref"), CORRUPT_PDF_MESSAGE),
        (ObjectNotFoundError("org/contract/version/file.pdf"), MISSING_FILE_MESSAGE),
    ],
)
def test_known_failures_get_a_readable_message(error, expected):
    assert message_for(error) == expected


def test_a_scanned_pdf_says_so_plainly(job):
    job_tracking.fail(job, message_for(NoTextLayerError("no text")))

    assert job.status is JobStatus.FAILED
    assert "scanned PDF" in job.error_message
    assert "NoTextLayerError" not in job.error_message


def test_unknown_failures_do_not_leak_internals():
    message = message_for(ZeroDivisionError("division by zero at line 41"))

    assert message == UNEXPECTED_MESSAGE
    assert "division" not in message


def test_storage_key_is_never_exposed_to_the_user():
    key = "org-1/contract-2/version-3/Very Private Agreement.pdf"

    assert key not in message_for(ObjectNotFoundError(key))


def test_every_extraction_error_is_covered():
    # a new extraction error without a message here would surface as "unexpected"
    from app.services import text_extraction

    subclasses = {
        cls for cls in vars(text_extraction).values()
        if isinstance(cls, type)
        and issubclass(cls, text_extraction.ExtractionError)
        and cls is not text_extraction.ExtractionError
    }

    assert subclasses <= set(processing.USER_FACING_ERRORS)


def test_start_marks_the_job_running_and_stamps_the_time(job):
    job_tracking.start(job, JobStage.EXTRACTION)

    assert job.status is JobStatus.RUNNING
    assert job.stage is JobStage.EXTRACTION
    assert job.started_at is not None
    assert job.finished_at is None


def test_a_retry_keeps_the_original_start_time(job):
    job_tracking.start(job, JobStage.EXTRACTION)
    first_started = job.started_at

    job_tracking.start(job, JobStage.EXTRACTION)

    assert job.started_at == first_started


def test_start_clears_the_error_from_a_previous_attempt(job):
    job.error_message = SCANNED_PDF_MESSAGE

    job_tracking.start(job, JobStage.EXTRACTION)

    assert job.error_message is None


def test_succeed_records_the_finish_time(job):
    job_tracking.succeed(job)

    assert job.status is JobStatus.SUCCEEDED
    assert job.finished_at is not None
    assert job.error_message is None


def test_a_failed_job_is_never_left_looking_unfinished(job):
    job_tracking.start(job, JobStage.EXTRACTION)
    job_tracking.fail(job, CORRUPT_PDF_MESSAGE)

    assert job.status not in {JobStatus.PENDING, JobStatus.RUNNING}
    assert job.finished_at is not None
    assert job.error_message == CORRUPT_PDF_MESSAGE


def test_the_job_document_survives_a_round_trip(job):
    job_tracking.start(job, JobStage.EXTRACTION)

    item = job.to_item()
    restored = JobDocument.model_validate(item)

    assert item["status"] == "running"
    assert item["organizationId"] == ORG
    assert restored.started_at == job.started_at


def test_the_statuses_the_pipeline_uses_exist():
    assert ProcessingStatus.EXTRACTING and ProcessingStatus.DONE and ProcessingStatus.FAILED
