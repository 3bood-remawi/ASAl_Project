from functools import lru_cache

import urllib3
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.database import DatabaseProxy

from app.core.config import settings
from app.documents.shapes import (
    CHUNKS_CONTAINER,
    CONTRACTS_CONTAINER,
    EMBEDDING_DIM,
    PARTITION_KEY_PATH,
)

# the emulator serves a self-signed certificate, so verification is off locally
_VERIFY_TLS = settings.ENV != "development"
if not _VERIFY_TLS:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_VECTOR_EMBEDDINGS = {
    "vectorEmbeddings": [
        {
            "path": "/embedding",
            "dataType": "float32",
            "distanceFunction": "cosine",
            "dimensions": EMBEDDING_DIM,
        }
    ]
}

_CHUNK_INDEXING = {
    "indexingMode": "consistent",
    "automatic": True,
    "includedPaths": [{"path": "/*"}],
    # the raw vector is searched, not range-indexed
    "excludedPaths": [{"path": '/"_etag"/?'}, {"path": "/embedding/*"}],
    "vectorIndexes": [{"path": "/embedding", "type": "quantizedFlat"}],
}


@lru_cache
def get_client() -> CosmosClient:
    """The Cosmos client. Built on first use so importing the app needs no database."""
    return CosmosClient(
        settings.COSMOS_ENDPOINT,
        credential=settings.COSMOS_KEY,
        connection_verify=_VERIFY_TLS,
    )


def get_database() -> DatabaseProxy:
    return get_client().get_database_client(settings.COSMOS_DATABASE)


def get_contracts_container():
    return get_database().get_container_client(CONTRACTS_CONTAINER)


def get_chunks_container():
    return get_database().get_container_client(CHUNKS_CONTAINER)


def create_database_and_containers() -> None:
    """Make the database and both containers if they are not there yet."""
    database = get_client().create_database_if_not_exists(settings.COSMOS_DATABASE)
    database.create_container_if_not_exists(
        id=CONTRACTS_CONTAINER,
        partition_key=PartitionKey(path=PARTITION_KEY_PATH),
    )
    database.create_container_if_not_exists(
        id=CHUNKS_CONTAINER,
        partition_key=PartitionKey(path=PARTITION_KEY_PATH),
        vector_embedding_policy=_VECTOR_EMBEDDINGS,
        indexing_policy=_CHUNK_INDEXING,
    )
