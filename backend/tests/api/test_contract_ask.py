import pytest
from fastapi.testclient import TestClient

import app.api.routes.contracts as routes
from app.main import app
from app.schemas.ask import AskResponse, Passage
from app.services.ask import ContractNotReadyError

CONTRACT_ID = "contract-1"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def stub_contract_lookup(monkeypatch):
    monkeypatch.setattr(routes, "get_contract_by_id", lambda org, contract_id: {"id": contract_id})
    yield


def ask(client, question="what is the termination notice period?"):
    return client.post(f"/api/contracts/{CONTRACT_ID}/ask", json={"question": question})


def test_404_when_the_contract_does_not_exist(client, monkeypatch):
    monkeypatch.setattr(routes, "get_contract_by_id", lambda org, contract_id: None)

    response = ask(client)

    assert response.status_code == 404


def test_409_when_the_contract_has_not_finished_processing(client, monkeypatch):
    def raise_not_ready(org, contract_id, question):
        raise ContractNotReadyError

    monkeypatch.setattr(routes, "ask_contract", raise_not_ready)

    response = ask(client)

    assert response.status_code == 409


def test_400_when_the_question_is_blank(client):
    response = ask(client, question="")

    assert response.status_code == 422


def test_returns_the_passages_from_the_service(client, monkeypatch):
    passage = Passage(
        chunk_id="chunk-1",
        text="Either party may terminate with 30 days notice.",
        page_number=4,
        score=0.87,
    )
    expected = AskResponse(passages=[passage])
    monkeypatch.setattr(routes, "ask_contract", lambda org, contract_id, question: expected)

    response = ask(client)

    assert response.status_code == 200
    body = response.json()
    assert body["passages"][0]["chunk_id"] == "chunk-1"
    assert body["passages"][0]["page_number"] == 4
    assert body["message"] is None


def test_returns_an_empty_list_and_message_when_nothing_matches(client, monkeypatch):
    no_match_message = "Couldn't find any passages in this contract that closely match your question."
    expected = AskResponse(passages=[], message=no_match_message)
    monkeypatch.setattr(routes, "ask_contract", lambda org, contract_id, question: expected)

    response = ask(client)

    assert response.status_code == 200
    body = response.json()
    assert body["passages"] == []
    assert body["message"]
