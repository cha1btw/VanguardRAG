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
                    score=point.score,
                )
            )

            context_str += f"\n--- Source [{idx + 1}]: {doc_name} (Chunk #{chunk_idx}) ---\n{content}\n"

        system_prompt = (
            "You are VanguardRAG, a corporate document assistant. Answer the "
            "user's question relying STRICTLY on the context below. "
            "If the answer is not in the context, say honestly that the "
            "information is missing from the documents. "
            "Always cite the numbers of the sources the information comes from. "
            "Always answer in the same language as the user's question, "
            "regardless of the language of the context.\n\n"
            f"Context:\n{context_str}"
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
