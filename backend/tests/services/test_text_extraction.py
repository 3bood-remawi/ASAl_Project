"""Tests for app.services.text_extraction."""

from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
from pdfminer.pdfdocument import PDFPasswordIncorrect
from pdfplumber.utils.exceptions import PdfminerException

from app.services.text_extraction import (
    CorruptPdfError,
    EncryptedPdfError,
    ExtractionResult,
    NoTextLayerError,
    extract_text,
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def _build_pdf(objects: list[bytes]) -> bytes:
    """Hand-assembles a minimal, syntactically valid PDF from raw object bodies,
    computing correct xref byte offsets so pdfminer's strict parser accepts it
    without falling back to recovery mode."""
    buf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj_body in enumerate(objects, start=1):
        offsets.append(len(buf))
        buf += f"{i} 0 obj\n".encode() + obj_body + b"\nendobj\n"
    xref_offset = len(buf)
    n = len(objects) + 1
    buf += f"xref\n0 {n}\n".encode()
    buf += b"0000000000 65535 f \n"
    for off in offsets:
        buf += f"{off:010d} 00000 n \n".encode()
    buf += f"trailer\n<< /Size {n} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode()
    return bytes(buf)


def _zero_page_pdf() -> bytes:
    return _build_pdf(
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [] /Count 0 >>",
        ]
    )


def _no_text_layer_pdf() -> bytes:
    return _build_pdf(
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << >> >>",
            b"<< /Length 0 >>\nstream\nendstream",
        ]
    )


def _stream_obj(content: bytes) -> bytes:
    return f"<< /Length {len(content)} >>\nstream\n".encode() + content + b"\nendstream"


def _mixed_text_pdf() -> bytes:
    """Page 1 has real text, page 2 is a stand-in for a scanned page (no text)."""
    page1_content = b"BT /F1 12 Tf 72 700 Td (Payment terms: net 30 days.) Tj ET"
    return _build_pdf(
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 5 0 R "
            b"/Resources << /Font << /F1 6 0 R >> >> >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 7 0 R /Resources << >> >>",
            _stream_obj(page1_content),
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            _stream_obj(b""),
        ]
    )


def test_extract_text_happy_path():
    with open(FIXTURES / "sample.pdf", "rb") as f:
        result = extract_text(f)

    assert isinstance(result, ExtractionResult)
    assert result.page_count == 3
    assert result.language == "en"
    assert result.text.startswith("Legal Note:")
    assert len(result.pages) == 3


def test_char_offsets_match_full_text():
    """Every block's char_start/char_end must index back into the canonical
    ExtractionResult.text exactly, on every page — this is what task 852
    (chunking) relies on for citations."""
    with open(FIXTURES / "sample.pdf", "rb") as f:
        result = extract_text(f)

    for page in result.pages:
        for block in page.blocks:
            assert result.text[block.char_start : block.char_end] == block.text


def test_zero_page_pdf_raises_corrupt_error():
    with pytest.raises(CorruptPdfError):
        extract_text(BytesIO(_zero_page_pdf()))


def test_no_text_layer_raises_no_text_layer_error():
    with pytest.raises(NoTextLayerError):
        extract_text(BytesIO(_no_text_layer_pdf()))


def test_mixed_pdf_with_one_scanned_page_raises_no_text_layer_error():
    """A page with no extractable text must not be silently dropped just
    because an earlier page in the same document had text."""
    with pytest.raises(NoTextLayerError):
        extract_text(BytesIO(_mixed_text_pdf()))


def test_garbage_bytes_raise_corrupt_error():
    with pytest.raises(CorruptPdfError):
        extract_text(BytesIO(b"this is not a pdf file at all"))


def test_encrypted_pdf_raises_encrypted_error():
    with patch(
        "app.services.text_extraction.pdfplumber.open",
        side_effect=PdfminerException(PDFPasswordIncorrect("bad password")),
    ):
        with pytest.raises(EncryptedPdfError):
            extract_text(BytesIO(b"irrelevant"))
