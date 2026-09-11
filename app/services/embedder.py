from typing import List
from langchain_community.embeddings import OllamaEmbeddings
from app.config import settings


class EmbedderService:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model=settings.EMBEDDING_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return await self.embeddings.aembed_documents(texts)

    async def embed_query(self, text: str) -> List[float]:
        return await self.embeddings.aembed_query(text)


embedder_service = EmbedderService()
