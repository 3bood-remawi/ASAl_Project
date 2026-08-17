import scripts.reprocess as reprocess_script
from app.data_access import chunks as chunks_data

ORG = "00000000-0000-0000-0000-000000000001"


class StubContainer:
    """Answers the chunk query and records what was deleted."""

    def __init__(self, rows):
        self._rows = rows
        self.deleted = []

    def query_items(self, *args, **kwargs):
        return list(self._rows)

    def delete_item(self, item, partition_key):
        self.deleted.append((item, partition_key))


def test_deleting_chunks_removes_every_one(monkeypatch):
    container = StubContainer([{"id": "v1-0"}, {"id": "v1-1"}, {"id": "v1-2"}])
    monkeypatch.setattr(chunks_data, "get_chunks_container", lambda: container)

    deleted = chunks_data.delete_chunks_for_version(ORG, "v1")

    assert deleted == 3
    assert [item for item, _ in container.deleted] == ["v1-0", "v1-1", "v1-2"]


def test_every_delete_stays_in_the_callers_partition(monkeypatch):
    container = StubContainer([{"id": "v1-0"}, {"id": "v1-1"}])
    monkeypatch.setattr(chunks_data, "get_chunks_container", lambda: container)

    chunks_data.delete_chunks_for_version(ORG, "v1")

    assert {key for _, key in container.deleted} == {ORG}


def test_a_version_with_no_chunks_deletes_nothing(monkeypatch):
    container = StubContainer([])
    monkeypatch.setattr(chunks_data, "get_chunks_container", lambda: container)

    assert chunks_data.delete_chunks_for_version(ORG, "v1") == 0
    assert container.deleted == []


def test_reprocess_clears_chunks_before_running_again(monkeypatch):
    calls = []
    monkeypatch.setattr(reprocess_script, "get_current_version_for_contract",
                        lambda org, contract_id: {"id": "version-1"})
    monkeypatch.setattr(reprocess_script, "delete_chunks_for_version",
                        lambda org, version_id: calls.append(("delete", version_id)) or 2)
    monkeypatch.setattr(reprocess_script, "process_version",
                        lambda org, version_id: calls.append(("process", version_id)))

    reprocess_script.reprocess(ORG, "contract-1")

    # stale chunks must go first, otherwise a shorter re-chunk leaves leftovers
    assert calls == [("delete", "version-1"), ("process", "version-1")]


def test_a_contract_with_no_version_is_left_alone(monkeypatch):
    calls = []
    monkeypatch.setattr(reprocess_script, "get_current_version_for_contract",
                        lambda org, contract_id: None)
    monkeypatch.setattr(reprocess_script, "delete_chunks_for_version",
                        lambda org, version_id: calls.append("delete"))
    monkeypatch.setattr(reprocess_script, "process_version",
                        lambda org, version_id: calls.append("process"))

    reprocess_script.reprocess(ORG, "contract-1")

    assert calls == []
