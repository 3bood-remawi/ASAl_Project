import hashlib
from typing import Any
from uuid import uuid4

from fastapi import UploadFile

from app.core.cosmos import get_contracts_container
from app.documents.enums import ContractStatus, JobStage, JobStatus, ProcessingStatus
from app.documents.shapes import ContractDocument, JobDocument, VersionDocument
from app.storage import build_key, get_storage

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
PDF_MAGIC = b"%PDF-"
CHUNK_SIZE = 1024 * 1024


class UploadRejected(Exception):
    """File did not pass validation."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def inspect_upload(upload: UploadFile) -> tuple[str, int]:
    """Hash and check the file in one pass. Returns (sha256 hex, size in bytes)."""
    digest = hashlib.sha256()
    head = b""
    size = 0

    upload.file.seek(0)
    while chunk := upload.file.read(CHUNK_SIZE):
        if len(head) < len(PDF_MAGIC):
            head = (head + chunk)[: len(PDF_MAGIC)]
        size += len(chunk)
        if size > MAX_UPLOAD_BYTES:
            raise UploadRejected(f"File must be a PDF under {MAX_UPLOAD_BYTES // (1024 * 1024)} MB", 413)
        digest.update(chunk)

    if size == 0:
        raise UploadRejected("File is empty")
    if head != PDF_MAGIC:
        # a name ending in .pdf proves nothing
        raise UploadRejected("File must be a PDF")

    upload.file.seek(0)
    return digest.hexdigest(), size


def contract_name(filename: str | None) -> str:
    name = (filename or "").replace("\\", "/").rsplit("/", 1)[-1]
    stem = name.rsplit(".", 1)[0] if "." in name else name
    return (stem.strip() or "Untitled contract")[:255]


def store_upload(
    user: dict[str, Any],
    upload: UploadFile,
    file_hash: str,
    size: int,
) -> tuple[ContractDocument, VersionDocument, JobDocument]:
    organization_id = user["organizationId"]
    contract_id = str(uuid4())
    version_id = str(uuid4())
    filename = upload.filename or "upload.pdf"
    key = build_key(organization_id, contract_id, version_id, filename)

    contract = ContractDocument(
        id=contract_id,
        organization_id=organization_id,
        name=contract_name(filename),
        status=ContractStatus.UPLOADED,
        created_by=user["id"],
    )
    version = VersionDocument(
        id=version_id,
        organization_id=organization_id,
        contract_id=contract_id,
        file_name=filename,
        file_path=key,
        file_type="application/pdf",
        file_size_bytes=size,
        file_hash=file_hash,
        processing_status=ProcessingStatus.PENDING,
        uploaded_by=user["id"],
    )
    job = JobDocument(
        id=str(uuid4()),
        organization_id=organization_id,
        version_id=version_id,
        stage=JobStage.UPLOAD,
        status=JobStatus.PENDING,
    )

    container = get_contracts_container()
    # one batch, so a contract can never exist without its version and job
    container.execute_item_batch(
        batch_operations=[
            ("create", (contract.to_item(),)),
            ("create", (version.to_item(),)),
            ("create", (job.to_item(),)),
        ],
        partition_key=organization_id,
    )

    try:
        get_storage().save(key, upload.file)
    except Exception as exc:
        # the batch is already committed, so say the job failed rather than leave
        # it pending against a file that was never written
        job.status = JobStatus.FAILED
        job.error_message = "The uploaded file could not be stored."
        container.upsert_item(job.to_item())
        raise UploadRejected("The uploaded file could not be stored.", 500) from exc

    return contract, version, job
