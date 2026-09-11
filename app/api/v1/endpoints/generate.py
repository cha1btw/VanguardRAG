from fastapi import APIRouter
from app.schemas.query import RAGQuery, RAGResponse
from app.services.embedder import embedder_service
from app.services.generator import generator_service
from app.services.qdrant_client import qdrant_service

router = APIRouter()


@router.post("/generate", response_model=RAGResponse)
async def generate_rag_answer(payload: RAGQuery):
    # 1. Поиск релевантных контекстов в Qdrant
    query_vector = await embedder_service.embed_query(payload.query)
    search_results = await qdrant_service.search_similar(
        query_vector=query_vector, limit=payload.top_k
    )

    # 2. Генерация ответа через LLM с цитированием
    rag_response = await generator_service.generate_answer(
        query=payload.query, context_points=search_results
    )

    return rag_response
