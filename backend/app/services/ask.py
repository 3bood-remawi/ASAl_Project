"""
Answers a question about one contract with the passages that are most
relevant to it. No LLM synthesis yet -- just the closest chunks, so the user
can judge relevance for themselves.
"""

from app.data_access.chunks import search_chunks_by_vector
from app.data_access.contracts import get_current_version_for_contract
from app.documents.enums import ProcessingStatus
from app.schemas.ask import AskResponse, Passage
from app.services.embedding import embed_text

TOP_K = 5

# VectorDistance with the container's cosine distance function returns a
# similarity score in [-1, 1], where +1 means identical. Below this, even the
# best-matching chunk isn't a real match for the question -- guessing an
# answer from it would do more harm than saying nothing was found.
MIN_SIMILARITY_SCORE = 0.3

NO_MATCH_MESSAGE = "Couldn't find any passages in this contract that closely match your question."


class ContractNotReadyError(Exception):
    """The contract has no version yet, or that version hasn't finished processing."""


def ask_contract(organization_id: str, contract_id: str, question: str) -> AskResponse:
    version = get_current_version_for_contract(organization_id, contract_id)
    if version is None or version.get("processingStatus") != ProcessingStatus.DONE.value:
        raise ContractNotReadyError

    question_embedding = embed_text(question)
    rows = search_chunks_by_vector(organization_id, version["id"], question_embedding, top_k=TOP_K)

    if not rows or rows[0]["score"] < MIN_SIMILARITY_SCORE:
        return AskResponse(passages=[], message=NO_MATCH_MESSAGE)

    passages = [
        Passage(chunk_id=row["id"], text=row["text"], page_number=row.get("pageNumber"), score=row["score"])
        for row in rows
    ]
    return AskResponse(passages=passages)
