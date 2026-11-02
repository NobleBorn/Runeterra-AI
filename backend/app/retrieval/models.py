
from pydantic import BaseModel, Field


class RetrievalResult(BaseModel):
    chunk_id: str
    document_id: str

    title: str
    source_url: str
    source_type: str
    continuity: str

    content: str

    semantic_score: float | None = None
    keyword_score: float | None = None

    semantic_rank: int | None = None
    keyword_rank: int | None = None

    rrf_score: float = 0.0


class SearchResponse(BaseModel):
    query: str
    results: list[RetrievalResult] = Field(
        default_factory=list
    )
