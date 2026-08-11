"""
Text extraction interface for the contract processing pipeline.

Turns an uploaded PDF into structured, cite-able text. Only PDFs that
already contain a text layer are supported — no OCR.

Coordinate system: all BoundingBox values are in PDF points (72 per inch),
measured from the TOP-LEFT corner of the page. The y axis grows DOWNWARD
(top=0 is the top of the page, increasing toward the bottom) — this matches
pdfplumber's convention, but NOT every PDF viewer, so do not assume it
elsewhere without checking.
"""

from dataclasses import dataclass
from typing import BinaryIO

import pdfplumber
from pdfminer.pdfdocument import PDFPasswordIncorrect
from pdfplumber.utils.exceptions import PdfminerException


@dataclass(frozen=True)
class BoundingBox:
    x0: float
    top: float
    x1: float
    bottom: float


@dataclass(frozen=True)
class TextBlock:
    text: str
    bounding_box: BoundingBox
    char_start: int  # offset of this block's text into ExtractionResult.text
    char_end: int  # exclusive


@dataclass(frozen=True)
class PageResult:
    page_number: int
    width: float
    height: float
    blocks: list[TextBlock]


@dataclass(frozen=True)
class ExtractionResult:
    text: str  # canonical full text: every block's text joined with "\n\n"
    page_count: int
    language: str
    pages: list[PageResult]


class ExtractionError(Exception):
    """Base class for all text extraction failures."""


class NoTextLayerError(ExtractionError):
    """Raised when a PDF has no extractable text (likely scanned)."""


class EncryptedPdfError(ExtractionError):
    """Raised when a PDF is password-protected and cannot be read."""


class CorruptPdfError(ExtractionError):
    """Raised when a PDF file is malformed or unreadable."""


def extract_text(f: BinaryIO) -> ExtractionResult:
    try:
        return _extract(f)
    except ExtractionError:
        raise
    except PdfminerException as exc:
        cause = exc.args[0] if exc.args else None
        if isinstance(cause, PDFPasswordIncorrect):
            raise EncryptedPdfError("PDF is password-protected and cannot be read") from exc
        raise CorruptPdfError(f"Failed to read PDF: {cause}") from exc
    except Exception as exc:
        raise CorruptPdfError(f"Failed to read PDF: {exc}") from exc





def _extract(f: BinaryIO) -> ExtractionResult:
    with pdfplumber.open(f) as pdf:
        if len(pdf.pages) == 0:
            raise CorruptPdfError("PDF has zero pages")

        pages: list[PageResult] = []
        text_parts: list[str] = []
        char_offset = 0

        for page_number, page in enumerate(pdf.pages, start=1):
            blocks: list[TextBlock] = []
            for line in page.extract_text_lines():
                text = line["text"]
                start = char_offset
                end = start + len(text)
                blocks.append(
                    TextBlock(
                        text=text,
                        bounding_box=BoundingBox(
                            x0=line["x0"], top=line["top"], x1=line["x1"], bottom=line["bottom"]
                        ),
                        char_start=start,
                        char_end=end,
                    )
                )
                text_parts.append(text)
                char_offset = end + 2  # "\n\n" separator

            if not blocks:
                raise NoTextLayerError(
                    f"Page {page_number} has no extractable text (scanned pages are not supported yet)"
                )

            pages.append(
                PageResult(page_number=page_number, width=page.width, height=page.height, blocks=blocks)
            )

        full_text = "\n\n".join(text_parts)
        return ExtractionResult(text=full_text, page_count=len(pdf.pages), language="en", pages=pages)
