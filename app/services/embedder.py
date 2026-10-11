import logging
from typing import List
from langchain_community.embeddings import OllamaEmbeddings
from app.config import settings
from app.core.exceptions import OllamaUnavailableError

logger = logging.getLogger(__name__)


class EmbedderService:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model=settings.EMBEDDING_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            return await self.embeddings.aembed_documents(texts)
        except Exception as error:
            logger.exception("Ollama embedding request failed")
            raise OllamaUnavailableError from error

    async def embed_query(self, text: str) -> List[float]:
        try:
            return await self.embeddings.aembed_query(text)
        except Exception as error:
            logger.exception("Ollama embedding request failed")
            raise OllamaUnavailableError from error


embedder_service = EmbedderService()
