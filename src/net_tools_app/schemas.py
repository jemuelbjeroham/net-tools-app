from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)

class SearchResult(BaseModel):
    content: str
    source: str
    chunk_index: int
    metadata: dict[str, object]

class SearchResponse(BaseModel):
    results: list[SearchResult]