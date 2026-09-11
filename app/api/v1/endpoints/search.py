from fastapi import APIRouter
from app.schemas.query import SearchQuery, SearchResponse, SearchResultItem
from app.services.embedder import embedder_service
from app.services.qdrant_client import qdrant_service

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_documents(payload: SearchQuery):
    query_vector = await embedder_service.embed_query(payload.query)
    search_results = await qdrant_service.search_similar(
        query_vector=query_vector, limit=payload.top_k
    )

    results = [
        SearchResultItem(
            score=point.score,
            document_name=point.payload.get("document_name", "Unknown"),
            content=point.payload.get("content", ""),
            metadata={
                "chunk_index": point.payload.get("chunk_index"),
                "total_chunks": point.payload.get("total_chunks"),
                "source": point.payload.get("source"),
            },
        )
        for point in search_results
    ]

    return SearchResponse(query=payload.query, results=results)
