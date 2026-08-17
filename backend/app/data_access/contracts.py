from typing import Any

from app.core.cosmos import get_chunks_container, get_contracts_container
from app.documents.enums import DocumentType
from app.documents.shapes import JobDocument, VersionDocument

SORTABLE_FIELDS = {
    "name": "c.name",
    "uploaded_date": "c.createdAt",
}


def get_contracts(organization_id: str) -> list[dict[str, Any]]:
    return list(
        get_contracts_container().query_items(
            query="SELECT * FROM c WHERE c.type = @type ORDER BY c.createdAt DESC",
            parameters=[{"name": "@type", "value": DocumentType.CONTRACT.value}],
            partition_key=organization_id,
        )
    )


def get_contract_by_id(
    organization_id: str,
    contract_id: str,
) -> dict[str, Any] | None:
    rows = list(
        get_contracts_container().query_items(
            query="SELECT * FROM c WHERE c.type = @type AND c.id = @id",
            parameters=[
                {"name": "@type", "value": DocumentType.CONTRACT.value},
                {"name": "@id", "value": contract_id},
            ],
            partition_key=organization_id,
        )
    )
    return rows[0] if rows else None


def get_version_by_hash(
    organization_id: str,
    file_hash: str,
) -> dict[str, Any] | None:
    rows = list(
        get_contracts_container().query_items(
            query=(
                "SELECT * FROM c WHERE c.type = @type AND c.fileHash = @hash "
                "ORDER BY c.uploadedAt"
            ),
            parameters=[
                {"name": "@type", "value": DocumentType.VERSION.value},
                {"name": "@hash", "value": file_hash},
            ],
            partition_key=organization_id,
        )
    )
    return rows[0] if rows else None


def get_version(
    organization_id: str,
    version_id: str,
) -> VersionDocument | None:
    rows = list(
        get_contracts_container().query_items(
            query="SELECT * FROM c WHERE c.type = @type AND c.id = @id",
            parameters=[
                {"name": "@type", "value": DocumentType.VERSION.value},
                {"name": "@id", "value": version_id},
            ],
            partition_key=organization_id,
        )
    )
    return VersionDocument.model_validate(rows[0]) if rows else None


def get_current_version_for_contract(
    organization_id: str,
    contract_id: str,
) -> dict[str, Any] | None:
    """Return the highest versionNumber row for this contract."""
    rows = list(
        get_contracts_container().query_items(
            query=(
                "SELECT * FROM c WHERE c.type = @type "
                "AND c.contractId = @contract_id "
                "ORDER BY c.versionNumber DESC"
            ),
            parameters=[
                {"name": "@type", "value": DocumentType.VERSION.value},
                {"name": "@contract_id", "value": contract_id},
            ],
            partition_key=organization_id,
        )
    )
    return rows[0] if rows else None


def get_job_for_version(
    organization_id: str,
    version_id: str,
) -> JobDocument | None:
    rows = list(
        get_contracts_container().query_items(
            query="SELECT * FROM c WHERE c.type = @type AND c.versionId = @version",
            parameters=[
                {"name": "@type", "value": DocumentType.JOB.value},
                {"name": "@version", "value": version_id},
            ],
            partition_key=organization_id,
        )
    )
    return JobDocument.model_validate(rows[0]) if rows else None


def get_current_version_job(
    organization_id: str,
    contract_id: str,
) -> dict[str, Any] | None:
    """Return the job for the contract's newest version."""
    versions = list(
        get_contracts_container().query_items(
            query=(
                "SELECT * FROM c WHERE c.type = @type "
                "AND c.contractId = @contract "
                "ORDER BY c.versionNumber DESC"
            ),
            parameters=[
                {"name": "@type", "value": DocumentType.VERSION.value},
                {"name": "@contract", "value": contract_id},
            ],
            partition_key=organization_id,
        )
    )
    if not versions:
        return None

    jobs = list(
        get_contracts_container().query_items(
            query="SELECT * FROM c WHERE c.type = @type AND c.versionId = @version",
            parameters=[
                {"name": "@type", "value": DocumentType.JOB.value},
                {"name": "@version", "value": versions[0]["id"]},
            ],
            partition_key=organization_id,
        )
    )
    return jobs[0] if jobs else None


def get_editor(organization_id: str) -> dict[str, Any] | None:
    rows = list(
        get_contracts_container().query_items(
            query=(
                "SELECT * FROM c WHERE c.type = @type AND c.role = @role "
                "ORDER BY c.createdAt"
            ),
            parameters=[
                {"name": "@type", "value": DocumentType.USER.value},
                {"name": "@role", "value": "editor"},
            ],
            partition_key=organization_id,
        )
    )
    return rows[0] if rows else None


def get_contracts_with_current_versions(
    organization_id: str,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """
    Return contracts and a mapping from contract ID to current version.

    Contracts and versions share the same container and organization partition.
    """
    rows = list(
        get_contracts_container().query_items(
            query=(
                "SELECT * FROM c "
                "WHERE c.type IN (@contract_type, @version_type)"
            ),
            parameters=[
                {
                    "name": "@contract_type",
                    "value": DocumentType.CONTRACT.value,
                },
                {
                    "name": "@version_type",
                    "value": DocumentType.VERSION.value,
                },
            ],
            partition_key=organization_id,
        )
    )

    contracts: list[dict[str, Any]] = []
    versions_by_contract: dict[str, dict[str, Any]] = {}

    for document in rows:
        if document["type"] == DocumentType.CONTRACT.value:
            contracts.append(document)
        elif document["type"] == DocumentType.VERSION.value:
            contract_id = document["contractId"]
            existing = versions_by_contract.get(contract_id)
            if (
                existing is None
                or document["versionNumber"] > existing["versionNumber"]
            ):
                versions_by_contract[contract_id] = document

    return contracts, versions_by_contract


def get_contracts_page(
    organization_id: str,
    offset: int,
    page_size: int,
    name: str | None = None,
    status: str | None = None,
    sort_by: str = "uploaded_date",
    sort_order: str = "desc",
    allowed_ids: set[str] | None = None,
) -> tuple[list[dict[str, Any]], int]:
    sort_field = SORTABLE_FIELDS.get(sort_by, "c.createdAt")
    sort_direction = "ASC" if sort_order == "asc" else "DESC"

    query_parts = ["SELECT * FROM c WHERE c.type = @type"]
    parameters = [
        {"name": "@type", "value": DocumentType.CONTRACT.value}
    ]

    if name:
        query_parts.append("AND CONTAINS(c.name, @name, true)")
        parameters.append({"name": "@name", "value": name})

    if status:
        query_parts.append("AND c.status = @status")
        parameters.append({"name": "@status", "value": status})

    if allowed_ids is not None:
        if not allowed_ids:
            return [], 0

        query_parts.append("AND ARRAY_CONTAINS(@allowed_ids, c.id)")
        parameters.append(
            {"name": "@allowed_ids", "value": list(allowed_ids)}
        )

    count_query = " ".join(
        [
            "SELECT VALUE COUNT(1) FROM c WHERE c.type = @type",
            *query_parts[1:],
        ]
    )
    total_items = list(
        get_contracts_container().query_items(
            query=count_query,
            parameters=parameters,
            partition_key=organization_id,
        )
    )[0]

    page_query_parts = query_parts + [
        f"ORDER BY {sort_field} {sort_direction}",
        "OFFSET @offset LIMIT @limit",
    ]
    page_parameters = parameters + [
        {"name": "@offset", "value": offset},
        {"name": "@limit", "value": page_size},
    ]

    rows = list(
        get_contracts_container().query_items(
            query=" ".join(page_query_parts),
            parameters=page_parameters,
            partition_key=organization_id,
        )
    )
    return rows, total_items


def get_contracts_page_with_versions(
    organization_id: str,
    offset: int,
    page_size: int,
    name: str | None = None,
    status: str | None = None,
    sort_by: str = "uploaded_date",
    sort_order: str = "desc",
    contract_type: str | None = None,
    language: str | None = None,
    uploaded_by: str | None = None,
    uploaded_after: str | None = None,
    uploaded_before: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], int]:
    allowed_ids = get_contract_ids_matching_version_filters(
        organization_id,
        contract_type,
        language,
        uploaded_by,
        uploaded_after,
        uploaded_before,
    )

    contracts, total_items = get_contracts_page(
        organization_id,
        offset,
        page_size,
        name,
        status,
        sort_by,
        sort_order,
        allowed_ids,
    )

    contract_ids = [contract["id"] for contract in contracts]
    if not contract_ids:
        return contracts, {}, total_items

    versions = list(
        get_contracts_container().query_items(
            query=(
                "SELECT * FROM c WHERE c.type = @type "
                "AND ARRAY_CONTAINS(@ids, c.contractId)"
            ),
            parameters=[
                {"name": "@type", "value": DocumentType.VERSION.value},
                {"name": "@ids", "value": contract_ids},
            ],
            partition_key=organization_id,
        )
    )

    versions_by_contract: dict[str, dict[str, Any]] = {}
    for version in versions:
        contract_id = version["contractId"]
        existing = versions_by_contract.get(contract_id)
        if (
            existing is None
            or version["versionNumber"] > existing["versionNumber"]
        ):
            versions_by_contract[contract_id] = version

    return contracts, versions_by_contract, total_items


def get_contract_ids_matching_version_filters(
    organization_id: str,
    contract_type: str | None = None,
    language: str | None = None,
    uploaded_by: str | None = None,
    uploaded_after: str | None = None,
    uploaded_before: str | None = None,
) -> set[str] | None:
    if not any(
        [
            contract_type,
            language,
            uploaded_by,
            uploaded_after,
            uploaded_before,
        ]
    ):
        return None

    versions = list(
        get_contracts_container().query_items(
            query=(
                "SELECT c.contractId, c.versionNumber, c.fileType, "
                "c.language, c.uploadedBy, c.uploadedAt "
                "FROM c WHERE c.type = @type"
            ),
            parameters=[
                {"name": "@type", "value": DocumentType.VERSION.value}
            ],
            partition_key=organization_id,
        )
    )

    current_version_by_contract: dict[str, dict[str, Any]] = {}
    for version in versions:
        contract_id = version["contractId"]
        existing = current_version_by_contract.get(contract_id)
        if (
            existing is None
            or version["versionNumber"] > existing["versionNumber"]
        ):
            current_version_by_contract[contract_id] = version

    matching_ids: set[str] = set()
    for contract_id, version in current_version_by_contract.items():
        if contract_type and version.get("fileType") != contract_type:
            continue
        if language and version.get("language") != language:
            continue
        if uploaded_by and version.get("uploadedBy") != uploaded_by:
            continue
        if uploaded_after and version.get("uploadedAt", "") < uploaded_after:
            continue
        if uploaded_before and version.get("uploadedAt", "") > uploaded_before:
            continue

        matching_ids.add(contract_id)

    return matching_ids


def get_user_by_id(
    organization_id: str,
    user_id: str,
) -> dict[str, Any] | None:
    users = list(
        get_contracts_container().query_items(
            query="SELECT * FROM c WHERE c.type = @type AND c.id = @id",
            parameters=[
                {"name": "@type", "value": DocumentType.USER.value},
                {"name": "@id", "value": user_id},
            ],
            partition_key=organization_id,
        )
    )
    return users[0] if users else None


def _chunk_sort_key(
    chunk: dict[str, Any],
) -> tuple[bool, int, int]:
    page_number = chunk.get("pageNumber")
    return (
        page_number is None,
        page_number if page_number is not None else 0,
        chunk["chunkOrder"],
    )


def get_paginated_text_chunks(
    organization_id: str,
    version_id: str,
    page: int,
    page_size: int,
) -> tuple[int, list[dict[str, Any]]]:
    chunks = list(
        get_chunks_container().query_items(
            query=(
                "SELECT * FROM c WHERE c.type = @type "
                "AND c.versionId = @version_id"
            ),
            parameters=[
                {"name": "@type", "value": DocumentType.CHUNK.value},
                {"name": "@version_id", "value": version_id},
            ],
            partition_key=organization_id,
        )
    )
    chunks.sort(key=_chunk_sort_key)

    total_items = len(chunks)
    offset = (page - 1) * page_size
    return total_items, chunks[offset : offset + page_size]


def get_distinct_statuses(organization_id: str) -> list[str]:
    return list(
        get_contracts_container().query_items(
            query=(
                "SELECT DISTINCT VALUE c.status "
                "FROM c WHERE c.type = @type"
            ),
            parameters=[
                {"name": "@type", "value": DocumentType.CONTRACT.value}
            ],
            partition_key=organization_id,
        )
    )


def get_distinct_contract_types(organization_id: str) -> list[str]:
    return list(
        get_contracts_container().query_items(
            query=(
                "SELECT DISTINCT VALUE c.fileType "
                "FROM c WHERE c.type = @type "
                "AND IS_DEFINED(c.fileType)"
            ),
            parameters=[
                {"name": "@type", "value": DocumentType.VERSION.value}
            ],
            partition_key=organization_id,
        )
    )