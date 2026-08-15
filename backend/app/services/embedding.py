"""
Turns text into vectors with all-MiniLM-L6-v2 (see app.documents.shapes.EMBEDDING_DIM).

The same model is used to embed contract chunks at processing time and to
embed the user's question at ask time, so the two sets of vectors live in
the same space and are safe to compare with VectorDistance.
"""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache
def _model() -> SentenceTransformer:
    # Loaded once per process. First call downloads/loads the model, which is
    # slow; every call after that reuses it.
    return SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> list[float]:
    """Embeds a single string, e.g. an incoming question."""
    return _model().encode(text, normalize_embeddings=True).tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embeds many strings at once, e.g. every chunk of a version. Order-preserving."""
    if not texts:
        return []
    return _model().encode(texts, normalize_embeddings=True).tolist()
