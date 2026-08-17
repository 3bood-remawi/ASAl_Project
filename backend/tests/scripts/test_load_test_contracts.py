import hashlib
from types import SimpleNamespace

import pytest

from scripts import load_test_contracts as loader

ORG = "00000000-0000-0000-0000-000000000001"
USER = {
    "id": "demo-editor",
    "organizationId": ORG,
}
PDF_BYTES = b"%PDF-1.4\nTest contract"


def test_load_contract_uses_existing_upload_and_processing_pipeline(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "agreement.pdf"
    path.write_bytes(PDF_BYTES)
    captured = {}

    def fake_lookup(organization_id, file_hash):
        captured["lookup"] = (organization_id, file_hash)
        return None

    def fake_store(user, upload, file_hash, size):
        captured["store"] = {
            "user": user,
            "filename": upload.filename,
            "file_hash": file_hash,
            "size": size,
        }
        return (
            SimpleNamespace(id="contract-1"),
            SimpleNamespace(id="version-1"),
            SimpleNamespace(id="job-1"),
        )

    processed = []

    monkeypatch.setattr(
        loader,
        "get_version_by_hash",
        fake_lookup,
    )
    monkeypatch.setattr(loader, "store_upload", fake_store)
    monkeypatch.setattr(
        loader,
        "process_version",
        lambda organization_id, version_id: processed.append(
            (organization_id, version_id)
        ),
    )

    created = loader.load_contract(path, USER)

    expected_hash = hashlib.sha256(PDF_BYTES).hexdigest()

    assert created is True
    assert captured["lookup"] == (ORG, expected_hash)
    assert captured["store"] == {
        "user": USER,
        "filename": "agreement.pdf",
        "file_hash": expected_hash,
        "size": len(PDF_BYTES),
    }
    assert processed == [(ORG, "version-1")]


def test_loading_the_same_pdf_twice_does_not_create_a_duplicate(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "agreement.pdf"
    path.write_bytes(PDF_BYTES)

    stored_hashes = set()
    store_calls = []
    process_calls = []

    def fake_lookup(organization_id, file_hash):
        if file_hash in stored_hashes:
            return {"id": "existing-version"}
        return None

    def fake_store(user, upload, file_hash, size):
        stored_hashes.add(file_hash)
        store_calls.append(file_hash)
        return (
            SimpleNamespace(id="contract-1"),
            SimpleNamespace(id="version-1"),
            SimpleNamespace(id="job-1"),
        )

    monkeypatch.setattr(
        loader,
        "get_version_by_hash",
        fake_lookup,
    )
    monkeypatch.setattr(loader, "store_upload", fake_store)
    monkeypatch.setattr(
        loader,
        "process_version",
        lambda organization_id, version_id: process_calls.append(
            (organization_id, version_id)
        ),
    )

    first_result = loader.load_contract(path, USER)
    second_result = loader.load_contract(path, USER)

    assert first_result is True
    assert second_result is False
    assert len(store_calls) == 1
    assert process_calls == [(ORG, "version-1")]


def test_load_test_contracts_reads_only_pdfs_in_filename_order(
    tmp_path,
    monkeypatch,
):
    for filename in [
        "normal-b.pdf",
        "ECsample-scan.pdf",
        "normal-a.pdf",
    ]:
        (tmp_path / filename).write_bytes(PDF_BYTES)

    (tmp_path / "README.md").write_text(
        "Not a contract",
        encoding="utf-8",
    )

    seen = []

    monkeypatch.setattr(
        loader,
        "get_editor",
        lambda organization_id: USER,
    )

    def fake_load(path, user):
        seen.append(path.name)
        return path.name != "normal-b.pdf"

    monkeypatch.setattr(loader, "load_contract", fake_load)

    created, skipped = loader.load_test_contracts(tmp_path)

    assert seen == [
        "ECsample-scan.pdf",
        "normal-a.pdf",
        "normal-b.pdf",
    ]
    assert created == 2
    assert skipped == 1


def test_load_test_contracts_requires_an_editor(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        loader,
        "get_editor",
        lambda organization_id: None,
    )

    with pytest.raises(RuntimeError, match="scripts/seed.py"):
        loader.load_test_contracts(tmp_path)


def test_load_test_contracts_requires_pdf_fixtures(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        loader,
        "get_editor",
        lambda organization_id: USER,
    )

    with pytest.raises(RuntimeError, match="No PDF fixtures"):
        loader.load_test_contracts(tmp_path)