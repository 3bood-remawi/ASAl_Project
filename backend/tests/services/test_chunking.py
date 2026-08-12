"""Tests for app.services.chunking."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from app.services.chunking import (
    CHUNK_SIZE,
    Chunk,
    _flatten_pages,
    _pack_units,
    _split_paragraphs,
    _split_sentences,
    chunk_text,
    save_chunks,
)
from app.services.text_extraction import (
    BoundingBox,
    ExtractionResult,
    PageResult,
    TextBlock,
    extract_text,
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "contracts"

_BOX = BoundingBox(x0=0, top=0, x1=0, bottom=0)


def _sentence(i: int) -> str:
    return f"This is sentence number {i} in the test document."

"""Builds a test ExtractionResult with text blocks, pages, and character offsets."""
def _make_extraction(pages: list[list[str]]) -> ExtractionResult:
    text_parts: list[str] = []
    page_results: list[PageResult] = []
    char_offset = 0

    for page_number, lines in enumerate(pages, start=1):
        blocks: list[TextBlock] = []
        for line in lines:
            start = char_offset
            end = start + len(line)
            blocks.append(TextBlock(text=line, bounding_box=_BOX, char_start=start, char_end=end))
            text_parts.append(line)
            char_offset = end + 2  # "\n\n" separator
        page_results.append(PageResult(page_number=page_number, width=612, height=792, blocks=blocks))

    full_text = "\n\n".join(text_parts)
    return ExtractionResult(text=full_text, page_count=len(pages), language="en", pages=page_results)


def test_chunk_text_on_real_contract():
    with open(FIXTURES / "Example-Mutual-Non-Disclosure-Agreement.pdf", "rb") as f:
        result = extract_text(f)

    chunks = chunk_text(result, version_id="version-1")

    assert len(chunks) > 0
    assert [c.chunk_order for c in chunks] == list(range(len(chunks)))
    assert all(1 <= c.page_number <= result.page_count for c in chunks)
    assert all(c.text for c in chunks)
    assert all(len(c.text) <= CHUNK_SIZE for c in chunks)


def test_chunk_ids_are_deterministic_and_sequential():
    extraction = _make_extraction([[_sentence(i) for i in range(30)]])

    chunks = chunk_text(extraction, version_id="version-42")

    assert len(chunks) > 1
    assert [c.chunk_order for c in chunks] == list(range(len(chunks)))
    for chunk in chunks:
        assert chunk.id == f"version-42-{chunk.chunk_order}"

"""Checks that running chunking twice produces identical chunks and IDs."""
def test_chunking_is_idempotent():
    extraction = _make_extraction([[_sentence(i) for i in range(30)]])

    first = chunk_text(extraction, version_id="version-42")
    second = chunk_text(extraction, version_id="version-42")

    assert first == second


def test_short_text_produces_single_chunk():
    extraction = _make_extraction([["A short confidentiality clause under the chunk size limit."]])

    chunks = chunk_text(extraction, version_id="version-1")

    assert len(chunks) == 1
    assert chunks[0].text == "A short confidentiality clause under the chunk size limit."
    assert chunks[0].page_number == 1

"""Checks that oversized text without sentence boundaries is split by words within CHUNK_SIZE."""
def test_oversized_sentence_does_not_exceed_chunk_size():
    long_word_run = " ".join(f"word{i}" for i in range(300))
    extraction = _make_extraction([[long_word_run]])

    chunks = chunk_text(extraction, version_id="version-1")

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.text) <= CHUNK_SIZE


def test_overlap_never_pushes_chunk_over_chunk_size():
    """Checks that overlap is reduced when needed so chunks stay within CHUNK_SIZE."""
    units = [("x" * 90, 1), ("y" * 750, 1)]

    packed = _pack_units(units, size=CHUNK_SIZE, overlap=100)

    for group, _ in packed:
        text = " ".join(t for t, _ in group)
        assert len(text) <= CHUNK_SIZE


def test_long_paragraph_splits_on_sentence_boundaries():
    """Checks that long paragraphs split on sentence boundaries without cutting sentences."""
    sentences = [_sentence(i) for i in range(20)]
    long_line = " ".join(sentences)
    extraction = _make_extraction([[long_line]])

    chunks = chunk_text(extraction, version_id="version-1")

    assert len(chunks) > 1
    for chunk in chunks:
        for piece in _split_sentences(chunk.text):
            assert piece in sentences


def test_consecutive_chunks_overlap():
    extraction = _make_extraction([[_sentence(i) for i in range(30)]])

    chunks = chunk_text(extraction, version_id="version-1")

    assert len(chunks) > 1
    for prev, nxt in zip(chunks, chunks[1:], strict=False):
        first_unit_of_next = _split_sentences(nxt.text)[0]
        assert first_unit_of_next in prev.text


def test_page_number_matches_source_page():
    page1_lines = [_sentence(i) for i in range(20)]
    page2_lines = [_sentence(i) for i in range(20, 35)]
    extraction = _make_extraction([page1_lines, page2_lines])

    chunks = chunk_text(extraction, version_id="version-1")
    page_numbers = [c.page_number for c in chunks]

    assert page_numbers[0] == 1
    assert page_numbers[-1] == 2
    assert page_numbers == sorted(page_numbers)  # never goes backwards

"""Checks that paragraphs stay aligned with their page numbers so chunks get the correct page."""
def test_paragraphs_stay_aligned_with_source_blocks():
    page1_lines = [_sentence(i) for i in range(15)]
    page2_lines = [_sentence(i) for i in range(15, 20)]
    extraction = _make_extraction([page1_lines, page2_lines])

    paragraphs = _split_paragraphs(extraction.text)
    pages = _flatten_pages(extraction)

    assert paragraphs == page1_lines + page2_lines
    assert pages == [1] * len(page1_lines) + [2] * len(page2_lines)

    chunks = chunk_text(extraction, version_id="version-1")
    assert len(chunks) > 1  # must actually span a page boundary to be meaningful

    for i, chunk in enumerate(chunks):
        # Ignore overlap from the previous chunk when finding the first new line.
        prev_text = chunks[i - 1].text if i > 0 else ""
        first_new_line = next(
            line for line in paragraphs if line in chunk.text and line not in prev_text
        )
        expected_page = pages[paragraphs.index(first_new_line)]
        assert chunk.page_number == expected_page


def test_save_chunks_upserts_each_chunk_document():
    chunks = [
        Chunk(id="version-1-0", version_id="version-1", page_number=1, chunk_order=0, text="First chunk."),
        Chunk(id="version-1-1", version_id="version-1", page_number=2, chunk_order=1, text="Second chunk."),
    ]
    mock_container = MagicMock()

    with patch("app.services.chunking.get_chunks_container", return_value=mock_container):
        save_chunks(chunks, organization_id="org-1")

    assert mock_container.upsert_item.call_count == 2
    saved_items = [call.args[0] for call in mock_container.upsert_item.call_args_list]

    assert saved_items[0]["id"] == "version-1-0"
    assert saved_items[0]["type"] == "chunk"
    assert saved_items[0]["organizationId"] == "org-1"
    assert saved_items[0]["versionId"] == "version-1"
    assert saved_items[0]["chunkOrder"] == 0
    assert saved_items[0]["pageNumber"] == 1
    assert saved_items[0]["text"] == "First chunk."

    assert saved_items[1]["id"] == "version-1-1"
    assert saved_items[1]["chunkOrder"] == 1
    assert saved_items[1]["pageNumber"] == 2


def test_save_chunks_uses_upsert_not_create():
    """Uses upsert so saving the same chunk again updates it instead of creating a duplicate."""
    chunks = [Chunk(id="version-1-0", version_id="version-1", page_number=1, chunk_order=0, text="Text.")]
    mock_container = MagicMock()

    with patch("app.services.chunking.get_chunks_container", return_value=mock_container):
        save_chunks(chunks, organization_id="org-1")

    mock_container.upsert_item.assert_called_once()
    mock_container.create_item.assert_not_called()