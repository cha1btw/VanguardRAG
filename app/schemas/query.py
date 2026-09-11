from typing import Any, Dict, List
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    query: str = Field(..., description="Поисковый запрос")
    top_k: int = Field(default=5, ge=1, le=20, description="Количество чанков")


class SearchResultItem(BaseModel):
    score: float
    document_name: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]


# --- RAG Generation Schemas ---
class Citation(BaseModel):
    document_name: str
    chunk_index: int
    content: str


class RAGQuery(BaseModel):
    query: str = Field(..., description="Вопрос пользователя")
    top_k: int = Field(default=3, ge=1, le=10)


class RAGResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
