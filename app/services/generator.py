from typing import List
from langchain_community.chat_models import ChatOllama
from app.config import settings
from app.schemas.query import Citation, RAGResponse


class RAGGeneratorService:
    def __init__(self):
        self.llm = ChatOllama(
            model=settings.LLM_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.0,
        )

    async def generate_answer(
        self, query: str, context_points: list
    ) -> RAGResponse:
        citations: List[Citation] = []
        context_str = ""

        for idx, point in enumerate(context_points):
            doc_name = point.payload.get("document_name", "Unknown")
            chunk_idx = point.payload.get("chunk_index", 0)
            content = point.payload.get("content", "")

            citations.append(
                Citation(
                    document_name=doc_name,
                    chunk_index=chunk_idx,
                    content=content,
                )
            )

            context_str += f"\n--- Источник [{idx + 1}]: {doc_name} (Чанк #{chunk_idx}) ---\n{content}\n"

        system_prompt = (
            "Ты — корпоративный ассистент VanguardRAG. Отвечай на вопрос пользователя, "
            "опираясь СТРОГО на предоставленный ниже контекст. "
            "Если ответа нет в контексте, честно скажи, что информация отсутствует в документах. "
            "Всегда ссылайся на номера источников, откуда взята информация.\n\n"
            f"Контекст:\n{context_str}"
        )

        messages = [
            ("system", system_prompt),
            ("user", query),
        ]

        response = await self.llm.ainvoke(messages)

        return RAGResponse(
            query=query, answer=str(response.content), citations=citations
        )


generator_service = RAGGeneratorService()
