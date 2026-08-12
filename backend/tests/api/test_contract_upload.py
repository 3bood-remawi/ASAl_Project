from io import BytesIO
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import app.api.routes.contracts as routes
from app.api.deps import get_current_user
from app.main import app
from app.services import upload as upload_service

SAMPLE_PDF = Path(__file__).resolve().parents[1] / "fixtures" / "sample.pdf"
ORG = "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def user():
    return {"id": "demo-editor", "organizationId": ORG, "email": "editor@demo.local", "role": "editor"}


@pytest.fixture
def client(user):
    def _client(duplicate=None):
        app.dependency_overrides[get_current_user] = lambda: user
        routes.get_version_by_hash = lambda org, file_hash: duplicate
        return TestClient(app)

    original = routes.get_version_by_hash
    yield _client
    routes.get_version_by_hash = original
    app.dependency_overrides.clear()


def post(client, data: bytes, filename: str = "contract.pdf"):
    return client.post("/api/contracts/", files={"file": (filename, BytesIO(data), "application/pdf")})


def test_rejects_a_non_pdf(client):
    response = post(client(), b"GIF89a not a pdf")

    assert response.status_code == 400
    assert response.json()["detail"] == "File must be a PDF"


def test_rejects_an_empty_file(client):
    response = post(client(), b"")

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_rejects_an_oversized_file(client, monkeypatch):
    monkeypatch.setattr(upload_service, "MAX_UPLOAD_BYTES", 512)

    response = post(client(), b"%PDF-" + b"x" * 1024)

    assert response.status_code == 413
    assert "PDF under" in response.json()["detail"]


def test_reports_a_duplicate_and_points_at_the_existing_contract(client):
    existing = {"id": str(uuid4()), "contractId": str(uuid4()), "organizationId": ORG}

    response = post(client(duplicate=existing), SAMPLE_PDF.read_bytes())

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["contract_id"] == existing["contractId"]
    assert detail["version_id"] == existing["id"]
    assert detail["message"]
