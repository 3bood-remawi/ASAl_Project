import pytest

from app.documents.enums import ProcessingStatus
from app.services import ask as ask_service
from app.services.ask import ContractNotReadyError, ask_contract

ORG = "00000000-0000-0000-0000-000000000001"
CONTRACT_ID = "contract-1"


def a_version(status: ProcessingStatus = ProcessingStatus.DONE) -> dict:
    return {"id": "version-1", "contractId": CONTRACT_ID, "processingStatus": status.value}


def a_row(score: float, chunk_id: str = "chunk-1") -> dict:
    return {"id": chunk_id, "text": "some passage text", "pageNumber": 3, "score": score}


@pytest.fixture(autouse=True)
def stub_embedding(monkeypatch):
    # Tests shouldn't need the real model loaded; only the shape of the vector matters.
    monkeypatch.setattr(ask_service, "embed_text", lambda text: [0.1, 0.2, 0.3])


def test_raises_when_the_contract_has_no_version_yet(monkeypatch):
    monkeypatch.setattr(ask_service, "get_current_version_for_contract", lambda org, cid: None)

    with pytest.raises(ContractNotReadyError):
        ask_contract(ORG, CONTRACT_ID, "what is the term?")


def test_raises_when_the_version_has_not_finished_processing(monkeypatch):
    monkeypatch.setattr(
        ask_service,
        "get_current_version_for_contract",
        lambda org, cid: a_version(ProcessingStatus.EXTRACTING),
    )

    with pytest.raises(ContractNotReadyError):
        ask_contract(ORG, CONTRACT_ID, "what is the term?")


def test_returns_the_top_passages_in_score_order(monkeypatch):
    rows = [a_row(0.91, "chunk-1"), a_row(0.85, "chunk-2"), a_row(0.5, "chunk-3")]
    monkeypatch.setattr(ask_service, "get_current_version_for_contract", lambda org, cid: a_version())
    captured = {}

    def fake_search(org, version_id, embedding, top_k):
        captured["org"] = org
        captured["version_id"] = version_id
        captured["embedding"] = embedding
        captured["top_k"] = top_k
        return rows

    monkeypatch.setattr(ask_service, "search_chunks_by_vector", fake_search)

    result = ask_contract(ORG, CONTRACT_ID, "what is the termination notice period?")

    assert [p.chunk_id for p in result.passages] == ["chunk-1", "chunk-2", "chunk-3"]
    assert result.passages[0].page_number == 3
    assert result.passages[0].score == 0.91
    assert result.message is None
    assert captured["org"] == ORG
    assert captured["version_id"] == "version-1"
    assert captured["top_k"] == 5
    assert captured["embedding"] == [0.1, 0.2, 0.3]


def test_returns_an_empty_list_with_a_message_when_no_chunks_exist(monkeypatch):
    monkeypatch.setattr(ask_service, "get_current_version_for_contract", lambda org, cid: a_version())
    monkeypatch.setattr(ask_service, "search_chunks_by_vector", lambda *a, **kw: [])

    result = ask_contract(ORG, CONTRACT_ID, "what is the term?")

    assert result.passages == []
    assert result.message == ask_service.NO_MATCH_MESSAGE


def test_returns_an_empty_list_with_a_message_when_the_best_score_is_too_low(monkeypatch):
    rows = [a_row(0.1, "chunk-1"), a_row(0.05, "chunk-2")]
    monkeypatch.setattr(ask_service, "get_current_version_for_contract", lambda org, cid: a_version())
    monkeypatch.setattr(ask_service, "search_chunks_by_vector", lambda *a, **kw: rows)

    result = ask_contract(ORG, CONTRACT_ID, "what color is the sky?")

    assert result.passages == []
    assert result.message == ask_service.NO_MATCH_MESSAGE


def test_a_score_right_at_the_threshold_is_accepted(monkeypatch):
    rows = [a_row(ask_service.MIN_SIMILARITY_SCORE, "chunk-1")]
    monkeypatch.setattr(ask_service, "get_current_version_for_contract", lambda org, cid: a_version())
    monkeypatch.setattr(ask_service, "search_chunks_by_vector", lambda *a, **kw: rows)

    result = ask_contract(ORG, CONTRACT_ID, "what is the term?")

    assert len(result.passages) == 1
    assert result.message is None
