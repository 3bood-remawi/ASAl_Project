from io import BytesIO
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import app.api.routes.contracts as routes
from app.api.deps import get_current_user
from app.documents.shapes import ContractDocument, JobDocument, VersionDocument
from app.main import app

SAMPLE_PDF = Path(__file__).resolve().parents[1] / "fixtures" / "sample.pdf"
ORG = "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def stored():
    contract_id, version_id = str(uuid4()), str(uuid4())
    contract = ContractDocument(id=contract_id, organization_id=ORG, name="Sample", created_by="demo-editor")
    version = VersionDocument(id=version_id, organization_id=ORG, contract_id=contract_id,
                              file_name="sample.pdf", file_path="k", file_size_bytes=1234,
                              uploaded_by="demo-editor")
    job = JobDocument(id=str(uuid4()), organization_id=ORG, version_id=version_id)
    return contract, version, job


@pytest.fixture
def client(stored):
    """Nothing reaches Cosmos: the lookup, the write and the pipeline are all stubbed."""
    started = []

    app.dependency_overrides[get_current_user] = lambda: {"id": "demo-editor", "organizationId": ORG}
    original_lookup = routes.get_version_by_hash
    original_store = routes.store_upload
    original_process = routes.process_version

    routes.get_version_by_hash = lambda org, file_hash: None
    routes.store_upload = lambda user, upload, file_hash, size: stored
    routes.process_version = lambda org, version_id: started.append((org, version_id))

    # no context manager: that would run the startup hook, which needs Cosmos
    yield TestClient(app), started

    routes.get_version_by_hash = original_lookup
    routes.store_upload = original_store
    routes.process_version = original_process
    app.dependency_overrides.clear()


def post(test_client, data: bytes, filename: str = "contract.pdf"):
    return test_client.post("/api/contracts/", files={"file": (filename, BytesIO(data), "application/pdf")})


def test_a_successful_upload_queues_processing(client, stored):
    test_client, started = client

    response = post(test_client, SAMPLE_PDF.read_bytes())

    assert response.status_code == 201
    assert started == [(ORG, stored[1].id)]


def test_processing_is_queued_for_the_version_that_was_stored(client):
    test_client, started = client

    body = post(test_client, SAMPLE_PDF.read_bytes()).json()

    assert started[0][1] == body["version_id"]


def test_a_rejected_upload_queues_nothing(client):
    test_client, started = client

    response = post(test_client, b"GIF89a not a pdf")

    assert response.status_code == 400
    assert started == []


def test_an_empty_file_queues_nothing(client):
    test_client, started = client

    assert post(test_client, b"").status_code == 400
    assert started == []
