from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

import app.api.routes.contracts as routes
from app.core.dependencies import current_organization_id
from app.main import app

ORG = "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def records():
    contract_id = str(uuid4())
    version_id = str(uuid4())

    contract = {
        "id": contract_id,
        "organizationId": ORG,
        "type": "contract",
        "name": "Example NDA",
        "status": "ready",
        "createdBy": "demo-editor",
        "createdAt": "2026-08-13T08:00:00Z",
    }
    version = {
        "id": version_id,
        "organizationId": ORG,
        "type": "contract_version",
        "contractId": contract_id,
        "versionNumber": 3,
        "uploadedBy": "demo-editor",
        "uploadedAt": "2026-08-13T08:30:00Z",
        "fileName": "example-nda.pdf",
        "fileSizeBytes": 2048,
        "pageCount": 4,
        "processingStatus": "done",
    }
    uploader = {
        "id": "demo-editor",
        "organizationId": ORG,
        "type": "user",
        "fullName": "Demo Editor",
    }
    return contract, version, uploader


@pytest.fixture
def client(records, monkeypatch):
    contract, version, uploader = records

    def find_contract(organization_id, contract_id):
        assert organization_id == ORG
        return contract if contract_id == contract["id"] else None

    def find_version(organization_id, contract_id):
        assert organization_id == ORG
        return version if contract_id == contract["id"] else None

    def find_user(organization_id, user_id):
        assert organization_id == ORG
        return uploader if user_id == uploader["id"] else None

    monkeypatch.setattr(routes, "get_contract_by_id", find_contract)
    monkeypatch.setattr(
        routes,
        "get_current_version_for_contract",
        find_version,
    )
    monkeypatch.setattr(routes, "get_user_by_id", find_user)
    monkeypatch.setattr(
        routes,
        "get_paginated_text_chunks",
        lambda organization_id, version_id, page, page_size: (0, []),
    )

    app.dependency_overrides[current_organization_id] = (
        lambda: UUID(ORG)
    )

    yield TestClient(app)

    app.dependency_overrides.pop(current_organization_id, None)


def test_returns_contract_detail(client, records):
    contract, version, _ = records

    response = client.get(f"/api/contracts/{contract['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == contract["id"]
    assert body["name"] == "Example NDA"
    assert body["status"] == "ready"
    assert body["current_version"]["version_number"] == 3
    assert body["current_version"]["uploaded_by"] == "Demo Editor"
    assert body["current_version"]["file_name"] == "example-nda.pdf"
    assert body["current_version"]["file_size_bytes"] == 2048
    assert body["current_version"]["page_count"] == 4
    assert body["current_version"]["processing_status"] == "done"
    assert body["current_version"]["uploaded_at"]


def test_unknown_contract_returns_404(client):
    response = client.get(f"/api/contracts/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Contract not found"


def test_text_endpoint_returns_paginated_chunks(
    client,
    records,
    monkeypatch,
):
    contract, version, _ = records
    received = {}

    def get_chunks(
        organization_id,
        version_id,
        page,
        page_size,
    ):
        received.update(
            organization_id=organization_id,
            version_id=version_id,
            page=page,
            page_size=page_size,
        )
        return 5, [
            {
                "pageNumber": 2,
                "chunkOrder": 2,
                "text": "Second page text",
            },
            {
                "pageNumber": 3,
                "chunkOrder": 3,
                "text": "Third page text",
            },
        ]

    monkeypatch.setattr(
        routes,
        "get_paginated_text_chunks",
        get_chunks,
    )

    response = client.get(
        f"/api/contracts/{contract['id']}/text",
        params={"page": 2, "page_size": 2},
    )

    assert response.status_code == 200
    assert received == {
        "organization_id": ORG,
        "version_id": version["id"],
        "page": 2,
        "page_size": 2,
    }

    body = response.json()
    assert body["contract_id"] == contract["id"]
    assert body["version_number"] == 3
    assert body["page"] == 2
    assert body["page_size"] == 2
    assert body["total_items"] == 5
    assert body["total_pages"] == 3
    assert body["items"] == [
        {
            "page_number": 2,
            "chunk_order": 2,
            "text": "Second page text",
        },
        {
            "page_number": 3,
            "chunk_order": 3,
            "text": "Third page text",
        },
    ]


def test_unknown_contract_text_returns_404(client):
    response = client.get(f"/api/contracts/{uuid4()}/text")

    assert response.status_code == 404
    assert response.json()["detail"] == "Contract not found"


def test_text_pagination_parameters_are_validated(client, records):
    contract, _, _ = records

    response = client.get(
        f"/api/contracts/{contract['id']}/text",
        params={"page": 0, "page_size": 101},
    )

    assert response.status_code == 422