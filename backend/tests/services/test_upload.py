import hashlib
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile

from app.services import upload as upload_service
from app.services.upload import UploadRejected, contract_name, inspect_upload

SAMPLE_PDF = Path(__file__).resolve().parents[1] / "fixtures" / "sample.pdf"


def make_upload(data: bytes, filename: str = "contract.pdf") -> UploadFile:
    return UploadFile(file=BytesIO(data), filename=filename)


def test_hashes_and_sizes_a_real_pdf():
    data = SAMPLE_PDF.read_bytes()

    file_hash, size = inspect_upload(make_upload(data))

    assert file_hash == hashlib.sha256(data).hexdigest()
    assert size == len(data)


def test_rewinds_so_the_file_can_be_stored_afterwards():
    data = SAMPLE_PDF.read_bytes()
    upload = make_upload(data)

    inspect_upload(upload)

    assert upload.file.read() == data


def test_rejects_an_empty_file():
    with pytest.raises(UploadRejected) as exc:
        inspect_upload(make_upload(b""))

    assert exc.value.status_code == 400
    assert "empty" in exc.value.message.lower()


def test_rejects_a_non_pdf_named_pdf():
    with pytest.raises(UploadRejected) as exc:
        inspect_upload(make_upload(b"GIF89a not really a pdf", "invoice.pdf"))

    assert exc.value.status_code == 400
    assert exc.value.message == "File must be a PDF"


def test_rejects_a_file_shorter_than_the_pdf_header():
    with pytest.raises(UploadRejected):
        inspect_upload(make_upload(b"%PD"))


def test_rejects_a_file_over_the_size_limit(monkeypatch):
    monkeypatch.setattr(upload_service, "MAX_UPLOAD_BYTES", 1024)

    with pytest.raises(UploadRejected) as exc:
        inspect_upload(make_upload(b"%PDF-" + b"x" * 2048))

    assert exc.value.status_code == 413


def test_size_limit_is_not_off_by_one(monkeypatch):
    monkeypatch.setattr(upload_service, "MAX_UPLOAD_BYTES", 10)

    _, size = inspect_upload(make_upload(b"%PDF-12345"))

    assert size == 10


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("Nexa Services Agreement.pdf", "Nexa Services Agreement"),
        ("no-extension", "no-extension"),
        ("C:\\Users\\me\\lease.pdf", "lease"),
        ("../../etc/passwd", "passwd"),
        (None, "Untitled contract"),
        ("   .pdf", "Untitled contract"),
    ],
)
def test_contract_name_from_filename(filename, expected):
    assert contract_name(filename) == expected
