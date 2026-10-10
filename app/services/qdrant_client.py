import logging
from typing import List
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from app.config import settings
from app.schemas.document import DocumentChunk, DocumentSummary

logger = logging.getLogger(__name__)


class QdrantService:
    def __init__(self):
        self.client = AsyncQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    async def check_connection(self):
        await self.client.get_collections()

    async def init_collection(self, vector_size: int = settings.VECTOR_SIZE):
        """Создает коллекцию в Qdrant, если она еще не существует."""
        try:
            collections = await self.client.get_collections()
            exists = any(
                c.name == self.collection_name for c in collections.collections
            )

            if not exists:
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE,
                    ),
                )
                logger.info(
                    f"Коллекция '{self.collection_name}' создана с размерностью векторов {vector_size}."
                )
            else:
                logger.info(
                    f"Коллекция '{self.collection_name}' уже существует."
                )
        except Exception as e:
            logger.error(f"Ошибка Qdrant при инициализации: {e}")
            raise e

    async def upsert_chunks(
        self, chunks: List[DocumentChunk], embeddings: List[List[float]]
    ):
        """Запись векторов и метаданных чанков в коллекцию Qdrant."""
        points = [
            models.PointStruct(
                id=chunk.chunk_id,
                vector=embedding,
                payload={
                    "content": chunk.content,
                    "document_name": chunk.document_name,
                    **chunk.metadata,
                },
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]

        await self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    async def delete_document(self, document_name: str) -> int:
        """Remove all stored chunks for a document and return how many existed."""
        document_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="document_name",
                    match=models.MatchValue(value=document_name),
                )
            ]
        )
        count_result = await self.client.count(
            collection_name=self.collection_name,
            count_filter=document_filter,
            exact=True,
        )
        if count_result.count:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=document_filter,
            )
        return count_result.count

    async def list_documents(self) -> List[DocumentSummary]:
        document_counts = {}
        offset = None

        while True:
            points, next_offset = await self.client.scroll(
                collection_name=self.collection_name,
                limit=256,
                offset=offset,
                with_payload=["document_name"],
                with_vectors=False,
            )
            for point in points:
                document_name = (point.payload or {}).get("document_name")
                if document_name:
                    document_counts[document_name] = (
                        document_counts.get(document_name, 0) + 1
                    )

            if next_offset is None:
                break
            offset = next_offset

        return [
            DocumentSummary(document_name=name, chunks_count=count)
            for name, count in sorted(document_counts.items())
        ]

    async def search_similar(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float | None = None,
    ) -> List[models.ScoredPoint]:
        """Поиск наиболее похожих векторов в Qdrant."""
        response = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )
        return response.points

    async def close(self):
        """Закрытие соединения с Qdrant."""
        await self.client.close()


qdrant_service = QdrantService()
