import logging
from typing import List
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from app.config import settings
from app.schemas.document import DocumentChunk

logger = logging.getLogger(__name__)


class QdrantService:
    def __init__(self):
        self.client = AsyncQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME

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

    async def search_similar(
        self, query_vector: List[float], limit: int = 5
    ) -> List[models.ScoredPoint]:
        """Поиск наиболее похожих векторов в Qdrant."""
        response = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
        )
        return response.points

    async def close(self):
        """Закрытие соединения с Qdrant."""
        await self.client.close()


qdrant_service = QdrantService()
