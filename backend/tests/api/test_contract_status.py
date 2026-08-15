from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import app.api.routes.contracts as routes
from app.main import app

ORG = "00000000-0000-0000-0000-000000000001"
TS = 1786000000  # what Cosmos stamps on the document


def job_document(**overrides):
    document = {
        "id": str(uuid4()),
        "type": "job",
        "organizationId": ORG,
        "versionId": str(uuid4()),
        "stage": "extraction",
        "status": "succeeded",
        "attempt": 1,
        "errorMessage": None,
        "_ts": TS,
    }
    document.update(overrides)
    return document


@pytest.fixture
def client():
    """Both reads are stubbed, so nothing here reaches Cosmos."""
    original_contract = routes.get_contract_by_id
    original_job = routes.get_current_version_job

    def _client(contract=None, job=None):
        routes.get_contract_by_id = lambda org, contract_id: contract
        routes.get_current_version_job = lambda org, contract_id: job
        return TestClient(app)

    yield _client

    routes.get_contract_by_id = original_contract
    routes.get_current_version_job = original_job


def get_status(test_client, contract_id=None):
    return test_client.get(f"/api/contracts/{contract_id or uuid4()}/status")


def test_returns_the_job_for_the_newest_version(client):
    job = job_document()

    body = get_status(client(contract={"id": "c"}, job=job)).json()

    assert body["job_id"] == job["id"]
    assert body["version_id"] == job["versionId"]
    assert body["status"] == "succeeded"
    assert body["stage"] == "extraction"


def test_a_finished_job_reports_no_error(client):
    body = get_status(client(contract={"id": "c"}, job=job_document())).json()

    assert body["error_message"] is None


def test_a_failed_job_carries_its_message(client):
    job = job_document(status="failed", errorMessage="This looks like a scanned PDF.")

    body = get_status(client(contract={"id": "c"}, job=job)).json()

    assert body["status"] == "failed"
    assert body["error_message"] == "This looks like a scanned PDF."


def test_last_changed_comes_from_the_cosmos_timestamp(client):
    body = get_status(client(contract={"id": "c"}, job=job_document())).json()

    expected = datetime.fromtimestamp(TS, tz=timezone.utc)
    assert datetime.fromisoformat(body["last_changed_at"]) == expected


def test_a_pending_job_still_reports_when_it_last_changed(client):
    # nothing has run yet, so startedAt and finishedAt are empty and only _ts can answer
    job = job_document(status="pending", stage="upload")

    body = get_status(client(contract={"id": "c"}, job=job)).json()

    assert body["status"] == "pending"
    assert body["last_changed_at"]


def test_an_unknown_contract_is_a_404(client):
    response = get_status(client(contract=None))

    assert response.status_code == 404
    assert response.json()["detail"] == "Contract not found"


def test_a_contract_with_no_job_is_a_404_that_says_so(client):
    response = get_status(client(contract={"id": "c"}, job=None))

    assert response.status_code == 404
    assert "no processing job" in response.json()["detail"]


def test_a_malformed_contract_id_is_rejected(client):
    response = client(contract={"id": "c"}, job=job_document()).get("/api/contracts/not-a-uuid/status")

    assert response.status_code == 422
