import logging

from app.core.cosmos import get_contracts_container
from app.data_access.contracts import get_job_for_version, get_version
from app.documents.enums import JobStage, ProcessingStatus
from app.documents.shapes import JobDocument, VersionDocument
from app.services import job_tracking
from app.services.chunking import chunk_text, save_chunks
from app.services.embedding import embed_texts
from app.services.text_extraction import (
    CorruptPdfError,
    EncryptedPdfError,
    ExtractionResult,
    NoTextLayerError,
    extract_text,
)
from app.storage import ObjectNotFoundError, get_storage

logger = logging.getLogger(__name__)

SCANNED_PDF_MESSAGE = "This looks like a scanned PDF. Text extraction is not supported yet."
ENCRYPTED_PDF_MESSAGE = "This PDF is password protected, so it cannot be read."
CORRUPT_PDF_MESSAGE = "This PDF could not be read. It may be damaged."
MISSING_FILE_MESSAGE = "The uploaded file could not be found in storage."
UNEXPECTED_MESSAGE = "Processing failed unexpectedly. Please try again or contact support."

# a bad PDF is the user's problem and needs a plain message, anything else is ours
USER_FACING_ERRORS = {
    NoTextLayerError: SCANNED_PDF_MESSAGE,
    EncryptedPdfError: ENCRYPTED_PDF_MESSAGE,
    CorruptPdfError: CORRUPT_PDF_MESSAGE,
    ObjectNotFoundError: MISSING_FILE_MESSAGE,
}


def process_version(organization_id: str, version_id: str) -> None:
    """Read the stored file and save its text on the version document."""
    version = get_version(organization_id, version_id)
    job = get_job_for_version(organization_id, version_id)
    if version is None or job is None:
        logger.warning("nothing to process for version %s", version_id)
        return

    try:
        _run(version, job)
    except Exception as exc:
        logger.exception("processing failed for version %s", version_id)
        job_tracking.fail(job, message_for(exc))
        _save_version(version, ProcessingStatus.FAILED)


def _run(version: VersionDocument, job: JobDocument) -> None:
    job_tracking.start(job, JobStage.EXTRACTION)
    _save_version(version, ProcessingStatus.EXTRACTING)

    result = _extract(version)
    version.full_text = result.text
    version.page_count = result.page_count
    version.language = result.language

    job_tracking.start(job, JobStage.EMBEDDING)
    _chunk_and_embed(version, result)

    _save_version(version, ProcessingStatus.DONE)
    job_tracking.succeed(job)


def _chunk_and_embed(version: VersionDocument, result: ExtractionResult) -> None:
    """Splits the extracted text into chunks and saves each with its embedding,
    so the ask endpoint has something to search once processing finishes."""
    chunks = chunk_text(result, version.id)
    embeddings = embed_texts([chunk.text for chunk in chunks])
    save_chunks(chunks, version.organization_id, embeddings=embeddings)


def _extract(version: VersionDocument) -> ExtractionResult:
    with get_storage().open(version.file_path) as f:
        return extract_text(f)


def _save_version(version: VersionDocument, status: ProcessingStatus) -> None:
    version.processing_status = status
    get_contracts_container().upsert_item(version.to_item())


def message_for(exc: Exception) -> str:
    for error_type, message in USER_FACING_ERRORS.items():
        if isinstance(exc, error_type):
            return message
    return UNEXPECTED_MESSAGE
