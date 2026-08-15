from typing import Any

from app.core.cosmos import get_chunks_container
from app.documents.enums import DocumentType


def search_chunks_by_vector(
    organization_id: str,
    version_id: str,
    query_embedding: list[float],
    top_k: int,
) -> list[dict[str, Any]]:
    """
    The top_k chunks of one contract version, nearest first, to query_embedding.

    Each row carries a `score` from VectorDistance: with the container's cosine
    distance function this ranges -1 (least similar) to +1 (most similar).
    ORDER BY VectorDistance(...) is a special case in Cosmos DB's query engine —
    it always sorts nearest-first using the vector index, no ASC/DESC needed.
    """
    query = (
        f"SELECT TOP {int(top_k)} c.id, c.text, c.pageNumber, "
        "VectorDistance(c.embedding, @embedding) AS score "
        "FROM c WHERE c.type = @type AND c.versionId = @versionId AND IS_DEFINED(c.embedding) "
        "ORDER BY VectorDistance(c.embedding, @embedding)"
    )
    return list(
        get_chunks_container().query_items(
            query=query,
            parameters=[
                {"name": "@type", "value": DocumentType.CHUNK.value},
                {"name": "@versionId", "value": version_id},
                {"name": "@embedding", "value": query_embedding},
            ],
            partition_key=organization_id,
        )
    )
