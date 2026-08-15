import logging
import sys
from functools import lru_cache
from pathlib import Path

from sentence_transformers import SentenceTransformer

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.cosmos import get_chunks_container
from app.documents.shapes import ChunkDocument

MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 32

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("azure").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


@lru_cache
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def find_chunks_missing_embedding() -> list[ChunkDocument]:
    container = get_chunks_container()
    query = "SELECT * FROM c WHERE NOT IS_DEFINED(c.embedding) OR IS_NULL(c.embedding)"
    items = container.query_items(query=query, enable_cross_partition_query=True)
    return [ChunkDocument.model_validate(item) for item in items]


def _batched(chunks: list[ChunkDocument], size: int) -> list[list[ChunkDocument]]:
    return [chunks[i : i + size] for i in range(0, len(chunks), size)]


def embed_batch(chunks: list[ChunkDocument]) -> list[list[float]]:
    model = get_model()
    texts = [chunk.text for chunk in chunks]
    vectors = model.encode(texts)
    return vectors.tolist()


def save_embeddings(chunks: list[ChunkDocument], vectors: list[list[float]]) -> None:
    container = get_chunks_container()
    for chunk, vector in zip(chunks, vectors, strict=True):
        chunk.embedding = vector
        container.upsert_item(chunk.to_item())


def main() -> None:
    chunks = find_chunks_missing_embedding()
    logger.info("Found %d chunk(s) missing an embedding", len(chunks))

    if not chunks:
        logger.info("Nothing to do.")
        return

    batches = _batched(chunks, BATCH_SIZE)
    logger.info("Processing in %d batch(es) of up to %d", len(batches), BATCH_SIZE)

    for batch_number, batch in enumerate(batches, start=1):
        vectors = embed_batch(batch)
        save_embeddings(batch, vectors)
        logger.info("Batch %d/%d done (%d chunks)", batch_number, len(batches), len(batch))

    logger.info("Finished. %d chunk(s) embedded.", len(chunks))


if __name__ == "__main__":
    main()