from typing import Any

import app.data_access.contracts as contract_data

ORG = "00000000-0000-0000-0000-000000000001"
CONTRACT_ID = "11111111-1111-1111-1111-111111111111"


class FakeContainer:
    def __init__(self, rows: list[dict[str, Any]]):
        self.rows = rows
        self.calls: list[dict[str, Any]] = []

    def query_items(self, **kwargs):
        self.calls.append(kwargs)
        return list(self.rows)


def test_current_version_has_the_highest_version_number(
    monkeypatch,
):
    # Cosmos applies ORDER BY before returning these rows.
    container = FakeContainer(
        [
            {"id": "version-3", "versionNumber": 3},
            {"id": "version-2", "versionNumber": 2},
            {"id": "version-1", "versionNumber": 1},
        ]
    )
    monkeypatch.setattr(
        contract_data,
        "get_contracts_container",
        lambda: container,
    )

    current_version = (
        contract_data.get_current_version_for_contract(
            ORG,
            CONTRACT_ID,
        )
    )

    assert current_version is not None
    assert current_version["id"] == "version-3"
    assert current_version["versionNumber"] == 3
    assert container.calls[0]["partition_key"] == ORG
    assert (
        "ORDER BY c.versionNumber DESC"
        in container.calls[0]["query"]
    )


def test_current_version_returns_none_when_no_versions_exist(
    monkeypatch,
):
    container = FakeContainer([])
    monkeypatch.setattr(
        contract_data,
        "get_contracts_container",
        lambda: container,
    )

    current_version = (
        contract_data.get_current_version_for_contract(
            ORG,
            CONTRACT_ID,
        )
    )

    assert current_version is None


def test_chunks_are_ordered_by_page_then_chunk_order(
    monkeypatch,
):
    container = FakeContainer(
        [
            {
                "id": "chunk-3",
                "pageNumber": 2,
                "chunkOrder": 3,
                "text": "Page two",
            },
            {
                "id": "chunk-null",
                "pageNumber": None,
                "chunkOrder": 4,
                "text": "Unknown page",
            },
            {
                "id": "chunk-1",
                "pageNumber": 1,
                "chunkOrder": 1,
                "text": "Page one second",
            },
            {
                "id": "chunk-0",
                "pageNumber": 1,
                "chunkOrder": 0,
                "text": "Page one first",
            },
        ]
    )
    monkeypatch.setattr(
        contract_data,
        "get_chunks_container",
        lambda: container,
    )

    total_items, items = (
        contract_data.get_paginated_text_chunks(
            ORG,
            "version-3",
            page=1,
            page_size=3,
        )
    )

    assert total_items == 4
    assert [item["id"] for item in items] == [
        "chunk-0",
        "chunk-1",
        "chunk-3",
    ]
    assert container.calls[0]["partition_key"] == ORG


def test_chunk_pagination_returns_the_requested_page(
    monkeypatch,
):
    container = FakeContainer(
        [
            {
                "id": "chunk-2",
                "pageNumber": 2,
                "chunkOrder": 2,
                "text": "Third",
            },
            {
                "id": "chunk-0",
                "pageNumber": 1,
                "chunkOrder": 0,
                "text": "First",
            },
            {
                "id": "chunk-1",
                "pageNumber": 1,
                "chunkOrder": 1,
                "text": "Second",
            },
        ]
    )
    monkeypatch.setattr(
        contract_data,
        "get_chunks_container",
        lambda: container,
    )

    total_items, items = (
        contract_data.get_paginated_text_chunks(
            ORG,
            "version-3",
            page=2,
            page_size=2,
        )
    )

    assert total_items == 3
    assert [item["id"] for item in items] == ["chunk-2"]