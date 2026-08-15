from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class Passage(BaseModel):
    chunk_id: str
    text: str
    page_number: int | None = None
    score: float


class AskResponse(BaseModel):
    passages: list[Passage]
    # set when passages is empty because nothing scored high enough to trust
    message: str | None = None
