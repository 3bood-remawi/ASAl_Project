""" Splits a contract version's extracted text into ~800-character chunks
with a small overlap, using paragraph and sentence boundaries where possible.
Each chunk keeps its page number and is identified by version ID and chunk order."""

import re
from dataclasses import dataclass

from app.core.cosmos import get_chunks_container
from app.documents.shapes import ChunkDocument
from app.services.text_extraction import ExtractionResult

CHUNK_SIZE = 800
OVERLAP = 100

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")

@dataclass(frozen=True)
class Chunk:
    id: str
    version_id: str
    page_number: int
    chunk_order: int
    text: str

def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]

def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_END.split(text) if s.strip()]

"""Splits an oversized sentence by words so each piece stays within CHUNK_SIZE without cutting words."""
def _split_words(text: str, size: int) -> list[str]:
    pieces: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip() if current else word
        if current and len(candidate) > size:
            pieces.append(current)
            current = word
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces


"""Returns the page number for each text block in document order."""
def _flatten_pages(extraction: ExtractionResult) -> list[int]:
    return [page.page_number for page in extraction.pages for _ in page.blocks]


def _units_with_pages(extraction: ExtractionResult) -> list[tuple[str, int]]:
    paragraphs = _split_paragraphs(extraction.text)
    pages = _flatten_pages(extraction)

    units: list[tuple[str, int]] = []
    for paragraph, page_number in zip(paragraphs, pages, strict=True):
        if len(paragraph) <= CHUNK_SIZE:
            units.append((paragraph, page_number))
            continue
        for sentence in _split_sentences(paragraph):
            if len(sentence) <= CHUNK_SIZE:
                units.append((sentence, page_number))
            else:
                units.extend((piece, page_number) for piece in _split_words(sentence, CHUNK_SIZE))
    return units


"""Carries trailing units from one chunk to the next within the overlap limit."""
def _carry_overlap(
    chunk: list[tuple[str, int]], overlap: int
) -> tuple[list[tuple[str, int]], int]:
    carried: list[tuple[str, int]] = []
    carried_len = 0
    for unit in reversed(chunk):
        unit_len = len(unit[0])
        sep = 1 if carried else 0
        if carried_len + sep + unit_len > overlap:
            break
        carried.insert(0, unit)
        carried_len += sep + unit_len
    return carried, carried_len

"""Groups text units into size-limited chunks with overlap and tracks where new content starts."""
def _pack_units(
    units: list[tuple[str, int]], size: int, overlap: int
) -> list[tuple[list[tuple[str, int]], int]]:
    chunks: list[tuple[list[tuple[str, int]], int]] = []
    current: list[tuple[str, int]] = []
    current_len = 0
    new_content_start = 0

    for text, page_number in units:
        sep = 1 if current else 0
        if current and current_len + sep + len(text) > size:
            chunks.append((current, new_content_start))
            # Reduce the carried overlap when needed so the overlap plus the new unit stays within the chunk size.
            available_for_overlap = max(0, size - len(text) - 1)
            current, current_len = _carry_overlap(current, min(overlap, available_for_overlap))
            new_content_start = len(current)
            sep = 1 if current else 0

        current.append((text, page_number))
        current_len += sep + len(text)

    if current:
        chunks.append((current, new_content_start))
    return chunks


def chunk_text(extraction: ExtractionResult, version_id: str) -> list[Chunk]:
    units = _units_with_pages(extraction)
    packed = _pack_units(units, CHUNK_SIZE, OVERLAP)

    chunks: list[Chunk] = []
    for chunk_order, (group, new_content_start) in enumerate(packed):
        # Use the first non-overlap unit for page_number to avoid assigning the previous page.
        page_index = min(new_content_start, len(group) - 1)
        chunks.append(
            Chunk(
                id=f"{version_id}-{chunk_order}",
                version_id=version_id,
                page_number=group[page_index][1],
                chunk_order=chunk_order,
                text=" ".join(text for text, _ in group),
            )
        )
    return chunks

"""Saves each chunk as a ChunkDocument using upsert to avoid duplicates on reruns."""
def save_chunks(chunks: list[Chunk], organization_id: str) -> None:
    container = get_chunks_container()
    for chunk in chunks:
        document = ChunkDocument(
            id=chunk.id,
            organization_id=organization_id,
            version_id=chunk.version_id,
            chunk_order=chunk.chunk_order,
            text=chunk.text,
            page_number=chunk.page_number,
        )
        container.upsert_item(document.to_item())