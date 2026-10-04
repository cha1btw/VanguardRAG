from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str
    document_name: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    filename: str
    total_chunks: int
    status: str = "success"
    message: str


class DocumentSummary(BaseModel):
    document_name: str
    chunks_count: int
